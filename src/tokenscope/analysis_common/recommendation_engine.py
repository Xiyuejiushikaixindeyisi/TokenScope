"""Bounded proposal -> guarded Plan -> original-scope replay -> sealed recommendation."""

import hashlib
from pathlib import Path
from typing import Any

from tokenscope.analysis_common.contracts import (
    AnalysisFragment,
    EvaluationResult,
    ModificationPlan,
    PreparedMutation,
    canonical_metadata,
    stable_id,
)
from tokenscope.analysis_common.evaluation import evaluate_plan
from tokenscope.analysis_common.plugins import (
    EvidenceCapabilities,
    ExecutionStopped,
    MutationPreparation,
    RunControl,
)
from tokenscope.analysis_common.presentation import evaluation_view
from tokenscope.analysis_common.proposal_plugins import ProposalAdapter, validate_support
from tokenscope.analysis_common.recommendation_evidence import advice_examples, edit_examples
from tokenscope.analysis_common.recommendation_execution import canonical_operations
from tokenscope.analysis_common.recommendation_grouping import digest, group_proposals
from tokenscope.analysis_common.recommendation_publication import written_items
from tokenscope.analysis_common.recommendation_reasons import reason_class
from tokenscope.analysis_common.recommendation_runtime import RecommendationControl
from tokenscope.analysis_common.recommendation_store import write_extension
from tokenscope.analysis_common.recommendations import (
    Impact,
    ObjectRef,
    Proposal,
    RecipeBundle,
    Recommendation,
)
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.analysis_common.storage import ResultWriter
from tokenscope.analysis_common.telemetry import Telemetry
from tokenscope.analysis_common.wire import from_wire, to_wire


def _run_token_recommendations(
    *,
    source: ResolvedSource,
    writer: ResultWriter,
    workspace: Path,
    task_id: str,
    snapshot: dict[str, Any],
    adapter: ProposalAdapter | None,
    control: RecommendationControl,
) -> dict[str, Any]:
    if adapter is None or adapter.describe().model_dump(mode="json") != snapshot["adapter"]:
        raise ExecutionStopped("AUTO_ADAPTER_UNAVAILABLE")
    bundle = RecipeBundle.model_validate_json(__import__("json").dumps(snapshot["bundle"]))
    if digest(bundle) != snapshot["bundle_digest"]:
        raise ExecutionStopped("RECIPE_BUNDLE_INVALID")
    # Validate the frozen snapshot again, never reload a live file during execution.
    validated = adapter.validate_bundle(bundle)
    if validated != bundle:
        raise ExecutionStopped("RECIPE_BUNDLE_CHANGED")
    proposals: list[Proposal] = []
    checked = 0
    for fragment_id, payload in written_items(writer, "fragment"):
        control.task.checkpoint()
        control.stop_location = "fragment:" + fragment_id
        fragment = from_wire(AnalysisFragment, payload)
        if not fragment.coverage.complete:
            raise ExecutionStopped("TOKEN_FRAGMENT_INCOMPLETE")
        request = source.read_request(fragment.request_key)
        for item in adapter.propose(
            task_id,
            source.scope.scope_id,
            request,
            fragment_id,
            fragment,
            bundle,
            EvidenceCapabilities(),
            RunControl(control.task.options.token_selection.budget, control.task.cancelled),
        ):
            item = Proposal.model_validate_json(item.model_dump_json())
            control.item_size("proposal_bytes", len(item.model_dump_json().encode()))
            control.consume("proposals")
            validate_support(item, task_id, source.scope.scope_id, fragment_id, fragment)
            if item.recipe not in bundle.recipes:
                raise ValueError("PROPOSAL_RECIPE_NOT_IN_SNAPSHOT")
            if item.applicability != "matched" and any(
                reason_class(c) != "business" for c in item.reason_codes
            ):
                raise ExecutionStopped("PROPOSAL_TECHNICAL_FAILURE")
            proposals.append(item)
        checked += 1
        control.scan_checked = checked
    if checked != source.scope.request_count:
        raise ExecutionStopped("PROPOSAL_SCAN_INCOMPLETE")
    control.scan_complete = True
    groups = group_proposals(
        proposals,
        task_id=task_id,
        scope_id=source.scope.scope_id,
        generator_identity=adapter.describe().generator_identity,
        bundle_digest=snapshot["bundle_digest"],
    )
    executions: dict[bytes, tuple[ModificationPlan, EvaluationResult]] = {}
    outcomes = {"completed": 0, "advice_only": 0, "blocked": 0, "failed": 0, "not_run": 0}
    first_failure_location: str | None = None
    stage_reasons: set[str] = set()
    for order, group in enumerate(groups):
        control.task.checkpoint()
        control.stop_location = "recommendation:" + group.recommendation_id
        try:
            control.consume("recommendations")
        except ExecutionStopped as exc:
            if exc.code == "ANALYSIS_INTERRUPTED":
                raise
            stage_reasons.add(exc.code)
            outcomes["not_run"] += len(groups) - order
            first_failure_location = first_failure_location or control.stop_location
            break
        members = [p for p in proposals if p.recipe == group.recipe]
        matched = [p for p in members if p.applicability == "matched"]
        operations: list[PreparedMutation] = []
        prepared_plan = None
        execution_plan = None
        evaluation = None
        fingerprint = None
        reused = False
        status = "advice_only"
        reason_codes: tuple[str, ...] = ()
        try:
            if not matched:
                reason_codes = tuple(sorted({c for p in members for c in p.reason_codes})) or (
                    "NO_MATCHED_TARGETS",
                )
            elif group.recipe.basis is None:
                reason_codes = ("RECIPE_BASIS_MISSING",)
            elif group.recipe.basis.kind == "offline_hypothesis":
                reason_codes = ("HYPOTHESIS_DISABLED",)
            elif group.recipe.basis.authority.status != "verified":
                status = "blocked"
                reason_codes = ("BASIS_INVALID",)
            else:
                for proposal in matched:
                    request = source.read_request(proposal.support_refs[0].request_key)
                    prepared = adapter.prepare_proposal(request, proposal, group.recipe.basis)
                    prepared = MutationPreparation.model_validate_json(prepared.model_dump_json())
                    if prepared.status != "prepared":
                        raise ExecutionStopped(
                            prepared.reason_codes[0]
                            if prepared.reason_codes
                            else "PREPARATION_FAILED"
                        )
                    control.consume("prepared_operations", len(prepared.operations))
                    for op in prepared.operations:
                        if (op.target.location.request_key, op.target.location.raw_sha256) != (
                            request.request_key,
                            request.raw_sha256,
                        ):
                            raise ValueError("PREPARED_TARGET_OUTSIDE_REQUEST")
                    operations.extend(prepared.operations)
                # No unvalidated proposal can borrow another proposal's execution.
                canonical = canonical_operations(operations)
                fingerprint = hashlib.sha256(
                    canonical_metadata([source.scope.scope_id, canonical.decode()])
                ).hexdigest()
                unique = {
                    canonical_metadata(
                        op.model_dump(exclude={"operation_id", "business_basis_ref"})
                    ): op
                    for op in operations
                }
                candidate_plan = ModificationPlan(
                    plan_id=stable_id("plan", [group.recommendation_id, canonical.decode()]),
                    version="1",
                    source_scope_id=source.scope.scope_id,
                    transformation_digest=digest(operations),
                    direction="token_content",
                    action_class="policy_based",
                    finding_refs=tuple(
                        sorted({f for s in group.support_refs for f in s.finding_ids})
                    ),
                    operations=tuple(unique[k] for k in sorted(unique)),
                )
                control.plan(len(candidate_plan.model_dump_json().encode()))
                writer.add("plan", candidate_plan.plan_id, to_wire(candidate_plan))
                prepared_plan = candidate_plan
                if canonical in executions:
                    execution_plan, evaluation = executions[canonical]
                    reused = True
                else:
                    control.consume("token_evaluations")
                    execution_plan = prepared_plan
                    path = workspace / "token_recommendations" / str(order)
                    with getattr(control.task, "telemetry", Telemetry()).span("token_evaluation"):
                        evaluation = evaluate_plan(
                            source, prepared_plan, path, control=control.task
                        )
                    if evaluation.manifest_ref:
                        evaluation = evaluation.model_copy(
                            update={
                                "manifest_ref": (path / "rows.sqlite3")
                                .relative_to(workspace)
                                .as_posix()
                            }
                        )
                    writer.add("evaluation", evaluation.evaluation_id, evaluation_view(evaluation))
                    executions[canonical] = (execution_plan, evaluation)
                if evaluation.status == "interrupted":
                    raise ExecutionStopped("ANALYSIS_INTERRUPTED")
                status = evaluation.status
                reason_codes = evaluation.reason_codes
        except (ExecutionStopped, ValueError, KeyError, TypeError, RuntimeError) as exc:
            code = getattr(exc, "code", "PREPARATION_FAILED")
            if code == "ANALYSIS_INTERRUPTED":
                raise
            status = "blocked"
            reason_codes = (code,)
        available = status == "available"
        m = source.scope.request_count
        n = (
            evaluation.modified_before.n
            if available and evaluation and evaluation.modified_before
            else None
        )
        impact = Impact(
            total_requests=m,
            matched_requests=len(
                {t.location.request_key for p in matched for t in p.request_targets}
            ),
            matched_checked_requests=checked,
            match_complete=True,
            modified_requests=n,
            evaluation_complete=available,
        )
        rec = Recommendation.model_validate_json(
            __import__("json").dumps(
                dict(
                    recommendation_id=group.recommendation_id,
                    task_id=task_id,
                    scope_id=source.scope.scope_id,
                    direction="token_content",
                    generator_identity=adapter.describe().generator_identity,
                    recipe_key=group.recipe_key,
                    group_basis_digest=digest(group.recipe),
                    recipe=group.recipe.model_dump(mode="json"),
                    support_refs=[s.model_dump(mode="json") for s in group.support_refs],
                    matched_set_digest=group.matched_set_digest,
                    support_set_digest=group.support_set_digest,
                    members_complete=True,
                    impact=impact.model_dump(mode="json"),
                    proposal_status="matched" if matched else "advice_only",
                    preparation_status="prepared"
                    if prepared_plan
                    else "not_required"
                    if status == "advice_only"
                    else "blocked",
                    evaluation_status=evaluation.status
                    if evaluation
                    else "not_required"
                    if status == "advice_only"
                    else "blocked",
                    status=status,
                    reason_codes=list(reason_codes),
                    prepared_plan_ref={"task_id": task_id, "id": prepared_plan.plan_id}
                    if prepared_plan
                    else None,
                    execution_plan_ref={"task_id": task_id, "id": execution_plan.plan_id}
                    if execution_plan
                    else None,
                    evaluation_ref={"task_id": task_id, "id": evaluation.evaluation_id}
                    if evaluation
                    else None,
                    evaluation_reused=reused,
                    execution_fingerprint=fingerprint,
                    evaluation=evaluation.model_dump(mode="json") if evaluation else None,
                    display_qualification="token_evaluated" if available else "token_advice",
                    display_order=order,
                )
            )
        )
        if (available and execution_plan) or status == "advice_only":
            try:
                examples = (
                    edit_examples(rec, execution_plan, source, control.budget)
                    if available and execution_plan
                    else advice_examples(
                        rec,
                        {
                            ref.fragment_id: from_wire(
                                AnalysisFragment,
                                __import__("json").loads(
                                    writer.db.execute(
                                        "SELECT payload FROM items WHERE kind='fragment' AND id=?",
                                        (ref.fragment_id,),
                                    ).fetchone()[0]
                                ),
                            )
                            for ref in rec.support_refs[: control.budget.max_examples_per_group]
                            if ref.fragment_id
                        },
                        source,
                        control.budget,
                    )
                )
            except (ExecutionStopped, ValueError) as exc:
                rec = rec.model_copy(
                    update={
                        "reason_codes": (
                            *rec.reason_codes,
                            getattr(exc, "code", "EVIDENCE_GENERATION_FAILED"),
                        )
                    }
                )
                write_extension(writer, task_id, source.scope.scope_id, rec)
                raise
            for example in examples:
                write_extension(writer, task_id, source.scope.scope_id, example)
            rec = rec.model_copy(
                update={
                    "example_refs": tuple(
                        ObjectRef(task_id=task_id, id=e.example_id) for e in examples
                    )
                }
            )
        write_extension(writer, task_id, source.scope.scope_id, rec)
        outcomes["completed" if available else status if status in outcomes else "failed"] += 1
        if not available and status != "advice_only" and first_failure_location is None:
            first_failure_location = control.stop_location
        if not available and status != "advice_only":
            stage_reasons.update(reason_codes)
    if not (outcomes["blocked"] or outcomes["failed"] or outcomes["not_run"]):
        control.stop_location = None
    else:
        control.stop_location = first_failure_location
    return {
        "checked": checked,
        "recommendations": len(groups),
        "reason_codes": sorted(stage_reasons),
        **outcomes,
        "complete": not (outcomes["blocked"] or outcomes["failed"] or outcomes["not_run"]),
    }


def run_token_recommendations(**kwargs: Any) -> dict[str, Any]:
    control = kwargs["control"]
    with getattr(control.task, "telemetry", Telemetry()).span("token_proposal_prepare_evaluation"):
        return _run_token_recommendations(**kwargs)

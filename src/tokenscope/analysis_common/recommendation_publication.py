"""Project existing low-hit experiments into sealed recommendation extensions."""

import json
from collections.abc import Iterator
from typing import Any

from tokenscope.analysis_common.contracts import EvaluationResult, ModificationPlan
from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.recommendation_evidence import difference_examples, edit_examples
from tokenscope.analysis_common.recommendation_runtime import RecommendationControl
from tokenscope.analysis_common.recommendation_store import write_extension
from tokenscope.analysis_common.recommendations import ObjectRef, RecommendationBudget
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.analysis_common.storage import ResultWriter
from tokenscope.analysis_common.wire import from_wire
from tokenscope.prefix_analysis.recommendation_groups import difference_groups
from tokenscope.prefix_analysis.recommendation_projection import project_low_hit
from tokenscope.prefix_analysis.service import PrefixFinding


def written_items(writer: ResultWriter, kind: str) -> Iterator[tuple[str, dict[str, Any]]]:
    for ident, raw in writer.db.execute(
        "SELECT id,payload FROM items WHERE kind=? ORDER BY rowid", (kind,)
    ):
        yield ident, json.loads(raw)


def publish_low_hit(
    source: ResolvedSource,
    writer: ResultWriter,
    task_id: str,
    budget: RecommendationBudget,
    complete: bool,
    control: RecommendationControl | None = None,
) -> tuple[int, int]:
    scope_id = source.scope.scope_id
    findings = [from_wire(PrefixFinding, v) for _, v in written_items(writer, "finding")]
    plans = [from_wire(ModificationPlan, v) for _, v in written_items(writer, "plan")]
    evaluations = [
        from_wire(
            EvaluationResult,
            {k: v for k, v in payload.items() if k in EvaluationResult.model_fields},
        )
        for _, payload in written_items(writer, "evaluation")
    ]
    recommendations = project_low_hit(
        findings,
        evaluations,
        plans,
        task_id=task_id,
        scope_id=scope_id,
        total_requests=source.scope.request_count,
        members_complete=complete,
    )
    groups = difference_groups(
        findings,
        task_id=task_id,
        scope_id=scope_id,
        read_raw=lambda key: source.read_request(key).raw_body,
        complete=complete,
    )
    plan_map = {p.plan_id: p for p in plans}
    evidence_errors: list[str] = []
    finding_map = {f.finding_id: f for f in findings}
    # Difference facts survive optimization-card/Plan budgets and failed example generation.
    for group in groups:
        try:
            samples = difference_examples(group, finding_map, source, budget)
        except (ExecutionStopped, ValueError) as exc:
            code = getattr(exc, "code", "EVIDENCE_GENERATION_FAILED")
            evidence_errors.append(code)
            samples = ()
            group = group.model_copy(update={"reason_codes": (*group.reason_codes, code)})
        for sample in samples:
            write_extension(writer, task_id, scope_id, sample)
        group = group.model_copy(
            update={
                "example_refs": tuple(ObjectRef(task_id=task_id, id=e.example_id) for e in samples)
            }
        )
        write_extension(writer, task_id, scope_id, group)
    if control:
        control.consume("recommendations", len(recommendations))
        for plan in plans:
            control.plan(len(plan.model_dump_json().encode()))
            control.consume("prepared_operations", len(plan.operations))
    for rec in recommendations:
        try:
            examples = (
                edit_examples(rec, plan_map[rec.execution_plan_ref.id], source, budget, finding_map)
                if rec.execution_plan_ref
                else ()
            )
        except (ExecutionStopped, ValueError) as exc:
            code = getattr(exc, "code", "EVIDENCE_GENERATION_FAILED")
            evidence_errors.append(code)
            examples = ()
            rec = rec.model_copy(update={"reason_codes": (*rec.reason_codes, code)})
        for item in examples:
            write_extension(writer, task_id, scope_id, item)
        rec = rec.model_copy(
            update={
                "example_refs": tuple(ObjectRef(task_id=task_id, id=e.example_id) for e in examples)
            }
        )
        write_extension(writer, task_id, scope_id, rec)
    if evidence_errors:
        raise ExecutionStopped(evidence_errors[0])
    return len(recommendations), len(groups)

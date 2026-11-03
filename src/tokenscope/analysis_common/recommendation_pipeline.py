"""Publish the independent extension inside the original diagnostic terminal transaction."""

from pathlib import Path
from typing import Any

from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.recommendation_engine import run_token_recommendations
from tokenscope.analysis_common.recommendation_grouping import digest
from tokenscope.analysis_common.recommendation_publication import publish_low_hit, written_items
from tokenscope.analysis_common.recommendation_runtime import (
    RecommendationControl,
    RecommendationSettings,
)
from tokenscope.analysis_common.recommendation_store import write_extension
from tokenscope.analysis_common.recommendations import (
    BudgetConsumption,
    RecommendationBudget,
    RecommendationSummary,
    StageCoverage,
)
from tokenscope.analysis_common.runtime_control import TaskControl
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.analysis_common.storage import ResultWriter


def run_extension(
    source: ResolvedSource,
    writer: ResultWriter,
    workspace: Path,
    task_id: str,
    snapshot: dict[str, Any],
    settings: RecommendationSettings | None,
    task: TaskControl,
    low_hit_complete: bool,
    *,
    enable_low_hit: bool = True,
    enable_token_content: bool = True,
    low_task: TaskControl | None = None,
) -> bool:
    budget = RecommendationBudget.model_validate_json(__import__("json").dumps(snapshot["budget"]))
    if digest(budget) != snapshot["budget_digest"]:
        raise ValueError("RECOMMENDATION_SNAPSHOT_CHANGED")
    control = RecommendationControl(budget, task)
    publication_control = control
    reasons = []
    first_stop: str | None = None
    proposal_coverage = evaluation_coverage = None
    for stage in ("low_hit", "token"):
        if (stage == "low_hit" and not enable_low_hit) or (
            stage == "token" and not enable_token_content
        ):
            continue
        if stage == "token" and not snapshot["bundle"]["recipes"]:
            proposal_coverage = StageCoverage(
                eligible=0,
                checked=0,
                completed=0,
                advice_only=0,
                blocked=0,
                not_run=0,
                failed=0,
                complete=True,
                reason_codes=("NO_CONFIGURED_RECIPES",),
            )
            continue
        try:
            if stage == "low_hit":
                control.stop_location = "low_hit_publication"
                publication_control = (
                    RecommendationControl(budget, low_task)
                    if task.v2 and low_task is not None
                    else control
                )
                with task.telemetry.span("low_hit_publication"):
                    publish_low_hit(
                        source, writer, task_id, budget, low_hit_complete, publication_control
                    )
            else:
                outcome = run_token_recommendations(
                    source=source,
                    writer=writer,
                    workspace=workspace,
                    task_id=task_id,
                    snapshot=snapshot,
                    adapter=settings.registry.get() if settings else None,
                    control=control,
                )
                proposal_coverage = StageCoverage(
                    eligible=source.scope.request_count,
                    checked=outcome["checked"],
                    completed=outcome["checked"],
                    advice_only=0,
                    blocked=0,
                    not_run=0,
                    failed=0,
                    complete=True,
                )
                count = outcome["recommendations"]
                evaluation_coverage = StageCoverage(
                    eligible=count,
                    checked=count - outcome["not_run"],
                    completed=outcome["completed"],
                    advice_only=outcome["advice_only"],
                    blocked=outcome["blocked"],
                    not_run=outcome["not_run"],
                    failed=outcome["failed"],
                    complete=outcome["complete"],
                    reason_codes=tuple(outcome["reason_codes"]),
                )
                if not outcome["complete"]:
                    reasons.append("RECOMMENDATION_EXECUTION_INCOMPLETE")
                    reasons.extend(outcome["reason_codes"])
        except (ExecutionStopped, ValueError, KeyError, TypeError, RuntimeError) as exc:
            code = getattr(exc, "code", "RECOMMENDATION_STAGE_FAILED")
            if code == "ANALYSIS_INTERRUPTED":
                raise
            reasons.append(code)
            if first_stop is None:
                first_stop = control.stop_location or stage
            if stage == "token" and proposal_coverage is None:
                proposal_coverage = StageCoverage(
                    eligible=source.scope.request_count,
                    checked=control.scan_checked,
                    completed=control.scan_checked,
                    advice_only=0,
                    blocked=0,
                    failed=0,
                    not_run=0,
                    complete=control.scan_complete,
                    reason_codes=() if control.scan_complete else (code,),
                )
    complete = not reasons
    if enable_token_content and not snapshot["bundle"]["recipes"]:
        reasons.append("NO_CONFIGURED_RECIPES")
    if not enable_token_content:
        reasons.append("TOKEN_DIRECTION_DISABLED")
    consumed = dict(control.consumed)
    if publication_control is not control:
        for key, value in publication_control.consumed.items():
            consumed[key] = consumed.get(key, 0) + value
    for key, value in consumed.items():
        task.telemetry.count("recommendations." + key, value)
    summary = RecommendationSummary(
        task_id=task_id,
        scope_id=source.scope.scope_id,
        availability="computed",
        configured_recipe_count=len(snapshot["bundle"]["recipes"]),
        recommendation_count=sum(1 for _ in written_items(writer, "recommendation")),
        difference_group_count=sum(1 for _ in written_items(writer, "difference_group")),
        proposal_coverage=proposal_coverage,
        evaluation_coverage=evaluation_coverage,
        budget=budget,
        budget_digest=digest(budget),
        reason_codes=tuple(reasons),
        stop_location=first_stop or control.stop_location,
        consumed=BudgetConsumption(
            proposals=consumed.get("proposals", 0),
            recommendations=consumed.get("recommendations", 0),
            prepared_operations=consumed.get("prepared_operations", 0),
            total_plan_bytes=consumed.get("total_plan_bytes", 0),
            token_evaluations=consumed.get("token_evaluations", 0),
            encoding_calls=task.encoding_calls
            + (low_task.encoding_calls if task.v2 and low_task is not None else 0),
        ),
    )
    write_extension(writer, task_id, source.scope.scope_id, summary)
    return complete

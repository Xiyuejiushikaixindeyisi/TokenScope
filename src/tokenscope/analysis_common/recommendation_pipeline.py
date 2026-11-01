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
from tokenscope.analysis_common.runtime import TaskControl
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
) -> bool:
    budget = RecommendationBudget.model_validate_json(__import__("json").dumps(snapshot["budget"]))
    if digest(budget) != snapshot["budget_digest"]:
        raise ValueError("RECOMMENDATION_SNAPSHOT_CHANGED")
    control = RecommendationControl(budget, task)
    reasons = []
    first_stop: str | None = None
    proposal_coverage = evaluation_coverage = None
    for stage in ("low_hit", "token"):
        try:
            if stage == "low_hit":
                control.stop_location = "low_hit_publication"
                publish_low_hit(source, writer, task_id, budget, low_hit_complete, control)
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
    if not snapshot["bundle"]["recipes"]:
        reasons.append("NO_CONFIGURED_RECIPES")
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
            proposals=control.consumed.get("proposals", 0),
            recommendations=control.consumed.get("recommendations", 0),
            prepared_operations=control.consumed.get("prepared_operations", 0),
            total_plan_bytes=control.consumed.get("total_plan_bytes", 0),
            token_evaluations=control.consumed.get("token_evaluations", 0),
            encoding_calls=task.encoding_calls,
        ),
    )
    write_extension(writer, task_id, source.scope.scope_id, summary)
    return complete

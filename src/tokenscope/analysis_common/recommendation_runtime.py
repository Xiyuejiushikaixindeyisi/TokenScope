"""Submission-frozen configuration and task-wide recommendation resources."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.proposal_plugins import ProposalRegistry
from tokenscope.analysis_common.recommendation_grouping import digest
from tokenscope.analysis_common.recommendations import RecipeBundle, RecommendationBudget
from tokenscope.analysis_common.runtime import TaskControl


@dataclass
class RecommendationSettings:
    registry: ProposalRegistry
    bundle: RecipeBundle | Path
    budget: RecommendationBudget = field(default_factory=RecommendationBudget)

    def snapshot(self, token_enabled: bool = True) -> dict[str, Any]:
        if not token_enabled:
            bundle = RecipeBundle(bundle_id="token-direction-disabled", revision="1", recipes=())
            return {
                "version": "analysis-recommendations-1",
                "bundle": bundle.model_dump(mode="json"),
                "bundle_digest": digest(bundle),
                "budget": self.budget.model_dump(mode="json"),
                "budget_digest": digest(self.budget),
                "adapter": None,
            }
        if isinstance(self.bundle, Path) and self.bundle.stat().st_size > 8 * 1024 * 1024:
            raise ValueError("RECIPE_BUNDLE_BYTES_EXHAUSTED")
        bundle = (
            RecipeBundle.model_validate_json(self.bundle.read_bytes())
            if isinstance(self.bundle, Path)
            else self.bundle
        )
        adapter = self.registry.get()
        if adapter:
            bundle = adapter.validate_bundle(bundle)
        bundle = RecipeBundle.model_validate_json(bundle.model_dump_json())
        if len(bundle.model_dump_json().encode()) > 8 * 1024 * 1024:
            raise ValueError("RECIPE_BUNDLE_BYTES_EXHAUSTED")
        if any(r.primary_rule not in ("T2", "T3", "T4") for r in bundle.recipes):
            raise ValueError("RECIPE_RULE_OUT_OF_SCOPE")
        return {
            "version": "analysis-recommendations-1",
            "bundle": bundle.model_dump(mode="json"),
            "bundle_digest": digest(bundle),
            "budget": self.budget.model_dump(mode="json"),
            "budget_digest": digest(self.budget),
            "adapter": adapter.describe().model_dump(mode="json") if adapter else None,
        }


@dataclass
class RecommendationControl:
    budget: RecommendationBudget
    task: TaskControl
    consumed: dict[str, int] = field(default_factory=dict)
    scan_checked: int = 0
    scan_complete: bool = False
    stop_location: str | None = None

    def consume(self, resource: str, amount: int = 1) -> None:
        self.task.checkpoint()
        if type(amount) is not int or amount < 0:
            raise ValueError("Invalid recommendation resource amount")
        field_name = "max_" + resource
        if field_name not in RecommendationBudget.model_fields:
            raise ValueError("Unknown recommendation resource")
        total = self.consumed.get(resource, 0) + amount
        if total > getattr(self.budget, field_name):
            raise ExecutionStopped("RECOMMENDATION_" + resource.upper() + "_EXHAUSTED")
        self.consumed[resource] = total

    def item_size(self, resource: str, size: int) -> None:
        self.task.checkpoint()
        if size > getattr(self.budget, "max_" + resource):
            raise ExecutionStopped("RECOMMENDATION_" + resource.upper() + "_EXHAUSTED")

    def plan(self, size: int) -> None:
        self.task.plan(size)
        self.item_size("plan_bytes", size)
        self.consume("total_plan_bytes", size)

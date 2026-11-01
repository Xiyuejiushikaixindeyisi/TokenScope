from types import SimpleNamespace

import pytest

from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.recommendation_runtime import RecommendationControl
from tokenscope.analysis_common.recommendations import RecommendationBudget


@pytest.mark.parametrize(
    "resource",
    [
        "proposals",
        "recommendations",
        "prepared_operations",
        "total_plan_bytes",
        "token_evaluations",
    ],
)
def test_budget_exact_boundary_and_failed_consumption(resource):
    task = SimpleNamespace(checkpoint=lambda: None)
    control = RecommendationControl(RecommendationBudget(), task)
    limit = getattr(control.budget, "max_" + resource)
    control.consume(resource, limit)
    with pytest.raises(ExecutionStopped, match="EXHAUSTED"):
        control.consume(resource, 1)
    assert control.consumed[resource] == limit
    with pytest.raises(ValueError):
        control.consume(resource, True)


@pytest.mark.parametrize("resource", ["proposal_bytes", "plan_bytes", "example_bytes_per_group"])
def test_single_object_boundaries(resource):
    control = RecommendationControl(
        RecommendationBudget(), SimpleNamespace(checkpoint=lambda: None)
    )
    limit = getattr(control.budget, "max_" + resource)
    control.item_size(resource, limit)
    with pytest.raises(ExecutionStopped):
        control.item_size(resource, limit + 1)

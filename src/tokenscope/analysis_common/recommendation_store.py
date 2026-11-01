"""Typed extension writer using the existing atomic result store."""

from tokenscope.analysis_common.contracts import Contract
from tokenscope.analysis_common.recommendations import (
    DifferenceGroup,
    Recommendation,
    RecommendationExample,
    RecommendationSummary,
)
from tokenscope.analysis_common.storage import ResultWriter
from tokenscope.analysis_common.wire import to_wire

EXTENSION_MODELS: dict[str, type[Contract]] = {
    "recommendation": Recommendation,
    "difference_group": DifferenceGroup,
    "recommendation_example": RecommendationExample,
    "recommendation_summary": RecommendationSummary,
}


def write_extension(
    writer: ResultWriter,
    task_id: str,
    scope_id: str,
    item: Recommendation | DifferenceGroup | RecommendationExample | RecommendationSummary,
) -> None:
    mapping = {
        Recommendation: ("recommendation", "recommendation_id"),
        DifferenceGroup: ("difference_group", "group_id"),
        RecommendationExample: ("recommendation_example", "example_id"),
        RecommendationSummary: ("recommendation_summary", "task_id"),
    }
    if type(item) not in mapping:
        raise ValueError("Unknown extension model")
    item = type(item).model_validate_json(item.model_dump_json())
    if (item.task_id, item.scope_id) != (task_id, scope_id):
        raise ValueError("Extension has foreign task/scope")
    kind, field = mapping[type(item)]
    writer.add(kind, getattr(item, field), to_wire(item))

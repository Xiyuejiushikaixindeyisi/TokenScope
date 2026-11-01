"""Public reason categories; never infer publication state from translated text."""

from typing import Literal

ReasonClass = Literal["business", "technical", "interrupted"]
REASONS: dict[str, ReasonClass] = {
    "RECIPE_BASIS_MISSING": "business",
    "REFERENCE_MAPPING_MISSING": "business",
    "NO_MATCHED_TARGETS": "business",
    "HYPOTHESIS_DISABLED": "business",
    "BASIS_INVALID": "technical",
    "AUTHORIZATION_SCOPE_MISMATCH": "technical",
    "AUTO_ADAPTER_UNAVAILABLE": "technical",
    "RECIPE_BUNDLE_INVALID": "technical",
    "RECOMMENDATION_BUDGET_EXHAUSTED": "technical",
    "PROPOSAL_FAILED": "technical",
    "PREPARATION_FAILED": "technical",
    "EVALUATION_FAILED": "technical",
    "EVIDENCE_LOCATION_AMBIGUOUS": "business",
    "EVIDENCE_LOCATION_UNAVAILABLE": "business",
    "ANALYSIS_INTERRUPTED": "interrupted",
}


def reason_class(code: str) -> ReasonClass:
    # Unknown private guard/budget errors fail closed; they never imply "no business basis".
    return REASONS.get(code, "technical")

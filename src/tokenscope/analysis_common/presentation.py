"""Saved evaluation views retain exact fractions, costs, and independent display gates."""

from typing import Any

from tokenscope.analysis_common.contracts import EvaluationResult, gain_percentage_points
from tokenscope.analysis_common.wire import to_wire


def evaluation_view(result: EvaluationResult) -> dict[str, Any]:
    payload = to_wire(result)
    gain = (
        gain_percentage_points(result.before, result.after)
        if result.before and result.after
        else None
    )
    payload.update(
        gate_passed=result.gate_passed,
        display_eligible=result.display_eligible,
        gain_percentage_points=None
        if gain is None
        else {"numerator": str(gain.numerator), "denominator": str(gain.denominator)},
        compute_tokens_delta=str(result.after.c - result.before.c)
        if result.before and result.after
        else None,
    )
    return payload

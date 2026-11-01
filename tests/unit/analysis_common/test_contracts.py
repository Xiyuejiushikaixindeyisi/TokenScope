from fractions import Fraction

import pytest
from pydantic import ValidationError

from tokenscope.analysis_common.contracts import (
    DiagnosticSelection,
    InputMetrics,
    RequestKey,
    gain_percentage_points,
    passes_gain_gate,
)


@pytest.mark.parametrize("hits,passed", [(6099, False), (6100, False), (6101, True)])
def test_absolute_gate(hits: int, passed: bool) -> None:
    before = InputMetrics(p=10000, h=6000, c=4000)
    after = InputMetrics(p=10000, h=hits, c=10000 - hits)
    assert passes_gain_gate(before, after, complete=True) is passed
    assert not passes_gain_gate(before, after, complete=False)


def test_no_float_rounding_at_large_boundary() -> None:
    total = 10**20
    before = InputMetrics(p=total, h=60 * total // 100, c=40 * total // 100)
    hits = 61 * total // 100 + 1
    after = InputMetrics(p=total, h=hits, c=total - hits)
    assert gain_percentage_points(before, after) == 1 + Fraction(100, total)
    assert passes_gain_gate(before, after, complete=True)


def test_zero_denominator_and_bad_conservation() -> None:
    zero = InputMetrics(p=0, h=0, c=0)
    assert gain_percentage_points(zero, zero) is None
    assert not passes_gain_gate(zero, zero, complete=True)
    with pytest.raises(ValidationError):
        InputMetrics(p=10, h=7, c=4)


@pytest.mark.parametrize("reason", ["request_length", "qps"])
def test_token_only_route(reason: str) -> None:
    selection = DiagnosticSelection.model_validate(
        {
            "reason_codes": (reason,),
            "enable_low_hit": False,
            "enable_token_content": True,
        }
    )
    assert selection.stages == ("token_content",)


def test_low_hit_route_and_conflict() -> None:
    selection = DiagnosticSelection(
        reason_codes=("low_hit", "qps"),
        enable_low_hit=True,
        enable_token_content=True,
    )
    assert selection.stages == ("low_hit", "token_content")
    with pytest.raises(ValidationError):
        DiagnosticSelection(
            reason_codes=("low_hit",),
            enable_low_hit=False,
            enable_token_content=True,
        )


def test_request_identity_is_not_display_hash() -> None:
    assert RequestKey(base_run_id="r", source_record_index=1) != RequestKey(
        base_run_id="r",
        source_record_index=2,
    )
    with pytest.raises(ValidationError):
        RequestKey(base_run_id="r", source_record_index=True)

import pytest
from pydantic import ValidationError

from tokenscope.monitoring.ma.contracts import Coverage, Submit, TokenTotals


def test_windows() -> None:
    payload = dict(
        submission_key="one",
        pre_file_ref="pre",
        now_file_ref="now",
        model_standard_name="q-64K",
        model_id="Qwen3.6-27B",
        pre_start="2026-10-20T07:00:00Z",
        now_start="2026-10-20T08:00:00Z",
        now_end="2026-10-20T09:00:00Z",
    )
    Submit.model_validate(payload)
    with pytest.raises(ValidationError):
        Submit.model_validate({**payload, "now_end": "2026-10-20T09:00:01Z"})
    with pytest.raises(ValidationError):
        Submit.model_validate({**payload, "now_file_ref": "pre"})


def test_coverage_intersection() -> None:
    Coverage(assigned="10", production_input="8", real="7", encoded="6", paired="3")
    with pytest.raises(ValidationError):
        Coverage(assigned="10", production_input="8", real="7", encoded="6", paired="2")


def test_exact_totals_and_zero() -> None:
    assert TokenTotals(input_tokens="0", cached_tokens="0", uncached_tokens="0").hit_rate() is None
    total = TokenTotals(
        input_tokens="9007199254740993", cached_tokens="1", uncached_tokens="9007199254740992"
    )
    assert total.input_tokens == "9007199254740993"
    with pytest.raises(ValidationError):
        TokenTotals(input_tokens="1", cached_tokens="2", uncached_tokens="0")
    with pytest.raises(ValidationError):
        TokenTotals(input_tokens="01", cached_tokens="0", uncached_tokens="1")

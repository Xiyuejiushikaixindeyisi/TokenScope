"""TA000 consumer checks against the currently available LH000 types.

These checks do not certify a frozen schema or a working plugin registry.
"""

import pytest
from pydantic import ValidationError

from tokenscope.analysis_common.contracts import DiagnosticSelection, RequestKey


@pytest.mark.parametrize(
    ("reasons", "low_hit", "stages"),
    [
        (("low_hit",), True, ("low_hit", "token_content")),
        (("request_length",), False, ("token_content",)),
        (("qps",), False, ("token_content",)),
        (("low_hit", "qps"), True, ("low_hit", "token_content")),
    ],
)
def test_token_direction_routing(reasons, low_hit, stages):
    selection = DiagnosticSelection(
        reason_codes=reasons, enable_low_hit=low_hit, enable_token_content=True
    )
    assert selection.stages == stages


@pytest.mark.parametrize(
    ("reasons", "low_hit", "token"),
    [
        ((), False, True),
        (("qps", "qps"), False, True),
        (("low_hit",), False, True),
        (("qps",), True, True),
        (("request_length",), False, False),
        (("unknown",), False, True),
    ],
)
def test_conflicting_selection_is_rejected(reasons, low_hit, token):
    with pytest.raises(ValidationError):
        DiagnosticSelection(
            reason_codes=reasons, enable_low_hit=low_hit, enable_token_content=token
        )


def test_request_identity_retains_source_row_and_run():
    first = RequestKey(base_run_id="run-a", source_record_index=1)
    assert first != RequestKey(base_run_id="run-a", source_record_index=2)
    assert first != RequestKey(base_run_id="run-b", source_record_index=1)
    with pytest.raises(ValidationError):
        first.source_record_index = 2

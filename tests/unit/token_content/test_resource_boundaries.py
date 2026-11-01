import pytest
from test_extraction import control, view

from tokenscope.analysis_common.plugins import EvidenceCapabilities, PluginSelection, RunControl
from tokenscope.token_content.plugin import TokenContentPlugin


@pytest.mark.parametrize(
    "resource",
    ["max_request_bytes", "max_units", "max_comparison_bytes", "max_candidates", "max_depth"],
)
@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_budget_below_equal_above_exact_need(resource, offset):
    messages = [{"role": "tool", "content": "ok"}, {"role": "user", "content": "ok"}]
    if resource == "max_candidates":
        messages.extend([{"role": "tool", "content": "yes"}, {"role": "user", "content": "yes"}])
    request = view({"messages": messages})
    need = {
        "max_request_bytes": len(request.raw_body.encode()),
        "max_units": 2,
        "max_comparison_bytes": 8,
        "max_candidates": 2,
        "max_depth": 3,
    }[resource]
    runtime = control(**{resource: need + offset})
    selection = PluginSelection(rule_ids=("T3",), budget=runtime.budget)
    result = TokenContentPlugin().analyze_request(
        request, selection, EvidenceCapabilities(), runtime
    )
    assert result.coverage.complete == (offset >= 0)
    if offset < 0:
        assert "ANALYSIS_BUDGET_EXHAUSTED" in result.reason_codes
        assert result.rule_results[0].condition == "unknown"
        assert result.rule_results[0].status in ("not_checked", "partial")
        assert result.rule_results[0].coverage.stop_location is not None
    else:
        assert result.rule_results[0].condition == "met"


def test_cancellation_during_extraction_and_fresh_retry_are_independent():
    request = view(
        {
            "messages": [
                {"role": "tool", "content": "payload"},
                {"role": "user", "content": "payload"},
            ]
        }
    )
    checkpoints = 0

    def cancelled():
        nonlocal checkpoints
        checkpoints += 1
        return checkpoints >= 4

    plugin = TokenContentPlugin()
    selection = PluginSelection(rule_ids=("T3",), budget=control().budget)
    interrupted = plugin.analyze_request(
        request, selection, EvidenceCapabilities(), RunControl(selection.budget, cancelled)
    )
    assert interrupted.reason_codes == ("ANALYSIS_INTERRUPTED",)
    assert not interrupted.coverage.complete
    retry = plugin.analyze_request(request, selection, EvidenceCapabilities(), control())
    assert retry.coverage.complete and len(retry.observations) == 1
    assert interrupted.observations == ()

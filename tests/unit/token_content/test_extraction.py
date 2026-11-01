import json

import pytest

from tokenscope.analysis_common.contracts import (
    BaselineMetrics,
    Participation,
    RequestKey,
    RequestView,
)
from tokenscope.analysis_common.plugins import (
    BudgetSpec,
    EvidenceCapabilities,
    ExecutionStopped,
    RunControl,
)
from tokenscope.token_content.extraction import extract
from tokenscope.token_content.json_values import ContentError, Number, digest, dumps, loads, resolve
from tokenscope.token_content.measurements import measure


def view(body, **updates):
    raw = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
    values = dict(
        request_key=RequestKey(base_run_id="r", source_record_index=0),
        scope_id="scope",
        appid="a",
        time_ns=0,
        hash_id="h",
        raw_body=raw,
        raw_sha256=digest(raw),
        raw_body_complete=True,
        baseline_metrics=BaselineMetrics(j=0, p=0),
        encoder_identity="e",
        asset_identity="a",
        effective_options_json="{}",
    )
    return RequestView(**(values | updates))


def control(**updates):
    return RunControl(
        BudgetSpec(
            **(
                dict(
                    max_request_bytes=1_000_000,
                    max_units=1000,
                    max_comparison_bytes=1_000_000,
                    max_depth=40,
                    max_candidates=100,
                    max_encoding_calls=1,
                )
                | updates
            )
        )
    )


def inventory(body, evidence=None):
    return extract(view(body), evidence or EvidenceCapabilities(), control())


@pytest.mark.parametrize("raw", ['{"x":1,"x":2}', "NaN", "Infinity", '"\\ud800"', "{"])
def test_invalid_json_rejected(raw):
    with pytest.raises(ContentError, match="INVALID_JSON"):
        loads(raw, max_depth=20)


def test_exact_values_and_pointer():
    raw = '{"z":123456789012345678901234567890,"1":1.0,"a/~":[true,1e10000]}'
    parsed = loads(raw, max_depth=10)
    assert dumps(parsed) == raw
    assert resolve(parsed, "/a~1~0/1") == Number("1e10000")
    assert resolve(parsed, "/1") == Number("1.0")
    assert resolve(parsed, "") is parsed
    with pytest.raises(ContentError):
        resolve(parsed, "/a~1~0/01")
    with pytest.raises(ContentError, match="BUDGET"):
        loads("[[[0]]]", max_depth=2)
    assert loads('"[[["', max_depth=1) == "[[["


def test_unicode_measures_and_parts_order():
    text = "中😀e\u0301\n\n"
    assert measure(text) == {"utf8_bytes": 12, "unicode_codepoints": 6, "lines": 2}
    result = inventory(
        {
            "messages": [
                {
                    "role": "tool",
                    "content": [
                        {"type": "text", "text": text},
                        {"type": "image", "url": "x"},
                        {"type": "input_text", "text": "end"},
                    ],
                }
            ]
        }
    )
    assert len(result.entries) == 3
    parent, first, last = result.entries
    assert [first.value, last.value] == [text, "end"]
    assert first.unit.container_unit_id == last.unit.container_unit_id == parent.unit.unit_id
    assert parent.unit.facets == ("tool_result", "history_tool_result")
    assert last.location.source_pointer == "/messages/0/content/2/text"


def test_embedded_identity_and_no_inherited_participation():
    body = {"messages": [{"role": "tool", "content": '{"a/~":12345678901234567890}'}]}
    evidence = EvidenceCapabilities(
        participation=(
            (
                "/messages/0/content",
                Participation(status="included", evidence_method="fixture", encoding_identity="e"),
            ),
        )
    )
    result = inventory(body, evidence)
    outer, root, field = result.entries
    assert outer.location.embedded is None
    assert root.location.embedded.pointer == ""
    assert field.location.embedded.pointer == "/a~1~0"
    assert outer.unit.participation.status == "included"
    assert root.unit.participation.status == field.unit.participation.status == "unknown"
    assert field.value == Number("12345678901234567890")
    assert len({e.location.location_id for e in result.entries}) == 3
    assert len({e.unit.unit_id for e in result.entries}) == 3


def test_malformed_inner_is_local_and_full_source_past_preview_used():
    result = inventory(
        {
            "messages": [
                {"role": "tool", "content": '{"x":1,"x":2}'},
                {"role": "tool", "content": "a" * 70_000 + "终"},
            ]
        }
    )
    assert result.local_errors == (("/messages/0/content", "INVALID_EMBEDDED_JSON"),)
    assert result.entries[-1].measures["utf8_bytes"] == 70_003
    assert result.entries[-1].value.endswith("终")


def test_tool_identity_ambiguity_and_protocol_exclusion():
    body = {
        "tools": [
            {"type": "function", "function": {"name": "f", "description": "a"}},
            {"type": "function", "function": {"name": "f", "description": "b"}},
        ],
        "messages": [
            {
                "role": "assistant",
                "tool_calls": [
                    {"id": "id", "function": {"name": "f", "arguments": '{"document":"data"}'}}
                ],
            },
            {"role": "tool", "tool_call_id": "id", "content": "data"},
            {"role": "tool", "tool_call_id": "missing", "content": "data"},
        ],
    }
    result = inventory(body)
    returns = [e for e in result.entries if "tool_result" in e.unit.facets]
    assert [e.identity_status for e in returns] == ["ambiguous", "missing"]
    assert not any(e.location.source_pointer.endswith("/id") for e in result.entries)
    assert any(
        e.location.embedded and e.location.embedded.pointer == "/document" for e in result.entries
    )
    body["tools"].pop()
    body["messages"][0]["tool_calls"].append(body["messages"][0]["tool_calls"][0])
    result = inventory(body)
    assert [e.identity_status for e in result.entries if "tool_result" in e.unit.facets] == [
        "ambiguous",
        "missing",
    ]


def test_source_boundary_budgets_cancellation_and_stable_ids():
    request = view({"messages": [{"role": "tool", "content": "x"}]})
    caps = EvidenceCapabilities()
    with pytest.raises(ContentError, match="INCOMPLETE_BODY"):
        extract(request.model_copy(update={"raw_body_complete": False}), caps, control())
    with pytest.raises(ContentError, match="BUDGET"):
        extract(request, caps, control(max_request_bytes=1))
    with pytest.raises(ExecutionStopped, match="INTERRUPTED"):
        extract(request, caps, RunControl(control().budget, cancelled=lambda: True))
    first = extract(request, caps, control())
    assert first == extract(request, caps, control())
    second = extract(
        request.model_copy(
            update={"request_key": RequestKey(base_run_id="r", source_record_index=1)}
        ),
        caps,
        control(),
    )
    assert first.entries[0].unit.unit_id != second.entries[0].unit.unit_id

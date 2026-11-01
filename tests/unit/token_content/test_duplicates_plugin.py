import json

import pytest
from test_extraction import control, inventory, view

from tokenscope.analysis_common.plugins import EvidenceCapabilities, PluginRegistry, PluginSelection
from tokenscope.token_content.duplicates import run_duplicates
from tokenscope.token_content.plugin import TokenContentPlugin


def duplicate(body):
    return run_duplicates(inventory(body), control())


def test_three_payloads_count_once_and_no_execution_claim():
    body = {
        "messages": [
            {"role": "tool", "content": "中文"},
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "x",
                        "function": {
                            "name": "f",
                            "arguments": '{"document":"中文","another":"中文"}',
                        },
                    }
                ],
            },
        ]
    }
    result = duplicate(body)
    assert len(result.observations) == 1
    details = json.loads(result.observations[0].details_json)
    assert details["occurrences"] == 3 and details["repeated_utf8_bytes"] == 12
    assert details["execution_count"] is None and details["saved_tokens"] is None
    assert not result.findings


@pytest.mark.parametrize("other", ["payload!", "pre payload", "PAYLOAD"])
def test_no_substring_or_semantic_duplicates(other):
    assert not duplicate(
        {"messages": [{"role": "tool", "content": "payload"}, {"role": "user", "content": other}]}
    ).observations


def test_only_cross_request_or_no_tool_does_not_match():
    body = {"messages": [{"role": "tool", "content": "normal history"}]}
    assert not duplicate(body).observations and not duplicate(body).observations
    assert not duplicate(
        {"messages": [{"role": "user", "content": "x"}, {"role": "assistant", "content": "x"}]}
    ).observations


def test_structural_key_order_numeric_types_and_overlap():
    body = {
        "messages": [
            {"role": "tool", "content": '{"x":{"a":1,"b":true}}'},
            {"role": "user", "content": '{"x":{"b":true,"a":1}}'},
        ]
    }
    result = duplicate(body)
    assert len(result.observations) == 1  # outer object suppresses nested object
    assert json.loads(result.observations[0].details_json)["repeated_utf8_bytes"] is None
    body["messages"][1]["content"] = '{"x":{"b":true,"a":1.0}}'
    assert not duplicate(body).observations
    body["messages"][1]["content"] = '{"x":{"a":1,"b":1}}'
    assert not duplicate(body).observations


def test_hash_collision_requires_exact_value(monkeypatch):
    monkeypatch.setattr("tokenscope.token_content.duplicates.digest", lambda _: "collision")
    result = duplicate(
        {"messages": [{"role": "tool", "content": "one"}, {"role": "user", "content": "two"}]}
    )
    assert not result.observations


def test_short_ok_is_fact_not_anomaly():
    result = duplicate(
        {"messages": [{"role": "tool", "content": "ok"}, {"role": "user", "content": "ok"}]}
    )
    assert len(result.observations) == 1 and not result.findings


def test_plugin_registration_shared_evidence_and_partial():
    plugin = TokenContentPlugin()
    registry = PluginRegistry()
    registry.register(plugin)
    assert registry.get("token_content") is plugin
    request = view(
        {"messages": [{"role": "tool", "content": "ok"}, {"role": "user", "content": "ok"}]}
    )
    selected = PluginSelection(rule_ids=("T1", "T2", "T3", "T4"), budget=control().budget)
    fragment = plugin.analyze_request(request, selected, EvidenceCapabilities(), control())
    assert fragment.coverage.complete and len(fragment.units) == 2
    assert len({u.unit_id for u in fragment.units}) == 2
    assert [r.rule_id for r in fragment.rule_results] == ["T1", "T2", "T3", "T4"]
    limited = plugin.analyze_request(
        request, selected, EvidenceCapabilities(), control(max_comparison_bytes=1)
    )
    assert not limited.coverage.complete
    assert [r.status for r in limited.rule_results] == [
        "not_applicable",
        "completed",
        "partial",
        "not_checked",
    ]
    assert limited.observations  # prior T2 inventory survives T3 stop
    cancelled = plugin.analyze_request(
        request,
        selected,
        EvidenceCapabilities(),
        type(control())(control().budget, cancelled=lambda: True),
    )
    assert cancelled.reason_codes == ("ANALYSIS_INTERRUPTED",)
    assert all(r.status == "not_checked" for r in cancelled.rule_results)


def test_plugin_unknown_inner_parse_and_no_silent_rule_selection():
    plugin = TokenContentPlugin()
    selected = PluginSelection(rule_ids=("T2",), budget=control().budget)
    result = plugin.analyze_request(
        view({"messages": [{"role": "tool", "content": '{"x":1,"x":2}'}]}),
        selected,
        EvidenceCapabilities(),
        control(),
    )
    assert result.rule_results[0].status == "partial"
    assert result.rule_results[0].condition == "unknown"
    assert result.observations
    with pytest.raises(ValueError):
        plugin.validate_selection(
            PluginSelection(rule_ids=("parameters",), budget=control().budget)
        )


def test_generated_candidates_are_pending_and_references_resolve():
    plugin = TokenContentPlugin()
    request = view({"messages": [{"role": "tool", "content": '[{"a":1,"b":2}]'}]})
    selected = PluginSelection(rule_ids=("T2",), budget=control().budget)
    result = plugin.analyze_request(request, selected, EvidenceCapabilities(), control())
    assert {c.handler_id for c in result.modification_candidates} == {
        "select_result_lines",
        "project_result_fields",
        "select_result_items",
    }
    finding_ids = {f.finding_id for f in result.finding_candidates}
    assert all(set(c.finding_refs) <= finding_ids for c in result.modification_candidates)
    for candidate in result.modification_candidates:
        assert "business_basis_ref" in candidate.missing_parameters
        assert plugin.prepare_mutation(request, candidate, "{}", None).status == "blocked"
    assert result == plugin.analyze_request(request, selected, EvidenceCapabilities(), control())


def test_description_candidate_does_not_offer_schema_edits():
    plugin = TokenContentPlugin()
    request = view(
        {
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "f",
                        "description": "summary",
                        "parameters": {
                            "type": "object",
                            "properties": {"x": {"type": "string", "description": "field"}},
                        },
                    },
                }
            ]
        }
    )
    result = plugin.analyze_request(
        request,
        PluginSelection(rule_ids=("T1",), budget=control().budget),
        EvidenceCapabilities(),
        control(),
    )
    assert [c.locations[0].source_pointer for c in result.modification_candidates] == [
        "/tools/0/function/description"
    ]

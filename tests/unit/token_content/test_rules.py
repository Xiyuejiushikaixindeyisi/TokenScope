import json

import pytest
from pydantic import ValidationError
from test_extraction import control, inventory

from tokenscope.token_content.policies import PolicySpec, parse_policies
from tokenscope.token_content.rules import run_inventory_rule


def policy(rule="T2", **updates):
    return PolicySpec(
        **(
            dict(
                policy_id="p",
                revision="1",
                source="business fixture",
                rule_id=rule,
                kind="limit",
                unit="utf8_bytes",
                limit=3,
            )
            | updates
        )
    )


def run(rule, body, *policies):
    data = inventory(body)
    return run_inventory_rule(
        rule,
        data,
        policies,
        control(),
        capture_truncation="unknown",
        message_count=data.message_count,
    )


def test_no_policy_is_facts_not_anomaly_and_shared_units():
    body = {"messages": [{"role": "tool", "content": "x" * 10000}]}
    t2, t4 = run("T2", body), run("T4", body)
    assert not t2.findings and not t4.findings
    assert t2.result.condition == t4.result.condition == "unknown"
    assert t2.observations[0].unit_ids == t4.observations[0].unit_ids
    facts = json.loads(t2.observations[0].details_json)
    assert facts["capture_truncation"] == "unknown"
    assert facts["token_contribution"] is None
    assert (
        run("T2", {"messages": [{"role": "user", "content": "x" * 10000}]}).result.status
        == "not_applicable"
    )


@pytest.mark.parametrize("limit,expected", [(2, "met"), (3, "not_met"), (4, "not_met")])
def test_budget_boundaries(limit, expected):
    result = run("T2", {"messages": [{"role": "tool", "content": "abc"}]}, policy(limit=limit))
    assert result.result.condition == expected
    assert len(result.findings) == (expected == "met")


def test_incompatible_units_and_unproven_model_participation():
    body = {"messages": [{"role": "tool", "content": "abcd"}]}
    for p in (policy(unit="tokens"), policy(basis="model_input")):
        result = run("T2", body, p)
        assert result.result.condition == "unknown" and not result.findings


def test_t1_rank_components_no_unused_tool_claim():
    body = {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "unused",
                    "description": "long description",
                    "parameters": {"type": "object"},
                },
            },
            {"type": "function", "function": {"name": "short"}},
        ]
    }
    result = run("T1", body)
    assert len(result.observations) == 2 and not result.findings
    assert json.loads(result.observations[0].details_json)["tool_name"] == "unused"
    assert len(json.loads(result.observations[0].details_json)["components"]) == 2
    assert run("T1", {"tools": []}).result.status == "completed"
    assert run("T1", {}).result.status == "not_applicable"


def test_field_allowlist_requires_exact_level_and_reports_rows():
    body = {"messages": [{"role": "tool", "content": '[{"a":1,"b":2},{"a":3}]'}]}
    p = policy(
        kind="field_allowlist",
        unit=None,
        limit=None,
        allowed_fields=("a",),
        field_level="array_items",
        source_pointer="/messages/0/content",
        embedded_pointer="",
    )
    result = run("T2", body, p)
    assert result.result.condition == "met"
    checks = [o for o in result.observations if o.policy_digest]
    assert len(checks) == 1
    assert json.loads(checks[0].details_json)["extra_fields"] == [{"row": 0, "fields": ["b"]}]
    body["messages"][0]["content"] = '[{"a":1},2]'
    assert run("T2", body, p).result.condition == "unknown"


@pytest.mark.parametrize("keep,exceeded", [(0, 2), (1, 1), (2, 0), (3, 0)])
def test_retention_counts_containers_not_text_parts(keep, exceeded):
    body = {
        "messages": [
            {
                "role": "tool",
                "content": [{"type": "text", "text": "a"}, {"type": "text", "text": "b"}],
            },
            {"role": "user", "content": "c"},
            {"role": "tool", "content": "d"},
        ]
    }
    p = policy("T4", kind="retain_last", unit=None, limit=None, keep_last=keep)
    result = run("T4", body, p)
    assert len(result.findings) == exceeded
    assert len([o for o in result.observations if o.policy_digest]) == 2
    assert json.loads(result.observations[0].details_json)["later_message_count"] == 2


def test_policy_validation_and_identity_versions():
    with pytest.raises(ValidationError):
        policy(tool_name="unknown")
    with pytest.raises(ValidationError):
        policy("T4", kind="retain_last", unit=None, limit=None)
    with pytest.raises(ValidationError):
        policy(limit=True)
    with pytest.raises(ValueError):
        parse_policies("[" + policy().model_dump_json() + "," + policy().model_dump_json() + "]")
    body = {"messages": [{"role": "tool", "content": "abcd"}]}
    first, second = run("T2", body, policy()), run("T2", body, policy(revision="2"))
    assert first.observations[-1].observation_id != second.observations[-1].observation_id
    assert first.observations[-1].unit_ids == second.observations[-1].unit_ids

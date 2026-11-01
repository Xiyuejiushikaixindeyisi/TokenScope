import json

import pytest
from test_diagnostic_tasks import options, setup

from tokenscope.errors import TokenScopeError


def test_real_cross_direction_combination_and_atomic_conflict(service):
    diagnostics, request = setup(service, True)
    task = diagnostics.submit(request, options())
    assert diagnostics.process_next().status in ("ready", "partial")
    finding = next(
        f for f in diagnostics.items(task.task_id, "finding") if f["data"]["rule_id"] == "L1"
    )
    low = diagnostics.submit_low_hit_evaluation(task.task_id, (finding["id"],), "low")
    assert diagnostics.process_next().status == "ready"
    low_plan = diagnostics.items(low.task_id, "plan")[0]["id"]
    fragment = diagnostics.items(task.task_id, "fragment")[0]
    candidate = next(
        c
        for c in fragment["data"]["modification_candidates"]
        if c["handler_id"] == "replace_tool_description"
    )
    tokens = []
    for i, value in enumerate(("short", "different")):
        token = diagnostics.submit_token_evaluation(
            task.task_id,
            fragment["id"],
            candidate["candidate_id"],
            json.dumps({"replacement_json": json.dumps(value)}),
            "explicit-test-basis",
            f"token-{i}",
        )
        assert diagnostics.process_next().status == "ready"
        tokens.append(
            {"task_id": token.task_id, "plan_id": diagnostics.items(token.task_id, "plan")[0]["id"]}
        )
    joined = diagnostics.submit_combination(
        task.task_id, [{"task_id": low.task_id, "plan_id": low_plan}, tokens[0]], "joined"
    )
    assert diagnostics.process_next().status == "ready"
    result = diagnostics.items(joined.task_id, "evaluation")[0]["data"]
    assert result["direction"] == "combined" and result["gate_passed"] is None
    assert result["before"]["n"] == result["after"]["n"] == "6"
    conflict = diagnostics.submit_combination(task.task_id, tokens, "conflict")
    assert diagnostics.process_next().status == "partial"
    failed = diagnostics.items(conflict.task_id, "evaluation")[0]["data"]
    assert failed["after"] is None and failed["reason_codes"] == ["PLAN_OPERATION_CONFLICT"]
    assert diagnostics.items(tokens[0]["task_id"], "evaluation")[0]["data"]["status"] == "available"
    with pytest.raises(TokenScopeError):
        diagnostics.submit_combination(task.task_id, [tokens[0], tokens[0]], "duplicate")
    with pytest.raises(TokenScopeError):
        diagnostics.submit_combination(
            task.task_id, [tokens[0], {"task_id": low.task_id, "plan_id": "foreign"}], "foreign"
        )

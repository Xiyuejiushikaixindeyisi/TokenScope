"""Normal V3 execution must retain non-clock low-hit behavior and complete evidence."""

import hashlib
import json

import pytest
from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.contracts_v3 import PreparationRequest3
from tokenscope.analysis_common.report_v3 import SampleReport3
from tokenscope.analysis_common.service_v3 import PreparationService
from tokenscope.analysis_common.wire_v3 import from_wire
from tokenscope.api.app import create_app
from tokenscope.domain import RunSubmission
from tokenscope.user_monitoring.service import UserRunService


def body(case, i):
    value = {
        "messages": [
            {"role": "system", "content": "stable " * 80},
            {"role": "user", "content": "hello"},
        ]
    }
    token = ["alpha", "betabetabetabetabeta"][i % 2]
    text = {
        "cch": "x-anthropic-billing-header: cc_version=1; cch=" + token + ";\n",
        "plain_timestamp": f"date 2026/11/{10 + i % 2} 09:00:00",
        "workspace": "/workspace/" + token,
    }.get(case)
    if text:
        value["messages"][0]["content"] = text + "\n" + "stable " * 80

    def tool(name, description="stable"):
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {"type": "object", "properties": {}},
            },
        }

    if case == "tool_order":
        value["tools"] = [tool("a"), tool("b")][:: 1 if i % 2 else -1]
    if case == "tool_description":
        value["tools"] = [tool("a", "Read /workspace/" + token)]
    if case == "tool_added":
        value["tools"] = [tool("a")] if i % 2 else []
    if case == "representation":
        value["messages"] += [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_a",
                        "type": "function",
                        "function": {"name": "a", "arguments": "{}"},
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_a",
                "content": '{"a":1}' if i % 2 else '{ "a": 1 }',
            },
        ]
        value["tools"] = [tool("a")]
    return value


@pytest.mark.parametrize(
    "case,rule",
    [
        ("cch", "L1"),
        ("plain_timestamp", "L1"),
        ("workspace", "L1"),
        ("tool_order", "L2"),
        ("tool_description", "L3"),
        ("tool_added", "L3"),
        ("representation", "L5"),
    ],
)
@pytest.mark.parametrize("review", [False, True])
def test_normal_nonclock_recommendations_and_evidence(service, case, rule, review):
    rows = [
        valid_row(
            appid=case,
            request_input=json.dumps(body(case, i)),
            model_handle_start_time=f"2026-11-10T09:00:0{i}Z",
        )
        for i in range(8)
    ]
    (service.inputs.root / "input.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="input.csv", model_id="DeepSeek-V4-Flash-0731"))
    assert service.processor.process_next().status == "completed"
    prep = PreparationService(service, UserRunService(service))
    if review:
        original_profile = prep.profile

        def limited(task_id):
            profile = original_profile(task_id)
            return profile.model_copy(
                update={"sample": profile.sample.model_copy(update={"max_requests": 4})}
            )

        prep.profile = limited
    receipt = prep.store.submit(
        PreparationRequest3(
            submission_key="automatic",
            source=SourceSelection(source_kind="base", base_run_id=run.run_id, appid=case),
        )
    )
    assert prep.process_next().state == "completed"
    task = prep.diagnoses.submit(receipt.preparation_id, "normal-diagnosis")
    execution = prep.process_next()
    assert execution.state == "completed", execution
    report = prep.diagnoses.report(task.task_id)
    assert report["automatic_full"] is False
    groups = report["discovery"]["cause_groups"]
    assert rule in {g["rule_id"] for g in groups}
    if case in ("tool_order", "representation"):
        selected = [g for g in groups if g["rule_id"] == rule]
        assert len(selected) == 1
        assert len(selected[0]["members"]) == (2 if review else 8)
    records = {
        json.dumps(r["request_key"], sort_keys=True): r
        for r in report["discovery"]["evidence_requests"]
    }
    for g in groups:
        for side in ("left", "right"):
            record = records[json.dumps(g["comparison"][side], sort_keys=True)]
            assert hashlib.sha256(record["raw_body"].encode()).hexdigest() == record["raw_sha256"]
            assert record["raw_sha256"] == g["comparison"][side + "_raw_sha256"]
            assert json.loads(record["raw_body"]) in [body(case, i) for i in range(8)]
    if case in ("tool_added", "representation"):
        assert not report["recommendations"]  # Evidence is not an invented executable change.
    else:
        matching = [r for r in report["recommendations"] if r["finding"]["rule_id"] == rule]
        assert matching
        for r in matching:
            window = r["windows"][0]
            assert (
                window["complete"]
                and window["n"] == (2 if review else 8)
                and window["modified"] > 0
            )
            if review:
                assert r["windows"][1]["complete"] and r["windows"][1]["n"] == 2
                assert r["windows"][1]["transformation_digest"] == r["transformation_digest"]
            assert window["before"]["p"] == window["before"]["h"] + window["before"]["c"]
            assert window["after"]["p"] == window["after"]["h"] + window["after"]["c"]
            assert r["finding"]["before_fragments"] != r["finding"]["after_fragments"]
    # Real API transport including union recipes, wire integer conversion and old read gates.
    client = TestClient(create_app(service))
    instance = client.get("/diagnostics/v3/capabilities").json()["service_instance_id"]
    response = client.get(
        f"/diagnostics/v3/tasks/{task.task_id}/report",
        headers={"x-tokenscope-service-instance": instance},
    )
    assert response.status_code == 200, response.text
    parsed = from_wire(SampleReport3, response.json())
    assert parsed.task_id == task.task_id
    (service.state_root / "wire-report.json").write_text(response.text)

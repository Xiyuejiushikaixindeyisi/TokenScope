import json

from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient
from test_task_service import options

from tokenscope.analysis_common.contracts import (
    DiagnosticRequest,
    DiagnosticSelection,
    SourceSelection,
)
from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.wire import to_wire
from tokenscope.api.app import create_app
from tokenscope.api.diagnostics import Authorization, Combination, PlanReference, Submission
from tokenscope.domain import RunSubmission
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.token_content.json_values import digest, dumps, loads
from tokenscope.token_content.plugin import TokenContentPlugin


def test_full_body_authorization_and_combination_real_http(service, monkeypatch):
    document = "x" * 70000 + "末尾"
    tool = {
        "type": "function",
        "function": {
            "name": "f",
            "parameters": {
                "type": "object",
                "properties": {"document": {"type": "string"}, "document_ref": {"type": "string"}},
                "required": [],
            },
        },
    }
    body = {
        "tools": [tool],
        "enable_thinking": False,
        "messages": [
            {"role": "user", "content": "task"},
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "c",
                        "type": "function",
                        "function": {
                            "name": "f",
                            "arguments": json.dumps({"document": document}, ensure_ascii=False),
                        },
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "c", "content": document},
            {"role": "user", "content": document},
        ],
    }
    raw = json.dumps(body, ensure_ascii=False)
    rows = [
        valid_row(
            appid=appid, request_input=raw, model_handle_start_time=f"2026-10-27T00:00:0{index}Z"
        )
        for index, appid in enumerate(("a", "b", "a"))
    ]
    (service.inputs.root / "authorization.csv").write_bytes(csv_bytes(rows))
    base_run = service.submit(RunSubmission(file_ref="authorization.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    source_db = service.state_root / "runs" / base_run.run_id / "requests.sqlite3"
    original_digest = file_digest(source_db)
    app = create_app(service, start_worker=False, legacy_diagnostics=True)
    with TestClient(app) as client:
        caps = client.get("/diagnostics/capabilities").json()
        headers = {"x-tokenscope-service-instance": caps["service_instance_id"]}
        request = DiagnosticRequest(
            source=SourceSelection(source_kind="base", base_run_id=base_run.run_id, appid="a"),
            submission_key="authorize-analysis",
            selection=DiagnosticSelection(
                reason_codes=("request_length",), enable_low_hit=False, enable_token_content=True
            ),
        )
        submitted = client.post(
            "/diagnostics/tasks",
            json=to_wire(Submission(request=request, options=options())),
            headers=headers,
        )
        assert submitted.status_code == 202, submitted.text
        task_id = submitted.json()["task_id"]
        prefix = f"/diagnostics/tasks/{task_id}"
        assert app.state.dispatcher.process_next().status == "ready"
        fragment = client.get(prefix + "/items/fragment", headers=headers).json()["items"][-1]
        evidence = client.get(prefix + "/requests/" + fragment["id"], headers=headers)
        assert evidence.status_code == 200, evidence.text
        evidence = evidence.json()
        assert evidence["raw_body"] == raw and len(evidence["raw_body"].encode()) > 65536
        assert evidence["raw_body_complete"] and evidence["capture_truncation"] == "unknown"
        assert (
            evidence["scope_id"]
            == client.get(prefix + "/report", headers=headers).json()["scope_id"]
        )
        assert client.get(prefix + "/requests/2", headers=headers).status_code == 404  # other appid
        observed = next(
            o
            for o in fragment["data"]["observations"]
            if o["rule_id"] == "T3" and o["predicate"] == "exact_payload_repetition"
        )
        # unit_id is a derived identity, intentionally reconstructed with the frozen model.
        from tokenscope.analysis_common.contracts import AnalysisFragment
        from tokenscope.analysis_common.wire import from_wire

        typed = from_wire(AnalysisFragment, fragment["data"])
        index = client.get(
            prefix + "/items/fragment_index/" + fragment["id"], headers=headers
        ).json()
        assert index["unit_ids"] == [unit.unit_id for unit in typed.units]
        observation = next(
            o
            for o in typed.observations
            if o.rule_id == "T3" and o.predicate == "exact_payload_repetition"
        )
        assert len(observed["unit_ids"]) == 3
        argument = next(
            u
            for u in typed.units
            if "argument_payload" in u.facets and u.unit_id in observation.unit_ids
        )
        message = next(
            u
            for u in typed.units
            if "message_payload" in u.facets and u.unit_id in observation.unit_ids
        )
        reference_params = json.dumps(
            {
                "reference_key": "document_ref",
                "reference_value": "existing://fixture/1",
                "protocol_ref": "business-v1",
                "tool_identity": digest(
                    dumps(loads(json.dumps(tool), max_depth=20), sort_keys=True)
                ),
            }
        )
        plans = []
        for key, handler, unit, parameters in (
            ("reference", "replace_payload_with_reference", argument, reference_params),
            ("remove", "remove_authorized_duplicate_message", message, '{"authorized":true}'),
        ):
            payload = to_wire(
                Authorization(
                    fragment_id=fragment["id"],
                    observation_id=observation.observation_id,
                    selected_unit_id=unit.unit_id,
                    handler_id=handler,
                    handler_version="1",
                    parameters_json=parameters,
                    business_basis_ref="business-approval",
                    submission_key=key,
                )
            )
            if key == "reference":
                bad = dict(payload, selected_unit_id="foreign", submission_key="bad")
                assert (
                    client.post(
                        prefix + "/token-authorizations", json=bad, headers=headers
                    ).status_code
                    == 422
                )
            response = client.post(prefix + "/token-authorizations", json=payload, headers=headers)
            assert response.status_code == 202, response.text
            evaluated = app.state.dispatcher.process_next()
            assert evaluated.status == "ready", evaluated
            evaluation_task = response.json()["task_id"]
            sub = f"/diagnostics/tasks/{evaluation_task}"
            assert client.get(sub + "/items/authorization", headers=headers).json()["items"]
            result = client.get(sub + "/items/evaluation", headers=headers).json()["items"][0][
                "data"
            ]
            assert result["status"] == "available" and result["stage"] == "direct_full"
            rows_url = sub + "/evaluations/" + result["evaluation_id"] + "/rows"
            row_response = client.get(rows_url, headers=headers)
            assert row_response.status_code == 200, row_response.text
            saved_rows = row_response.json()["items"]
            assert [row["source_record_index"] for row in saved_rows] == ["1", "3"]
            assert saved_rows[-1]["evidence"]["changes"]
            assert isinstance(saved_rows[-1]["evidence"]["after_p"], str)
            assert json.loads(saved_rows[-1]["evidence"]["after_raw"])["messages"]
            assert client.get(sub + "/evaluations/foreign/rows", headers=headers).status_code == 404
            assert int(result["after"]["p"]) < int(result["before"]["p"])
            if key == "reference":
                assert int(result["after"]["c"]) > int(result["before"]["c"])
            plan_id = client.get(sub + "/items/plan", headers=headers).json()["items"][0]["id"]
            plans.append(PlanReference(task_id=evaluation_task, plan_id=plan_id))
        combination = client.post(
            prefix + "/combination-evaluations",
            headers=headers,
            json=to_wire(Combination(plan_refs=tuple(plans), submission_key="combine")),
        )
        assert combination.status_code == 202, combination.text
        assert app.state.dispatcher.process_next().status == "ready"
        result = client.get(
            f"/diagnostics/tasks/{combination.json()['task_id']}/items/evaluation", headers=headers
        ).json()["items"][0]["data"]
        assert result["direction"] == "combined" and result["status"] == "available"
        assert result["before"]["n"] == result["after"]["n"] == "2"
        assert result["modified_after"]["n"] == "1"

        def forbidden(*args, **kwargs):
            raise AssertionError("body GET computed content")

        monkeypatch.setattr(TokenContentPlugin, "analyze_request", forbidden)
        monkeypatch.setattr(EncodingContext, "encode", forbidden)
        assert (
            client.get(prefix + "/requests/" + fragment["id"], headers=headers).json() == evidence
        )
        assert client.get(rows_url, headers=headers).json()["items"] == saved_rows
        assert file_digest(source_db) == original_digest

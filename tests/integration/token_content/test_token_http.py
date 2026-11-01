from fastapi.testclient import TestClient
from test_task_service import options, setup

from tokenscope.analysis_common.contracts import (
    DiagnosticRequest,
    DiagnosticSelection,
    SourceSelection,
)
from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.wire import to_wire
from tokenscope.api.app import create_app
from tokenscope.api.diagnostics import Submission, TokenEvaluation
from tokenscope.token_content.plugin import TokenContentPlugin


def test_token_http_explicit_evaluation_instance_membership_and_readonly(service, monkeypatch):
    _, _, source = setup(service)
    app = create_app(service, start_worker=False)
    with TestClient(app) as client:
        capabilities = client.get("/diagnostics/capabilities").json()
        assert capabilities["http_version"] == "diagnostics-http-1"
        headers = {"x-tokenscope-service-instance": capabilities["service_instance_id"]}
        request = DiagnosticRequest(
            source=SourceSelection(
                source_kind="base", base_run_id=source.scope.source.base_run_id, appid="a"
            ),
            submission_key="http-token",
            selection=DiagnosticSelection(
                reason_codes=("qps",), enable_low_hit=False, enable_token_content=True
            ),
        )
        payload = to_wire(Submission(request=request, options=options()))
        assert client.post("/diagnostics/tasks", json=payload).status_code == 422
        assert (
            client.post(
                "/diagnostics/tasks",
                json=payload,
                headers={"x-tokenscope-service-instance": "foreign"},
            ).status_code
            == 409
        )
        response = client.post("/diagnostics/tasks", json=payload, headers=headers)
        assert response.status_code == 202, response.text
        task_id = response.json()["task_id"]
        base = f"/diagnostics/tasks/{task_id}"
        assert client.get(base + "/report", headers=headers).status_code == 409
        assert app.state.dispatcher.process_next().status == "ready"
        report = client.get(base + "/report", headers=headers).json()
        assert [stage["direction"] for stage in report["stages"]] == ["token_content"]
        fragments = client.get(base + "/items/fragment", headers=headers).json()["items"]
        assert len(fragments) == 2
        fragment = fragments[0]
        candidate = next(
            c
            for c in fragment["data"]["modification_candidates"]
            if c["handler_id"] == "select_result_lines"
        )
        params = to_wire(
            TokenEvaluation(
                fragment_id=fragment["id"],
                candidate_id=candidate["candidate_id"],
                parameters_json='{"start":0,"end":2}',
                business_basis_ref="approved-fixture",
                submission_key="http-zero",
            )
        )
        wrong = dict(params, candidate_id="foreign", submission_key="http-foreign")
        assert (
            client.post(base + "/token-evaluations", json=wrong, headers=headers).status_code == 404
        )
        queued = client.post(base + "/token-evaluations", json=params, headers=headers)
        assert queued.status_code == 202, queued.text
        assert app.state.dispatcher.process_next().status == "ready"
        evaluation_base = f"/diagnostics/tasks/{queued.json()['task_id']}"
        results = client.get(evaluation_base + "/items/evaluation", headers=headers).json()["items"]
        assert len(results) == 1
        result = results[0]["data"]
        assert result["before"] == result["after"]
        assert result["stage"] == "direct_full" and result["gate_passed"] is None
        assert result["display_eligible"] is False  # still present via evaluation endpoint

        def forbidden(*args, **kwargs):
            raise AssertionError("HTTP GET triggered computation")

        monkeypatch.setattr(TokenContentPlugin, "analyze_request", forbidden)
        monkeypatch.setattr(EncodingContext, "encode", forbidden)
        monkeypatch.setattr("tokenscope.analysis_common.service.evaluate_plan", forbidden)
        assert client.get(base + "/report", headers=headers).json() == report
        assert (
            client.get(evaluation_base + "/items/evaluation", headers=headers).json()["items"]
            == results
        )
        assert client.get(base + "/items/fragment/foreign", headers=headers).status_code == 404
        assert client.get(base + "/items/fragment?limit=101", headers=headers).status_code == 422
        assert app.state.dispatcher.process_next() is None

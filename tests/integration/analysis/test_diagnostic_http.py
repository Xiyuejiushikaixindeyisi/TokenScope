from fastapi.testclient import TestClient
from test_diagnostic_tasks import options, setup

from tokenscope.analysis_common.wire import to_wire
from tokenscope.api.app import create_app
from tokenscope.api.diagnostics import Submission


def test_real_http_saved_evidence_and_explicit_full(service):
    _, request = setup(service, True)
    app = create_app(service, start_worker=False)
    with TestClient(app) as client:
        capability = client.get("/diagnostics/capabilities")
        assert capability.status_code == 200
        ident = capability.json()["service_instance_id"]
        headers = {"x-tokenscope-service-instance": ident}
        payload = to_wire(Submission(request=request, options=options()))
        assert client.post("/diagnostics/tasks", json=payload).status_code == 422
        assert (
            client.post(
                "/diagnostics/tasks",
                json=payload,
                headers={"x-tokenscope-service-instance": "other"},
            ).status_code
            == 409
        )
        response = client.post("/diagnostics/tasks", json=payload, headers=headers)
        assert response.status_code == 202, response.text
        task_id = response.json()["task_id"]
        assert response.json()["attempt"] == "1"
        assert (
            client.get(f"/diagnostics/tasks/{task_id}/report", headers=headers).status_code == 409
        )
        result = app.state.dispatcher.process_next()
        assert result.task_id == task_id and result.status in ("ready", "partial"), result
        base = f"/diagnostics/tasks/{task_id}"
        report = client.get(base + "/report", headers=headers).json()
        assert [s["direction"] for s in report["stages"]] == ["low_hit", "token_content"]
        finding = client.get(base + "/items/finding", headers=headers).json()["items"][0]
        pair = client.get(base + "/comparisons/" + finding["id"], headers=headers)
        assert pair.status_code == 200 and pair.json()["raw_body_complete"]
        assert client.get(base + "/items/finding?limit=101", headers=headers).status_code == 422
        assert client.get(base + "/comparisons/foreign", headers=headers).status_code == 404
        evaluation = client.post(
            base + "/low-hit-evaluations",
            headers=headers,
            json={"finding_ids": [finding["id"]], "submission_key": "explicit"},
        )
        assert evaluation.status_code == 202, evaluation.text
        evaluated = app.state.dispatcher.process_next()
        assert evaluated.status == "ready", evaluated
        eval_id = evaluation.json()["task_id"]
        view = client.get(f"/diagnostics/tasks/{eval_id}/items/evaluation", headers=headers).json()[
            "items"
        ][0]["data"]
        assert view["stage"] == "direct_full" and view["gain_percentage_points"] is not None
        rows = client.get(
            f"/diagnostics/tasks/{eval_id}/evaluations/{view['evaluation_id']}/rows",
            headers=headers,
        )
        assert rows.status_code == 200, rows.text
        assert len(rows.json()["items"]) == 6
        assert rows.json()["items"][0]["evidence"]["changes"]
        assert isinstance(rows.json()["items"][0]["evidence"]["before_p"], str)
        assert (
            client.get(
                f"/diagnostics/tasks/{eval_id}/evaluations/foreign/rows", headers=headers
            ).status_code
            == 404
        )
        optimization = client.get(base + "/items/optimization", headers=headers).json()["items"][0][
            "data"
        ]
        assert (
            client.get(
                base + "/evaluations/" + optimization["evaluation_id"] + "/rows", headers=headers
            ).status_code
            == 200
        )
        # No inferred workflow or source recollection from read-only endpoints.
        assert app.state.dispatcher.process_next() is None
        assert client.get("/healthz").status_code == 200
        # Wire metadata integers cannot quietly accept JSON numbers.
        payload["options"]["candidate_limit"] = 2
        bad = client.post("/diagnostics/tasks", json=payload, headers=headers)
        assert bad.status_code == 422 and "raw_body" not in bad.text

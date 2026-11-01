from fastapi.testclient import TestClient
from test_diagnostic_tasks import options, setup

from tokenscope.analysis_common.wire import to_wire
from tokenscope.api.app import create_app
from tokenscope.api.diagnostics import Submission


def test_discovery_real_report_terminal_and_instance_guard(service):
    _, request = setup(service)
    app = create_app(service, start_worker=False)
    with TestClient(app) as client:
        prefix = "/diagnostics/discovery"
        capability = client.get(prefix + "/capabilities").json()
        headers = {"x-tokenscope-service-instance": capability["service_instance_id"]}
        assert client.get(prefix + "/catalog").status_code == 422
        assert (
            client.get(
                prefix + "/events?cursor=bad", headers={"x-tokenscope-service-instance": "other"}
            ).status_code
            == 409
        )
        initial = client.get(prefix + "/catalog", headers=headers).json()
        task = client.post(
            "/diagnostics/tasks",
            headers=headers,
            json=to_wire(Submission(request=request, options=options())),
        ).json()
        path = prefix + f"/tasks/{task['task_id']}/terminal"
        assert client.get(path, headers=headers).json()["terminal"] is None
        assert app.state.dispatcher.process_next().status == "ready"
        terminal = client.get(path, headers=headers).json()["terminal"]
        assert terminal["report_published"] and terminal["analysis_completed_at"].endswith("Z")
        report = client.get(f"/diagnostics/tasks/{task['task_id']}/report", headers=headers)
        assert report.status_code == 200
        assert terminal["scope_id"] == report.json()["scope_id"]
        assert (
            client.get(prefix + "/catalog", headers=headers).json()["defaults"][0]["task_id"]
            == task["task_id"]
        )
        # Same snapshot stays empty; a reopen without snapshot discovers the new publication.
        assert (
            client.get(
                prefix + "/catalog", headers=headers, params={"snapshot": initial["snapshot"]}
            ).json()["items"]
            == []
        )
        response = client.get(prefix + "/events?cursor=wrong:0", headers=headers)
        assert response.status_code == 200 and "event: reset" in response.text
        assert client.get(prefix + "/catalog?after=01", headers=headers).status_code == 422
        assert app.state.dispatcher.process_next() is None  # GETs did not trigger work.
        retry = client.post(
            f"/diagnostics/tasks/{task['task_id']}/retry",
            headers=headers,
            json={"submission_key": "cancel-retry"},
        ).json()
        client.post(f"/diagnostics/tasks/{retry['task_id']}/cancel", headers=headers)
        canceled = client.get(
            prefix + f"/tasks/{retry['task_id']}/terminal", headers=headers
        ).json()["terminal"]
        assert canceled["status"] == "interrupted" and canceled["published_at"] is None
        assert (
            client.get(prefix + "/catalog", headers=headers).json()["defaults"][0]["task_id"]
            == task["task_id"]
        )

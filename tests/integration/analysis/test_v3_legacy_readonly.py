"""Existing synthetic reports remain readable with production V3 execution policy."""

import pytest
from fastapi.testclient import TestClient
from test_diagnostic_tasks import options, setup

from tokenscope.api.app import create_app


@pytest.mark.parametrize("low_hit", [True, False])
def test_production_dormancy_keeps_old_report_and_prevents_execution(service, low_hit, monkeypatch):
    old, request = setup(service, low_hit)
    receipt = old.submit(request, options())
    assert old.process_next().status in ("ready", "partial")
    path = f"/diagnostics/tasks/{receipt.task_id}"
    legacy = create_app(service, start_worker=False, legacy_diagnostics=True)
    headers = {"x-tokenscope-service-instance": legacy.state.user.service_id}
    expected = TestClient(legacy).get(path + "/report", headers=headers).json()
    monkeypatch.setenv("TOKENSCOPE_RECOMMENDATION_BUNDLE", "/nonexistent-dormant-bundle")
    production = create_app(service, start_worker=False)
    client = TestClient(production)
    assert client.get(path + "/report", headers=headers).json() == expected
    for kind in ("finding", "fragment", "evaluation", "optimization"):
        assert client.get(path + "/items/" + kind, headers=headers).status_code == 200
    caps = client.get("/diagnostics/v2/capabilities").json()
    assert caps["execution_enabled"] is False and caps["directions"] == []
    for suffix in ("/retry", "/low-hit-evaluations", "/token-evaluations", "/combinations"):
        assert client.post(path + suffix, json={}, headers=headers).status_code == 409
    assert client.post("/diagnostics/v2/tasks", json={}, headers=headers).status_code == 409
    assert production.state.dispatcher.process_next() is None

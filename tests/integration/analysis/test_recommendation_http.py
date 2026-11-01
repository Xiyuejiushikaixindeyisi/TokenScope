from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse
from test_diagnostic_tasks import options, setup
from test_recommendation_engine import configured

from tokenscope.api.diagnostic_recommendations import router
from tokenscope.errors import TokenScopeError


def client_for(diagnostics):
    app = FastAPI()

    @app.exception_handler(TokenScopeError)
    async def error(request, exc):
        return JSONResponse({"error": exc.as_dict()}, status_code=exc.http_status)

    app.include_router(router(diagnostics, "instance"))
    return TestClient(app, headers={"x-tokenscope-service-instance": "instance"})


def test_sealed_get_pages_no_compute_and_private_policy_redacted(service, monkeypatch):
    diagnostics, request = configured(service, duplicate=True)
    task = diagnostics.submit(request, options(max_encoding_calls=500))
    client = client_for(diagnostics)
    base = f"/diagnostics/tasks/{task.task_id}"
    assert client.get(base + "/recommendations").status_code == 409
    assert diagnostics.process_next().status == "ready"

    def forbidden(*args, **kwargs):
        raise AssertionError("GET performed mutation or computation")

    monkeypatch.setattr(diagnostics, "submit", forbidden)
    monkeypatch.setattr(diagnostics, "process_next", forbidden)
    monkeypatch.setattr(diagnostics.recommendations.registry.get(), "propose", forbidden)
    monkeypatch.setattr(diagnostics.recommendations.registry.get(), "prepare_proposal", forbidden)
    first = client.get(base + "/recommendations", params={"limit": "1"}).json()
    assert len(first["items"]) == 1 and first["next_offset"] == "1"
    second = client.get(base + "/recommendations", params={"limit": "1", "offset": "1"}).json()
    assert second["next_offset"] is None and second["items"][0]["id"] != first["items"][0]["id"]
    rec = first["items"][0]
    assert "parameter_generator_json" not in rec["data"]["recipe"]
    assert "selector_json" not in rec["data"]["recipe"]
    assert "scope_selector" not in rec["data"]["recipe"]["basis"]
    assert int(rec["data"]["metrics"]["input_tokens_delta"]) < 0
    detail = client.get(base + "/recommendations/" + rec["id"])
    assert detail.status_code == 200
    examples = client.get(base + "/recommendations/" + rec["id"] + "/examples").json()
    assert len(examples["items"]) == 3
    assert client.get(base + "/recommendation-summary").json()["availability"] == "computed"
    assert client.get(base + "/recommendations", params={"limit": "101"}).status_code == 422
    assert client.get(base + "/recommendations", params={"offset": "01"}).status_code == 422
    assert (
        client.get(
            base + "/recommendations", headers={"x-tokenscope-service-instance": "other"}
        ).status_code
        == 409
    )
    assert client.post(base + "/recommendations", json={}).status_code == 405


def test_legacy_is_not_computed_and_never_backfilled(service):
    diagnostics, request = setup(service)
    task = diagnostics.submit(request, options())
    assert diagnostics.process_next().status == "ready"
    client = client_for(diagnostics)
    base = f"/diagnostics/tasks/{task.task_id}"
    result = client.get(base + "/recommendations").json()
    assert result["availability"] == "not_computed" and not result["items"]
    assert client.get(base + "/recommendation-summary").json()["budget"] is None
    assert client.get(base + "/recommendations/not-present").status_code == 404

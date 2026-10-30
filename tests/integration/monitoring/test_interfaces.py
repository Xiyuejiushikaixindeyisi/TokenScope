import json
import sqlite3

from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient

from tokenscope.api.app import create_app
from tokenscope.cli import main


def test_cli_and_http_share_settings_and_version(service, capsys):
    client = TestClient(create_app(service))
    args = ["--input-root", str(service.inputs.root), "--state-root", str(service.state_root)]
    assert main([*args, "version"]) == 0
    assert json.loads(capsys.readouterr().out) == client.get("/version").json()
    response = client.put(
        "/models/GLM-5.2/settings", json={"expected_revision": 1, "changes": {"block_size": 256}}
    )
    assert response.status_code == 200
    assert main([*args, "settings", "GLM-5.2"]) == 0
    assert json.loads(capsys.readouterr().out) == response.json()
    assert (
        client.put(
            "/models/GLM-5.2/settings",
            json={"expected_revision": 1, "changes": {"block_size": 512}},
        ).status_code
        == 409
    )


def test_liveness_readiness_and_submit_no_fake_metrics(service):
    (service.inputs.root / "glm.csv").write_bytes(csv_bytes([valid_row()]))
    client = TestClient(create_app(service))
    assert client.get("/healthz").status_code == 200
    ready = client.get("/readyz")
    assert ready.status_code == 200
    assert ready.json()["ready"] is True
    response = client.post("/analysis-runs", json={"file_ref": "glm.csv", "model_id": "GLM-5.2"})
    assert response.status_code == 202
    assert response.json()["status"] == "queued"
    assert response.json()["result"] is None
    assert client.get("/analysis-runs/" + response.json()["run_id"] + "/metrics").status_code == 409
    with service.control.connect() as db:
        assert db.execute("SELECT count(*) FROM analysis_runs").fetchone()[0] == 1
    assert client.get("/analysis-runs/nonexistent").status_code == 404


def test_input_validation_cli_round_trip(service, capsys):
    raw = valid_row()[4]
    (service.inputs.root / "glm.csv").write_bytes(csv_bytes([valid_row(), valid_row()]))
    args = ["--input-root", str(service.inputs.root), "--state-root", str(service.state_root)]
    assert main([*args, "validate-input", "glm.csv", "--model", "GLM-5.2"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["kind"] == "input_validation_only"
    assert result["token_metrics"] is None
    assert result["quality"]["duplicate_hash_id_rows"] == 1
    with sqlite3.connect(
        service.state_root / "validations" / result["validation_id"] / "requests.sqlite3"
    ) as db:
        assert db.execute("SELECT request_input FROM request_records").fetchone()[0] == raw


def test_error_does_not_echo_sensitive_body(service):
    client = TestClient(create_app(service))
    response = client.post(
        "/analysis-runs", json={"file_ref": "secret", "request_input": "PRIVATE_BODY"}
    )
    assert response.status_code == 422
    assert "PRIVATE_BODY" not in response.text
    assert "secret" not in response.text
    response = client.post("/analysis-runs", json={"file_ref": "../private", "model_id": "GLM-5.2"})
    assert response.json()["error"]["code"] == "INVALID_FILE_REF"


def test_http_storage_error_is_service_failure(service, monkeypatch):
    def fail():
        raise sqlite3.OperationalError("disk full private path")

    monkeypatch.setattr(service, "readiness", fail)
    response = TestClient(create_app(service)).get("/readyz")
    assert response.status_code == 503
    assert "private" not in response.text


def test_openapi_refers_to_shared_request_and_run_types(service):
    schema = create_app(service).openapi()
    assert schema["paths"]["/analysis-runs"]["post"]["requestBody"]["content"]["application/json"][
        "schema"
    ]["$ref"].endswith("/RunSubmission")
    assert (
        schema["components"]["schemas"]["ModelSettings"]["properties"]["block_size"][
            "exclusiveMinimum"
        ]
        == 0
    )


def test_extreme_queries_are_rejected_without_storage_access(service):
    client = TestClient(create_app(service, start_worker=False))
    for query in [
        "offset=" + str(2**100),
        "lower=" + str(2**100),
        "upper=" + str(2**100),
        "metric=unknown",
        "lower=20&upper=10",
    ]:
        response = client.get("/analysis-runs/unknown/lengths?appid=a&" + query)
        assert response.status_code == 422


def test_release_identity_is_explicit_metadata(service, monkeypatch):
    monkeypatch.setenv("TOKENSCOPE_RELEASE_ID", "synthetic-release-check")
    monkeypatch.setenv("TOKENSCOPE_SOURCE_MANIFEST_SHA256", "a" * 64)
    result = TestClient(create_app(service, start_worker=False)).get("/version").json()
    assert result["release_id"] == "synthetic-release-check"
    assert result["source_manifest_sha256"] == "a" * 64

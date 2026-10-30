import json
import sqlite3

import pytest
from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient

from tokenscope.api.app import create_app
from tokenscope.errors import TokenScopeError
from tokenscope.user_monitoring.contracts import Bind, Submit
from tokenscope.user_monitoring.service import UserRunService


def setup(service):
    (service.inputs.root / "r.csv").write_bytes(csv_bytes([valid_row()]))
    user = UserRunService(service)
    request = Submit(
        submission_key="r", file_ref="r.csv", common_name="GLM-V5.2", model_id="GLM-5.2"
    )
    return user, request


def test_response_loss_finds_base_after_input_removed(service, monkeypatch):
    user, request = setup(service)
    receipt = user.submit(request)
    original = user.store.update
    monkeypatch.setattr(user.store, "update", lambda *a, **kw: (_ for _ in ()).throw(OSError()))
    assert user.process_next().state == "accepted"
    completed = service.processor.process_next()
    assert completed.status == "completed"
    with pytest.raises(TokenScopeError, match="reserved"):
        user.submit(
            Bind(submission_key="steal", base_run_id=completed.run_id, common_name="GLM-V5.2")
        )
    (service.inputs.root / "r.csv").unlink()
    monkeypatch.setattr(user.store, "update", original)
    assert user.process_next().state == "base_pending"
    assert user.process_next().state == "ready"
    assert user.submit(request).user_run_id == receipt.user_run_id


def test_missing_control_get_does_not_recreate(service):
    app = create_app(service, start_worker=False)
    client = TestClient(app)
    user = app.state.user
    user.store.path.unlink()
    response = client.get(
        "/monitoring/user-v2/runs/unknown", headers={"X-TokenScope-Instance-Id": user.service_id}
    )
    assert response.status_code == 503
    assert not user.store.path.exists()


def test_invalid_inputs_safe_errors_and_runtime_contract(service):
    user, request = setup(service)
    client = TestClient(create_app(service, start_worker=False))
    headers = {"X-TokenScope-Instance-Id": user.service_id}
    prefix = "/monitoring/user-v2"
    for data in (
        request.model_dump() | {"file_ref": "../secret"},
        request.model_dump() | {"submission_key": "s" * 5000},
    ):
        response = client.post(prefix + "/runs", json=data, headers=headers)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "INVALID_ARGUMENT"
        assert "secret" not in response.text and "sss" not in response.text
    huge = dict(
        submission_key="s",
        user_run_id="u",
        appid="a",
        scenario_id="s",
        scenario_revision="1",
        target_seconds="9" * 5000,
        waiting_seconds="0",
        comparator="le",
    )
    response = client.post(prefix + "/evaluations", json=huge, headers=headers)
    assert response.status_code == 422 and "9999" not in response.text
    response = client.post(
        prefix + "/bindings",
        headers=headers,
        json=dict(submission_key="b", base_run_id="ma-id", common_name="GLM-V5.2"),
    )
    assert response.status_code == 404 and response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"
    spec = client.get("/openapi.json").json()
    paths = {p: v for p, v in spec["paths"].items() if p.startswith(prefix)}
    assert sum(len(ops) for ops in paths.values()) == 9
    for operations in paths.values():
        for operation in operations.values():
            assert any(
                p["name"] == "X-TokenScope-Instance-Id" and p["required"]
                for p in operation["parameters"]
            )
            assert operation["x-runtime-implemented"]


def test_missing_assets_not_mocked_as_success(service, monkeypatch):
    user, request = setup(service)
    user.submit(request)

    def missing(*args):
        raise TokenScopeError("MODEL_ASSET_MISSING", "Assets absent", 503)

    monkeypatch.setattr(service.assets, "load", missing)
    result = user.process_next()
    assert result.state == "failed" and result.error_code == "MODEL_ASSET_MISSING"


def test_schema_guard_and_missing_index_readonly(service):
    user, request = setup(service)
    receipt = user.submit(request)
    user.process_next()
    service.processor.process_next()
    user.process_next()
    (user.root / (receipt.user_run_id + ".sqlite3")).unlink()
    with pytest.raises(TokenScopeError, match="missing"):
        with user.index(receipt.user_run_id):
            pass
    assert user.receipt(receipt.user_run_id).state == "ready"
    user.rebuild(receipt.user_run_id)
    assert user.process_next().state == "ready"
    with user.store.connect() as db:
        db.execute("PRAGMA user_version=99")
    with pytest.raises(TokenScopeError, match="schema"):
        UserRunService(service)
    with sqlite3.connect(user.store.path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 99


def test_large_json_original_preserved(service):
    raw = json.dumps({"messages": [{"role": "user", "content": "x " * 140000}]}, indent=3)
    (service.inputs.root / "large.csv").write_bytes(csv_bytes([valid_row(request_input=raw)]))
    user = UserRunService(service)
    receipt = user.submit(
        Submit(
            submission_key="large", file_ref="large.csv", common_name="GLM-V5.2", model_id="GLM-5.2"
        )
    )
    user.process_next()
    assert service.processor.process_next().status == "completed"
    ready = user.process_next()
    with service.result_db(ready.base_run_id) as db:
        assert db.execute("SELECT request_input FROM request_records").fetchone()[0] == raw
    with user.index(receipt.user_run_id) as db:
        row = json.loads(db.execute("SELECT payload FROM groups WHERE width=5000").fetchone()[0])
        assert int(row["prompt_p90"]) > 100000
        assert int(row["representative_bin"]["upper"]) > int(row["total_ideal_compute_tokens"])

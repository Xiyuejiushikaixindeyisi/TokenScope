import pytest
from fastapi.testclient import TestClient

from tokenscope.api.app import create_app
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.ma.ingest import connect
from tokenscope.monitoring.ma.pipeline import verify
from tokenscope.monitoring.ma.service import MaService
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.monitoring.service import MonitoringService

from .helpers import binding, row, write_csv


def prepare(service: MonitoringService) -> MaService:
    write_csv(service.inputs.root / "pre.csv", [row("pre")])
    write_csv(
        service.inputs.root / "now.csv", [row(), row(instance_uuid="B", request_input="{bad")]
    )
    return MaService(service)


def test_http_complete_and_get_readonly(service: MonitoringService) -> None:
    prepare(service)
    app = create_app(service, start_worker=False)
    with TestClient(app) as client:
        response = client.post("/monitoring/ma/runs", json=binding().model_dump())
        assert response.status_code == 202, response.text
        run_id = response.json()["ma_run_id"]
        assert client.get(f"/monitoring/ma/runs/{run_id}/instances/A").status_code == 409
        done = app.state.ma.processor.process_next()
        assert done.state == "completed", done
        directory = app.state.ma.processor.runs / run_id
        before = {str(p): file_digest(p) for p in directory.rglob("*") if p.is_file()}
        data = client.get(f"/monitoring/ma/runs/{run_id}/instances/A").json()
        assert data["instance"]["coverage"]["assigned"] == "1"
        assert data["instance"]["pre_encoded"] == "1"
        assert client.get("/monitoring/ma/catalog").json()["entries"][0]["instance_uuids"] == [
            "A",
            "B",
        ]
        assert client.get(f"/monitoring/ma/runs/{run_id}/instances/C").status_code == 404
        assert client.get(f"/monitoring/ma/runs/{run_id}/quality").json()["total"] == "1"
        assert client.get("/monitoring/ma/catalog?offset=1").status_code == 409
        assert before == {str(p): file_digest(p) for p in directory.rglob("*") if p.is_file()}
        (service.inputs.root / "pre.csv").unlink()
        assert (
            client.post("/monitoring/ma/runs", json=binding().model_dump()).json()["ma_run_id"]
            == run_id
        )
        wrong = binding().model_dump() | {"model_standard_name": "other"}
        assert client.post("/monitoring/ma/runs", json=wrong).status_code == 409


def test_seal_recovery_and_interrupted(
    service: MonitoringService, monkeypatch: pytest.MonkeyPatch
) -> None:
    ma = prepare(service)
    receipt = ma.submit(binding())
    original = ma.store.complete

    def fail(*args: object) -> None:
        raise OSError("injected control commit failure")

    monkeypatch.setattr(ma.store, "complete", fail)
    result = ma.processor.process_next()
    assert result is not None and result.state == "running"
    manifest = ma.processor.runs / receipt.ma_run_id / "manifest.json"
    before = manifest.read_bytes()
    monkeypatch.setattr(ma.store, "complete", original)
    ma.processor.process_next()
    assert ma.store.receipt(receipt.ma_run_id).state == "completed"
    assert manifest.read_bytes() == before
    assert verify(manifest.parent, receipt.ma_run_id)["ma_run_id"] == receipt.ma_run_id
    second = ma.submit(binding().model_copy(update={"submission_key": "two"}))
    ma.store.claim(second.ma_run_id, service.control.settings(binding().model_id))
    ma.processor.process_next()
    assert ma.store.receipt(second.ma_run_id).state == "interrupted"
    assert ma.catalog().total == "1"
    with connect(ma.store.path) as db:
        assert db.execute("SELECT revision FROM metadata").fetchone()[0] == 1


def test_bad_seal_is_rejected(service: MonitoringService, monkeypatch: pytest.MonkeyPatch) -> None:
    ma = prepare(service)
    receipt = ma.submit(binding())
    original = ma.store.complete
    monkeypatch.setattr(ma.store, "complete", lambda *args: (_ for _ in ()).throw(OSError()))
    ma.processor.process_next()
    summary = ma.processor.runs / receipt.ma_run_id / "summary.json"
    summary.write_text("{}")
    monkeypatch.setattr(ma.store, "complete", original)
    ma.processor.process_next()
    assert ma.store.receipt(receipt.ma_run_id).error_code == "RESULT_SEAL_INVALID"
    assert ma.catalog().total == "0"


def test_paths_and_empty_pair(service: MonitoringService) -> None:
    ma = prepare(service)
    with pytest.raises(TokenScopeError):
        ma.submit(binding().model_copy(update={"pre_file_ref": "../outside.csv"}))
    write_csv(service.inputs.root / "pre.csv", [])
    write_csv(service.inputs.root / "now.csv", [])
    ma.submit(binding())
    result = ma.processor.process_next()
    assert result is not None and result.state == "completed"
    assert ma.catalog().entries[0].empty_scope_reason == "empty_file"
    assert ma.catalog().entries[0].instance_uuids == []

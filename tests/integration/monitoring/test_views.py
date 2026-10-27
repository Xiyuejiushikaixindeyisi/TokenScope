import json
import sqlite3

from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient

from tokenscope.api.app import create_app
from tokenscope.domain import RunSubmission, SettingsUpdate
from tokenscope.monitoring.view_models import canonical, sha, wire
from tokenscope.monitoring.view_projection import location


def test_snapshot_frozen_read_only_and_etag(service, monkeypatch):
    (service.inputs.root / "view.csv").write_bytes(csv_bytes([valid_row()]))
    run = service.submit(RunSubmission(file_ref="view.csv", model_id="GLM-5.2"))
    service.processor.process_next()
    expected = wire(service.metrics(run.run_id, "tenant")["groups"][0])

    def forbidden(*args, **kwargs):
        raise AssertionError("GET must not analyze or encode")

    monkeypatch.setattr(service, "explain_encoding", forbidden)
    monkeypatch.setattr(service.processor, "process_next", forbidden)
    monkeypatch.setattr(service.assets, "load", forbidden)
    with TestClient(create_app(service, start_worker=False)) as client:
        path = f"/analysis-runs/{run.run_id}/view-snapshot?appid=tenant"
        first = client.get(path)
        assert first.status_code == 200, first.text
        body = first.json()
        assert body["metrics"] == expected
        with service.result_db(run.run_id) as db:
            hist = json.loads(
                db.execute("SELECT histograms_json FROM groups WHERE appid='tenant'").fetchone()[0]
            )
        assert body["distributions"] == wire(hist)
        assert first.content == canonical(body)
        assert first.headers["etag"] == '"' + sha(first.content) + '"'
        assert len(first.content) < 512 * 1024
        service.control.update_settings(
            "GLM-5.2", SettingsUpdate(expected_revision=1, changes={"block_size": 64})
        )
        assert client.get(path).content == first.content
        cached = client.get(path, headers={"If-None-Match": first.headers["etag"]})
        assert cached.status_code == 304 and not cached.content
        assert client.get(path.replace("tenant", "absent")).status_code == 404
        assert client.get("/analysis-runs/absent/view-snapshot?appid=tenant").status_code == 404
        output = service.state_root / "snapshot-test.json"
        output.write_bytes(first.content)
        # Retain actual DTO separately for independent fixed-schema validation.
        import os

        if os.environ.get("TOKENSCOPE_VIEW_CAPTURE"):
            from pathlib import Path

            Path(os.environ["TOKENSCOPE_VIEW_CAPTURE"]).write_bytes(first.content)
        with sqlite3.connect(location(service.state_root, run.run_id) / "view.sqlite3") as db:
            db.execute("UPDATE view_groups SET body=?", (json.dumps({}).encode(),))
        assert client.get(path).json()["error"]["code"] == "VIEW_ARTIFACT_UNAVAILABLE"

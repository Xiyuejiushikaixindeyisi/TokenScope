import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient
from starlette.requests import ClientDisconnect

from tokenscope.api.app import create_app
from tokenscope.api.views import ClosingResponse
from tokenscope.domain import RunSubmission
from tokenscope.monitoring import view_projection
from tokenscope.monitoring.storage import ControlStore


@pytest.mark.parametrize("point", ["projection", "before_commit", "after_commit"])
def test_crash_boundaries_publish_once(service, monkeypatch, point):
    (service.inputs.root / "input.csv").write_bytes(csv_bytes([valid_row()]))
    run = service.submit(RunSubmission(file_ref="input.csv", model_id="GLM-5.2"))
    if point == "projection":
        original = view_projection.prepare

        def crash(*args, **kwargs):
            original(*args, **kwargs)
            raise SystemExit("synthetic process exit")

        monkeypatch.setattr(view_projection, "prepare", crash)
    else:
        original = service.control.complete

        def crash(*args, **kwargs):
            if point == "after_commit":
                original(*args, **kwargs)
            raise SystemExit("synthetic process exit")

        monkeypatch.setattr(service.control, "complete", crash)
    with pytest.raises(SystemExit):
        service.processor.process_next()
    monkeypatch.undo()
    service.processor.process_next()
    service.processor.process_next()
    status = service.control.run(run.run_id).status
    assert status == ("interrupted" if point == "projection" else "completed")
    with service.control.connect() as db:
        assert (
            db.execute("SELECT count(*) FROM ui_events WHERE run_id=?", (run.run_id,)).fetchone()[0]
            == 1
        )
        assert db.execute(
            "SELECT count(*) FROM publications WHERE run_id=?", (run.run_id,)
        ).fetchone()[0] == (point != "projection")


def test_stream_disconnect_closes_underlying_iterator():
    closed = []

    def chunks():
        try:
            yield b"first"
            yield b"second"
        finally:
            closed.append(True)

    async def exercise():
        response = ClosingResponse(chunks())

        async def send(message):
            if message["type"] == "http.response.body":
                raise OSError("synthetic disconnect")

        async def receive():
            return {"type": "http.disconnect"}

        with pytest.raises(ClientDisconnect):
            await response({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, send)

    asyncio.run(exercise())
    assert closed == [True]


def test_frozen_openapi_and_exact_query_lexemes(service):
    root = Path(__file__).resolve().parents[3]
    frozen = json.loads(
        (root / "docs/contracts/schemas/monitoring-view-v1.design.openapi.json").read_text()
    )
    with TestClient(create_app(service, start_worker=False)) as c:
        actual = c.get("/openapi.json").json()
        for path, operations in frozen["paths"].items():
            for method in operations:
                assert actual["paths"][path][method]["x-runtime-implemented"] is True
        for offset in ("01", "1.0", "-1", "+1", " 1"):
            assert c.get("/monitoring/catalog", params=dict(offset=offset)).status_code == 422
        assert c.get("/monitoring/catalog?model_id=unknown").status_code == 422
        assert c.get("/monitoring/catalog?appid=").status_code == 422
        assert (
            c.post(
                "/analysis-runs",
                json=dict(file_ref="x.csv", model_id="GLM-5.2", submission_key=None),
            ).status_code
            == 422
        )


def test_schema_backup_is_usable_by_actual_dev5_code(service, tmp_path):
    # An isolated old-style control DB, then restore the backup using the preserved dev5 source.
    original = tmp_path / "legacy.sqlite3"
    store = ControlStore(original)
    with store.connect() as db:
        for table in (
            "submission_receipts",
            "active_groups",
            "publication_groups",
            "publications",
            "ui_events",
            "service_metadata",
        ):
            db.execute(f"DROP TABLE {table}")
        db.execute("PRAGMA user_version=2")
    ControlStore(original)
    backup = original.with_name("legacy.schema2.backup.sqlite3")
    restored = tmp_path / "restored.sqlite3"
    shutil.copy2(backup, restored)
    root = Path(__file__).resolve().parents[3]
    baseline = root / "tests/fixtures/dev5_control"
    assert (baseline / "tokenscope/monitoring/storage.py").exists()
    code = (
        "from pathlib import Path; from tokenscope.monitoring.storage import ControlStore; "
        "s=ControlStore(Path(__import__('sys').argv[1])); "
        "print(s.settings('GLM-5.2').block_size); "
        "print(__import__('sqlite3').connect(s.path).execute('PRAGMA user_version').fetchone()[0])"
    )
    result = subprocess.check_output(
        [sys.executable, "-c", code, str(restored)],
        env={**os.environ, "PYTHONPATH": str(baseline)},
        text=True,
    )
    assert result.splitlines() == ["128", "2"]

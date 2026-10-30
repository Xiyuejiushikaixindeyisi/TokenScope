import json
import socket
import sqlite3
import subprocess
import sys
import time

import httpx
import pytest

from tokenscope.domain import SettingsChanges, SettingsUpdate
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.ma.service import MaService
from tokenscope.monitoring.service import MonitoringService

from .helpers import binding, row, write_csv


def test_live_http_background_worker(service: MonitoringService) -> None:
    write_csv(service.inputs.root / "pre.csv", [row("pre")])
    write_csv(service.inputs.root / "now.csv", [row()])
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    command = [
        sys.executable,
        "-m",
        "tokenscope.cli",
        "--input-root",
        str(service.inputs.root),
        "--state-root",
        str(service.state_root),
        "serve",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        with httpx.Client(
            base_url=f"http://127.0.0.1:{port}", timeout=5, trust_env=False
        ) as client:
            deadline = time.monotonic() + 30
            while True:
                try:
                    response = client.get("/monitoring/ma/catalog")
                    if response.status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                assert time.monotonic() < deadline and process.poll() is None
                time.sleep(0.1)
            response = client.post("/monitoring/ma/runs", json=binding().model_dump())
            assert response.status_code == 202, response.text
            run_id = response.json()["ma_run_id"]
            while True:
                receipt = client.get(f"/monitoring/ma/runs/{run_id}").json()
                if receipt["state"] not in ("queued", "running"):
                    break
                assert time.monotonic() < deadline
                time.sleep(0.1)
            assert receipt["state"] == "completed", receipt
            snapshot = client.get(f"/monitoring/ma/runs/{run_id}/instances/A")
            assert snapshot.json()["instance"]["coverage"]["assigned"] == "1"
            assert snapshot.headers["cache-control"] == "no-store"
            assert (
                client.get(
                    "/monitoring/ma/catalog", headers={"X-TokenScope-Instance-Id": "wrong"}
                ).status_code
                == 409
            )
    finally:
        process.terminate()
        try:
            process.wait(15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(5)


def test_batch_replay_prewarm_and_repeat(service: MonitoringService) -> None:
    raw = json.dumps({"messages": [{"role": "user", "content": "repeat prefix " * 2500}]})
    write_csv(
        service.inputs.root / "pre.csv",
        [
            row("pre", instance_uuid="pre-only"),
            row("pre", request_input=raw, cached_tokens="", appid="pre-tenant"),
        ],
    )
    write_csv(
        service.inputs.root / "now.csv",
        [
            row(request_input=raw, appid="new-tenant"),
            row(request_input=raw, appid="third", cached_tokens=""),
            row(request_input=raw, request_time="20/10/2026 08:59:59.999999999"),
        ],
    )
    ma = MaService(service)
    outputs = []
    for index, batch in enumerate((1, 256)):
        service.processor.batch_rows = batch
        receipt = ma.submit(binding().model_copy(update={"submission_key": f"batch{index}"}))
        result = ma.processor.process_next()
        assert result is not None and result.state == "completed", result
        output = ma.snapshot(receipt.ma_run_id, "A").instance
        assert output.ideal.totals.cached_tokens != "0"
        assert output.coverage.encoded == "3" and output.coverage.paired == "2"
        assert output.bins[-1].pressure.request_count == "1"
        pre_only = ma.snapshot(receipt.ma_run_id, "pre-only").instance
        assert pre_only.ideal_status == "empty_now" and pre_only.real.hit_rate is None
        outputs.append(output)
    assert outputs[0] == outputs[1]


@pytest.mark.parametrize("fault", ["asset", "sqlite"])
def test_system_failure_recovery(
    service: MonitoringService, monkeypatch: pytest.MonkeyPatch, fault: str
) -> None:
    write_csv(service.inputs.root / "pre.csv", [])
    write_csv(service.inputs.root / "now.csv", [row()])
    ma = MaService(service)
    receipt = ma.submit(binding())
    original = ma.store.complete

    def asset(*args: object) -> None:
        raise TokenScopeError("ASSETS_NOT_FOUND", "injected unavailable assets", 503)

    def commit(*args: object) -> None:
        raise sqlite3.OperationalError("database is locked")

    if fault == "asset":
        monkeypatch.setattr(service.assets, "load", asset)
    else:
        monkeypatch.setattr(ma.store, "complete", commit)
    result = ma.processor.process_next()
    assert result is not None
    if fault == "asset":
        assert result.state == "failed" and result.error_code == "ASSETS_NOT_FOUND"
    else:
        assert result.state == "running"
        monkeypatch.setattr(ma.store, "complete", original)
        ma.processor.process_next()
        assert ma.store.receipt(receipt.ma_run_id).state == "completed"


@pytest.mark.parametrize("after_seal", [False, True])
def test_actual_process_exit(service: MonitoringService, after_seal: bool) -> None:
    write_csv(service.inputs.root / "pre.csv", [])
    write_csv(service.inputs.root / "now.csv", [row()])
    ma = MaService(service)
    receipt = ma.submit(binding())
    script = """
import os,sys
from pathlib import Path
from tokenscope.monitoring.service import MonitoringService
from tokenscope.monitoring.ma.service import MaService
import tokenscope.monitoring.ma.pipeline as pipeline
service=MonitoringService(Path(sys.argv[1]),Path(sys.argv[2]))
ma=MaService(service)
def crash(*args): os._exit(77)
if sys.argv[3]=='after': ma.store.complete=crash
else: pipeline.seal=crash
ma.processor.process_next()
"""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(service.inputs.root),
            str(service.state_root),
            "after" if after_seal else "before",
        ],
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 77, result.stderr
    assert ma.store.receipt(receipt.ma_run_id).state == "running"
    ma.processor.process_next()
    assert ma.store.receipt(receipt.ma_run_id).state == (
        "completed" if after_seal else "interrupted"
    )


def test_settings_frozen_at_claim(
    service: MonitoringService, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_csv(service.inputs.root / "pre.csv", [])
    write_csv(service.inputs.root / "now.csv", [row()])
    ma = MaService(service)
    receipt = ma.submit(binding())
    before = service.control.settings(binding().model_id)
    original = service.inputs.snapshot

    def changing(ref, destination):
        value = original(ref, destination)
        if ref == "pre.csv":
            service.update_settings(
                before.model_id,
                SettingsUpdate(
                    expected_revision=before.revision,
                    changes=SettingsChanges(block_size=before.block_size + 1),
                ),
            )
        return value

    monkeypatch.setattr(service.inputs, "snapshot", changing)
    result = ma.processor.process_next()
    assert result is not None and result.state == "completed"
    assert ma.store.settings(receipt.ma_run_id) == before
    assert service.control.settings(before.model_id).revision == before.revision + 1

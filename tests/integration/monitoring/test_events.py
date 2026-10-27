import asyncio
import json
import socket
import sqlite3
import threading
import time
from contextlib import contextmanager

import httpx
import pytest
import uvicorn
from starlette.requests import ClientDisconnect

from tokenscope.api.app import create_app
from tokenscope.domain import RunSubmission, SettingsUpdate
from tokenscope.monitoring.events import EventResponse, PublicationEventReader
from tokenscope.monitoring.publications import PublicationRepository
from tokenscope.monitoring.storage import ControlStore


def fail(service):
    run = service.control.enqueue(RunSubmission(file_ref="synthetic.csv", model_id="GLM-5.2"))
    service.control.claim_next()
    service.control.fail(run.run_id, "SYNTHETIC_FAILURE")
    return run.run_id


@contextmanager
def server(service):
    app = create_app(service, start_worker=False)
    app.state.events.heartbeat = 0.05
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    sock.listen()
    address = f"http://127.0.0.1:{sock.getsockname()[1]}"
    srv = uvicorn.Server(uvicorn.Config(app, log_level="error", lifespan="on"))
    thread = threading.Thread(target=srv.run, kwargs=dict(sockets=[sock]), daemon=True)
    thread.start()
    deadline = time.monotonic() + 5
    while not srv.started:
        assert time.monotonic() < deadline
        time.sleep(0.01)
    try:
        yield address, app
    finally:
        srv.should_exit = True
        thread.join(5)
        sock.close()
        assert not thread.is_alive()


def test_terminal_atomicity_retention_and_identity(service):
    reader = PublicationEventReader(service.control)
    before = PublicationRepository(service.control).catalog()
    run = service.control.enqueue(RunSubmission(file_ref="synthetic.csv", model_id="GLM-5.2"))
    service.control.claim_next()
    with service.control.connect() as db:
        db.execute(
            "CREATE TRIGGER stop_event BEFORE INSERT ON ui_events "
            "BEGIN SELECT RAISE(ABORT,'injected');END"
        )
    with pytest.raises(sqlite3.IntegrityError):
        service.control.fail(run.run_id, "SYNTHETIC_FAILURE")
    assert service.control.run(run.run_id).status == "running"
    with service.control.connect() as db:
        db.execute("DROP TRIGGER stop_event")
    service.control.fail(run.run_id, "SYNTHETIC_FAILURE")
    fail(service)
    ident, _, reason, rows = reader.read(before["cursor"])
    assert reason is None and len(rows) == 2
    assert all(r["kind"] == "run_terminal" for r in rows)
    assert PublicationRepository(service.control).catalog()["catalog_revision"] == "0"
    assert json.loads(rows[0]["payload"])["run_id"] == run.run_id
    reader.prune(max_rows=1)
    assert reader.read(before["cursor"])[2] == "expired"
    assert len(reader.read(ident["service_instance_id"] + ":1")[3]) == 1
    reader.prune(days=0)
    assert reader.read(ident["service_instance_id"] + ":2")[2] is None
    assert reader.read(ident["service_instance_id"] + ":3")[2] == "future_cursor"
    assert reader.read("other:0")[2] == "instance_changed"
    assert reader.read("garbage")[2] == "invalid_cursor"
    restored = PublicationRepository(ControlStore(service.control.path)).catalog()
    assert restored["service_instance_id"] == ident["service_instance_id"]
    assert service.control.run(run.run_id).status == "failed"


def test_claim_failure_has_terminal_event(service):
    run = service.control.enqueue(RunSubmission(file_ref="synthetic.csv", model_id="Qwen3.6-27B"))
    service.control.update_settings(
        "Qwen3.6-27B", SettingsUpdate(expected_revision=1, changes=dict(hybrid_enabled=True))
    )
    assert service.control.claim_next().status == "failed"
    with service.control.connect() as db:
        data = json.loads(db.execute("SELECT payload FROM ui_events").fetchone()[0])
    assert data["run_id"] == run.run_id and data["error_code"] == "UNSUPPORTED_CACHE_MODE"


def test_actual_http_sse_replay_header_priority_heartbeat_capacity(service):
    cursor = PublicationRepository(service.control).catalog()["cursor"]
    run_id = fail(service)
    with server(service) as (url, app), httpx.Client(timeout=3) as client:
        with client.stream(
            "GET",
            url + "/monitoring/events",
            params=dict(after="bad"),
            headers={"Last-Event-ID": cursor},
        ) as stream:
            assert stream.status_code == 200
            event = []
            for line in stream.iter_lines():
                event.append(line)
                if line.startswith("data:"):
                    break
            assert any(line == "event: run_terminal" for line in event)
            assert run_id in event[-1]
        after = PublicationRepository(service.control).catalog()["cursor"]
        with client.stream("GET", url + "/monitoring/events", params=dict(after=after)) as stream:
            assert (
                next(line for line in stream.iter_lines() if line.startswith(":")) == ": heartbeat"
            )
        reset = client.get(url + "/monitoring/events?after=invalid")
        assert "event: reset" in reset.text and "id:" not in reset.text
        app.state.events.capacity = 0
        response = client.get(url + "/monitoring/events")
        assert (
            response.status_code == 503
            and response.json()["error"]["code"] == "SSE_CAPACITY_EXCEEDED"
        )


def test_bounded_send_releases_capacity_on_timeout(service):
    async def run():
        reader = PublicationEventReader(service.control, send_timeout=0.01)
        reader.reserve()
        response = EventResponse(reader, None, "synthetic")

        async def slow_send(message):
            await asyncio.sleep(1)

        async def receive():
            await asyncio.sleep(1)
            return {"type": "http.disconnect"}

        with pytest.raises(ClientDisconnect):
            await response({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, slow_send)
        assert reader.active == 0

    asyncio.run(run())

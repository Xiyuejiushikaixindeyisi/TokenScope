import asyncio
import json
import threading
from pathlib import Path

import pytest

from tokenscope.analysis_common.contracts import AnalysisScope, SourceIdentity
from tokenscope.analysis_common.discovery import Discovery
from tokenscope.analysis_common.discovery_contracts import Catalog, Terminal, TerminalEvent
from tokenscope.analysis_common.storage import DiagnosticStore
from tokenscope.analysis_common.wire import from_wire
from tokenscope.api.diagnostic_discovery import DiscoveryResponse, stream
from tokenscope.errors import TokenScopeError


def source(model="m", appid="a"):
    return AnalysisScope(
        source=SourceIdentity(
            base_run_id="r",
            model_id=model,
            manifest_sha256="a" * 64,
            asset_identity="asset",
            encoder_identity="encoder",
            profile_json="{}",
            settings_json="{}",
            algorithm_version="1",
        ),
        appid=appid,
        window=None,
        request_count=1,
        request_keys_digest="b" * 64,
        baseline_origin="original_run_window",
    ).model_dump_json()


def publish(store, key, status="ready", *, model="m", low=True, kind="analysis"):
    intent = {
        "kind": kind,
        "parent": "parent" if kind != "analysis" else None,
        "request": {"selection": {"enable_low_hit": low, "enable_token_content": True}},
    }
    task = store.submit(key, json.dumps(intent), source(model), "{}")
    store.update(task.task_id, status="running")
    work = store.root / ("work-" + key)
    work.mkdir()
    store.publish(task.task_id, work, {"stages": []}, status)
    return task.task_id


def test_atomic_outbox_readable_replay_and_snapshot(tmp_path):
    store = DiagnosticStore(tmp_path)
    reader = Discovery(store, "instance")
    empty = reader.catalog()
    first = publish(store, "first")
    second = publish(store, "second", "partial")
    page = reader.catalog(limit=1)
    third = publish(store, "third", low=False)
    tail = reader.catalog(page["snapshot"], page["next_after"], limit=1)
    assert [e["task_id"] for e in page["items"] + tail["items"]] == [first, second]
    assert tail["defaults"] == page["defaults"] and tail["next_after"] is None
    batch = reader.events(empty["event_cursor"])
    from_wire(Catalog, reader.catalog())
    from_wire(Terminal, reader.terminal(first))
    assert [e["task_id"] for e in batch["items"]] == [first, second, third]
    assert batch == reader.events(empty["event_cursor"])
    for event in batch["items"]:
        from_wire(
            TerminalEvent,
            {"version": "diagnostics-discovery-1", "service_instance_id": "instance", **event},
        )
        assert "scope" not in event and event["published_at"] == event["terminal_at"]
        assert store.result_directory(event["task_id"]).is_dir()
    current = {e["direction"]: e["task_id"] for e in reader.catalog()["defaults"]}
    assert current == {"low_hit": first, "token_content": third}
    assert reader.events(batch["cursor"])["items"] == []
    assert Discovery(DiagnosticStore(tmp_path), "instance").catalog() == reader.catalog()


def test_partial_empty_evaluation_and_models_never_overwrite(tmp_path):
    store = DiagnosticStore(tmp_path)
    reader = Discovery(store, "i")
    publish(store, "partial", "partial")
    publish(store, "empty", "empty")
    assert reader.catalog()["defaults"] == []
    first = publish(store, "first")
    second = publish(store, "model2", model="m2")
    evaluated = publish(store, "eval", kind="token_authorization")
    assert {v["task_id"] for v in reader.catalog()["defaults"]} == {first, second}
    assert evaluated not in {v["task_id"] for v in reader.catalog()["items"]}
    assert reader.terminal(evaluated)["terminal"]["parent_task_id"] == "parent"


def test_failed_cancel_recover_and_rollback_have_durable_terminal(tmp_path):
    store = DiagnosticStore(tmp_path)
    reader = Discovery(store, "i")
    cursor = reader.catalog()["event_cursor"]
    for key in ("cancel", "failed", "restart"):
        task = store.submit(key, '{"kind":"analysis"}', source(), "{}")
        if key == "cancel":
            store.cancel(task.task_id)
        else:
            store.update(task.task_id, status="running")
            if key == "failed":
                store.update(task.task_id, status="failed", error="EXAMPLE")
    store.recover()
    assert len(reader.events(cursor)["items"]) == 3
    assert reader.catalog()["items"] == []
    task = store.submit("rollback", '{"kind":"analysis"}', source(), "{}")
    with pytest.raises(RuntimeError), store.connect() as db:
        db.execute("UPDATE tasks SET status='failed' WHERE id=?", (task.task_id,))
        raise RuntimeError("transaction rollback")
    assert reader.terminal(task.task_id)["terminal"] is None
    assert len(reader.events(cursor)["items"]) == 3


def test_legacy_migration_no_fabricated_timestamp_or_default(tmp_path):
    store = DiagnosticStore(tmp_path)
    task_id = publish(store, "old")
    with store.connect() as db:
        db.execute("DROP TRIGGER diagnostic_terminal_outbox")
        db.execute("DROP TABLE diagnostic_terminals")
        db.execute("DROP TABLE discovery_meta")
    migrated = Discovery(DiagnosticStore(tmp_path), "i")
    entry = migrated.terminal(task_id)["terminal"]
    assert entry["legacy"] and entry["analysis_completed_at"] is None
    assert migrated.catalog()["items"][0]["task_id"] == task_id
    assert migrated.catalog()["defaults"] == []


def test_reset_validation_and_stream_resume(tmp_path):
    reader = Discovery(DiagnosticStore(tmp_path), "i")
    cursor = reader.catalog()["event_cursor"]
    task_id = publish(reader.store, "new")

    async def consume():
        generator = stream(reader, cursor)
        assert await anext(generator) == b"retry: 3000\n\n"
        event = await anext(generator)
        assert b"event: terminal" in event and task_id.encode() in event
        await generator.aclose()
        reset = stream(reader, "another-instance:0")
        await anext(reset)
        assert b"event: reset" in await anext(reset)
        with pytest.raises(StopAsyncIteration):
            await anext(reset)

    asyncio.run(consume())
    for invalid in ("bad", cursor.rsplit(":", 1)[0] + ":999999", cursor + "x"):
        with pytest.raises(TokenScopeError, match="cursor|changed"):
            reader.catalog(invalid)
    with pytest.raises(TokenScopeError):
        reader.catalog(after="1")


def test_sse_disconnect_releases_capacity_and_heartbeat_is_readonly(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from starlette.requests import ClientDisconnect

    reader = Discovery(DiagnosticStore(tmp_path), "i")
    cursor = reader.catalog()["event_cursor"]
    publish(reader.store, "sse")
    slots = threading.BoundedSemaphore(1)
    sent = []

    async def send(message):
        sent.append(message)
        if message.get("body", b"").startswith(b"id:"):
            raise OSError("client disconnected")

    async def receive():
        return {"type": "http.disconnect"}

    async def check():
        response = DiscoveryResponse(reader, cursor, slots)
        with pytest.raises(ClientDisconnect):
            await response({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, send)
        assert slots.acquire(False)
        blocked = []

        async def capacity_send(message):
            blocked.append(message)

        await DiscoveryResponse(reader, cursor, slots)(
            {"type": "http", "asgi": {"spec_version": "2.4"}}, receive, capacity_send
        )
        assert blocked[0]["status"] == 503
        slots.release()
        ticks = iter([0, 21, 22])
        monkeypatch.setattr(
            "tokenscope.api.diagnostic_discovery.time",
            SimpleNamespace(monotonic=lambda: next(ticks)),
        )
        # Only the journal is read, not report/receipt/analysis.
        monkeypatch.setattr(reader.store, "result_directory", lambda *_: pytest.fail("report read"))
        gen = stream(reader, reader.catalog()["event_cursor"])
        await anext(gen)
        assert await anext(gen) == b": heartbeat\n\n"
        await gen.aclose()
        monkeypatch.undo()

    asyncio.run(check())


def test_frozen_discovery_schema_and_source_manifest():
    import hashlib

    from tokenscope.analysis_common.discovery_contracts import schemas

    root = Path(__file__).resolve().parents[3]
    folder = root / "docs/contracts/diagnostics-discovery-1"
    assert json.loads((folder / "wire.json").read_text()) == schemas()
    manifest = json.loads((folder / "manifest.json").read_text())
    for path, digest in manifest["files"].items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest

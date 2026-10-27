import fcntl
import json
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from conftest import csv_bytes, valid_row

from tokenscope.domain import DEFAULT_SETTINGS, RunSubmission
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.service import MonitoringService
from tokenscope.monitoring.storage import ControlStore


def submit(service, rows=None, model="GLM-5.2"):
    (service.inputs.root / "input.csv").write_bytes(csv_bytes(rows or [valid_row()]))
    return service.submit(RunSubmission(file_ref="input.csv", model_id=model))


@pytest.mark.parametrize("model", list(DEFAULT_SETTINGS))
def test_batch_size_invariance(tmp_path, model):
    inputs = tmp_path / "input"
    inputs.mkdir()
    raw = json.dumps(
        {"messages": [{"role": "user", "content": "shared " * 4000}], "enable_thinking": False}
    )
    (inputs / "data.csv").write_bytes(
        csv_bytes(
            [valid_row(hash_id=str(i), appid=str(i % 2), request_input=raw) for i in range(7)]
        )
    )
    all_facts = []
    all_groups = []
    for batch in [1, 256]:
        service = MonitoringService(inputs, tmp_path / f"state-{batch}", batch_rows=batch)
        run = service.submit(RunSubmission(file_ref="data.csv", model_id=model))
        assert service.processor.process_next().status == "completed"
        with service.result_db(run.run_id) as db:
            all_facts.append(
                [
                    tuple(r)
                    for r in db.execute("""SELECT source_record_index,json_tokens,
                prompt_tokens,ideal_cached_input_tokens,ideal_compute_input_tokens,completion_tokens,
                token_slice_json,evidence_json,events_json
                FROM facts ORDER BY source_record_index""")
                ]
            )
        all_groups.append(service.metrics(run.run_id)["groups"])
    assert all_facts[0] == all_facts[1]
    assert all_groups[0] == all_groups[1]


def test_worker_process_lock_prevents_parallel_claim_and_recovery(service):
    first = submit(service)
    second = submit(service)
    with (service.state_root / "worker.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert service.processor.process_next() is None
        assert service.control.run(first.run_id).status == "queued"
        assert service.control.run(second.run_id).status == "queued"


def test_readers_never_observe_unpublished_facts(service, monkeypatch):
    run = submit(service)
    entered = threading.Event()
    release = threading.Event()
    original = service.control.complete

    def hold(*args):
        entered.set()
        assert release.wait(10)
        return original(*args)

    monkeypatch.setattr(service.control, "complete", hold)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(service.processor.process_next)
        assert entered.wait(20)
        try:
            assert (service.state_root / "runs" / run.run_id).is_dir()
            with pytest.raises(TokenScopeError) as error:
                service.metrics(run.run_id)
            assert error.value.code == "RESULT_NOT_READY"
            assert service.processor.process_next() is None
        finally:
            release.set()
        assert future.result().status == "completed"


def test_corrupt_seal_and_token_shard_do_not_pass_recovery(service, monkeypatch):
    run = submit(service)
    original = service.control.complete

    def fail(*args):
        raise OSError("injected")

    monkeypatch.setattr(service.control, "complete", fail)
    service.processor.process_next()
    directory = service.state_root / "runs" / run.run_id
    shard = next((directory / "tokens").glob("*.bin"))
    with shard.open("r+b") as stream:
        stream.write(b"bad!")
    monkeypatch.setattr(service.control, "complete", original)
    service.processor.process_next()
    assert service.control.run(run.run_id).status == "interrupted"
    assert service.control.run(run.run_id).error_code == "RESULT_SEAL_INVALID"
    with pytest.raises(TokenScopeError):
        service.metrics(run.run_id)


def test_input_changed_after_enqueue_and_malformed_file(service):
    run = submit(service)
    (service.inputs.root / "input.csv").write_bytes(b"wrong,header\n")
    assert service.processor.process_next().status == "failed"
    assert service.control.run(run.run_id).error_code == "INVALID_CSV_HEADER"
    with pytest.raises(TokenScopeError):
        service.metrics(run.run_id)


def test_write_failure_is_run_error_not_skipped_row(service, monkeypatch):
    import tokenscope.monitoring.pipeline as pipeline

    run = submit(service)

    def fail(*args, **kwargs):
        raise OSError("No space left on device")

    monkeypatch.setattr(pipeline, "encode_input", fail)
    assert service.processor.process_next().error_code == "STORAGE_UNAVAILABLE"
    assert service.control.run(run.run_id).result is None
    assert not (service.state_root / "runs" / run.run_id).exists()


def test_schema_one_is_migrated_without_losing_settings(tmp_path):
    path = tmp_path / "control.sqlite3"
    store = ControlStore(path)
    with store.connect() as db:
        db.execute("PRAGMA user_version=1")
        db.execute("DROP TABLE run_signals")
        db.execute("DROP TABLE outbox")
    reopened = ControlStore(path)
    assert reopened.settings("GLM-5.2").block_size == 128
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 3
        assert db.execute("SELECT count(*) FROM outbox").fetchone()[0] == 0

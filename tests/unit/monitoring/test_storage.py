import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest
from conftest import csv_bytes, valid_row
from pydantic import ValidationError

from tokenscope.domain import (
    DEFAULT_SETTINGS,
    ModelSettings,
    RunSubmission,
    SettingsUpdate,
    capability,
)
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.storage import ControlStore, RawRequestStore


def change(store, changes, revision=1, model="GLM-5.2"):
    return store.update_settings(
        model, SettingsUpdate.model_validate({"expected_revision": revision, "changes": changes})
    )


def test_defaults_and_immutable_models():
    assert [s.block_size for s in DEFAULT_SETTINGS.values()] == [128, 1536, 32]
    for settings in DEFAULT_SETTINGS.values():
        assert settings.mtp and settings.cp_world_size == 1
        assert capability(settings).executable
        with pytest.raises(ValidationError):
            settings.block_size = 1


@pytest.mark.parametrize(
    "patch",
    [
        {"block_size": 0},
        {"block_size": True},
        {"cp_world_size": -1},
        {"mtp": "yes"},
        {"cache_mode": "qwen_hybrid"},
        {"unknown": 5},
    ],
)
def test_invalid_settings_rejected(patch):
    values = DEFAULT_SETTINGS["GLM-5.2"].model_dump()
    values.update(patch)
    with pytest.raises(ValidationError):
        ModelSettings.model_validate(values)


def test_freeze_on_start_not_queue_and_reopen(tmp_path):
    path = tmp_path / "control.db"
    store = ControlStore(path)
    queued = store.enqueue(RunSubmission(file_ref="glm.csv", model_id="GLM-5.2"))
    assert queued.settings is None
    updated = change(store, {"block_size": 256, "cp_world_size": 2})
    running = store.claim_next()
    assert running.run_id == queued.run_id
    assert running.settings == updated
    assert running.settings.effective_block_size == 512
    change(store, {"block_size": 512}, revision=2)
    assert ControlStore(path).run(queued.run_id).settings == updated
    store.fail(running.run_id, "TEST_INTERRUPTED", interrupted=True)
    second = store.enqueue(RunSubmission(file_ref="glm.csv", model_id="GLM-5.2"))
    assert store.claim_next().settings.revision == 3
    assert store.run(second.run_id).status == "running"
    assert store.run(queued.run_id).status == "interrupted"


def test_revision_conflict_and_null_rollback(tmp_path):
    store = ControlStore(tmp_path / "control.db")
    change(store, {"block_size": 256})
    with pytest.raises(TokenScopeError) as exc:
        change(store, {"block_size": 512})
    assert exc.value.code == "REVISION_CONFLICT"
    with pytest.raises(TokenScopeError):
        change(store, {"block_size": None}, revision=2)
    assert store.settings("GLM-5.2").revision == 2
    assert store.settings("GLM-5.2").block_size == 256


def test_concurrent_config_update_only_one_wins(tmp_path):
    store = ControlStore(tmp_path / "control.db")

    def update(value):
        try:
            return change(store, {"block_size": value}).revision
        except TokenScopeError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(update, [256, 512]))
    assert results.count(2) == 1
    assert results.count("REVISION_CONFLICT") == 1


def test_one_active_run_and_invalid_state_transition(tmp_path):
    store = ControlStore(tmp_path / "control.db")
    for _ in range(2):
        store.enqueue(RunSubmission(file_ref="a.csv", model_id="GLM-5.2"))
    with ThreadPoolExecutor(max_workers=2) as pool:
        claimed = list(pool.map(lambda _: store.claim_next(), range(2)))
    assert sum(run is not None for run in claimed) == 1
    active = next(run for run in claimed if run)
    store.fail(active.run_id, "TEST_FAILURE")
    with pytest.raises(TokenScopeError):
        store.fail(active.run_id, "TEST_FAILURE")
    assert store.claim_next().status == "running"


def test_hybrid_selection_never_falls_back(tmp_path):
    store = ControlStore(tmp_path / "control.db")
    change(store, {"hybrid_enabled": True, "cache_mode": "qwen_hybrid"}, model="Qwen3.6-27B")
    queued = store.enqueue(RunSubmission(file_ref="a.csv", model_id="Qwen3.6-27B"))
    run = store.claim_next()
    assert run.run_id == queued.run_id
    assert run.status == "failed"
    assert run.error_code == "UNSUPPORTED_CACHE_MODE"


def test_future_database_version_not_modified(tmp_path):
    path = tmp_path / "control.db"
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA user_version=999")
    before = path.read_bytes()
    with pytest.raises(TokenScopeError):
        ControlStore(path)
    assert path.read_bytes() == before


def test_duplicates_kept_and_exact_stable_order(tmp_path, reader):
    source = tmp_path / "data.csv"
    source.write_bytes(
        csv_bytes(
            [
                valid_row(model_handle_start_time="2026-10-27T00:00:00.000000002Z"),
                valid_row(model_handle_start_time="2026-10-27T00:00:00.000000001Z"),
                valid_row(model_handle_start_time="2026-10-27T00:00:00.000000001Z"),
                valid_row(completion_tokens="bad"),
            ]
        )
    )
    store = RawRequestStore(tmp_path / "requests.db")
    quality = store.ingest(source, reader)
    assert quality.model_dump() == dict(
        records_read=4, valid_requests=3, skipped_rows=1, duplicate_hash_id_rows=2
    )
    assert [r.source_record_index for r in store.replay_records()] == [2, 3, 1]
    with pytest.raises(TokenScopeError) as error:
        store.ingest(source, reader)
    assert error.value.code == "INPUT_ALREADY_STARTED"
    assert len(list(store.replay_records())) == 3
    with pytest.raises(FileExistsError):
        RawRequestStore(store.path)


def test_mid_input_failure_not_completed(tmp_path, reader):
    from tokenscope.ingestion.csv_reader import CsvBatchReader

    source = tmp_path / "data.csv"
    source.write_bytes(csv_bytes([valid_row(), valid_row()]) + b'"unclosed')
    store = RawRequestStore(tmp_path / "requests.db")
    with pytest.raises(TokenScopeError):
        store.ingest(source, CsvBatchReader(reader.settings, batch_rows=1))
    with store.connect() as db:
        assert db.execute("SELECT complete FROM input_status").fetchone()[0] == 0
    with pytest.raises(TokenScopeError):
        list(store.replay_records())


def test_sqlite_write_failure_not_bad_row(tmp_path, reader):
    source = tmp_path / "data.csv"
    source.write_bytes(csv_bytes([valid_row()]))
    store = RawRequestStore(tmp_path / "requests.db")
    with store.connect() as db:
        db.execute("""CREATE TRIGGER fail_write BEFORE INSERT ON request_records
                      BEGIN SELECT RAISE(ABORT, 'injected storage failure'); END""")
    with pytest.raises(sqlite3.IntegrityError):
        store.ingest(source, reader)
    with store.connect() as db:
        assert db.execute("SELECT complete FROM input_status").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM row_errors").fetchone()[0] == 0


def test_empty_valid_input_is_not_fake_request(tmp_path, reader):
    source = tmp_path / "empty.csv"
    source.write_bytes(csv_bytes([]))
    store = RawRequestStore(tmp_path / "empty.db")
    assert store.ingest(source, reader).records_read == 0
    assert list(store.replay_records()) == []

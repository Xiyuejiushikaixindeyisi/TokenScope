import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from conftest import csv_bytes, valid_row

from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.user_monitoring.contracts import Bind, Submit
from tokenscope.user_monitoring.service import UserRunService


def submitted(service, model="GLM-5.2", common="GLM-V5.2"):
    raw = json.dumps({"messages": [{"role": "user", "content": "shared prefix " * 2000}]})
    (service.inputs.root / "user.csv").write_bytes(
        csv_bytes(
            [valid_row(hash_id="dup", appid=appid, request_input=raw) for appid in ("a", "b", "a")]
            + [valid_row(completion_tokens="bad")]
        )
    )
    user = UserRunService(service)
    request = Submit(submission_key="key", file_ref="user.csv", common_name=common, model_id=model)
    return user, request, user.submit(request)


@pytest.mark.parametrize(
    "model,common",
    [
        ("GLM-5.2", "GLM-V5.2"),
        ("Qwen3.6-27B", "Qwen-V3.6-27B"),
        ("DeepSeek-V4-Flash-0731", "DeepSeek-V4-Flash"),
    ],
)
def test_binding_real_facts_and_rebuild(service, model, common):
    user, request, receipt = submitted(service, model, common)
    assert user.submit(request) == receipt
    pending = user.process_next()
    assert pending.state == "base_pending"
    assert user.process_next() is None
    assert service.processor.process_next().status == "completed"
    directory = service.state_root / "runs" / pending.base_run_id
    seal = file_digest(directory / "manifest.json")
    ready = user.process_next()
    assert ready.state == "ready"
    with user.index(ready.user_run_id) as db:
        groups = [
            json.loads(r[0])
            for r in db.execute("SELECT payload FROM groups WHERE width=5000 ORDER BY appid")
        ]
        assert [g["request_count"] for g in groups] == ["2", "1"]
        assert int(groups[0]["total_ideal_cached_tokens"]) > 0
        assert groups[1]["total_ideal_cached_tokens"] == "0"
    user.rebuild(ready.user_run_id)
    assert user.process_next().index_revision == ready.index_revision
    assert file_digest(directory / "manifest.json") == seal
    assert UserRunService(service).receipt(ready.user_run_id) == ready
    with pytest.raises(TokenScopeError):
        user.submit(request.model_copy(update={"common_name": "unknown"}))
    with pytest.raises(TokenScopeError):
        user.index("ma-not-a-user-run").__enter__()


def test_concurrent_intent_and_crash_after_base_submit(service, monkeypatch):
    user, request, receipt = submitted(service)
    with ThreadPoolExecutor(4) as pool:
        assert {r.user_run_id for r in pool.map(user.submit, [request] * 8)} == {
            receipt.user_run_id
        }
    original = user.store.update

    def fail(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(user.store, "update", fail)
    assert user.process_next().state == "accepted"
    monkeypatch.setattr(user.store, "update", original)
    pending = user.process_next()
    with service.control.connect() as db:
        assert db.execute("SELECT count(*) FROM analysis_runs").fetchone()[0] == 1
    assert pending.base_run_id


def test_mixed_service_and_alias_rejected(service):
    user, request, receipt = submitted(service)
    from tokenscope.ingestion.csv_reader import REQUIRED_COLUMNS

    (service.inputs.root / "user.csv").write_bytes(
        csv_bytes([valid_row() + ["another"]], header=(*REQUIRED_COLUMNS, "common_name"))
    )
    failed = user.process_next()
    assert failed.error_code == "SERVICE_BINDING_CONFLICT"
    with pytest.raises(TokenScopeError, match="alias"):
        user.submit(
            request.model_copy(update={"submission_key": "other", "common_name": "unknown"})
        )


def test_publish_interruption_lock_and_corruption(service, monkeypatch):
    import fcntl

    user, _, receipt = submitted(service)
    with (service.state_root / "worker.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        assert user.process_next() is None
    user.process_next()
    service.processor.process_next()
    original = user.publish
    monkeypatch.setattr(user, "publish", lambda *args: (_ for _ in ()).throw(OSError("crash")))
    assert user.process_next().state == "indexing"
    with pytest.raises(TokenScopeError, match="published"):
        with user.index(receipt.user_run_id):
            pass
    monkeypatch.setattr(user, "publish", original)
    assert user.process_next().state == "ready"
    path = user.root / (receipt.user_run_id + ".sqlite3")
    with path.open("ab") as stream:
        stream.write(b"corrupt")
    with pytest.raises(TokenScopeError, match="digest"):
        with user.index(receipt.user_run_id):
            pass


def test_historical_binding_and_bad_source(service):
    from tokenscope.domain import RunSubmission

    (service.inputs.root / "old.csv").write_bytes(csv_bytes([valid_row()]))
    base = service.submit(RunSubmission(file_ref="old.csv", model_id="GLM-5.2"))
    service.processor.process_next()
    user = UserRunService(service)
    receipt = user.submit(
        Bind(submission_key="old", base_run_id=base.run_id, common_name="GLM-V5.2")
    )
    (service.state_root / "runs" / base.run_id / "input.csv").write_text("corrupt")
    assert user.process_next().error_code == "RESULT_SEAL_INVALID"
    assert user.receipt(receipt.user_run_id).state == "failed"


def test_all_invalid_is_empty_and_missing_source_is_explicit(service):
    user, request, _ = submitted(service)
    (service.inputs.root / "user.csv").write_bytes(csv_bytes([valid_row(completion_tokens="bad")]))
    user.process_next()
    assert service.processor.process_next().status == "no_valid_rows"
    result = user.process_next()
    assert result.state == "empty", result
    with user.index(result.user_run_id) as db:
        assert db.execute("SELECT count(*) FROM groups").fetchone()[0] == 0
    user.rebuild(result.user_run_id)
    (service.state_root / "runs" / result.base_run_id / "requests.sqlite3").unlink()
    assert user.process_next().error_code == "REANALYSIS_REQUIRED"


def test_pre_rename_storage_failure_and_recovery(service, monkeypatch):
    from tokenscope.user_monitoring import projection

    user, _, receipt = submitted(service)
    user.process_next()
    service.processor.process_next()
    original = projection.os.replace
    monkeypatch.setattr(
        projection.os, "replace", lambda *args: (_ for _ in ()).throw(PermissionError())
    )
    assert user.process_next().state == "indexing"
    assert not (user.root / (receipt.user_run_id + ".sqlite3")).exists()
    assert not list(user.root.glob("*.tmp"))
    monkeypatch.setattr(projection.os, "replace", original)
    assert user.process_next().state == "ready"

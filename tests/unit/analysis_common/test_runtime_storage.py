import pytest

from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.storage import DiagnosticStore, ResultWriter
from tokenscope.errors import TokenScopeError


def test_publish_crash_never_exposes_orphan(tmp_path, monkeypatch):
    store = DiagnosticStore(tmp_path)
    task = store.submit("key", "{}", "{}", "{}")
    store.update(task.task_id, status="running")
    workspace = tmp_path / "work"
    workspace.mkdir()
    writer = ResultWriter(workspace)
    writer.add("evidence", "one", {"x": "1"})
    writer.close()
    original = store.complete

    def fail(*args, **kwargs):
        raise OSError("injected transaction failure")

    monkeypatch.setattr(store, "complete", fail)
    with pytest.raises(OSError):
        store.publish(task.task_id, workspace, {"complete": True}, "ready")
    assert (tmp_path / task.task_id / "manifest.json").exists()
    with pytest.raises(TokenScopeError, match="published"):
        store.result_directory(task.task_id)
    monkeypatch.setattr(store, "complete", original)
    store.recover()
    assert store.receipt(task.task_id).status == "interrupted"
    with pytest.raises(TokenScopeError, match="intent"):
        store.submit("key", "{}", "{}", "{}", attempt=2)


def test_before_rename_failure_does_not_publish(tmp_path, monkeypatch):
    store = DiagnosticStore(tmp_path)
    task = store.submit("key", "{}", "{}", "{}")
    workspace = tmp_path / "work"
    workspace.mkdir()

    def fail(*args):
        raise OSError("injected disk failure")

    monkeypatch.setattr("tokenscope.analysis_common.storage.os.fsync", fail)
    with pytest.raises(OSError):
        store.publish(task.task_id, workspace, {}, "ready")
    assert not (tmp_path / task.task_id).exists()
    assert store.receipt(task.task_id).report_ref is None


def test_cancel_during_sealing_cannot_publish_success(tmp_path, monkeypatch):
    from pathlib import Path

    store = DiagnosticStore(tmp_path)
    task = store.submit("key", "{}", "{}", "{}")
    store.update(task.task_id, status="running")
    workspace = tmp_path / "work"
    workspace.mkdir()
    rename = Path.rename

    def cancel_then_rename(path, target):
        store.update(task.task_id, cancel=1)
        return rename(path, target)

    monkeypatch.setattr(Path, "rename", cancel_then_rename)
    with pytest.raises(ExecutionStopped, match="INTERRUPTED"):
        store.publish(task.task_id, workspace, {}, "ready")
    assert store.receipt(task.task_id).report_ref is None


def test_atomic_claim_cancel_and_terminal_cancellation(tmp_path):
    store = DiagnosticStore(tmp_path)
    first = store.submit("first", "{}", "{}", "{}")
    second = store.submit("second", "{}", "{}", "{}")
    store.cancel(first.task_id)
    assert store.claim_next() == second.task_id
    assert store.claim_next() is None
    store.complete(second.task_id, "a" * 64, "ready")
    assert store.cancel(second.task_id).status == "ready"
    assert store.row(second.task_id)["cancel"] == 0

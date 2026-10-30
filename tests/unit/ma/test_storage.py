from pathlib import Path

import pytest

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.ma.ingest import connect
from tokenscope.monitoring.ma.storage import Store

from .helpers import binding


def test_receipts_and_publication(tmp_path: Path) -> None:
    store = Store(tmp_path, "service")
    request = binding()
    first = store.enqueue(request)
    assert store.enqueue(request).ma_run_id == first.ma_run_id
    with pytest.raises(TokenScopeError):
        store.enqueue(request.model_copy(update={"model_standard_name": "other"}))
    settings = DEFAULT_SETTINGS[request.model_id]
    store.claim(first.ma_run_id, settings)
    assert store.settings(first.ma_run_id) == settings
    store.complete(first.ma_run_id, {"ok": True})
    store.complete(first.ma_run_id, {"ok": False})
    store.fail(first.ma_run_id, "late_failure")
    assert store.summary(first.ma_run_id) == {"ok": True}
    assert store.receipt(first.ma_run_id).state == "completed"
    with connect(store.path) as db:
        assert db.execute("SELECT revision FROM metadata").fetchone()[0] == 1


def test_normalized_binding(tmp_path: Path) -> None:
    store = Store(tmp_path, "service")
    request = binding()
    first = store.enqueue(request)
    same = request.model_copy(
        update={"pre_start": "2026-10-20T15:00:00+08:00", "pre_file_ref": "./pre.csv"}
    )
    assert store.enqueue(same).ma_run_id == first.ma_run_id
    with pytest.raises(TokenScopeError):
        store.summary(first.ma_run_id)

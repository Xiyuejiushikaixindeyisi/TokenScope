import json

import pytest

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.contracts_v3 import PreparationRequest3
from tokenscope.analysis_common.execution_v3 import automatic_profile, calibrated_sample
from tokenscope.analysis_common.preparation_store import PreparationStore
from tokenscope.analysis_common.runtime_v3 import (
    BudgetLedger,
    CheckpointJournal,
    TaskStopped,
    guard_json,
)
from tokenscope.errors import TokenScopeError


def profile():
    return automatic_profile(available_bytes=2 * 1024**3, source_bytes=1000000, cpu_budget=2)


@pytest.mark.parametrize("kind", list(profile().budgets))
def test_every_budget_before_action_boundary_and_total(kind, monkeypatch):
    # This test isolates counter admission. Real RSS/RLIMIT behavior is exercised
    # by test_execution_v3_resources in fresh bounded child processes.
    monkeypatch.setattr("tokenscope.analysis_common.runtime_v3.current_rss", lambda: 0)
    p = profile()
    ledger = BudgetLedger(p, lambda: False)
    limit = p.budgets[kind]
    ledger.reserve(kind, limit - 1)
    assert ledger.consumed[kind] == limit - 1
    ledger.reserve(kind)
    assert ledger.consumed[kind] == limit
    with pytest.raises(TaskStopped, match="BUDGET_EXHAUSTED"):
        ledger.reserve(kind)
    assert ledger.consumed[kind] == limit
    # Every channel shares this same ledger, not independent copies of the limit.
    with pytest.raises(TaskStopped):
        ledger.reserve_many({kind: 1, "plans": 1})
    if kind != "plans":
        assert ledger.consumed.get("plans", 0) == 0


def test_profile_digest_order_and_cancel_deadline():
    p = profile()
    assert (
        p.digest == p.model_copy(update={"budgets": dict(reversed(list(p.budgets.items())))}).digest
    )
    with pytest.raises(TaskStopped, match="USER_CANCELLED"):
        BudgetLedger(p, lambda: True).reserve("requests")
    with pytest.raises(TaskStopped, match="DEADLINE_EXHAUSTED"):
        BudgetLedger(p, lambda: False, started=0).checkpoint()


def test_tiny_headroom_shrinks_sample_without_spending_safety_reserve():
    p = profile()
    fixed = p.address_space_bytes - 129 * 1024 * 1024
    sample = calibrated_sample(p, fixed)
    assert sample.max_requests == 2
    assert sample.max_raw_bytes == 65536
    assert sample.max_prompt_tokens == 4096
    assert p.address_space_bytes - fixed - 16 * sample.max_raw_bytes == 128 * 1024 * 1024
    with pytest.raises(TokenScopeError, match="fixed overhead"):
        calibrated_sample(p, fixed + 1)


def test_json_admission_before_parser_and_escaped_delimiters():
    def guard(raw, **kw):
        guard_json(raw, **(dict(max_bytes=1000, max_depth=3, max_nodes=10) | kw))

    guard(json.dumps({"s": '[{\\"x"}]}'}))
    guard("[[[0]]]")
    with pytest.raises(TaskStopped, match="JSON_DEPTH_LIMIT"):
        guard("[[[[0]]]]")
    with pytest.raises(TaskStopped, match="JSON_NODE_LIMIT"):
        guard("[0,1,2,3,4,5,6,7,8,9]")
    guard('"中文"', max_bytes=8)
    with pytest.raises(TaskStopped, match="JSON_BYTE_LIMIT"):
        guard('"中文"', max_bytes=7)


def test_checkpoint_only_complete_prefix_survives_half_write_and_corruption(tmp_path):
    journal = CheckpointJournal(tmp_path, max_entries=4, max_bytes=1000)
    (tmp_path / "first.json").write_text('{"complete":true}')
    first = journal.commit("findings", "first.json")
    (tmp_path / "checkpoints" / "000002.json").write_text('{"half":')
    (tmp_path / "checkpoints" / "ignored.pending").write_text("ignored")
    assert journal.committed() == (first,)
    (tmp_path / "first.json").write_text("modified")
    assert journal.committed() == ()
    with pytest.raises(TokenScopeError):
        journal.commit("report", "../escape")


def request(key="one"):
    return PreparationRequest3(
        submission_key=key,
        source=SourceSelection(source_kind="base", base_run_id="base", appid="a"),
    )


def test_store_cancel_publish_race_retry_recovery_and_immutable_terminal(tmp_path):
    store = PreparationStore(tmp_path)
    first = store.submit(request())
    assert store.submit(request()) == first
    assert store.claim().state == "running"
    store.cancel(first.preparation_id)
    stopped = store.finish(
        first.preparation_id,
        {"state": "completed", "sample_id": "sample-x", "manifest_sha256": "a" * 64},
        profile().digest,
    )
    assert stopped.state == "stopped" and stopped.sample_id is None
    assert store.finish(first.preparation_id, {"state": "failed"}, None) == stopped
    with pytest.raises(TokenScopeError, match="new submission key"):
        store.retry(first.preparation_id, "one")
    retry = store.retry(first.preparation_id, "two")
    assert retry.preparation_id != first.preparation_id
    assert store.claim().preparation_id == retry.preparation_id
    restarted = PreparationStore(tmp_path)
    restarted.recover()
    assert restarted.receipt(retry.preparation_id).state == "interrupted"
    assert restarted.claim() is None
    assert restarted.receipt(first.preparation_id) == stopped


def test_finished_task_ignores_late_cancel(tmp_path):
    store = PreparationStore(tmp_path)
    receipt = store.submit(request())
    store.claim()
    done = store.finish(
        receipt.preparation_id,
        {"state": "completed", "sample_id": "sample-x", "manifest_sha256": "a" * 64},
        profile().digest,
    )
    assert store.cancel(receipt.preparation_id) == done
    assert not store.execution(receipt.preparation_id).cancel_requested


def test_journal_disk_full_retains_prior_committed_evidence(tmp_path, monkeypatch):
    import errno
    import os

    journal = CheckpointJournal(tmp_path, max_entries=3, max_bytes=1000)
    (tmp_path / "one").write_text("complete")
    committed = journal.commit("findings", "one")

    def no_space(*args):
        raise OSError(errno.ENOSPC, "injected disk full")

    monkeypatch.setattr(os, "link", no_space)
    with pytest.raises(OSError):
        journal.commit("report", "one")
    assert journal.committed() == (committed,)
    assert not (tmp_path / "checkpoints" / "000002.json").exists()

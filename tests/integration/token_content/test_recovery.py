import pytest
from test_task_service import setup

from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.token_content.plugin import TokenContentPlugin


def test_cancel_retry_preserves_sealed_token_report_and_does_not_double_count(service, monkeypatch):
    diagnostics, receipt, _ = setup(service)
    original = diagnostics.items(receipt.task_id, "fragment")
    report_file = diagnostics.store.result_directory(receipt.task_id) / "report.json"
    before = file_digest(report_file)
    queued = diagnostics.retry(receipt.task_id, "cancel-queued")
    diagnostics.cancel(queued.task_id)
    assert diagnostics.process_next() is None
    assert diagnostics.receipt(queued.task_id).status == "interrupted"
    running = diagnostics.retry(receipt.task_id, "cancel-running")
    analyze = TokenContentPlugin.analyze_request

    def cancel_in_stage(plugin, *args, **kwargs):
        diagnostics.cancel(running.task_id)
        return analyze(plugin, *args, **kwargs)

    monkeypatch.setattr(TokenContentPlugin, "analyze_request", cancel_in_stage)
    assert diagnostics.process_next().status == "interrupted"
    with pytest.raises(TokenScopeError):
        diagnostics.report(running.task_id)
    monkeypatch.setattr(TokenContentPlugin, "analyze_request", analyze)
    retried = diagnostics.retry(running.task_id, "retry-real")
    assert retried.attempt == 3
    assert diagnostics.process_next().status == "ready"
    assert diagnostics.items(retried.task_id, "fragment") == original
    assert len(original) == 2 and file_digest(report_file) == before


def test_changed_shared_source_blocks_before_token_and_preserves_original_report(
    service, monkeypatch
):
    diagnostics, receipt, source = setup(service)
    report = diagnostics.report(receipt.task_id)
    queued = diagnostics.retry(receipt.task_id, "changed-source")
    # Fault injection only in pytest's disposable source fixture; restore bytes afterwards.
    manifest = source.directory / "manifest.json"
    sealed = manifest.read_bytes()

    def forbidden(*args, **kwargs):
        raise AssertionError("Token ran on invalid source")

    monkeypatch.setattr(TokenContentPlugin, "analyze_request", forbidden)
    try:
        manifest.write_bytes(sealed + b"\n")
        assert diagnostics.process_next().status == "failed"
        with pytest.raises(TokenScopeError):
            diagnostics.report(queued.task_id)
    finally:
        manifest.write_bytes(sealed)
    assert diagnostics.report(receipt.task_id) == report

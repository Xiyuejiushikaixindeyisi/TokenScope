import json

import pytest
from conftest import csv_bytes, valid_row

from tokenscope.analysis_common.contracts import RequestKey, SourceSelection, TimeWindow
from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.domain import DEFAULT_SETTINGS, RunSubmission
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.user_monitoring.contracts import Bind
from tokenscope.user_monitoring.service import UserRunService


def prepare(service, model="GLM-5.2"):
    raw = json.dumps(
        {"messages": [{"role": "user", "content": "共享前缀" * 12000}], "enable_thinking": False},
        ensure_ascii=False,
    )
    rows = [
        valid_row(
            hash_id="duplicate",
            appid=appid,
            request_input=raw,
            model_handle_start_time=f"2026-10-27T00:00:0{second}Z",
        )
        for appid, second in [("a", 2), ("b", 1), ("a", 1), ("a", 2)]
    ]
    (service.inputs.root / "source.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="source.csv", model_id=model))
    assert service.processor.process_next().status == "completed"
    return run.run_id


@pytest.mark.parametrize("model", list(DEFAULT_SETTINGS))
def test_real_scope_and_encoding_identity(service, model):
    run_id = prepare(service, model)
    resolver = SourceResolver(service)
    source = resolver.resolve_scope(
        SourceSelection(source_kind="base", base_run_id=run_id, appid="a")
    )
    before = file_digest(source.directory / "requests.sqlite3")
    requests = list(source.iter_requests())
    assert [r.request_key.source_record_index for r in requests] == [3, 1, 4]
    assert all(len(r.raw_body.encode()) > 65536 for r in requests)
    context = EncodingContext(source)
    for request in requests:
        context.verify_baseline(request)
    assert file_digest(source.directory / "requests.sqlite3") == before
    with pytest.raises(TokenScopeError, match="outside scope"):
        source.read_request(RequestKey(base_run_id=run_id, source_record_index=2))
    selected = resolver.resolve_scope(
        SourceSelection(
            source_kind="base",
            base_run_id=run_id,
            appid="a",
            window=TimeWindow(start_ns=requests[0].time_ns, end_ns=requests[1].time_ns),
        )
    )
    assert [r.request_key.source_record_index for r in selected.iter_requests()] == [3]
    assert selected.scope.baseline_origin == "selected_window_recomputed"
    empty = resolver.resolve_scope(
        SourceSelection(source_kind="base", base_run_id=run_id, appid="missing")
    )
    assert empty.scope.request_count == 0 and list(empty.iter_requests()) == []


def test_user_binding_and_changed_seal(service):
    run_id = prepare(service)
    user = UserRunService(service)
    receipt = user.submit(Bind(submission_key="bind", base_run_id=run_id, common_name="GLM-5.2"))
    user.process_next()
    receipt = user.receipt(receipt.user_run_id)
    source = SourceResolver(service, user).resolve_scope(
        SourceSelection(
            source_kind="user_v2",
            user_run_id=receipt.user_run_id,
            appid="a",
            expected_index_revision=receipt.index_revision,
        )
    )
    assert source.scope.source.common_name == "GLM-5.2"
    with pytest.raises(TokenScopeError):
        SourceResolver(service, user).resolve_scope(
            SourceSelection(
                source_kind="user_v2",
                user_run_id=receipt.user_run_id,
                appid="a",
                expected_index_revision="stale",
            )
        )
    manifest = source.directory / "manifest.json"
    manifest.write_text(manifest.read_text() + " ")
    with pytest.raises(TokenScopeError, match="manifest changed"):
        list(source.iter_requests())

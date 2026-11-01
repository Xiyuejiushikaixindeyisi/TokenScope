import json

import pytest
from test_source import prepare

from tokenscope.analysis_common.contracts import (
    Location,
    ModificationPlan,
    PreparedMutation,
    SourceSelection,
    TargetLocation,
    TimeWindow,
)
from tokenscope.analysis_common.evaluation import evaluate_plan
from tokenscope.analysis_common.modifications import value_digest
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.monitoring.pipeline import file_digest


def plan_for(source, request, replacement, guard=None):
    original = json.loads(request.raw_body)["messages"][0]["content"]
    operation = PreparedMutation(
        operation_id="op",
        handler_id="test",
        handler_version="1",
        target=TargetLocation(
            location=Location(
                request_key=request.request_key,
                raw_sha256=request.raw_sha256,
                source_pointer="/messages/0/content",
            ),
            original_type="string",
            value_guard=guard or value_digest(original),
        ),
        public_primitive="replace_value",
        replacement_json=json.dumps(replacement),
    )
    return ModificationPlan(
        plan_id="p",
        version="1",
        source_scope_id=source.scope.scope_id,
        transformation_digest="a" * 64,
        direction="low_hit",
        action_class="stabilization",
        finding_refs=(),
        operations=(operation,),
    )


@pytest.mark.parametrize("model", list(DEFAULT_SETTINGS))
def test_real_replay_noop_and_atomic_failure(service, tmp_path, model):
    run_id = prepare(service, model)
    source = SourceResolver(service).resolve_scope(
        SourceSelection(source_kind="base", base_run_id=run_id, appid="a")
    )
    requests = list(source.iter_requests())
    request = requests[1]
    original = json.loads(request.raw_body)["messages"][0]["content"]
    digest = file_digest(source.directory / "requests.sqlite3")
    result = evaluate_plan(source, plan_for(source, request, original), tmp_path / "eval")
    assert result.status == "available", result
    assert result.before == result.after
    assert result.before.h == sum(r.baseline_metrics.h for r in requests)
    assert result.modified_after.n == 0
    failed = evaluate_plan(source, plan_for(source, request, "short", "b" * 64), tmp_path / "bad")
    assert failed.status == "blocked" and failed.after is None
    assert "MODIFICATION_GUARD_FAILED" in failed.reason_codes
    assert file_digest(source.directory / "requests.sqlite3") == digest


def test_subwindow_recomputes_empty_baseline(service, tmp_path):
    run_id = prepare(service)
    resolver = SourceResolver(service)
    full = resolver.resolve_scope(
        SourceSelection(source_kind="base", base_run_id=run_id, appid="a")
    )
    requests = list(full.iter_requests())
    source = resolver.resolve_scope(
        SourceSelection(
            source_kind="base",
            base_run_id=run_id,
            appid="a",
            window=TimeWindow(start_ns=requests[1].time_ns, end_ns=requests[1].time_ns + 1),
        )
    )
    selected = list(source.iter_requests())
    result = evaluate_plan(source, plan_for(source, selected[0], "short"), tmp_path / "sub")
    assert result.status == "available", result
    assert result.before.n == 2
    assert result.before.h < sum(r.baseline_metrics.h for r in selected)
    assert result.after.p < result.before.p


@pytest.mark.parametrize("failure", ["cancel", "source_changed"])
def test_final_request_boundary_cannot_publish_after(service, tmp_path, monkeypatch, failure):
    from test_diagnostic_tasks import options

    from tokenscope.analysis_common.encoding import EncodingContext
    from tokenscope.analysis_common.runtime import TaskControl

    run_id = prepare(service)
    source = SourceResolver(service).resolve_scope(
        SourceSelection(source_kind="base", base_run_id=run_id, appid="a")
    )
    requests = list(source.iter_requests())
    last = requests[-1]
    cancelled = False
    original = EncodingContext.encode

    def encode(context, request, raw):
        nonlocal cancelled
        result = original(context, request, raw)
        if request.request_key == last.request_key and raw != request.raw_body:
            if failure == "cancel":
                cancelled = True
            else:
                manifest = source.directory / "manifest.json"
                manifest.write_bytes(manifest.read_bytes() + b" ")
        return result

    monkeypatch.setattr(EncodingContext, "encode", encode)
    result = evaluate_plan(
        source,
        plan_for(source, last, "short"),
        tmp_path / "last",
        control=TaskControl(options(), lambda: cancelled),
    )
    assert result.status == ("interrupted" if failure == "cancel" else "blocked")
    assert result.after is None and not result.display_eligible

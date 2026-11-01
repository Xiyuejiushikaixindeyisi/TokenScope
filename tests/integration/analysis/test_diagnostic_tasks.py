import json

import pytest
from conftest import csv_bytes, valid_row

from tokenscope.analysis_common.contracts import (
    DiagnosticRequest,
    DiagnosticSelection,
    SourceSelection,
)
from tokenscope.analysis_common.plugins import BudgetSpec, PluginRegistry, PluginSelection
from tokenscope.analysis_common.runtime import RuntimeOptions
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.domain import RunSubmission
from tokenscope.errors import TokenScopeError
from tokenscope.token_content.plugin import TokenContentPlugin


def options(**overrides):
    values = dict(
        token_selection=PluginSelection(
            rule_ids=("T1", "T2", "T3", "T4"),
            budget=BudgetSpec(
                max_request_bytes=1048576,
                max_units=10000,
                max_comparison_bytes=1000000,
                max_depth=64,
                max_candidates=1000,
                max_encoding_calls=100,
            ),
        ),
        candidate_limit=2,
        pilot_limit=3,
        max_source_requests=100,
        max_source_bytes=10000000,
        max_findings=1000,
        max_experiments=8,
        max_combinations=2,
        max_encoding_calls=100,
    )
    values.update(overrides)
    return RuntimeOptions(**values)


def setup(service, low_hit=False, registry=None):
    rows = []
    for i in range(6):
        raw = json.dumps(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": f"time 2026-10-31 09:00:0{i}\n" + "stable " * 300,
                    },
                    {"role": "user", "content": "question"},
                ],
                "enable_thinking": False,
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "f",
                            "description": "static description",
                            "parameters": {"type": "object", "properties": {}},
                        },
                    }
                ],
            }
        )
        rows.append(
            valid_row(
                appid="a", request_input=raw, model_handle_start_time=f"2026-10-27T00:00:0{i}Z"
            )
        )
    (service.inputs.root / "tasks.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="tasks.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    if registry is None:
        registry = PluginRegistry()
        registry.register(TokenContentPlugin())
    diagnostics = DiagnosticService(SourceResolver(service), registry)
    request = DiagnosticRequest(
        source=SourceSelection(source_kind="base", base_run_id=run.run_id, appid="a"),
        selection=DiagnosticSelection(
            reason_codes=("low_hit",) if low_hit else ("request_length",),
            enable_low_hit=low_hit,
            enable_token_content=True,
        ),
        submission_key="one",
    )
    return diagnostics, request


def test_real_order_sealing_idempotency_retry_and_readonly(service):
    diagnostics, request = setup(service, True)
    receipt = diagnostics.submit(request, options())
    assert diagnostics.submit(request, options()) == receipt
    with pytest.raises(TokenScopeError, match="intent"):
        diagnostics.submit(request, options(candidate_limit=3))
    result = diagnostics.process_next()
    assert result.status in ("ready", "partial"), result
    report = diagnostics.report(receipt.task_id)
    assert [s["direction"] for s in report["stages"]] == ["low_hit", "token_content"]
    assert report["stages"][1]["status"] == "completed"
    fragments = diagnostics.items(receipt.task_id, "fragment")
    assert len(fragments) == 6
    assert diagnostics.items(receipt.task_id, "optimization")
    findings = diagnostics.items(receipt.task_id, "finding")
    pair = diagnostics.comparison(receipt.task_id, findings[0]["id"])
    assert len(json.loads(pair["left_raw_body"])["messages"]) == 2
    # GETs have no queued work and original source survives unchanged.
    assert diagnostics.process_next() is None
    retry = diagnostics.retry(receipt.task_id, "retry")
    assert retry.task_id != receipt.task_id and retry.attempt == 2
    diagnostics.cancel(retry.task_id)
    assert diagnostics.receipt(retry.task_id).status == "interrupted"
    directory = diagnostics.store.result_directory(receipt.task_id)
    (directory / "report.json").write_text("{}")
    with pytest.raises(TokenScopeError, match="differs"):
        diagnostics.report(receipt.task_id)


def test_missing_plugin_restart_and_shared_lock(service):
    diagnostics, request = setup(service, registry=PluginRegistry())
    task = diagnostics.submit(request, options())
    import fcntl

    with (service.state_root / "worker.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert diagnostics.process_next() is None
    result = diagnostics.process_next()
    assert result.status == "partial"
    assert diagnostics.report(task.task_id)["stages"][0]["reason"] == "PLUGIN_UNAVAILABLE"
    retry = diagnostics.retry(task.task_id, "restart")
    diagnostics.store.update(retry.task_id, status="running")
    assert diagnostics.process_next() is None
    assert diagnostics.receipt(retry.task_id).error_code == "WORKER_RESTARTED"


def test_budget_failure_no_published_gain(service):
    diagnostics, request = setup(service)
    task = diagnostics.submit(request, options(max_source_requests=5))
    assert diagnostics.process_next().error_code == "SOURCE_REQUEST_BUDGET_EXHAUSTED"
    with pytest.raises(TokenScopeError, match="published"):
        diagnostics.report(task.task_id)


def test_local_failure_continues_token_but_cancel_stops_between_stages(service, monkeypatch):
    diagnostics, request = setup(service, True)

    def fail(*args, **kwargs):
        raise RuntimeError("private body must not escape")

    monkeypatch.setattr(diagnostics, "_low_hit", fail)
    task = diagnostics.submit(request, options())
    assert diagnostics.process_next().status == "partial"
    stages = diagnostics.report(task.task_id)["stages"]
    assert stages[0]["reason"] == "LOW_HIT_FAILED"
    assert stages[1]["status"] == "completed"
    retry = diagnostics.retry(task.task_id, "cancel-at-boundary")

    def cancel(*args, **kwargs):
        diagnostics.cancel(retry.task_id)
        return {"direction": "low_hit", "status": "completed"}

    monkeypatch.setattr(diagnostics, "_low_hit", cancel)
    plugin = diagnostics.registry.get("token_content")

    def forbidden(*args):
        pytest.fail("Token must not run after cancellation")

    monkeypatch.setattr(plugin, "analyze_request", forbidden)
    assert diagnostics.process_next().status == "interrupted"
    assert diagnostics.receipt(retry.task_id).report_ref is None


def test_full_plan_budget_keeps_pilot_scope_and_metrics(service, tmp_path):
    from tokenscope.prefix_analysis.detection import collect_dynamics
    from tokenscope.prefix_analysis.experiments import compile_combination, pilot_scope

    diagnostics, request = setup(service, True)
    source = diagnostics.resolver.resolve_scope(request.source)
    found = collect_dynamics(source, tmp_path / "preview", candidate_limit=2)
    finding = next(f for f in found.findings if f.recipe_json)
    small = pilot_scope(source, finding, 3)
    pilot_plan = compile_combination(small, (finding,))
    full_plan = compile_combination(source, (finding,))
    from tokenscope.analysis_common.plugins import ExecutionStopped
    from tokenscope.analysis_common.runtime import TaskControl

    exact_size = len(pilot_plan.model_dump_json().encode())
    assert (
        compile_combination(
            small, (finding,), TaskControl(options(max_plan_bytes=exact_size), lambda: False)
        )
        == pilot_plan
    )
    with pytest.raises(ExecutionStopped, match="PLAN_BYTES"):
        compile_combination(
            small, (finding,), TaskControl(options(max_plan_bytes=exact_size - 1), lambda: False)
        )
    pilot_bytes = sum(len(o.model_dump_json().encode()) for o in pilot_plan.operations)
    full_bytes = sum(len(o.model_dump_json().encode()) for o in full_plan.operations)
    task = diagnostics.submit(request, options(max_plan_bytes=(pilot_bytes + full_bytes) // 2))
    assert diagnostics.process_next().status == "partial"
    experiment = diagnostics.items(task.task_id, "experiment")[0]["data"]
    assert experiment["status"] == "full_not_run"
    assert experiment["pilot_scope"]["request_count"] == "3"
    assert experiment["pilot_scope"]["request_keys_digest"] == small.scope.request_keys_digest
    assert experiment["confidence_basis"] == "pilot_gain_gt_1pp"
    assert experiment["reason_codes"] == ["PLAN_BYTES_EXHAUSTED"]
    evaluations = diagnostics.items(task.task_id, "evaluation")
    assert (
        evaluations[0]["data"]["stage"] == "pilot" and evaluations[0]["data"]["after"] is not None
    )
    assert not diagnostics.items(task.task_id, "optimization")
    assert diagnostics.report(task.task_id)["stages"][1]["checked_requests"] == "6"


def test_workspace_creation_failure_is_terminal(service, monkeypatch):
    from pathlib import Path

    diagnostics, request = setup(service)
    task = diagnostics.submit(request, options())
    original = Path.mkdir

    def fail_working(path, *args, **kwargs):
        if ".working-" in path.name:
            raise OSError("injected disk failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", fail_working)
    assert diagnostics.process_next().status == "failed"
    assert diagnostics.receipt(task.task_id).report_ref is None


@pytest.mark.parametrize("kind", ["dynamic", "tool_order"])
def test_discovery_budget_before_second_request_preserves_count(
    service, tmp_path, monkeypatch, kind
):
    from tokenscope.analysis_common.plugins import ExecutionStopped
    from tokenscope.analysis_common.runtime import TaskControl
    from tokenscope.prefix_analysis.detection import collect_dynamics
    from tokenscope.prefix_analysis.service import collect_l2

    diagnostics, request = setup(service, True)
    source = diagnostics.resolver.resolve_scope(request.source)
    control = TaskControl(options(), lambda: False)
    calls = 0

    def stop_second(request):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ExecutionStopped("REQUEST_BYTES_EXHAUSTED")

    monkeypatch.setattr(control, "request", stop_second)
    collector = collect_dynamics if kind == "dynamic" else collect_l2
    report = collector(source, tmp_path / kind, candidate_limit=2, control=control)
    assert report.checked_requests == 1
    assert report.candidate_coverage_partial is True
    assert "REQUEST_BYTES_EXHAUSTED" in report.reason_codes

from types import SimpleNamespace

import pytest

from tokenscope.analysis_common.plugins import BudgetSpec, ExecutionStopped, PluginSelection
from tokenscope.analysis_common.runtime import RuntimeOptions, TaskControl
from tokenscope.analysis_common.service import DiagnosticService


def config(**overrides):
    values = dict(
        token_selection=PluginSelection(
            rule_ids=("T1",),
            budget=BudgetSpec(
                max_request_bytes=64,
                max_comparison_bytes=64,
                max_units=10,
                max_depth=3,
                max_candidates=10,
                max_encoding_calls=2,
            ),
        ),
        candidate_limit=2,
        pilot_limit=2,
        max_source_requests=3,
        max_source_bytes=100,
        max_findings=2,
        max_experiments=2,
        max_combinations=1,
        max_encoding_calls=2,
        max_plan_bytes=64,
    )
    values.update(overrides)
    return RuntimeOptions(**values)


@pytest.mark.parametrize("amount", [63, 64, 65])
@pytest.mark.parametrize("kind", ["plan", "request", "comparison"])
def test_byte_limits_equal_is_allowed(amount, kind):
    control = TaskControl(config(), lambda: False)

    def action():
        if kind == "plan":
            control.plan(amount)
        elif kind == "request":
            control.request(SimpleNamespace(raw_body="x" * amount))
        else:
            control.comparison(
                SimpleNamespace(raw_body="x"), SimpleNamespace(raw_body="x" * (amount - 1))
            )

    if amount > 64:
        with pytest.raises(ExecutionStopped):
            action()
    else:
        action()


@pytest.mark.parametrize("method", ["encode", "finding"])
def test_count_limits_and_cancel(method):
    control = TaskControl(config(), lambda: False)
    getattr(control, method)()
    getattr(control, method)()
    with pytest.raises(ExecutionStopped):
        getattr(control, method)()
    control.cancelled = lambda: True
    with pytest.raises(ExecutionStopped, match="INTERRUPTED"):
        control.checkpoint()


@pytest.mark.parametrize("count", [2, 3, 4])
def test_source_count_boundary(count):
    source = SimpleNamespace(scope=SimpleNamespace(request_count=count), _rows=lambda: iter([]))
    control = TaskControl(config(), lambda: False)
    if count > 3:
        with pytest.raises(ExecutionStopped, match="SOURCE_REQUEST"):
            DiagnosticService._preflight(source, control)
    else:
        DiagnosticService._preflight(source, control)


@pytest.mark.parametrize("depth", [2, 3, 4])
def test_source_depth_boundary_ignores_quoted_braces(depth):
    raw = "[" * depth + '"escaped \\" {["' + "]" * depth
    source = SimpleNamespace(
        scope=SimpleNamespace(request_count=1), _rows=lambda: iter([{"request_input": raw}])
    )
    control = TaskControl(config(), lambda: False)
    if depth > 3:
        with pytest.raises(ExecutionStopped, match="DEPTH"):
            DiagnosticService._preflight(source, control)
    else:
        DiagnosticService._preflight(source, control)


@pytest.mark.parametrize("size", [99, 100, 101])
def test_total_source_bytes_boundary(size):
    rows = [{"request_input": " " * 50}, {"request_input": " " * (size - 50)}]
    source = SimpleNamespace(scope=SimpleNamespace(request_count=2), _rows=lambda: iter(rows))
    control = TaskControl(config(), lambda: False)
    if size > 100:
        with pytest.raises(ExecutionStopped, match="SOURCE_BYTES"):
            DiagnosticService._preflight(source, control)
    else:
        DiagnosticService._preflight(source, control)

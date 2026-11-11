from types import SimpleNamespace

import pytest

from tokenscope.analysis_common.evaluation_v3 import (
    WindowEvaluation3,
    evaluate_window,
    improvement,
    stopped_status,
)
from tokenscope.analysis_common.execution_v3 import automatic_profile
from tokenscope.analysis_common.runtime_v3 import BudgetLedger, TaskStopped
from tokenscope.analysis_common.wire_v3 import from_wire, to_wire
from tokenscope.prefix_analysis.clock_discovery_v3 import ClockFinding3, ClockPlanResult
from tokenscope.prefix_analysis.prefix_findings_v3 import PrefixFinding3, PrefixRecipe3
from tokenscope.prefix_analysis.session_clock_v3 import ClockRecipe3


@pytest.mark.parametrize(
    "before,after,expected", [(1, 2, "positive"), (2, 2, "zero"), (3, 2, "negative")]
)
def test_exact_signed_rates_and_wire(before, after, expected):
    b, a = dict(p=7, h=before, c=7 - before), dict(p=7, h=after, c=7 - after)
    pp = improvement(b, a)
    result = WindowEvaluation3(
        role="discovery",
        status=expected,
        transformation_digest="x",
        complete=True,
        n=2,
        before=b,
        after=a,
        improvement_pp=pp,
    )
    assert from_wire(WindowEvaluation3, to_wire(result)) == result
    assert (
        pp.numerator == (after - before) * 100 and pp.denominator == 7
        if before != after
        else pp.numerator == 0
    )
    with pytest.raises(ValueError, match="Incomplete"):
        WindowEvaluation3.model_validate(result.model_dump() | {"complete": False})


def test_zero_denominator_and_invalid_conservation():
    assert improvement(dict(p=0, h=0), dict(p=10, h=1)) is None
    with pytest.raises(ValueError, match="conserved"):
        WindowEvaluation3(
            role="review",
            status="zero",
            transformation_digest="x",
            complete=True,
            n=1,
            before=dict(p=4, h=1, c=4),
            after=dict(p=4, h=1, c=3),
        )


@pytest.mark.parametrize(
    "code,status",
    [
        ("USER_CANCELLED", "cancelled"),
        ("BUDGET_EXHAUSTED:encoding_calls", "budget_exhausted"),
        ("BASELINE_MISMATCH", "failed"),
        ("MEMORY_PRESSURE", "budget_exhausted"),
        ("DEADLINE_EXHAUSTED", "budget_exhausted"),
    ],
)
@pytest.mark.parametrize("finding_class", [ClockFinding3, PrefixFinding3])
def test_failure_has_no_complete_after(tmp_path, monkeypatch, code, status, finding_class):
    from tokenscope.analysis_common import evaluation_v3

    def stop(*args):
        raise TaskStopped(code)

    monkeypatch.setattr(
        evaluation_v3,
        "compile_clock_plan" if finding_class is ClockFinding3 else "compile_prefix_plan",
        stop,
    )
    recipe = ClockRecipe3(logical_field="x", field_shape=("", ""), block_indices=(0,))
    if finding_class is PrefixFinding3:
        recipe = PrefixRecipe3(kind="sort_tools", set_digest="test")
    source = SimpleNamespace(role="review")
    control = BudgetLedger(
        automatic_profile(available_bytes=4 * 1024**3, source_bytes=1000000, cpu_budget=1),
        lambda: False,
    )
    result = evaluate_window(
        source, finding_class.model_construct(recipe=recipe), tmp_path / "new", control
    )
    assert result.status == stopped_status(code) == status
    assert not result.complete and result.after is None and result.improvement_pp is None
    assert from_wire(WindowEvaluation3, to_wire(result)) == result


@pytest.mark.parametrize("matched,status", [((), "no_targets"), (("request",), "no_op")])
@pytest.mark.parametrize("finding_class", [ClockFinding3, PrefixFinding3])
def test_inapplicable_and_noop_distinct(tmp_path, monkeypatch, matched, status, finding_class):
    from tokenscope.analysis_common import evaluation_v3

    monkeypatch.setattr(
        evaluation_v3,
        "compile_clock_plan" if finding_class is ClockFinding3 else "compile_prefix_plan",
        lambda *args: ClockPlanResult(None, matched, ()),
    )
    recipe = ClockRecipe3(logical_field="x", field_shape=("", ""), block_indices=(0,))
    if finding_class is PrefixFinding3:
        recipe = PrefixRecipe3(kind="sort_tools", set_digest="test")
    result = evaluate_window(
        SimpleNamespace(role="review"),
        finding_class.model_construct(recipe=recipe),
        tmp_path / "new",
        None,
    )
    assert result.status == status and result.after is None

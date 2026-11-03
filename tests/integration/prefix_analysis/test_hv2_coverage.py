"""Real user_v2 source and v2 controls for private L1-L5 coverage boundaries."""

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.runtime_control import TaskControl
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.prefix_analysis.detection import collect_dynamics
from tokenscope.prefix_analysis.service import collect_l2

spec = importlib.util.spec_from_file_location(
    "hv2_profile", Path(__file__).resolve().parents[3] / "docs/tasks/prefix-analysis/hv2_profile.py"
)
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


@pytest.fixture(scope="module")
def sources(tmp_path_factory):
    result = {}
    for case in ["mixed", "order", "set", "messages"]:
        service, user, selection = profile.prepare(tmp_path_factory.mktemp(case), case, 8)
        result[case] = (
            SourceResolver(service, user).resolve_scope(selection),
            service,
            user,
            selection,
        )
    return result


def collect(fn, source, path, control):
    control.lane = "l2" if fn is collect_l2 else "dynamics"
    return fn(
        source,
        path,
        candidate_limit=control.options.candidate_limit,
        control=control,
        **({"include_history": True} if fn is collect_dynamics else {}),
    )


@pytest.mark.parametrize("fn", [collect_l2, collect_dynamics])
def test_candidate_truncation_and_comparison_stop_both_preserved(sources, tmp_path, fn):
    control = TaskControl(profile.options(1, max_comparisons=3), lambda: False)
    report = collect(fn, sources["order"][0], tmp_path / "scan", control)
    assert report.candidate_comparisons == 3
    assert report.checked_requests < 8 and report.candidate_coverage_partial
    assert set(report.reason_codes) == {
        "CANDIDATE_LOOKUP_TRUNCATED",
        "COMPARISON_COUNT_BUDGET_EXHAUSTED",
    }


def test_dense_l4_reservations_keep_all_rules_and_honest_evidence(sources, tmp_path):
    control = TaskControl(profile.options(16, max_findings=5), lambda: False)
    findings = []
    for name, fn in [("l2", collect_l2), ("dynamics", collect_dynamics)]:
        report = collect(fn, sources["mixed"][0], tmp_path / name, control)
        assert report.checked_requests == 8 and not report.candidate_coverage_partial
        findings.extend(report.findings)
    assert control.detected["L4"] > control.detected["L1"] > 1
    assert control.retained == {r: 1 for r in ("L1", "L2", "L3", "L4", "L5")}
    assert not control.retention_complete and len(findings) == 5
    for f in findings:
        if f.rule_id == "L4":
            assert f.evidence_status == "needs_association" and f.recipe_json is None
        if f.rule_id == "L5":
            assert f.recipe_json is None
        if f.rule_id in ("L1", "L2"):
            assert f.recipe_json


@pytest.mark.parametrize("fn", [collect_l2, collect_dynamics])
def test_byte_retention_limit_keeps_full_scan(sources, tmp_path, fn):
    control = TaskControl(profile.options(16, max_retained_bytes=5), lambda: False)
    report = collect(fn, sources["mixed"][0], tmp_path / "scan", control)
    assert report.checked_requests == 8 and not report.candidate_coverage_partial
    assert report.findings == () and not control.retention_complete
    assert sum(control.retained_bytes.values()) == 0


@pytest.mark.parametrize("fn", [collect_l2, collect_dynamics])
def test_comparison_bytes_and_cancel(sources, tmp_path, fn):
    opts = profile.options(16)
    opts = opts.model_copy(
        update={
            "token_selection": opts.token_selection.model_copy(
                update={
                    "budget": opts.token_selection.budget.model_copy(
                        update={"max_comparison_bytes": 1}
                    )
                }
            )
        }
    )
    report = collect(fn, sources["mixed"][0], tmp_path / "bytes", TaskControl(opts, lambda: False))
    assert report.reason_codes == ("COMPARISON_BYTES_EXHAUSTED",)
    assert report.candidate_comparisons == 0 and report.checked_requests == 1
    with pytest.raises(ExecutionStopped, match="ANALYSIS_INTERRUPTED"):
        collect(fn, sources["mixed"][0], tmp_path / "cancel", TaskControl(opts, lambda: True))


def test_set_change_is_not_order_and_stable_messages_negative(sources, tmp_path):
    for case in ["set", "messages"]:
        c = TaskControl(profile.options(16), lambda: False)
        l2 = collect(collect_l2, sources[case][0], tmp_path / (case + "-l2"), c)
        dyn = collect(collect_dynamics, sources[case][0], tmp_path / (case + "-dyn"), c)
        assert l2.findings == ()
        if case == "set":
            assert {f.rule_id for f in dyn.findings} == {"L3"}
            assert all(f.recipe_json is None for f in dyn.findings)
        else:
            assert dyn.findings == () and not c.detected


@pytest.mark.parametrize("encoding_limit", [1, 512])
def test_actual_public_runtime_low_only_user_source(sources, encoding_limit):
    from tokenscope.analysis_common.bootstrap import build_diagnostics
    from tokenscope.analysis_common.execution_v2 import RequestV2, SelectionV2

    _, base, user, selection = sources["mixed"]
    d = build_diagnostics(base, user)
    req = RequestV2(
        source=selection,
        selection=SelectionV2(
            reason_codes=("low_hit",), enable_low_hit=True, enable_token_content=False
        ),
        submission_key=f"r2-low-only-{encoding_limit}",
    )
    with (
        patch.object(d.registry, "get", side_effect=AssertionError("disabled Token")),
        patch.object(
            d.recommendations.registry, "get", side_effect=AssertionError("disabled adapter")
        ),
    ):
        receipt = d.submit(
            req,
            profile.options(
                16, max_findings=5, max_encoding_calls=encoding_limit, max_experiments=1
            ),
        )
        assert d.process_next().status == "partial"
    report = d.report(receipt.task_id)
    stage = report["stages"][0]
    assert report["selected_directions"] == ["low_hit"]
    assert stage["scan_complete"] and stage["comparison_complete"]
    assert (
        not stage["retention_complete"] and "FINDING_RETENTION_TRUNCATED" in stage["reason_codes"]
    )
    assert int(report["encoding_calls"]) <= encoding_limit
    experiments = d.items(receipt.task_id, "experiment")
    if encoding_limit == 1:
        assert any(
            "ENCODING_BUDGET_EXHAUSTED" in x["data"].get("reason_codes", []) for x in experiments
        )
        assert all(
            x["data"].get("reason") == "ENCODING_BUDGET_EXHAUSTED"
            for x in experiments
            if x["data"]["status"] == "not_run"
        )
    else:
        assert any(x["data"].get("reason") == "EXPERIMENT_BUDGET_EXHAUSTED" for x in experiments)
    assert d.items(receipt.task_id, "fragment") == []


@pytest.mark.parametrize(
    "budget,code",
    [
        ("max_source_requests", "SOURCE_REQUEST_BUDGET_EXHAUSTED"),
        ("max_source_bytes", "SOURCE_BYTES_EXHAUSTED"),
    ],
)
def test_preflight_hard_source_limits(sources, budget, code):
    from tokenscope.analysis_common.bootstrap import build_diagnostics
    from tokenscope.analysis_common.execution_v2 import RequestV2, SelectionV2

    _, base, user, selection = sources["messages"]
    d = build_diagnostics(base, user)
    req = RequestV2(
        source=selection,
        selection=SelectionV2(
            reason_codes=("low_hit",), enable_low_hit=True, enable_token_content=False
        ),
        submission_key=budget,
    )
    receipt = d.submit(req, profile.options(16, **{budget: 1}))
    assert d.process_next().status == "failed"
    assert d.store.row(receipt.task_id)["error"] == code

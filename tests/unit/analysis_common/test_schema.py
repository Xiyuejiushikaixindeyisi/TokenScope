import hashlib

import pytest
from pydantic import ValidationError

from tokenscope.analysis_common.contracts import (
    AggregateMetrics,
    AnalysisFragment,
    ContentUnit,
    Coverage,
    EmbeddedLocation,
    EvaluationResult,
    Location,
    Participation,
    RequestKey,
    SourceSelection,
    TargetLocation,
    canonical_metadata,
)
from tokenscope.analysis_common.plugins import BudgetSpec, ExecutionStopped, RunControl
from tokenscope.analysis_common.wire import from_wire, to_wire, wire_schema

KEY = RequestKey(base_run_id="r", source_record_index=10**20)
SHA = "a" * 64


def test_wire_decimal_roundtrip_and_schema() -> None:
    wire = to_wire(KEY)
    assert wire["source_record_index"] == "100000000000000000000"
    assert from_wire(RequestKey, wire) == KEY
    assert wire_schema(RequestKey)["properties"]["source_record_index"]["type"] == "string"
    for bad in [1, True, "01", "+1", "-0", "1.0"]:
        with pytest.raises(ValueError):
            from_wire(RequestKey, {"base_run_id": "r", "source_record_index": bad})


def test_fixed_metadata_encoding() -> None:
    assert canonical_metadata({"中": 12, "a": True}) == b'{"a":true,"\xe4\xb8\xad":"12"}'
    assert hashlib.sha256(canonical_metadata({})).hexdigest() == (
        "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
    )


def test_location_and_unit_facets_do_not_change_identity() -> None:
    loc = Location(request_key=KEY, raw_sha256=SHA, source_pointer="/messages/3/content")
    fields = dict(
        location_id=loc.location_id,
        representation="utf8",
        measurement_version="1",
        content_sha256=SHA,
        measurement_unit="bytes",
        measured_value=9,
    )
    t2 = ContentUnit(**fields, facets=("tool_result",))
    t4 = ContentUnit(**fields, facets=("historical_result",))
    assert t2.unit_id == t4.unit_id
    with pytest.raises(ValidationError):
        Location(request_key=KEY, raw_sha256=SHA, source_pointer="/bad~2")


def test_embedded_requires_outer_guard() -> None:
    loc = Location(
        request_key=KEY,
        raw_sha256=SHA,
        source_pointer="/arguments",
        embedded=EmbeddedLocation(parser_version="exact-1", pointer=""),
    )
    with pytest.raises(ValidationError):
        TargetLocation(location=loc, original_type="string", value_guard=SHA)
    target = TargetLocation(
        location=loc, original_type="string", value_guard=SHA, outer_string_guard=SHA
    )
    assert from_wire(TargetLocation, to_wire(target)) == target


def test_invalid_scope_selection_and_exact_spans() -> None:
    with pytest.raises(ValidationError):
        SourceSelection(source_kind="base", appid="a", base_run_id="r", user_run_id="u")
    with pytest.raises(ValidationError):
        Participation(status="included")
    with pytest.raises(ValidationError):
        Participation(prompt_token_spans=())


def test_fragment_rejects_foreign_location() -> None:
    loc = Location(
        request_key=RequestKey(base_run_id="other", source_record_index=1),
        raw_sha256=SHA,
        source_pointer="",
    )
    with pytest.raises(ValidationError):
        AnalysisFragment(
            request_key=KEY,
            raw_sha256=SHA,
            plugin_id="token_content",
            plugin_version="1",
            locations=(loc,),
            coverage=Coverage(checked=1, eligible=1, complete=True),
        )


def test_token_results_have_no_low_hit_gate() -> None:
    before = AggregateMetrics(n=2, j=100, p=100, h=60, c=40)
    after = AggregateMetrics(n=2, j=90, p=100, h=80, c=20)
    values = dict(
        evaluation_id="e",
        plan_id="p",
        scope_id="s",
        stage="full",
        direction="token_content",
        status="available",
        baseline_origin="selected_window_recomputed",
        coverage=Coverage(checked=2, eligible=2, complete=True),
        before=before,
        after=after,
    )
    result = EvaluationResult(**values)
    assert result.gate_passed is None
    assert not result.display_eligible
    with pytest.raises(ValidationError):
        EvaluationResult(**{**values, "status": "failed"})
    with pytest.raises(ValidationError):
        EvaluationResult(**{**values, "after": AggregateMetrics(n=1, j=90, p=100, h=80, c=20)})


def test_budget_exact_limit_and_interrupt() -> None:
    budget = BudgetSpec(
        max_request_bytes=10,
        max_units=2,
        max_comparison_bytes=10,
        max_depth=2,
        max_candidates=2,
        max_encoding_calls=2,
    )
    control = RunControl(budget)
    control.consume("max_units", 2)
    with pytest.raises(ExecutionStopped, match="BUDGET"):
        control.consume("max_units", 1)
    with pytest.raises(ValueError):
        control.consume("max_units", -1)
    with pytest.raises(ExecutionStopped, match="INTERRUPTED"):
        RunControl(budget, cancelled=lambda: True).checkpoint()

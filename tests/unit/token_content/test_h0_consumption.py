"""Consumer acceptance for analysis-common-1.0; no runtime integration claim."""

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tokenscope.analysis_common import contracts as c
from tokenscope.analysis_common import plugins as p
from tokenscope.analysis_common.wire import from_wire, to_wire, wire_schema

ROOT = Path(__file__).resolve().parents[3]


def request():
    raw = '{"messages":[{"role":"user","content":"中文"}]}'
    return c.RequestView(
        request_key=c.RequestKey(base_run_id="run", source_record_index=10**20),
        scope_id="scope:fixture",
        appid="app",
        time_ns=7,
        hash_id="display-only",
        raw_body=raw,
        raw_sha256=hashlib.sha256(raw.encode()).hexdigest(),
        raw_body_complete=True,
        baseline_metrics=c.BaselineMetrics(j=20, p=10),
        encoder_identity="encoder",
        asset_identity="asset",
        effective_options_json='{"n":1}',
    )


def test_frozen_manifest_and_schemas_match_consumed_types():
    folder = ROOT / "docs/contracts/analysis-common-1.0"
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["version"] == c.CONTRACT_VERSION == "analysis-common-1.0"
    for entry in manifest["files"]:
        assert hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
    internal = json.loads((folder / "internal.json").read_text())["models"]
    wire = json.loads((folder / "wire.json").read_text())["models"]
    for name, schema in internal.items():
        model = getattr(c, name, None) or getattr(p, name)
        assert model.model_json_schema() == schema
        assert wire_schema(model) == wire[name]


def test_full_request_wire_preserves_embedded_numbers_and_unknown_capture():
    original = request()
    payload = to_wire(original)
    assert payload["request_key"]["source_record_index"] == "100000000000000000000"
    assert payload["effective_options_json"] == '{"n":1}'
    assert payload["raw_body_complete"] is True
    assert from_wire(c.RequestView, payload) == original
    assert original.capture_truncation == "unknown"
    assert original.baseline_metrics.h is None


@pytest.mark.parametrize("value", ["01", "+1", "-0", "1.0", 1, True, "-1"])
def test_bad_request_key_wire_rejected(value):
    with pytest.raises((ValueError, ValidationError)):
        from_wire(c.RequestKey, {"base_run_id": "r", "source_record_index": value})


def test_locations_units_and_rule_observations_have_separate_identities():
    view = request()
    loc = c.Location(
        request_key=view.request_key,
        raw_sha256=view.raw_sha256,
        source_pointer="/messages/0/content",
    )
    embedded = loc.model_copy(
        update={"embedded": c.EmbeddedLocation(parser_version="json-exact-1", pointer="")}
    )
    assert loc.location_id != embedded.location_id
    unit = c.ContentUnit(
        location_id=loc.location_id,
        representation="text",
        measurement_version="1",
        content_sha256="a" * 64,
        measurement_unit="utf8_bytes",
        measured_value=6,
        facets=("tool_result",),
    )
    assert unit.unit_id == unit.model_copy(update={"facets": ("history",)}).unit_id
    obs = c.Observation(
        rule_id="T2",
        rule_version="1",
        unit_ids=(unit.unit_id,),
        predicate="burden",
        method="exact",
        condition="unknown",
    )
    assert obs.observation_id != obs.model_copy(update={"rule_id": "T4"}).observation_id
    fragment = c.AnalysisFragment(
        request_key=view.request_key,
        raw_sha256=view.raw_sha256,
        plugin_id="token_content",
        plugin_version="1",
        locations=(loc,),
        units=(unit,),
        observations=(obs,),
        coverage=c.Coverage(checked=1, eligible=1, complete=True),
    )
    assert from_wire(c.AnalysisFragment, to_wire(fragment)) == fragment
    with pytest.raises(ValidationError):
        c.AnalysisFragment(**{**fragment.model_dump(), "locations": ()})


def test_embedded_mutation_is_outer_string_replacement_and_atomic_preparation():
    view = request()
    loc = c.Location(
        request_key=view.request_key,
        raw_sha256=view.raw_sha256,
        source_pointer="/messages/0/content",
    )
    replacement = json.dumps('{"document_ref":"doc://real"}')
    operation = c.PreparedMutation(
        operation_id="op",
        handler_id="token_content.replace",
        handler_version="1",
        target=c.TargetLocation(
            location=loc, original_type="string", value_guard="a" * 64, outer_string_guard="b" * 64
        ),
        public_primitive="replace_value",
        replacement_json=replacement,
        source_operations_json='[{"pointer":"/document"}]',
    )
    result = p.MutationPreparation(status="prepared", operations=(operation,))
    assert from_wire(p.MutationPreparation, to_wire(result)) == result
    assert json.loads(operation.replacement_json) == '{"document_ref":"doc://real"}'
    with pytest.raises(ValidationError):
        p.MutationPreparation(status="blocked", operations=(operation,))


@pytest.mark.parametrize("after_h", [0, 10, 11, 12])
def test_token_direct_full_has_no_low_hit_gate(after_h):
    metrics = c.AggregateMetrics(n=1, j=120, p=100, h=10, c=90)
    result = c.EvaluationResult(
        evaluation_id="e",
        plan_id="p",
        scope_id="s",
        stage="direct_full",
        direction="token_content",
        status="available",
        baseline_origin="selected_window_recomputed",
        coverage=c.Coverage(checked=1, eligible=1, complete=True),
        before=metrics,
        after=c.AggregateMetrics(n=1, j=120, p=100, h=after_h, c=100 - after_h),
    )
    assert result.gate_passed is None
    # This property is specifically low-hit card eligibility, NOT Token visibility.
    assert result.display_eligible is False
    assert from_wire(c.EvaluationResult, to_wire(result)) == result


def test_run_control_and_descriptor_version_boundary():
    budget = p.BudgetSpec(
        max_request_bytes=1000,
        max_units=2,
        max_comparison_bytes=100,
        max_depth=10,
        max_candidates=2,
        max_encoding_calls=1,
    )
    control = p.RunControl(budget)
    control.consume("max_units", 2)
    with pytest.raises(p.ExecutionStopped, match="ANALYSIS_BUDGET_EXHAUSTED"):
        control.consume("max_units", 1)
    cancelled = p.RunControl(budget, cancelled=lambda: True)
    with pytest.raises(p.ExecutionStopped, match="ANALYSIS_INTERRUPTED"):
        cancelled.checkpoint()
    with pytest.raises(ValidationError):
        p.PluginDescriptor(
            plugin_id="token_content",
            version="1",
            contract_version="unknown",
            parser_version="1",
            measurement_version="1",
            rule_versions=(),
            policy_schema_version="1",
            handlers=(),
        )

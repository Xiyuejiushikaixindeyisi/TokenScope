import pytest
from pydantic import ValidationError

from tokenscope.analysis_common.execution_v2 import RuntimeV2, SelectionV2
from tokenscope.analysis_common.plugins import BudgetSpec, ExecutionStopped, PluginSelection
from tokenscope.analysis_common.runtime_control import TaskControl


def limits(**kw):
    values = dict(
        token_selection=PluginSelection(
            rule_ids=("T2",),
            budget=BudgetSpec(
                max_request_bytes=100000,
                max_units=100,
                max_comparison_bytes=200000,
                max_depth=32,
                max_candidates=100,
                max_encoding_calls=10,
            ),
        ),
        candidate_limit=4,
        pilot_limit=2,
        max_source_requests=100,
        max_source_bytes=1000000,
        max_findings=10,
        max_experiments=2,
        max_combinations=0,
        max_encoding_calls=2,
        max_retained_bytes=1000,
        max_comparisons=2,
    )
    values.update(kw)
    return RuntimeV2(**values)


@pytest.mark.parametrize("low,token", [(True, False), (False, True), (True, True)])
def test_explicit_directions(low, token):
    s = SelectionV2(reason_codes=("low_hit",), enable_low_hit=low, enable_token_content=token)
    assert (s.enable_low_hit, s.enable_token_content) == (low, token)


def test_empty_selection_rejected():
    with pytest.raises(ValidationError):
        SelectionV2(reason_codes=("low_hit",), enable_low_hit=False, enable_token_content=False)


def test_rule_retention_does_not_stop_scanning_or_other_rules():
    c = TaskControl(limits(), lambda: False)
    for i in range(10000):
        assert c.retain("L4", 30) == (i < 2)
    assert c.retain("L1", 30) and c.retain("L5", 30)
    assert c.detected == {"L4": 10000, "L1": 1, "L5": 1}
    assert sum(c.retained.values()) == 4 and sum(c.retained_bytes.values()) == 120
    assert not c.retention_complete
    assert c.telemetry.counters["low_hit.L4.omitted"] == 9998
    assert len(c.detected) == 3
    assert not c.retain("L3", 201)  # fixed byte reservation, not only count


def test_cancellation_and_direction_budget_isolation():
    root = TaskControl(limits(), lambda: False)
    low = root.fork("low_hit")
    token = root.fork("token_content")
    low.encode()
    low.encode()
    with pytest.raises(ExecutionStopped, match="ENCODING"):
        low.encode()
    token.encode()
    assert token.encoding_calls == 1
    low.cancelled = lambda: True
    with pytest.raises(ExecutionStopped, match="INTERRUPTED"):
        low.retain("L1", 1)


def test_partial_fallback_ready_priority_snapshot_restart(tmp_path):
    from test_discovery import publish

    from tokenscope.analysis_common.discovery_v2 import DiscoveryV2 as Discovery
    from tokenscope.analysis_common.storage import DiagnosticStore

    store = DiagnosticStore(tmp_path)
    reader = Discovery(store, "i")
    partial = publish(store, "p", "partial")
    page = reader.catalog_v2(limit=1)
    assert not page["defaults"]
    assert {v["task_id"] for v in page["selected_reports"]} == {partial}
    assert all(
        v["selection_kind"] == "published_partial_fallback" for v in page["selected_reports"]
    )
    ready = publish(store, "r")
    publish(store, "p2", "partial")
    assert {v["task_id"] for v in reader.catalog_v2()["selected_reports"]} == {ready}
    assert reader.catalog_v2(page["snapshot"]) == page
    assert Discovery(DiagnosticStore(tmp_path), "i").catalog_v2() == reader.catalog_v2()
    with pytest.raises(Exception, match="changed"):
        Discovery(store, "different").catalog_v2(page["snapshot"])


def test_fallback_exclusions_directions_and_pages(tmp_path):
    from test_discovery import publish, source

    from tokenscope.analysis_common.discovery_v2 import DiscoveryV2
    from tokenscope.analysis_common.storage import DiagnosticStore

    store = DiagnosticStore(tmp_path)
    low_both = publish(store, "both", "partial")
    token = publish(store, "token", "partial", low=False)
    publish(store, "empty", "empty")
    publish(store, "evaluation", kind="token_authorization")
    failed = store.submit("failed", '{"kind":"analysis"}', source(), "{}")
    store.update(failed.task_id, status="failed", error="TEST")
    reader = DiscoveryV2(store, "i")
    first = reader.catalog_v2(limit=1)
    assert {v["direction"]: v["task_id"] for v in first["selected_reports"]} == {
        "low_hit": low_both,
        "token_content": token,
    }
    page = first
    ids = []
    while True:
        ids.extend(v["task_id"] for v in page["items"])
        if page["next_after"] is None:
            break
        page = reader.catalog_v2(first["snapshot"], page["next_after"], 1)
        assert page["selected_reports"] == first["selected_reports"]
    assert len(ids) == len(set(ids))
    assert failed.task_id not in ids
    with store.connect() as db:
        db.execute("DROP TRIGGER diagnostic_terminal_outbox")
        db.execute("DROP TABLE diagnostic_terminals")
        db.execute("DROP TABLE discovery_meta")
    migrated = DiscoveryV2(DiagnosticStore(tmp_path), "i")
    assert migrated.catalog_v2()["selected_reports"] == []


def test_response_schema_decimal_maps_reject_invalid_values():
    from tokenscope.analysis_common.execution_v2 import MetricsV2
    from tokenscope.analysis_common.wire import from_wire

    for value in ("-1", "01", "1.0", 1):
        with pytest.raises(ValueError):
            from_wire(
                MetricsV2,
                {
                    "version": "diagnostics-telemetry-2",
                    "clock": "perf_counter_ns",
                    "elapsed_ns": {"stage": value},
                    "counts": {},
                },
            )


def test_candidate_schema_and_actual_http_examples():
    import json
    from pathlib import Path

    from tokenscope.analysis_common.execution_v2 import CatalogV2, ExecutionViewV2, SubmissionV2
    from tokenscope.analysis_common.wire import from_wire, wire_schema

    root = Path(__file__).resolve().parents[3] / "docs/contracts/diagnostics-execution-2"
    schemas = json.loads((root / "wire.json").read_bytes())
    examples = json.loads((root / "examples.json").read_bytes())
    for name, model in (
        ("submission", SubmissionV2),
        ("catalog", CatalogV2),
        ("execution", ExecutionViewV2),
    ):
        assert schemas[name] == wire_schema(model)
        from_wire(model, examples[name])

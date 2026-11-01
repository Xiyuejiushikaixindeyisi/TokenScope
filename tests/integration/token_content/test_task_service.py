"""H3a consumer acceptance through real persistence, worker and encoding."""

import json

import pytest
from conftest import csv_bytes, valid_row

from tokenscope.analysis_common.contracts import (
    AnalysisFragment,
    DiagnosticRequest,
    DiagnosticSelection,
    EvaluationResult,
    SourceSelection,
)
from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.plugins import BudgetSpec, PluginRegistry, PluginSelection
from tokenscope.analysis_common.runtime import RuntimeOptions
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.analysis_common.wire import from_wire
from tokenscope.domain import RunSubmission
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.token_content.plugin import TokenContentPlugin


def options():
    return RuntimeOptions(
        token_selection=PluginSelection(
            rule_ids=("T1", "T2", "T3", "T4"),
            budget=BudgetSpec(
                max_request_bytes=1_000_000,
                max_units=10_000,
                max_comparison_bytes=1_000_000,
                max_depth=64,
                max_candidates=1000,
                max_encoding_calls=100,
            ),
        ),
        candidate_limit=2,
        pilot_limit=2,
        max_source_requests=100,
        max_source_bytes=10_000_000,
        max_findings=1000,
        max_experiments=4,
        max_combinations=0,
        max_encoding_calls=100,
    )


def setup(service, low_hit=False, tool_content="a\nb\n"):
    rows = []
    for index, appid in enumerate(("a", "b", "a")):
        body = {
            "enable_thinking": False,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "f",
                        "description": "existing description",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            ],
            "messages": [
                {
                    "role": "system",
                    "content": f"time 2026-10-31 09:00:0{index}\n" + "stable " * 500,
                },
                {"role": "user", "content": "task"},
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "c",
                            "type": "function",
                            "function": {"name": "f", "arguments": "{}"},
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": "c", "content": tool_content},
            ],
        }
        rows.append(
            valid_row(
                appid=appid,
                request_input=json.dumps(body),
                model_handle_start_time=f"2026-10-27T00:00:0{index}Z",
            )
        )
    (service.inputs.root / "ta005.csv").write_bytes(csv_bytes(rows))
    base = service.submit(RunSubmission(file_ref="ta005.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    selection = SourceSelection(source_kind="base", base_run_id=base.run_id, appid="a")
    registry = PluginRegistry()
    registry.register(TokenContentPlugin())
    diagnostics = DiagnosticService(SourceResolver(service), registry)
    request = DiagnosticRequest(
        source=selection,
        submission_key="analysis",
        selection=DiagnosticSelection(
            reason_codes=("low_hit",) if low_hit else ("request_length",),
            enable_low_hit=low_hit,
            enable_token_content=True,
        ),
    )
    receipt = diagnostics.submit(request, options())
    assert diagnostics.process_next().status in ("ready", "partial")
    return diagnostics, receipt, SourceResolver(service).resolve_scope(selection)


def test_real_saved_candidates_explicit_zero_negative_and_missing_parameters(service, tmp_path):
    diagnostics, receipt, source = setup(service)
    source_digest = file_digest(source.directory / "requests.sqlite3")
    fragments = diagnostics.items(receipt.task_id, "fragment")
    assert len(fragments) == 2
    saved = fragments[-1]
    fragment = from_wire(AnalysisFragment, saved["data"])
    line_candidate = next(
        c for c in fragment.modification_candidates if c.handler_id == "select_result_lines"
    )
    description = next(
        c for c in fragment.modification_candidates if c.handler_id == "replace_tool_description"
    )
    assert not diagnostics.items(receipt.task_id, "evaluation")  # analysis did not auto-evaluate
    for key, candidate, parameters in (
        ("zero", line_candidate, '{"start":0,"end":2}'),
        (
            "negative",
            description,
            json.dumps({"replacement_json": json.dumps("long added text " * 1000)}),
        ),
    ):
        queued = diagnostics.submit_token_evaluation(
            receipt.task_id,
            saved["id"],
            candidate.candidate_id,
            parameters,
            "explicit-business-approval",
            key,
        )
        assert diagnostics.process_next().status == "ready"
        data = diagnostics.items(queued.task_id, "evaluation")[0]["data"]
        # Service presentation adds these documented derived values to the frozen core.
        derived = {
            key: data[key]
            for key in (
                "gate_passed",
                "display_eligible",
                "gain_percentage_points",
                "compute_tokens_delta",
            )
        }
        assert derived["gate_passed"] is None and derived["display_eligible"] is False
        result = from_wire(
            EvaluationResult, {key: value for key, value in data.items() if key not in derived}
        )
        assert result.status == "available" and result.stage == "direct_full"
        assert result.direction == "token_content" and result.gate_passed is None
        assert result.before.n == result.after.n == 2
        if key == "zero":
            assert result.before == result.after and result.modified_after.n == 0
        else:
            assert result.after.p > result.before.p
        assert diagnostics.report(queued.task_id)["evaluation_id"] == result.evaluation_id
    missing = diagnostics.submit_token_evaluation(
        receipt.task_id, saved["id"], line_candidate.candidate_id, "{}", None, "missing"
    )
    assert diagnostics.process_next().status == "partial"
    assert diagnostics.report(missing.task_id)["reason_codes"] == ["BUSINESS_BASIS_REQUIRED"]
    assert diagnostics.items(missing.task_id, "evaluation") == []
    with pytest.raises(TokenScopeError):
        diagnostics.submit_token_evaluation(
            receipt.task_id, saved["id"], "foreign-candidate", "{}", "basis", "wrong"
        )
    assert file_digest(source.directory / "requests.sqlite3") == source_digest


def test_low_hit_precedes_token_original_scope_and_queries_are_readonly(service, monkeypatch):
    diagnostics, receipt, source = setup(service, low_hit=True)
    report = diagnostics.report(receipt.task_id)
    assert [s["direction"] for s in report["stages"]] == ["low_hit", "token_content"]
    assert report["stages"][1]["status"] == "completed"
    fragments = diagnostics.items(receipt.task_id, "fragment")
    for saved in fragments:
        fragment = from_wire(AnalysisFragment, saved["data"])
        original = source.read_request(fragment.request_key)
        assert fragment.raw_sha256 == original.raw_sha256
        t2 = next(
            o
            for o in fragment.observations
            if o.rule_id == "T2" and o.predicate == "content_inventory"
        )
        t4 = next(
            o
            for o in fragment.observations
            if o.rule_id == "T4" and o.predicate == "content_inventory"
        )
        assert t2.unit_ids == t4.unit_ids

    def forbidden(*args, **kwargs):
        raise AssertionError("read query invoked computation")

    monkeypatch.setattr(TokenContentPlugin, "analyze_request", forbidden)
    monkeypatch.setattr(EncodingContext, "encode", forbidden)
    monkeypatch.setattr("tokenscope.analysis_common.service.evaluate_plan", forbidden)
    for _ in range(2):
        assert diagnostics.report(receipt.task_id) == report
        assert diagnostics.items(receipt.task_id, "fragment") == fragments
    assert diagnostics.process_next() is None

"""Bounded synthetic low-hit profile; outputs are evidence, not production strategies."""

import argparse
import cProfile
import csv
import hashlib
import json
import pstats
import resource
import time
from pathlib import Path
from unittest.mock import patch

from tokenscope.analysis_common.bootstrap import build_diagnostics
from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.execution_v2 import RequestV2, RuntimeV2, SelectionV2
from tokenscope.analysis_common.plugins import BudgetSpec, PluginSelection
from tokenscope.analysis_common.runtime_control import TaskControl
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.analysis_common.source_observation import ObservedSource
from tokenscope.domain import RunSubmission
from tokenscope.ingestion.csv_reader import REQUIRED_COLUMNS
from tokenscope.monitoring.service import MonitoringService
from tokenscope.prefix_analysis.detection import collect_dynamics
from tokenscope.prefix_analysis.service import collect_l2
from tokenscope.user_monitoring.contracts import Bind
from tokenscope.user_monitoring.service import UserRunService

SEED = 20261103  # deterministic formulas; no random sampling


def body(case, i):
    a = {
        "type": "function",
        "function": {
            "name": "a",
            "description": "stable lookup",
            "parameters": {"type": "object", "properties": {"q": {"type": "string"}}},
        },
    }
    b = {"type": "function", "function": {"name": "b", "description": "stable second"}}
    value = {
        "messages": [
            {"role": "system", "content": "stable instruction " * 100},
            {"role": "user", "content": "query"},
        ],
        "enable_thinking": False,
    }
    if case == "messages":
        return value
    if case == "schema":
        a["function"]["parameters"]["properties"] = {
            f"field_{n}": {"type": "string", "description": "documented field " * 10}
            for n in range(96)
        }
    if case in ("mixed", "history"):
        value["messages"] += [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call-a",
                        "type": "function",
                        "function": {"name": "a", "arguments": "{}"},
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call-a",
                "content": json.dumps(
                    {"rows": [{"id": n, "status": "ok"} for n in range(8)]},
                    indent=2 if i % 2 else None,
                ),
            },
        ]
        value["messages"] += [{"role": "user", "content": f"legitimate independent question {i}"}]
    if case == "mixed":
        value["messages"][0]["content"] = (
            f"Time 2026-11-03 09:00:{i:02d}\n" + "stable instruction " * 100
        )
        a["function"]["description"] = f"workspace /tmp/job-{i // 2 % 2}\n" + "stable schema " * 40
    tools = [a, b]
    if case == "set" and i % 2:
        tools = [a]
    if case in ("order", "mixed") and i % 2:
        tools.reverse()
    value["tools"] = tools
    return value


def options(k, **updates):
    values = dict(
        token_selection=PluginSelection(
            rule_ids=("T2", "T3", "T4"),
            budget=BudgetSpec(
                max_request_bytes=1048576,
                max_units=10000,
                max_comparison_bytes=2097152,
                max_depth=64,
                max_candidates=1000,
                max_encoding_calls=100,
            ),
        ),
        candidate_limit=k,
        pilot_limit=4,
        max_source_requests=64,
        max_source_bytes=8 * 1024 * 1024,
        max_findings=25,
        max_retained_bytes=1024 * 1024,
        max_comparisons=1000,
        max_experiments=2,
        max_combinations=0,
        max_encoding_calls=512,
    )
    values.update(updates)
    return RuntimeV2(**values)


def prepare(root, case, n):
    inputs = root / "inputs"
    inputs.mkdir(parents=True)
    with (inputs / "synthetic.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(REQUIRED_COLUMNS)
        for i in range(n):
            row = {
                "hash_id": f"synthetic-{i}",
                "appid": "synthetic-profile",
                "model_handle_start_time": f"2026-10-27T00:00:{i:02d}Z",
                "completion_tokens": "12",
                "request_input": json.dumps(body(case, i), ensure_ascii=False),
            }
            writer.writerow([row[k] for k in REQUIRED_COLUMNS])
    service = MonitoringService(inputs, root / "state")
    run = service.submit(RunSubmission(file_ref="synthetic.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    user = UserRunService(service)
    bound = user.submit(
        Bind(submission_key="synthetic-bind", base_run_id=run.run_id, common_name="GLM-5.2")
    )
    user.process_next()
    bound = user.receipt(bound.user_run_id)
    selection = SourceSelection(
        source_kind="user_v2",
        user_run_id=bound.user_run_id,
        appid="synthetic-profile",
        expected_index_revision=bound.index_revision,
        window=None,
    )
    return service, user, selection


def run(root, case, n, k, mode):
    root.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    service, user, selection = prepare(root, case, n)
    setup_seconds = time.perf_counter() - start
    opts = options(k)
    profiler = cProfile.Profile()
    cpu = time.process_time()
    wall = time.perf_counter()
    phase_costs = []
    profiler.enable()
    if mode == "detect":
        control = TaskControl(opts, lambda: False, direction="low_hit")
        with control.telemetry.span("source_initial_verification"):
            source = SourceResolver(service, user).resolve_scope(selection)
        source = ObservedSource(source.service, source.scope, source.directory, control.telemetry)
        reports = []
        for lane, fn in [("l2", collect_l2), ("dynamics", collect_dynamics)]:
            control.lane = lane
            with control.telemetry.span("low_hit_detection." + lane):
                reports.append(
                    fn(
                        source,
                        root / lane,
                        candidate_limit=k,
                        control=control,
                        **({"include_history": True} if lane == "dynamics" else {}),
                    )
                )
        result = {
            "reports": [r.model_dump(mode="json") for r in reports],
            "detected": control.detected,
            "retained": control.retained,
            "retained_bytes": control.retained_bytes,
            "retention_complete": control.retention_complete,
            "encoding_calls": control.encoding_calls,
            "telemetry": control.telemetry.view(),
        }
    else:
        d = build_diagnostics(service, user)
        request = RequestV2(
            source=selection,
            selection=SelectionV2(
                reason_codes=("low_hit",), enable_low_hit=True, enable_token_content=False
            ),
            submission_key="profile",
        )
        receipt = d.submit(request, opts)
        from tokenscope.prefix_analysis import experiments

        original_evaluate = experiments.evaluate_plan

        def measured_evaluate(*args, **kwargs):
            started = time.perf_counter_ns()
            cpu_started = time.process_time_ns()
            try:
                return original_evaluate(*args, **kwargs)
            finally:
                phase_costs.append(
                    {
                        "stage": kwargs.get("stage"),
                        "wall_ns": time.perf_counter_ns() - started,
                        "cpu_ns": time.process_time_ns() - cpu_started,
                    }
                )

        with patch.object(experiments, "evaluate_plan", measured_evaluate):
            terminal = d.process_next()
        result = {
            "receipt_status": terminal.status,
            "report": d.report(receipt.task_id),
            "experiments": d.items(receipt.task_id, "experiment"),
            "evaluations": d.items(receipt.task_id, "evaluation"),
            "optimizations": d.items(receipt.task_id, "optimization"),
            "telemetry": d.report(receipt.task_id)["telemetry"],
        }
    profiler.disable()
    elapsed = time.perf_counter() - wall
    cpu = time.process_time() - cpu
    profiler.dump_stats(str(root / "analysis.prof"))
    stats = pstats.Stats(profiler)
    functions = [
        {
            "file": f,
            "line": line,
            "name": name,
            "primitive_calls": cc,
            "calls": nc,
            "self_seconds": tt,
            "cumulative_seconds": ct,
        }
        for (f, line, name), (cc, nc, tt, ct, _) in stats.stats.items()
    ]
    functions.sort(key=lambda x: x["cumulative_seconds"], reverse=True)
    summary = {
        "case": case,
        "n": n,
        "candidate_limit": k,
        "mode": mode,
        "seed": SEED,
        "model": "GLM-5.2",
        "synthetic": True,
        "source": selection.model_dump(mode="json"),
        "options": opts.model_dump(mode="json"),
        "setup_wall_seconds": setup_seconds,
        "analysis_wall_seconds": elapsed,
        "analysis_cpu_seconds": cpu,
        "process_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "rss_scope": "whole isolated process including model setup; not analysis-only delta",
        "input_bytes": (root / "inputs/synthetic.csv").stat().st_size,
        "input_sha256": hashlib.sha256((root / "inputs/synthetic.csv").read_bytes()).hexdigest(),
        "result": result,
        "profile_functions": functions,
        "evaluation_phase_costs": phase_costs,
    }
    (root / "result.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--case", choices=["messages", "schema", "order", "set", "history", "mixed"], required=True
    )
    parser.add_argument("--n", type=int, choices=[8, 16], required=True)
    parser.add_argument("--k", type=int, choices=[1, 4, 16], required=True)
    parser.add_argument("--mode", choices=["detect", "full"], default="detect")
    a = parser.parse_args()
    r = run(a.output, a.case, a.n, a.k, a.mode)
    print(
        json.dumps(
            {
                k: r[k]
                for k in [
                    "case",
                    "n",
                    "candidate_limit",
                    "mode",
                    "analysis_wall_seconds",
                    "analysis_cpu_seconds",
                    "process_peak_rss_kib",
                ]
            }
        )
    )

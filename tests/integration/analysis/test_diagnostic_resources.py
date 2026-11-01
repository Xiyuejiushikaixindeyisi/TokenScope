"""Reproducible local calibration, not a production throughput claim."""

import json
import platform
import resource
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from conftest import csv_bytes, valid_row
from test_diagnostic_tasks import options

from tokenscope.analysis_common.bootstrap import build_diagnostics
from tokenscope.analysis_common.contracts import (
    DiagnosticRequest,
    DiagnosticSelection,
    SourceSelection,
)
from tokenscope.domain import RunSubmission
from tokenscope.user_monitoring.service import UserRunService


@pytest.mark.parametrize("count,size,tools", [(16, 1024, 2), (64, 8192, 8), (128, 65536, 16)])
def test_local_scale_record(service, count, size, tools):
    rows = []
    start = datetime(2026, 10, 27, tzinfo=UTC)
    for i in range(count):
        raw = json.dumps(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": f"time 2026-10-31 09:00:{i % 60:02d}\n" + "x " * (size // 2),
                    },
                    {"role": "user", "content": "query"},
                ],
                "tools": [
                    {"type": "function", "function": {"name": f"tool_{k}", "description": "static"}}
                    for k in range(tools)
                ],
                "enable_thinking": False,
            }
        )
        rows.append(
            valid_row(
                appid="scale",
                request_input=raw,
                model_handle_start_time=(start + timedelta(seconds=i))
                .isoformat()
                .replace("+00:00", "Z"),
            )
        )
    (service.inputs.root / "scale.csv").write_bytes(csv_bytes(rows))
    del rows
    started = time.perf_counter()
    run = service.submit(RunSubmission(file_ref="scale.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    source_seconds = time.perf_counter() - started
    diagnostics = build_diagnostics(service, UserRunService(service))
    request = DiagnosticRequest(
        source=SourceSelection(source_kind="base", base_run_id=run.run_id, appid="scale"),
        selection=DiagnosticSelection(
            reason_codes=("low_hit",), enable_low_hit=True, enable_token_content=True
        ),
        submission_key="scale",
    )
    configured = options(
        max_source_requests=128,
        max_source_bytes=32 * 1024 * 1024,
        max_findings=256,
        max_experiments=1,
        max_combinations=0,
        max_encoding_calls=1024,
        pilot_limit=8,
    )
    task = diagnostics.submit(request, configured)
    started = time.perf_counter()
    result = diagnostics.process_next()
    elapsed = time.perf_counter() - started
    assert result.status in ("ready", "partial"), result
    report = diagnostics.report(task.task_id)
    assert report["stages"][1]["checked_requests"] == str(count)
    assert int(report["encoding_calls"]) <= 1024
    directory = diagnostics.store.result_directory(task.task_id)
    record = {
        "case": {"requests": count, "static_chars": size, "tools": tools},
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu_budget": service.cpu_budget,
        "source_preparation_seconds": source_seconds,
        "analysis_seconds": elapsed,
        "process_peak_rss_kib_cumulative": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "artifact_bytes": sum(p.stat().st_size for p in directory.rglob("*") if p.is_file()),
        "source_identity": report["scope"]["source"],
        "runtime_options": report["runtime_options"],
        "stages": report["stages"],
        "encoding_calls": report["encoding_calls"],
        "rule_coverage": diagnostics.items(task.task_id, "rule_coverage"),
    }
    output = Path("artifacts/validation/prefix-analysis/lh009")
    output.mkdir(parents=True, exist_ok=True)
    (output / f"scale-{count}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2))

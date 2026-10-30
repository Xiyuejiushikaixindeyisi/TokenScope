"""Fixed synthetic MA resource acceptance; no production input or deployment."""

import argparse
import csv
import json
import os
import resource
import time
from pathlib import Path

from tokenscope.monitoring.ma.contracts import Submit
from tokenscope.monitoring.ma.ingest import COLUMNS
from tokenscope.monitoring.ma.service import MaService
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.monitoring.service import MonitoringService
from tokenscope.resources import configure_process


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.output.resolve()
    project = Path(__file__).resolve().parents[2]
    if not root.is_relative_to(project / "artifacts/validation/monitoring/v2-ma"):
        raise ValueError("resource outputs must stay inside MA validation artifacts")
    root.mkdir(parents=True, exist_ok=False)
    inputs = root / "inputs"
    inputs.mkdir()
    configure_process(8)
    for role, hour in (("pre", 7), ("now", 8)):
        with (inputs / f"{role}.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            for index in range(500):
                content = "shared workload " * 40
                if role == "now" and index == 499:
                    content = "x " * 524288
                stamp = f"2026-10-20T{hour:02}:{index % 60:02}:00Z"
                writer.writerow(
                    dict(
                        instance_uuid=f"cluster-{index % 16:02}",
                        hash_id=str(index),
                        appid=f"tenant-{index % 7}",
                        request_time=stamp,
                        model_handle_start_time=stamp,
                        prompt_tokens="1000",
                        cached_tokens="100",
                        completion_tokens="20",
                        request_input=json.dumps(
                            {"messages": [{"role": "user", "content": content}]}
                        ),
                    )
                )
    base = MonitoringService(inputs, root / "state", cpu_budget=8)
    ma = MaService(base)
    request = Submit(
        submission_key="resource-0",
        pre_file_ref="pre.csv",
        now_file_ref="now.csv",
        model_standard_name="Qwen3.6-27B-64K",
        model_id="Qwen3.6-27B",
        pre_start="2026-10-20T07:00:00Z",
        now_start="2026-10-20T08:00:00Z",
        now_end="2026-10-20T09:00:00Z",
    )
    baseline_fd = len(os.listdir("/proc/self/fd"))
    results = []
    previous = None
    for index in range(2):
        receipt = ma.submit(request.model_copy(update={"submission_key": f"resource-{index}"}))
        start = time.monotonic()
        result = ma.processor.process_next()
        elapsed = time.monotonic() - start
        assert result is not None and result.state == "completed", result
        summary = ma.store.summary(receipt.ma_run_id)
        values = [
            ma.snapshot(receipt.ma_run_id, uuid).instance.model_dump(mode="json")
            for uuid in summary["instance_uuids"]
        ]
        if previous is not None:
            assert values == previous, "repeat run metrics changed"
        previous = values
        fd_count = len(os.listdir("/proc/self/fd"))
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        assert peak <= 3 * 1024**3, "RSS exceeds frozen 3GiB resource budget"
        assert fd_count <= baseline_fd, "file descriptors leaked across runs"
        assert sum(int(value["coverage"]["assigned"]) for value in values) == 500
        results.append(
            dict(
                run_id=receipt.ma_run_id,
                elapsed_seconds_through_commit=elapsed,
                peak_rss_bytes=peak,
                fd_count=fd_count,
                uuid_count=len(values),
                runtime=summary["runtime"],
                file_quality=summary["file_quality"],
                disk_bytes=sum(
                    p.stat().st_size
                    for p in (ma.processor.runs / receipt.ma_run_id).rglob("*")
                    if p.is_file()
                ),
            )
        )
    report = dict(
        kind="synthetic_not_onsite_performance",
        pre_rows=500,
        now_rows=500,
        budget_rss_bytes=3 * 1024**3,
        baseline_fd=baseline_fd,
        runs=results,
        sources={
            p.name: dict(bytes=p.stat().st_size, sha256=file_digest(p)) for p in inputs.iterdir()
        },
    )
    (root / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "passed": True,
                "runs": [
                    {
                        k: r[k]
                        for k in (
                            "elapsed_seconds_through_commit",
                            "peak_rss_bytes",
                            "disk_bytes",
                            "fd_count",
                        )
                    }
                    for r in results
                ],
            }
        )
    )


if __name__ == "__main__":
    main()

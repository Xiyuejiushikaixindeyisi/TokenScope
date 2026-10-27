"""Actual HTTP process E2E plus independent disk-fact reference and restart validation."""

import argparse
import json
import math
import os
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from generate_monitoring_data import generate

from tokenscope.encoding.shards import TokenSlice, read_slice
from tokenscope.monitoring.pipeline import file_digest, verify_seal

ROOT = Path(__file__).resolve().parents[2]


def request(base, path, body=None, method=None):
    req = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def reference(directory, settings):
    """Independent sampled prefix oracle and all-row arithmetic/statistics."""
    with sqlite3.connect(directory / "requests.sqlite3") as db:
        db.row_factory = sqlite3.Row
        apps = [r[0] for r in db.execute("SELECT DISTINCT appid FROM facts ORDER BY appid")]
        assert len(apps) == 5
        max_length = 0
        for appid in apps:
            rows = db.execute(
                "SELECT * FROM facts WHERE appid=? ORDER BY time_ns,source_record_index", (appid,)
            ).fetchall()
            metrics = json.loads(
                db.execute("SELECT metrics_json FROM groups WHERE appid=?", (appid,)).fetchone()[0]
            )
            assert len(rows) == metrics["request_count"]
            for metric, total in metrics["totals"].items():
                assert sum(r[metric] for r in rows) == total
            for metric, qs in metrics["quantiles"].items():
                ordered = sorted(r[metric] for r in rows)
                assert qs == {
                    name: ordered[math.ceil(q * len(rows)) - 1]
                    for name, q in [("p50", 0.5), ("p80", 0.8), ("p90", 0.9)]
                }
            for row in rows:
                assert (
                    row["prompt_tokens"]
                    == row["ideal_cached_input_tokens"] + row["ideal_compute_input_tokens"]
                )
                max_length = max(max_length, row["prompt_tokens"])
            # Compare the first 30 in chronological order against complete historical sequences.
            history = []
            size = settings["block_size"] * settings["cp_world_size"]
            for row in rows[:30]:
                ids = read_slice(
                    directory / "tokens", TokenSlice.model_validate_json(row["token_slice_json"])
                )
                longest = 0
                for previous in history:
                    common = 0
                    for a, b in zip(ids, previous, strict=False):
                        if a != b:
                            break
                        common += 1
                    longest = max(longest, common // size)
                matched = min(longest, max(len(ids) - 1, 0) // size)
                hit = (
                    max(matched - int(settings["mtp"]), 0) * size
                    if settings["prefix_cache_enabled"]
                    else 0
                )
                assert row["ideal_cached_input_tokens"] == hit
                history.append(ids)
        return dict(
            appids=len(apps),
            maximum_prompt_tokens=max_length,
            arithmetic="all requests",
            reference_prefix_replay="first 30 per appid",
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mean-requests", type=int, default=2000)
    parser.add_argument("--long-per-app", type=int, default=15)
    parser.add_argument("--batch", choices=["B005", "B005.1"], default="B005")
    args = parser.parse_args()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "artifacts/validation/monitoring" / args.batch / stamp
    out.mkdir(parents=True)
    manifest = generate(
        out / "inputs", mean_requests=args.mean_requests, long_per_app=args.long_per_app
    )
    state = out / "state"
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    cmd = [
        sys.executable,
        "-m",
        "tokenscope.cli",
        "--input-root",
        str(out / "inputs"),
        "--state-root",
        str(state),
        "--asset-root",
        str(ROOT),
        "serve",
        "--port",
        str(port),
    ]
    log = (out / "server.log").open("w")
    process = None
    checks = []
    peaks = dict(rss_kib=0, threads=0)

    def start():
        server = subprocess.Popen(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        for _ in range(200):
            try:
                request(base, "/healthz")
                return server
            except (OSError, urllib.error.URLError):
                if server.poll() is not None:
                    raise RuntimeError("Server exited") from None
                time.sleep(0.1)
        server.terminate()
        server.wait()
        raise RuntimeError("Server did not start")

    def sample():
        try:
            fields = dict(
                line.split(":", 1)
                for line in Path(f"/proc/{process.pid}/status").read_text().splitlines()
                if ":" in line
            )
            peaks["rss_kib"] = max(peaks["rss_kib"], int(fields["VmRSS"].strip().split()[0]))
            peaks["threads"] = max(peaks["threads"], int(fields["Threads"]))
        except (OSError, KeyError):
            pass

    try:
        process = start()
        previous = None
        for item in manifest["files"]:
            started = time.monotonic()
            run = request(
                base, "/analysis-runs", {"file_ref": item["file_ref"], "model_id": item["model_id"]}
            )
            run_id = run["run_id"]
            while True:
                sample()
                current = request(base, f"/analysis-runs/{run_id}")
                if previous:
                    with ThreadPoolExecutor(max_workers=3) as pool:
                        list(
                            pool.map(
                                lambda path: request(base, path),
                                [
                                    f"/analysis-runs/{previous}/metrics",
                                    f"/analysis-runs/{previous}/length-histograms?appid=synthetic-app-1",
                                    f"/analysis-runs/{previous}/lengths?appid=synthetic-app-1&limit=5",
                                ],
                            )
                        )
                if current["status"] not in ("queued", "running"):
                    break
                if time.monotonic() - started > 7200:
                    raise RuntimeError("Local run exceeded 2h")
                time.sleep(0.2)
            assert current["status"] == "completed", current
            assert current["result"]["quality"]["records_read"] == item["records"]
            assert current["result"]["quality"]["skipped_rows"] == item["invalid_rows"]
            elapsed = time.monotonic() - started
            directory = state / "runs" / run_id
            oracle = reference(directory, current["settings"])
            assert oracle["maximum_prompt_tokens"] >= 200000
            verify_seal(directory, run_id)
            metrics = request(base, f"/analysis-runs/{run_id}/metrics")
            assert metrics["total_groups"] == 5
            for group in metrics["groups"]:
                app = urllib.parse.quote(group["appid"])
                for width in [1000, 2000, 5000]:
                    hist = request(
                        base,
                        f"/analysis-runs/{run_id}/length-histograms?appid={app}&bin_width={width}",
                    )
                    for value in hist["metrics"].values():
                        assert sum(b["count"] for b in value["bins"]) == group["request_count"]
                first = request(base, f"/analysis-runs/{run_id}/lengths?appid={app}&limit=2")
                second = request(
                    base, f"/analysis-runs/{run_id}/lengths?appid={app}&offset=2&limit=2"
                )
                assert [p["rank"] for p in first["points"] + second["points"]] == [1, 2, 3, 4]
            cli = json.loads(
                subprocess.check_output(cmd[: cmd.index("serve")] + ["metrics", run_id], cwd=ROOT)
            )
            assert cli == metrics
            record = dict(
                model_id=item["model_id"],
                run_id=run_id,
                wall_seconds_submit_to_complete=elapsed,
                result=current["result"],
                reference=oracle,
                peak_server_process_so_far=dict(peaks),
                artifact_bytes=sum(p.stat().st_size for p in directory.rglob("*") if p.is_file()),
            )
            if args.batch == "B005.1":
                from run_monitoring_view_e2e import check_views

                record["view_checks"] = check_views(base, run_id, metrics)
            checks.append(record)
            (out / f"{item['file_ref']}.metrics.json").write_text(json.dumps(metrics, indent=2))
            print(
                json.dumps(
                    dict(
                        model=item["model_id"],
                        seconds=elapsed,
                        quality=current["result"]["quality"],
                        peak_rss_mib=peaks["rss_kib"] / 1024,
                    )
                ),
                flush=True,
            )
            previous = run_id
        before = request(base, f"/analysis-runs/{previous}/metrics")
        process.terminate()
        process.wait(timeout=40)
        process = start()
        assert request(base, f"/analysis-runs/{previous}/metrics") == before
        # Kill our own worker process during a live run, then verify durable recovery.
        interrupted = request(
            base,
            "/analysis-runs",
            {
                "file_ref": manifest["files"][0]["file_ref"],
                "model_id": manifest["files"][0]["model_id"],
            },
        )
        crash_id = interrupted["run_id"]
        deadline = time.monotonic() + 30
        while True:
            active = request(base, f"/analysis-runs/{crash_id}")
            if active["status"] == "running" and active["snapshot"]["runtime"] is not None:
                break
            assert active["status"] in ("queued", "running")
            assert time.monotonic() < deadline
            time.sleep(0.1)
        process.kill()
        process.wait(timeout=10)
        process = start()
        deadline = time.monotonic() + 10
        while request(base, f"/analysis-runs/{crash_id}")["status"] == "running":
            assert time.monotonic() < deadline
            time.sleep(0.1)
        assert request(base, f"/analysis-runs/{crash_id}")["status"] == "interrupted"
        assert request(base, f"/analysis-runs/{previous}/metrics") == before
        version = request(base, "/version")
        report = dict(
            passed=True,
            data_kind="synthetic_not_production",
            manifest=manifest,
            checks=checks,
            http_concurrent_reads=True,
            cli_parity=True,
            restart_persistence=True,
            actual_process_kill_recovery=True,
            python=sys.version,
            platform=os.uname()._asdict() if hasattr(os.uname(), "_asdict") else list(os.uname()),
            version=version,
            uv_lock_sha256=file_digest(ROOT / "uv.lock"),
            source_files_sha256={
                str(p.relative_to(ROOT)): file_digest(p)
                for p in sorted(
                    [
                        *ROOT.glob("src/**/*.py"),
                        *ROOT.glob("scripts/validation/*.py"),
                        ROOT / "pyproject.toml",
                        ROOT / "uv.lock",
                    ]
                )
            },
            peak_server=peaks,
        )
        (out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        print("E2E_PASS", out, flush=True)
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=40)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        log.close()


if __name__ == "__main__":
    main()

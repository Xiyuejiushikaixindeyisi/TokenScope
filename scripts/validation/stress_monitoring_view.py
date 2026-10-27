"""Isolated presentation load fixtures, not fabricated measurement evidence."""

import csv
import fcntl
import hashlib
import io
import json
import math
import socket
import sqlite3
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import httpx

from tokenscope.domain import RunSubmission
from tokenscope.monitoring.service import MonitoringService
from tokenscope.monitoring.view_projection import location

ROOT = Path(__file__).resolve().parents[2]


def main():
    out = (
        ROOT
        / "artifacts/validation/monitoring/B005.1"
        / ("stress-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"))
    )
    inputs = out / "inputs"
    inputs.mkdir(parents=True)
    text = io.StringIO(newline="")
    csv.writer(text).writerows(
        [
            ["hash_id", "appid", "model_handle_start_time", "completion_tokens", "request_input"],
            [
                "fixture",
                "load",
                "2026-10-27T00:00:00Z",
                "1",
                json.dumps(dict(messages=[dict(role="user", content="load fixture")])),
            ],
        ]
    )
    (inputs / "synthetic.csv").write_text(text.getvalue())
    service = MonitoringService(inputs, out / "state")
    run = service.submit(RunSubmission(file_ref="synthetic.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    # Dedicated synthetic DB extension exercises directory and export capacity only.
    with service.control.connect() as db:
        g = db.execute("SELECT * FROM publication_groups").fetchone()
        for i in range(1000):
            app = f"load-{i:04}"
            db.execute(
                "INSERT INTO publication_groups VALUES(?,?,?,?,?,?)",
                (run.run_id, app, g["model_id"], g["min_ns"], g["max_ns"], g["publish_seq"]),
            )
            db.execute(
                "INSERT INTO active_groups VALUES(?,?,?,?,?)",
                (app, g["model_id"], run.run_id, g["max_ns"], g["publish_seq"]),
            )
    with sqlite3.connect(location(service.state_root, run.run_id) / "view.sqlite3") as db:
        row = db.execute("SELECT * FROM request_projection").fetchone()
        db.execute("DELETE FROM request_projection")
        for i in range(1024):
            db.execute(
                "INSERT INTO request_projection VALUES(?,?,?,?,?,?,?,?,?)",
                (i + 1, "load", "x" * 262144, *row[3:]),
            )
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    base = f"http://127.0.0.1:{port}"
    cmd = [
        sys.executable,
        "-m",
        "tokenscope.cli",
        "--input-root",
        str(inputs),
        "--state-root",
        str(service.state_root),
        "--asset-root",
        str(ROOT),
        "serve",
        "--port",
        str(port),
    ]
    log = (out / "server.log").open("w")
    proc = subprocess.Popen(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    stop = threading.Event()

    def rss():
        for line in Path(f"/proc/{proc.pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) * 1024
        raise AssertionError("No RSS")

    try:
        with httpx.Client(base_url=base, timeout=60) as client:
            for _ in range(200):
                try:
                    client.get("/healthz").raise_for_status()
                    break
                except httpx.TransportError:
                    time.sleep(0.1)
            # Directory revision-pinned traversal of >1000 groups.
            catalog = client.get("/monitoring/catalog?limit=100").raise_for_status().json()
            assert catalog["total"] == "1001"
            items = list(catalog["items"])
            offset = catalog["next_offset"]
            while offset is not None:
                data = (
                    client.get(
                        "/monitoring/catalog",
                        params=dict(
                            offset=offset, limit=100, catalog_revision=catalog["catalog_revision"]
                        ),
                    )
                    .raise_for_status()
                    .json()
                )
                items.extend(data["items"])
                offset = data["next_offset"]
            assert len(items) == len({x["appid"] for x in items}) == 1001
            timings = []
            for _ in range(30):
                start = time.monotonic()
                client.get("/monitoring/catalog?limit=100").raise_for_status()
                timings.append(1000 * (time.monotonic() - start))
            p95 = sorted(timings)[math.ceil(0.95 * len(timings)) - 1]
            assert p95 <= 300
            baseline = rss()
            peak = [baseline]

            def sample():
                while not stop.wait(0.01):
                    peak[0] = max(peak[0], rss())

            monitor = threading.Thread(target=sample)
            monitor.start()
            count = size = 0
            digest = hashlib.sha256()
            summary = None
            with client.stream(
                "GET", f"/analysis-runs/{run.run_id}/requests/export?appid=load&format=ndjson"
            ) as response:
                response.raise_for_status()
                for raw in response.iter_lines():
                    size += len(raw.encode()) + 1
                    value = json.loads(raw)
                    if value["type"] == "request":
                        count += 1
                        digest.update(raw.encode() + b"\n")
                    if value["type"] == "summary":
                        summary = value
            stop.set()
            monitor.join()
            assert size >= 256 * 1024 * 1024 and count == 1024
            assert summary["request_lines_sha256"] == digest.hexdigest()
            extra = peak[0] - baseline
            assert extra <= 64 * 1024 * 1024, (baseline, peak)
            # 19 consuming connections and one deliberately slow consumer; isolated real sockets.
            ready = [threading.Event() for _ in range(20)]
            cursor = client.get("/monitoring/catalog").json()["cursor"]
            released = [0.0]

            def listen(i):
                with httpx.Client(base_url=base, timeout=15) as c:
                    with c.stream(
                        "GET", "/monitoring/events", params=dict(after=cursor)
                    ) as response:
                        response.raise_for_status()
                        ready[i].set()
                        if i == 19:
                            time.sleep(2)
                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                return (time.monotonic() - released[0]) * 1000
                raise AssertionError("Missing SSE event")

            with ThreadPoolExecutor(20) as pool:
                futures = [pool.submit(listen, i) for i in range(20)]
                for event in ready:
                    assert event.wait(20)
                with (service.state_root / "worker.lock").open("a") as lock:
                    fcntl.flock(lock, fcntl.LOCK_EX)
                    terminal = service.control.enqueue(
                        RunSubmission(file_ref="missing.csv", model_id="GLM-5.2")
                    )
                    service.control.claim_next()
                    released[0] = time.monotonic()
                    service.control.fail(terminal.run_id, "SYNTHETIC_FAILURE")
                delays = [f.result(timeout=20) for f in futures]
            fast = sorted(delays[:19])
            latency = fast[math.ceil(0.95 * len(fast)) - 1]
            assert latency <= 1000, delays
            report = dict(
                passed=True,
                fixture_kind="synthetic_projection_load_only",
                groups=1001,
                catalog_p95_ms=p95,
                export_bytes=size,
                export_rows=count,
                server_rss_baseline=baseline,
                server_rss_peak=peak[0],
                server_rss_delta=extra,
                sse_connections=20,
                sse_fast_p95_ms=latency,
                sse_slow_ms=delays[-1],
                terminal_run_id=terminal.run_id,
                ui_or_browser_test=False,
                docker=False,
            )
            (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps(report), flush=True)
            print(out, flush=True)
    finally:
        stop.set()
        proc.terminate()
        try:
            proc.wait(30)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        log.close()


if __name__ == "__main__":
    main()

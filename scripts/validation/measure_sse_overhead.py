"""Repeated real-service timings with/without 20 SSE connections, synthetic GLM input."""

import json
import shutil
import socket
import statistics
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]


def main():
    out = (
        ROOT
        / "artifacts/validation/monitoring/B005.1"
        / ("sse-overhead-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"))
    )
    out.mkdir(parents=True)
    reports = sorted((ROOT / "artifacts/validation/monitoring/B005.1").glob("20*/report.json"))
    source = reports[-1].parent
    report = json.loads(reports[-1].read_text())
    item = report["manifest"]["files"][0]
    inputs = out / "inputs"
    inputs.mkdir()
    shutil.copy2(source / "inputs" / item["file_ref"], inputs / item["file_ref"])
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    base = f"http://127.0.0.1:{port}"
    log = (out / "server.log").open("w")
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "tokenscope.cli",
            "--input-root",
            str(inputs),
            "--state-root",
            str(out / "state"),
            "--asset-root",
            str(ROOT),
            "serve",
            "--port",
            str(port),
        ],
        cwd=ROOT,
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    stop = threading.Event()
    ready = [threading.Event() for _ in range(20)]
    observations = []
    try:
        with httpx.Client(base_url=base, timeout=60) as client:
            for _ in range(200):
                try:
                    client.get("/healthz").raise_for_status()
                    break
                except httpx.TransportError:
                    time.sleep(0.1)

            def run():
                start = time.monotonic()
                task = (
                    client.post(
                        "/analysis-runs",
                        json=dict(file_ref=item["file_ref"], model_id=item["model_id"]),
                    )
                    .raise_for_status()
                    .json()
                )
                while True:
                    status = (
                        client.get("/analysis-runs/" + task["run_id"]).raise_for_status().json()
                    )
                    if status["status"] not in ("queued", "running"):
                        assert status["status"] == "completed", status
                        seconds = time.monotonic() - start
                        observations.append(dict(run_id=task["run_id"], seconds=seconds))
                        return seconds
                    assert time.monotonic() - start < 7200
                    time.sleep(0.05)

            warmup = run()
            baseline = [run() for _ in range(3)]
            cursor = client.get("/monitoring/catalog").json()["cursor"]

            def listen(i):
                with httpx.Client(base_url=base, timeout=35) as listener:
                    with listener.stream(
                        "GET", "/monitoring/events", params=dict(after=cursor)
                    ) as response:
                        response.raise_for_status()
                        ready[i].set()
                        for _line in response.iter_lines():
                            if stop.is_set():
                                return
                            if i == 19:
                                time.sleep(0.25)
                raise AssertionError("SSE disconnected unexpectedly")

            with ThreadPoolExecutor(20) as pool:
                futures = [pool.submit(listen, i) for i in range(20)]
                for event in ready:
                    assert event.wait(20)
                loaded = [run() for _ in range(3)]
                stop.set()
                for future in futures:
                    future.result(timeout=30)
            overhead = statistics.median(loaded) / statistics.median(baseline) - 1
            result = dict(
                passed=overhead <= 0.10,
                synthetic=True,
                model=item["model_id"],
                input_sha256=item.get("sha256"),
                warmup_seconds=warmup,
                baseline_seconds=baseline,
                subscribers_20_seconds=loaded,
                median_relative_overhead=overhead,
                observations=observations,
                docker=False,
            )
            (out / "report.json").write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps(result), flush=True)
            print(out, flush=True)
            assert result["passed"], result
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

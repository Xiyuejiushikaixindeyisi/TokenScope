"""Actual HTTP replay with exclusive synthetic state; keeps service for user review."""

import argparse
import hashlib
import json
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from v3_repair_fixtures import generate

ROOT = Path(__file__).resolve().parents[2]
ORIGIN = "http://127.0.0.1:18002"


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def request(path, instance=None, body=None):
    headers = {"Content-Type": "application/json"}
    if instance:
        headers.update(
            {"x-tokenscope-service-instance": instance, "x-tokenscope-instance-id": instance}
        )
    req = urllib.request.Request(
        ORIGIN + path, headers=headers, data=None if body is None else json.dumps(body).encode()
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def wait(path, instance, field="state"):
    # Test-harness guard only, never installed in the product runtime.
    started = time.monotonic()
    while True:
        value = request(path, instance)
        if value[field] not in ("queued", "running", "preparing"):
            return value
        if time.monotonic() - started > 7200:
            raise RuntimeError("HARNESS_NOT_FINISHED_2H")
        time.sleep(0.25)


def run_case(output, case, instance):
    run = request("/analysis-runs", instance, {"file_ref": case["file"], "model_id": case["model"]})
    monitoring = wait("/analysis-runs/" + run["run_id"], instance, "status")
    save(output / (case["group"] + "-monitoring.json"), monitoring)
    assert monitoring["status"] == "completed", monitoring
    prep = request(
        "/diagnostics/v3/source-preparations",
        instance,
        {
            "submission_key": case["group"],
            "source": {"source_kind": "base", "base_run_id": run["run_id"], "appid": case["appid"]},
        },
    )
    prep_id = prep["preparation_id"]
    prepared = wait("/diagnostics/v3/source-preparations/" + prep_id + "/execution", instance)
    save(output / (case["group"] + "-preparation.json"), prepared)
    assert prepared["state"] == "completed", prepared
    task = request(
        "/diagnostics/v3/tasks",
        instance,
        {"submission_key": case["group"], "preparation_id": prep_id},
    )
    ident = task["task_id"]
    execution = wait("/diagnostics/v3/tasks/" + ident, instance)
    save(output / (case["group"] + "-execution.json"), execution)
    report = request("/diagnostics/v3/tasks/" + ident + "/report", instance)
    save(output / (case["group"] + "-report.json"), report)
    assert execution["state"] == "completed" and not execution["forced_termination"], execution
    assert report["discovery"]["complete"], report["discovery"]["reason_codes"]
    assert any(r["finding"]["rule_version"] == "clock-3.1" for r in report["recommendations"])
    assert all(r["windows"][0]["complete"] for r in report["recommendations"])
    save(
        output / (case["group"] + "-link.json"),
        {
            "appid": case["appid"],
            "model": case["model"],
            "task": ident,
            "run": run["run_id"],
            "preparation": prep_id,
            "url": ORIGIN + "/#/analysis?direction=low_hit&mode=history&task=" + ident,
        },
    )
    print(case["group"], ident, "complete", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("dist", type=Path)
    args = parser.parse_args()
    output, dist = args.output.resolve(), args.dist.resolve()
    assert output.is_relative_to(ROOT / "artifacts/validation/development-v3")
    assert dist.is_relative_to(ROOT / "artifacts/validation/development-v3")
    with socket.socket() as sock:
        assert sock.connect_ex(("127.0.0.1", 18002)) != 0, "Old service still running"
    output.mkdir(parents=True, exist_ok=False)
    fixtures = generate(output / "inputs")
    command = [
        sys.executable,
        "-m",
        "tokenscope.cli",
        "--input-root",
        str(output / "inputs"),
        "--state-root",
        str(output / "state"),
        "--asset-root",
        str(ROOT),
        "--cpu-budget",
        "2",
        "serve",
        "--host",
        "0.0.0.0",
        "--port",
        "18002",
        "--viewer-root",
        str(dist),
    ]
    # No model/worker is started before the old-service checks and new-state creation.
    with (output / "server.log").open("x") as log:
        server = subprocess.Popen(
            command,
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,
        )
    save(output / "server.json", {"pid": server.pid, "command": command, "origin": ORIGIN})
    try:
        for _ in range(100):
            try:
                instance = request("/diagnostics/v3/capabilities")["service_instance_id"]
                break
            except OSError:
                assert server.poll() is None
                time.sleep(0.1)
        else:
            raise RuntimeError("SERVER_START_FAILED")
        save(
            output / "candidate.json",
            {
                "instance": instance,
                "version": request("/version"),
                "source_sha256": {
                    str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for folder in (ROOT / "src", ROOT / "apps/viewer/src")
                    for p in sorted(folder.rglob("*"))
                    if p.is_file() and "__pycache__" not in p.parts
                },
                "dist_sha256": {
                    str(p.relative_to(dist)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(dist.rglob("*"))
                    if p.is_file()
                },
            },
        )
        for case in fixtures["groups"]:
            run_case(output, case, instance)
        save(
            output / "BACKEND_PASS.json",
            {
                "groups": 5,
                "count": 64,
                "instance": instance,
                "frontend": "PENDING",
                "large_source": "PENDING",
                "user_acceptance": "PENDING",
            },
        )
    except BaseException as exc:
        save(output / "FAIL.json", {"error": str(exc), "server_pid": server.pid})
        raise


if __name__ == "__main__":
    main()

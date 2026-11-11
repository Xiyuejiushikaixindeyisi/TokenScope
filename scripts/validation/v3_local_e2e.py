"""Fresh-state real HTTP/browser acceptance driver; outputs are exclusive per attempt."""

import argparse
import csv
import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--dist", type=Path, required=True)
parser.add_argument("--prefix-inputs", type=Path)
args = parser.parse_args()
root = args.output.resolve()
assert root.is_relative_to(PROJECT / "artifacts/validation/development-v3/V3B007")
root.mkdir(parents=True, exist_ok=False)
inputs, state = root / "inputs", root / "state"
inputs.mkdir()
sock = socket.socket()
assert sock.connect_ex(("127.0.0.1", 18002)) != 0, "Old service still occupies acceptance port"
sock.close()
cases = [
    dict(appid="v3-deepseek", model="DeepSeek-V4-Flash-0731", count=16, large=False),
    dict(appid="v3-qwen", model="Qwen3.6-27B", count=16, large=False),
    dict(appid="v3-large", model="DeepSeek-V4-Flash-0731", count=2200, large=True),
]
for case in cases:
    with (inputs / (case["appid"] + ".csv")).open("x", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ["hash_id", "appid", "model_handle_start_time", "completion_tokens", "request_input"]
        )
        for i in range(case["count"]):
            stamp = datetime(2026, 11, 10, tzinfo=UTC) + timedelta(seconds=i)
            clock = stamp.strftime("%Y/%m/%d %H:%M:%S")
            text = (
                "stable-prefix " * 160
                + f"<session_clock>{clock}</session_clock>"
                + " stable-suffix" * 160
            )
            messages = [{"role": "system", "content": text}, {"role": "user", "content": "hello"}]
            if i % 2:
                messages.extend(
                    [{"role": "assistant", "content": "reply"}, {"role": "user", "content": "next"}]
                )
            writer.writerow(
                [f"h{i}", case["appid"], stamp.isoformat(), 12, json.dumps({"messages": messages})]
            )
if args.prefix_inputs:
    # Read-only copies of the independent review's synthetic inputs; never reuse its state.
    for name, rule in (
        ("cch", "L1"),
        ("plain_timestamp", "L1"),
        ("workspace", "L1"),
        ("tool_order", "L2"),
        ("tool_description", "L3"),
        ("tool_added", "L3"),
    ):
        payload = (args.prefix_inputs / (name + ".csv")).read_bytes()
        with (inputs / (name + ".csv")).open("xb") as stream:
            stream.write(payload)
        cases.append(
            dict(
                appid=name,
                model="DeepSeek-V4-Flash-0731",
                count=8,
                large=False,
                prefix_rule=rule,
                evidence_only=name == "tool_added",
            )
        )
    with (inputs / "representation.csv").open("x", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ["hash_id", "appid", "model_handle_start_time", "completion_tokens", "request_input"]
        )
        for i in range(8):
            body = {
                "messages": [
                    {"role": "user", "content": "hello"},
                    {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_a",
                                "type": "function",
                                "function": {"name": "a", "arguments": "{}"},
                            }
                        ],
                    },
                    {
                        "role": "tool",
                        "tool_call_id": "call_a",
                        "content": '{"a":1}' if i % 2 else '{ "a": 1 }',
                    },
                ],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "a",
                            "description": "stable",
                            "parameters": {"type": "object", "properties": {}},
                        },
                    }
                ],
            }
            writer.writerow(
                [f"r{i}", "representation", f"2026-11-10T09:00:0{i}Z", 12, json.dumps(body)]
            )
    cases.append(
        dict(
            appid="representation",
            model="DeepSeek-V4-Flash-0731",
            count=8,
            large=False,
            prefix_rule="L5",
            evidence_only=True,
        )
    )
(root / "cases.json").write_text(json.dumps(cases))
command = [
    sys.executable,
    "-m",
    "tokenscope.cli",
    "--input-root",
    str(inputs),
    "--state-root",
    str(state),
    "--asset-root",
    str(PROJECT),
    "--cpu-budget",
    "2",
    "serve",
    "--host",
    "127.0.0.1",
    "--port",
    "18002",
    "--viewer-root",
    str(args.dist.resolve()),
]
log = (root / "server.log").open("x")
server = subprocess.Popen(command, cwd=PROJECT, stdout=log, stderr=log, start_new_session=True)
origin = "http://127.0.0.1:18002"


def request(path, body=None, instance=None):
    headers = {"Content-Type": "application/json"}
    if instance:
        headers.update(
            {"x-tokenscope-instance-id": instance, "x-tokenscope-service-instance": instance}
        )
    req = urllib.request.Request(
        origin + path, data=None if body is None else json.dumps(body).encode(), headers=headers
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


try:
    for _ in range(100):
        try:
            caps = request("/diagnostics/v3/capabilities")
            break
        except OSError:
            assert server.poll() is None, "Candidate failed to start"
            time.sleep(0.1)
    else:
        raise RuntimeError("Startup timed out")
    instance = caps["service_instance_id"]
    source_files = [
        p
        for folder in (PROJECT / "src", PROJECT / "apps/viewer/src")
        for p in folder.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    ]
    (root / "source-sha256.json").write_text(
        json.dumps(
            {
                str(p.relative_to(PROJECT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(source_files)
            },
            indent=2,
        )
    )
    (root / "candidate.json").write_text(
        json.dumps(
            {
                "command": command,
                "pid": server.pid,
                "instance": instance,
                "version": request("/version"),
                "dist": str(args.dist.resolve()),
                "dist_sha256": {
                    str(p.relative_to(args.dist)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in args.dist.rglob("*")
                    if p.is_file()
                },
            },
            indent=2,
        )
    )
    for case in cases:
        run = request(
            "/analysis-runs",
            dict(file_ref=case["appid"] + ".csv", model_id=case["model"]),
            instance,
        )
        deadline = time.monotonic() + 240
        while run["status"] in ("queued", "running"):
            assert time.monotonic() < deadline
            time.sleep(0.3)
            run = request("/analysis-runs/" + run["run_id"], instance=instance)
        assert run["status"] == "completed", run
        (root / (case["appid"] + "-monitoring.json")).write_text(json.dumps(run, indent=2))
    node = "/home/zhangxiyue/.nvm/versions/node/v22.22.2/bin/node"
    subprocess.run(
        [node, str(PROJECT / "scripts/validation/v3_browser_e2e.mjs"), str(root), origin],
        cwd=PROJECT,
        check=True,
        timeout=900,
    )
    results = json.loads((root / "browser-results.json").read_text())
    for item in results["results"]:
        execution = request("/diagnostics/v3/tasks/" + item["task"], instance=instance)
        report = request("/diagnostics/v3/tasks/" + item["task"] + "/report", instance=instance)
        assert execution["state"] == "completed" and not execution["forced_termination"], execution
        (root / (item["appid"] + "-execution.json")).write_text(json.dumps(execution, indent=2))
        (root / (item["appid"] + "-report.json")).write_text(
            json.dumps(report, ensure_ascii=False, indent=2)
        )
    (root / "SUCCESS").write_text(
        "Real HTTP/browser cases completed; Huawei business gains NOT_RUN\n"
    )
finally:
    os.killpg(server.pid, signal.SIGTERM)
    server.wait(timeout=30)
    log.close()
    sock = socket.socket()
    closed = sock.connect_ex(("127.0.0.1", 18002)) != 0
    sock.close()
    (root / "shutdown.json").write_text(
        json.dumps({"exit_code": server.returncode, "port_closed": closed})
    )

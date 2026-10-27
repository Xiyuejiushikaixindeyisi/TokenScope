"""Reproducible B001 gate, environment identity and real-process HTTP smoke check."""

import hashlib
import importlib.metadata
import json
import platform
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/validation/monitoring/B001"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    results = []
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    for name, command in (
        ("pytest", [sys.executable, "-m", "pytest", "-q"]),
        ("ruff", [sys.executable, "-m", "ruff", "check", "src", "tests", str(Path(__file__))]),
        (
            "format",
            [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--check",
                "src",
                "tests",
                str(Path(__file__)),
            ],
        ),
        ("mypy", [sys.executable, "-m", "mypy"]),
    ):
        logfile = OUT / f"{timestamp}-{name}.log"
        started = time.monotonic()
        with logfile.open("w") as log:
            result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        results.append(
            {
                "check": name,
                "command": command,
                "exit_code": result.returncode,
                "seconds": time.monotonic() - started,
                "log": str(logfile.relative_to(ROOT)),
            }
        )
        print(name, result.returncode, logfile.read_text()[-2000:])
    with tempfile.TemporaryDirectory(prefix="b001-", dir=OUT) as temporary:
        work = Path(temporary)
        inputs = work / "inputs"
        inputs.mkdir()
        args = [
            sys.executable,
            "-m",
            "tokenscope.cli",
            "--input-root",
            str(inputs),
            "--state-root",
            str(work / "state"),
        ]
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        with (OUT / f"{timestamp}-http.log").open("w") as log:
            process = subprocess.Popen(
                [*args, "serve", "--port", str(port)],
                cwd=ROOT,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            try:
                deadline = time.monotonic() + 15
                while True:
                    try:
                        with urllib.request.urlopen(
                            f"http://127.0.0.1:{port}/healthz", timeout=1
                        ) as response:
                            assert response.status == 200
                            assert json.load(response) == {"status": "alive"}
                        break
                    except urllib.error.URLError:
                        if time.monotonic() > deadline or process.poll() is not None:
                            raise
                        time.sleep(0.1)
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/models", timeout=2
                ) as response:
                    assert [item["settings"]["block_size"] for item in json.load(response)] == [
                        128,
                        1536,
                        32,
                    ]
                try:
                    urllib.request.urlopen(f"http://127.0.0.1:{port}/readyz", timeout=2)
                    raise AssertionError("B001 must not claim analysis readiness")
                except urllib.error.HTTPError as response:
                    assert response.code == 503
                    assert json.load(response)["ready"] is False
                results.append(
                    {
                        "check": "real_process_http",
                        "exit_code": 0,
                        "command": [*args, "serve", "--port", str(port)],
                        "log": str((OUT / f"{timestamp}-http.log").relative_to(ROOT)),
                    }
                )
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        schema = subprocess.run(
            [*args, "schema"], cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE
        ).stdout
        target = ROOT / "docs/contracts/schemas/monitoring-b001.openapi.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(json.loads(schema), indent=2, ensure_ascii=False) + "\n")
    report = {
        "timestamp_utc": timestamp,
        "python": sys.version,
        "platform": platform.platform(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("fastapi", "pydantic", "uvicorn", "pytest", "ruff", "mypy", "httpx")
        },
        "uv_lock_sha256": hashlib.sha256((ROOT / "uv.lock").read_bytes()).hexdigest(),
        "checks": results,
        "passed": all(item["exit_code"] == 0 for item in results),
    }
    (OUT / f"{timestamp}-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("gate_checks_passed", report["passed"])
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Local gate only: never builds images or modifies approved design documents."""

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("batch", choices=["B002", "B003", "B004", "B005", "B005.1", "B006"])
    args = parser.parse_args()
    out = ROOT / "artifacts/validation/monitoring" / args.batch
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    results = []
    for name, command in [
        ("pytest", [sys.executable, "-m", "pytest", "-q"]),
        (
            "ruff",
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "src",
                "tests",
                "scripts/validation",
            ],
        ),
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
                "scripts/validation",
            ],
        ),
        ("mypy", [sys.executable, "-m", "mypy"]),
    ]:
        log = out / f"{stamp}-{name}.log"
        started = time.monotonic()
        with log.open("w") as stream:
            result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
        results.append(
            dict(
                check=name,
                command=command,
                exit_code=result.returncode,
                seconds=time.monotonic() - started,
                log=str(log.relative_to(ROOT)),
            )
        )
        print(name, result.returncode, log.read_text()[-3000:], flush=True)
    passed = all(r["exit_code"] == 0 for r in results)
    report = dict(
        timestamp_utc=stamp,
        python=sys.version,
        platform=platform.platform(),
        checks=results,
        passed=passed,
    )
    (out / f"{stamp}-report.json").write_text(json.dumps(report, indent=2) + "\n")
    if passed:
        files = sorted(
            [
                *ROOT.glob("src/**/*.py"),
                *ROOT.glob("src/**/*.json"),
                *ROOT.glob("tests/**/*.py"),
                *ROOT.glob("scripts/validation/*.py"),
                ROOT / "pyproject.toml",
                ROOT / "uv.lock",
                ROOT / "env/encoding-assets.lock.json",
            ]
        )
        manifest = []
        for path in files:
            rel = path.relative_to(ROOT)
            dest = out / "source-snapshot" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            manifest.append(
                dict(path=str(rel), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            )
        (out / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

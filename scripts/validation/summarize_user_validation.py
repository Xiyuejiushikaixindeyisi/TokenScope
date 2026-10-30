"""Capture exact local user-backend source/evidence identity; no release or package."""

import hashlib
import json
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from tokenscope.user_monitoring import contracts


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path(__file__).resolve().parents[2]
    evidence = root / "artifacts/validation/user-monitoring"
    report_path = evidence / "U005/http-5e7619f2/report.json"
    report = json.loads(report_path.read_text())
    assert report["passed"] and report["process_exit_recovery"]
    examples = []
    for item in report["models"]:
        for model, key in (
            ("Receipt", "receipt"),
            ("Ranking", "ranking"),
            ("Evaluation", "evaluation"),
        ):
            getattr(contracts, model).model_validate_json(json.dumps(item[key]))
            examples.append(dict(model=model, source="local_http_synthetic_csv", value=item[key]))
    destination = root / "docs/contracts/user-monitoring-v2/runtime.examples.json"
    destination.write_text(json.dumps(examples, ensure_ascii=False, indent=2) + "\n")
    test_results = {}
    for path in sorted(evidence.rglob("*.xml")):
        suite = ET.parse(path).getroot().find("testsuite")
        if suite is not None:
            test_results[str(path.relative_to(root))] = dict(suite.attrib) | {
                "sha256": digest(path)
            }
    assert test_results[str((evidence / "U005/full-final.xml").relative_to(root))]["tests"] == "289"
    assert (
        test_results[str((evidence / "U005/full-final.xml").relative_to(root))]["failures"] == "0"
    )
    files = set((root / "src/tokenscope").rglob("*.py"))
    for pattern in (
        "tests/**/test_user*.py",
        "tests/**/test_v2*.py",
        "scripts/validation/*user*.py",
        "docs/contracts/user-monitoring-v2/*.json",
    ):
        files.update(root.glob(pattern))
    files.update(
        root / name
        for name in (
            "pyproject.toml",
            "uv.lock",
            "env/encoding-assets.lock.json",
            "env/sources.lock.json",
            "src/tokenscope/api/monitoring_view_openapi.json",
        )
    )
    sources = {str(p.relative_to(root)): digest(p) for p in sorted(files) if p.is_file()}
    links = 0
    broken = []
    docs = list((root / "docs/tasks/monitoring/v2-user").rglob("*.md")) + [
        root / "docs/contracts/user-monitoring-v2/README.md"
    ]
    manifest_path = root / "docs/tasks/monitoring/v2-user/batches/U005/VALIDATION_MANIFEST.json"
    for path in docs:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (path.parent / target.split("#")[0]).resolve()
            if not resolved.exists() and resolved != manifest_path:
                broken.append((str(path.relative_to(root)), target))
            links += 1
    assert not broken, broken
    subprocess.run(["git", "diff", "--check"], cwd=root, check=True, capture_output=True)
    cpu = next(
        (
            line.split(":", 1)[1].strip()
            for line in Path("/proc/cpuinfo").read_text().splitlines()
            if line.startswith("model name")
        ),
        "unknown",
    )
    result = dict(
        backend_identity="u005-local-1",
        contract="1.0.1",
        index_algorithm="user-index-1",
        kind="local_worktree_not_release",
        python=sys.version,
        platform=platform.platform(),
        cpu=cpu,
        cpu_budget=8,
        batch_rows=256,
        batch_bytes=16 * 1024 * 1024,
        git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        git_branch=subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=root, text=True
        ).strip(),
        sources=sources,
        tests=test_results,
        checked_local_links=links,
        git_diff_check="passed",
        e2e={
            "path": str(report_path.relative_to(root)),
            "sha256": digest(report_path),
            "models": 3,
            "ma_joint": report["ma_joint"],
            "cross_process_worker_lock": True,
            "process_exit_recovery": report["process_exit_recovery"],
        },
        resources={
            name: json.loads((evidence / "resources" / name).read_text())
            for name in ("projection.json", "query.json")
        },
        pending=["frontend integration", "real TTFT calibration", "onsite/network validation"],
        deployed=False,
        packaged=False,
        git_commit_of_changes=False,
    )
    manifest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            dict(
                source_files=len(sources),
                checked_links=links,
                runtime_examples=len(examples),
                manifest=str(manifest_path.relative_to(root)),
            )
        )
    )


if __name__ == "__main__":
    main()

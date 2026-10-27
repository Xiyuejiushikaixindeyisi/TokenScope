"""Approval-gated final packaging. --check only inspects sources and never invokes Docker."""

import argparse
import json
import os
import re
import shutil
import subprocess
import tarfile
from pathlib import Path

from tokenscope import __version__
from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.encoding.assets import AssetRegistry
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.monitoring.rules import digest

ROOT = Path(__file__).resolve().parents[2]


def source_files(root: Path) -> list[Path]:
    paths = set()
    for pattern in (
        "src/**/*.py",
        "tests/**/*.py",
        "scripts/validation/*.py",
        "scripts/release/*.py",
    ):
        paths.update(root.glob(pattern))
    for name in (
        "pyproject.toml",
        "uv.lock",
        "env/requirements.runtime.txt",
        "env/encoding-assets.lock.json",
        "env/docker/Dockerfile.monitoring",
        "env/docker/compose.monitoring.yaml",
        "prompts/delivery/HUAWEI_MONITORING_V1.md",
        "docs/operations/MONITORING_LOCAL.md",
        "docs/contracts/MONITORING_IMPLEMENTED_API.md",
        "docs/contracts/schemas/monitoring-current.openapi.json",
        "docs/contracts/examples/monitoring-v1-executed-synthetic.json",
    ):
        paths.add(root / name)
    assets = json.loads((root / "env/encoding-assets.lock.json").read_text())
    for model in assets["models"]:
        for item in model["files"]:
            paths.add(root / item["path"])
    for path in paths:
        if (
            not path.is_file()
            or path.is_symlink()
            or not path.resolve().is_relative_to(root.resolve())
        ):
            raise ValueError("Invalid release source: " + str(path.relative_to(root)))
    return sorted(paths)


def preflight(root: Path = ROOT) -> dict:
    out = root / "artifacts/validation/monitoring/B005"
    gate_paths = sorted(out.glob("*-report.json"))
    e2e_paths = sorted(out.glob("*/report.json"))
    if not gate_paths or not e2e_paths:
        raise ValueError("B005 evidence is absent")
    gate, e2e = (json.loads(paths[-1].read_text()) for paths in (gate_paths, e2e_paths))
    if not gate["passed"] or not e2e["passed"] or not e2e["actual_process_kill_recovery"]:
        raise ValueError("B005 gate did not pass")
    manifest_path = out / "source-manifest.json"
    records = json.loads(manifest_path.read_text())
    recorded = {item["path"] for item in records}
    for path in [
        *root.glob("src/**/*.py"),
        *root.glob("tests/**/*.py"),
        *root.glob("scripts/validation/*.py"),
    ]:
        if str(path.relative_to(root)) not in recorded:
            raise ValueError("Untested source added after B005")
    for item in records:
        if file_digest(root / item["path"]) != item["sha256"]:
            raise ValueError("Source changed since B005 gate: " + item["path"])
    if not e2e.get("source_files_sha256"):
        raise ValueError("E2E source identity is missing")
    for name, checksum in e2e["source_files_sha256"].items():
        if file_digest(root / name) != checksum:
            raise ValueError("Source changed since E2E: " + name)
    registry = AssetRegistry(root)
    for model in DEFAULT_SETTINGS:
        registry.load(model)
    files = source_files(root)
    plan = dict(
        code_version=__version__,
        b005_manifest_sha256=file_digest(manifest_path),
        gate_report=str(gate_paths[-1].relative_to(root)),
        e2e_report=str(e2e_paths[-1].relative_to(root)),
        frontend_scope="monitoring_backend_only",
        docker_available=shutil.which("docker") is not None,
        files=[dict(path=str(p.relative_to(root)), sha256=file_digest(p)) for p in files],
    )
    plan["release_plan_sha256"] = digest(dict(files=plan["files"], scope=plan["frontend_scope"]))
    return plan


def validate_approval(approval: dict, plan: dict) -> None:
    if (
        approval.get("approved") is not True
        or approval.get("frontend_scope") != plan["frontend_scope"]
        or approval.get("b005_manifest_sha256") != plan["b005_manifest_sha256"]
        or approval.get("release_plan_sha256") != plan.get("release_plan_sha256")
        or not approval.get("user_message")
        or not approval.get("approved_at")
    ):
        raise ValueError(
            "New explicit user approval for this source and frontend scope is required"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--approval-file", type=Path)
    parser.add_argument(
        "--base-image", help="Python 3.11 linux/amd64 image pinned with @sha256:..."
    )
    parser.add_argument("--release-id")
    args = parser.parse_args()
    plan = preflight()
    if args.check:
        print(json.dumps(plan, indent=2))
        return 0
    if args.approval_file is None:
        raise ValueError("Packaging is not authorized: provide a new explicit approval record")
    approval = json.loads(args.approval_file.read_text())
    validate_approval(approval, plan)
    if not plan["docker_available"]:
        raise ValueError("Docker build environment is not installed/configured")
    if not args.base_image or not re.fullmatch(r"[^\s]+@sha256:[0-9a-f]{64}", args.base_image):
        raise ValueError("A verified immutable base-image digest is required")
    if not args.release_id or not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{1,100}", args.release_id):
        raise ValueError("A lowercase release id is required")
    if os.name != "posix":
        raise ValueError("Use the Linux/WSL build environment")
    output = ROOT / "artifacts/deliveries" / args.release_id
    output.mkdir(parents=True, exist_ok=False)
    context = output / "source"
    for item in plan["files"]:
        destination = context / item["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / item["path"], destination)
        if file_digest(destination) != item["sha256"]:
            raise ValueError("Source changed during snapshot")
    (context / "SOURCE_MANIFEST.json").write_text(json.dumps(plan, indent=2) + "\n")
    tag = "tokenscope-monitoring:" + args.release_id
    log = (output / "build.log").open("w")

    def run(command):
        subprocess.run(command, check=True, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)

    try:
        run(
            [
                "docker",
                "build",
                "--platform",
                "linux/amd64",
                "--build-arg",
                "BASE_IMAGE=" + args.base_image,
                "--build-arg",
                "RELEASE_ID=" + args.release_id,
                "--build-arg",
                "SOURCE_MANIFEST_SHA256=" + file_digest(context / "SOURCE_MANIFEST.json"),
                "-t",
                tag,
                "-f",
                str(context / "env/docker/Dockerfile.monitoring"),
                str(context),
            ]
        )
        run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--entrypoint",
                "python",
                tag,
                "-c",
                "import sys; assert sys.version_info[:2] == (3, 11); print(sys.version)",
            ]
        )
        validation = output / "container-validation"
        validation.mkdir()
        # Offline, read-only root, bounded CPU/RAM, actual HTTP/CLI/restart/kill E2E inside image.
        run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--read-only",
                "--cpus",
                "8",
                "--memory",
                "32g",
                "--user",
                f"{os.getuid()}:{os.getgid()}",
                "--tmpfs",
                "/tmp:size=536870912,mode=1777",
                "--mount",
                f"type=bind,source={validation},target=/app/artifacts/validation",
                "--entrypoint",
                "python",
                tag,
                "/app/scripts/validation/run_monitoring_e2e.py",
                "--mean-requests",
                "20",
                "--long-per-app",
                "1",
            ]
        )
        reports = list(validation.glob("monitoring/B005/*/report.json"))
        if not reports or not json.loads(reports[-1].read_text())["passed"]:
            raise ValueError("Container acceptance evidence missing")
        run(["docker", "save", "-o", str(output / "image.tar"), tag])
        with tarfile.open(output / "code.tar.gz", "x:gz") as archive:
            archive.add(context, arcname="TokenScope", recursive=True)
        shutil.copy2(
            context / "prompts/delivery/HUAWEI_MONITORING_V1.md", output / "AGENT_PROMPT.md"
        )
        shutil.copy2(context / "env/docker/compose.monitoring.yaml", output / "compose.yaml")
        image = json.loads(subprocess.check_output(["docker", "image", "inspect", tag], text=True))[
            0
        ]
        manifest = dict(
            release_id=args.release_id,
            code_version=__version__,
            schema_version=2,
            image_tag=tag,
            image_id=image["Id"],
            base_image=args.base_image,
            platform="linux/amd64",
            frontend_scope=plan["frontend_scope"],
            approval=approval,
            source_manifest_sha256=file_digest(context / "SOURCE_MANIFEST.json"),
            b005_gate=plan["gate_report"],
            b005_e2e=plan["e2e_report"],
            container_acceptance="passed_offline",
            target_acceptance="pending",
            files=[
                dict(path=p.name, sha256=file_digest(p), bytes=p.stat().st_size)
                for p in (
                    output / "image.tar",
                    output / "code.tar.gz",
                    output / "AGENT_PROMPT.md",
                    output / "compose.yaml",
                )
            ],
        )
        (output / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(output)
    finally:
        log.close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error)) from error

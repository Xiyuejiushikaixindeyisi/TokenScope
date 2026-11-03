"""Build an offline context from a fixed Git commit, never a shared dirty tree."""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--base-image", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--version-file", default="docs/tasks/analysis/VERSION_RV2_20261101.json")
    parser.add_argument("--onsite-prompt", default="prompts/delivery/HUAWEI_FULL_SERVICE_RV2.md")
    args = parser.parse_args()
    for name in (args.version_file, args.onsite_prompt):
        if Path(name).is_absolute() or ".." in Path(name).parts:
            parser.error("Version and prompt must be repository-relative paths")
    root = Path(__file__).resolve().parents[2]
    out = args.output.resolve()
    if not out.is_relative_to(root / "artifacts/builds"):
        parser.error("Build context must stay in project artifacts/builds")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]+", args.release_id):
        parser.error("Invalid release ID")
    if "@sha256:" not in args.base_image:
        parser.error("Base image must use a fixed digest")
    commit = subprocess.check_output(
        ["git", "rev-parse", args.source_commit + "^{commit}"], cwd=root, text=True
    ).strip()

    def blob(name):
        return subprocess.check_output(["git", "show", commit + ":" + name], cwd=root)

    tracked = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", commit], cwd=root, text=True
    ).splitlines()
    # Reject symlinks in selected source instead of interpreting their bytes as regular code.
    modes = subprocess.check_output(
        ["git", "ls-tree", "-r", commit], cwd=root, text=True
    ).splitlines()
    links = {line.split("\t", 1)[1] for line in modes if line.startswith("120000")}
    out.mkdir(parents=True, exist_ok=False)
    stage = out.with_name(out.name + "-frontend")
    stage.mkdir(exist_ok=False)
    for name in tracked:
        if name.startswith("apps/viewer/"):
            if name in links:
                raise ValueError("Source symlink: " + name)
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob(name))
    # Reuse the installed build tools, but require their lock to match the fixed source.
    assert (stage / "apps/viewer/package-lock.json").read_bytes() == (
        root / "apps/viewer/package-lock.json"
    ).read_bytes()
    (stage / "apps/viewer/node_modules").symlink_to(
        root / "apps/viewer/node_modules", target_is_directory=True
    )
    with (out.parent / (out.name + "-frontend-build.log")).open("w") as log:
        subprocess.run(
            ["npm", "run", "build"],
            cwd=stage / "apps/viewer",
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )
    files = [
        "pyproject.toml",
        "uv.lock",
        "env/requirements.runtime.txt",
        "env/encoding-assets.lock.json",
        "env/sources.lock.json",
        "scripts/validation/generate_monitoring_data.py",
        "scripts/release/verify_service.py",
        args.onsite_prompt,
        args.version_file,
    ]
    files += [p for p in tracked if p.startswith(("src/", "configs/", "deploy/monitoring/"))]
    for name in sorted(set(files)):
        if name in links:
            raise ValueError("Source symlink: " + name)
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob(name))
    shutil.copytree(stage / "apps/viewer/dist", out / "apps/viewer/dist")
    lock = json.loads((out / "env/encoding-assets.lock.json").read_text())
    for model in lock["models"]:
        for asset in model["files"]:
            source = root / asset["path"]
            assert not source.is_symlink() and digest(source) == asset["sha256"], asset["path"]
            target = out / asset["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    requirements = (out / "env/requirements.runtime.txt").read_text()
    allowed = set(re.findall(r"--hash=sha256:([0-9a-f]{64})", requirements))
    wheels = list(args.wheelhouse.glob("*.whl"))
    assert wheels, "No offline wheels"
    (out / "wheelhouse").mkdir()
    for wheel in wheels:
        assert not wheel.is_symlink() and digest(wheel) in allowed, wheel.name
        shutil.copyfile(wheel, out / "wheelhouse" / wheel.name)
    version = json.loads(blob(args.version_file))
    for name, sha in version["source_and_dependency_files"].items():
        assert hashlib.sha256(blob(name)).hexdigest() == sha, name
    candidate = {
        "release_id": args.release_id,
        "source_commit": commit,
        "version_file": args.version_file,
        "onsite_prompt": args.onsite_prompt,
        "base_image": args.base_image,
        "versions": {
            k: version[k]
            for k in ["version", "frontend", "public_backend", "token_private", "token_plugin"]
        },
        "source_identity_sha256": version["source_identity_sha256"],
        "monitoring_contracts": version.get(
            "monitoring_contracts", {"s0": "1.0.0", "user": "2.0.0", "ma": "1.0.0"}
        ),
        "control_schema": 3,
        "view_schema": "1",
        "frontend_built_from_commit": commit,
        "frontend_build_node": subprocess.check_output(["node", "--version"], text=True).strip(),
        "models": lock["models"],
        "files": {
            str(p.relative_to(out)): digest(p) for p in sorted(out.rglob("*")) if p.is_file()
        },
    }
    (out / "candidate.json").write_text(json.dumps(candidate, indent=2) + "\n")
    print(
        json.dumps({"context": str(out), "source_commit": commit, "files": len(candidate["files"])})
    )


if __name__ == "__main__":
    main()

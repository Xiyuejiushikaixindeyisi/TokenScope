"""Prepare an explicit offline full-service build context; never include runtime state."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--base-image", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    out = args.output.resolve()
    if not out.is_relative_to(root / "artifacts/builds"):
        parser.error("Build context must stay in project artifacts/builds")
    out.mkdir(parents=True, exist_ok=False)
    files = [
        "pyproject.toml",
        "uv.lock",
        "env/requirements.runtime.txt",
        "env/encoding-assets.lock.json",
        "deploy/monitoring/Dockerfile",
        "scripts/validation/generate_monitoring_data.py",
        "scripts/release/verify_service.py",
    ]
    tracked = subprocess.check_output(["git", "ls-files"], cwd=root, text=True).splitlines()
    files += [p for p in tracked if p.startswith(("src/", "configs/"))]
    files += [
        str(p.relative_to(root)) for p in (root / "apps/viewer/dist").rglob("*") if p.is_file()
    ]
    lock = json.loads((root / "env/encoding-assets.lock.json").read_text())
    for model in lock["models"]:
        for asset in model["files"]:
            assert (
                hashlib.sha256((root / asset["path"]).read_bytes()).hexdigest() == asset["sha256"]
            )
            files.append(asset["path"])
    for name in sorted(set(files)):
        src = root / name
        if src.is_symlink():
            raise ValueError("Do not dereference arbitrary context symlinks: " + name)
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
    shutil.copytree(args.wheelhouse, out / "wheelhouse")
    candidate = {
        "release_id": args.release_id,
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "base_image": args.base_image,
        "backend": "0.1.0.dev6",
        "frontend": "0.1.0-f007",
        "control_schema": 3,
        "view_schema": "1",
        "contract": "1.0.0",
        "files": {
            str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.rglob("*"))
            if p.is_file()
        },
    }
    (out / "candidate.json").write_text(json.dumps(candidate, indent=2) + "\n")
    print(json.dumps({"context": str(out), "files": len(candidate["files"])}))


if __name__ == "__main__":
    main()

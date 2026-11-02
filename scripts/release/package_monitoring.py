"""Archive a tested WSL Docker image and matching code; never push artifacts."""

import argparse
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import tarfile
from pathlib import Path


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument("--restart", type=Path, required=True)
    parser.add_argument("--browser-log", type=Path, required=True)
    parser.add_argument(
        "--validation",
        type=Path,
        required=True,
        help="Unified container validation bound to image and commit",
    )
    parser.add_argument("--backup-branch", required=True)
    parser.add_argument(
        "--acceptance-kit", type=Path, help="Optional synthetic-only onsite input kit"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    candidate = json.loads((args.context / "candidate.json").read_text())
    release_id = candidate["release_id"]
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]+", release_id):
        raise ValueError("Invalid release ID")
    initial = json.loads(args.acceptance.read_text())
    restart = json.loads(args.restart.read_text())
    assert initial["passed"] and restart["passed"] and restart["restart_verified"]
    assert initial["service_instance_id"] == restart["service_instance_id"]
    assert initial["scopes"] == restart["scopes"]
    browser_text = args.browser_log.read_text()
    assert re.search(r"[1-9][0-9]* passed", browser_text) and not re.search(
        r"[1-9][0-9]* failed", browser_text
    )
    assert args.backup_branch.startswith("backup/")
    validation = json.loads(args.validation.read_text())
    assert (
        validation["passed"] is True and validation["source_commit"] == candidate["source_commit"]
    )
    assert all(validation["checks"].values())
    for name, expected in candidate["files"].items():
        assert digest(args.context / name) == expected, name
    image = json.loads(subprocess.check_output(["docker", "image", "inspect", args.image]))[0]
    assert image["Os"] == "linux" and image["Architecture"] == "amd64"
    assert (
        image["Config"]["Labels"]["org.opencontainers.image.revision"] == candidate["source_commit"]
    )
    assert validation["image_id"] == image["Id"]
    assert image["Config"]["Labels"]["org.opencontainers.image.version"] == release_id
    out = root / "artifacts/releases" / release_id
    out.mkdir(parents=True, exist_ok=False)
    code_tar = out / (release_id + "-code.tar")
    subprocess.run(
        [
            "git",
            "archive",
            "--format=tar",
            "--prefix=TokenScope/",
            "-o",
            str(code_tar),
            candidate["source_commit"],
        ],
        cwd=root,
        check=True,
    )
    with tarfile.open(code_tar, "a") as archive:
        extras = ["models", "apps/viewer/dist", "wheelhouse", "candidate.json"]
        for name in extras:
            p = args.context / name
            entries = [p] if p.is_file() else sorted(q for q in p.rglob("*") if q.is_file())
            for entry in entries:
                assert not entry.is_symlink()
                archive.add(entry, arcname="TokenScope/" + str(entry.relative_to(args.context)))
    with tarfile.open(code_tar) as archive:
        members = archive.getmembers()
        assert len({m.name for m in members}) == len(members)
        assert all(
            not m.issym()
            and not m.islnk()
            and not m.name.startswith("/")
            and ".." not in Path(m.name).parts
            for m in members
        )
        for name, expected in candidate["files"].items():
            assert (
                hashlib.sha256(archive.extractfile("TokenScope/" + name).read()).hexdigest()
                == expected
            ), name
    code_gz = code_tar.with_suffix(".tar.gz")
    with code_tar.open("rb") as source, code_gz.open("wb") as target:
        with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as compressed:
            shutil.copyfileobj(source, compressed, 1024 * 1024)
    code_tar.unlink()
    image_gz = out / (release_id + "-image.tar.gz")
    with (out / "docker-save.log").open("wb") as log, image_gz.open("wb") as target:
        process = subprocess.Popen(
            ["docker", "save", args.image], stdout=subprocess.PIPE, stderr=log
        )
        with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as compressed:
            shutil.copyfileobj(process.stdout, compressed, 1024 * 1024)
        assert process.wait() == 0, "docker save failed; output is not a release"
    copies = {
        "compose.yaml": args.context / "deploy/monitoring/compose.yaml",
        "deployment.env.example": args.context / "deploy/monitoring/deployment.env.example",
        "HUAWEI_AGENT_PROMPT.md": args.context
        / candidate.get("onsite_prompt", "prompts/delivery/HUAWEI_FULL_SERVICE_RV2.md"),
        "DEPLOYMENT_README.md": args.context / "deploy/monitoring/README.md",
        "candidate.json": args.context / "candidate.json",
        "container-acceptance.json": args.acceptance,
        "container-restart.json": args.restart,
        "container-browser.log": args.browser_log,
        "unified-container-validation.json": args.validation,
    }
    if args.acceptance_kit:
        copies["SYNTHETIC_ACCEPTANCE.tar.gz"] = args.acceptance_kit
    for name, source in copies.items():
        shutil.copyfile(source, out / name)
    manifest = {
        **{k: v for k, v in candidate.items() if k != "files"},
        "image_tag": args.image,
        "image_id": image["Id"],
        "platform": "linux/amd64",
        "image_archive": image_gz.name,
        "code_archive": code_gz.name,
        "built_in": "WSL Ubuntu-22.04",
        "container_acceptance": "passed",
        "onsite_acceptance": "pending",
        "production_data_included": False,
        "files": {
            p.name: {"sha256": digest(p), "bytes": p.stat().st_size}
            for p in sorted(out.iterdir())
            if p.is_file()
        },
        "local_backup_branch": args.backup_branch,
        "desktop_destination": None,
    }
    (out / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    sums = "".join(f"{digest(p)}  {p.name}\n" for p in sorted(out.iterdir()) if p.is_file())
    (out / "SHA256SUMS").write_text(sums)
    print(
        json.dumps(
            {
                "release": str(out),
                "image_id": image["Id"],
                "source_commit": candidate["source_commit"],
            }
        )
    )


if __name__ == "__main__":
    main()

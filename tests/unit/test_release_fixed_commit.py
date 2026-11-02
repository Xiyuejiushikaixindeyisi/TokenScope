"""Release boundary checks use a real isolated Git repository and fake build tools."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("custom_metadata", [False, True])
def test_fixed_commit_ignores_dirty_source_and_dist(tmp_path, custom_metadata):
    root = tmp_path / "repo"
    root.mkdir()
    source = Path(__file__).resolve().parents[2]

    def put(name, data):
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data)
        return p

    script = put(
        "scripts/release/prepare_monitoring_context.py",
        (source / "scripts/release/prepare_monitoring_context.py").read_text(),
    )
    put("src/test.py", "fixed-source")
    put("apps/viewer/package-lock.json", "{}")
    put("apps/viewer/package.json", "{}")
    put("apps/viewer/src/main.ts", "fixed-frontend")
    for name in [
        "pyproject.toml",
        "uv.lock",
        "env/sources.lock.json",
        "deploy/monitoring/Dockerfile",
        "scripts/validation/generate_monitoring_data.py",
        "scripts/release/verify_service.py",
        "prompts/delivery/HUAWEI_FULL_SERVICE_RV2.md",
    ]:
        put(name, "fixed")
    put("env/encoding-assets.lock.json", '{"models":[]}')
    wheel = put("wheels/fixture.whl", "wheel")
    put(
        "env/requirements.runtime.txt",
        "--hash=sha256:" + hashlib.sha256(wheel.read_bytes()).hexdigest(),
    )
    version = {
        k: "fixture"
        for k in [
            "version",
            "frontend",
            "public_backend",
            "token_private",
            "token_plugin",
            "source_identity_sha256",
        ]
    }
    version["source_and_dependency_files"] = {
        "src/test.py": hashlib.sha256(b"fixed-source").hexdigest()
    }
    put("docs/tasks/analysis/VERSION_RV2_20261101.json", json.dumps(version))

    if custom_metadata:
        put(
            "docs/tasks/delivery/new-version.json",
            json.dumps({**version, "version": "new-version"}),
        )
        put("prompts/delivery/new-prompt.md", "new-prompt-fixed")

    def git(*args):
        return subprocess.check_output(
            ["git", *args], cwd=root, stderr=subprocess.STDOUT, text=True
        ).strip()

    git("init")
    git("add", ".")
    git(
        "-c",
        "user.name=Release Test",
        "-c",
        "user.email=release@example.invalid",
        "commit",
        "-m",
        "fixture",
    )
    commit = git("rev-parse", "HEAD")
    if custom_metadata:
        put("prompts/delivery/new-prompt.md", "UNCOMMITTED-prompt")
        put("docs/tasks/delivery/new-version.json", "UNCOMMITTED-version")
    put("src/test.py", "UNCOMMITTED-source")
    put("apps/viewer/src/main.ts", "UNCOMMITTED-frontend")
    put("apps/viewer/dist/index.html", "STALE-dist")
    (root / "apps/viewer/node_modules").mkdir()
    bin_dir = root / "fake-bin"
    npm = put(
        "fake-bin/npm",
        '#!/usr/bin/env python3\nfrom pathlib import Path\nPath("dist").mkdir()\n'
        'Path("dist/index.html").write_text(Path("src/main.ts").read_text())\n',
    )
    npm.chmod(0o755)
    node = put("fake-bin/node", "#!/bin/sh\necho v22.22.2\n")
    node.chmod(0o755)
    env = {**os.environ, "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]}
    out = root / "artifacts/builds/review/context"
    command = [
        sys.executable,
        str(script),
        "--output",
        str(out),
        "--wheelhouse",
        str(wheel.parent),
        "--release-id",
        "review-test",
        "--base-image",
        "python@sha256:" + "a" * 64,
        "--source-commit",
        commit,
    ]
    if custom_metadata:
        command += [
            "--version-file",
            "docs/tasks/delivery/new-version.json",
            "--onsite-prompt",
            "prompts/delivery/new-prompt.md",
        ]
    subprocess.run(command, cwd=root, env=env, check=True, capture_output=True)
    assert (out / "src/test.py").read_text() == "fixed-source"
    assert (out / "apps/viewer/dist/index.html").read_text() == "fixed-frontend"
    assert (root / "src/test.py").read_text() == "UNCOMMITTED-source"
    assert (root / "apps/viewer/dist/index.html").read_text() == "STALE-dist"
    candidate = json.loads((out / "candidate.json").read_text())
    assert candidate["source_commit"] == candidate["frontend_built_from_commit"] == commit
    if custom_metadata:
        assert candidate["versions"]["version"] == "new-version"
        assert (out / candidate["onsite_prompt"]).read_text() == "new-prompt-fixed"
        assert (root / "prompts/delivery/new-prompt.md").read_text() == "UNCOMMITTED-prompt"
    assert not (out / "wheels").exists()
    for file, expected in candidate["files"].items():
        assert hashlib.sha256((out / file).read_bytes()).hexdigest() == expected
    # Reject an unlocked wheel before making a usable candidate.
    wheel.write_text("changed-wheel")
    bad = root / "artifacts/builds/review/bad"
    command[command.index(str(out))] = str(bad)
    failed = subprocess.run(command, cwd=root, env=env, capture_output=True)
    assert failed.returncode != 0 and not (bad / "candidate.json").exists()
    shutil.rmtree(root / "fake-bin")

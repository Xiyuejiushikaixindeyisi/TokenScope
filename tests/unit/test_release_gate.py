import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "release_builder", ROOT / "scripts/release/build_monitoring.py"
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def test_missing_or_stale_approval_cannot_build():
    plan = dict(
        frontend_scope="monitoring_backend_only",
        b005_manifest_sha256="a" * 64,
        release_plan_sha256="c" * 64,
    )
    for approval in [
        {},
        {"approved": True},
        dict(
            approved=True,
            user_message="yes",
            approved_at="now",
            frontend_scope="monitoring_backend_only",
            b005_manifest_sha256="b" * 64,
        ),
    ]:
        with pytest.raises(ValueError, match="approval"):
            builder.validate_approval(approval, plan)
    builder.validate_approval(
        dict(
            approved=True,
            user_message="explicit test only",
            approved_at="test",
            frontend_scope="monitoring_backend_only",
            b005_manifest_sha256="a" * 64,
            release_plan_sha256="c" * 64,
        ),
        plan,
    )


def test_source_allowlist_excludes_inputs_state_and_frontend():
    files = builder.source_files(ROOT)
    relative = [str(path.relative_to(ROOT)) for path in files]
    assert any(p.startswith("models/") for p in relative)
    assert any(p.startswith("src/") for p in relative)
    assert not any(
        p.startswith(("data/", "artifacts/", "apps/", "upstream/", ".venv/")) for p in relative
    )
    assert not any("gf-20261027" in p for p in relative)


def test_check_mode_and_denial_never_invoke_docker(monkeypatch, capsys):
    monkeypatch.setattr(
        builder,
        "preflight",
        lambda: dict(
            frontend_scope="monitoring_backend_only",
            b005_manifest_sha256="a" * 64,
            docker_available=False,
        ),
    )
    monkeypatch.setattr(builder.subprocess, "run", lambda *a, **kw: pytest.fail("Docker invoked"))
    monkeypatch.setattr("sys.argv", ["build_monitoring.py", "--check"])
    assert builder.main() == 0
    assert "monitoring_backend_only" in capsys.readouterr().out
    monkeypatch.setattr("sys.argv", ["build_monitoring.py"])
    with pytest.raises(ValueError, match="not authorized"):
        builder.main()

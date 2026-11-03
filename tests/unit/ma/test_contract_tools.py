"""Mutation checks for frozen MA compatibility and complete extension checking."""

import copy
import hashlib
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def tools(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts/contracts"))
    return (
        importlib.import_module("validate_ma_contract"),
        importlib.import_module("validate_ma_availability"),
    )


def test_current_contracts_readonly(tools):
    old, extension = tools
    paths = [*old.DEST.glob("*.json"), *extension.DEST.glob("*.json")]
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    old.validate_frozen_identity()
    runtime = old.artifacts()
    old.validate_legacy(runtime)
    extension.validate_extension(runtime["design.openapi.json"])
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


@pytest.mark.parametrize("area", ["schema", "path", "component", "metadata"])
def test_reject_old_contract_drift(tools, area):
    old, _ = tools
    runtime = copy.deepcopy(old.artifacts())
    spec = runtime["design.openapi.json"]
    if area == "schema":
        runtime["schema.json"]["Submit"]["additionalProperties"] = True
    elif area == "path":
        del spec["paths"]["/monitoring/ma/catalog"]["get"]["responses"]["200"]
    elif area == "component":
        spec["components"]["schemas"]["Submit"]["additionalProperties"] = True
    else:
        spec["info"]["version"] = "changed"
    with pytest.raises(AssertionError):
        old.validate_legacy(runtime)


@pytest.mark.parametrize(
    "area", ["route", "dto", "sample_value", "sample_missing", "unexpected_route"]
)
def test_reject_extension_drift(tools, tmp_path, area):
    old, ext = tools
    for p in ext.DEST.glob("*.json"):
        shutil.copyfile(p, tmp_path / p.name)
    runtime = old.artifacts()["design.openapi.json"]
    filename = (
        "candidate.openapi.json"
        if area in ("route", "unexpected_route")
        else ("schema.json" if area == "dto" else "examples.json")
    )
    p = tmp_path / filename
    value = json.loads(p.read_text())
    if area == "route":
        value["paths"][ext.EXTENSION_PATH]["get"]["responses"]["200"]["description"] = "changed"
    elif area == "unexpected_route":
        value["paths"]["/monitoring/ma/unreviewed"] = {"get": {}}
        runtime = value  # even mutually matching runtime/candidate must reject undeclared route
    elif area == "dto":
        value["additionalProperties"] = True
    elif area == "sample_missing":
        value["cases"].pop()
    else:
        value["cases"][0]["response"]["availability"]["metrics"]["independent_ideal_hit_rate"][
            "numerator"
        ] = "0"
    p.write_text(json.dumps(value))
    with pytest.raises(AssertionError):
        ext.validate_extension(runtime, tmp_path)


@pytest.mark.parametrize("target", ["manifest", "frozen_bytes"])
def test_frozen_identity_cannot_be_regenerated_away(tools, tmp_path, target):
    old, _ = tools
    dest = tmp_path / "docs/contracts/ma-monitoring-v2"
    dest.mkdir(parents=True)
    manifest = json.loads((old.DEST / "manifest.json").read_text())
    shutil.copyfile(old.DEST / "manifest.json", dest / "manifest.json")
    for name in manifest:
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, p)
    if target == "manifest":
        (dest / "manifest.json").write_text(json.dumps(manifest))
    else:
        with (dest / "examples.json").open("ab") as stream:
            stream.write(b" ")
    with pytest.raises(AssertionError):
        old.validate_frozen_identity(tmp_path, dest)


def test_write_flag_refuses_frozen_changes(tools):
    old, _ = tools
    before = {p: p.read_bytes() for p in old.DEST.glob("*.json")}
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/contracts/validate_ma_contract.py"), "--write"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 2 and "frozen" in result.stderr
    assert before == {p: p.read_bytes() for p in old.DEST.glob("*.json")}

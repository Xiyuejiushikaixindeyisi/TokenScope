"""Generate/check MA-only protocol artifacts; never installs production routes."""

import argparse
import hashlib
import json
from pathlib import Path

from fastapi import FastAPI
from pydantic import ValidationError

from tokenscope.monitoring.ma import contracts as c

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "docs/contracts/ma-monitoring-v2"
MODELS = (c.Submit, c.Receipt, c.Catalog, c.Snapshot, c.QualityPage, c.ErrorEnvelope)


def artifacts() -> dict[str, object]:
    app = FastAPI(title="MA monitoring design contract", version="1.0.0")
    from typing import cast

    from tokenscope.api.ma import router
    from tokenscope.monitoring.ma.service import MaService

    app.include_router(router(cast(MaService, None)))
    spec = app.openapi()
    spec["x-status"] = "runtime-route-signatures; no service execution during generation"
    schema = {m.__name__: m.model_json_schema() for m in MODELS}
    return {"schema.json": schema, "design.openapi.json": spec}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        parser.error("MA 1.0.0 is frozen; --write cannot overwrite its artifacts or manifest")
    validate_frozen_identity()
    runtime = artifacts()
    validate_legacy(runtime)
    from validate_ma_availability import validate_extension

    validate_extension(runtime["design.openapi.json"])
    payload = dict(
        submission_key="example",
        pre_file_ref="pre.csv",
        now_file_ref="now.csv",
        model_standard_name="Qwen-64K",
        model_id="Qwen3.6-27B",
        pre_start="2026-10-20T07:00:00Z",
        now_start="2026-10-20T08:00:00Z",
        now_end="2026-10-20T09:00:00Z",
    )
    examples = {
        "submit": payload,
        "empty_catalog": dict(
            service_instance_id="service-1",
            catalog_revision="0",
            total="0",
            next_offset=None,
            entries=[],
        ),
    }
    c.Submit.model_validate(payload)
    c.Catalog.model_validate(examples["empty_catalog"])
    rejected = 0
    for change in (
        {"now_end": "2026-10-20T10:00:00Z"},
        {"now_file_ref": "pre.csv"},
        {"source_timezone": "Asia/Shanghai"},
        {"unknown": True},
    ):
        try:
            c.Submit.model_validate({**payload, **change})
        except ValidationError:
            rejected += 1
    assert rejected == 4
    frontend = DEST / "frontend.examples.json"
    if frontend.exists():
        for example in json.loads(frontend.read_text())["examples"]:
            getattr(c, example["type"]).model_validate(example["payload"])
    for name, sha in json.loads((DEST / "manifest.json").read_text()).items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, name
    print("MA frozen compatibility + candidate extension valid; 2 positive, 4 negative submissions")


def validate_legacy(runtime: dict[str, object], destination: Path = DEST) -> None:
    schema = json.loads((destination / "schema.json").read_text())
    assert runtime["schema.json"] == schema, "Frozen MA schema changed"
    old = json.loads((destination / "design.openapi.json").read_text())
    new = runtime["design.openapi.json"]
    assert isinstance(new, dict)
    for key in old.keys() - {"paths", "components"}:
        assert new[key] == old[key], f"Frozen OpenAPI metadata changed: {key}"
    for path, operations in old["paths"].items():
        assert new["paths"][path] == operations, f"Frozen path changed: {path}"
    for group, definitions in old["components"].items():
        for name, definition in definitions.items():
            assert new["components"][group][name] == definition, f"Frozen component changed: {name}"


def validate_frozen_identity(root: Path = ROOT, destination: Path = DEST) -> None:
    manifest = destination / "manifest.json"
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == (
        "b29e3edfac5ce5fc6cf9d46f11df0b0cbd71b1738bb898ef3b423c309faa81e9"
    ), "Frozen manifest identity changed"
    for name, sha in json.loads(manifest.read_text()).items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == sha, name


if __name__ == "__main__":
    main()

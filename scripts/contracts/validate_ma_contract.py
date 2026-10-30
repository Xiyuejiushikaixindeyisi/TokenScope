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
    for name, value in artifacts().items():
        text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        path = DEST / name
        if args.write:
            path.write_text(text)
        elif path.read_text() != text:
            raise SystemExit(f"Stale protocol artifact: {name}")
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
    if args.write:
        (DEST / "examples.json").write_text(json.dumps(examples, indent=2) + "\n")
        files = [*DEST.glob("*.json"), ROOT / "src/tokenscope/monitoring/ma/contracts.py"]
        manifest = {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files
            if p.name != "manifest.json"
        }
        (DEST / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    else:
        for name, sha in json.loads((DEST / "manifest.json").read_text()).items():
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, name
    print("MA schema/artifacts valid; 2 positive examples, 4 negative submissions")


if __name__ == "__main__":
    main()

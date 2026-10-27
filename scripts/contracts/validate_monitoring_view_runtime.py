"""Validate captured actual responses against unchanged S0, independently of runtime DTO code."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]


def main():
    fixed = json.loads((ROOT / "docs/tasks/monitoring/batches/B005.1/S0_MANIFEST.json").read_text())
    for entry in fixed["files"]:
        assert hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest() == entry["sha256"], (
            entry["path"]
        )
    schema = json.loads(
        (ROOT / "docs/contracts/schemas/monitoring-view-v1.schema.json").read_text()
    )
    folder = ROOT / "artifacts/validation/monitoring/B005.1"
    values = [(folder / "S3/snapshot.json", "ViewSnapshot")]
    values += [(p, p.stem.split("-")[0]) for p in (folder / "S4/actual").glob("*.json")]
    results = []
    for path, name in values:
        Draft202012Validator(
            {"$defs": schema["$defs"], "$ref": "#/$defs/" + name}, format_checker=FormatChecker()
        ).validate(json.loads(path.read_text()))
        results.append(
            dict(
                path=str(path.relative_to(ROOT)),
                schema=name,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        )
    (folder / "runtime-contract-check.json").write_text(
        json.dumps(
            dict(passed=True, frozen_files=len(fixed["files"]), actual_responses=results), indent=2
        )
        + "\n"
    )
    print(f"PASS: {len(fixed['files'])} frozen files, {len(results)} actual responses")


if __name__ == "__main__":
    main()

"""Regenerate the HTTP layer schemas without touching frozen analysis-common-1.0."""

import hashlib
import json
from pathlib import Path

from tokenscope.analysis_common.wire import wire_schema
from tokenscope.api.diagnostics import (
    Authorization,
    Combination,
    LowHitEvaluation,
    Retry,
    Submission,
    TokenEvaluation,
)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    directory = root / "docs/contracts/diagnostics-http-1"
    directory.mkdir(parents=True, exist_ok=True)
    models = (Submission, Retry, TokenEvaluation, LowHitEvaluation, Combination, Authorization)
    payload = {
        "version": "diagnostics-http-1",
        "analysis_contract": "analysis-common-1.0",
        "models": {model.__name__: wire_schema(model) for model in models},
    }
    raw = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    (directory / "wire.json").write_bytes(raw)
    files = [
        root / "src/tokenscope/api/diagnostics.py",
        root / "src/tokenscope/analysis_common/runtime.py",
        directory / "wire.json",
    ]
    manifest = {
        "version": "diagnostics-http-1",
        "files": {
            path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files
        },
    }
    (directory / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    main()

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


def test_frozen_http_schema_and_implementation_manifest():
    root = Path(__file__).resolve().parents[3]
    directory = root / "docs/contracts/diagnostics-http-1"
    payload = json.loads((directory / "wire.json").read_bytes())
    for model in (Submission, Retry, TokenEvaluation, LowHitEvaluation, Combination, Authorization):
        assert payload["models"][model.__name__] == wire_schema(model)
    manifest = json.loads((directory / "manifest.json").read_bytes())
    for path, digest in manifest["files"].items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest

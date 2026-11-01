"""Freeze readonly payload views separately from adapter input schemas."""

import hashlib
import json
from pathlib import Path

from tokenscope.analysis_common.recommendation_store import EXTENSION_MODELS
from tokenscope.analysis_common.recommendation_views import recommendation_view_schema
from tokenscope.analysis_common.recommendations import VERSION
from tokenscope.analysis_common.wire import wire_schema

root = Path("docs/contracts/analysis-recommendations-1")
payload = {
    "version": VERSION,
    "models": {
        **{name: wire_schema(model) for name, model in EXTENSION_MODELS.items()},
        "recommendation": recommendation_view_schema(),
    },
}
data = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
(root / "public-views.json").write_bytes(data)
manifest = {
    "version": VERSION,
    "files": {"public-views.json": hashlib.sha256(data).hexdigest()},
    "note": "Public GET recipe summaries omit private selector/generator/basis scope JSON.",
}
(root / "http-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

"""Export only the independent discovery v1 contract, never rewrite frozen H0/HTTP v1."""

import hashlib
import json
from pathlib import Path

from tokenscope.analysis_common.discovery_contracts import schemas

root = Path(__file__).resolve().parents[1]
destination = root / "docs/contracts/diagnostics-discovery-1"
destination.mkdir(parents=True, exist_ok=True)
wire = destination / "wire.json"
wire.write_text(json.dumps(schemas(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
paths = [
    wire.relative_to(root).as_posix(),
    "src/tokenscope/analysis_common/discovery.py",
    "src/tokenscope/analysis_common/discovery_contracts.py",
    "src/tokenscope/api/diagnostic_discovery.py",
    "src/tokenscope/analysis_common/storage.py",
]
(destination / "manifest.json").write_text(
    json.dumps(
        {
            "version": "diagnostics-discovery-1",
            "identity_kind": "local_worktree_not_deployment",
            "files": {
                path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths
            },
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)

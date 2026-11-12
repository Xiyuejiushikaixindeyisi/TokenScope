"""Export the separate V3 sample report schema, without changing older contracts."""

import argparse
import hashlib
import json
from pathlib import Path

from tokenscope.analysis_common.execution_v3 import Execution3
from tokenscope.analysis_common.report_v3 import SampleReport3
from tokenscope.analysis_common.sample_evidence_v3 import EvidenceBundle3
from tokenscope.analysis_common.wire_v3 import wire_schema

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
data = (
    json.dumps(
        {
            "SampleReport3": wire_schema(SampleReport3),
            "Execution3": wire_schema(Execution3),
            "EvidenceBundle3": wire_schema(EvidenceBundle3),
        },
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )
    + "\n"
)
digest = hashlib.sha256(data.encode()).hexdigest()
for name in (
    "docs/contracts/diagnostics-report-3/wire.json",
    "apps/viewer/src/api/analysis/generated/diagnostics-report-3.json",
):
    path = root / name
    if args.check:
        assert path.read_text() == data, name
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)
lock = root / "docs/contracts/diagnostics-report-3/manifest.json"
value = json.dumps({"version": "diagnostics-report-3", "sha256": digest}, indent=2) + "\n"
if args.check:
    assert lock.read_text() == value
else:
    lock.write_text(value)
print(digest)

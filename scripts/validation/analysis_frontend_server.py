"""Isolated local frontend acceptance server; actual backend with synthetic input.
No production data, no automatic worker, no changes to backend implementation.
"""
from pathlib import Path
import sys
import json
import os
import uvicorn
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "tests/integration/analysis")]
from test_diagnostic_tasks import setup, options
from tokenscope.monitoring.service import MonitoringService
from tokenscope.api.app import create_app
from tokenscope.analysis_common.wire import to_wire

root = ROOT / "artifacts/validation/viewer/analysis/AF006/local-server"
root.mkdir(parents=True, exist_ok=True)
inputs = root / "inputs"
inputs.mkdir(exist_ok=True)
service = MonitoringService(inputs, root / "state")
# Seed only the dedicated acceptance state. Subsequent launches reuse sealed results.
marker = root / "receipt.json"
if not marker.exists():
    diagnostics, request = setup(service, True)
    receipt = diagnostics.submit(request, options(candidate_limit=128))
    result = diagnostics.process_next()
    marker.write_text(json.dumps({"synthetic": True, "receipt": to_wire(result), "source": "tests/integration/analysis/test_diagnostic_tasks.py:setup"}, indent=2))
app = create_app(service, start_worker=False, viewer_root=ROOT / "apps/viewer/dist")
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("TOKENSCOPE_FRONTEND_ACCEPTANCE_PORT", "8139")), access_log=False)

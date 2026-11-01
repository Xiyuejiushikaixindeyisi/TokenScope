"""CLI synthetic calibration; fresh process per case, no real data or model inference."""

import argparse
import json
import platform
import resource
import time

from tokenscope.analysis_common.contracts import BaselineMetrics, RequestKey, RequestView
from tokenscope.analysis_common.plugins import (
    BudgetSpec,
    EvidenceCapabilities,
    PluginSelection,
    RunControl,
)
from tokenscope.token_content.json_values import digest
from tokenscope.token_content.plugin import TokenContentPlugin


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, required=True)
    parser.add_argument("--payload-bytes", type=int, required=True)
    parser.add_argument("--copies", type=int, default=2)
    args = parser.parse_args()
    budget = BudgetSpec(
        max_request_bytes=1048576,
        max_units=10000,
        max_comparison_bytes=8388608,
        max_depth=64,
        max_candidates=1000,
        max_encoding_calls=100,
    )
    plugin = TokenContentPlugin()
    selection = PluginSelection(rule_ids=("T1", "T2", "T3", "T4"), budget=budget)
    raw = json.dumps(
        {
            "messages": [
                {"role": "tool" if index == 0 else "user", "content": "x" * args.payload_bytes}
                for index in range(args.copies)
            ]
        }
    )
    started = time.perf_counter()
    last = None
    for index in range(args.requests):
        request = RequestView(
            request_key=RequestKey(base_run_id="synthetic-benchmark", source_record_index=index),
            scope_id="synthetic-scope",
            appid="synthetic-app",
            time_ns=index,
            hash_id="not-identity",
            raw_body=raw,
            raw_sha256=digest(raw),
            raw_body_complete=True,
            baseline_metrics=BaselineMetrics(j=0, p=0),
            encoder_identity="not-encoded",
            asset_identity="not-encoded",
            effective_options_json="{}",
        )
        last = plugin.analyze_request(
            request, selection, EvidenceCapabilities(), RunControl(budget)
        )
        assert last.coverage.complete, last.reason_codes
    elapsed = time.perf_counter() - started
    assert last is not None
    print(
        json.dumps(
            {
                "scenario": vars(args),
                "raw_bytes_per_request": len(raw.encode()),
                "units_per_request": len(last.units),
                "observations_per_request": len(last.observations),
                "wall_seconds": elapsed,
                "process_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "platform": platform.platform(),
                "python": platform.python_version(),
                "plugin": plugin.describe().model_dump(),
                "budget": budget.model_dump(),
                "low_hit_wait_seconds": 0,
                "encoding_calls": 0,
                "source": "synthetic-not-model-token-counts",
            }
        )
    )


if __name__ == "__main__":
    main()

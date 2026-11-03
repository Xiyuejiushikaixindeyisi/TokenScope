"""Interleaved isolated extraction comparison, no source rewrites."""

import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

from profile_hv2 import bodies
from test_extraction import control, view

from tokenscope.analysis_common.plugins import EvidenceCapabilities
from tokenscope.token_content.extraction import extract


def main():
    namespaces = {}
    for name in ("measurements", "extraction"):
        ns = {"__name__": "tokenscope.token_content." + name}
        raw = subprocess.check_output(
            [
                "git",
                "show",
                "7cbe28621f4e46083bf47f9aa14b011b3cb250c4:src/tokenscope/token_content/"
                + name
                + ".py",
            ]
        )
        exec(compile(raw, "baseline-" + name, "exec"), ns)
        namespaces[name] = ns
    namespaces["extraction"]["measure"] = namespaces["measurements"]["measure"]
    old = namespaces["extraction"]["extract"]
    result = {}
    for name, body in bodies().items():
        request = view(body)
        a = old(request, EvidenceCapabilities(), control(max_units=3000))
        b = extract(request, EvidenceCapabilities(), control(max_units=3000))
        # Baseline dataclass is a separate type: compare its field content explicitly.
        assert a.local_errors == b.local_errors
        assert [(e.location, e.unit, e.value, e.measures) for e in a.entries] == [
            (e.location, e.unit, e.value, e.measures) for e in b.entries
        ]
        times = {"baseline": [], "optimized": []}
        cpu = {"baseline": [], "optimized": []}
        for i in range(30):
            pair = [("baseline", old), ("optimized", extract)]
            if i % 2:
                pair.reverse()
            for label, fn in pair:
                t = time.perf_counter_ns()
                c = time.process_time_ns()
                fn(request, EvidenceCapabilities(), control(max_units=3000))
                times[label].append(time.perf_counter_ns() - t)
                cpu[label].append(time.process_time_ns() - c)
        result[name] = {
            "wall_ns": times,
            "cpu_ns": cpu,
            "median_wall_ns": {k: statistics.median(v) for k, v in times.items()},
            "identical_inventory": True,
        }
    Path(sys.argv[1]).write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v["median_wall_ns"] for k, v in result.items()}))


if __name__ == "__main__":
    main()

"""Independently check recorded real resource runs against the approved bounded-work gates."""

import argparse
import json
from pathlib import Path

from v3_repair_e2e import save

from tokenscope.analysis_common.execution_v3 import calibrated_sample
from tokenscope.analysis_common.runtime_v3 import RuntimeProfile3


def verify(folder):
    measurements = []
    for name in ("DS1200", "DS12000", "QW1200", "QW12000"):

        def read(kind, name=name):
            return json.loads((folder / (name + "-" + kind + ".json")).read_text())

        prep, execution, report, manifest = (
            read("preparation"),
            read("execution"),
            read("report"),
            read("manifest"),
        )
        profile = RuntimeProfile3.model_validate(read("profile"))
        assert profile.deadline_ms is None and not profile.phase_deadlines_ms
        assert profile.address_space_bytes == 2 * 1024**3 * 65 // 100
        for run in (prep, execution):
            assert (
                run["state"] == "completed"
                and not run["forced_termination"]
                and run["exit_code"] == 0
            )
            assert run["telemetry"]["telemetry"]["hard_control"] == "RLIMIT_AS"
        calibration = prep["telemetry"]["calibration"]
        expected = calibrated_sample(profile, calibration["peak_virtual_bytes"])
        assert expected.model_dump(mode="json") == manifest["decision"]["limits"]
        assert not prep["telemetry"]["attempts"]
        decision = manifest["decision"]
        selected = sum(len(w["members"]) for w in decision["windows"])
        tokens = sum(w["prompt_tokens"] for w in decision["windows"])
        raw = manifest["selected_raw_bytes"]
        assert decision["parent_count"] == int(name[2:])
        assert 0 < selected <= expected.max_requests and selected < decision["parent_count"]
        assert raw <= expected.max_raw_bytes and tokens <= expected.max_prompt_tokens
        assert report["discovery"]["complete"]
        assert len(report["recommendations"]) == 1
        rec = report["recommendations"][0]
        assert rec["finding"]["rule_version"] == "clock-3.1"
        assert len(rec["windows"]) == 1 and rec["windows"][0]["complete"]
        c = execution["telemetry"]["telemetry"]["consumed"]
        # One baseline plus one all-member clock replay; no parent-sized encoding.
        assert c["encoding_calls"] == selected * 2
        assert c["requests"] <= selected * 8 and c["raw_read_bytes"] <= raw * 8
        assert c["comparisons"] <= selected * 16
        measurements.append(
            {
                "case": name,
                "parent": decision["parent_count"],
                "selected": selected,
                "raw": raw,
                "tokens": tokens,
                "address_limit": profile.address_space_bytes,
                "calibration_peak": calibration["peak_virtual_bytes"],
                "asset": calibration["asset_identity"],
                "prepare_peak_rss": prep["telemetry"]["supervisor_peak_rss_bytes"],
                "diagnose_peak_rss": execution["telemetry"]["supervisor_peak_rss_bytes"],
                "counters": c,
            }
        )
    for i in (0, 2):
        a, b = measurements[i : i + 2]
        assert b["parent"] == 10 * a["parent"] and a["asset"] == b["asset"]
        assert a["address_limit"] == b["address_limit"]
        # Same request shape/distribution, allowing adaptive native-overhead calibration.
        assert a["raw"] * b["selected"] == b["raw"] * a["selected"]
        assert a["tokens"] * b["selected"] == b["tokens"] * a["selected"]
        for key in ("prepare_peak_rss", "diagnose_peak_rss"):
            assert b[key] < a[key] * 2
        for key in ("requests", "raw_read_bytes", "encoding_calls", "comparisons"):
            assert b["counters"][key] < a["counters"][key] * 2
    return measurements


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    evidence, out = args.evidence.resolve(), args.output.resolve()
    project = Path(__file__).resolve().parents[2]
    assert all(
        p.is_relative_to(project / "artifacts/validation/development-v3") for p in (evidence, out)
    )
    out.mkdir(parents=True, exist_ok=False)
    measurements = verify(evidence)
    save(
        out / "PASS.json",
        {
            "evidence": str(evidence),
            "measurements": measurements,
            "gate": "bounded sample materialization and RSS under 10x parent size",
            "equal_sample_count_required": False,
            "actual_rlimit": True,
            "cgroup_test": False,
        },
    )
    print(json.dumps(measurements, ensure_ascii=False))


if __name__ == "__main__":
    main()

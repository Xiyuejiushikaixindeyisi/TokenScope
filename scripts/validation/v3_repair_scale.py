"""Long-source actual monitoring -> automatic small sample -> complete replay probe."""

import argparse
import csv
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from v3_repair_e2e import request, run_case, save
from v3_repair_fixtures import GROUPS, make_request

from tokenscope.ingestion.csv_reader import REQUIRED_COLUMNS
from tokenscope.monitoring.pipeline import file_digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("server_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root, output = args.server_root.resolve(), args.output.resolve()
    project = Path(__file__).resolve().parents[2]
    assert root.is_relative_to(project / "artifacts/validation/development-v3")
    assert output.is_relative_to(project / "artifacts/validation/development-v3")
    output.mkdir(parents=True, exist_ok=False)
    instance = request("/diagnostics/v3/capabilities")["service_instance_id"]
    measurements = []
    for group in (GROUPS[0], GROUPS[4]):
        for count in (1200, 12000):
            name = ("DS" if group[0] == "BUS01" else "QW") + str(count)
            filename = "synthetic-scale-" + name + ".csv"
            case = {
                "group": name,
                "appid": "synthetic-scale-" + name,
                "model": group[2],
                "file": filename,
            }
            payloads = [
                json.dumps(make_request(group, i), ensure_ascii=False, separators=(",", ":"))
                for i in (0, 1)
            ]
            path = root / "inputs" / filename
            with path.open("x", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(REQUIRED_COLUMNS)
                for i in range(count):
                    stamp = datetime(2026, 11, 11, tzinfo=UTC) + timedelta(seconds=i)
                    writer.writerow(
                        [
                            f"synthetic-{name}-{i}",
                            case["appid"],
                            stamp.isoformat(),
                            12,
                            payloads[i % 2],
                        ]
                    )
            save(
                output / (name + "-input.json"),
                {
                    "count": count,
                    "sha256": file_digest(path),
                    "bytes": path.stat().st_size,
                    "request_bytes": [len(p.encode()) for p in payloads],
                    "system_characters": group[3],
                    "tools": group[5],
                    "synthetic": True,
                },
            )
            print(name, "monitoring and sample starting", flush=True)
            run_case(output, case, instance)
            report = json.loads((output / (name + "-report.json")).read_text())
            execution = json.loads((output / (name + "-execution.json")).read_text())
            prep = json.loads((output / (name + "-preparation.json")).read_text())
            decision = report["sample"]["decision"]
            selected = sum(len(w["members"]) for w in decision["windows"])
            assert int(decision["parent_count"]) == count
            assert 0 < selected < count and selected <= 300
            assert all(w["complete"] for r in report["recommendations"] for w in r["windows"])
            measurements.append(
                {
                    "case": name,
                    "parent": count,
                    "selected": selected,
                    "raw_bytes": report["sample"]["selected_raw_bytes"],
                    "tokens": sum(int(w["prompt_tokens"]) for w in decision["windows"]),
                    "prepare_peak_rss": prep["telemetry"]["supervisor_peak_rss_bytes"],
                    "diagnose_peak_rss": execution["telemetry"]["supervisor_peak_rss_bytes"],
                    "counters": execution["telemetry"]["telemetry"]["consumed"],
                }
            )
            print(measurements[-1], flush=True)
    # Host availability changes between cases. Equal-condition assertions belong to
    # v3_repair_memory.py, which replays these sealed sources with one fixed envelope.
    save(
        output / "PASS.json",
        {
            "measurements": measurements,
            "time_limit_installed": False,
            "scope": "four automatic-admission cases only",
            "equal_memory_comparison": "REQUIRES_CONTROLLED_REPLAY",
        },
    )


if __name__ == "__main__":
    main()

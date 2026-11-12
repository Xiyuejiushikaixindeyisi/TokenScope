"""Real negative/L5/cancelled reports for local manual review, not mock metrics."""

import argparse
import csv
import json
import time
from pathlib import Path

from v3_repair_e2e import request, save, wait
from v3_repair_fixtures import GROUPS, make_request

from tokenscope.ingestion.csv_reader import REQUIRED_COLUMNS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.output.resolve()
    assert out.is_relative_to(
        Path(__file__).resolve().parents[2] / "artifacts/validation/development-v3"
    )
    out.mkdir(parents=True, exist_ok=False)
    instance = request("/diagnostics/v3/capabilities")["service_instance_id"]
    for name in ("synthetic-constant-clock", "synthetic-l5-large-int", "synthetic-cancelled"):
        rows = []
        for i in range(8):
            body = make_request(GROUPS[0], 6 if "l5" in name else i if "cancelled" in name else 0)
            if "l5" in name:
                tool = next(m for m in body["messages"] if m["role"] == "tool")
                tool["content"] = (
                    '{"id":900719925474099312345,"ok":true}'
                    if i % 2
                    else '{ "id": 900719925474099312345, "ok": true }'
                )
            rows.append(
                [
                    name + str(i),
                    name,
                    f"2026-11-11T01:00:{i:02d}Z",
                    12,
                    json.dumps(body, ensure_ascii=False),
                ]
            )
        with (root / "inputs" / (name + ".csv")).open("x", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(REQUIRED_COLUMNS)
            writer.writerows(rows)
        run = request(
            "/analysis-runs", instance, {"file_ref": name + ".csv", "model_id": GROUPS[0][2]}
        )
        assert wait("/analysis-runs/" + run["run_id"], instance, "status")["status"] == "completed"
        prep = request(
            "/diagnostics/v3/source-preparations",
            instance,
            {
                "submission_key": name,
                "source": {"source_kind": "base", "base_run_id": run["run_id"], "appid": name},
            },
        )
        assert (
            wait(
                "/diagnostics/v3/source-preparations/" + prep["preparation_id"] + "/execution",
                instance,
            )["state"]
            == "completed"
        )
        task = request(
            "/diagnostics/v3/tasks",
            instance,
            {"submission_key": name, "preparation_id": prep["preparation_id"]},
        )
        ident = task["task_id"]
        if "cancelled" in name:
            checkpoint = root / "state/diagnostics-v3/jobs" / ident / "report-0000.json"
            until = time.monotonic() + 60
            while not checkpoint.exists():
                assert time.monotonic() < until
                time.sleep(0.005)
            request("/diagnostics/v3/tasks/" + ident + "/cancel", instance, {})
        execution = wait("/diagnostics/v3/tasks/" + ident, instance)
        report = request("/diagnostics/v3/tasks/" + ident + "/report", instance)
        save(out / (name + "-execution.json"), execution)
        save(out / (name + "-report.json"), report)
        if "constant" in name:
            assert execution["state"] == "completed" and not report["recommendations"]
        if "l5" in name:
            assert execution["state"] == "completed"
            groups = [g for g in report["discovery"]["cause_groups"] if g["rule_id"] == "L5"]
            assert groups
            evidence = request(
                f"/diagnostics/v3/tasks/{ident}/evidence/{groups[0]['group_id']}", instance
            )
            assert "900719925474099312345" in json.dumps(evidence)
            save(out / (name + "-evidence.json"), evidence)
        if "cancelled" in name:
            assert execution["state"] == "stopped" and execution["reason_code"] == "USER_CANCELLED"
            assert report["recommendations"] and any(
                not r["windows"] or not r["windows"][0]["complete"]
                for r in report["recommendations"]
            )
        save(
            out / (name + "-link.json"),
            {
                "appid": name,
                "task": ident,
                "url": "http://127.0.0.1:18002/#/analysis?direction=low_hit&mode=history&task="
                + ident,
            },
        )
        print(name, execution["state"], flush=True)
    save(out / "PASS.json", {"cases": 3, "actual": True})


if __name__ == "__main__":
    main()

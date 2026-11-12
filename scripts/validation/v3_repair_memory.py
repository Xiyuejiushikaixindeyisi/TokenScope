"""Controlled equal-memory replay of sealed large sources, with the HTTP server stopped."""

import argparse
import json
import socket
from pathlib import Path
from unittest.mock import patch

from v3_repair_e2e import save

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.contracts_v3 import PreparationRequest3
from tokenscope.analysis_common.service_v3 import PreparationService
from tokenscope.monitoring.service import MonitoringService
from tokenscope.user_monitoring.service import UserRunService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("server_root", type=Path)
    parser.add_argument("scale_evidence", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root, evidence, out = (
        args.server_root.resolve(),
        args.scale_evidence.resolve(),
        args.output.resolve(),
    )
    project = Path(__file__).resolve().parents[2]
    assert all(
        p.is_relative_to(project / "artifacts/validation/development-v3")
        for p in (root, evidence, out)
    )
    with socket.socket() as sock:
        assert sock.connect_ex(("127.0.0.1", 18002)) != 0, (
            "Stop this candidate server before exclusive replay"
        )
    out.mkdir(parents=True, exist_ok=False)
    # Reuse immutable monitor artifacts in this candidate's isolated state.
    # Create new submission keys/jobs only.
    base = MonitoringService(root / "inputs", root / "state", project, cpu_budget=2)
    service = PreparationService(base, UserRunService(base))
    measurements = []
    # Harness-only available-memory observation. The actual children enforce RLIMIT_AS.
    # This is not a cgroup or a whole-host memory limit.
    with patch("tokenscope.analysis_common.service_v3.available_memory", return_value=2 * 1024**3):
        for name in ("DS1200", "DS12000", "QW1200", "QW12000"):
            link = json.loads((evidence / (name + "-link.json")).read_text())
            receipt = service.store.submit(
                PreparationRequest3(
                    submission_key=out.name + name,
                    source=SourceSelection(
                        source_kind="base", base_run_id=link["run"], appid=link["appid"]
                    ),
                )
            )
            profile = service.profile(receipt.preparation_id)
            save(out / (name + "-profile.json"), profile.model_dump(mode="json"))
            prepared = service.process_next()
            execution = service.store.execution(receipt.preparation_id)
            save(out / (name + "-preparation.json"), execution.model_dump(mode="json"))
            assert prepared.state == "completed", execution
            manifest = json.loads(
                (
                    service.store.root
                    / "jobs"
                    / receipt.preparation_id
                    / execution.telemetry["manifest_path"]
                ).read_text()
            )
            save(out / (name + "-manifest.json"), manifest)
            task = service.diagnoses.submit(receipt.preparation_id, out.name + name)
            finished = service.process_next()
            save(out / (name + "-execution.json"), finished.model_dump(mode="json"))
            report = service.diagnoses.report(task.task_id)
            save(out / (name + "-report.json"), report)
            assert finished.state == "completed" and not finished.forced_termination, finished
            count = sum(len(w["members"]) for w in manifest["decision"]["windows"])
            assert 0 < count < 300
            assert report["recommendations"] and all(
                w["complete"] for r in report["recommendations"] for w in r["windows"]
            )
            measurements.append(
                {
                    "case": name,
                    "selected": count,
                    "parent": manifest["decision"]["parent_count"],
                    "profile": profile.model_dump(mode="json"),
                    "calibration": execution.telemetry["calibration"],
                    "prepare_peak_rss": execution.telemetry["supervisor_peak_rss_bytes"],
                    "diagnose_peak_rss": finished.telemetry["supervisor_peak_rss_bytes"],
                    "counters": finished.telemetry["telemetry"]["consumed"],
                }
            )
            print(name, "controlled memory complete", count, flush=True)
        from v3_repair_verify_resources import verify

        verify(out)
        save(
            out / "PASS.json",
            {
                "measurements": measurements,
                "available_observation": 2 * 1024**3,
                "hard_control": "RLIMIT_AS",
                "cgroup_test": False,
            },
        )


if __name__ == "__main__":
    main()

import json

import pytest
from conftest import csv_bytes, valid_row

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.contracts_v3 import PreparationRequest3
from tokenscope.analysis_common.service_v3 import PreparationService
from tokenscope.domain import RunSubmission
from tokenscope.user_monitoring.service import UserRunService


@pytest.mark.parametrize("model", ["DeepSeek-V4-Flash-0731", "Qwen3.6-27B"])
@pytest.mark.parametrize("changing", [True, False])
@pytest.mark.parametrize("review", [True, False])
def test_normal_worker_automatically_discovers_and_encodes_clock(service, model, changing, review):
    rows = []
    for i in range(8):
        text = (
            "stable " * 100 + "<session_clock> ## 当前时间（本机时区：Asia/Shanghai） "
            f"2026/11/10 09:00:{i if changing else 0:02d} </session_clock>" + " suffix" * 100
        )
        messages = [{"role": "system", "content": text}, {"role": "user", "content": "hello"}]
        if i % 2:
            messages.extend(
                [{"role": "assistant", "content": "reply"}, {"role": "user", "content": "next"}]
            )
        rows.append(
            valid_row(
                appid="clock",
                request_input=json.dumps({"messages": messages}),
                model_handle_start_time=f"2026-11-10T09:00:0{i}Z",
            )
        )
    (service.inputs.root / "clock.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="clock.csv", model_id=model))
    assert service.processor.process_next().status == "completed"
    preparation = PreparationService(service, UserRunService(service))
    if review:
        original_profile = preparation.profile

        def constrained(task_id):
            profile = original_profile(task_id)
            return profile.model_copy(
                update={"sample": profile.sample.model_copy(update={"max_requests": 4})}
            )

        preparation.profile = constrained
    request = PreparationRequest3(
        submission_key="auto-clock",
        source=SourceSelection(source_kind="base", base_run_id=run.run_id, appid="clock"),
    )
    receipt = preparation.store.submit(request)
    assert preparation.process_next().state == "completed"
    task = preparation.diagnoses.submit(receipt.preparation_id, "diagnose-clock")
    completed = preparation.process_next()
    assert completed.state == "completed", completed
    result = completed.telemetry
    root = preparation.store.root / "jobs" / task.task_id
    report = preparation.diagnoses.report(task.task_id)
    assert report["automatic_full"] is False
    findings = json.loads((root / "findings.json").read_text())
    assert bool(findings["findings"]) == changing
    if changing:
        recommendation = report["recommendations"][0]
        assert recommendation["finding"]["finding_id"] == findings["findings"][0]["finding_id"]
        assert len(recommendation["windows"]) == 2
        if review:
            assert all(w["complete"] and w["n"] == 2 for w in recommendation["windows"])
        for window in recommendation["windows"]:
            assert window["transformation_digest"] == recommendation["transformation_digest"]
            if window["status"] == "unavailable":
                assert window["reason_code"] == "REVIEW_UNAVAILABLE"
                continue
            assert window["complete"], window
            assert window["status"] in ("positive", "zero", "negative")
            rows = json.loads((root / window["rows_ref"]).read_text())
            plan = json.loads((root / window["plan_ref"]).read_text())
            from fractions import Fraction

            for side in ("before", "after"):
                for metric in ("p", "h", "c"):
                    assert window[side][metric] == sum(row[side][metric] for row in rows)
                assert all(row[side]["c"] == row[side]["p"] - row[side]["h"] for row in rows)
            before, after = window["before"], window["after"]
            pp = 100 * (Fraction(after["h"], after["p"]) - Fraction(before["h"], before["p"]))
            assert pp == Fraction(
                window["improvement_pp"]["numerator"], window["improvement_pp"]["denominator"]
            )
            for operation in plan["operations"]:
                replacement = json.loads(operation["replacement_json"])
                assert "<session_clock>NORMALIZED</session_clock>" in replacement
                assert replacement.startswith("stable ") and replacement.endswith(" suffix")
        assert not result["forced_termination"]
    assert result["report_available"]

    from fastapi.testclient import TestClient

    from tokenscope.analysis_common.report_v3 import SampleReport3
    from tokenscope.analysis_common.wire_v3 import from_wire
    from tokenscope.api.app import create_app

    app = create_app(service, start_worker=False)
    client = TestClient(app)
    headers = {"x-tokenscope-service-instance": app.state.user.service_id}
    fetched = client.get(f"/diagnostics/v3/tasks/{task.task_id}/report", headers=headers)
    assert fetched.status_code == 200, fetched.text
    typed = from_wire(SampleReport3, fetched.json())
    assert typed.task_id == task.task_id
    repeated = client.post(
        "/diagnostics/v3/tasks",
        json={"preparation_id": receipt.preparation_id, "submission_key": "diagnose-clock"},
        headers=headers,
    )
    assert repeated.status_code == 202 and repeated.json()["task_id"] == task.task_id
    assert preparation.process_next() is None  # GET/idempotent submission never schedules full.
    if review and changing and model == "DeepSeek-V4-Flash-0731":
        import os
        import sys

        from tokenscope.analysis_common.execution_v3 import WorkerSpec3
        from tokenscope.analysis_common.supervisor_v3 import WorkerSupervisor

        crash = preparation.diagnoses.submit(receipt.preparation_id, "crash-on-review")
        assert preparation.diagnoses.claim()[0].task_id == crash.task_id
        original = WorkerSpec3.model_validate_json((root / "job.json").read_bytes())
        crash_root = root.parent / crash.task_id
        spec = original.model_copy(
            update={"job_id": crash.task_id, "job_root": str(crash_root), "parent_pid": os.getpid()}
        )
        command = (
            "import os; from pathlib import Path\n"
            "from tokenscope.analysis_common import clock_worker_v3 as clock\n"
            "from tokenscope.analysis_common.worker_v3 import main\n"
            "original=clock.evaluate_window\n"
            "def fault(source,*args):\n"
            " if source.role=='review': os._exit(7)\n"
            " return original(source,*args)\n"
            "clock.evaluate_window=fault\n"
            f"raise SystemExit(main(Path({str(crash_root / 'job.json')!r})))\n"
        )
        stopped = WorkerSupervisor().run(
            spec, lambda: False, test_command=(sys.executable, "-c", command)
        )
        assert stopped["state"] == "failed"
        preparation.diagnoses.finish(crash.task_id, stopped, spec.profile.digest)
        saved = preparation.diagnoses.report(crash.task_id)
        assert len(saved["recommendations"][0]["windows"]) == 1
        assert saved["recommendations"][0]["windows"][0]["complete"]
    # A committed report cannot hide corruption in its supporting row evidence.
    if changing:
        row_path = root / report["recommendations"][0]["windows"][0]["rows_ref"]
        row_path.write_text("corrupt")  # This test's own new tmp_path only.
        fallback = client.get(f"/diagnostics/v3/tasks/{task.task_id}/report", headers=headers)
        assert fallback.status_code in (200, 409)
        if fallback.status_code == 200:
            assert fallback.json()["recommendations"] == []

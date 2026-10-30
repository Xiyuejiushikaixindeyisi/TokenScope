"""Real local HTTP/CLI, three models, MA isolation and process-lock acceptance."""

import csv
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import httpx

from tokenscope.domain import RunSubmission
from tokenscope.ingestion.csv_reader import REQUIRED_COLUMNS
from tokenscope.monitoring.ma.contracts import Submit as MaSubmit
from tokenscope.monitoring.ma.ingest import COLUMNS
from tokenscope.monitoring.ma.service import MaService
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.monitoring.service import MonitoringService
from tokenscope.user_monitoring.contracts import Submit as UserSubmit
from tokenscope.user_monitoring.service import UserRunService


def main():
    project = Path(__file__).resolve().parents[2]
    root = project / "artifacts/validation/user-monitoring/U005" / ("http-" + uuid4().hex[:8])
    inputs, state = root / "inputs", root / "state"
    inputs.mkdir(parents=True)
    base = MonitoringService(inputs, state)
    user = UserRunService(base)
    raw = json.dumps(
        {
            "messages": [{"role": "user", "content": "shared prefix " * 2000}],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "lookup",
                        "description": "example",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            ],
        },
        indent=2,
    )
    for model, _common in (
        ("GLM-5.2", "GLM-V5.2"),
        ("Qwen3.6-27B", "Qwen-V3.6-27B"),
        ("DeepSeek-V4-Flash-0731", "DeepSeek-V4-Flash"),
    ):
        with (inputs / (model + ".csv")).open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(REQUIRED_COLUMNS)
            for app, stamp in (
                ("a", "30/10/2026 00:00:00.000000001"),
                ("b", "2026-10-30T00:00:01Z"),
                ("a", "2026-10-30T00:00:02Z"),
            ):
                writer.writerow(["dup", app, stamp, "12", raw])
            writer.writerow(["bad", "a", "bad-date", "12", "{invalid"])
    # Same raw prefix, pre tenant A -> now tenant B on UUID A. UUID B has no prewarm.
    for role in ("pre", "now"):
        with (inputs / (role + ".csv")).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            for uid in ["A"] if role == "pre" else ["A", "B"]:
                stamp = "2026-10-30T07:01:00Z" if role == "pre" else "2026-10-30T08:01:00Z"
                writer.writerow(
                    dict(
                        instance_uuid=uid,
                        hash_id="dup",
                        appid="a" if role == "pre" else "b",
                        request_time=stamp,
                        model_handle_start_time=stamp,
                        prompt_tokens="10000",
                        cached_tokens="1000",
                        completion_tokens="12",
                        request_input=raw,
                    )
                )
    command = [
        str(project / ".venv/bin/tokenscope"),
        "--input-root",
        str(inputs),
        "--state-root",
        str(state),
    ]
    headers = {"X-TokenScope-Instance-Id": user.service_id}
    prefix = "/monitoring/user-v2"
    report = {
        "kind": "local_synthetic_not_deployment",
        "models": [],
        "sources": {},
        "passed": False,
    }
    for p in inputs.iterdir():
        report["sources"][p.name] = file_digest(p)

    def launch():
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        log = (root / f"server-{port}.log").open("wb")
        process = subprocess.Popen(
            command + ["serve", "--host", "127.0.0.1", "--port", str(port)],
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        log.close()
        client = httpx.Client(base_url=f"http://127.0.0.1:{port}", headers=headers, timeout=30)
        for _ in range(200):
            if process.poll() is not None:
                raise RuntimeError("Local server failed; see artifact log")
            try:
                if client.get("/version").status_code == 200:
                    return process, client
            except httpx.TransportError:
                pass
            time.sleep(0.1)
        process.terminate()
        raise RuntimeError("Local startup timeout")

    def stop(process, client):
        client.close()
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    process, client = launch()
    saved = []
    try:
        for model, common in (
            ("GLM-5.2", "GLM-V5.2"),
            ("Qwen3.6-27B", "Qwen-V3.6-27B"),
            ("DeepSeek-V4-Flash-0731", "DeepSeek-V4-Flash"),
        ):
            response = client.post(
                prefix + "/runs",
                json=dict(
                    submission_key=model,
                    file_ref=model + ".csv",
                    model_id=model,
                    common_name=common,
                ),
            )
            assert response.status_code == 202, response.text
            receipt = response.json()
            for _ in range(600):
                receipt = client.get(prefix + "/runs/" + receipt["user_run_id"]).json()
                if receipt["state"] in ("ready", "failed", "empty", "interrupted"):
                    break
                time.sleep(0.1)
            assert receipt["state"] == "ready", receipt
            path = prefix + "/runs/" + receipt["user_run_id"] + "/rankings"
            ranking = client.get(path).json()
            assert ranking["file_quality"] == dict(
                read_rows="4", valid_rows="3", skipped_rows="1"
            ), ranking
            assert ranking["rows"][0]["appid"] == "a"
            assert int(ranking["rows"][0]["total_ideal_cached_tokens"]) > 0
            assert ranking["rows"][1]["total_ideal_cached_tokens"] == "0"
            assert (
                client.get(
                    path, params=dict(limit=1, offset="1", index_revision=receipt["index_revision"])
                ).json()["rows"][0]["appid"]
                == "b"
            )
            scenario = dict(
                scenario_id=model,
                revision="1",
                model_id=model,
                common_name=common,
                deployment="synthetic-test",
                source="user_assumption",
                source_description="synthetic",
                evidence_sha256=None,
                measurement_boundary="GF dispatch-first token",
                workload_description="fixed cost",
                thinking_mode="disabled",
                min_prompt_tokens="0",
                max_prompt_tokens="1000000",
                chunk_tokens="8192",
                chunk_seconds="2",
                overhead_seconds="1",
                sample_count="0",
                calibration_notes="not calibrated",
            )
            assert client.post(prefix + "/scenarios", json=scenario).status_code == 201
            evaluation = client.post(
                prefix + "/evaluations",
                json=dict(
                    submission_key=model,
                    user_run_id=receipt["user_run_id"],
                    appid="a",
                    scenario_id=model,
                    scenario_revision="1",
                    target_seconds="8",
                    waiting_seconds="3",
                    comparator="le",
                ),
            )
            assert evaluation.status_code == 201, evaluation.text
            data = evaluation.json()
            assert data["status"] in ("reference", "reference_with_limit")
            assert (
                client.get("/analysis-runs/" + receipt["base_run_id"] + "/metrics").status_code
                == 200
            )
            saved.append((path, ranking, prefix + "/evaluations/" + data["evaluation_id"], data))
            report["models"].append(
                dict(model=model, receipt=receipt, ranking=ranking, evaluation=data)
            )
        ma_request = dict(
            submission_key="joint",
            pre_file_ref="pre.csv",
            now_file_ref="now.csv",
            model_standard_name="Qwen-V3.6-27B-64K",
            model_id="Qwen3.6-27B",
            pre_start="2026-10-30T07:00:00Z",
            now_start="2026-10-30T08:00:00Z",
            now_end="2026-10-30T09:00:00Z",
        )
        response = client.post("/monitoring/ma/runs", json=ma_request)
        assert response.status_code == 202, response.text
        ma_id = response.json()["ma_run_id"]
        for _ in range(600):
            ma_receipt = client.get("/monitoring/ma/runs/" + ma_id).json()
            if ma_receipt["state"] in ("completed", "failed", "interrupted"):
                break
            time.sleep(0.1)
        assert ma_receipt["state"] == "completed", ma_receipt
        a = client.get(f"/monitoring/ma/runs/{ma_id}/instances/A").json()["instance"]
        b = client.get(f"/monitoring/ma/runs/{ma_id}/instances/B").json()["instance"]
        assert a["ideal"]["hit_rate"] > 0 and b["ideal"]["hit_rate"] == 0, (a, b)
        assert client.get(prefix + "/runs/" + ma_id).status_code == 404
        assert (
            client.get(
                "/monitoring/ma/runs/" + report["models"][0]["receipt"]["user_run_id"]
            ).status_code
            == 404
        )
        report["ma_joint"] = dict(
            uuid_a_cross_app_hit=a["ideal"]["hit_rate"], uuid_b_hit=b["ideal"]["hit_rate"]
        )
    finally:
        stop(process, client)
    process, client = launch()
    try:
        for path, ranking, eval_path, evaluation in saved:
            assert client.get(path).json() == ranking
            assert client.get(eval_path).json() == evaluation
        report["restart_reads"] = True
    finally:
        stop(process, client)
    # Real process flock contention: all three queues return without heavy work.
    import fcntl

    waiting_user = user.submit(
        UserSubmit(
            submission_key="lock-user",
            file_ref="GLM-5.2.csv",
            model_id="GLM-5.2",
            common_name="GLM-V5.2",
        )
    )
    waiting_base = base.submit(
        RunSubmission(submission_key="lock-base", file_ref="GLM-5.2.csv", model_id="GLM-5.2")
    )
    ma = MaService(base)
    waiting_ma = ma.submit(MaSubmit.model_validate(ma_request | {"submission_key": "lock-ma"}))
    with (state / "worker.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done = subprocess.run(command + ["work-once"], capture_output=True, text=True, timeout=30)
        assert done.returncode == 0 and json.loads(done.stdout) is None, done.stderr
        assert user.receipt(waiting_user.user_run_id).state == "accepted"
        assert base.control.run(waiting_base.run_id).status == "queued"
        assert ma.store.receipt(waiting_ma.ma_run_id).state == waiting_ma.state
    from tokenscope.monitoring.dispatcher import Dispatcher

    dispatcher = Dispatcher(base.processor, ma.processor, state_root=state)
    dispatcher.register(user)
    for _ in range(12):
        if dispatcher.process_next() is None:
            break
    assert user.receipt(waiting_user.user_run_id).state == "ready"
    assert base.control.run(waiting_base.run_id).status == "completed"
    assert ma.store.receipt(waiting_ma.ma_run_id).state == "completed"
    report["cross_process_worker_lock"] = True
    run_id = report["models"][0]["receipt"]["user_run_id"]
    revision = user.receipt(run_id).index_revision
    for phase in ("before_rename", "before_publish"):
        user.rebuild(run_id)
        code = """
import os,sys
from pathlib import Path
from tokenscope.monitoring.service import MonitoringService
from tokenscope.user_monitoring.service import UserRunService
from tokenscope.user_monitoring import projection
user=UserRunService(MonitoringService(Path(sys.argv[1]),Path(sys.argv[2])))
def crash(*args,**kwargs): os._exit(72)
if sys.argv[3]=='before_rename': projection.os.replace=crash
else: user.publish=crash
user.process_next()
"""
        crashed = subprocess.run(
            [sys.executable, "-c", code, str(inputs), str(state), phase],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert crashed.returncode == 72, crashed.stderr
        assert user.receipt(run_id).state == "indexing"
        assert user.process_next().index_revision == revision
    report["process_exit_recovery"] = ["before_rename", "before_publish"]
    report["passed"] = True
    (root / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            dict(
                passed=True,
                report=str(root / "report.json"),
                models=3,
                ma_joint=report["ma_joint"],
                restart=True,
                cross_process_lock=True,
            )
        )
    )


if __name__ == "__main__":
    main()

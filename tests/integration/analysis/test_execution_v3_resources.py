import json
import os
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.contracts_v3 import PreparationRequest3, SampleManifest3
from tokenscope.analysis_common.execution_v3 import WorkerSpec3, automatic_profile
from tokenscope.analysis_common.supervisor_v3 import WorkerSupervisor
from tokenscope.analysis_common.wire import to_wire
from tokenscope.api.app import create_app
from tokenscope.domain import RunSubmission


def spec(tmp_path, **changes):
    p = automatic_profile(available_bytes=2 * 1024**3, source_bytes=100000, cpu_budget=1)
    p = p.model_copy(update=changes)
    ident = "prep-" + "a" * 32
    return WorkerSpec3(
        job_id=ident,
        action="prepare",
        input_root=str(tmp_path),
        state_root=str(tmp_path),
        asset_root=str(Path.cwd()),
        job_root=str(tmp_path / "diagnostics-v3" / "jobs" / ident),
        request=PreparationRequest3(
            submission_key="x",
            source=SourceSelection(source_kind="base", base_run_id="b", appid="a"),
        ),
        profile=p,
        parent_pid=os.getpid(),
    )


def workload(value, body):
    # Only this test supplies a command; production API/spec has no such field.
    header = (
        "from pathlib import Path; import time,json,os\n"
        "from tokenscope.analysis_common.execution_v3 import WorkerSpec3\n"
        "from tokenscope.analysis_common.worker_v3 import enforce\n"
        "from tokenscope.analysis_common.supervisor_v3 import atomic_json\n"
        "from tokenscope.analysis_common.runtime_v3 import CheckpointJournal\n"
        f"root=Path({value.job_root!r})\n"
        "spec=WorkerSpec3.model_validate_json((root/'job.json').read_bytes()); enforce(spec)\n"
    )
    return (sys.executable, "-c", header + body)


@pytest.mark.parametrize("cause", ["cancel", "deadline", "phase", "crash"])
def test_real_blocked_worker_stops_preserves_only_committed_checkpoint(tmp_path, cause):
    value = spec(tmp_path, deadline_ms=900 if cause == "deadline" else 10000)
    cancel = threading.Event()
    body = (
        "atomic_json(root/'complete.json', {'complete':True})\n"
        "CheckpointJournal(root,max_entries=10,max_bytes=10000).commit('findings','complete.json')\n"
        "(root/'checkpoints'/'second.pending').write_text('{half')\n"
        + (
            "atomic_json(root/'phase.json',{'phase':'model','deadline':time.monotonic()+0.1})\n"
            if cause == "phase"
            else ""
        )
        + ("os._exit(7)\n" if cause == "crash" else "time.sleep(60)\n")
    )
    with ThreadPoolExecutor(1) as pool:
        future = pool.submit(
            WorkerSupervisor().run, value, cancel.is_set, test_command=workload(value, body)
        )
        deadline = time.monotonic() + 5
        checkpoint = Path(value.job_root) / "checkpoints" / "000001.json"
        while not checkpoint.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert checkpoint.exists()
        started = time.monotonic()
        if cause == "cancel":
            cancel.set()
        result = future.result(timeout=6)
    assert time.monotonic() - started < 5
    assert len(result["checkpoints"]) == 1
    assert (
        result["reason_code"]
        == {
            "cancel": "USER_CANCELLED",
            "deadline": "DEADLINE_EXHAUSTED",
            "phase": "PHASE_DEADLINE_EXHAUSTED",
            "crash": "WORKER_CRASH",
        }[cause]
    )
    pid = json.loads((Path(value.job_root) / "process.json").read_text())["pid"]
    assert not Path(f"/proc/{pid}").exists()


def test_real_hard_address_space_and_spawn_denial(tmp_path):
    value = spec(tmp_path)
    command = workload(
        value,
        "import subprocess,resource\n"
        "try:\n subprocess.Popen(['true']); raise AssertionError('spawn allowed')\n"
        "except Exception as exc:\n assert getattr(exc,'code',None)=='WORKER_SPAWN_FORBIDDEN'\n"
        "assert resource.getrlimit(resource.RLIMIT_AS)==(spec.profile.address_space_bytes,)*2\n"
        "try:\n x=bytearray(spec.profile.address_space_bytes*2)\n"
        " raise AssertionError('allocation allowed')\n"
        "except MemoryError:\n pass\n"
        "atomic_json(root/'worker-result.json', "
        "{'state':'failed','reason_code':'TEST_MEMORY_LIMIT'})\n",
    )
    result = WorkerSupervisor().run(value, lambda: False, test_command=command)
    assert result["reason_code"] == "TEST_MEMORY_LIMIT"
    assert result["exit_code"] == 0


@pytest.mark.parametrize(
    "model,count", [("GLM-5.2", 1100), ("DeepSeek-V4-Flash-0731", 12), ("Qwen3.6-27B", 12)]
)
def test_real_automatic_prepare_no_memory_kill_and_responsive_api(service, model, count):
    raw = json.dumps({"messages": [{"role": "user", "content": "same payload " * 50}]})
    rows = [valid_row(appid="a", hash_id=f"h{i}", request_input=raw) for i in range(count)]
    (service.inputs.root / "input.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="input.csv", model_id=model))
    assert service.processor.process_next().status == "completed"
    app = create_app(service, start_worker=False)
    client = TestClient(app)
    headers = {"X-TokenScope-Service-Instance": app.state.user.service_id}
    request = PreparationRequest3(
        submission_key="one",
        source=SourceSelection(source_kind="base", base_run_id=run.run_id, appid="a"),
    )
    response = client.post(
        "/diagnostics/v3/source-preparations", json=to_wire(request), headers=headers
    )
    assert response.status_code == 202
    task_id = response.json()["preparation_id"]
    latencies = {"health": [], "receipt": []}
    with ThreadPoolExecutor(1) as pool:
        future = pool.submit(app.state.preparation.process_next)
        phase_file = app.state.preparation.store.root / "jobs" / task_id / "phase.json"
        until = time.monotonic() + 15
        observed_model = False
        while not future.done() and time.monotonic() < until:
            if phase_file.exists() and json.loads(phase_file.read_text())["phase"] == "model":
                observed_model = True
                break
            time.sleep(0.01)
        assert observed_model, "Response probes must overlap actual model loading"
        for _ in range(20):
            for kind, url in (
                ("health", "/healthz"),
                ("receipt", f"/diagnostics/v3/source-preparations/{task_id}"),
            ):
                started = time.monotonic()
                assert client.get(url, headers=headers).status_code == 200
                latencies[kind].append(time.monotonic() - started)
        result = future.result(timeout=120)
    execution = app.state.preparation.store.execution(task_id)
    evidence = service.state_root.parent / (model + "-resource-measurements.json")
    evidence.write_text(
        json.dumps(
            {"latencies": latencies, "execution": execution.model_dump(mode="json")}, indent=2
        )
    )
    assert result.state == "completed", execution.telemetry
    assert not execution.forced_termination and execution.exit_code == 0
    assert execution.telemetry["telemetry"]["hard_control"] == "RLIMIT_AS"
    for observations in latencies.values():
        assert sorted(observations)[18] <= 1
    root = app.state.preparation.store.root / "jobs" / task_id
    manifest = SampleManifest3.model_validate_json(
        (root / execution.telemetry["manifest_path"]).read_bytes()
    )
    selected = sum(len(w.members) for w in manifest.decision.windows)
    assert 0 < selected <= count
    if count == 1100:
        assert selected < count
    assert result.sample_id == manifest.sample_id


def test_default_app_blocks_old_execution_without_loading_token_bundle(service, monkeypatch):
    monkeypatch.setenv("TOKENSCOPE_RECOMMENDATION_BUNDLE", "/missing/bundle")
    app = create_app(service, start_worker=False)
    client = TestClient(app)
    for path in (
        "tasks",
        "v2/tasks",
        "tasks/old/retry",
        "tasks/old/token-evaluations",
        "tasks/old/low-hit-evaluations",
        "tasks/old/combination-evaluations",
        "tasks/old/token-authorizations",
    ):
        response = client.post("/diagnostics/" + path, content=b"not even JSON")
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "LEGACY_DIAGNOSTICS_READ_ONLY"
    assert app.state.diagnostics not in app.state.dispatcher.processors
    assert client.get("/healthz").status_code == 200
    response = client.post("/diagnostics/v3/source-preparations", content=b"x" * 65537)
    assert response.status_code == 413


def test_http_cancel_running_worker_and_shared_lock(service, monkeypatch):
    import fcntl

    app = create_app(service, start_worker=False)
    preparation = app.state.preparation
    client = TestClient(app)
    value = spec(service.state_root.parent)
    monkeypatch.setattr(preparation, "profile", lambda ident: value.profile)
    original = preparation.supervisor.run

    def block(actual, cancelled):
        return original(
            actual,
            cancelled,
            test_command=workload(
                actual, "atomic_json(root/'ready.json',{'ready':True})\ntime.sleep(60)\n"
            ),
        )

    monkeypatch.setattr(preparation.supervisor, "run", block)
    headers = {"X-TokenScope-Service-Instance": app.state.user.service_id}
    receipt = client.post(
        "/diagnostics/v3/source-preparations", json=to_wire(value.request), headers=headers
    ).json()
    ident = receipt["preparation_id"]
    root = preparation.store.root / "jobs" / ident
    with ThreadPoolExecutor(1) as pool:
        future = pool.submit(preparation.process_next)
        until = time.monotonic() + 5
        while not (root / "ready.json").exists() and time.monotonic() < until:
            time.sleep(0.01)
        assert (root / "ready.json").exists()
        with (service.state_root / "worker.lock").open("a") as lock:
            with pytest.raises(BlockingIOError):
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        start = time.monotonic()
        response = client.post(
            f"/diagnostics/v3/source-preparations/{ident}/cancel", headers=headers
        )
        http_elapsed = time.monotonic() - start
        assert response.status_code == 200 and http_elapsed <= 1
        assert client.get("/healthz").status_code == 200
        assert future.result(timeout=5).state == "stopped"
        elapsed = time.monotonic() - start
        assert elapsed <= 5
    (root / "cancel-measurements.json").write_text(
        json.dumps({"http_seconds": http_elapsed, "stop_seconds": elapsed})
    )
    pid = json.loads((root / "process.json").read_text())["pid"]
    assert not Path(f"/proc/{pid}").exists()


def test_recovery_salvages_only_committed_checkpoint_without_rerun(tmp_path):
    from tokenscope.analysis_common.preparation_store import PreparationStore
    from tokenscope.analysis_common.runtime_v3 import CheckpointJournal
    from tokenscope.analysis_common.supervisor_v3 import atomic_json

    store = PreparationStore(tmp_path / "diagnostics-v3")
    value = spec(tmp_path)
    receipt = store.submit(value.request)
    store.claim()
    root = store.root / "jobs" / receipt.preparation_id
    root.mkdir(parents=True)
    actual = value.model_copy(update={"job_id": receipt.preparation_id, "job_root": str(root)})
    atomic_json(root / "job.json", actual.model_dump(mode="json"))
    atomic_json(root / "complete.json", {"findings": []})
    journal = CheckpointJournal(root, max_entries=4, max_bytes=10000)
    item = journal.commit("findings", "complete.json")
    (root / "checkpoints" / "000002.json").write_text("{broken")
    store.recover()
    recovered = store.execution(receipt.preparation_id)
    assert recovered.state == "interrupted" and recovered.checkpoints == (item,)
    assert store.claim() is None
    assert (root / "checkpoints" / "000002.json").read_text() == "{broken"


def test_real_worker_file_limit_stops_without_complete_checkpoint(tmp_path):
    value = spec(tmp_path, max_file_bytes=1024 * 1024)
    command = workload(
        value,
        "try:\n (root/'oversize.pending').write_bytes(b'x'*(2*1024*1024))\n"
        "except OSError:\n atomic_json(root/'worker-result.json',"
        "{'state':'failed','reason_code':'DISK_LIMIT'})\n",
    )
    result = WorkerSupervisor().run(value, lambda: False, test_command=command)
    assert result["state"] == "failed" and result["reason_code"] == "DISK_LIMIT"
    assert result["checkpoints"] == []
    assert (
        Path(value.job_root) / "oversize.pending"
    ).stat().st_size <= value.profile.max_file_bytes


def test_parent_death_kills_its_worker(tmp_path):
    value = spec(tmp_path)
    source = tmp_path / "spec.json"
    source.write_text(value.model_dump_json())
    child_body = "atomic_json(root/'ready.json',{'ready':True})\ntime.sleep(60)\n"
    command = workload(value, child_body)
    parent_code = (
        "import os\nfrom pathlib import Path\n"
        "from tokenscope.analysis_common.execution_v3 import WorkerSpec3\n"
        "from tokenscope.analysis_common.supervisor_v3 import WorkerSupervisor\n"
        f"s=WorkerSpec3.model_validate_json(Path({str(source)!r}).read_bytes())\n"
        "s=s.model_copy(update={'parent_pid':os.getpid()})\n"
        f"WorkerSupervisor().run(s,lambda:False,test_command={command!r})\n"
    )
    root = Path(value.job_root)
    parent = subprocess.Popen(
        [sys.executable, "-c", parent_code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    pid = None
    try:
        until = time.monotonic() + 5
        while not (root / "ready.json").exists() and time.monotonic() < until:
            time.sleep(0.01)
        assert (root / "ready.json").exists()
        pid = json.loads((root / "process.json").read_text())["pid"]
        parent.terminate()
        parent.wait(timeout=5)
        until = time.monotonic() + 5
        status = Path(f"/proc/{pid}/stat")
        while (
            status.exists()
            and status.read_text().split(") ", 1)[1][0] != "Z"
            and time.monotonic() < until
        ):
            time.sleep(0.01)
        assert not status.exists() or status.read_text().split(") ", 1)[1][0] == "Z"
    finally:
        if parent.poll() is None:
            parent.kill()
            parent.wait(timeout=5)
        if pid is not None and Path(f"/proc/{pid}").exists():
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_cooperative_memory_release_is_not_misclassified_as_user_cancel(tmp_path):
    value = spec(tmp_path, soft_rss_bytes=180 * 1024 * 1024)
    command = workload(
        value,
        "import gc\n"
        "buf=bytearray(180*1024*1024)\n"
        "time.sleep(0.15)\n"
        "del buf; gc.collect()\n"
        "time.sleep(0.15)\n"
        "assert not (root/'cancel.json').exists()\n"
        "atomic_json(root/'worker-result.json',{'state':'completed'})\n",
    )
    result = WorkerSupervisor().run(value, lambda: False, test_command=command)
    assert result["supervisor_peak_rss_bytes"] >= value.profile.soft_rss_bytes
    assert result["state"] == "completed" and not result["forced_termination"]


@pytest.mark.parametrize("model,address", [("GLM-5.2", 794374963), ("Qwen3.6-27B", 789047500)])
def test_initial_failed_memory_envelope_reproduced_with_smaller_cpu(
    service, monkeypatch, model, address
):
    import tokenscope.analysis_common.service_v3 as module

    # Reproduce the first failure's bound; fluctuating host availability must
    # not be credited as a code fix. The request still has no sample_limit.
    monkeypatch.setattr(module, "available_memory", lambda: (address * 100 + 64) // 65)
    test_real_automatic_prepare_no_memory_kill_and_responsive_api(service, model, 12)

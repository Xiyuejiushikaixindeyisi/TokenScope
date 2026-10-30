import json
import multiprocessing
import subprocess
import sys
import time
from pathlib import Path

from tokenscope.domain import RunSubmission
from tokenscope.monitoring.dispatcher import Dispatcher
from tokenscope.monitoring.ma.service import MaService
from tokenscope.monitoring.service import MonitoringService

from .helpers import binding, row, write_csv


def hold_worker(root: str, ready: object, release: object) -> None:
    import fcntl

    with (Path(root) / "worker.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        ready.set()
        release.wait(30)


def run_dispatch(inputs: str, root: str, trace: str) -> None:
    service = MonitoringService(Path(inputs), Path(root))
    ma = MaService(service)
    for processor, name in ((service.processor, "v1"), (ma.processor, "ma")):
        original = processor.execute

        def traced(run: object, original=original, name=name) -> None:
            with open(trace, "a") as log:
                log.write(json.dumps(["start", name, time.monotonic()]) + "\n")
            original(run)
            with open(trace, "a") as log:
                log.write(json.dumps(["end", name, time.monotonic()]) + "\n")

        processor.execute = traced
    dispatcher = Dispatcher(service.processor, ma.processor, state_root=service.state_root)
    for _ in range(120):
        if dispatcher.process_next() is not None:
            return
        time.sleep(0.1)


def test_real_process_lock_and_both_queues(service: MonitoringService, tmp_path: Path) -> None:
    write_csv(service.inputs.root / "pre.csv", [row("pre")])
    write_csv(service.inputs.root / "now.csv", [row()])
    ma = MaService(service)
    a = ma.submit(binding())
    v = service.submit(RunSubmission(file_ref="now.csv", model_id="Qwen3.6-27B"))
    ctx = multiprocessing.get_context("spawn")
    ready, release = ctx.Event(), ctx.Event()
    holder = ctx.Process(target=hold_worker, args=(str(service.state_root), ready, release))
    holder.start()
    try:
        assert ready.wait(15)
        assert ma.processor.process_next() is None
        assert service.processor.process_next() is None
        assert ma.store.receipt(a.ma_run_id).state == "queued"
    finally:
        release.set()
        holder.join(20)
    trace = tmp_path / "trace.jsonl"
    workers = [
        ctx.Process(
            target=run_dispatch,
            args=(str(service.inputs.root), str(service.state_root), str(trace)),
        )
        for _ in range(2)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(60)
        assert worker.exitcode == 0
    events = [json.loads(line) for line in trace.read_text().splitlines()]
    assert [e[0] for e in events] == ["start", "end", "start", "end"]
    assert {e[1] for e in events} == {"v1", "ma"}
    assert ma.store.receipt(a.ma_run_id).state == "completed"
    assert service.control.run(v.run_id).status == "completed"


def test_cli_roundtrip(service: MonitoringService) -> None:
    write_csv(service.inputs.root / "pre.csv", [row("pre")])
    write_csv(service.inputs.root / "now.csv", [row()])
    prefix = [
        sys.executable,
        "-m",
        "tokenscope.cli",
        "--input-root",
        str(service.inputs.root),
        "--state-root",
        str(service.state_root),
    ]

    def call(*args: str) -> dict:
        result = subprocess.run([*prefix, *args], text=True, capture_output=True, timeout=60)
        assert result.returncode == 0, result.stdout + result.stderr
        return json.loads(result.stdout)

    receipt = call("ma-submit", "--json", binding().model_dump_json())
    assert call("work-once")["state"] == "completed"
    snapshot = call("ma-snapshot", receipt["ma_run_id"], "A")
    assert snapshot == MaService(service).snapshot(receipt["ma_run_id"], "A").model_dump(
        mode="json"
    )

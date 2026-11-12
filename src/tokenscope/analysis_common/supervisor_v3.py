"""One fixed worker process at a time, supervised outside the HTTP event loop."""

import json
import os
import signal
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from tokenscope.analysis_common.execution_v3 import WorkerSpec3
from tokenscope.analysis_common.runtime_v3 import CheckpointJournal


def atomic_json(path: Path, value: Any) -> None:
    pending = path.with_suffix(path.suffix + ".pending")
    data = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    with pending.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    pending.replace(path)


def process_rss(pid: int) -> int:
    try:
        return int(Path(f"/proc/{pid}/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except (OSError, ValueError, IndexError):
        return 0


def terminate_group(process: subprocess.Popen[bytes], grace: float = 0.5) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=2)
    except ProcessLookupError:
        process.wait(timeout=2)


class WorkerSupervisor:
    def run(
        self,
        spec: WorkerSpec3,
        cancelled: Callable[[], bool],
        *,
        # Only trusted test callers replace the executable workload. No HTTP,
        # source record or job-file field can supply a command.
        test_command: tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        root = Path(spec.job_root)
        root.mkdir(parents=True, exist_ok=False)
        job_file = root / "job.json"
        atomic_json(job_file, spec.model_dump(mode="json"))
        command = test_command or (
            sys.executable,
            "-m",
            "tokenscope.analysis_common.worker_v3",
            str(job_file),
        )
        env = dict(os.environ)
        env.update(
            MALLOC_ARENA_MAX="2",
            OPENBLAS_NUM_THREADS="1",
            OMP_NUM_THREADS="1",
            MKL_NUM_THREADS="1",
            NUMEXPR_NUM_THREADS="1",
            VECLIB_MAXIMUM_THREADS="1",
            RAYON_NUM_THREADS=str(spec.profile.cpu_budget),
            HF_HUB_OFFLINE="1",
            TRANSFORMERS_OFFLINE="1",
        )
        started = time.monotonic()
        peak = 0
        stop_reason: str | None = None
        stop_at = 0.0
        forced = False
        with (
            (root / "worker.stdout.log").open("xb") as out,
            (root / "worker.stderr.log").open("xb") as err,
        ):
            process = subprocess.Popen(
                command,
                cwd=spec.asset_root,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=out,
                stderr=err,
                start_new_session=True,
            )
            atomic_json(root / "process.json", {"pid": process.pid, "job_id": spec.job_id})
            try:
                while process.poll() is None:
                    now = time.monotonic()
                    rss = process_rss(process.pid)
                    peak = max(peak, rss)
                    if stop_reason == "MEMORY_PRESSURE" and rss < spec.profile.soft_rss_bytes:
                        # A cooperating worker released the attempt before its
                        # grace expired; allow its bounded smaller retry.
                        stop_reason = None
                    if stop_reason == "MEMORY_PRESSURE" and cancelled():
                        stop_reason, stop_at = "USER_CANCELLED", now
                        atomic_json(root / "cancel.json", {"reason_code": stop_reason})
                    if stop_reason is None:
                        if cancelled():
                            stop_reason = "USER_CANCELLED"
                        elif rss >= spec.profile.soft_rss_bytes:
                            stop_reason = "MEMORY_PRESSURE"
                        if stop_reason is not None:
                            # Memory pressure is observed by BudgetLedger and
                            # causes shrinking. Do not turn it into user cancel.
                            if stop_reason != "MEMORY_PRESSURE":
                                atomic_json(root / "cancel.json", {"reason_code": stop_reason})
                            stop_at = now
                    elif now - stop_at >= 0.5:
                        forced = True
                        terminate_group(process)
                        break
                    time.sleep(0.025)
            finally:
                if process.poll() is None:
                    terminate_group(process)
        result_path = root / "worker-result.json"
        result: dict[str, Any] = {}
        if (
            result_path.is_file()
            and result_path.stat().st_size <= spec.profile.sample.max_metadata_bytes
        ):
            try:
                result = json.loads(result_path.read_text())
            except (ValueError, OSError):
                result = {}
        if not isinstance(result, dict):
            result = {}
        if stop_reason is not None:
            result["state"] = "stopped"
            result["reason_code"] = stop_reason
        elif process.returncode != 0 or result.get("state") not in (
            "completed",
            "stopped",
            "failed",
        ):
            result = {"state": "failed", "reason_code": "WORKER_CRASH"}
        if forced and stop_reason == "MEMORY_PRESSURE":
            result["state"] = "failed"
            result["reason_code"] = "MEMORY_LIMIT_TERMINATION"
        journal = CheckpointJournal(
            root,
            max_entries=spec.profile.budgets["checkpoints"],
            max_bytes=spec.profile.max_file_bytes,
        )
        result.update(
            exit_code=process.returncode,
            forced_termination=forced,
            supervisor_peak_rss_bytes=peak,
            supervisor_elapsed_ms=round((time.monotonic() - started) * 1000),
            checkpoints=[item.model_dump(mode="json") for item in journal.committed()],
        )
        atomic_json(root / "supervisor-result.json", result)
        return result

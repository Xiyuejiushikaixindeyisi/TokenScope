"""Fixed, bounded Linux worker. No user-provided command or import is executed."""

import ctypes
import gc
import json
import os
import resource
import signal
import sys
from pathlib import Path
from typing import Any

from tokenscope.analysis_common.execution_v3 import WorkerSpec3, calibrated_sample
from tokenscope.analysis_common.runtime_v3 import (
    BudgetLedger,
    CheckpointJournal,
    TaskStopped,
    guard_json,
)
from tokenscope.analysis_common.sampling_v3 import SampleLimits, SampleMetadata
from tokenscope.errors import TokenScopeError


def enforce(spec: WorkerSpec3) -> None:
    profile = spec.profile
    resource.setrlimit(resource.RLIMIT_AS, (profile.address_space_bytes,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (profile.max_file_bytes,) * 2)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    # Native threads share the address-space cap. Additional processes are not allowed.
    def audit(event: str, args: tuple[Any, ...]) -> None:
        if event in {
            "os.fork",
            "os.forkpty",
            "os.posix_spawn",
            "os.exec",
            "os.system",
            "subprocess.Popen",
        }:
            raise TokenScopeError("WORKER_SPAWN_FORBIDDEN", "Worker cannot spawn processes", 409)

    sys.addaudithook(audit)
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0 or os.getppid() != spec.parent_pid:
        raise TokenScopeError("WORKER_PARENT_LOST", "Worker parent unavailable", 503)
    from tokenscope.resources import configure_process

    configure_process(profile.cpu_budget)


def virtual_peak() -> int:
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("VmPeak:"):
            return int(line.split()[1]) * 1024
    raise TokenScopeError("RESOURCE_ENFORCEMENT_UNAVAILABLE", "Cannot measure worker memory", 503)


def run(spec: WorkerSpec3, ledger: BudgetLedger) -> dict[str, Any]:
    from tokenscope.analysis_common.encoding import EncodingContext
    from tokenscope.analysis_common.source import SourceResolver
    from tokenscope.analysis_common.source_preparation import PreparationIO, prepare_snapshot
    from tokenscope.analysis_common.supervisor_v3 import atomic_json
    from tokenscope.encoding.batch import EncodingFailure
    from tokenscope.encoding.models import EncodingProfile
    from tokenscope.monitoring.service import MonitoringService
    from tokenscope.resources import configure_process
    from tokenscope.user_monitoring.service import UserRunService

    if spec.action != "prepare":
        from tokenscope.analysis_common.clock_worker_v3 import diagnose_clock

        return diagnose_clock(spec, ledger)
    root, profile = Path(spec.job_root), spec.profile
    base = MonitoringService(
        Path(spec.input_root), Path(spec.state_root), Path(spec.asset_root), profile.cpu_budget
    )
    resolver = SourceResolver(base, UserRunService(base))
    journal = CheckpointJournal(
        root,
        max_entries=profile.budgets["checkpoints"],
        max_bytes=profile.sample.max_metadata_bytes,
    )
    measurements: dict[str, Any] = {}
    sample = profile.sample

    def phase(name: str) -> None:
        ledger.enter(name)
        atomic_json(root / "phase.json", {"phase": name})

    def charge(member: SampleMetadata) -> None:
        ledger.reserve_many(
            {
                "requests": 1,
                "raw_read_bytes": member.raw_bytes,
                "token_read_bytes": (member.prompt_tokens or 0) * 4,
            }
        )

    def guard(raw: str) -> None:
        ledger.checkpoint()
        guard_json(
            raw,
            max_bytes=max(profile.sample.max_record_bytes, profile.sample.max_metadata_bytes),
            max_depth=profile.max_json_depth,
            max_nodes=profile.max_json_nodes,
        )

    def calibrate(source: Any, limits: SampleLimits) -> SampleLimits:
        if not measurements:
            phase("model")
            # The original encoder identity remains authoritative; CPU concurrency
            # may match its profile while affinity never exceeds the task allocation.
            original_profile = EncodingProfile.model_validate_json(source.scope.source.profile_json)
            configure_process(min(original_profile.cpu_budget, profile.cpu_budget))
            ledger.checkpoint()
            context = EncodingContext(source, cpu_budget=profile.cpu_budget)
            probe = json.dumps(
                {"messages": [{"role": "user", "content": "resource calibration " * 1024}]}
            )
            ledger.reserve_many({"encoding_calls": 1, "encoding_input_bytes": len(probe.encode())})
            encoded = context.batch.encode_batch([probe])[0]
            if isinstance(encoded, EncodingFailure):
                raise TokenScopeError(encoded.code, "Model calibration failed", 422)
            ledger.reserve("encoding_output_tokens", encoded.prompt_tokens)
            peak = virtual_peak()
            measurements.update(
                model_id=source.scope.source.model_id,
                asset_identity=source.scope.source.asset_identity,
                peak_virtual_bytes=peak,
                calibration_tokens=encoded.prompt_tokens,
            )
            atomic_json(root / "calibration.json", measurements)
            del context, encoded
            gc.collect()
        bounded = calibrated_sample(profile, measurements["peak_virtual_bytes"])
        values = limits.model_dump()
        for name in (
            "max_requests",
            "max_raw_bytes",
            "max_prompt_tokens",
            "max_record_bytes",
            "max_record_tokens",
        ):
            values[name] = min(values[name], getattr(bounded, name))
        return SampleLimits.model_validate(values)

    io = PreparationIO(
        profile.sample.max_metadata_bytes,
        checkpoint=ledger.checkpoint,
        charge_verification=lambda n: ledger.reserve("verification_bytes", n),
        charge_snapshot=lambda n: ledger.reserve("snapshot_bytes", n),
        charge_member=charge,
        guard=guard,
        phase=phase,
        charge_metadata=lambda n: ledger.reserve_many({"metadata_rows": 1, "metadata_bytes": n}),
    )
    attempts: list[dict[str, Any]] = []
    for attempt in range(1, profile.max_attempts + 1):
        target = root / f"sample-{attempt}"
        try:
            manifest = prepare_snapshot(
                resolver, spec.request.source, sample, target, io=io, calibrate=calibrate
            )
            ledger.reserve("checkpoints")
            checkpoint = journal.commit("sample", f"sample-{attempt}/manifest.json")
            return {
                "state": "completed",
                "sample_id": manifest.sample_id,
                "manifest_sha256": checkpoint.sha256,
                "manifest_path": checkpoint.artifact,
                "calibration": measurements,
                "attempts": attempts,
                "selected_count": sum(len(w.members) for w in manifest.decision.windows),
                "parent_count": manifest.decision.parent_count,
                "sample_limits": manifest.decision.limits.model_dump(),
            }
        except TokenScopeError as exc:
            attempts.append({"attempt": attempt, "reason_code": exc.code})
            atomic_json(root / "attempts.json", attempts)
            if (
                exc.code not in {"MEMORY_PRESSURE", "SNAPSHOT_DISK_LIMIT"}
                or attempt == profile.max_attempts
            ):
                raise
            gc.collect()
            ctypes.CDLL(None).malloc_trim(0)
            values = sample.model_dump()
            for name in (
                "max_requests",
                "max_raw_bytes",
                "max_prompt_tokens",
                "max_record_bytes",
                "max_record_tokens",
            ):
                values[name] = max(1, values[name] // 2)
            sample = SampleLimits.model_validate(values)
    raise AssertionError("Attempt bound exhausted")


def main(job_file: Path) -> int:
    # Job files are generated by the parent, bounded before parsing and confined
    # to the task directory. API inputs cannot choose these paths or limits.
    if job_file.stat().st_size > 1024 * 1024:
        return 2
    spec = WorkerSpec3.model_validate_json(job_file.read_bytes())
    root = Path(spec.job_root).resolve()
    expected = Path(spec.state_root).resolve() / "diagnostics-v3" / "jobs" / spec.job_id
    if root != expected or job_file.resolve() != root / "job.json":
        return 2
    enforce(spec)
    ledger = BudgetLedger(spec.profile, lambda: (root / "cancel.json").exists())
    from tokenscope.analysis_common.supervisor_v3 import atomic_json

    try:
        result = run(spec, ledger)
    except TaskStopped as exc:
        result = {"state": "stopped", "reason_code": exc.code}
    except TokenScopeError as exc:
        result = {"state": "failed", "reason_code": exc.code}
    except MemoryError:
        result = {"state": "failed", "reason_code": "MEMORY_ALLOCATION_FAILED"}
    except OSError:
        result = {"state": "failed", "reason_code": "STORAGE_UNAVAILABLE"}
    except Exception:
        # No raw payloads/tracebacks in externally readable task errors.
        result = {"state": "failed", "reason_code": "WORKER_INTERNAL_ERROR"}
    result["telemetry"] = ledger.metrics()
    atomic_json(root / "worker-result.json", result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

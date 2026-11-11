"""V3 preparation queue; HTTP registration never inspects the source."""

import os
import threading
import time
from pathlib import Path

from tokenscope.analysis_common.contracts_v3 import PreparationReceipt3
from tokenscope.analysis_common.diagnostic_store_v3 import DiagnosticStore3
from tokenscope.analysis_common.execution_v3 import (
    Execution3,
    WorkerSpec3,
    automatic_profile,
    available_memory,
)
from tokenscope.analysis_common.preparation_store import PreparationStore
from tokenscope.analysis_common.runtime_v3 import RuntimeProfile3
from tokenscope.analysis_common.supervisor_v3 import WorkerSupervisor
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.service import MonitoringService
from tokenscope.user_monitoring.service import UserRunService


class PreparationService:
    def __init__(self, base: MonitoringService, user: UserRunService) -> None:
        self.base, self.user = base, user
        self.store = PreparationStore(base.state_root / "diagnostics-v3")
        self.diagnoses = DiagnosticStore3(self.store)
        self.supervisor = WorkerSupervisor()
        self.shutdown = threading.Event()

    def profile(self, task_id: str) -> RuntimeProfile3:
        selection = self.store.request(task_id).source
        base_id = selection.base_run_id
        if selection.source_kind == "user_v2":
            base_id = self.user.receipt(selection.user_run_id or "").base_run_id
        if base_id is None:
            raise TokenScopeError("SOURCE_UNAVAILABLE", "Base source unavailable", 503)
        run = self.base.control.run(base_id)
        directory = (self.base.state_root / "runs" / run.run_id).resolve(strict=True)
        if not directory.is_relative_to((self.base.state_root / "runs").resolve()):
            raise TokenScopeError("SOURCE_IDENTITY_INVALID", "Invalid source directory", 409)
        # Directory metadata only, off the HTTP path. Source hashing/body access
        # occurs exclusively inside the bounded child; no user sample tuning.
        size = 0
        started = time.monotonic()
        for root, _, files in os.walk(directory, followlinks=False):
            if self.shutdown.is_set() or self.store.execution(task_id).cancel_requested:
                raise TokenScopeError("USER_CANCELLED", "Preparation cancelled", 409)
            if time.monotonic() - started > 10:
                raise TokenScopeError(
                    "SOURCE_INVENTORY_LIMIT", "Source inventory deadline exceeded", 409
                )
            for name in files:
                path = Path(root) / name
                if not path.is_symlink():
                    size += path.stat().st_size
        return automatic_profile(
            available_bytes=available_memory(), source_bytes=size, cpu_budget=self.base.cpu_budget
        )

    def process_next(self) -> PreparationReceipt3 | Execution3 | None:
        import fcntl

        with (self.base.state_root / "worker.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return None
            self.store.recover()
            self.diagnoses.recover()
            receipt = self.store.claim()
            if receipt is None:
                return self.process_diagnosis()
            ident = receipt.preparation_id
            profile_digest = None
            try:
                profile = self.profile(ident)
                profile_digest = profile.digest
                spec = WorkerSpec3(
                    job_id=ident,
                    action="prepare",
                    input_root=str(self.base.inputs.root),
                    state_root=str(self.base.state_root),
                    asset_root=str(self.base.assets.root),
                    job_root=str(self.store.root / "jobs" / ident),
                    request=self.store.request(ident),
                    profile=profile,
                    parent_pid=os.getpid(),
                )
                result = self.supervisor.run(
                    spec,
                    lambda: self.shutdown.is_set() or self.store.execution(ident).cancel_requested,
                )
            except TokenScopeError as exc:
                result = {
                    "state": "stopped" if exc.code == "USER_CANCELLED" else "failed",
                    "reason_code": exc.code,
                }
            except OSError:
                result = {"state": "failed", "reason_code": "STORAGE_UNAVAILABLE"}
            return self.store.finish(ident, result, profile_digest)

    def process_diagnosis(self) -> Execution3 | None:
        """Caller owns worker.lock; no automatic full or another dispatcher."""
        claimed = self.diagnoses.claim()
        if claimed is None:
            return None
        execution, preparation_id = claimed
        ident = execution.task_id
        digest = None
        try:
            profile = self.profile(preparation_id)
            digest = profile.digest
            spec = WorkerSpec3(
                job_id=ident,
                action="diagnose",
                input_root=str(self.base.inputs.root),
                state_root=str(self.base.state_root),
                asset_root=str(self.base.assets.root),
                job_root=str(self.store.root / "jobs" / ident),
                request=self.store.request(preparation_id),
                profile=profile,
                parent_pid=os.getpid(),
                sample_preparation_id=preparation_id,
            )
            result = self.supervisor.run(
                spec,
                lambda: self.shutdown.is_set() or self.diagnoses.execution(ident).cancel_requested,
            )
        except TokenScopeError as exc:
            result = {
                "state": "stopped" if exc.code == "USER_CANCELLED" else "failed",
                "reason_code": exc.code,
            }
        except OSError:
            result = {"state": "failed", "reason_code": "STORAGE_UNAVAILABLE"}
        return self.diagnoses.finish(ident, result, digest)

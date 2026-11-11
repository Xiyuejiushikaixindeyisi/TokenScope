"""Task-local v3 budgets, bounded JSON admission and durable checkpoints.

Address space is a hard process limit; RSS is measured separately. No claim is
made that RLIMIT_AS is an RSS or cgroup limit.
"""

import hashlib
import os
import resource
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Self
from uuid import uuid4

from pydantic import Field, model_validator

from tokenscope.analysis_common.contracts import Contract, Digest, canonical_metadata
from tokenscope.analysis_common.sampling_v3 import SampleLimits
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest, sync_directory


class RuntimeProfile3(Contract):
    version: Literal["bounded-runtime-3.1"] = "bounded-runtime-3.1"
    address_space_bytes: int = Field(ge=128 * 1024 * 1024)
    soft_rss_bytes: int = Field(gt=0)
    deadline_ms: int = Field(gt=0)
    phase_deadlines_ms: dict[str, int]
    cpu_budget: int = Field(ge=1, le=64)
    max_file_bytes: int = Field(gt=0)
    sample: SampleLimits
    budgets: dict[str, int]
    max_json_depth: int = Field(ge=1, le=512)
    max_json_nodes: int = Field(gt=0)
    max_attempts: int = Field(ge=1, le=4)

    @model_validator(mode="after")
    def positive(self) -> Self:
        if self.soft_rss_bytes >= self.address_space_bytes:
            raise ValueError("Soft RSS boundary must precede hard address limit")
        if not self.budgets or any(value <= 0 for value in self.budgets.values()):
            raise ValueError("All budget limits must be positive")
        if not self.phase_deadlines_ms or any(v <= 0 for v in self.phase_deadlines_ms.values()):
            raise ValueError("All phase deadlines must be positive")
        return self

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_metadata(self)).hexdigest()


def current_rss() -> int:
    return int(Path("/proc/self/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")


class TaskStopped(TokenScopeError):
    def __init__(self, code: str) -> None:
        super().__init__(code, "Bounded task stopped: " + code, 409)


@dataclass
class BudgetLedger:
    profile: RuntimeProfile3
    cancelled: Callable[[], bool]
    started: float = field(default_factory=time.monotonic)
    consumed: dict[str, int] = field(default_factory=dict)
    stage: str = "startup"
    stage_deadline: float | None = None

    def enter(self, stage: str) -> float:
        self.stage = stage
        self.stage_deadline = time.monotonic() + self.profile.phase_deadlines_ms[stage] / 1000
        return self.stage_deadline

    def checkpoint(self) -> None:
        if self.cancelled():
            raise TaskStopped("USER_CANCELLED")
        if (time.monotonic() - self.started) * 1000 >= self.profile.deadline_ms:
            raise TaskStopped("DEADLINE_EXHAUSTED")
        if self.stage_deadline is not None and time.monotonic() >= self.stage_deadline:
            raise TaskStopped("PHASE_DEADLINE_EXHAUSTED")
        if current_rss() >= self.profile.soft_rss_bytes:
            raise TaskStopped("MEMORY_PRESSURE")

    def reserve(self, kind: str, amount: int = 1) -> None:
        self.reserve_many({kind: amount})

    def reserve_many(self, amounts: dict[str, int]) -> None:
        self.checkpoint()
        for kind, amount in amounts.items():
            if type(amount) is not int or amount < 0 or kind not in self.profile.budgets:
                raise ValueError("Unknown or invalid budget charge")
            if self.consumed.get(kind, 0) + amount > self.profile.budgets[kind]:
                raise TaskStopped("BUDGET_EXHAUSTED:" + kind)
        for kind, amount in amounts.items():
            self.consumed[kind] = self.consumed.get(kind, 0) + amount

    def metrics(self) -> dict[str, Any]:
        return {
            "consumed": dict(self.consumed),
            "limits": self.profile.budgets,
            "elapsed_ms": round((time.monotonic() - self.started) * 1000),
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "address_space_limit_bytes": self.profile.address_space_bytes,
            "hard_control": "RLIMIT_AS",
            "stop_location": self.stage,
            "rss_peak_scope": "OS lifetime including inherited pre-exec high-water mark",
        }


def guard_json(raw: str, *, max_bytes: int, max_depth: int, max_nodes: int) -> None:
    """Lexical complexity admission before json.loads; not a replacement parser."""
    if len(raw.encode("utf-8")) > max_bytes:
        raise TaskStopped("JSON_BYTE_LIMIT")
    depth = nodes = 0
    quoted = escaped = scalar = False
    for character in raw:
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
            continue
        if character == '"':
            quoted, scalar = True, False
            nodes += 1  # Includes keys; deliberately conservative.
        elif character in "[{":
            depth += 1
            nodes += 1
            scalar = False
            if depth > max_depth:
                raise TaskStopped("JSON_DEPTH_LIMIT")
        elif character in "]}":
            depth -= 1
            scalar = False
            if depth < 0:
                raise TokenScopeError("INVALID_JSON", "Invalid JSON structure", 422)
        elif character in ",: \t\r\n":
            scalar = False
        elif not scalar:
            scalar = True
            nodes += 1
        if nodes > max_nodes:
            raise TaskStopped("JSON_NODE_LIMIT")
    if depth or quoted:
        raise TokenScopeError("INVALID_JSON", "Unclosed JSON structure", 422)


class Checkpoint3(Contract):
    version: Literal["diagnostic-checkpoint-3"] = "diagnostic-checkpoint-3"
    sequence: int = Field(ge=1)
    kind: Literal["sample", "findings", "window_evaluation", "report"]
    artifact: str = Field(min_length=1, max_length=512)
    sha256: Digest
    complete: Literal[True] = True


class CheckpointJournal:
    def __init__(self, root: Path, *, max_entries: int, max_bytes: int) -> None:
        self.root = root.resolve()
        self.directory = self.root / "checkpoints"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.max_entries, self.max_bytes = max_entries, max_bytes
        self.sequence = len(self.committed())

    def checked_artifact(self, reference: str) -> Path:
        relative = Path(reference)
        if relative.is_absolute() or ".." in relative.parts:
            raise TokenScopeError("INVALID_ARTIFACT", "Checkpoint path escapes task", 409)
        path = (self.root / relative).resolve(strict=True)
        if (
            not path.is_relative_to(self.root)
            or not path.is_file()
            or path.stat().st_size > self.max_bytes
        ):
            raise TokenScopeError("INVALID_ARTIFACT", "Checkpoint artifact is invalid", 409)
        return path

    def committed(self) -> tuple[Checkpoint3, ...]:
        result = []
        for number in range(1, self.max_entries + 1):
            path = self.directory / f"{number:06d}.json"
            if not path.exists():
                break
            try:
                if path.stat().st_size > self.max_bytes:
                    break
                item = Checkpoint3.model_validate_json(path.read_bytes())
                if item.sequence != number:
                    break
                if file_digest(self.checked_artifact(item.artifact)) != item.sha256:
                    break
            except (OSError, ValueError, TokenScopeError):
                break
            result.append(item)
        return tuple(result)

    def commit(self, kind: Any, artifact: str) -> Checkpoint3:
        if self.sequence >= self.max_entries:
            raise TaskStopped("CHECKPOINT_LIMIT")
        item = Checkpoint3(
            sequence=self.sequence + 1,
            kind=kind,
            artifact=artifact,
            sha256=file_digest(self.checked_artifact(artifact)),
        )
        data = item.model_dump_json().encode()
        if len(data) > self.max_bytes:
            raise TaskStopped("CHECKPOINT_BYTE_LIMIT")
        pending = self.directory / (uuid4().hex + ".pending")
        final = self.directory / f"{item.sequence:06d}.json"
        with pending.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        # Atomic no-overwrite publication; .pending is never evidence.
        os.link(pending, final)
        pending.unlink()
        sync_directory(self.directory)
        self.sequence = item.sequence
        return item

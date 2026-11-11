"""V3 internal worker/execution contracts, separate from frozen sampling-3."""

import os
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from tokenscope.analysis_common.contracts import Contract, Digest
from tokenscope.analysis_common.contracts_v3 import PreparationRequest3
from tokenscope.analysis_common.runtime_v3 import Checkpoint3, RuntimeProfile3
from tokenscope.analysis_common.sampling_v3 import SampleLimits
from tokenscope.errors import TokenScopeError


class WorkerSpec3(Contract):
    job_id: str = Field(pattern=r"^(prep|diag)-[0-9a-f]{32}$")
    action: Literal["prepare", "diagnose"]
    input_root: str
    state_root: str
    asset_root: str
    job_root: str
    request: PreparationRequest3
    profile: RuntimeProfile3
    parent_pid: int = Field(gt=0)
    sample_preparation_id: str | None = Field(default=None, pattern=r"^prep-[0-9a-f]{32}$")


class Execution3(Contract):
    version: Literal["diagnostics-execution-3"] = "diagnostics-execution-3"
    task_id: str
    state: Literal["queued", "running", "completed", "stopped", "failed", "interrupted"]
    phase: str
    reason_code: str | None = None
    profile_digest: Digest | None = None
    checkpoints: tuple[Checkpoint3, ...] = ()
    telemetry: dict[str, Any] = Field(default_factory=dict)
    cancel_requested: bool = False
    exit_code: int | None = None
    forced_termination: bool = False


def available_memory() -> int:
    """Include a visible cgroup limit, never assume host RAM belongs to this job."""
    available = 0
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            available = int(line.split()[1]) * 1024
            break
    cgroup = Path("/sys/fs/cgroup")
    maximum, current = cgroup / "memory.max", cgroup / "memory.current"
    if maximum.is_file() and current.is_file():
        text = maximum.read_text().strip()
        if text != "max":
            available = min(available, max(0, int(text) - int(current.read_text())))
    if available <= 0:
        raise TokenScopeError("RESOURCE_ENFORCEMENT_UNAVAILABLE", "No available memory bound", 503)
    return available


def automatic_profile(
    *, available_bytes: int, source_bytes: int, cpu_budget: int
) -> RuntimeProfile3:
    # This is an upper envelope. After native-model calibration, sample capacity
    # is tightened again using measured VmPeak; callers cannot enlarge it.
    address = available_bytes * 65 // 100
    if address < 512 * 1024 * 1024:
        raise TokenScopeError("RESOURCE_ENVIRONMENT_LIMIT", "Insufficient worker headroom", 503)
    metadata = min(8 * 1024 * 1024, address // 128)
    raw = address // 32
    tokens = address // 512
    requests = min(1024, max(2, raw // 65536))
    disk = raw + tokens * 4 + requests * 65536 + metadata
    verification = (max(1, source_bytes) + metadata * 8) * 8
    # Full-source integrity I/O is budgeted separately, not rejected against the
    # small raw-body sample cap. Deadline includes its planned streaming cost.
    deadline_ms = (120 + verification // (8 * 1024 * 1024) + tokens // 5000) * 1000
    return RuntimeProfile3(
        address_space_bytes=address,
        soft_rss_bytes=address * 85 // 100,
        deadline_ms=deadline_ms,
        phase_deadlines_ms={
            "verification": deadline_ms,
            "model": 60000,
            "selection": deadline_ms,
            "snapshot": 120000,
        },
        cpu_budget=min(cpu_budget, os.cpu_count() or 1, 1 if address < 1024**3 else 8),
        max_file_bytes=max(raw, disk),
        sample=SampleLimits(
            max_requests=requests,
            max_raw_bytes=raw,
            max_prompt_tokens=tokens,
            max_record_bytes=raw // 2,
            max_record_tokens=tokens // 2,
            max_metadata_bytes=metadata,
            max_snapshot_bytes=disk,
            max_exclusion_examples=32,
        ),
        budgets={
            "metadata_rows": max(1, verification // 32),
            "metadata_bytes": verification,
            "verification_bytes": verification,
            "snapshot_bytes": disk * 3,
            "requests": requests * 12,
            "raw_read_bytes": raw * 12,
            "token_read_bytes": tokens * 4 * 12,
            "comparisons": min(20000, requests * 32),
            "comparison_bytes": raw * 32,
            "encoding_calls": requests * 8,
            "encoding_input_bytes": raw * 8,
            "encoding_output_tokens": tokens * 8,
            "plans": 32,
            "plan_bytes": metadata * 2,
            "result_bytes": metadata * 4,
            "checkpoints": 128,
        },
        max_json_depth=128,
        max_json_nodes=200000,
        max_attempts=3,
    )


def calibrated_sample(profile: RuntimeProfile3, peak_virtual_bytes: int) -> SampleLimits:
    headroom = profile.address_space_bytes - peak_virtual_bytes - 128 * 1024 * 1024
    # Keep the same 128 MiB safety reserve and expansion factors. A small
    # positive capacity must become a smaller sample, not an arbitrary 16 MiB
    # minimum that rejects otherwise admissible short requests.
    if headroom < 1024 * 1024:
        raise TokenScopeError(
            "RESOURCE_FIXED_OVERHEAD_LIMIT", "Model fixed overhead leaves no sample capacity", 503
        )
    sample = profile.sample
    raw = min(sample.max_raw_bytes, headroom // 16)
    tokens = min(sample.max_prompt_tokens, headroom // 256)
    return SampleLimits(
        max_requests=min(sample.max_requests, max(2, raw // 65536)),
        max_raw_bytes=raw,
        max_prompt_tokens=tokens,
        max_record_bytes=min(sample.max_record_bytes, raw // 2),
        max_record_tokens=min(sample.max_record_tokens, tokens // 2),
        max_metadata_bytes=sample.max_metadata_bytes,
        max_snapshot_bytes=sample.max_snapshot_bytes,
        max_exclusion_examples=sample.max_exclusion_examples,
        review_requested=sample.review_requested,
    )

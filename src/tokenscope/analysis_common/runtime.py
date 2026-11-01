"""Versioned task options; separate from the frozen plugin wire contract."""

from collections.abc import Callable
from dataclasses import dataclass

from pydantic import Field

from tokenscope.analysis_common.contracts import Contract, RequestView
from tokenscope.analysis_common.plugins import ExecutionStopped, PluginSelection


class RuntimeOptions(Contract):
    version: str = "diagnostics-runtime-1"
    token_selection: PluginSelection
    candidate_limit: int = Field(ge=1, le=128)
    pilot_limit: int = Field(ge=2)
    max_source_requests: int = Field(ge=1)
    max_source_bytes: int = Field(ge=1)
    max_findings: int = Field(ge=1)
    max_experiments: int = Field(ge=1)
    max_combinations: int = Field(ge=0)
    max_encoding_calls: int = Field(ge=1)
    max_plan_bytes: int = Field(default=16 * 1024 * 1024, ge=1)


@dataclass
class TaskControl:
    options: RuntimeOptions
    cancelled: Callable[[], bool]
    encoding_calls: int = 0
    findings: int = 0

    def checkpoint(self) -> None:
        if self.cancelled():
            raise ExecutionStopped("ANALYSIS_INTERRUPTED")

    def request(self, request: RequestView) -> None:
        self.checkpoint()
        if (
            len(request.raw_body.encode("utf-8"))
            > self.options.token_selection.budget.max_request_bytes
        ):
            raise ExecutionStopped("REQUEST_BYTES_EXHAUSTED")

    def encode(self) -> None:
        self.checkpoint()
        if self.encoding_calls >= self.options.max_encoding_calls:
            raise ExecutionStopped("ENCODING_BUDGET_EXHAUSTED")
        self.encoding_calls += 1

    def comparison(self, left: RequestView, right: RequestView) -> None:
        self.checkpoint()
        if (
            len(left.raw_body.encode()) + len(right.raw_body.encode())
            > self.options.token_selection.budget.max_comparison_bytes
        ):
            raise ExecutionStopped("COMPARISON_BYTES_EXHAUSTED")

    def finding(self) -> None:
        self.checkpoint()
        if self.findings >= self.options.max_findings:
            raise ExecutionStopped("FINDING_BUDGET_EXHAUSTED")
        self.findings += 1

    def plan(self, size: int) -> None:
        self.checkpoint()
        if size > self.options.max_plan_bytes:
            raise ExecutionStopped("PLAN_BYTES_EXHAUSTED")

"""V2 retention and instrumentation overlay; frozen RuntimeOptions remains unchanged."""

from collections.abc import Callable
from dataclasses import dataclass, field

from tokenscope.analysis_common.contracts import RequestView
from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.runtime import RuntimeOptions
from tokenscope.analysis_common.runtime import TaskControl as LegacyTaskControl
from tokenscope.analysis_common.telemetry import Telemetry


@dataclass
class TaskControl(LegacyTaskControl):
    options: RuntimeOptions
    cancelled: Callable[[], bool]
    encoding_calls: int = 0
    findings: int = 0
    direction: str = "task"
    lane: str = "default"
    telemetry: Telemetry = field(default_factory=Telemetry)
    retained: dict[str, int] = field(default_factory=dict)
    retained_bytes: dict[str, int] = field(default_factory=dict)
    detected: dict[str, int] = field(default_factory=dict)
    comparisons: dict[str, int] = field(default_factory=dict)

    @property
    def v2(self) -> bool:
        return self.options.version == "diagnostics-runtime-2"

    def limit(self, name: str) -> int:
        return int(self.options.model_dump()[name])

    def fork(self, direction: str) -> "TaskControl":
        return TaskControl(
            self.options, self.cancelled, direction=direction, telemetry=self.telemetry
        )

    def retain(self, rule: str, size: int) -> bool:
        self.checkpoint()
        if not self.v2:
            self.finding()
            return True
        if rule not in ("L1", "L2", "L3", "L4", "L5") or size < 0:
            raise ValueError("Invalid retention input")
        self.detected[rule] = self.detected.get(rule, 0) + 1
        self.telemetry.count("low_hit." + rule + ".detected")
        # Fixed rule reservations prevent frequent L4 evidence from starving L1/L3/L5.
        index = int(rule[1:]) - 1
        quota = self.options.max_findings // 5 + (index < self.options.max_findings % 5)
        byte_limit = self.limit("max_retained_bytes")
        byte_quota = byte_limit // 5 + (index < byte_limit % 5)
        if (
            self.retained.get(rule, 0) >= quota
            or self.retained_bytes.get(rule, 0) + size > byte_quota
        ):
            self.telemetry.count("low_hit." + rule + ".omitted")
            return False
        self.retained[rule] = self.retained.get(rule, 0) + 1
        self.retained_bytes[rule] = self.retained_bytes.get(rule, 0) + size
        self.telemetry.count("low_hit." + rule + ".retained")
        self.telemetry.count("low_hit.retained_bytes", size)
        return True

    @property
    def retention_complete(self) -> bool:
        return all(n == self.retained.get(rule, 0) for rule, n in self.detected.items())

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
        self.telemetry.count(self.direction + ".encoding_calls")

    def comparison(self, left: RequestView, right: RequestView) -> None:
        self.checkpoint()
        if self.v2:
            n = self.comparisons.get(self.lane, 0)
            if n >= self.limit("max_comparisons"):
                raise ExecutionStopped("COMPARISON_COUNT_BUDGET_EXHAUSTED")
            self.comparisons[self.lane] = n + 1
            self.telemetry.count("low_hit." + self.lane + ".comparisons")
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


def retain_finding(control: LegacyTaskControl | None, rule: str, size: int) -> bool:
    if control is None:
        return True
    if isinstance(control, TaskControl):
        return control.retain(rule, size)
    control.finding()
    return True

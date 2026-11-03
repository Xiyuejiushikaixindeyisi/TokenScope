"""Monotonic stage measurements; no raw content or inferred terminal durations."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from time import perf_counter_ns


@dataclass
class Telemetry:
    durations: dict[str, int] = field(default_factory=dict)
    counters: dict[str, int] = field(default_factory=dict)

    @contextmanager
    def span(self, name: str) -> Iterator[None]:
        start = perf_counter_ns()
        try:
            yield
        finally:
            self.durations[name] = self.durations.get(name, 0) + perf_counter_ns() - start

    def count(self, name: str, amount: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + amount

    def view(self) -> dict[str, object]:
        return {
            "version": "diagnostics-telemetry-2",
            "clock": "perf_counter_ns",
            "elapsed_ns": {k: str(v) for k, v in sorted(self.durations.items())},
            "counts": {k: str(v) for k, v in sorted(self.counters.items())},
        }

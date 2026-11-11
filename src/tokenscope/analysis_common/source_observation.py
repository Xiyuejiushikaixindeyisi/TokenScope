"""Optional worker-only monotonic source instrumentation; GET uses original reader."""

import sqlite3
from collections.abc import Generator, Iterator
from dataclasses import dataclass
from typing import Any

from tokenscope.analysis_common.contracts import RequestView
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.analysis_common.telemetry import Telemetry


@dataclass(frozen=True)
class ObservedSource(ResolvedSource):
    telemetry: Telemetry

    def verify(self) -> None:
        with self.telemetry.span("source_verification"):
            super().verify()

    def _rows(self, index: int | None = None) -> Iterator[sqlite3.Row]:
        iterator = super()._rows(index)
        try:
            while True:
                with self.telemetry.span("source_fetch"):
                    row = next(iterator, None)
                if row is None:
                    return
                self.telemetry.count("source.rows_read")
                self.telemetry.count("source.raw_bytes_read", len(row["request_input"].encode()))
                yield row
        finally:
            if isinstance(iterator, Generator):
                iterator.close()

    def _view(self, row: sqlite3.Row | dict[str, Any]) -> RequestView:
        with self.telemetry.span("source_decode_and_identity"):
            return super()._view(row)

    def read_ids(self, request: RequestView) -> list[int]:
        with self.telemetry.span("source_token_read_inclusive"):
            ids = super().read_ids(request)
        self.telemetry.count("source.token_ids_read", len(ids))
        return ids

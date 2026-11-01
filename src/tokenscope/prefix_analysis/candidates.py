"""Disk-backed bounded predecessor lookup; insert only after inspecting the request."""

import sqlite3
from pathlib import Path

from tokenscope.analysis_common.contracts import RequestKey


class CandidateIndex:
    def __init__(self, path: Path, base_run_id: str, limit: int) -> None:
        if limit <= 0:
            raise ValueError("Candidate limit must be positive")
        self.db = sqlite3.connect(path)
        self.db.execute(
            "CREATE TABLE candidates (channel TEXT, fingerprint TEXT, seq INTEGER, "
            "request_index INTEGER, PRIMARY KEY(channel,fingerprint,seq))"
        )
        self.base_run_id, self.limit, self.seq = base_run_id, limit, 0

    def lookup(self, channel: str, fingerprint: str) -> tuple[tuple[RequestKey, ...], bool]:
        rows = self.db.execute(
            "SELECT request_index FROM candidates WHERE channel=? AND "
            "fingerprint=? ORDER BY seq DESC LIMIT ?",
            (channel, fingerprint, self.limit + 1),
        ).fetchall()
        return tuple(
            RequestKey(base_run_id=self.base_run_id, source_record_index=row[0])
            for row in rows[: self.limit]
        ), len(rows) > self.limit

    def insert(self, key: RequestKey, channels: dict[str, str]) -> None:
        if key.base_run_id != self.base_run_id:
            raise ValueError("Foreign candidate source")
        self.seq += 1
        self.db.executemany(
            "INSERT INTO candidates VALUES (?,?,?,?)",
            [
                (channel, fingerprint, self.seq, key.source_record_index)
                for channel, fingerprint in channels.items()
            ],
        )

    def close(self) -> None:
        self.db.close()

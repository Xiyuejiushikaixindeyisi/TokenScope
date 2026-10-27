"""Logical discrete events over an unlimited disk-backed prefix ledger, without KV tensors."""

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from tokenscope.domain import ModelSettings, capability
from tokenscope.encoding.batch import ids_bytes
from tokenscope.encoding.shards import TokenSlice, read_slice
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.storage import RawRequestStore

EVENTS = (
    "REQUEST_ARRIVED",
    "CACHE_LOOKUP",
    "PREFILL_COMPLETED",
    "CACHE_PUBLISHED",
    "REQUEST_FINISHED",
)


@dataclass(frozen=True)
class CacheResult:
    hit_tokens: int
    compute_tokens: int
    matched_blocks: int
    published_blocks: int
    status: str


class PrefixLedger:
    def __init__(self, path: Path) -> None:
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA cache_size=-8192")
        self.db.execute("CREATE TABLE prefixes (key BLOB PRIMARY KEY) WITHOUT ROWID")

    def contains(self, key: bytes) -> bool:
        return self.db.execute("SELECT 1 FROM prefixes WHERE key=?", (key,)).fetchone() is not None

    def publish(self, keys: list[bytes]) -> None:
        self.db.executemany("INSERT OR IGNORE INTO prefixes VALUES (?)", ((k,) for k in keys))

    def close(self) -> None:
        self.db.commit()
        self.db.close()


class CacheStrategy(Protocol):
    def process(self, appid: str, ids: list[int]) -> CacheResult: ...


class FullBlockStrategy:
    def __init__(self, settings: ModelSettings, asset_identity: str, ledger: PrefixLedger) -> None:
        self.settings, self.asset_identity, self.ledger = settings, asset_identity, ledger

    def process(self, appid: str, ids: list[int]) -> CacheResult:
        size = self.settings.effective_block_size
        parent = hashlib.sha256(
            json.dumps(
                [
                    "chain-sha256-uint32le-v1",
                    self.settings.model_id,
                    self.asset_identity,
                    appid,
                    size,
                ],
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode()
        ).digest()
        keys = []
        for start in range(0, len(ids) - size + 1, size):
            parent = hashlib.sha256(parent + ids_bytes(ids[start : start + size])).digest()
            keys.append(parent)
        limit = max(len(ids) - 1, 0) // size
        matched = 0
        for key in keys[:limit]:
            if not self.ledger.contains(key):
                break
            matched += 1
        hit = max(matched - int(self.settings.mtp), 0) * size
        # Publication follows lookup: the request never hits its own new cache entries.
        self.ledger.publish(keys)
        return CacheResult(hit, len(ids) - hit, matched, len(keys), "available")


class NoCacheStrategy:
    def process(self, appid: str, ids: list[int]) -> CacheResult:
        return CacheResult(0, len(ids), 0, 0, "disabled")


class QwenHybridStrategy:
    def process(self, appid: str, ids: list[int]) -> CacheResult:
        raise TokenScopeError("UNSUPPORTED_CACHE_MODE", "Qwen hybrid is reserved", 422)


class DeepSeekHybridStrategy:
    def process(self, appid: str, ids: list[int]) -> CacheResult:
        raise TokenScopeError("UNSUPPORTED_CACHE_MODE", "DeepSeek hybrid is reserved", 422)


def make_strategy(
    settings: ModelSettings,
    asset_identity: str,
    ledger: PrefixLedger,
) -> CacheStrategy:
    if not capability(settings).executable:
        raise TokenScopeError("UNSUPPORTED_CACHE_MODE", "Enhanced hybrid is reserved", 422)
    if not settings.prefix_cache_enabled:
        return NoCacheStrategy()
    return FullBlockStrategy(settings, asset_identity, ledger)


def replay(
    store: RawRequestStore,
    token_directory: Path,
    settings: ModelSettings,
    asset_identity: str,
    ledger_path: Path,
) -> None:
    ledger = PrefixLedger(ledger_path)
    try:
        strategy = make_strategy(settings, asset_identity, ledger)
        with store.connect() as read, store.connect() as write:
            if not read.execute("SELECT complete FROM encoding_status").fetchone()[0]:
                raise TokenScopeError("ENCODING_INCOMPLETE", "Encoding has not finished", 409)
            if read.execute(
                "SELECT 1 FROM encoded_requests WHERE cache_status IS NOT NULL"
            ).fetchone():
                raise TokenScopeError("REPLAY_ALREADY_STARTED", "Use a new run for replay", 409)
            count = 0
            for row in read.execute("""SELECT * FROM request_records
                JOIN encoded_requests USING(source_record_index)
                ORDER BY appid,time_ns,source_record_index"""):
                ref = TokenSlice.model_validate_json(row["token_slice_json"])
                ids = read_slice(token_directory, ref)
                result = strategy.process(row["appid"], ids)
                events = [
                    dict(
                        type=name,
                        local_event_seq=index + 1,
                        time_ns=row["time_ns"],
                        source_record_index=row["source_record_index"],
                    )
                    for index, name in enumerate(EVENTS)
                ]
                events[1]["matched_blocks_before_mtp"] = result.matched_blocks
                events[3]["published_full_blocks"] = result.published_blocks
                write.execute(
                    """UPDATE encoded_requests SET ideal_cached_input_tokens=?,
                    ideal_compute_input_tokens=?,cache_status=?,events_json=?
                    WHERE source_record_index=?""",
                    (
                        result.hit_tokens,
                        result.compute_tokens,
                        result.status,
                        json.dumps(events),
                        row["source_record_index"],
                    ),
                )
                count += 1
                if count % 256 == 0:
                    write.commit()
                    ledger.db.commit()
            write.execute("CREATE TABLE replay_status (complete INTEGER NOT NULL)")
            write.execute("INSERT INTO replay_status VALUES (1)")
    finally:
        ledger.close()

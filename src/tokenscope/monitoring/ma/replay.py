"""Bounded shared encoding and per-instance warmup/replay orchestration."""

import json
import sqlite3
from pathlib import Path

from tokenscope.domain import ModelSettings
from tokenscope.encoding.batch import EncodingBatchService, EncodingFailure
from tokenscope.encoding.shards import TokenShardWriter, TokenSlice, read_slice
from tokenscope.monitoring.ma.ingest import connect
from tokenscope.monitoring.simulation import PrefixLedger, make_strategy


def encode(
    path: Path,
    directory: Path,
    encoder: EncodingBatchService,
    batch_rows: int = 256,
    batch_bytes: int = 16 * 1024 * 1024,
) -> None:
    if min(batch_rows, batch_bytes) <= 0:
        raise ValueError("invalid encoding budget")
    writer = TokenShardWriter(directory)
    try:
        # Fetch bounded batches before write commits, avoiding a second connection reader lock.
        last = 0
        while True:
            with connect(path) as db:
                rows: list[sqlite3.Row] = []
                size = 0
                cursor = db.execute(
                    "SELECT * FROM records WHERE candidate=1 AND id>? ORDER BY id", (last,)
                )
                for row in cursor:
                    length = len(row["request_input"].encode())
                    if rows and (len(rows) >= batch_rows or size + length > batch_bytes):
                        break
                    rows.append(row)
                    size += length
                cursor.close()
                if not rows:
                    break
                results = encoder.encode_batch([row["request_input"] for row in rows])
                for row, result in zip(rows, results, strict=True):
                    if isinstance(result, EncodingFailure):
                        db.execute(
                            "INSERT INTO issues VALUES (?,?,?,?,?,?)",
                            (
                                row["role"],
                                row["source_record_index"],
                                row["line_start"],
                                row["line_end"],
                                result.field,
                                result.code,
                            ),
                        )
                    else:
                        ref = writer.append(result.prompt_ids)
                        db.execute(
                            "UPDATE records SET local_prompt=?,token_slice=?,evidence=? WHERE id=?",
                            (
                                result.prompt_tokens,
                                ref.model_dump_json(),
                                json.dumps(result.light_evidence),
                                row["id"],
                            ),
                        )
                last = rows[-1]["id"]
    finally:
        writer.close()


def replay(
    path: Path,
    directory: Path,
    settings: ModelSettings,
    asset_identity: str,
    model_standard_name: str,
    ledger_directory: Path,
) -> None:
    ledger_directory.mkdir()
    with connect(path) as db:
        # Cursor is scope-sized, never a list of all request bodies or tokens.
        uuids = db.execute(
            "SELECT DISTINCT instance_uuid FROM records WHERE assigned=1 ORDER BY instance_uuid"
        )
        for sequence, (uuid,) in enumerate(uuids):
            bounds = db.execute(
                """SELECT
                max(CASE WHEN role='pre' THEN handle_ns END),
                min(CASE WHEN role='now' THEN handle_ns END),
                count(CASE WHEN role='pre' THEN 1 END)
                FROM records WHERE instance_uuid=? AND local_prompt IS NOT NULL""",
                (uuid,),
            ).fetchone()
            now_count = db.execute(
                "SELECT count(*) FROM records WHERE instance_uuid=? AND assigned=1 AND role='now'",
                (uuid,),
            ).fetchone()[0]
            conflict = bounds[0] is not None and bounds[1] is not None and bounds[0] > bounds[1]
            status = (
                "warmup_order_conflict"
                if conflict
                else "empty_now"
                if not now_count
                else "no_valid_prewarm"
                if not bounds[2]
                else "available"
            )
            db.execute("INSERT INTO scopes VALUES (?,?)", (uuid, status))
            if conflict:
                continue
            ledger = PrefixLedger(ledger_directory / f"{sequence}.sqlite3")
            try:
                strategy = make_strategy(settings, asset_identity, ledger)
                scope = json.dumps(
                    ["ma-v1", model_standard_name, uuid], ensure_ascii=False, separators=(",", ":")
                )
                cursor = db.execute(
                    """SELECT id,token_slice FROM records WHERE instance_uuid=?
                    AND local_prompt IS NOT NULL ORDER BY CASE role WHEN 'pre' THEN 0 ELSE 1 END,
                    handle_ns,source_record_index""",
                    (uuid,),
                )
                for count, row in enumerate(cursor, 1):
                    ids = read_slice(directory, TokenSlice.model_validate_json(row["token_slice"]))
                    result = strategy.process(scope, ids)
                    db.execute(
                        "UPDATE records SET ideal_hit=? WHERE id=?", (result.hit_tokens, row["id"])
                    )
                    if count % 256 == 0:
                        ledger.db.commit()
            finally:
                ledger.close()

"""Bounded encoding stage; successful facts and rejected rows share an auditable input DB."""

import json
from pathlib import Path

from tokenscope.domain import Quality
from tokenscope.encoding.batch import EncodingBatchService, EncodingFailure
from tokenscope.encoding.shards import TokenShardWriter
from tokenscope.ingestion.csv_reader import RequestRecord
from tokenscope.monitoring.storage import RawRequestStore


def encode_input(
    store: RawRequestStore,
    encoder: EncodingBatchService,
    directory: Path,
    *,
    batch_rows: int = 256,
    batch_bytes: int = 16 * 1024 * 1024,
) -> Quality:
    if batch_rows <= 0 or batch_bytes <= 0:
        raise ValueError("Batch limits must be positive")
    with store.connect() as db:
        db.execute("""CREATE TABLE encoded_requests (
            source_record_index INTEGER PRIMARY KEY REFERENCES request_records,
            json_tokens INTEGER NOT NULL, prompt_tokens INTEGER NOT NULL,
            token_slice_json TEXT NOT NULL, encoder_identity TEXT NOT NULL,
            evidence_json TEXT NOT NULL, ideal_cached_input_tokens INTEGER,
            ideal_compute_input_tokens INTEGER, cache_status TEXT, events_json TEXT)""")
        db.execute("CREATE TABLE encoding_status (complete INTEGER, quality_json TEXT)")
        db.execute("INSERT INTO encoding_status VALUES (0,NULL)")
    writer = TokenShardWriter(directory)

    def flush(records: list[RequestRecord]) -> None:
        results = encoder.encode_batch([r.request_input for r in records])
        with store.connect() as db:
            for record, result in zip(records, results, strict=True):
                if isinstance(result, EncodingFailure):
                    db.execute(
                        "INSERT INTO row_errors VALUES (?,?,?,?,?)",
                        (
                            record.source_record_index,
                            record.physical_line_start,
                            record.physical_line_end,
                            result.code,
                            result.field,
                        ),
                    )
                    continue
                ref = writer.append(result.prompt_ids)
                db.execute(
                    "INSERT INTO encoded_requests VALUES (?,?,?,?,?,?,NULL,NULL,NULL,NULL)",
                    (
                        record.source_record_index,
                        result.json_tokens,
                        result.prompt_tokens,
                        ref.model_dump_json(),
                        result.encoder_identity,
                        json.dumps(result.light_evidence, ensure_ascii=False),
                    ),
                )

    try:
        records: list[RequestRecord] = []
        size = 0
        for record in store.replay_records():
            length = len(record.request_input.encode())
            if records and (len(records) >= batch_rows or size + length > batch_bytes):
                flush(records)
                records, size = [], 0
            records.append(record)
            size += length
        if records:
            flush(records)
    finally:
        writer.close()
    with store.connect() as db:
        original = Quality.model_validate_json(
            db.execute("SELECT quality_json FROM input_status").fetchone()[0]
        )
        valid = db.execute("SELECT count(*) FROM encoded_requests").fetchone()[0]
        # Duplicates are a property of the final valid set, not rejected predecessors.
        distinct = db.execute("""SELECT count(DISTINCT hash_id) FROM request_records
            JOIN encoded_requests USING(source_record_index)""").fetchone()[0]
        quality = Quality(
            records_read=original.records_read,
            valid_requests=valid,
            skipped_rows=original.records_read - valid,
            duplicate_hash_id_rows=valid - distinct,
        )
        db.execute(
            "UPDATE encoding_status SET complete=1,quality_json=?", (quality.model_dump_json(),)
        )
    return quality

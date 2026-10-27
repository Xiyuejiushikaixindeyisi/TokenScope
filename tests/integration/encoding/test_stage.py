import json
from pathlib import Path

import pytest
from conftest import csv_bytes, valid_row

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.encoding.assets import AssetRegistry
from tokenscope.encoding.batch import EncodingBatchService
from tokenscope.encoding.models import ModelEncoder
from tokenscope.encoding.shards import TokenSlice, read_slice
from tokenscope.encoding.stage import encode_input
from tokenscope.ingestion.csv_reader import CsvBatchReader
from tokenscope.monitoring.simulation import EVENTS, replay
from tokenscope.monitoring.storage import RawRequestStore

ROOT = Path(__file__).resolve().parents[3]


def test_stage_retains_rows_and_seals_shards(tmp_path):
    settings = DEFAULT_SETTINGS["GLM-5.2"]
    encoder = EncodingBatchService(
        ModelEncoder(AssetRegistry(ROOT).load(settings.model_id), settings)
    )
    source = tmp_path / "input.csv"
    source.write_bytes(
        csv_bytes(
            [
                valid_row(),
                valid_row(),
                valid_row(completion_tokens="bad"),
                valid_row(
                    request_input=json.dumps(
                        {
                            "messages": [{"role": "user", "content": "bad mode"}],
                            "chat_template_kwargs": {"continue_final_message": True},
                        }
                    )
                ),
            ]
        )
    )
    store = RawRequestStore(tmp_path / "requests.sqlite3")
    store.ingest(source, CsvBatchReader(settings))
    quality = encode_input(store, encoder, tmp_path / "tokens", batch_rows=1)
    assert quality.model_dump() == dict(
        records_read=4, valid_requests=2, skipped_rows=2, duplicate_hash_id_rows=1
    )
    with store.connect() as db:
        rows = db.execute("SELECT * FROM encoded_requests").fetchall()
        assert len(rows) == 2
        assert db.execute("SELECT complete FROM encoding_status").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM row_errors").fetchone()[0] == 2
    for row in rows:
        ref = TokenSlice.model_validate_json(row["token_slice_json"])
        assert len(read_slice(tmp_path / "tokens", ref)) == row["prompt_tokens"]
        assert encoder.explain(valid_row()[4], ref.sha256)["ids_digest"] == ref.sha256
    replay(
        store,
        tmp_path / "tokens",
        settings.model_copy(update={"block_size": 2}),
        encoder.encoder.assets.identity,
        tmp_path / "ledger.sqlite3",
    )
    with store.connect() as db:
        results = db.execute(
            "SELECT * FROM encoded_requests ORDER BY source_record_index"
        ).fetchall()
        assert results[0]["ideal_cached_input_tokens"] == 0
        assert results[1]["ideal_cached_input_tokens"] > 0
        for row in results:
            assert (
                row["prompt_tokens"]
                == row["ideal_cached_input_tokens"] + row["ideal_compute_input_tokens"]
            )
            events = json.loads(row["events_json"])
            assert tuple(e["type"] for e in events) == EVENTS
            assert [e["local_event_seq"] for e in events] == [1, 2, 3, 4, 5]


def test_stage_failure_is_not_complete(tmp_path, monkeypatch):
    source = tmp_path / "input.csv"
    source.write_bytes(csv_bytes([valid_row()]))
    store = RawRequestStore(tmp_path / "requests.sqlite3")
    store.ingest(source, CsvBatchReader(DEFAULT_SETTINGS["GLM-5.2"]))

    class Broken:
        def encode_batch(self, rows):
            raise OSError("injected write failure")

    with pytest.raises(OSError):
        encode_input(store, Broken(), tmp_path / "tokens")
    with store.connect() as db:
        assert db.execute("SELECT complete FROM encoding_status").fetchone()[0] == 0

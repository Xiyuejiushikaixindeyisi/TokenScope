import json
from pathlib import Path

import pytest

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.encoding.batch import EncodingBatchService
from tokenscope.encoding.models import ModelEncoder
from tokenscope.monitoring.ma.ingest import connect, ingest, initialize
from tokenscope.monitoring.ma.replay import encode, replay
from tokenscope.monitoring.pipeline import profile_for
from tokenscope.monitoring.service import MonitoringService

from .helpers import binding, row, write_csv


@pytest.mark.parametrize("model", list(DEFAULT_SETTINGS))
def test_real_assets_share_only_within_uuid(
    tmp_path: Path, service: MonitoringService, model: str
) -> None:
    settings = DEFAULT_SETTINGS[model].model_copy(
        update={"mtp": False, "encoding_profile": "thinking_disabled"}
    )
    assets = service.assets.load(model)
    encoder = EncodingBatchService(ModelEncoder(assets, settings, profile_for(settings, 8)))
    raw = json.dumps({"messages": [{"role": "user", "content": "hello world " * 2000}]})
    request = binding().model_copy(update={"model_id": model})
    pre, now, db = tmp_path / "pre.csv", tmp_path / "now.csv", tmp_path / "facts.db"
    write_csv(pre, [row("pre", request_input=raw, appid="first", cached_tokens="")])
    write_csv(
        now, [row(request_input=raw, appid="second"), row(request_input=raw, instance_uuid="B")]
    )
    initialize(db)
    ingest(db, pre, "pre", request, settings)
    ingest(db, now, "now", request, settings)
    encode(db, tmp_path / "tokens", encoder, batch_rows=1, batch_bytes=128)
    replay(
        db,
        tmp_path / "tokens",
        settings,
        assets.identity,
        request.model_standard_name,
        tmp_path / "ledgers",
    )
    with connect(db) as con:
        a = con.execute("SELECT * FROM records WHERE role='now' AND instance_uuid='A'").fetchone()
        b = con.execute("SELECT * FROM records WHERE role='now' AND instance_uuid='B'").fetchone()
        assert (
            a["ideal_hit"]
            == ((a["local_prompt"] - 1) // settings.effective_block_size)
            * settings.effective_block_size
        )
        assert a["ideal_hit"] > 0
        assert b["ideal_hit"] == 0
        assert a["appid"] == "second"


def test_conflict_does_not_discard_real(tmp_path: Path, service: MonitoringService) -> None:
    settings = DEFAULT_SETTINGS["Qwen3.6-27B"]
    assets = service.assets.load(settings.model_id)
    encoder = EncodingBatchService(ModelEncoder(assets, settings, profile_for(settings, 8)))
    db = tmp_path / "facts.db"
    initialize(db)
    for role, records in (
        ("pre", [row("pre", model_handle_start_time="2026-10-20T08:02:00Z")]),
        ("now", [row()]),
    ):
        source = tmp_path / f"{role}.csv"
        write_csv(source, records)
        ingest(db, source, role, binding(), settings)
    encode(db, tmp_path / "tokens", encoder)
    replay(db, tmp_path / "tokens", settings, assets.identity, "q-64K", tmp_path / "ledgers")
    with connect(db) as con:
        assert con.execute("SELECT status FROM scopes").fetchone()[0] == "warmup_order_conflict"
        assert (
            con.execute("SELECT count(*) FROM records WHERE ideal_hit IS NOT NULL").fetchone()[0]
            == 0
        )
        assert con.execute("SELECT cached_tokens FROM records WHERE role='now'").fetchone()[0] == 25

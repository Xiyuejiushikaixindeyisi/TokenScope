from pathlib import Path

import pytest

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.ma.ingest import connect, ingest, initialize, token_cell

from .helpers import binding, row, write_csv


def test_independent_fields_and_original(tmp_path: Path) -> None:
    db = tmp_path / "facts.db"
    source = tmp_path / "now.csv"
    raw = '{"model":"Qwen3.6-27B",\n "messages":[{"role":"user","content":"hi"}]}'
    write_csv(
        source,
        [
            row(request_input=raw, completion_tokens="wrong"),
            row(request_input="{bad"),
            row(cached_tokens=""),
            row(instance_uuid=""),
            row(cached_tokens="101"),
        ],
    )
    initialize(db)
    ingest(db, source, "now", binding(), DEFAULT_SETTINGS["Qwen3.6-27B"])
    with connect(db) as con:
        records = list(con.execute("SELECT * FROM records"))
        assert len(records) == 5
        assert sum(r["assigned"] for r in records) == 4
        assert sum(r["candidate"] for r in records) == 3
        assert records[0]["request_input"] == raw
        assert records[0]["completion_tokens"] is None
        assert records[1]["cached_tokens"] == 25
        assert records[2]["cached_tokens"] is None
        assert records[4]["cached_tokens"] is None
        assert records[0]["line_end"] > records[0]["line_start"]


@pytest.mark.parametrize("value", ["", "-1", "1.0", "NaN", "9223372036854775808"])
def test_bad_token(value: str) -> None:
    with pytest.raises(ValueError):
        token_cell(value)


def test_exact_token() -> None:
    assert token_cell("0009223372036854775807") == 2**63 - 1


def test_boundary_fails_pair(tmp_path: Path) -> None:
    db, source = tmp_path / "facts.db", tmp_path / "pre.csv"
    initialize(db)
    write_csv(source, [row(request_time="2026-10-20T08:00:00Z")])
    with pytest.raises(TokenScopeError, match="Window violation"):
        ingest(db, source, "pre", binding(), DEFAULT_SETTINGS["Qwen3.6-27B"])

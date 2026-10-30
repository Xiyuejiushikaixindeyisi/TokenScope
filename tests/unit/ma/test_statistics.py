import json
from pathlib import Path

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.monitoring.ma.ingest import connect, ingest, initialize
from tokenscope.monitoring.ma.statistics import aggregate, file_quality

from .helpers import binding, row, write_csv


def test_weighted_metrics_partial_bins_and_histograms(tmp_path: Path) -> None:
    db, source = tmp_path / "facts.db", tmp_path / "now.csv"
    initialize(db)
    write_csv(
        source,
        [
            row(prompt_tokens="100", cached_tokens="0"),
            row(prompt_tokens="900", cached_tokens="900", request_input="broken"),
            row(prompt_tokens="200000", cached_tokens="", request_time="2026-10-20T08:06:00Z"),
        ],
    )
    ingest(db, source, "now", binding(), DEFAULT_SETTINGS["Qwen3.6-27B"])
    with connect(db) as con:
        con.execute("INSERT INTO scopes VALUES ('A','no_valid_prewarm')")
        con.execute("UPDATE records SET local_prompt=120,ideal_hit=0 WHERE id=1")
        con.execute("UPDATE records SET local_prompt=200000,ideal_hit=128 WHERE id=3")
    aggregate(db, binding())
    with connect(db) as con:
        value = json.loads(con.execute("SELECT snapshot FROM projections").fetchone()[0])
    assert value["real"]["hit_rate"] == 0.9
    assert value["coverage"] == dict(
        assigned="3", production_input="3", real="2", encoded="2", paired="1"
    )
    assert value["paired_real"]["sample_count"] == "1"
    assert value["mismatched_input_count"] == "1"
    assert value["hour"]["uncached_tokens"] == "100"
    assert value["hour"]["requests_per_second"] == 3 / 3600
    assert value["bins"][1]["pressure"]["uncached_tokens"] is None
    assert value["bins"][2]["pressure"]["uncached_tokens"] == "0"
    assert value["input_histograms"]["5000"]["bins"][-1]["count"] == "1"
    assert value["uncached_histograms"]["5000"]["sample_count"] == "2"
    assert value["zero_uncached_count"] == "1"
    assert file_quality(db)[1].duplicate_hash_rows == "2"


def test_cumulative_tokens_exceed_int64(tmp_path: Path) -> None:
    db, source = tmp_path / "facts.db", tmp_path / "now.csv"
    initialize(db)
    write_csv(source, [row(prompt_tokens=str(2**63 - 1), cached_tokens="0") for _ in range(3)])
    ingest(db, source, "now", binding(), DEFAULT_SETTINGS["Qwen3.6-27B"])
    with connect(db) as con:
        con.execute("INSERT INTO scopes VALUES ('A','no_valid_prewarm')")
    aggregate(db, binding())
    with connect(db) as con:
        value = json.loads(con.execute("SELECT snapshot FROM projections").fetchone()[0])
    assert value["real"]["totals"]["input_tokens"] == str((2**63 - 1) * 3)

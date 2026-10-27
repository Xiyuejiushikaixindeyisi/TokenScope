"""Exact, disk-sorted statistics and precomputed frequency histograms."""

import json
import sqlite3
from collections.abc import Iterable
from typing import Any

LENGTHS = ("json_tokens", "prompt_tokens", "ideal_compute_input_tokens")
TOTALS = (*LENGTHS, "ideal_cached_input_tokens", "completion_tokens")
WIDTHS = (1000, 2000, 5000)


def distribution(sorted_values: Iterable[int], count: int, width: int) -> dict[str, Any]:
    if width not in WIDTHS:
        raise ValueError("Unsupported histogram width")
    bins = [0] * (200000 // width + 1)
    ranks = {
        "p50": (count * 50 + 99) // 100,
        "p80": (count * 80 + 99) // 100,
        "p90": (count * 90 + 99) // 100,
    }
    quantiles: dict[str, int | None] = dict.fromkeys(ranks)
    under = seen = 0
    maximum: int | None = None
    for seen, value in enumerate(sorted_values, 1):
        if value < 0 or (maximum is not None and value < maximum):
            raise ValueError("Distribution requires sorted nonnegative lengths")
        maximum = value
        under += int(value < 8000)
        bins[min(value // width, len(bins) - 1)] += 1
        for label, rank in ranks.items():
            if seen == rank:
                quantiles[label] = value
    if seen != count:
        raise ValueError("Distribution count mismatch")
    mode = max(bins)
    return {
        "bin_width": width,
        "regular_domain": [0, 200000],
        "overflow_start": 200000,
        "boundary": "left_closed_right_open",
        "sample_count": count,
        "quantile_algorithm": "nearest_rank",
        "quantiles": quantiles,
        "bins": [
            dict(
                lower=i * width,
                upper=(i + 1) * width if i < len(bins) - 1 else None,
                count=n,
                share=n / count if count else None,
                overflow=i == len(bins) - 1,
            )
            for i, n in enumerate(bins)
        ],
        "summary": dict(
            mode_bin_indices=[i for i, n in enumerate(bins) if n == mode and n > 0],
            mode_count=mode,
            mode_share=mode / count if count else None,
            under_8k_count=under,
            overflow_count=bins[-1],
            max_length=maximum,
        ),
    }


def aggregate(db: sqlite3.Connection) -> None:
    if not db.execute("SELECT complete FROM replay_status").fetchone()[0]:
        raise ValueError("Replay incomplete")
    db.execute("""CREATE TABLE facts AS SELECT r.hash_id,r.appid,r.time_ns,r.time_utc,
        r.completion_tokens,e.* FROM request_records r JOIN encoded_requests e
        USING(source_record_index)""")
    db.execute("CREATE UNIQUE INDEX fact_ref ON facts(source_record_index)")
    for metric in LENGTHS:
        db.execute(f"CREATE INDEX fact_{metric} ON facts(appid,{metric},source_record_index)")
    db.execute(
        "CREATE TABLE groups (appid TEXT PRIMARY KEY,metrics_json TEXT,histograms_json TEXT)"
    )
    for (appid,) in db.execute("SELECT DISTINCT appid FROM facts ORDER BY appid"):
        totals = dict.fromkeys(TOTALS, 0)
        count = 0
        for row in db.execute(f"SELECT {','.join(TOTALS)} FROM facts WHERE appid=?", (appid,)):
            count += 1
            for name, value in zip(TOTALS, row, strict=True):
                if value is None:
                    raise ValueError("Incomplete metric")
                totals[name] += value
        if (
            totals["prompt_tokens"]
            != totals["ideal_cached_input_tokens"] + totals["ideal_compute_input_tokens"]
        ):
            raise ValueError("Token conservation failed")
        histograms: dict[str, Any] = {}
        quantiles: dict[str, Any] = {}
        for metric in LENGTHS:
            histograms[metric] = {}
            for width in WIDTHS:
                values = (
                    row[0]
                    for row in db.execute(
                        f"SELECT {metric} FROM facts WHERE appid=? "
                        f"ORDER BY {metric},source_record_index",
                        (appid,),
                    )
                )
                histograms[metric][str(width)] = distribution(values, count, width)
            quantiles[metric] = histograms[metric]["5000"]["quantiles"]
        metrics = dict(
            appid=appid,
            request_count=count,
            totals=totals,
            quantiles=quantiles,
            ideal_hit_rate=totals["ideal_cached_input_tokens"] / totals["prompt_tokens"]
            if totals["prompt_tokens"]
            else None,
            json_to_prompt_delta=totals["prompt_tokens"] - totals["json_tokens"],
        )
        db.execute(
            "INSERT INTO groups VALUES (?,?,?)",
            (appid, json.dumps(metrics), json.dumps(histograms)),
        )

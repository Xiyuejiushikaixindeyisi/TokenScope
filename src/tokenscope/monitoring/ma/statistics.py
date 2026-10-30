"""Exact MA aggregates and immutable, precomputed display projections."""

import sqlite3
from pathlib import Path
from typing import Any

from tokenscope.ingestion.csv_reader import parse_utc
from tokenscope.monitoring.ma.contracts import FileQuality, InstanceSnapshot, Submit
from tokenscope.monitoring.ma.ingest import connect
from tokenscope.monitoring.statistics import WIDTHS, distribution
from tokenscope.monitoring.view_models import utc_ns


def wire(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, dict):
        return {str(k): wire(v) for k, v in value.items()}
    if isinstance(value, list):
        return [wire(v) for v in value]
    return value


def metric(count: int, prompt: int, hit: int) -> dict[str, Any]:
    return dict(
        sample_count=str(count),
        totals=dict(
            input_tokens=str(prompt), cached_tokens=str(hit), uncached_tokens=str(prompt - hit)
        ),
        hit_rate=hit / prompt if prompt else None,
    )


def pressure(count: int, real: int, uncached: int, seconds: int) -> dict[str, Any]:
    missing = count > 0 and real == 0
    return dict(
        seconds=seconds,
        request_count=str(count),
        real_count=str(real),
        uncached_tokens=None if missing else str(uncached),
        requests_per_second=count / seconds,
        uncached_tokens_per_second=None if missing else uncached / seconds,
    )


def file_quality(path: Path) -> list[FileQuality]:
    result = []
    with connect(path, readonly=True) as db:
        for role in ("pre", "now"):
            counts = db.execute(
                """SELECT count(*),coalesce(sum(assigned),0),count(local_prompt),
                count(CASE WHEN hash_id IS NOT NULL AND hash_id!='' THEN 1 END)
                -count(DISTINCT CASE WHEN hash_id!='' THEN hash_id END)
                FROM records WHERE role=?""",
                (role,),
            ).fetchone()
            reasons = {
                row[0]: str(row[1])
                for row in db.execute(
                    "SELECT code,count(*) FROM issues WHERE role=? GROUP BY code", (role,)
                )
            }
            result.append(
                FileQuality(
                    role=role,
                    records_read=str(counts[0]),
                    assigned=str(counts[1]),
                    unassigned=str(counts[0] - counts[1]),
                    encoded=str(counts[2]),
                    duplicate_hash_rows=str(counts[3]),
                    reasons=reasons,
                )
            )
    return result


def histograms(db: sqlite3.Connection, uuid: str, *, uncached: bool) -> dict[str, Any]:
    expression = "prompt_tokens-cached_tokens" if uncached else "prompt_tokens"
    condition = " AND cached_tokens IS NOT NULL" if uncached else ""
    where = (
        "instance_uuid=? AND role='now' AND assigned=1 AND prompt_tokens IS NOT NULL" + condition
    )
    count = db.execute(f"SELECT count(*) FROM records WHERE {where}", (uuid,)).fetchone()[0]
    return {
        str(width): wire(
            distribution(
                (
                    row[0]
                    for row in db.execute(
                        f"SELECT {expression} FROM records WHERE {where} ORDER BY {expression}",
                        (uuid,),
                    )
                ),
                count,
                width,
            )
        )
        for width in WIDTHS
    }


def aggregate(path: Path, binding: Submit) -> None:
    start, end = parse_utc(binding.now_start)[0], parse_utc(binding.now_end)[0]
    with connect(path) as db:
        for uuid, status in db.execute(
            "SELECT instance_uuid,status FROM scopes ORDER BY instance_uuid"
        ):
            counts = dict.fromkeys(("a", "p", "r", "e", "q"), 0)
            totals = dict.fromkeys(("p", "rp", "rh", "ep", "eh", "qp", "qh", "qlp", "qlh"), 0)
            mismatch = zero = outside = 0
            low: int | None = None
            high: int | None = None
            buckets = [[0, 0, 0] for _ in range(12)]
            for row in db.execute(
                "SELECT * FROM records WHERE instance_uuid=? AND role='now' AND assigned=1", (uuid,)
            ):
                counts["a"] += 1
                bucket = buckets[(row["request_ns"] - start) // 300_000_000_000]
                bucket[0] += 1
                p, h, lp, lh = (
                    row["prompt_tokens"],
                    row["cached_tokens"],
                    row["local_prompt"],
                    row["ideal_hit"],
                )
                r = p is not None and h is not None
                e = lp is not None and lh is not None
                if p is not None:
                    counts["p"] += 1
                    totals["p"] += p
                if r:
                    counts["r"] += 1
                    totals["rp"] += p
                    totals["rh"] += h
                    bucket[1] += 1
                    bucket[2] += p - h
                    zero += int(p == h)
                if e:
                    counts["e"] += 1
                    totals["ep"] += lp
                    totals["eh"] += lh
                if r and e:
                    counts["q"] += 1
                    for key, value in (("qp", p), ("qh", h), ("qlp", lp), ("qlh", lh)):
                        totals[key] += value
                    mismatch += int(p != lp)
                handle = row["handle_ns"]
                if handle is not None:
                    low = handle if low is None else min(low, handle)
                    high = handle if high is None else max(high, handle)
                    outside += int(not start <= handle < end)
            pre = db.execute(
                "SELECT count(*),count(local_prompt) FROM records "
                "WHERE instance_uuid=? AND role='pre' AND assigned=1",
                (uuid,),
            ).fetchone()
            bins = [
                dict(
                    index=i,
                    start=utc_ns(start + i * 300_000_000_000),
                    end=utc_ns(start + (i + 1) * 300_000_000_000),
                    pressure=pressure(values[0], values[1], values[2], 300),
                )
                for i, values in enumerate(buckets)
            ]
            result = InstanceSnapshot.model_validate(
                dict(
                    instance_uuid=uuid,
                    model_standard_name=binding.model_standard_name,
                    coverage=dict(
                        assigned=str(counts["a"]),
                        production_input=str(counts["p"]),
                        real=str(counts["r"]),
                        encoded=str(counts["e"]),
                        paired=str(counts["q"]),
                    ),
                    pre_assigned=str(pre[0]),
                    pre_encoded=str(pre[1]),
                    ideal_status=status,
                    production_input_tokens=str(totals["p"]),
                    real=metric(counts["r"], totals["rp"], totals["rh"]),
                    ideal=metric(counts["e"], totals["ep"], totals["eh"]),
                    paired_real=metric(counts["q"], totals["qp"], totals["qh"]),
                    paired_ideal=metric(counts["q"], totals["qlp"], totals["qlh"]),
                    mismatched_input_count=str(mismatch),
                    paired_request_coverage=counts["q"] / counts["r"] if counts["r"] else None,
                    paired_input_coverage=totals["qp"] / totals["rp"] if totals["rp"] else None,
                    hour=pressure(counts["a"], counts["r"], totals["rp"] - totals["rh"], 3600),
                    bins=bins,
                    input_histograms=histograms(db, uuid, uncached=False),
                    uncached_histograms=histograms(db, uuid, uncached=True),
                    zero_uncached_count=str(zero),
                    handle_time_min=utc_ns(low),
                    handle_time_max=utc_ns(high),
                    handle_outside_window_count=str(outside),
                    limitations=[
                        "finite_prewarm_not_production_upper_bound",
                        "provided_records_not_full_traffic",
                        "request_time_event_unknown",
                        "chained_approximation_not_hybrid",
                        "equal_lengths_do_not_prove_token_identity",
                        "gf_encoding_equivalence_unverified",
                        "production_topology_and_glm_cp_mapping_not_reproduced",
                    ]
                    + (["input_measurement_mismatch"] if mismatch else []),
                )
            )
            db.execute("INSERT INTO projections VALUES (?,?)", (uuid, result.model_dump_json()))

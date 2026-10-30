"""Disk-backed sparse projection with exact Python accumulation and atomic publication."""

import json
import os
import sqlite3
from itertools import groupby
from pathlib import Path
from typing import Any

from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest, sync_directory
from tokenscope.user_monitoring.contracts import Fraction, ModeBin, RankRow
from tokenscope.user_monitoring.storage import canonical


def populate(source: sqlite3.Connection, target: sqlite3.Connection) -> None:
    target.executescript("""
        CREATE TABLE groups(appid TEXT, width INTEGER, payload TEXT,
          request_count TEXT, ideal_hit_rate TEXT, total_ideal_compute_tokens TEXT,
          typical_ideal_compute_tokens TEXT, PRIMARY KEY(appid,width));
        CREATE TABLE bins(appid TEXT, width INTEGER, lower TEXT, count INTEGER, payload TEXT,
          PRIMARY KEY(appid,width,lower));
        CREATE INDEX modal ON bins(appid,width,count);
        CREATE TABLE metadata(payload TEXT);
    """)
    try:
        source.execute(
            "SELECT prompt_tokens,ideal_cached_input_tokens,"
            "ideal_compute_input_tokens FROM facts LIMIT 0"
        )
    except sqlite3.Error as exc:
        raise TokenScopeError("REANALYSIS_REQUIRED", "Source facts are unavailable", 409) from exc
    for (appid,) in source.execute("SELECT DISTINCT appid FROM facts ORDER BY appid"):
        n = p = h = c = 0
        for pv, hv, cv in source.execute(
            "SELECT prompt_tokens,ideal_cached_input_tokens,ideal_compute_input_tokens "
            "FROM facts WHERE appid=?",
            (appid,),
        ):
            if any(not isinstance(v, int) or v < 0 for v in (pv, hv, cv)) or pv != hv + cv:
                raise TokenScopeError("RESULT_SEAL_INVALID", "Invalid source conservation", 409)
            n, p, h, c = n + 1, p + pv, h + hv, c + cv
        p90 = source.execute(
            "SELECT prompt_tokens FROM facts WHERE appid=? ORDER BY prompt_tokens LIMIT 1 OFFSET ?",
            (appid, (n * 90 + 99) // 100 - 1),
        ).fetchone()[0]
        for width in (1000, 2000, 5000):
            best = ties = 0
            representative: dict[str, Any] = {}
            values = source.execute(
                "SELECT ideal_compute_input_tokens FROM facts WHERE appid=? "
                "ORDER BY ideal_compute_input_tokens",
                (appid,),
            )
            for key, bucket in groupby(values, key=lambda row: row[0] // width):
                count = total = 0
                for (value,) in bucket:
                    count, total = count + 1, total + value
                item = ModeBin(
                    lower=str(key * width),
                    upper=str((key + 1) * width),
                    count=str(count),
                    sum_compute_tokens=str(total),
                    share=count / n,
                    mean=Fraction(numerator=str(total), denominator=str(count)),
                )
                data = item.model_dump(mode="json")
                target.execute(
                    "INSERT INTO bins VALUES(?,?,?,?,?)",
                    (appid, width, str(key * width), count, canonical(data)),
                )
                if count > best:
                    best, ties, representative = count, 1, data
                elif count == best:
                    ties += 1
            mean = representative["mean"]
            result = RankRow(
                appid=appid,
                request_count=str(n),
                total_prompt_tokens=str(p),
                total_ideal_cached_tokens=str(h),
                total_ideal_compute_tokens=str(c),
                ideal_hit_rate=h / p if p else None,
                prompt_p90=str(p90),
                typical_compute_tokens=Fraction.model_validate(mean),
                representative_bin=ModeBin.model_validate(representative),
                tie_count=str(ties),
            )
            target.execute(
                "INSERT INTO groups VALUES(?,?,?,?,?,?,?)",
                (
                    appid,
                    width,
                    result.model_dump_json(),
                    str(n),
                    f"{h}/{p}" if p else None,
                    str(c),
                    mean["numerator"] + "/" + mean["denominator"],
                ),
            )


def build(source_path: Path, destination: Path, metadata: dict[str, Any]) -> str:
    temporary = destination.with_suffix(".tmp")
    temporary.unlink(missing_ok=True)
    try:
        source = sqlite3.connect(source_path.as_uri() + "?mode=ro", uri=True)
        target = sqlite3.connect(temporary)
        try:
            target.execute("PRAGMA temp_store=FILE")
            target.execute("PRAGMA cache_size=-8192")
            with target:
                populate(source, target)
                target.execute("INSERT INTO metadata VALUES(?)", (canonical(metadata),))
        finally:
            source.close()
            target.close()
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
        revision = file_digest(temporary)
        os.replace(temporary, destination)
        sync_directory(destination.parent)
        return revision
    finally:
        temporary.unlink(missing_ok=True)


def metadata(path: Path) -> dict[str, Any]:
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        value: dict[str, Any] = json.loads(db.execute("SELECT payload FROM metadata").fetchone()[0])
        return value
    finally:
        db.close()

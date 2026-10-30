"""Synthetic resource probe; never production/calibration evidence."""

import json
import resource
import sqlite3
import time
from pathlib import Path

from tokenscope.monitoring.service import MonitoringService
from tokenscope.user_monitoring.projection import build
from tokenscope.user_monitoring.ranking import RankingService, RankQuery
from tokenscope.user_monitoring.service import UserRunService


def main():
    root = Path("artifacts/validation/user-monitoring/resources").resolve()
    root.mkdir(parents=True, exist_ok=True)
    source_path = root / "facts.sqlite3"
    source_path.unlink(missing_ok=True)
    with sqlite3.connect(source_path) as db:
        db.execute(
            "CREATE TABLE facts(appid TEXT,prompt_tokens INTEGER,"
            "ideal_cached_input_tokens INTEGER,ideal_compute_input_tokens INTEGER)"
        )
        db.executemany(
            "INSERT INTO facts VALUES(?,?,?,?)",
            (
                (f"app-{i // 10:05d}", 1000 + i % 70000, i % 1000, 1000 + i % 70000 - i % 1000)
                for i in range(100000)
            ),
        )
        db.execute("CREATE INDEX cp ON facts(appid,ideal_compute_input_tokens)")
        db.execute("CREATE INDEX pp ON facts(appid,prompt_tokens)")
    before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    started = time.perf_counter()
    destination = root / "index.sqlite3"
    revision = build(
        source_path,
        destination,
        {
            "fixture": "100k-facts-10k-apps",
            "file_quality": {"read_rows": "100000", "valid_rows": "100000", "skipped_rows": "0"},
        },
    )
    elapsed = time.perf_counter() - started
    rss = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - before) * 1024
    report = dict(
        facts=100000,
        groups=10000,
        seconds=elapsed,
        rss_delta_bytes=rss,
        source_bytes=source_path.stat().st_size,
        index_bytes=destination.stat().st_size,
        revision=revision,
    )
    assert rss <= 256 * 1024**2, report
    assert destination.stat().st_size <= source_path.stat().st_size * 3 + 32 * 1024**2, report
    (root / "projection.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    import shutil

    (root / "inputs").mkdir(exist_ok=True)
    user = UserRunService(MonitoringService(root / "inputs", root / "state"))
    shutil.copyfile(destination, user.root / "ur-resource.sqlite3")
    with user.store.connect() as db:
        db.execute(
            "INSERT OR REPLACE INTO runs VALUES('ur-resource','resource','{}',"
            "'base-resource','GLM-V5.2','GLM-5.2','ready',?,NULL)",
            (revision,),
        )
    timings = {}
    for phase in ("new_connection", "repeated"):
        durations = []
        for _i in range(10):
            rank = RankingService(user)
            start = time.perf_counter()
            result = rank.rankings("ur-resource", RankQuery(sort="typical_ideal_compute_tokens"))
            durations.append(time.perf_counter() - start)
            assert len(result.rows) == 100 and result.total == "10000"
        assert max(durations) <= 2.0, durations
        timings[phase] = durations
    (root / "query.json").write_text(json.dumps(timings, indent=2) + "\n")
    print(json.dumps(timings))


if __name__ == "__main__":
    main()

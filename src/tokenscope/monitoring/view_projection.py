"""Immutable view sidecars built only on the worker/maintenance write path."""

import json
import os
import shutil
import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.view_models import canonical, data_range, rule_wire, sha, wire

SORTS = (
    "time_ns",
    "source_record_index",
    "json_tokens",
    "prompt_tokens",
    "ideal_cached_input_tokens",
    "ideal_compute_input_tokens",
    "completion_tokens",
)


def file_sha(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1048576), b""):
            h.update(part)
    return h.hexdigest()


def location(root: Path, run_id: str) -> Path:
    return root / "view-artifacts" / "v1" / run_id


def verify(root: Path, run_id: str) -> dict[str, Any]:
    directory = location(root, run_id)
    try:
        m = json.loads((directory / "manifest.json").read_bytes())
        if m["run_id"] != run_id or m["sha256"] != file_sha(directory / "view.sqlite3"):
            raise ValueError("Invalid sidecar")
        return dict(m)
    except (OSError, ValueError, KeyError) as exc:
        raise TokenScopeError("VIEW_ARTIFACT_UNAVAILABLE", "View verification failed", 503) from exc


def prepare(
    root: Path,
    run_id: str,
    source: Path,
    summary: dict[str, Any],
    signals: list[dict[str, Any]],
    source_label: str,
) -> dict[str, Any]:
    final = location(root, run_id)
    if final.exists():
        return verify(root, run_id)
    temporary = final.with_name(run_id + ".partial")
    temporary.parent.mkdir(parents=True, exist_ok=True)
    # Only our exact unsealed sidecar directory, under the caller's state root.
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir()
    origin = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
    origin.row_factory = sqlite3.Row
    dest = sqlite3.connect(temporary / "view.sqlite3")
    try:
        dest.execute("PRAGMA synchronous=FULL")
        dest.execute(
            "CREATE TABLE request_projection(source_record_index INTEGER PRIMARY KEY,appid "
            "TEXT,hash_id TEXT,time_ns INTEGER,json_tokens INTEGER,prompt_tokens INTEGER,id"
            "eal_cached_input_tokens INTEGER,ideal_compute_input_tokens INTEGER,completion_"
            "tokens INTEGER)"
        )
        cols = (
            "source_record_index,appid,hash_id,time_ns,json_tokens,prompt_tokens,ideal_cached_i"
            "nput_tokens,ideal_compute_input_tokens,completion_tokens"
        )
        dest.executemany(
            "INSERT INTO request_projection VALUES (?,?,?,?,?,?,?,?,?)",
            origin.execute(f"SELECT {cols} FROM facts"),
        )
        for col in SORTS:
            dest.execute(
                f"CREATE INDEX idx_{col} ON request_projection(appid,{col},source_record_index)"
            )
        dest.execute("CREATE INDEX idx_hash ON request_projection(appid,hash_id)")
        dest.execute(
            "CREATE TABLE view_groups(appid TEXT PRIMARY KEY,min_ns INTEGER,max_ns INTEGER,"
            "body BLOB NOT NULL,sha256 TEXT NOT NULL)"
        )
        bounds = origin.execute("SELECT min(time_ns),max(time_ns) FROM facts").fetchone()
        ranges = {
            r[0]: r
            for r in origin.execute(
                "SELECT appid,min(time_ns),max(time_ns),count(*),count(DISTINCT hash_id) FR"
                "OM facts GROUP BY appid"
            )
        }
        rejected = dict(
            origin.execute(
                "SELECT appid,count(*) FROM request_records r LEFT JOIN encoded_requests e "
                "USING(source_record_index) WHERE e.source_record_index IS NULL GROUP BY ap"
                "pid"
            )
        )
        grouped_signals: dict[str, list[dict[str, Any]]] = {}
        for event in signals:
            grouped_signals.setdefault(event["appid"], []).append(event)
        for row in origin.execute("SELECT * FROM groups ORDER BY appid"):
            appid = row["appid"]
            _, low, high, count, distinct = ranges[appid]
            metrics = json.loads(row["metrics_json"])
            rules = [r for r in summary["rules"] if r["appid"] == appid]
            states = {x.get("rule_id"): x["status"] for x in metrics["threshold_states"]}
            comparisons = []
            for rule in rules:
                value: Any = metrics
                for key in rule["metric"].split("."):
                    value = value.get(key) if isinstance(value, dict) else None
                comparisons.append(
                    dict(
                        rule=rule_wire(rule),
                        observed_value=value if rule["metric"] == "ideal_hit_rate" else wire(value),
                        state=states.get(rule["rule_id"], "disabled"),
                    )
                )
            ids = sorted(e["event_id"] for e in grouped_signals.get(appid, []))
            base = f"/analysis-runs/{run_id}"
            query = urlencode(dict(appid=appid))
            runtime = summary["runtime"]
            body = dict(
                provenance=dict(
                    data_range_utc=data_range(low, high),
                    file_data_range_utc=data_range(*bounds),
                    source_label=source_label,
                    input_sha256=summary["input_sha256"],
                    settings=wire(summary["settings"]),
                    rules=[rule_wire(r) for r in rules],
                    runtime={
                        **{
                            k: runtime[k]
                            for k in (
                                "code_version",
                                "algorithm_version",
                                "asset_identity",
                                "encoder_identity",
                                "asset_revision",
                            )
                        },
                        "encoding_profile": summary["settings"]["encoding_profile"],
                        "profile_json": canonical(runtime["profile"]).decode(),
                    },
                    simulation_semantics=metrics["capability"]["simulation_semantics"],
                    metadata_origin="stored_facts_projection",
                ),
                metrics=wire(metrics),
                distributions=wire(json.loads(row["histograms_json"])),
                quality=dict(
                    file_quality={"scope": "file", **wire(summary["quality"])},
                    group_quality=dict(
                        scope="appid",
                        coverage="known_appid_rows_only",
                        valid_requests=str(count),
                        encoding_rejected_rows=str(rejected.get(appid, 0)),
                        skipped_rows=None,
                        duplicate_scope="appid",
                        duplicate_hash_id_rows_within_group=str(count - distinct),
                        unattributed_skips_available_in="file_quality",
                    ),
                ),
                thresholds=comparisons,
                signal_summary=dict(
                    count=str(len(ids)),
                    event_ids_digest=sha("".join(x + "\n" for x in ids).encode()),
                    view_signals_url=base + "/view-signals?" + query,
                ),
                capabilities=dict(
                    original_json=True,
                    light_evidence=True,
                    requests=True,
                    export=True,
                    templated_text=False,
                ),
                links=dict(
                    requests=base + "/requests?" + query,
                    view_signals=base + "/view-signals?" + query,
                    export_ndjson=base + "/requests/export?" + query + "&format=ndjson",
                    export_csv=base + "/requests/export?" + query + "&format=csv",
                ),
            )
            raw = canonical(body)
            dest.execute(
                "INSERT INTO view_groups VALUES (?,?,?,?,?)", (appid, low, high, raw, sha(raw))
            )
        dest.commit()
    finally:
        origin.close()
        dest.close()
    manifest = dict(
        run_id=run_id,
        sha256=file_sha(temporary / "view.sqlite3"),
        file_data_range_utc=data_range(*bounds),
        groups=[dict(appid=k, min_ns=v[1], max_ns=v[2]) for k, v in ranges.items()],
    )
    (temporary / "manifest.json").write_bytes(canonical(manifest))
    for path in temporary.iterdir():
        with path.open("rb") as f:
            os.fsync(f.fileno())
    fd = os.open(temporary, os.O_RDONLY)
    os.fsync(fd)
    os.close(fd)
    temporary.rename(final)
    fd = os.open(final.parent, os.O_RDONLY)
    os.fsync(fd)
    os.close(fd)
    return manifest

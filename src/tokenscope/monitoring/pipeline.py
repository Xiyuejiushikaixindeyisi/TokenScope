"""Single-run orchestration and durable publication; CPU-only and entirely offline."""

import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

from tokenscope import ALGORITHM_VERSION, __version__
from tokenscope.domain import ModelSettings, RunState, capability
from tokenscope.encoding.assets import AssetRegistry
from tokenscope.encoding.batch import EncodingBatchService
from tokenscope.encoding.models import EncodingProfile, ModelEncoder
from tokenscope.encoding.stage import encode_input
from tokenscope.errors import TokenScopeError
from tokenscope.ingestion.csv_reader import CsvBatchReader, parse_utc
from tokenscope.monitoring import publications, view_projection
from tokenscope.monitoring.rules import evaluate, signatures
from tokenscope.monitoring.simulation import replay
from tokenscope.monitoring.statistics import aggregate
from tokenscope.monitoring.storage import ControlStore, RawRequestStore
from tokenscope.monitoring.view_models import utc_ns
from tokenscope.paths import InputRoot


def profile_for(settings: ModelSettings, cpu_budget: int) -> EncodingProfile:
    profiles = {"default": None, "thinking_enabled": True, "thinking_disabled": False}
    if settings.encoding_profile not in profiles:
        raise TokenScopeError(
            "UNKNOWN_ENCODING_PROFILE", "Select a registered encoding profile", 422
        )
    return EncodingProfile(
        name=settings.encoding_profile,
        cpu_budget=cpu_budget,
        default_thinking=profiles[settings.encoding_profile],
    )


def file_digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_json(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())


def verify_seal(directory: Path, run_id: str) -> dict[str, Any]:
    try:
        manifest = json.loads((directory / "manifest.json").read_text())
        if manifest["run_id"] != run_id:
            raise ValueError("Wrong run")
        paths = [item["path"] for item in manifest["files"]]
        if len(set(paths)) != len(paths) or not {
            "summary.json",
            "signals.json",
            "requests.sqlite3",
            "input.csv",
        }.issubset(paths):
            raise ValueError("Incomplete manifest")
        for item in manifest["files"]:
            path = (directory / item["path"]).resolve(strict=True)
            if not path.is_relative_to(directory.resolve()) or file_digest(path) != item["sha256"]:
                raise ValueError("Invalid seal")
        summary = json.loads((directory / "summary.json").read_text())
        if summary["run_id"] != run_id:
            raise ValueError("Wrong summary")
        return dict(summary=summary, signals=json.loads((directory / "signals.json").read_text()))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise TokenScopeError(
            "RESULT_SEAL_INVALID", "Sealed result verification failed", 409
        ) from exc


class RunProcessor:
    def __init__(
        self,
        inputs: InputRoot,
        state_root: Path,
        assets: AssetRegistry,
        control: ControlStore,
        cpu_budget: int = 8,
        batch_rows: int = 256,
        batch_bytes: int = 16 * 1024 * 1024,
    ) -> None:
        self.inputs, self.root, self.assets, self.control = inputs, state_root, assets, control
        self.cpu_budget, self.batch_rows, self.batch_bytes = cpu_budget, batch_rows, batch_bytes
        if min(cpu_budget, batch_rows, batch_bytes) <= 0:
            raise ValueError("Resource budgets must be positive")
        (self.root / "runs").mkdir(parents=True, exist_ok=True)

    def process_next(self) -> RunState | None:
        import fcntl

        with (self.root / "worker.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return None
            # The process lock proves no surviving worker owns a previous running task.
            self.backfill_views()
            self.recover()
            run = self.control.claim_next()
            if run is None or run.status != "running":
                return run
            try:
                self.execute(run)
            except TokenScopeError as exc:
                self.control.fail(run.run_id, exc.code)
            except (OSError, sqlite3.Error):
                # A sealed directory can be atomically committed by the next worker.
                if not (self.root / "runs" / run.run_id).exists():
                    self.control.fail(run.run_id, "STORAGE_UNAVAILABLE")
            except Exception:
                self.control.fail(run.run_id, "INTERNAL_ERROR")
            return self.control.run(run.run_id)

    def backfill_views(self) -> None:
        with self.control.connect() as db:
            if db.execute("SELECT ready FROM service_metadata WHERE id=1").fetchone()[0]:
                return
            runs = [
                dict(r)
                for r in db.execute(
                    "SELECT r.run_id,r.finished_at,r.file_ref,c.summary_json FROM analysis_"
                    "runs r JOIN completed_results c USING(run_id)"
                )
            ]
        runs.sort(key=lambda r: (parse_utc(r["finished_at"])[0], r["run_id"]))
        for row in runs:
            run_id = row["run_id"]
            with self.control.connect() as db:
                if db.execute("SELECT 1 FROM publications WHERE run_id=?", (run_id,)).fetchone():
                    continue
            directory = self.root / "runs" / run_id
            sealed = verify_seal(directory, run_id)
            summary = json.loads(row["summary_json"])
            projection = view_projection.prepare(
                self.root,
                run_id,
                directory / "requests.sqlite3",
                summary,
                sealed["signals"],
                row["file_ref"],
            )
            with self.control.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                publications.publish(
                    db,
                    run_id,
                    summary,
                    projection,
                    parse_utc(row["finished_at"])[1],
                    row["file_ref"],
                )
        with self.control.connect() as db:
            db.execute("UPDATE service_metadata SET ready=1 WHERE id=1")

    def recover(self) -> None:
        with self.control.connect() as db:
            ids = [
                row[0]
                for row in db.execute("SELECT run_id FROM analysis_runs WHERE status='running'")
            ]
        for run_id in ids:
            directory = self.root / "runs" / run_id
            if directory.exists():
                try:
                    sealed = verify_seal(directory, run_id)
                    sealed["summary"]["recovered_after_seal"] = True
                    projection = view_projection.prepare(
                        self.root,
                        run_id,
                        directory / "requests.sqlite3",
                        sealed["summary"],
                        sealed["signals"],
                        self.control.run(run_id).file_ref,
                    )
                    self.control.complete(run_id, sealed["summary"], sealed["signals"], projection)
                except TokenScopeError as exc:
                    self.control.fail(run_id, exc.code, interrupted=True)
            else:
                self.control.fail(run_id, "WORKER_INTERRUPTED", interrupted=True)

    def execute(self, run: RunState) -> None:
        started = time.monotonic()
        settings = run.settings
        if settings is None:
            raise TokenScopeError("SNAPSHOT_NOT_READY", "Missing settings snapshot", 500)
        directory = self.root / "runs" / (run.run_id + ".partial")
        directory.mkdir()
        timing: dict[str, float] = {}
        last = started

        def checkpoint(name: str) -> None:
            nonlocal last
            now = time.monotonic()
            timing[name] = now - last
            last = now

        assets = self.assets.load(settings.model_id)
        profile = profile_for(settings, self.cpu_budget)
        encoder = EncodingBatchService(ModelEncoder(assets, settings, profile))
        runtime = dict(
            profile=profile.model_dump(),
            asset_identity=assets.identity,
            encoder_identity=encoder.encoder.identity,
            asset_revision=assets.spec.revision,
            code_version=__version__,
            algorithm_version=ALGORITHM_VERSION,
        )
        self.control.bind_runtime(run.run_id, runtime)
        frozen = self.control.snapshot(run.run_id)
        checksum = self.inputs.snapshot(run.file_ref, directory / "input.csv")
        checkpoint("assets_and_snapshot")
        store = RawRequestStore(directory / "requests.sqlite3")
        store.ingest(directory / "input.csv", CsvBatchReader(settings))
        checkpoint("ingestion")
        quality = encode_input(
            store,
            encoder,
            directory / "tokens",
            batch_rows=self.batch_rows,
            batch_bytes=self.batch_bytes,
        )
        checkpoint("encoding")
        replay(store, directory / "tokens", settings, assets.identity, directory / "ledger.sqlite3")
        checkpoint("simulation")
        metric_signatures = signatures(settings, encoder.encoder.identity, assets.identity)
        signals = []
        with store.connect() as db:
            aggregate(db)
            for row in db.execute("SELECT appid,metrics_json FROM groups"):
                metrics = json.loads(row["metrics_json"])
                states, events = evaluate(
                    metrics,
                    frozen["rules"],
                    metric_signatures,
                    checksum,
                    settings.model_id,
                    run.run_id,
                )
                metrics.update(
                    model_id=settings.model_id,
                    threshold_states=states,
                    measurement_signatures=metric_signatures,
                    capability=capability(settings).model_dump(),
                )
                db.execute(
                    "UPDATE groups SET metrics_json=? WHERE appid=?",
                    (json.dumps(metrics), row["appid"]),
                )
                signals.extend(events)
            bounds = db.execute(
                "SELECT min(time_ns),max(time_ns),count(DISTINCT appid) FROM facts"
            ).fetchone()
        with store.connect() as db:
            db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            db.execute("PRAGMA journal_mode=DELETE")
        checkpoint("statistics")
        summary = dict(
            run_id=run.run_id,
            input_sha256=checksum,
            input_bytes=(directory / "input.csv").stat().st_size,
            model_id=settings.model_id,
            settings=settings.model_dump(),
            runtime=runtime,
            rules=frozen["rules"],
            quality=quality.model_dump(),
            timings_seconds=timing,
            time_range_utc=[utc_ns(bounds[0]), utc_ns(bounds[1])],
            appid_count=bounds[2],
            measurement_signatures=metric_signatures,
            elapsed_seconds=time.monotonic() - started,
            elapsed_scope="through_statistics_before_seal",
            cpu_budget=self.cpu_budget,
            batch_rows=self.batch_rows,
            batch_bytes=self.batch_bytes,
            affinity_cpus=sorted(os.sched_getaffinity(0))
            if hasattr(os, "sched_getaffinity")
            else None,
        )
        projection = view_projection.prepare(
            self.root, run.run_id, directory / "requests.sqlite3", summary, signals, run.file_ref
        )
        checkpoint("view_projection")
        write_json(directory / "summary.json", summary)
        write_json(directory / "signals.json", signals)
        files = []
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                with path.open("rb") as stream:
                    os.fsync(stream.fileno())
                files.append(
                    dict(
                        path=str(path.relative_to(directory)),
                        sha256=file_digest(path),
                        bytes=path.stat().st_size,
                    )
                )
        write_json(directory / "manifest.json", dict(run_id=run.run_id, files=files))
        sync_directory(directory)
        final = self.root / "runs" / run.run_id
        directory.rename(final)
        sync_directory(final.parent)
        # Includes hashing/fsync/seal in the authoritative wall-clock duration.
        summary["elapsed_seconds"] = time.monotonic() - started
        summary["elapsed_scope"] = "through_seal_before_control_commit"
        summary["timings_seconds"]["seal"] = summary["elapsed_seconds"] - sum(timing.values())
        self.control.complete(run.run_id, summary, signals, projection)

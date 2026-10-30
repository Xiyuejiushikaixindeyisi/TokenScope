"""Single-lock MA execution, immutable seal and recoverable publication."""

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

from tokenscope import ALGORITHM_VERSION, __version__
from tokenscope.domain import capability
from tokenscope.encoding.batch import EncodingBatchService
from tokenscope.encoding.models import ModelEncoder
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.ma.contracts import Receipt
from tokenscope.monitoring.ma.ingest import connect, ingest, initialize
from tokenscope.monitoring.ma.replay import encode, replay
from tokenscope.monitoring.ma.statistics import aggregate, file_quality
from tokenscope.monitoring.ma.storage import Store
from tokenscope.monitoring.pipeline import file_digest, profile_for, sync_directory, write_json
from tokenscope.monitoring.service import MonitoringService


def seal(directory: Path, run_id: str) -> None:
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
    write_json(
        directory / "manifest.json", dict(schema_version="1.0.0", ma_run_id=run_id, files=files)
    )
    for child in sorted((p for p in directory.rglob("*") if p.is_dir()), reverse=True):
        sync_directory(child)
    sync_directory(directory)


def verify(directory: Path, run_id: str) -> dict[str, Any]:
    try:
        manifest = json.loads((directory / "manifest.json").read_text())
        if manifest["ma_run_id"] != run_id or manifest["schema_version"] != "1.0.0":
            raise ValueError("invalid manifest identity")
        names = [item["path"] for item in manifest["files"]]
        if len(names) != len(set(names)) or not {
            "pre.csv",
            "now.csv",
            "requests.sqlite3",
            "summary.json",
        } <= set(names):
            raise ValueError("incomplete seal")
        for entry in manifest["files"]:
            path = (directory / entry["path"]).resolve(strict=True)
            if not path.is_relative_to(directory.resolve()) or file_digest(path) != entry["sha256"]:
                raise ValueError("digest mismatch")
        summary: dict[str, Any] = json.loads((directory / "summary.json").read_text())
        if summary["ma_run_id"] != run_id:
            raise ValueError("invalid result identity")
        return summary
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise TokenScopeError(
            "RESULT_SEAL_INVALID", "MA sealed result verification failed", 409
        ) from exc


class Processor:
    def __init__(self, base: MonitoringService, store: Store) -> None:
        self.base, self.store = base, store
        self.runs = store.root / "runs"
        self.runs.mkdir(exist_ok=True)

    def recover(self) -> None:
        with connect(self.store.path, readonly=True) as db:
            ids = [row[0] for row in db.execute("SELECT run_id FROM runs WHERE state='running'")]
        for run_id in ids:
            final = self.runs / run_id
            if not final.exists():
                self.store.fail(run_id, "WORKER_INTERRUPTED", interrupted=True)
                continue
            try:
                self.store.complete(run_id, verify(final, run_id))
            except TokenScopeError as exc:
                self.store.fail(run_id, exc.code, interrupted=True)

    def process_next(self) -> Receipt | None:
        import fcntl

        with (self.base.state_root / "worker.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return None
            self.recover()
            receipt = self.store.queued()
            if receipt is None:
                return None
            run_id = receipt.ma_run_id
            try:
                settings = self.base.control.settings(receipt.binding.model_id)
                self.store.claim(run_id, settings)
                self.execute(self.store.receipt(run_id))
            except TokenScopeError as exc:
                self.store.fail(run_id, exc.code, detail=str(exc)[:512] or None)
            except (OSError, sqlite3.Error):
                if not (self.runs / run_id).exists():
                    self.store.fail(run_id, "STORAGE_UNAVAILABLE")
            except Exception:
                self.store.fail(run_id, "INTERNAL_ERROR")
            return self.store.receipt(run_id)

    def execute(self, receipt: Receipt) -> None:
        started = time.monotonic()
        run_id, binding = receipt.ma_run_id, receipt.binding
        settings = self.store.settings(run_id)
        if not capability(settings).executable:
            raise TokenScopeError("UNSUPPORTED_CACHE_MODE", "Hybrid simulation is reserved", 422)
        directory = self.runs / (run_id + ".partial")
        directory.mkdir()
        timing: dict[str, float] = {}
        last = started

        def checkpoint(name: str) -> None:
            nonlocal last
            now = time.monotonic()
            timing[name], last = now - last, now

        assets = self.base.assets.load(settings.model_id)
        profile = profile_for(settings, self.base.cpu_budget)
        encoder = EncodingBatchService(ModelEncoder(assets, settings, profile))
        sources = {}
        for role, ref in (("pre", binding.pre_file_ref), ("now", binding.now_file_ref)):
            checksum = self.base.inputs.snapshot(ref, directory / f"{role}.csv")
            sources[role] = dict(
                sha256=checksum, bytes=str((directory / f"{role}.csv").stat().st_size)
            )
        checkpoint("assets_and_snapshots")
        facts = directory / "requests.sqlite3"
        initialize(facts)
        for role in ("pre", "now"):
            ingest(facts, directory / f"{role}.csv", role, binding, settings)
        checkpoint("ingestion")
        encode(
            facts,
            directory / "tokens",
            encoder,
            self.base.processor.batch_rows,
            self.base.processor.batch_bytes,
        )
        checkpoint("encoding")
        replay(
            facts,
            directory / "tokens",
            settings,
            assets.identity,
            binding.model_standard_name,
            directory / "ledgers",
        )
        checkpoint("simulation")
        aggregate(facts, binding)
        quality = file_quality(facts)
        with connect(facts, readonly=True) as db:
            uuids = [
                row[0]
                for row in db.execute(
                    "SELECT instance_uuid FROM projections ORDER BY instance_uuid"
                )
            ]
        checkpoint("statistics")
        runtime = dict(
            settings=settings.model_dump(mode="json"),
            profile=profile.model_dump(mode="json"),
            asset_identity=assets.identity,
            asset_revision=assets.spec.revision,
            encoder_identity=encoder.encoder.identity,
            algorithm_version=ALGORITHM_VERSION,
            code_version=__version__,
            mode_provenance="configuration_snapshot_not_verified_production_default",
            deepseek_site_assumption=(
                settings.model_id == "DeepSeek-V4-Flash-0731"
                and settings.encoding_profile == "thinking_disabled"
            ),
            sources=sources,
            timings_seconds=timing,
            cpu_budget=self.base.cpu_budget,
            batch_rows=self.base.processor.batch_rows,
            batch_bytes=self.base.processor.batch_bytes,
        )
        summary = dict(
            ma_run_id=run_id,
            binding=binding.model_dump(mode="json"),
            runtime=runtime,
            file_quality=[q.model_dump(mode="json") for q in quality],
            instance_uuids=uuids,
            empty_scope_reason=(
                "empty_file" if quality[1].records_read == "0" else "all_unassigned"
            )
            if quality[1].assigned == "0"
            else None,
        )
        write_json(directory / "summary.json", summary)
        seal(directory, run_id)
        final = self.runs / run_id
        directory.rename(final)
        sync_directory(self.runs)
        self.store.complete(run_id, summary)

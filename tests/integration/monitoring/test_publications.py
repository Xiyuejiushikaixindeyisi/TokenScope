import json
import sqlite3

import pytest
from conftest import csv_bytes, valid_row

from tokenscope.domain import RunSubmission
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring import publications, view_projection
from tokenscope.monitoring.publications import PublicationRepository
from tokenscope.monitoring.storage import ControlStore


def process(service, time="2026-10-27T00:00:00Z", appid="a", bad=False):
    (service.inputs.root / "view.csv").write_bytes(
        csv_bytes(
            [
                valid_row(
                    appid=appid,
                    model_handle_start_time=time,
                    completion_tokens="bad" if bad else "3",
                )
            ]
        )
    )
    run = service.submit(RunSubmission(file_ref="view.csv", model_id="GLM-5.2"))
    done = service.processor.process_next()
    assert done.status == ("no_valid_rows" if bad else "completed"), done
    return run.run_id


def test_latest_numeric_time_empty_and_revision(service):
    repo = PublicationRepository(service.control)
    newest = process(service, "2026-10-27T00:00:00.1Z")
    older = process(service, "2026-10-27T00:00:00Z")
    catalog = repo.catalog()
    assert catalog["items"][0]["active_run_id"] == newest
    repeated = process(service, "2026-10-27T00:00:00.100000000Z")
    assert repo.catalog()["items"][0]["active_run_id"] == repeated
    empty = process(service, bad=True)
    assert repo.catalog()["items"][0]["active_run_id"] == repeated
    assert repo.catalog(runs=True)["items"][0]["run_id"] == empty
    assert len(repo.catalog(appid="a", runs=True)["items"]) == 3
    with pytest.raises(TokenScopeError, match="Reload"):
        repo.catalog(revision=int(catalog["catalog_revision"]))
    assert (
        repo.catalog(offset=2**80, revision=int(repo.catalog()["catalog_revision"]))["items"] == []
    )
    assert older != newest


def test_projection_preserves_original_metrics_and_ranges(service):
    (service.inputs.root / "view.csv").write_bytes(
        csv_bytes(
            [
                valid_row(hash_id="dup", appid="a", model_handle_start_time="2026-10-27T00:00:00Z"),
                valid_row(
                    hash_id="dup", appid="b", model_handle_start_time="2026-10-27T00:00:00.1Z"
                ),
                valid_row(
                    hash_id="dup", appid="a", model_handle_start_time="2026-10-27T00:00:00.01Z"
                ),
                valid_row(completion_tokens="invalid"),
            ]
        )
    )
    run = service.submit(RunSubmission(file_ref="view.csv", model_id="GLM-5.2"))
    service.processor.process_next()
    directory = view_projection.location(service.state_root, run.run_id)
    view_projection.verify(service.state_root, run.run_id)
    with sqlite3.connect(directory / "view.sqlite3") as db:
        body = json.loads(db.execute("SELECT body FROM view_groups WHERE appid='a'").fetchone()[0])
    assert body["provenance"]["data_range_utc"]["end"].endswith(".010000000Z")
    assert body["provenance"]["file_data_range_utc"]["end"].endswith(".100000000Z")
    assert body["quality"]["file_quality"]["duplicate_hash_id_rows"] == "2"
    assert body["quality"]["group_quality"]["duplicate_hash_id_rows_within_group"] == "1"
    assert body["quality"]["group_quality"]["skipped_rows"] is None
    original = service.metrics(run.run_id, "a")["groups"][0]
    assert int(body["metrics"]["totals"]["prompt_tokens"]) == original["totals"]["prompt_tokens"]
    assert (
        sum(len(h["bins"]) for widths in body["distributions"].values() for h in widths.values())
        == 1029
    )


def test_migration_backup_resume_and_immutable_seal(service):
    run_id = process(service)
    seal = service.state_root / "runs" / run_id / "manifest.json"
    before = seal.read_bytes()
    with service.control.connect() as db:
        for name in (
            "submission_receipts",
            "active_groups",
            "publication_groups",
            "publications",
            "ui_events",
            "service_metadata",
        ):
            db.execute(f"DROP TABLE {name}")
        db.execute("PRAGMA user_version=2")
    service.control = ControlStore(service.control.path)
    service.processor.control = service.control
    backup = service.control.path.with_name("control.schema2.backup.sqlite3")
    with sqlite3.connect(backup) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 2
    repo = PublicationRepository(service.control)
    with pytest.raises(TokenScopeError) as error:
        repo.catalog()
    assert error.value.code == "VIEW_INDEX_NOT_READY"
    service.processor.backfill_views()
    first = repo.catalog()
    service.processor.backfill_views()
    assert repo.catalog() == first
    assert seal.read_bytes() == before
    assert first["items"][0]["active_run_id"] == run_id


def test_transaction_rollback_cannot_expose_partial_groups(service):
    repo = PublicationRepository(service.control)
    before = repo.catalog()
    with pytest.raises(sqlite3.IntegrityError):
        with service.control.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            summary = dict(
                model_id="GLM-5.2", quality=dict(valid_requests=2), input_sha256="a" * 64
            )
            group = dict(appid="same", min_ns=1, max_ns=2)
            publications.publish(
                db,
                "synthetic",
                summary,
                dict(file_data_range_utc={}, groups=[group, group]),
                "2026-10-27T00:00:00.000000000Z",
                "test.csv",
            )
    assert repo.catalog() == before


def test_backfill_resume_after_second_publication_rollback(service, monkeypatch):
    first = process(service, "2026-10-27T00:00:00Z")
    second = process(service, "2026-10-27T01:00:00Z")
    with service.control.connect() as db:
        db.execute("DELETE FROM active_groups")
        db.execute("DELETE FROM publication_groups")
        db.execute("DELETE FROM publications")
        db.execute("DELETE FROM ui_events")
        db.execute("UPDATE service_metadata SET ready=0")
    original = publications.publish
    calls = []

    def interrupted(*args, **kwargs):
        original(*args, **kwargs)
        calls.append(True)
        if len(calls) == 2:
            raise OSError("Synthetic backfill interruption")

    monkeypatch.setattr(publications, "publish", interrupted)
    with pytest.raises(OSError):
        service.processor.backfill_views()
    with pytest.raises(TokenScopeError) as error:
        service.publications.catalog()
    assert error.value.code == "VIEW_INDEX_NOT_READY"
    monkeypatch.setattr(publications, "publish", original)
    service.processor.backfill_views()
    with service.control.connect() as db:
        assert db.execute("SELECT count(*) FROM publications").fetchone()[0] == 2
        assert db.execute("SELECT count(*) FROM ui_events").fetchone()[0] == 2
    assert service.publications.catalog()["items"][0]["active_run_id"] == second
    assert first != second

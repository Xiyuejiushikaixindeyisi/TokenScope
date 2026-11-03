"""Explicit synthetic fixtures: no Huawei CSV or production reproduction claim."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from tokenscope.api.app import create_app
from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.encoding.batch import EncodedRequest, EncodingFailure
from tokenscope.encoding.shards import TokenShardWriter
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.ma.availability import (
    Availability,
    AvailabilityResponse,
    InstanceAvailability,
)
from tokenscope.monitoring.ma.contracts import InstanceSnapshot
from tokenscope.monitoring.ma.ingest import connect, ingest, initialize
from tokenscope.monitoring.ma.pipeline import seal, verify
from tokenscope.monitoring.ma.replay import encode, replay
from tokenscope.monitoring.ma.service import MaService
from tokenscope.monitoring.ma.statistics import aggregate
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.monitoring.service import MonitoringService

from .helpers import binding, row, write_csv


def synthetic(tmp_path, pre, now, *, spec="q-64K"):
    """Real ingestion/replay/aggregation; explicitly synthetic identical 4096-token inputs."""
    tmp_path.mkdir(exist_ok=True)
    db = tmp_path / "facts.db"
    initialize(db)
    request = binding().model_copy(update={"model_standard_name": spec})
    settings = DEFAULT_SETTINGS["Qwen3.6-27B"].model_copy(update={"mtp": False})
    for role, rows in (("pre", pre), ("now", now)):
        source = tmp_path / f"{role}.csv"
        write_csv(source, rows)
        ingest(db, source, role, request, settings)
    writer = TokenShardWriter(tmp_path / "tokens")
    with connect(db) as con:
        for (rid,) in con.execute("SELECT id FROM records WHERE candidate=1"):
            ref = writer.append([1] * 4096)
            con.execute(
                "UPDATE records SET local_prompt=4096,token_slice=? WHERE id=?",
                (ref.model_dump_json(), rid),
            )
    writer.close()
    replay(db, tmp_path / "tokens", settings, "synthetic", spec, tmp_path / "ledgers")
    aggregate(db, request)
    with connect(db, readonly=True) as con:
        snapshot = InstanceSnapshot.model_validate_json(
            con.execute("SELECT snapshot FROM projections WHERE instance_uuid='A'").fetchone()[0]
        )
        explanation = InstanceAvailability.model_validate_json(
            con.execute("SELECT projection FROM availability WHERE instance_uuid='A'").fetchone()[0]
        )
    return snapshot, explanation


@pytest.mark.parametrize(
    "case,changes,counts,reason",
    [
        ("missing_cached", {"cached_tokens": ""}, (1, 1, 0, 1, 0), "source_cached_missing"),
        (
            "no_prompt",
            {"prompt_tokens": "", "request_input": "bad"},
            (1, 0, 0, 0, 0),
            "no_valid_prompt",
        ),
        ("zero_cached", {"cached_tokens": "0"}, (1, 1, 1, 1, 1), None),
        ("bad_json", {"request_input": "bad", "completion_tokens": "bad"}, (1, 1, 1, 0, 0), None),
        (
            "zero_prompt",
            {"prompt_tokens": "0", "cached_tokens": "0"},
            (1, 1, 1, 1, 1),
            "zero_input_denominator",
        ),
        ("invalid_cached", {"cached_tokens": "101"}, (1, 1, 0, 1, 0), "invalid_cached"),
    ],
)
def test_independent_availability(tmp_path: Path, case, changes, counts, reason) -> None:
    s, a = synthetic(tmp_path, [row("pre")], [row(**changes)])
    assert tuple(map(int, s.coverage.model_dump().values())) == counts
    m = a.metrics
    if reason:
        assert reason in m.independent_real_hit_rate.reasons
    if case == "missing_cached":
        assert s.ideal.hit_rate == 3072 / 4096
        assert m.independent_ideal_hit_rate.state == "available"
        assert m.paired_ideal_hit_rate.state == "unavailable"
        assert m.paired_real_hit_rate.numerator is None
        assert m.actual_uncached_tokens.numerator is None
        assert s.hour.uncached_tokens is None
        assert a.now_field_issues[0].field == "cached_tokens"
    if case == "bad_json":
        assert s.real.hit_rate == 0.25 and s.real.totals.uncached_tokens == "75"
        assert m.independent_real_hit_rate.reasons == []
        assert m.actual_uncached_tokens.state == "available"
        assert s.paired_real.hit_rate is None
    if case == "zero_cached":
        assert s.real.hit_rate == 0 and m.independent_real_hit_rate.state == "available"
        assert m.actual_uncached_tokens.numerator == "100"
    if case == "zero_prompt":
        assert s.real.hit_rate is None
        assert m.independent_real_hit_rate.state == "unavailable"
        assert m.paired_ideal_hit_rate.state == "available"
        assert m.actual_uncached_tokens.numerator == "0"
        assert m.actual_uncached_tokens.state == "available"
    assert len(a.bins) == 12
    assert a.bins[1].state == "empty" and a.bins[1].numerator == "0"
    assert s.hour.requests_per_second == 1 / 3600


def test_overlap_preserves_real_and_records_actual_encoded_bounds(tmp_path: Path) -> None:
    s, a = synthetic(
        tmp_path, [row("pre", model_handle_start_time="2026-10-20T08:02:00Z")], [row()]
    )
    assert s.ideal_status == "warmup_order_conflict"
    assert s.coverage.model_dump() == dict(
        assigned="1", production_input="1", real="1", encoded="0", paired="0"
    )
    assert s.real.hit_rate == 0.25 and s.hour.uncached_tokens == "75"
    assert a.metrics.independent_real_hit_rate.state == "available"
    assert "warmup_order_conflict" in a.metrics.paired_real_hit_rate.reasons
    assert a.warmup.encoded_now_count == "1"  # encoded input != successfully replayed E
    assert a.warmup.pre_max_handle_time == "2026-10-20T08:02:00.000000000Z"
    assert a.warmup.now_min_handle_time == "2026-10-20T08:01:00.000000000Z"


@pytest.mark.parametrize(
    "invalid", [dict(request_input="bad"), dict(hash_id=""), dict(model_handle_start_time="bad")]
)
def test_invalid_pre_tail_cannot_create_conflict(tmp_path: Path, invalid) -> None:
    tail = row("pre", model_handle_start_time="2026-10-20T08:30:00Z") | invalid
    s, a = synthetic(tmp_path, [tail, row("pre")], [row()])
    assert s.ideal_status == "available" and s.ideal.hit_rate == 0.75
    assert a.warmup.encoded_pre_count == "1"
    assert a.warmup.pre_max_handle_time == "2026-10-20T07:01:00.000000000Z"


def test_equal_handle_and_duplicate_hash_and_order(tmp_path: Path) -> None:
    tie = "2026-10-20T08:01:00Z"
    s, a = synthetic(
        tmp_path, [row("pre", model_handle_start_time=tie), row("pre")], [row(appid="other"), row()]
    )
    assert s.ideal_status == "available" and s.coverage.assigned == "2"
    assert s.ideal.hit_rate == 0.75
    assert a.warmup.pre_max_handle_time == a.warmup.now_min_handle_time
    assert s.real.totals.uncached_tokens == "150"


def test_empty_now_and_no_valid_prewarm(tmp_path: Path) -> None:
    s, a = synthetic(tmp_path / "empty", [row("pre")], [])
    assert s.ideal_status == "empty_now" and s.real.hit_rate is None
    assert a.metrics.actual_uncached_tokens.state == "empty"
    assert a.metrics.actual_uncached_tokens.numerator == "0"
    s, a = synthetic(tmp_path / "cold", [], [row()])
    assert s.ideal_status == "no_valid_prewarm" and s.ideal.hit_rate == 0
    assert a.metrics.independent_ideal_hit_rate.state == "available"
    assert a.metrics.independent_ideal_hit_rate.reasons == ["no_valid_prewarm"]


def test_partial_known_totals_bins_and_model_scope_isolation(tmp_path: Path) -> None:
    now = [
        row(cached_tokens="0"),
        row(cached_tokens="", request_time="2026-10-20T08:05:00Z"),
        row(cached_tokens="100", request_time="2026-10-20T08:59:59.999999999Z"),
    ]
    s, a = synthetic(tmp_path / "one", [row("pre")], now, spec="q-32K")
    assert s.hour.uncached_tokens == "100" and s.hour.uncached_tokens_per_second == 100 / 3600
    assert a.metrics.hour_uncached_tokens_per_second.state == "partial"
    assert a.metrics.hour_uncached_tokens_per_second.denominator == "3600"
    assert a.bins[0].numerator == "100" and a.bins[1].numerator is None
    assert a.bins[11].numerator == "0" and a.bins[11].state == "available"
    assert sum(int(b.pressure.uncached_tokens or 0) for b in s.bins) == 100
    assert sum(int(b.pressure.request_count) for b in s.bins) == 3
    other, _ = synthetic(tmp_path / "two", [], [row()], spec="q-128K")
    assert other.ideal.hit_rate == 0 and s.ideal.hit_rate == 0.75


def test_request_window_is_fatal_not_handle_filter(tmp_path: Path) -> None:
    with pytest.raises(TokenScopeError, match="Window violation"):
        synthetic(tmp_path / "bad", [row("pre", request_time="2026-10-20T08:00:00Z")], [row()])
    s, _ = synthetic(
        tmp_path / "handle", [row("pre")], [row(model_handle_start_time="2026-10-20T09:18:00Z")]
    )
    assert s.handle_outside_window_count == "1" and s.coverage.real == "1"


def test_encoding_failure_pre_tail_excluded(tmp_path: Path) -> None:
    db = tmp_path / "facts.db"
    initialize(db)
    settings = DEFAULT_SETTINGS["Qwen3.6-27B"]
    pre, now = tmp_path / "pre.csv", tmp_path / "now.csv"
    write_csv(pre, [row("pre", model_handle_start_time="2026-10-20T08:30:00Z"), row("pre")])
    write_csv(now, [row()])
    ingest(db, pre, "pre", binding(), settings)
    ingest(db, now, "now", binding(), settings)
    # Inject an explicit encoder failure, then use real shard/replay/statistics code.
    encoded = EncodedRequest(0, [1] * 4096, "synthetic", "synthetic", {})
    encoder = SimpleNamespace(
        encode_batch=lambda values: [
            EncodingFailure("SYNTHETIC_ENCODING_FAILURE", "request_input"),
            encoded,
            encoded,
        ]
    )
    encode(db, tmp_path / "tokens", encoder)
    replay(db, tmp_path / "tokens", settings, "synthetic", "q-64K", tmp_path / "ledgers")
    aggregate(db, binding())
    with connect(db, readonly=True) as con:
        a = InstanceAvailability.model_validate_json(
            con.execute("SELECT projection FROM availability").fetchone()[0]
        )
        assert con.execute("SELECT status FROM scopes").fetchone()[0] == "available"
    assert a.warmup.encoded_pre_count == "1"
    assert a.warmup.pre_max_handle_time == "2026-10-20T07:01:00.000000000Z"


@pytest.mark.parametrize(
    "change",
    [
        {"state": "available"},
        {"numerator": "0"},
        {"denominator": None},
        {"sample_count": "2"},
        {"reasons": []},
    ],
)
def test_availability_contract_rejects_false_observations(change) -> None:
    from pydantic import ValidationError

    value = dict(
        state="unavailable",
        sample_count="0",
        population_count="1",
        numerator=None,
        denominator="3600",
        denominator_unit="seconds",
        reasons=["no_real_samples"],
    )
    with pytest.raises(ValidationError):
        Availability.model_validate(value | change)


def test_http_projection_readonly_and_old_results(service: MonitoringService, monkeypatch) -> None:
    write_csv(service.inputs.root / "pre.csv", [row("pre")])
    write_csv(service.inputs.root / "now.csv", [row(cached_tokens="")])
    app = create_app(service, start_worker=False)
    with TestClient(app) as client:
        ma: MaService = app.state.ma
        run = ma.submit(binding()).ma_run_id
        url = f"/monitoring/ma/runs/{run}/instances/A/availability"
        assert client.get(url).status_code == 409
        assert ma.processor.process_next().state == "completed"
        directory = ma.processor.runs / run
        before = {str(p): file_digest(p) for p in directory.rglob("*") if p.is_file()}
        monkeypatch.setattr(
            "tokenscope.monitoring.ma.statistics.explain", lambda *a: pytest.fail("GET computed")
        )
        for _ in range(2):
            response = client.get(url)
            assert response.status_code == 200
            parsed = AvailabilityResponse.model_validate(response.json())
            assert parsed.availability.metrics.independent_real_hit_rate.state == "unavailable"
            assert response.headers["cache-control"] == "no-store"
            assert response.headers["x-tokenscope-instance-id"] == ma.service_id
        assert client.get(url, headers={"X-TokenScope-Instance-Id": "wrong"}).status_code == 409
        assert client.get(url.replace("/A/", "/unknown/")).status_code == 404
        assert before == {str(p): file_digest(p) for p in directory.rglob("*") if p.is_file()}
        old_snapshot = ma.snapshot(run, "A").model_dump()
        # Synthetic legacy fixture, not an edit to any real published result.
        with connect(directory / "requests.sqlite3") as db:
            db.execute("DROP TABLE availability")
        # Rebuild only this temporary legacy fixture seal, never a production seal.
        (directory / "manifest.json").unlink()
        seal(directory, run)
        assert verify(directory, run)["ma_run_id"] == run
        legacy_before = file_digest(directory / "requests.sqlite3")
        response = client.get(url)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "AVAILABILITY_NOT_RECORDED"
        assert ma.snapshot(run, "A").model_dump() == old_snapshot
        assert file_digest(directory / "requests.sqlite3") == legacy_before

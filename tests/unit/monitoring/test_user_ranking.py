import random
import sqlite3
from fractions import Fraction

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from tokenscope.api.app import create_app
from tokenscope.errors import TokenScopeError
from tokenscope.user_monitoring.projection import build
from tokenscope.user_monitoring.ranking import METRICS, ModeQuery, RankingService, RankQuery
from tokenscope.user_monitoring.service import UserRunService


@pytest.fixture
def indexed(service):
    rng = random.Random(41)
    source = service.state_root / "fixture.sqlite3"
    values = {}
    with sqlite3.connect(source) as db:
        db.execute(
            "CREATE TABLE facts(appid,prompt_tokens,ideal_cached_input_tokens,"
            "ideal_compute_input_tokens)"
        )
        for app in ["a", "A", "%_", "中文", "empty", "precise1", "precise2"] + [
            f"g{i}" for i in range(35)
        ]:
            rows = [
                (rng.randrange(1, 20000), rng.randrange(0, 1000))
                for _ in range(rng.randrange(1, 20))
            ]
            if app == "empty":
                rows = [(0, 0)]
            if app.startswith("precise"):
                rows = [(2**53 + int(app[-1]), 0)]
            values[app] = [(p + h, h, p) for p, h in rows]
            db.executemany(
                "INSERT INTO facts VALUES(?,?,?,?)", [(app, *row) for row in values[app]]
            )
        db.execute("CREATE INDEX c ON facts(appid,ideal_compute_input_tokens)")
    user = UserRunService(service)
    n = sum(map(len, values.values()))
    meta = {"file_quality": {"read_rows": str(n), "valid_rows": str(n), "skipped_rows": "0"}}
    revision = build(source, user.root / "ur-fixture.sqlite3", meta)
    with user.store.connect() as db:
        db.execute(
            "INSERT INTO runs VALUES('ur-fixture','fixture','{}','base-fixture',"
            "'GLM-V5.2','GLM-5.2','ready',?,NULL)",
            (revision,),
        )
    return user, values


def oracle(values, metric, width=5000):
    totals = [sum(r[i] for r in values) for i in range(3)]
    if metric == "request_count":
        return Fraction(len(values))
    if metric == "ideal_hit_rate":
        return Fraction(totals[1], totals[0]) if totals[0] else None
    if metric == "total_ideal_compute_tokens":
        return Fraction(totals[2])
    buckets = {}
    for _p, _h, c in values:
        buckets.setdefault(c // width, []).append(c)
    best = sorted(buckets, key=lambda k: (-len(buckets[k]), k))[0]
    return Fraction(sum(buckets[best]), len(buckets[best]))


@pytest.mark.parametrize("metric", METRICS)
@pytest.mark.parametrize("direction", ["asc", "desc"])
def test_sort_filter_pagination_oracle(indexed, metric, direction):
    user, values = indexed
    rank = RankingService(user)
    sign = 1 if direction == "asc" else -1
    expected = sorted(
        values,
        key=lambda a: (
            oracle(values[a], metric) is None,
            sign * (oracle(values[a], metric) or 0),
            a.encode("utf-8"),
        ),
    )
    pages = []
    for offset in range(0, len(values), 7):
        response = rank.rankings(
            "ur-fixture",
            RankQuery(
                sort=metric,
                direction=direction,
                limit=7,
                offset=str(offset),
                index_revision=user.receipt("ur-fixture").index_revision,
            ),
        )
        pages.extend(r.appid for r in response.rows)
    assert pages == expected
    bounds = {
        metric + "_min": "1" if metric != "ideal_hit_rate" else "0.01",
        metric + "_max": "999999999999999999" if metric != "ideal_hit_rate" else "0.5",
    }
    result = rank.rankings("ur-fixture", RankQuery(sort=metric, direction=direction, **bounds))
    assert [r.appid for r in result.rows] == [
        a
        for a in expected
        if oracle(values[a], metric) is not None
        and Fraction(bounds[metric + "_min"])
        <= oracle(values[a], metric)
        <= Fraction(bounds[metric + "_max"])
    ]


def test_literal_search_modes_and_precision(indexed):
    user, values = indexed
    rank = RankingService(user)
    assert [r.appid for r in rank.rankings("ur-fixture", RankQuery(appid_contains="%_")).rows] == [
        "%_"
    ]
    assert [r.appid for r in rank.rankings("ur-fixture", RankQuery(appid_contains="A")).rows] == [
        "A"
    ]
    exact = rank.rankings("ur-fixture", RankQuery(total_ideal_compute_tokens_min=str(2**53 + 2)))
    assert [r.appid for r in exact.rows] == ["precise2"]
    for app, rows in values.items():
        counts = {}
        for _, _, c in rows:
            counts[c // 5000] = counts.get(c // 5000, 0) + 1
        expected = [k * 5000 for k in sorted(counts) if counts[k] == max(counts.values())]
        actual = []
        for offset in range(len(expected)):
            result = rank.modes(
                "ur-fixture",
                ModeQuery(
                    appid=app,
                    offset=str(offset),
                    limit=1,
                    index_revision=user.receipt("ur-fixture").index_revision,
                ),
            )
            actual.extend(int(b.lower) for b in result.bins)
        assert actual == expected
    with pytest.raises(TokenScopeError, match="revision"):
        rank.rankings("ur-fixture", RankQuery(index_revision="stale"))


@pytest.mark.parametrize(
    "query",
    [
        {"offset": "-1"},
        {"offset": "01"},
        {"limit": 1001},
        {"sort": "sql injection"},
        {"ideal_hit_rate_min": "NaN"},
        {"ideal_hit_rate_max": "1.1"},
        {"request_count_min": "2", "request_count_max": "1"},
        {"offset": str(2**64)},
        {"bin_width": 999},
        {"other": "unknown"},
    ],
)
def test_bad_query(query):
    with pytest.raises(ValidationError):
        RankQuery(**query)


def test_http_readonly_identity_and_schema(service, indexed):
    user, _ = indexed
    client = TestClient(create_app(service, start_worker=False))
    prefix = "/monitoring/user-v2/runs/ur-fixture"
    headers = {"X-TokenScope-Instance-Id": user.service_id}
    before = {str(p): p.stat().st_mtime_ns for p in service.state_root.rglob("*") if p.is_file()}
    assert client.get(prefix + "/rankings").status_code == 409
    result = client.get(prefix + "/rankings?bin_width=1000&limit=1", headers=headers)
    assert result.status_code == 200, result.text
    from tokenscope.user_monitoring.contracts import Ranking

    Ranking.model_validate_json(result.content)
    assert (
        client.get(prefix + "/rankings?request_count_min=NaN", headers=headers).status_code == 422
    )
    assert client.get(prefix + "/modes?appid=a&bin_width=5000", headers=headers).status_code == 200
    assert client.get(prefix + "/rankings?extra=1", headers=headers).status_code == 422
    assert (
        client.get(prefix.replace("ur-fixture", "ma-unknown"), headers=headers).status_code == 404
    )
    assert before == {
        str(p): p.stat().st_mtime_ns for p in service.state_root.rglob("*") if p.is_file()
    }


def test_estimate_http_immutable_snapshot_and_concurrency(service, indexed):
    from concurrent.futures import ThreadPoolExecutor

    from tokenscope.user_monitoring.contracts import EvaluationRequest, Scenario
    from tokenscope.user_monitoring.estimator import EstimatorService

    user, _ = indexed
    estimator = EstimatorService(user)
    fixture = Scenario.model_validate(
        dict(
            scenario_id="test",
            revision="1",
            model_id="GLM-5.2",
            common_name="GLM-V5.2",
            deployment="synthetic",
            source="user_assumption",
            source_description="test",
            evidence_sha256=None,
            measurement_boundary="GF",
            workload_description="assumed",
            thinking_mode="disabled",
            min_prompt_tokens="0",
            max_prompt_tokens="999999999999999999",
            chunk_tokens="8192",
            chunk_seconds="2",
            overhead_seconds="1",
            sample_count="0",
            calibration_notes="not calibrated",
        )
    )
    estimator.put_scenario(fixture)
    assert estimator.put_scenario(fixture) == fixture
    with pytest.raises(TokenScopeError, match="Immutable"):
        estimator.put_scenario(fixture.model_copy(update={"chunk_seconds": "3"}))
    req = EvaluationRequest.model_validate(
        dict(
            submission_key="estimate",
            user_run_id="ur-fixture",
            appid="a",
            scenario_id="test",
            scenario_revision="1",
            target_seconds="8",
            waiting_seconds="3",
            comparator="le",
        )
    )
    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(estimator.evaluate, [req] * 8))
    assert len({r.evaluation_id for r in results}) == 1
    original = results[0]
    estimator.put_scenario(
        fixture.model_copy(
            update={
                "scenario_id": "other-model",
                "model_id": "Qwen3.6-27B",
                "common_name": "Qwen-V3.6-27B",
            }
        )
    )
    with pytest.raises(TokenScopeError, match="differ"):
        estimator.evaluate(
            req.model_copy(update={"submission_key": "wrong-model", "scenario_id": "other-model"})
        )
    estimator.put_scenario(fixture.model_copy(update={"revision": "2", "chunk_seconds": "0.1"}))
    assert estimator.evaluation(original.evaluation_id) == original
    with pytest.raises(TokenScopeError, match="differs"):
        estimator.evaluate(req.model_copy(update={"waiting_seconds": "1"}))
    assert (
        estimator.evaluate(
            req.model_copy(update={"submission_key": "missing", "appid": "missing"})
        ).status
        == "unavailable"
    )
    client = TestClient(create_app(service, start_worker=False))
    headers = {"X-TokenScope-Instance-Id": user.service_id}
    prefix = "/monitoring/user-v2"
    assert (
        client.post(prefix + "/scenarios", json=fixture.model_dump(), headers=headers).status_code
        == 201
    )
    response = client.post(prefix + "/evaluations", json=req.model_dump(), headers=headers)
    assert response.status_code == 201, response.text
    assert response.json() == original.model_dump(mode="json")
    before = {str(p): p.stat().st_mtime_ns for p in service.state_root.rglob("*") if p.is_file()}
    assert (
        client.get(prefix + "/evaluations/" + original.evaluation_id, headers=headers).json()
        == response.json()
    )
    assert client.get(prefix + "/scenarios/test/1", headers=headers).json() == fixture.model_dump()
    assert before == {
        str(p): p.stat().st_mtime_ns for p in service.state_root.rglob("*") if p.is_file()
    }
    (user.root / "ur-fixture.sqlite3").unlink()
    assert EstimatorService(UserRunService(service)).evaluate(req) == original

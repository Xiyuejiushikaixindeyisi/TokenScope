import json
import time
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from tokenscope.user_monitoring.contracts import EvaluationRequest, Scenario
from tokenscope.user_monitoring.estimator import calculate


def scenario(**updates):
    data = dict(
        scenario_id="synthetic",
        revision="1",
        model_id="GLM-5.2",
        common_name="GLM-V5.2",
        deployment="synthetic fixture, not production",
        source="user_assumption",
        source_description="arithmetic test",
        evidence_sha256=None,
        measurement_boundary="GF dispatch to first token",
        workload_description="fixed waiting",
        thinking_mode="disabled",
        min_prompt_tokens="0",
        max_prompt_tokens="999999",
        chunk_tokens="8192",
        chunk_seconds="2",
        overhead_seconds="1",
        sample_count="0",
        calibration_notes="not calibrated",
    )
    data.update(updates)
    return Scenario.model_validate(data)


def request(**updates):
    data = dict(
        submission_key="test",
        user_run_id="ur-test",
        appid="a",
        scenario_id="synthetic",
        scenario_revision="1",
        target_seconds="8",
        waiting_seconds="3",
        comparator="le",
    )
    data.update(updates)
    return EvaluationRequest.model_validate(data)


def run(req=None, sc=None, n=10, p90=32768):
    return calculate(
        req or request(),
        sc or scenario(),
        count=n,
        prompt_p90=p90,
        service_id="test-service",
        evaluation_id="test-eval",
    )


def test_exact_example_and_extremes():
    assert run().required_hit_rate == 0.5
    assert run(request(comparator="lt")).required_hit_rate == 0.75
    assert run(request(target_seconds="4")).status == "reference_with_limit"
    assert run(request(target_seconds="4")).required_hit_rate == 1.0
    assert run(request(target_seconds="4", comparator="lt")).status == "no_budget"
    assert run(request(target_seconds="3")).required_hit_rate is None
    assert run(request(target_seconds="100")).required_hit_rate == 0.0
    assert run(n=0, p90=None).status == "unavailable"
    assert run(p90=0).status == "unavailable"
    assert run(sc=scenario(max_prompt_tokens="100")).status == "out_of_scope"
    assert (
        run(
            request(target_seconds="0.3", waiting_seconds="0.1"),
            scenario(overhead_seconds="0", chunk_seconds="0.1"),
        ).allowed_chunks
        == "2"
    )
    assert (
        run(
            request(target_seconds="0.3", waiting_seconds="0.1", comparator="lt"),
            scenario(overhead_seconds="0", chunk_seconds="0.1"),
        ).allowed_chunks
        == "1"
    )


def test_decimal_oracle_monotonicity_and_budget():
    started = time.perf_counter()
    checked = 0
    for comparator in ("le", "lt"):
        for wait in ("0", "0.1", "1", "3", "4"):
            previous = 1.0
            for target in range(1, 101):
                t = str(Decimal(target) / 10)
                result = run(
                    request(target_seconds=t, waiting_seconds=wait, comparator=comparator),
                    scenario(chunk_seconds="0.2", overhead_seconds="0.1"),
                )
                feasible = [
                    i
                    for i in range(51)
                    if (
                        Decimal(wait) + Decimal("0.1") + i * Decimal("0.2") <= Decimal(t)
                        if comparator == "le"
                        else Decimal(wait) + Decimal("0.1") + i * Decimal("0.2") < Decimal(t)
                    )
                ]
                if not feasible:
                    assert result.status == "no_budget"
                else:
                    assert int(result.allowed_chunks) == max(feasible)
                    assert result.required_hit_rate <= previous
                    previous = result.required_hit_rate
                checked += 1
    seconds = time.perf_counter() - started
    assert checked == 1000 and seconds < 2.0
    root = Path("artifacts/validation/user-monitoring/U004")
    root.mkdir(parents=True, exist_ok=True)
    (root / "estimator-performance.json").write_text(
        json.dumps(dict(cases=checked, seconds=seconds))
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"chunk_seconds": "0"},
        {"chunk_seconds": "NaN"},
        {"chunk_seconds": "Infinity"},
        {"chunk_tokens": "0"},
        {"overhead_seconds": "-1"},
        {"source": "verified_measurement"},
        {"min_prompt_tokens": "1000000"},
    ],
)
def test_invalid_scenario(changes):
    with pytest.raises(ValidationError):
        scenario(**changes)


@pytest.mark.parametrize(
    "changes",
    [
        {"target_seconds": "0"},
        {"target_seconds": "NaN"},
        {"waiting_seconds": "-1"},
        {"comparator": "="},
    ],
)
def test_invalid_request(changes):
    with pytest.raises(ValidationError):
        request(**changes)


@pytest.mark.parametrize(
    "field", ["chunk_tokens", "chunk_seconds", "overhead_seconds", "waiting_seconds"]
)
@pytest.mark.parametrize("missing", ["absent", "null", "blank"])
def test_required_parameters_have_no_defaults(field, missing):
    model = EvaluationRequest if field == "waiting_seconds" else Scenario
    data = (request() if field == "waiting_seconds" else scenario()).model_dump(mode="json")
    if missing == "absent":
        del data[field]
    else:
        data[field] = None if missing == "null" else ""
    with pytest.raises(ValidationError):
        model.model_validate(data)


def test_explicit_zero_wait_is_not_a_missing_value():
    assert request(waiting_seconds="0").waiting_seconds == "0"
    assert run(request(waiting_seconds="0")).request.waiting_seconds == "0"


@pytest.mark.parametrize(
    "field", ["chunk_tokens", "chunk_seconds", "overhead_seconds", "waiting_seconds"]
)
@pytest.mark.parametrize("missing", ["absent", "null", "blank"])
def test_http_missing_parameters_produce_no_rate_or_saved_evaluation(service, field, missing):
    from fastapi.testclient import TestClient

    from tokenscope.api.app import create_app

    app = create_app(service, start_worker=False)
    headers = {"X-TokenScope-Instance-Id": app.state.ma.service_id}
    data = (request() if field == "waiting_seconds" else scenario()).model_dump(mode="json")
    if missing == "absent":
        del data[field]
    else:
        data[field] = None if missing == "null" else ""
    endpoint = "evaluations" if field == "waiting_seconds" else "scenarios"
    with TestClient(app) as client:
        response = client.post(f"/monitoring/user-v2/{endpoint}", json=data, headers=headers)
    assert response.status_code == 422
    assert set(response.json()) == {"error"}
    with app.state.user.store.connect(readonly=True) as db:
        assert db.execute("SELECT count(*) FROM evaluations").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM scenarios").fetchone()[0] == 0

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient

from tokenscope.api.app import create_app
from tokenscope.user_monitoring.contracts import EvaluationRequest
from tokenscope.user_monitoring.estimator import EstimatorService


def new_scenario(model="GLM-5.2", common="GLM-V5.2"):
    return dict(
        timing_model="batch_reference_total_noncompute_v1",
        scenario_id="minimal",
        revision="1",
        model_id=model,
        common_name=common,
        deployment="synthetic fixed deployment",
        source="user_assumption",
        source_description="arithmetic fixture, not real calibration",
        chunk_tokens="8192",
        chunk_seconds="1",
    )


def req(run, **updates):
    value = dict(
        submission_key="eval",
        user_run_id=run,
        appid="tenant",
        scenario_id="minimal",
        scenario_revision="1",
        target_seconds="8",
        waiting_seconds="5",
        comparator="le",
    )
    value.update(updates)
    return value


@pytest.mark.parametrize(
    "model,common",
    [
        ("GLM-5.2", "GLM-V5.2"),
        ("Qwen3.6-27B", "Qwen-V3.6-27B"),
        ("DeepSeek-V4-Flash-0731", "DeepSeek-V4-Flash"),
    ],
)
def test_http_real_csv_new_and_legacy_restart(service, model, common):
    (service.inputs.root / "minimal.csv").write_bytes(
        csv_bytes(
            [
                valid_row(hash_id="dup"),
                valid_row(hash_id="dup"),
            ]
        )
    )
    app = create_app(service, start_worker=False)
    headers = {"X-TokenScope-Instance-Id": app.state.user.service_id}
    prefix = "/monitoring/user-v2"
    with TestClient(app) as client:
        created = client.post(
            prefix + "/runs",
            json=dict(
                submission_key="run",
                file_ref="minimal.csv",
                model_id=model,
                common_name=common,
            ),
            headers=headers,
        )
        assert created.status_code == 202, created.text
        run = created.json()["user_run_id"]
        app.state.user.process_next()
        assert service.processor.process_next().status == "completed"
        assert app.state.user.process_next().state == "ready"
        sc = new_scenario(model, common)
        posted = client.post(prefix + "/scenarios", json=sc, headers=headers)
        assert posted.status_code == 201, posted.text
        assert "overhead_seconds" not in posted.json()
        assert posted.json()["min_prompt_tokens"] is None
        assert client.post(prefix + "/scenarios", json=sc, headers=headers).json() == posted.json()
        assert (
            client.post(
                prefix + "/scenarios", json=dict(sc, chunk_seconds="2"), headers=headers
            ).status_code
            == 409
        )
        body = req(run)
        response = client.post(prefix + "/evaluations", json=body, headers=headers)
        assert response.status_code == 201, response.text
        result = response.json()
        assert result["request_count"] == "2"
        assert result["allowed_chunks"] == "3"
        p90 = int(result["prompt_p90"])
        assert result["required_hit_rate"] == max(0, (p90 - 24576) / p90)
        assert result["scenario"]["timing_model"] == sc["timing_model"]
        assert (
            client.post(
                prefix + "/evaluations", json=dict(body, waiting_seconds="0"), headers=headers
            ).status_code
            == 409
        )
        # Legacy client writes the unchanged 1.0.1 shape, still subtracting O.
        examples = json.loads(Path("docs/contracts/user-monitoring-v2/examples.json").read_text())
        legacy = next(e["value"] for e in examples if e["model"] == "Scenario" and e["valid"])
        legacy.update(scenario_id="legacy", model_id=model, common_name=common)
        assert client.post(prefix + "/scenarios", json=legacy, headers=headers).json() == legacy
        oldbody = req(run, submission_key="legacy-eval", scenario_id="legacy", waiting_seconds="3")
        old = client.post(prefix + "/evaluations", json=oldbody, headers=headers).json()
        assert old["allowed_chunks"] == "2"
        assert "timing_model" not in old["scenario"]
        assert (
            client.post(
                prefix + "/scenarios",
                json=dict(sc, revision="2", chunk_seconds="2"),
                headers=headers,
            ).status_code
            == 201
        )
        estimator = EstimatorService(app.state.user)
        with ThreadPoolExecutor(4) as pool:
            repeats = list(
                pool.map(
                    estimator.evaluate,
                    [EvaluationRequest.model_validate(req(run, submission_key="concurrent"))] * 8,
                )
            )
        assert len({r.evaluation_id for r in repeats}) == 1
        # GETs must not write state, and the OpenAPI must expose both branches.
        before = {p: p.stat().st_mtime_ns for p in service.state_root.rglob("*") if p.is_file()}
        assert (
            client.get(prefix + "/evaluations/" + result["evaluation_id"], headers=headers).json()
            == result
        )
        assert client.get(prefix + "/scenarios/legacy/1", headers=headers).json() == legacy
        assert before == {
            p: p.stat().st_mtime_ns for p in service.state_root.rglob("*") if p.is_file()
        }
        spec = app.openapi()
        variants = spec["paths"][prefix + "/scenarios"]["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"]["anyOf"]
        assert {v["$ref"].split("/")[-1] for v in variants} == {"Scenario", "BatchScenario"}
    # Fresh app instance, same disk; saved results remain usable even without the index.
    dbpath = app.state.user.store.path
    with app.state.user.store.connect(readonly=True) as db:
        snapshot = list(db.execute("SELECT id, payload FROM evaluations ORDER BY id"))
        stored = [(row[0], row[1]) for row in snapshot]
    (app.state.user.root / (run + ".sqlite3")).unlink()
    restarted = create_app(service, start_worker=False)
    with TestClient(restarted) as client:
        assert client.post(prefix + "/evaluations", json=body, headers=headers).json() == result
        assert client.post(prefix + "/evaluations", json=oldbody, headers=headers).json() == old
        digest = hashlib.sha256(dbpath.read_bytes()).hexdigest()
        for expected in (result, old):
            assert (
                client.get(
                    prefix + "/evaluations/" + expected["evaluation_id"], headers=headers
                ).json()
                == expected
            )
        assert hashlib.sha256(dbpath.read_bytes()).hexdigest() == digest
    with restarted.state.user.store.connect(readonly=True) as db:
        assert [
            (r[0], r[1]) for r in db.execute("SELECT id,payload FROM evaluations ORDER BY id")
        ] == stored
    output = Path("artifacts/validation/user-monitoring/U007")
    output.mkdir(parents=True, exist_ok=True)
    (output / (model + ".json")).write_text(json.dumps(dict(new=result, legacy=old), indent=2))


@pytest.mark.parametrize("field", ["chunk_tokens", "chunk_seconds", "waiting_seconds"])
@pytest.mark.parametrize("missing", ["absent", "null", "blank"])
def test_http_missing_never_defaults(service, field, missing):
    app = create_app(service, start_worker=False)
    headers = {"X-TokenScope-Instance-Id": app.state.user.service_id}
    value = req("missing-run") if field == "waiting_seconds" else new_scenario()
    if missing == "absent":
        del value[field]
    else:
        value[field] = None if missing == "null" else ""
    endpoint = "evaluations" if field == "waiting_seconds" else "scenarios"
    with TestClient(app) as client:
        response = client.post("/monitoring/user-v2/" + endpoint, json=value, headers=headers)
        assert response.status_code == 422
        assert set(response.json()) == {"error"}
    with app.state.user.store.connect(readonly=True) as db:
        assert db.execute("SELECT count(*) FROM scenarios").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM evaluations").fetchone()[0] == 0


@pytest.mark.parametrize(
    "changes",
    [
        {"timing_model": "future"},
        {"overhead_seconds": "0"},
        {"min_prompt_tokens": "1"},
    ],
)
def test_http_rejects_ambiguous_or_unknown_shapes(service, changes):
    app = create_app(service, start_worker=False)
    headers = {"X-TokenScope-Instance-Id": app.state.user.service_id}
    with TestClient(app) as client:
        response = client.post(
            "/monitoring/user-v2/scenarios", json=dict(new_scenario(), **changes), headers=headers
        )
        assert response.status_code == 422


def test_preupgrade_frozen_evaluation_replay_without_run(service):
    from tokenscope.user_monitoring.storage import canonical

    app = create_app(service, start_worker=False)
    examples = json.loads(Path("docs/contracts/user-monitoring-v2/examples.json").read_text())
    saved = next(e["value"] for e in examples if e["model"] == "Evaluation" and e["valid"])
    # Insert frozen 1.0.1 payload directly, not a result produced by the new calculator.
    payload = json.dumps(saved)
    with app.state.user.store.connect() as db:
        db.execute(
            "INSERT INTO evaluations VALUES(?,?,?,?)",
            (
                saved["evaluation_id"],
                saved["request"]["submission_key"],
                canonical(saved["request"]),
                payload,
            ),
        )
    headers = {"X-TokenScope-Instance-Id": app.state.user.service_id}
    with TestClient(create_app(service, start_worker=False)) as client:
        assert (
            client.get(
                "/monitoring/user-v2/evaluations/" + saved["evaluation_id"], headers=headers
            ).json()
            == saved
        )
        assert (
            client.post(
                "/monitoring/user-v2/evaluations", json=saved["request"], headers=headers
            ).json()
            == saved
        )
    with app.state.user.store.connect(readonly=True) as db:
        assert db.execute("SELECT payload FROM evaluations").fetchone()[0] == payload

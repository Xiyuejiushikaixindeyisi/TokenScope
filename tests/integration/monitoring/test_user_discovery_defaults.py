"""HV2-R1-USER synthetic sealed fixtures: not Huawei production data."""

import hashlib
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tokenscope.api.app import create_app
from tokenscope.user_monitoring.contracts import Evaluation
from tokenscope.user_monitoring.defaults import DefaultEstimator
from tokenscope.user_monitoring.discovery_contracts import (
    AutoEvaluationRequest,
    DefaultQuery,
    DefaultUpdate,
)
from tokenscope.user_monitoring.projection import build
from tokenscope.user_monitoring.storage import canonical

MODELS = [
    ("Qwen3.6-27B", "Qwen-V3.6-27B", "1"),
    ("GLM-5.2", "GLM-V5.2", "2.7"),
    ("DeepSeek-V4-Flash-0731", "DeepSeek-V4-Flash", "2.6"),
]
PREFIX = "/monitoring/user-v2"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(root):
    return {
        str(p.relative_to(root)): (p.stat().st_mtime_ns, digest(p))
        for p in root.rglob("*")
        if p.is_file()
    }


@pytest.fixture
def context(service):
    app = create_app(service, start_worker=False)
    user = app.state.user
    headers = {"X-TokenScope-Instance-Id": user.service_id}

    def publish(model=MODELS[0], groups=None, state="ready"):
        groups = {"shared": [32768, 32768], "single": [100]} if groups is None else groups
        base_id, run_id = str(uuid4()), "ur-" + uuid4().hex
        folder = service.state_root / "runs" / base_id
        folder.mkdir(parents=True)
        summary = dict(
            run_id=base_id,
            model_id=model[0],
            input_sha256="a" * 64,
            settings={"model_id": model[0]},
            runtime={"encoder_identity": "synthetic-encoder", "asset_identity": "synthetic-assets"},
            time_range_utc=["2026-10-20T07:00:00Z", "2026-10-20T09:18:57Z"],
        )
        (folder / "summary.json").write_text(json.dumps(summary))
        (folder / "manifest.json").write_text(
            json.dumps(
                dict(
                    run_id=base_id,
                    files=[
                        {"path": "summary.json", "sha256": digest(folder / "summary.json")},
                    ],
                )
            )
        )
        source = folder / "requests.sqlite3"
        with sqlite3.connect(source) as db:
            db.execute(
                "CREATE TABLE facts(appid,prompt_tokens,ideal_cached_input_tokens,"
                "ideal_compute_input_tokens)"
            )
            db.executemany(
                "INSERT INTO facts VALUES(?,?,0,?)",
                [(a, v, v) for a, values in groups.items() for v in values],
            )
        metadata = dict(
            user_run_id=run_id,
            base_run_id=base_id,
            common_name=model[1],
            source_seal=digest(folder / "manifest.json"),
            file_quality=dict(read_rows="2", valid_rows="2", skipped_rows="0"),
        )
        revision = build(source, user.root / (run_id + ".sqlite3"), metadata)
        with user.store.connect() as db:
            db.execute(
                "INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    run_id,
                    run_id,
                    "{}",
                    base_id,
                    model[1],
                    model[0],
                    state,
                    revision,
                    None if state in ("ready", "empty") else "TEST",
                ),
            )
        return run_id, revision, base_id

    return app, headers, publish


def payload(run, revision, key="eval", **kwargs):
    result = dict(
        submission_key=key,
        user_run_id=run,
        appid="shared",
        index_revision=revision,
        waiting_seconds="5",
        target_seconds="8",
    )
    result.update(kwargs)
    return result


def test_discovery_cold_pagination_models_defaults_history_restart(service, context):
    app, headers, publish = context
    with TestClient(app) as client:
        assert client.get(PREFIX + "/runs", headers=headers).json()["entries"] == []
        assert client.get(PREFIX + "/runs").status_code == 409
        older = publish()
        glm = publish(MODELS[1], {"shared": [32768], "glm-only": [12]})
        ds = publish(MODELS[2], {"shared": [32768]})
        latest = publish(groups={"shared": [16000]})
        publish(state="indexing")
        publish(state="failed")
        empty = publish(groups={}, state="empty")
        before = fingerprint(service.state_root)
        first = client.get(
            PREFIX + "/runs", params={"appid": "shared", "limit": 1}, headers=headers
        ).json()
        assert first["total"] == "4"
        entries = first["entries"]
        offset = first["next_offset"]
        while offset is not None:
            page = client.get(
                PREFIX + "/runs",
                params=dict(appid="shared", limit=1, offset=offset, snapshot=first["snapshot"]),
                headers=headers,
            ).json()
            assert page["snapshot"] == first["snapshot"]
            entries += page["entries"]
            offset = page["next_offset"]
        assert {e["source"]["model_id"] for e in entries} == {m[0] for m in MODELS}
        assert {e["source"]["user_run_id"] for e in entries if e["is_default"]} == {
            latest[0],
            glm[0],
            ds[0],
        }
        assert entries[-1]["source"]["user_run_id"] == older[0]
        assert entries[-1]["is_default"] is False
        assert (
            client.get(PREFIX + "/runs", params={"appid": "glm-only"}, headers=headers).json()[
                "total"
            ]
            == "1"
        )
        assert (
            client.get(PREFIX + "/runs", params={"offset": "1"}, headers=headers).status_code == 409
        )
        assert (
            client.get(PREFIX + "/runs", params={"snapshot": "f" * 64}, headers=headers).status_code
            == 409
        )
        assert (
            client.get(
                PREFIX + "/runs", params={"user_run_id": "ur-unknown"}, headers=headers
            ).status_code
            == 404
        )
        found = client.get(
            PREFIX + "/runs", params={"user_run_id": empty[0]}, headers=headers
        ).json()["entries"][0]
        assert found["appid"] is None and found["state"] == "empty"
        assert found["prompt_p90"] is None
        assert fingerprint(service.state_root) == before
        fixed = client.get(
            PREFIX + "/runs", params={"user_run_id": older[0]}, headers=headers
        ).json()
        publish(groups={"shared": [99]})
        assert (
            client.get(
                PREFIX + "/runs",
                params=dict(appid="shared", snapshot=first["snapshot"], offset="1"),
                headers=headers,
            ).status_code
            == 409
        )
    with TestClient(create_app(service, start_worker=False)) as client:
        after = client.get(
            PREFIX + "/runs", params={"user_run_id": older[0]}, headers=headers
        ).json()
        assert after == fixed  # fixed historical row does not become another run


@pytest.mark.parametrize("model", MODELS)
def test_auto_defaults_and_exact_calculation(service, context, model):
    app, headers, publish = context
    run, rev, _ = publish(model)
    with TestClient(app) as client:
        before = fingerprint(service.state_root)
        config = client.get(
            PREFIX + "/ttft/defaults",
            params=dict(common_name=model[1], model_id=model[0]),
            headers=headers,
        ).json()["configs"][0]
        assert config["chunk_seconds"] == model[2]
        assert config["chunk_tokens"] == config["tau_reference_chunk_tokens"] == "8192"
        assert config["calibrated"] is False and config["source"] == "user_provided"
        assert fingerprint(service.state_root) == before
        value = payload(run, rev)
        response = client.post(PREFIX + "/ttft/evaluations", json=value, headers=headers)
        assert response.status_code == 201, response.text
        result = response.json()
        assert result["defaults"] == config
        assert result["evaluation"]["scenario"]["model_id"] == model[0]
        assert result["evaluation"]["request"]["comparator"] == "le"
        assert result["evaluation"]["allowed_chunks"] == ("3" if model == MODELS[0] else "1")
        old_id = result["evaluation_id"]
        override = client.post(
            PREFIX + "/ttft/evaluations",
            json=payload(run, rev, "override", chunk_tokens="4096"),
            headers=headers,
        ).json()
        assert override["chunk_tokens_origin"] == "request_override" and not override["tau_scaled"]
        assert override["evaluation"]["scenario"]["chunk_seconds"] == model[2]
        assert any("not proportionally" in msg for msg in override["evaluation"]["limitations"])
        restored = client.post(
            PREFIX + "/ttft/evaluations", json=payload(run, rev, "restored"), headers=headers
        ).json()
        assert restored["evaluation"]["scenario"]["chunk_tokens"] == "8192"
        assert (
            client.post(
                PREFIX + "/ttft/evaluations", json=dict(value, target_seconds="9"), headers=headers
            ).status_code
            == 409
        )
        assert (
            client.post(
                PREFIX + "/ttft/evaluations",
                json=payload(run, "b" * 64, "wrong-index"),
                headers=headers,
            ).status_code
            == 409
        )
        malformed = payload(run, rev, "wrong-model", model_id=MODELS[1][0])
        assert (
            client.post(PREFIX + "/ttft/evaluations", json=malformed, headers=headers).status_code
            == 422
        )
    with TestClient(create_app(service, start_worker=False)) as client:
        before = fingerprint(service.state_root)
        assert client.get(PREFIX + "/ttft/evaluations/" + old_id, headers=headers).json() == result
        assert fingerprint(service.state_root) == before
        assert (
            client.post(PREFIX + "/ttft/evaluations", json=value, headers=headers).json() == result
        )


def test_config_cas_idempotency_missing_tau_and_history(service, context):
    app, headers, publish = context
    run, rev, _ = publish()
    endpoint = PREFIX + "/ttft/defaults"
    update = dict(
        submission_key="config",
        model_id=MODELS[0][0],
        common_name=MODELS[0][1],
        expected_revision="1",
        chunk_seconds="0.5",
        source_description="synthetic fixture",
    )
    with TestClient(app) as client:
        initial = client.post(
            PREFIX + "/ttft/evaluations", json=payload(run, rev), headers=headers
        ).json()
        response = client.post(endpoint, json=update, headers=headers)
        assert response.status_code == 201
        config = response.json()
        assert config["revision"] == "2"
        assert client.post(endpoint, json=update, headers=headers).json() == config
        assert (
            client.post(endpoint, json=dict(update, chunk_seconds="1"), headers=headers).status_code
            == 409
        )
        assert (
            client.post(
                endpoint, json=dict(update, submission_key="stale"), headers=headers
            ).status_code
            == 409
        )
        assert (
            client.post(
                endpoint,
                json=dict(update, submission_key="cross-model", model_id=MODELS[1][0]),
                headers=headers,
            ).status_code
            == 422
        )
        current = client.post(
            PREFIX + "/ttft/evaluations", json=payload(run, rev, "new"), headers=headers
        ).json()
        assert current["defaults"]["revision"] == "2"
        assert current["evaluation"]["required_hit_rate"] == 0
        fixed = client.post(
            PREFIX + "/ttft/evaluations",
            json=payload(run, rev, "old-config", default_revision="1"),
            headers=headers,
        ).json()
        assert (
            fixed["evaluation"]["required_hit_rate"] == initial["evaluation"]["required_hit_rate"]
        )
        assert (
            client.post(
                PREFIX + "/ttft/evaluations",
                json=payload(run, rev, "unknown-config", default_revision="999"),
                headers=headers,
            ).status_code
            == 404
        )
        assert (
            client.get(
                endpoint,
                params=dict(common_name=MODELS[0][1], model_id=MODELS[0][0], revision="999"),
                headers=headers,
            ).status_code
            == 404
        )
        clear = dict(update, submission_key="clear", expected_revision="2", chunk_seconds=None)
        assert client.post(endpoint, json=clear, headers=headers).json()["revision"] == "3"
    with TestClient(create_app(service, start_worker=False)) as client:
        # startup must not overwrite explicit null with the bootstrap default.
        response = client.post(
            PREFIX + "/ttft/evaluations", json=payload(run, rev, "missing"), headers=headers
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "TTFT_DEFAULT_NOT_CONFIGURED"
        assert (
            client.post(
                PREFIX + "/ttft/evaluations", json=payload(run, rev), headers=headers
            ).json()
            == initial
        )
        unknown = client.get(
            endpoint, params=dict(common_name="unknown", model_id=MODELS[0][0]), headers=headers
        ).json()
        assert unknown["configs"] == []


def test_k_configuration_restore_and_concurrent_evaluation(context):
    app, _, publish = context
    run, rev, _ = publish()
    service = DefaultEstimator(app.state.user)
    config = service.update(
        DefaultUpdate(
            submission_key="set-k",
            common_name=MODELS[0][1],
            model_id=MODELS[0][0],
            expected_revision="1",
            chunk_tokens="4096",
            chunk_seconds="1",
            source_description="synthetic fixed tau, changed K",
        )
    )
    assert config.chunk_tokens == "4096"
    req = AutoEvaluationRequest.model_validate(payload(run, rev))
    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(service.evaluate, [req] * 8))
    assert len({r.evaluation_id for r in results}) == 1
    assert results[0].evaluation.scenario.chunk_tokens == "4096"
    assert results[0].defaults.tau_reference_chunk_tokens == "8192"
    service.update(
        DefaultUpdate(
            submission_key="restore-k",
            common_name=MODELS[0][1],
            model_id=MODELS[0][0],
            expected_revision="2",
            chunk_seconds="1",
            source_description="restore fixture K",
        )
    )
    assert (
        service.get(DefaultQuery(model_id=MODELS[0][0], common_name=MODELS[0][1]))
        .configs[0]
        .chunk_tokens
        == "8192"
    )


@pytest.mark.parametrize(
    "wait,target,cmp,chunks,status",
    [
        ("0", "1", "le", "1", "reference"),
        ("5", "5", "le", "0", "reference_with_limit"),
        ("5", "5", "lt", None, "no_budget"),
        ("5", "4", "le", None, "no_budget"),
    ],
)
def test_auto_budget_edges(context, wait, target, cmp, chunks, status):
    app, headers, publish = context
    run, rev, _ = publish()
    with TestClient(app) as client:
        response = client.post(
            PREFIX + "/ttft/evaluations",
            json=payload(run, rev, waiting_seconds=wait, target_seconds=target, comparator=cmp),
            headers=headers,
        )
        value = response.json()["evaluation"]
        assert value["status"] == status and value["allowed_chunks"] == chunks


def test_decimal_equality_empty_and_no_p90(context):
    app, headers, publish = context
    run, rev, _ = publish(MODELS[1])
    zero, zrev, _ = publish(groups={"shared": [0]})
    empty, erev, _ = publish(groups={}, state="empty")
    with TestClient(app) as client:
        for cmp, n in (("le", "1"), ("lt", "0")):
            result = client.post(
                PREFIX + "/ttft/evaluations",
                json=payload(run, rev, cmp, target_seconds="7.7", comparator=cmp),
                headers=headers,
            ).json()
            assert result["evaluation"]["allowed_chunks"] == n
        for i, revision in ((zero, zrev), (empty, erev)):
            result = client.post(
                PREFIX + "/ttft/evaluations", json=payload(i, revision, i), headers=headers
            ).json()
            assert result["evaluation"]["reason"] == "NO_POSITIVE_P90"


@pytest.mark.parametrize("field", ["waiting_seconds", "target_seconds"])
@pytest.mark.parametrize("kind", ["absent", "null", "blank"])
def test_auto_no_missing_time_defaults(context, field, kind):
    app, headers, _ = context
    data = payload("unknown", "a" * 64)
    if kind == "absent":
        del data[field]
    else:
        data[field] = None if kind == "null" else ""
    with TestClient(app) as client:
        response = client.post(PREFIX + "/ttft/evaluations", json=data, headers=headers)
        assert response.status_code == 422


def test_frozen_old_evaluations_still_read(context):
    app, headers, _ = context
    examples = json.loads(Path("docs/contracts/user-monitoring-v2/2.0.0/examples.json").read_text())
    saved = next(e["value"] for e in examples if e["model"] == "Evaluation" and e["valid"])
    Evaluation.model_validate(saved)
    with app.state.user.store.connect() as db:
        db.execute(
            "INSERT INTO evaluations VALUES(?,?,?,?)",
            (
                saved["evaluation_id"],
                saved["request"]["submission_key"],
                canonical(saved["request"]),
                json.dumps(saved),
            ),
        )
    with TestClient(app) as client:
        assert (
            client.get(PREFIX + "/evaluations/" + saved["evaluation_id"], headers=headers).json()
            == saved
        )


def test_candidate_contract_artifacts(context):
    """Export only with explicit opt-in; ordinary test verifies candidate/runtime agreement."""
    import os

    from pydantic.json_schema import models_json_schema

    from tokenscope.user_monitoring import discovery_contracts as c

    app, headers, publish = context
    run, rev, _ = publish()
    models = [
        c.DiscoveryQuery,
        c.TraceSource,
        c.DiscoveryEntry,
        c.DiscoveryPage,
        c.DefaultConfig,
        c.DefaultUpdate,
        c.DefaultQuery,
        c.DefaultPage,
        c.AutoEvaluationRequest,
        c.AutoEvaluation,
    ]
    _, schema = models_json_schema(
        [(model, "validation") for model in models], title="User monitoring 2.1.0 candidate"
    )
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    full = app.openapi()
    paths = {p: v for p, v in full["paths"].items() if p.startswith(PREFIX + "/")}
    assert sum(len(v) for v in paths.values()) == 14
    components = {}

    def collect(value):
        if isinstance(value, dict):
            ref = value.get("$ref", "")
            if ref.startswith("#/components/schemas/"):
                name = ref.rsplit("/", 1)[1]
                if name not in components:
                    components[name] = full["components"]["schemas"][name]
                    collect(components[name])
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(paths)
    spec = dict(
        openapi=full["openapi"],
        info=dict(title="User monitoring candidate (not independently frozen)", version="2.1.0"),
        paths=paths,
        components={"schemas": dict(sorted(components.items()))},
    )
    for methods in paths.values():
        for operation in methods.values():
            assert operation["x-user-contract-version"] == "2.1.0"
            assert any(
                p["name"] == "X-TokenScope-Instance-Id" and p["required"]
                for p in operation["parameters"]
            )
    out = Path("docs/contracts/user-monitoring-v2/2.1.0")
    if os.environ.get("TOKENSCOPE_UPDATE_USER_CONTRACT") == "1":
        out.mkdir(parents=True, exist_ok=True)
        with TestClient(app) as client:
            examples = []
            for model, url in (
                ("DiscoveryPage", "/runs"),
                ("DefaultPage", "/ttft/defaults"),
            ):
                response = client.get(PREFIX + url, headers=headers)
                assert response.status_code == 200
                examples.append(dict(model=model, value=response.json(), valid=True))
            request = payload(run, rev, "candidate-example")
            response = client.post(PREFIX + "/ttft/evaluations", headers=headers, json=request)
            assert response.status_code == 201
            examples += [
                dict(model="AutoEvaluationRequest", value=request, valid=True),
                dict(model="AutoEvaluation", value=response.json(), valid=True),
                dict(
                    model="AutoEvaluationRequest",
                    value={k: v for k, v in request.items() if k != "waiting_seconds"},
                    valid=False,
                ),
                dict(
                    model="AutoEvaluationRequest",
                    value={**request, "chunk_tokens": "0"},
                    valid=False,
                ),
                dict(
                    model="AutoEvaluationRequest",
                    value={**request, "overhead_seconds": "0"},
                    valid=False,
                ),
                dict(
                    model="DefaultUpdate",
                    value=dict(
                        submission_key="update-example",
                        model_id=MODELS[0][0],
                        common_name=MODELS[0][1],
                        expected_revision="1",
                        chunk_seconds="1",
                        source_description="Synthetic update example",
                    ),
                    valid=True,
                ),
            ]
        for name, value in (
            ("schema.json", schema),
            ("runtime.openapi.json", spec),
            ("examples.json", examples),
        ):
            (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        (out / "manifest.json").write_text(
            json.dumps(
                {
                    "contract_version": "2.1.0",
                    "status": "candidate_pending_independent_acceptance",
                    "fixture": "synthetic; examples are not production data",
                    "operations": 14,
                    "sha256": {
                        p.name: digest(p)
                        for p in sorted(out.glob("*.json"))
                        if p.name != "manifest.json"
                    },
                },
                indent=2,
            )
            + "\n"
        )
    assert json.loads((out / "schema.json").read_text()) == schema
    assert json.loads((out / "runtime.openapi.json").read_text()) == spec
    for name, expected in json.loads((out / "manifest.json").read_text())["sha256"].items():
        assert digest(out / name) == expected
    by_name = {model.__name__: model for model in models}
    for example in json.loads((out / "examples.json").read_text()):
        if example["valid"]:
            by_name[example["model"]].model_validate_json(json.dumps(example["value"]))
        else:
            with pytest.raises(ValueError):
                by_name[example["model"]].model_validate_json(json.dumps(example["value"]))


def test_catalog_rejects_corrupt_source_without_repair(context):
    app, headers, publish = context
    _, _, base = publish()
    folder = app.state.user.base.state_root / "runs" / base
    target = folder / "summary.json"
    target.write_text("{}")
    before = fingerprint(app.state.user.base.state_root)
    with TestClient(app) as client:
        result = client.get(PREFIX + "/runs", headers=headers)
        assert result.status_code == 409
    assert before == fingerprint(app.state.user.base.state_root)

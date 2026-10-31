"""Generate/recheck frozen user-v2 contract artifacts; no service startup."""

import hashlib
import json
from pathlib import Path

from pydantic import ValidationError
from pydantic.json_schema import models_json_schema

from tokenscope.user_monitoring import contracts as c

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/contracts/user-monitoring-v2/2.0.0"
MODELS = [
    c.Submit,
    c.Bind,
    c.Receipt,
    c.Ranking,
    c.Modes,
    c.Scenario,
    c.BatchScenario,
    c.EvaluationRequest,
    c.Evaluation,
    c.ErrorEnvelope,
]
MODELS_BY_NAME = {m.__name__: m for m in MODELS}


def dump(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _, schema = models_json_schema(
        [(m, "validation") for m in MODELS], title="User monitoring 2.0.0"
    )
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    dump("schema.json", schema)
    components = json.loads(
        json.dumps(schema["$defs"]).replace("#/$defs/", "#/components/schemas/")
    )
    components["ScenarioPayload"] = {
        "anyOf": [
            {"$ref": "#/components/schemas/Scenario"},
            {"$ref": "#/components/schemas/BatchScenario"},
        ]
    }
    paths = {}
    operations = [
        ("/runs", "post", "Submit", "Receipt", "202"),
        ("/bindings", "post", "Bind", "Receipt", "202"),
        ("/runs/{user_run_id}", "get", None, "Receipt", "200"),
        ("/runs/{user_run_id}/rankings", "get", None, "Ranking", "200"),
        ("/runs/{user_run_id}/modes", "get", None, "Modes", "200"),
        ("/scenarios", "post", "ScenarioPayload", "ScenarioPayload", "201"),
        ("/scenarios/{scenario_id}/{revision}", "get", None, "ScenarioPayload", "200"),
        ("/evaluations", "post", "EvaluationRequest", "Evaluation", "201"),
        ("/evaluations/{evaluation_id}", "get", None, "Evaluation", "200"),
    ]

    def response(model):
        return {
            "description": model,
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + model}}},
        }

    for path, verb, request, result, status in operations:
        params = [
            {
                "name": part[1:-1],
                "in": "path",
                "required": True,
                "schema": {"type": "string", "minLength": 1},
            }
            for part in path.split("/")
            if part.startswith("{")
        ]
        params.append(
            {
                "name": "X-TokenScope-Instance-Id",
                "in": "header",
                "required": True,
                "schema": {"type": "string", "minLength": 1},
            }
        )
        query = {}
        if path.endswith("/rankings"):
            query = {
                "appid_contains": {"type": "string"},
                "bin_width": {"type": "integer", "enum": [1000, 2000, 5000], "default": 5000},
                "sort": {
                    "type": "string",
                    "enum": [
                        "request_count",
                        "ideal_hit_rate",
                        "total_ideal_compute_tokens",
                        "typical_ideal_compute_tokens",
                    ],
                    "default": "request_count",
                },
                "direction": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
            }
            for key in [
                "request_count",
                "ideal_hit_rate",
                "total_ideal_compute_tokens",
                "typical_ideal_compute_tokens",
            ]:
                for suffix in ["min", "max"]:
                    query[key + "_" + suffix] = {
                        "type": "string",
                        "pattern": (
                            r"^(0|[1-9][0-9]*)$"
                            if key in ("request_count", "total_ideal_compute_tokens")
                            else r"^(0|[1-9][0-9]*)(\.[0-9]+)?$"
                        ),
                        "maxLength": 128,
                    }
        if path.endswith(("/rankings", "/modes")):
            query.update(
                {
                    "index_revision": {"type": "string"},
                    "offset": {"type": "string", "pattern": r"^(0|[1-9][0-9]*)$", "default": "0"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100},
                }
            )
        if path.endswith("/modes"):
            query.update(
                {
                    "appid": {"type": "string", "minLength": 1},
                    "bin_width": {"type": "integer", "enum": [1000, 2000, 5000], "default": 5000},
                }
            )
        params.extend(
            {"name": k, "in": "query", "required": k == "appid", "schema": v}
            for k, v in query.items()
        )
        operation = {
            "operationId": verb
            + "_"
            + path.strip("/").replace("/", "_").replace("{", "").replace("}", ""),
            "x-runtime-implemented": False,
            "parameters": params,
            "responses": {
                status: response(result),
                **{x: response("ErrorEnvelope") for x in ["404", "409", "422", "503"]},
            },
        }
        if request:
            operation["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/" + request}}
                },
            }
        paths["/monitoring/user-v2" + path] = {verb: operation}
    dump(
        "design.openapi.json",
        {
            "openapi": "3.1.0",
            "info": {"title": "User monitoring design", "version": "2.0.0"},
            "paths": paths,
            "components": {"schemas": components},
        },
    )
    examples = []
    receipt = {
        "service_instance_id": "synthetic-service",
        "user_run_id": "synthetic-user-run",
        "base_run_id": None,
        "common_name": "Qwen-V3.6-27B",
        "model_id": "Qwen3.6-27B",
        "index_revision": None,
        "error_code": None,
    }
    for state in c.UserState:
        examples.append(
            {
                "model": "Receipt",
                "valid": True,
                "value": dict(
                    receipt,
                    state=state.value,
                    base_run_id="base" if state.value in ("ready", "empty") else None,
                    index_revision="1" if state.value == "ready" else None,
                    error_code="TEST" if state.value in ("failed", "interrupted") else None,
                ),
            }
        )
    examples.extend(
        [
            {
                "model": "Submit",
                "valid": True,
                "value": {
                    "submission_key": "test",
                    "file_ref": "qwen.csv",
                    "common_name": "Qwen-V3.6-27B",
                    "model_id": "Qwen3.6-27B",
                },
            },
            {
                "model": "Submit",
                "valid": False,
                "value": {
                    "submission_key": "test",
                    "file_ref": "qwen.csv",
                    "common_name": "Qwen-V3.6-27B",
                    "model_id": "unknown",
                },
            },
            {"model": "Receipt", "valid": False, "value": dict(receipt, state="ready", extra=True)},
        ]
    )
    scenario = {
        "scenario_id": "synthetic",
        "revision": "1",
        "model_id": "Qwen3.6-27B",
        "common_name": "Qwen-V3.6-27B",
        "deployment": "synthetic only",
        "source": "user_assumption",
        "source_description": "arithmetic fixture, not measured",
        "evidence_sha256": None,
        "measurement_boundary": "GF dispatch to first token; assumed",
        "workload_description": "synthetic",
        "thinking_mode": "default",
        "min_prompt_tokens": "1",
        "max_prompt_tokens": "131072",
        "chunk_tokens": "8192",
        "chunk_seconds": "2",
        "overhead_seconds": "1",
        "sample_count": "0",
        "calibration_notes": "not calibrated",
    }
    examples.append({"model": "Scenario", "valid": True, "value": scenario})
    examples.append(
        {
            "model": "Scenario",
            "valid": False,
            "value": dict(scenario, source="verified_measurement"),
        }
    )
    examples.append(
        {"model": "Scenario", "valid": False, "value": dict(scenario, chunk_seconds="0")}
    )
    request = {
        "submission_key": "sample",
        "user_run_id": "synthetic-user-run",
        "appid": "tenant",
        "scenario_id": "synthetic",
        "scenario_revision": "1",
        "target_seconds": "8",
        "waiting_seconds": "3",
        "comparator": "le",
    }
    for state in ["reference", "reference_with_limit", "no_budget", "out_of_scope", "unavailable"]:
        ok = state.startswith("reference")
        examples.append(
            {
                "model": "Evaluation",
                "valid": True,
                "value": {
                    "evaluation_id": "synthetic-eval",
                    "service_instance_id": "synthetic-service",
                    "request": request,
                    "scenario": scenario,
                    "status": state,
                    "reason": None if ok else state,
                    "request_count": "10",
                    "prompt_p90": "32768",
                    "allowed_chunks": "2" if ok else None,
                    "computable_tokens": "16384" if ok else None,
                    "required_hit_fraction": {"numerator": "16384", "denominator": "32768"}
                    if ok
                    else None,
                    "required_hit_rate": 0.5 if ok else None,
                    "limitations": ["not a production SLA guarantee"],
                },
            }
        )
    mode = {
        "lower": "0",
        "upper": "5000",
        "count": "2",
        "sum_compute_tokens": "300",
        "share": 1.0,
        "mean": {"numerator": "300", "denominator": "2"},
    }
    row = {
        "appid": "tenant",
        "request_count": "2",
        "total_prompt_tokens": "300",
        "total_ideal_cached_tokens": "0",
        "total_ideal_compute_tokens": "300",
        "ideal_hit_rate": 0.0,
        "prompt_p90": "200",
        "typical_compute_tokens": mode["mean"],
        "representative_bin": mode,
        "tie_count": "1",
    }
    ranking = {
        "service_instance_id": "synthetic-service",
        "user_run_id": "synthetic-user-run",
        "common_name": "Qwen-V3.6-27B",
        "index_revision": "1",
        "bin_width": 5000,
        "total": "1",
        "next_offset": None,
        "file_quality": {"read_rows": "2", "valid_rows": "2", "skipped_rows": "0"},
        "rows": [row],
    }
    examples.extend(
        [
            {
                "model": "Bind",
                "valid": True,
                "value": {
                    "submission_key": "bind",
                    "base_run_id": "base",
                    "common_name": "Qwen-V3.6-27B",
                },
            },
            {"model": "Ranking", "valid": True, "value": ranking},
            {
                "model": "Ranking",
                "valid": False,
                "value": dict(ranking, rows=[dict(row, total_prompt_tokens="400")]),
            },
            {
                "model": "Modes",
                "valid": True,
                "value": {
                    "user_run_id": "synthetic-user-run",
                    "appid": "tenant",
                    "index_revision": "1",
                    "bin_width": 5000,
                    "total": "1",
                    "next_offset": None,
                    "bins": [mode],
                },
            },
            {"model": "EvaluationRequest", "valid": True, "value": request},
            {
                "model": "EvaluationRequest",
                "valid": False,
                "value": dict(request, target_seconds="0"),
            },
            {"model": "Receipt", "valid": False, "value": dict(receipt, state="ready")},
            {
                "model": "ErrorEnvelope",
                "valid": True,
                "value": {"error": {"code": "INDEX_NOT_READY", "message": "Index unavailable"}},
            },
        ]
    )
    minimal = {
        k: scenario[k]
        for k in (
            "scenario_id",
            "revision",
            "model_id",
            "common_name",
            "deployment",
            "source",
            "source_description",
            "chunk_tokens",
            "chunk_seconds",
        )
    }
    minimal["timing_model"] = "batch_reference_total_noncompute_v1"
    examples.append({"model": "BatchScenario", "valid": True, "value": minimal})
    for changes in (
        {"overhead_seconds": "0"},
        {"timing_model": "unknown"},
        {"min_prompt_tokens": "1"},
        {"chunk_seconds": "0"},
    ):
        examples.append(
            {"model": "BatchScenario", "valid": False, "value": dict(minimal, **changes)}
        )
    for example in examples:
        try:
            MODELS_BY_NAME[example["model"]].model_validate_json(json.dumps(example["value"]))
            passed = True
        except ValidationError:
            passed = False
        assert passed == example["valid"], example
    dump("examples.json", examples)
    manifest = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in OUT.iterdir()
        if p.suffix == ".json" and p.name != "manifest.json"
    }
    dump("manifest.json", manifest)
    print(
        json.dumps(
            {
                "examples": len(examples),
                "schemas": len(components),
                "operations": len(operations),
                "status": "passed",
            }
        )
    )


if __name__ == "__main__":
    main()

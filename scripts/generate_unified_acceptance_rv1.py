"""Generate a new, synthetic unified acceptance state using existing production APIs."""

import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from tokenscope.analysis_common.contracts import (
    DiagnosticRequest,
    DiagnosticSelection,
    SourceSelection,
)
from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.plugins import BudgetSpec, PluginRegistry, PluginSelection
from tokenscope.analysis_common.proposal_plugins import ProposalRegistry
from tokenscope.analysis_common.recommendation_runtime import RecommendationSettings
from tokenscope.analysis_common.recommendations import RecipeBundle, RecommendationBudget
from tokenscope.analysis_common.runtime import RuntimeOptions
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.api.app import create_app
from tokenscope.domain import RunSubmission
from tokenscope.monitoring.service import MonitoringService
from tokenscope.token_content.auto_proposals import TokenProposalAdapter
from tokenscope.token_content.current_plugin import CurrentTokenContentPlugin


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if not output.is_relative_to(root / "artifacts/validation"):
        raise ValueError("Output must be under project artifacts/validation")
    output.mkdir(parents=True, exist_ok=False)  # Never overwrite an acceptance state.
    old = root / "artifacts/validation/art4-readable-20261031-01/test_chinese_recipes_actual_se0"
    inputs = output / "inputs"
    inputs.mkdir()
    with (old / "inputs/synthetic-orders.csv").open(newline="", encoding="utf-8") as f:
        old_rows = list(csv.DictReader(f))
    original = next(row for row in old_rows if row["appid"] == "synthetic-orders")
    mapping = json.loads((old / "synthetic-reference-map.json").read_text())
    original_body = json.loads(original["request_input"])
    assert mapping["fixture://orders/snapshot-001"] == original_body["messages"][2]["content"]
    rows = []
    for i in range(6):
        body = copy.deepcopy(original_body)
        body["messages"].insert(
            0,
            {
                "role": "system",
                "content": f"构造采样时间 2026-11-01 09:00:0{i}\n" + "稳定订单汇总规则；" * 300,
            },
        )
        # Preserve exact duplicated latest result/argument/user payload for T3. Alternate only
        # the earlier result's JSON representation to exercise L5 without changing its values.
        if i % 2:
            body["messages"][3]["content"] = json.dumps(
                json.loads(body["messages"][3]["content"]), ensure_ascii=False, indent=2
            )
        rows.append(
            {
                **original,
                "hash_id": f"unified-{i}",
                "model_handle_start_time": f"2026-11-01T09:00:0{i}Z",
                "request_input": json.dumps(body, ensure_ascii=False),
            }
        )
    rows.append({**rows[0], "appid": "excluded-app", "hash_id": "excluded"})
    with (inputs / "unified-orders.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(original))
        writer.writeheader()
        writer.writerows(rows)
    for name in ["synthetic-recipes.json", "synthetic-reference-map.json"]:
        (output / name).write_bytes((old / name).read_bytes())
    bundle = RecipeBundle.model_validate_json((output / "synthetic-recipes.json").read_bytes())
    service = MonitoringService(inputs, output / "state")
    run = service.submit(RunSubmission(file_ref="unified-orders.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    registry = PluginRegistry()
    registry.register(CurrentTokenContentPlugin())
    adapters = ProposalRegistry()
    adapters.register(TokenProposalAdapter())
    settings = RecommendationSettings(adapters, bundle)
    diagnostics = DiagnosticService(SourceResolver(service), registry, settings)
    options = RuntimeOptions(
        token_selection=PluginSelection(
            rule_ids=("T2", "T3", "T4"),
            budget=BudgetSpec(
                max_request_bytes=1048576,
                max_units=10000,
                max_comparison_bytes=1000000,
                max_depth=64,
                max_candidates=1000,
                max_encoding_calls=1000,
            ),
        ),
        candidate_limit=16,
        pilot_limit=3,
        max_source_requests=100,
        max_source_bytes=10000000,
        max_findings=1000,
        max_experiments=8,
        max_combinations=2,
        max_encoding_calls=1000,
    )
    tasks = []
    for label in ["history_ready", "default_ready", "latest_partial"]:
        if label == "latest_partial":
            diagnostics = DiagnosticService(
                SourceResolver(service),
                registry,
                RecommendationSettings(adapters, bundle, RecommendationBudget(max_proposals=1)),
            )
        task = diagnostics.submit(
            DiagnosticRequest(
                source=SourceSelection(
                    source_kind="base", base_run_id=run.run_id, appid="synthetic-orders"
                ),
                selection=DiagnosticSelection(
                    reason_codes=("low_hit",), enable_low_hit=True, enable_token_content=True
                ),
                submission_key="unified-rv1-" + label,
            ),
            options,
        )
        done = diagnostics.process_next()
        assert done.status == ("partial" if label == "latest_partial" else "ready"), done
        tasks.append((label, task.task_id))

    def forbidden(*args, **kwargs):
        raise AssertionError("Readonly acceptance performed analysis or encoding")

    result = {
        "synthetic": True,
        "production_authorization": False,
        "input_root": str(inputs),
        "state_root": str(service.state_root),
        "source_base_run_id": run.run_id,
        "appid": "synthetic-orders",
        "model": "GLM-5.2",
        "common_name": None,
        "tasks": [],
        "scope_request_count": 6,
        "csv_request_count": 7,
    }
    with (
        patch.object(CurrentTokenContentPlugin, "analyze_request", forbidden),
        patch.object(EncodingContext, "encode", forbidden),
        patch.object(DiagnosticService, "process_next", forbidden),
        patch.object(DiagnosticService, "submit", forbidden),
        TestClient(create_app(service, start_worker=False)) as client,
    ):
        cap = client.get("/diagnostics/recommendations/capabilities").json()
        result["service_instance_id"] = cap["service_instance_id"]
        client.headers["x-tokenscope-service-instance"] = cap["service_instance_id"]
        for label, task_id in tasks:
            base = f"/diagnostics/tasks/{task_id}"

            def get(route):
                response = client.get(route)
                assert response.status_code == 200, response.text
                return response.json()

            recs = get(base + "/recommendations")
            groups = get(base + "/difference-groups")
            examples = {}
            for kind, response in [("recommendations", recs), ("difference-groups", groups)]:
                for item in response["items"]:
                    route = base + "/" + kind + "/" + item["id"] + "/examples"
                    examples[route] = get(route)
                    assert len(examples[route]["items"]) <= 3
            if label != "latest_partial":
                assert any(
                    x["data"]["display_qualification"] == "low_hit_optimization"
                    for x in recs["items"]
                )
                assert {
                    x["data"]["recipe"]["primary_rule"]
                    for x in recs["items"]
                    if x["data"]["display_qualification"] == "token_evaluated"
                } >= {"T2", "T3", "T4"}
                assert any(x["data"]["rule_id"] == "L5" for x in groups["items"])
            result["tasks"].append(
                {
                    "label": label,
                    "task_id": task_id,
                    "report": diagnostics.report(task_id),
                    "recommendations": recs,
                    "difference_groups": groups,
                    "examples": examples,
                    "summary": get(base + "/recommendation-summary"),
                    "terminal": get(f"/diagnostics/discovery/tasks/{task_id}/terminal"),
                }
            )
        result["catalog"] = get("/diagnostics/discovery/catalog")
    defaults = result["catalog"]["defaults"]
    assert len(defaults) == 2 and {d["direction"] for d in defaults} == {"low_hit", "token_content"}
    assert {d["task_id"] for d in defaults} == {tasks[1][1]}
    assert len({d["binding_id"] for d in defaults}) == 1
    result["binding_id"] = defaults[0]["binding_id"]
    assert len({t["report"]["scope_id"] for t in result["tasks"]}) == 1
    assert all(t["report"]["scope"]["request_count"] == "6" for t in result["tasks"])
    (output / "actual-unified-rv1.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2)
    )
    files = [
        inputs / "unified-orders.csv",
        output / "synthetic-recipes.json",
        output / "synthetic-reference-map.json",
        output / "actual-unified-rv1.json",
    ]
    (output / "fixture-identity.json").write_text(
        json.dumps(
            {
                "identity": "unified-acceptance-rv1-20261101-1",
                "files": {
                    str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in files
                },
                "generator": {
                    str(Path(__file__).resolve().relative_to(root)): hashlib.sha256(
                        Path(__file__).read_bytes()
                    ).hexdigest()
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(
        json.dumps(
            {
                "result": "PASS",
                "state_root": str(service.state_root),
                "instance": result["service_instance_id"],
                "binding": result["binding_id"],
                "tasks": tasks,
            }
        )
    )


if __name__ == "__main__":
    main()

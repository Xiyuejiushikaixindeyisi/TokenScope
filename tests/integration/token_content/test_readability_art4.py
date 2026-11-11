"""Chinese, concrete recipes over real sealed output; all data and policies are synthetic."""

import json

from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient
from test_task_service import options

from tokenscope.analysis_common.contracts import (
    DiagnosticRequest,
    DiagnosticSelection,
    SourceSelection,
)
from tokenscope.analysis_common.plugins import PluginRegistry
from tokenscope.analysis_common.proposal_plugins import ProposalRegistry
from tokenscope.analysis_common.recommendation_runtime import RecommendationSettings
from tokenscope.analysis_common.recommendations import Basis, BasisAuthority, Recipe, RecipeBundle
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.api.app import create_app
from tokenscope.domain import RunSubmission
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.token_content.auto_proposals import TokenProposalAdapter
from tokenscope.token_content.current_plugin import CurrentTokenContentPlugin
from tokenscope.token_content.json_values import digest, dumps, loads


def test_chinese_recipes_actual_sealed_report(service, tmp_path):
    def text(value):
        return json.dumps(value, ensure_ascii=False)

    def identity(value):
        return digest(dumps(loads(text(value), max_depth=32), sort_keys=True))

    search = {"type": "function", "function": {"name": "query_orders"}}
    summarize = {
        "type": "function",
        "function": {
            "name": "summarize_orders",
            "parameters": {
                "type": "object",
                "properties": {"document": {"type": "string"}, "document_ref": {"type": "string"}},
                "required": [],
            },
        },
    }
    document = text(
        [
            {
                "order_id": "DEMO-001",
                "status": "已发货",
                "debug_log": "构造调试明细：逐项查询成功；" * 30,
            },
            {"order_id": "DEMO-002", "status": "待发货", "debug_log": "构造内部检索日志；" * 30},
        ]
    )
    reference = "fixture://orders/snapshot-001"
    # A real local fixture mapping, checked before using its reference. This is not a
    # claim that any production tool or remote service supports this URI/protocol.
    mapping = {reference: document}
    mapping_path = tmp_path / "synthetic-reference-map.json"
    mapping_path.write_text(text(mapping))
    assert json.loads(mapping_path.read_text())[reference] == document

    def call(name, ident, arguments):
        return {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": ident,
                    "type": "function",
                    "function": {"name": name, "arguments": text(arguments)},
                }
            ],
        }

    body = {
        "enable_thinking": False,
        "tools": [search, summarize],
        "messages": [
            {"role": "user", "content": "汇总这些构造订单的订单号和状态。"},
            call("query_orders", "old-query", {}),
            {"role": "tool", "tool_call_id": "old-query", "content": document},
            call("query_orders", "latest-query", {}),
            {"role": "tool", "tool_call_id": "latest-query", "content": document},
            call("summarize_orders", "summary", {"document": document}),
            {"role": "user", "content": document},
        ],
    }
    rows = [
        valid_row(
            appid=appid,
            hash_id=f"readable-{i}",
            request_input=text(body),
            model_handle_start_time=f"2026-10-27T00:00:0{i}Z",
        )
        for i, appid in enumerate(("synthetic-orders", "excluded-app", "synthetic-orders"))
    ]
    (service.inputs.root / "synthetic-orders.csv").write_bytes(csv_bytes(rows))
    base = service.submit(RunSubmission(file_ref="synthetic-orders.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    result_selector = {
        "version": "token-result-selector-1",
        "appid": "synthetic-orders",
        "tool_name": "query_orders",
        "tool_identity": identity(search),
        "representation": "structural_json",
        "embedded_pointer": "",
    }
    duplicate_selector = {
        "version": "token-duplicate-selector-1",
        "appid": "synthetic-orders",
        "payload_digest": digest(dumps(document)),
    }
    recipes = []

    def recipe(key, rule, title, summary, selector, generator, handler, basis_kind):
        source = text({"synthetic": True, "selector": selector, "generator": generator})
        basis = Basis(
            kind=basis_kind,
            ref=f"synthetic-policy:{key}",
            revision="1",
            digest=digest(source),
            scope_selector=text(selector),
            authority=BasisAuthority(
                source_kind="synthetic_fixture",
                source_ref=key,
                source_digest=digest(source),
                status="verified",
            ),
            limitations=("仅为构造策略验证；不代表生产业务授权、质量等价或真实业务收益。",),
        )
        recipes.append(
            Recipe(
                recipe_id=key,
                revision="1",
                primary_rule=rule,
                category_rules=(rule,),
                selector_json=text(selector),
                parameter_generator_json=text(generator),
                handler_id=handler,
                handler_version="1",
                basis=basis,
                title=title,
                change_summary=summary,
                conditions=("仅适用于 synthetic-orders 构造数据及这里固定的工具定义。",),
            )
        )

    recipe(
        "orders-fields",
        "T2",
        "订单查询结果只保留订单号与状态",
        "对 query_orders 返回数组的每条订单保留 order_id、status，"
        "移除 debug_log；订单条数和顺序保持不变。",
        result_selector,
        {
            "version": "token-result-generator-1",
            "kind": "project_fields",
            "fields": ["order_id", "status"],
            "field_level": "array_items",
            "omission_permitted": True,
        },
        "project_result_fields",
        "business_policy",
    )
    recipe(
        "orders-retention",
        "T4",
        "保留最近1份订单查询结果，替换较早结果",
        "在同一请求中保留 query_orders 最近1份完整结果；较早结果替换为 "
        '{"omitted":true,"reason":"较早订单快照已省略"}，保留工具消息与调用关系。',
        result_selector,
        {
            "version": "token-result-generator-1",
            "kind": "retain_last",
            "keep_last": 1,
            "replacement_json": text({"omitted": True, "reason": "较早订单快照已省略"}),
            "omission_permitted": True,
        },
        "apply_retention_replacements",
        "business_policy",
    )
    recipe(
        "orders-reference",
        "T3",
        "汇总工具的重复订单全文改为快照引用",
        "将 summarize_orders 参数 document 中与查询结果完全相同的订单全文，改为 document_ref=fixture://orders/snapshot-001；该引用已在本地构造映射中核对，生产消费协议未验证。",
        {
            **duplicate_selector,
            "target_kind": "argument_field",
            "tool_identity": identity(summarize),
            "argument_pointer": "/document",
        },
        {
            "version": "token-duplicate-generator-1",
            "kind": "reference",
            "omission_permitted": True,
            "reference_key": "document_ref",
            "reference_value": reference,
            "protocol_ref": "synthetic-orders-reference-v1",
        },
        "replace_payload_with_reference",
        "explicit_authorization",
    )
    recipe(
        "orders-copy",
        "T3",
        "删除重复粘贴订单全文的普通用户消息",
        "删除仅包含这份完整订单快照的重复 user 消息；"
        "保留最初的汇总指令、query_orders 工具结果和工具调用消息。",
        {**duplicate_selector, "target_kind": "ordinary_message", "message_role": "user"},
        {
            "version": "token-duplicate-generator-1",
            "kind": "delete_message",
            "omission_permitted": True,
        },
        "remove_authorized_duplicate_message",
        "explicit_authorization",
    )
    bundle = RecipeBundle(
        bundle_id="synthetic-orders-readable-art4", revision="1", recipes=tuple(recipes)
    )
    (tmp_path / "synthetic-recipes.json").write_text(bundle.model_dump_json(indent=2))
    registry = PluginRegistry()
    registry.register(CurrentTokenContentPlugin())
    adapters = ProposalRegistry()
    adapters.register(TokenProposalAdapter())
    diagnostics = DiagnosticService(
        SourceResolver(service), registry, RecommendationSettings(adapters, bundle)
    )
    selection = SourceSelection(
        source_kind="base", base_run_id=base.run_id, appid="synthetic-orders"
    )
    receipt = diagnostics.submit(
        DiagnosticRequest(
            source=selection,
            submission_key="synthetic-readable-art4",
            selection=DiagnosticSelection(
                reason_codes=("request_length",), enable_low_hit=False, enable_token_content=True
            ),
        ),
        options(),
    )
    completed = diagnostics.process_next()
    assert completed.status == "ready", completed
    with TestClient(create_app(service, start_worker=False, legacy_diagnostics=True)) as client:
        capabilities = client.get("/diagnostics/recommendations/capabilities").json()
        headers = {"x-tokenscope-service-instance": capabilities["service_instance_id"]}
        route = f"/diagnostics/tasks/{receipt.task_id}"
        response = client.get(route + "/recommendations", headers=headers)
        assert response.status_code == 200, response.text
        items = response.json()["items"]
        assert len(items) == 4
        examples = {}
        for item in items:
            value = item["data"]
            assert value["status"] == "available", value["reason_codes"]
            assert value["impact"]["modified_requests"] == value["impact"]["total_requests"] == "2"
            assert value["recipe"]["title"] in [r.title for r in recipes]
            assert value["recipe"]["change_summary"] in [r.change_summary for r in recipes]
            fetched = client.get(route + f"/recommendations/{item['id']}/examples", headers=headers)
            assert fetched.status_code == 200
            examples[item["id"]] = fetched.json()
        actual = {
            "synthetic": True,
            "production_authorization": False,
            "input_root": str(service.inputs.root.resolve()),
            "state_root": str(service.state_root.resolve()),
            "service_instance_id": capabilities["service_instance_id"],
            "task_id": receipt.task_id,
            "base_run_id": base.run_id,
            "model": "GLM-5.2",
            "recommendations": response.json(),
            "examples": examples,
            "reference_map_sha256": file_digest(mapping_path),
        }
        (tmp_path / "actual-readable-art4.json").write_text(
            json.dumps(actual, ensure_ascii=False, indent=2)
        )

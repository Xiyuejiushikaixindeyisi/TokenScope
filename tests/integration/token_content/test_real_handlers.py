"""Actual fixed assets, public mutation and replay; no mocked encoder/service."""

import json

import pytest
from conftest import csv_bytes, valid_row

from tokenscope.analysis_common.contracts import (
    EmbeddedLocation,
    Location,
    ModificationCandidate,
    ModificationPlan,
    SourceSelection,
)
from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.evaluation import evaluate_plan
from tokenscope.analysis_common.modifications import apply_mutations
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.domain import DEFAULT_SETTINGS, RunSubmission
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.token_content.json_values import PARSER_VERSION, digest, dumps, loads
from tokenscope.token_content.plugin import TokenContentPlugin


@pytest.mark.parametrize("model", list(DEFAULT_SETTINGS))
def test_all_handlers_real_encoding_and_token_replay(service, tmp_path, model):
    document = '[{"a":"内容<|im_start|>","b":"extra"},{"a":"second","b":"extra"}]'
    tool = {
        "type": "function",
        "function": {
            "name": "lookup",
            "description": "详细工具说明" * 50,
            "parameters": {
                "type": "object",
                "properties": {"document": {"type": "string"}, "document_ref": {"type": "string"}},
                "required": [],
            },
        },
    }
    body = {
        "tools": [tool],
        "enable_thinking": False,
        "messages": [
            {"role": "user", "content": "查阅资料"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "lookup",
                            "arguments": json.dumps({"document": document}),
                        },
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "call_1", "content": document},
            {"role": "user", "content": document},
        ],
    }
    raw = json.dumps(body, ensure_ascii=False)
    rows = [
        valid_row(
            appid=appid,
            hash_id=f"row{index}",
            request_input=raw,
            model_handle_start_time=f"2026-10-27T00:00:0{index}Z",
        )
        for index, appid in enumerate(("a", "b", "a"))
    ]
    (service.inputs.root / "token.csv").write_bytes(csv_bytes(rows))
    receipt = service.submit(RunSubmission(file_ref="token.csv", model_id=model))
    completed = service.processor.process_next()
    assert completed.status == "completed", completed
    source = SourceResolver(service).resolve_scope(
        SourceSelection(source_kind="base", base_run_id=receipt.run_id, appid="a")
    )
    requests = list(source.iter_requests())
    assert len(requests) == 2
    request = requests[-1]
    before_hash = file_digest(source.directory / "requests.sqlite3")
    context = EncodingContext(source)
    context.verify_baseline(request)
    cases = [
        (
            "replace_tool_description",
            "/tools/0/function/description",
            None,
            {"replacement_json": '"简述"'},
        ),
        (
            "project_result_fields",
            "/messages/2/content",
            "",
            {"fields": ["a"], "field_level": "array_items"},
        ),
        ("select_result_items", "/messages/2/content", "", {"start": 0, "end": 1}),
        ("select_result_lines", "/messages/2/content", None, {"start": 0, "end": 0}),
        (
            "apply_retention_replacements",
            "/messages/2/content",
            None,
            {"replacement_json": '"保留的业务摘要"'},
        ),
        (
            "replace_payload_with_reference",
            "/messages/1/tool_calls/0/function/arguments",
            "/document",
            {
                "reference_key": "document_ref",
                "reference_value": "existing://fixture/1",
                "protocol_ref": "fixture-v1",
                "tool_identity": digest(
                    dumps(loads(json.dumps(tool), max_depth=30), sort_keys=True)
                ),
            },
        ),
        ("remove_authorized_duplicate_message", "/messages/3", None, {"authorized": True}),
    ]
    plugin = TokenContentPlugin()
    prepared_cases = []
    for handler, pointer, embedded, parameters in cases:
        candidate = ModificationCandidate(
            candidate_id=handler,
            finding_refs=(),
            handler_id=handler,
            handler_version="1",
            action_class="policy_based",
            parameters_json="{}",
            locations=(
                Location(
                    request_key=request.request_key,
                    raw_sha256=request.raw_sha256,
                    source_pointer=pointer,
                    embedded=None
                    if embedded is None
                    else EmbeddedLocation(parser_version=PARSER_VERSION, pointer=embedded),
                ),
            ),
        )
        prepared = plugin.prepare_mutation(
            request, candidate, json.dumps(parameters), "fixture-business-policy"
        )
        assert prepared.status == "prepared", (handler, prepared)
        modified, manifest = apply_mutations(request, prepared.operations, DEFAULT_SETTINGS[model])
        assert manifest and modified != request.raw_body
        encoded = context.encode(request, modified)
        detailed = context.batch.explain(modified, encoded.prompt_digest)
        assert detailed["ids"] == encoded.prompt_ids
        assert len(detailed["ids"]) == encoded.prompt_tokens
        prepared_cases.append(prepared)
    plan = ModificationPlan(
        plan_id="token-plan",
        version="1",
        source_scope_id=source.scope.scope_id,
        transformation_digest="a" * 64,
        direction="token_content",
        action_class="policy_based",
        finding_refs=(),
        operations=prepared_cases[0].operations,
    )
    result = evaluate_plan(source, plan, tmp_path / "token-evaluation")
    assert result.status == "available", result
    assert result.stage == "direct_full" and result.gate_passed is None
    assert result.before.n == result.after.n == 2
    assert result.modified_after.n == 1 and result.after.p < result.before.p
    assert file_digest(source.directory / "requests.sqlite3") == before_hash

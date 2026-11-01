import json

import pytest
from test_extraction import view

from tokenscope.analysis_common.contracts import EmbeddedLocation, Location, ModificationCandidate
from tokenscope.analysis_common.modifications import apply_mutations
from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.errors import TokenScopeError
from tokenscope.token_content.json_values import PARSER_VERSION, digest, dumps, loads
from tokenscope.token_content.transformations import HANDLER_VERSION, prepare


def candidate(request, handler, pointers):
    locations = []
    for pointer in pointers:
        source, inner = pointer if isinstance(pointer, tuple) else (pointer, None)
        locations.append(
            Location(
                request_key=request.request_key,
                raw_sha256=request.raw_sha256,
                source_pointer=source,
                embedded=None
                if inner is None
                else EmbeddedLocation(parser_version=PARSER_VERSION, pointer=inner),
            )
        )
    return ModificationCandidate(
        candidate_id="candidate",
        finding_refs=(),
        handler_id=handler,
        handler_version=HANDLER_VERSION,
        action_class="policy_based",
        locations=tuple(locations),
        parameters_json="{}",
    )


def execute(request, handler, pointers, parameters):
    prepared = prepare(
        request, candidate(request, handler, pointers), json.dumps(parameters), "fixture-policy"
    )
    assert prepared.status == "prepared", prepared
    raw, manifest = apply_mutations(request, prepared.operations, DEFAULT_SETTINGS["GLM-5.2"])
    return json.loads(raw), manifest, prepared


def body(content="a\nb\nc\n"):
    return {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "f",
                    "description": "long description",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ],
        "messages": [
            {"role": "user", "content": "task"},
            {
                "role": "assistant",
                "tool_calls": [
                    {"id": "call", "type": "function", "function": {"name": "f", "arguments": "{}"}}
                ],
            },
            {"role": "tool", "tool_call_id": "call", "content": content},
        ],
    }


def test_description_changes_no_schema_or_name_and_source_immutable():
    original = body()
    request = view(original)
    modified, manifest, _ = execute(
        request,
        "replace_tool_description",
        ["/tools/0/function/description"],
        {"replacement_json": '"short"'},
    )
    assert modified["tools"][0]["function"]["description"] == "short"
    modified["tools"][0]["function"]["description"] = "long description"
    assert modified == original and json.loads(request.raw_body) == original
    assert manifest[0]["protocol_validated"]


def test_embedded_projection_preserves_numeric_lexemes_and_row_order():
    request = view(body('[{"a":1e20,"b":2},{"a":12345678901234567890,"b":3}]'))
    modified, manifest, prepared = execute(
        request,
        "project_result_fields",
        [("/messages/2/content", "")],
        {"fields": ["a"], "field_level": "array_items"},
    )
    assert modified["messages"][2]["content"] == '[{"a":1e20},{"a":12345678901234567890}]'
    assert len(prepared.operations) == 1 and manifest[0]["outer_string_guard"]
    assert modified["messages"][:2] == json.loads(request.raw_body)["messages"][:2]


def test_two_inner_targets_compile_once_and_conflicts_block():
    request = view(body('{"a":[1,2],"b":[3,4],"n":1e20}'))
    locations = [("/messages/2/content", "/a"), ("/messages/2/content", "/b")]
    modified, _, prepared = execute(
        request, "select_result_items", locations, {"start": 0, "end": 1}
    )
    assert len(prepared.operations) == 1
    assert modified["messages"][2]["content"] == '{"a":[1],"b":[3],"n":1e20}'
    bad = candidate(request, "select_result_items", [("/messages/2/content", ""), locations[0]])
    assert prepare(request, bad, '{"start":0,"end":1}', "policy").status == "blocked"


def test_lines_keep_newlines_and_retention_explicit_replacement():
    request = view(body("中\r\n😀\nend"))
    modified, _, _ = execute(
        request, "select_result_lines", ["/messages/2/content"], {"start": 1, "end": 2}
    )
    assert modified["messages"][2]["content"] == "😀\n"
    modified, _, _ = execute(
        request,
        "apply_retention_replacements",
        ["/messages/2/content"],
        {"replacement_json": '"retained externally"'},
    )
    assert modified["messages"][2]["tool_call_id"] == "call"


def test_reference_requires_real_protocol_and_supported_schema():
    original = body("document")
    definition = original["tools"][0]
    definition["function"]["parameters"] = {
        "type": "object",
        "properties": {"document": {"type": "string"}, "document_ref": {"type": "string"}},
        "required": [],
    }
    original["messages"][1]["tool_calls"][0]["function"]["arguments"] = (
        '{"document":"document","n":1e20}'
    )
    request = view(original)
    locations = [("/messages/1/tool_calls/0/function/arguments", "/document")]
    params = {
        "reference_key": "document_ref",
        "reference_value": "existing://object/1",
        "protocol_ref": "business-contract-v1",
        "tool_identity": digest(dumps(loads(json.dumps(definition), max_depth=30), sort_keys=True)),
    }
    modified, _, prepared = execute(request, "replace_payload_with_reference", locations, params)
    assert (
        modified["messages"][1]["tool_calls"][0]["function"]["arguments"]
        == '{"n":1e20,"document_ref":"existing://object/1"}'
    )
    assert len(json.loads(prepared.operations[0].source_operations_json)) == 2
    del params["protocol_ref"]
    assert (
        prepare(
            request,
            candidate(request, "replace_payload_with_reference", locations),
            json.dumps(params),
            "policy",
        ).status
        == "blocked"
    )


def test_authorized_duplicate_message_removal_and_protected_protocol():
    original = body("payload")
    original["messages"].extend(
        [{"role": "user", "content": "payload"}, {"role": "assistant", "content": "payload"}]
    )
    request = view(original)
    modified, _, _ = execute(
        request,
        "remove_authorized_duplicate_message",
        ["/messages/3", "/messages/4"],
        {"authorized": True},
    )
    assert modified["messages"] == original["messages"][:3]
    for path in ("/messages/1", "/messages/2", "/messages/0"):
        assert (
            prepare(
                request,
                candidate(request, "remove_authorized_duplicate_message", [path]),
                '{"authorized":true}',
                "policy",
            ).status
            == "blocked"
        )


@pytest.mark.parametrize(
    "parameters",
    [{}, {"start": True, "end": 1}, {"start": 1, "end": 100}, {"start": 0, "end": 1, "extra": 1}],
)
def test_invalid_parameters_never_yield_partial_operations(parameters):
    request = view(body())
    result = prepare(
        request,
        candidate(request, "select_result_lines", ["/messages/2/content"]),
        json.dumps(parameters),
        "policy",
    )
    assert result.status == "blocked" and not result.operations


def test_stale_guard_bad_target_and_unsafe_outer_number_block_whole_plan():
    request = view(body())
    good = candidate(
        request, "select_result_lines", ["/messages/2/content", "/messages/999/content"]
    )
    result = prepare(request, good, '{"start":0,"end":1}', "policy")
    assert result.status == "blocked" and not result.operations
    stale = request.model_copy(update={"raw_sha256": "a" * 64})
    assert prepare(stale, good, '{"start":0,"end":1}', "policy").status == "blocked"
    raw = request.raw_body[:-1] + ',"number":1e20}'
    unsafe = view(raw)
    assert prepare(
        unsafe,
        candidate(unsafe, "select_result_lines", ["/messages/2/content"]),
        '{"start":0,"end":1}',
        "policy",
    ).reason_codes == ("PUBLIC_NUMBER_LEXEME_UNSAFE",)


def test_public_rechecks_guards_and_rejects_conflicting_plans():
    request = view(body())
    target = candidate(request, "select_result_lines", ["/messages/2/content"])
    one = prepare(request, target, '{"start":0,"end":1}', "policy")
    two = prepare(request, target, '{"start":1,"end":2}', "policy")
    with pytest.raises(TokenScopeError, match="conflict"):
        apply_mutations(request, one.operations + two.operations, DEFAULT_SETTINGS["GLM-5.2"])
    operation = one.operations[0]
    bad = operation.model_copy(
        update={"target": operation.target.model_copy(update={"value_guard": "b" * 64})}
    )
    with pytest.raises(TokenScopeError, match="guard"):
        apply_mutations(request, (bad,), DEFAULT_SETTINGS["GLM-5.2"])
    assert json.loads(request.raw_body) == body()

import json

import pytest
from test_extraction import control, view

from tokenscope.analysis_common.modifications import apply_mutations
from tokenscope.analysis_common.plugins import EvidenceCapabilities, PluginSelection
from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.token_content.authorizations import authorize_candidate
from tokenscope.token_content.json_values import ContentError, digest, dumps, loads
from tokenscope.token_content.plugin import TokenContentPlugin


def evidence():
    tool = {
        "type": "function",
        "function": {
            "name": "f",
            "parameters": {
                "type": "object",
                "properties": {"document": {"type": "string"}, "document_ref": {"type": "string"}},
                "required": [],
            },
        },
    }
    request = view(
        {
            "tools": [tool],
            "messages": [
                {"role": "user", "content": "task"},
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "c",
                            "type": "function",
                            "function": {"name": "f", "arguments": '{"document":"payload"}'},
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": "c", "content": "payload"},
                {"role": "user", "content": "payload"},
            ],
        }
    )
    plugin = TokenContentPlugin()
    fragment = plugin.analyze_request(
        request,
        PluginSelection(rule_ids=("T3",), budget=control().budget),
        EvidenceCapabilities(),
        control(),
    )
    observed = fragment.observations[0]
    argument = next(
        u
        for u in fragment.units
        if "argument_payload" in u.facets
        and u.representation == "text"
        and u.unit_id in observed.unit_ids
    )
    message = next(
        u
        for u in fragment.units
        if "message_payload" in u.facets and u.unit_id in observed.unit_ids
    )
    reference = json.dumps(
        {
            "reference_key": "document_ref",
            "reference_value": "existing://fixture/1",
            "protocol_ref": "business-v1",
            "tool_identity": digest(dumps(loads(json.dumps(tool), max_depth=20), sort_keys=True)),
        }
    )
    return request, fragment, observed, argument, message, reference


@pytest.mark.parametrize(
    "handler", ["replace_payload_with_reference", "remove_authorized_duplicate_message"]
)
def test_authorized_candidate_compiles_and_applies_to_copy(handler):
    request, fragment, observed, argument, message, reference = evidence()
    selected = argument if handler == "replace_payload_with_reference" else message
    params = reference if handler == "replace_payload_with_reference" else '{"authorized":true}'
    original_fragment = fragment.model_dump_json()
    candidate = authorize_candidate(
        fragment,
        observed.observation_id,
        selected.unit_id,
        handler,
        "1",
        params,
        "business-approval",
    )
    assert candidate == authorize_candidate(
        fragment,
        observed.observation_id,
        selected.unit_id,
        handler,
        "1",
        params,
        "business-approval",
    )
    assert candidate.business_basis_ref == "business-approval" and not candidate.missing_parameters
    prepared = TokenContentPlugin().prepare_mutation(
        request, candidate, candidate.parameters_json, candidate.business_basis_ref
    )
    assert prepared.status == "prepared", prepared
    modified, _ = apply_mutations(request, prepared.operations, DEFAULT_SETTINGS["GLM-5.2"])
    parsed = json.loads(modified)
    if handler == "replace_payload_with_reference":
        assert json.loads(parsed["messages"][1]["tool_calls"][0]["function"]["arguments"]) == {
            "document_ref": "existing://fixture/1"
        }
    else:
        assert candidate.locations[0].source_pointer == "/messages/3"
        assert len(parsed["messages"]) == 3
    assert fragment.model_dump_json() == original_fragment
    assert len(json.loads(request.raw_body)["messages"]) == 4


@pytest.mark.parametrize(
    "change",
    [
        "foreign_observation",
        "foreign_unit",
        "tool_unit",
        "wrong_handler",
        "wrong_version",
        "empty_basis",
        "missing_authorization",
        "duplicate_parameters",
        "unknown_parameters",
    ],
)
def test_membership_authorization_and_version_rejected(change):
    _, fragment, observed, _, message, _ = evidence()
    args = dict(
        fragment=fragment,
        observation_id=observed.observation_id,
        selected_unit_id=message.unit_id,
        handler_id="remove_authorized_duplicate_message",
        handler_version="1",
        parameters_json='{"authorized":true}',
        business_basis_ref="approved",
    )
    if change == "foreign_observation":
        args["observation_id"] = "foreign"
    elif change == "foreign_unit":
        args["selected_unit_id"] = "foreign"
    elif change == "tool_unit":
        args["selected_unit_id"] = next(
            u.unit_id for u in fragment.units if "tool_result" in u.facets
        )
    elif change == "wrong_handler":
        args["handler_id"] = "select_result_lines"
    elif change == "wrong_version":
        args["handler_version"] = "2"
    elif change == "empty_basis":
        args["business_basis_ref"] = " "
    elif change == "missing_authorization":
        args["parameters_json"] = "{}"
    elif change == "duplicate_parameters":
        args["parameters_json"] = '{"authorized":true,"authorized":false}'
    else:
        args["parameters_json"] = '{"authorized":true,"source_pointer":"/messages/0"}'
    with pytest.raises(ValueError):
        authorize_candidate(**args)


def test_reference_requires_protocol_and_source_rechecked_by_prepare():
    request, fragment, observed, argument, _, reference = evidence()
    params = json.loads(reference)
    del params["protocol_ref"]
    with pytest.raises(ContentError, match="PROTOCOL"):
        authorize_candidate(
            fragment,
            observed.observation_id,
            argument.unit_id,
            "replace_payload_with_reference",
            "1",
            json.dumps(params),
            "business",
        )
    candidate = authorize_candidate(
        fragment,
        observed.observation_id,
        argument.unit_id,
        "replace_payload_with_reference",
        "1",
        reference,
        "business",
    )
    changed = request.model_copy(update={"raw_sha256": "b" * 64})
    assert (
        TokenContentPlugin()
        .prepare_mutation(changed, candidate, candidate.parameters_json, "business")
        .status
        == "blocked"
    )


def test_duplicate_or_non_t3_evidence_rejected():
    _, fragment, observed, _, message, _ = evidence()
    duplicate = fragment.model_copy(update={"units": fragment.units + (message,)})
    with pytest.raises(ContentError, match="AMBIGUOUS"):
        authorize_candidate(
            duplicate,
            observed.observation_id,
            message.unit_id,
            "remove_authorized_duplicate_message",
            "1",
            '{"authorized":true}',
            "business",
        )
    other = observed.model_copy(update={"rule_id": "T2"})
    wrong = fragment.model_copy(update={"observations": (other,)})
    with pytest.raises(ContentError, match="T3"):
        authorize_candidate(
            wrong,
            other.observation_id,
            message.unit_id,
            "remove_authorized_duplicate_message",
            "1",
            '{"authorized":true}',
            "business",
        )

"""Pure T3 authorization-to-candidate adapter over sealed fragment membership."""

import re

from tokenscope.analysis_common.contracts import AnalysisFragment, ModificationCandidate, stable_id
from tokenscope.token_content.json_values import PARSER_VERSION, ContentError, dumps, loads
from tokenscope.token_content.rules import RULE_VERSION
from tokenscope.token_content.transformations import COMPILE_MAX_BYTES, HANDLER_VERSION

AUTHORIZATION_VERSION = "token-authorization-1"


def authorize_candidate(
    fragment: AnalysisFragment,
    observation_id: str,
    selected_unit_id: str,
    handler_id: str,
    handler_version: str,
    parameters_json: str,
    business_basis_ref: str,
) -> ModificationCandidate:
    """No source reads, mutation or evaluation; prepare_mutation must recheck real source."""
    if handler_version != HANDLER_VERSION or handler_id not in (
        "replace_payload_with_reference",
        "remove_authorized_duplicate_message",
    ):
        raise ContentError("UNSUPPORTED_AUTHORIZATION_HANDLER")
    if not isinstance(business_basis_ref, str) or not business_basis_ref.strip():
        raise ContentError("BUSINESS_BASIS_REQUIRED")
    if len(parameters_json.encode("utf-8")) > COMPILE_MAX_BYTES:
        raise ContentError("COMPILE_BUDGET_EXHAUSTED")
    parameters = loads(parameters_json, max_depth=4)
    if not isinstance(parameters, dict):
        raise ContentError("INVALID_AUTHORIZATION_PARAMETERS")
    # Revalidate and reject duplicate identities, including malicious model_copy input.
    checked = AnalysisFragment.model_validate_json(fragment.model_dump_json())
    observations = {o.observation_id: o for o in checked.observations}
    units = {u.unit_id: u for u in checked.units}
    locations = {loc.location_id: loc for loc in checked.locations}
    if (
        len(observations) != len(checked.observations)
        or len(units) != len(checked.units)
        or len(locations) != len(checked.locations)
    ):
        raise ContentError("AMBIGUOUS_EVIDENCE_IDENTITY")
    observed = observations.get(observation_id)
    if (
        checked.plugin_id != "token_content"
        or observed is None
        or (
            observed.rule_id != "T3"
            or observed.rule_version != RULE_VERSION
            or observed.predicate != "exact_payload_repetition"
            or observed.condition != "met"
            or observed.method != "source-content-v1"
        )
    ):
        raise ContentError("T3_OBSERVATION_REQUIRED")
    if selected_unit_id not in observed.unit_ids or len(set(observed.unit_ids)) < 2:
        raise ContentError("UNIT_NOT_IN_OBSERVATION")
    group = [units[key] for key in observed.unit_ids]
    selected = units[selected_unit_id]
    if not any("tool_result" in unit.facets for unit in group) or any(
        unit.representation != selected.representation
        or unit.content_sha256 != selected.content_sha256
        for unit in group
    ):
        raise ContentError("EXACT_TOOL_PAYLOAD_EVIDENCE_REQUIRED")
    location = locations[selected.location_id]
    if location.text_range is not None:
        raise ContentError("COMPLETE_PAYLOAD_REQUIRED")
    if handler_id == "replace_payload_with_reference":
        expected = {"reference_key", "reference_value", "protocol_ref", "tool_identity"}
        if set(parameters) != expected or any(
            not isinstance(parameters[key], str) or not str(parameters[key]).strip()
            for key in expected
        ):
            raise ContentError("REFERENCE_PROTOCOL_AND_VALUE_REQUIRED")
        if re.fullmatch(r"[0-9a-f]{64}", str(parameters["tool_identity"])) is None:
            raise ContentError("TOOL_IDENTITY_REQUIRED")
        if (
            "argument_payload" not in selected.facets
            or location.embedded is None
            or (
                location.embedded.parser_version != PARSER_VERSION
                or re.fullmatch(r"/[^/]+", location.embedded.pointer) is None
                or re.fullmatch(
                    r"/messages/(0|[1-9][0-9]*)/tool_calls/(0|[1-9][0-9]*)/function/arguments",
                    location.source_pointer,
                )
                is None
            )
        ):
            raise ContentError("REFERENCE_TARGET_UNSUPPORTED")
    else:
        if set(parameters) != {"authorized"} or parameters["authorized"] is not True:
            raise ContentError("EXPLICIT_MESSAGE_REMOVAL_REQUIRED")
        match = re.fullmatch(r"(/messages/(0|[1-9][0-9]*))/content", location.source_pointer)
        if (
            match is None
            or location.embedded is not None
            or selected.representation != "text"
            or ("message_payload" not in selected.facets or selected.parent_unit_id is not None)
        ):
            raise ContentError("ORDINARY_COMPLETE_MESSAGE_REQUIRED")
        # Derive the containing message from the sealed location, never from client JSON Pointer.
        location = location.model_copy(update={"source_pointer": match[1]})
    canonical_parameters = dumps(parameters, sort_keys=True)
    return ModificationCandidate(
        candidate_id=stable_id(
            "authorized-candidate",
            {
                "authorization_version": AUTHORIZATION_VERSION,
                "observation_id": observation_id,
                "selected_unit_id": selected_unit_id,
                "location_id": location.location_id,
                "handler_id": handler_id,
                "handler_version": handler_version,
                "parameters": canonical_parameters,
                "business_basis_ref": business_basis_ref,
            },
        ),
        finding_refs=tuple(
            f.finding_id for f in checked.finding_candidates if observation_id in f.observation_ids
        ),
        handler_id=handler_id,
        handler_version=handler_version,
        action_class="policy_based",
        locations=(location,),
        parameters_json=canonical_parameters,
        business_basis_ref=business_basis_ref,
    )

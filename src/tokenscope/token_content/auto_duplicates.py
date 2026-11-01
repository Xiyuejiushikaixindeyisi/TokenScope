"""T3 automatic proposals require exact payload scope and explicit authorization."""

import re
from typing import Literal, Self

from pydantic import model_validator

from tokenscope.analysis_common.contracts import (
    AnalysisFragment,
    Contract,
    Digest,
    Name,
    Pointer,
    RequestView,
)
from tokenscope.analysis_common.plugins import EvidenceCapabilities, PluginSelection, RunControl
from tokenscope.analysis_common.recommendations import Proposal, ProposalTarget, Recipe, SupportRef
from tokenscope.token_content.authorizations import authorize_candidate
from tokenscope.token_content.auto_config import OmissionPermission, checked_raw
from tokenscope.token_content.extraction import extract
from tokenscope.token_content.json_values import ContentError, dumps, loads, resolve
from tokenscope.token_content.plugin import TokenContentPlugin


class DuplicateSelector(Contract):
    version: Literal["token-duplicate-selector-1"]
    appid: Name
    payload_digest: Digest
    target_kind: Literal["argument_field", "ordinary_message"]
    tool_identity: Digest | None = None
    argument_pointer: Pointer | None = None
    message_role: Literal["user", "assistant"] | None = None

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if self.target_kind == "argument_field":
            if not self.tool_identity or not self.argument_pointer or self.message_role:
                raise ValueError("Reference requires exact tool identity and argument field")
            if re.fullmatch(r"/[^/]+", self.argument_pointer) is None:
                raise ValueError("Only top-level argument fields supported")
        elif self.message_role is None or self.tool_identity or self.argument_pointer:
            raise ValueError("Ordinary deletion requires explicit message role")
        return self


class DuplicateGenerator(OmissionPermission):
    version: Literal["token-duplicate-generator-1"]
    kind: Literal["reference", "delete_message"]
    reference_key: Name | None = None
    reference_value: Name | None = None
    protocol_ref: Name | None = None

    @model_validator(mode="after")
    def coherent(self) -> Self:
        fields = (self.reference_key, self.reference_value, self.protocol_ref)
        if self.kind == "reference" and (not self.reference_key or not self.protocol_ref):
            raise ValueError("Reference protocol and destination key required")
        if self.kind == "delete_message" and any(x is not None for x in fields):
            raise ValueError("Reference parameters not valid for deletion")
        return self


def duplicate_config(recipe: Recipe) -> tuple[DuplicateSelector, DuplicateGenerator]:
    checked_raw(recipe.selector_json)
    checked_raw(recipe.parameter_generator_json)
    selector = DuplicateSelector.model_validate_json(recipe.selector_json)
    generator = DuplicateGenerator.model_validate_json(recipe.parameter_generator_json)
    expected = (
        ("argument_field", "replace_payload_with_reference")
        if generator.kind == "reference"
        else ("ordinary_message", "remove_authorized_duplicate_message")
    )
    if (
        (selector.target_kind, recipe.handler_id) != expected
        or recipe.primary_rule != "T3"
        or recipe.category_rules != ("T3",)
        or recipe.handler_version != "1"
    ):
        raise ValueError("T3 recipe/selector/handler mismatch")
    if recipe.basis is not None:
        basis = recipe.basis
        if basis.kind != "explicit_authorization" or basis.authority.status != "verified":
            raise ContentError("BASIS_INVALID")
        checked_raw(basis.scope_selector)
        if DuplicateSelector.model_validate_json(basis.scope_selector) != selector:
            raise ContentError("AUTHORIZATION_SCOPE_MISMATCH")
    return selector, generator


def duplicate_proposal(
    task_id: str,
    scope_id: str,
    request: RequestView,
    fragment_id: str,
    fragment: AnalysisFragment,
    recipe: Recipe,
    control: RunControl,
) -> Proposal | None:
    selector, generator = duplicate_config(recipe)
    if selector.appid != request.appid:
        return None
    inventory = extract(request, EvidenceCapabilities(), control)
    if inventory.local_errors:
        raise ContentError("EVIDENCE_LOCATION_UNAVAILABLE")
    entries = {e.unit.unit_id: e for e in inventory.entries}
    root = loads(request.raw_body, max_depth=control.budget.max_depth)
    supports: list[SupportRef] = []
    targets: list[ProposalTarget] = []
    selected: set[str] = set()
    for observed in fragment.observations:
        control.checkpoint()
        if (
            observed.rule_id != "T3"
            or observed.predicate != "exact_payload_repetition"
            or observed.condition != "met"
        ):
            continue
        for unit_id in observed.unit_ids:
            entry = entries.get(unit_id)
            if entry is None or entry.unit.content_sha256 != selector.payload_digest:
                continue
            loc = entry.location
            if selector.target_kind == "argument_field":
                if (
                    "argument_payload" not in entry.unit.facets
                    or loc.embedded is None
                    or loc.embedded.pointer != selector.argument_pointer
                ):
                    continue
                # Verify actual called function definition, not just a payload match.
                function_path = loc.source_pointer.rsplit("/", 1)[0]
                function = resolve(root, function_path)
                name = function.get("name") if isinstance(function, dict) else None
                identities = {
                    e.tool_identity
                    for e in inventory.entries
                    if "tool_definition" in e.unit.facets and e.tool_name == name
                }
                if identities != {selector.tool_identity}:
                    continue
            else:
                if (
                    "message_payload" not in entry.unit.facets
                    or entry.unit.parent_unit_id is not None
                    or loc.embedded is not None
                    or entry.unit.representation != "text"
                ):
                    continue
                message = resolve(root, loc.source_pointer.rsplit("/", 1)[0])
                if (
                    not isinstance(message, dict)
                    or message.get("role") != selector.message_role
                    or "tool_calls" in message
                    or "function_call" in message
                ):
                    continue
            if unit_id in selected:
                continue
            control.consume("max_candidates", 1)
            selected.add(unit_id)
            supports.append(
                SupportRef(
                    kind="token_observation",
                    task_id=task_id,
                    scope_id=scope_id,
                    request_key=request.request_key,
                    raw_sha256=request.raw_sha256,
                    fragment_id=fragment_id,
                    observation_ids=(observed.observation_id,),
                    unit_ids=(unit_id,),
                    location_ids=(loc.location_id,),
                )
            )
            params = (
                dumps({"authorized": True})
                if generator.kind == "delete_message"
                else dumps(
                    {
                        "reference_key": generator.reference_key,
                        "reference_value": generator.reference_value,
                        "protocol_ref": generator.protocol_ref,
                        "tool_identity": selector.tool_identity,
                    }
                )
            )
            if recipe.basis is not None and (
                generator.kind != "reference" or generator.reference_value
            ):
                authorize_candidate(
                    fragment,
                    observed.observation_id,
                    unit_id,
                    recipe.handler_id,
                    recipe.handler_version,
                    params,
                    recipe.basis.ref,
                )
                targets.append(ProposalTarget(location=loc, parameters_json=params))
    if not supports:
        return None
    reasons = (() if recipe.basis else ("RECIPE_BASIS_MISSING",)) + (
        ("REFERENCE_MAPPING_MISSING",)
        if generator.kind == "reference" and generator.reference_value is None
        else ()
    )
    return Proposal(
        recipe=recipe,
        support_refs=tuple(supports),
        request_targets=tuple(targets),
        applicability="advice_only" if reasons else "matched",
        reason_codes=reasons,
    )


def fresh_duplicate_fragment(request: RequestView, control: RunControl) -> AnalysisFragment:
    fragment = TokenContentPlugin().analyze_request(
        request,
        PluginSelection(rule_ids=("T3",), budget=control.budget),
        EvidenceCapabilities(),
        control,
    )
    if not fragment.coverage.complete:
        raise ContentError("EVIDENCE_LOCATION_UNAVAILABLE")
    return fragment

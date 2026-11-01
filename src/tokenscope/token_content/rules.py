"""Content facts and explicit policy checks for T1, T2 and T4."""

import json
from dataclasses import dataclass
from typing import Literal

from tokenscope.analysis_common.contracts import (
    Coverage,
    FindingCandidate,
    Observation,
    RuleResult,
    stable_id,
)
from tokenscope.analysis_common.plugins import RunControl
from tokenscope.token_content.extraction import Entry, Inventory
from tokenscope.token_content.policies import PolicySpec

RULE_VERSION = "1"
Condition = Literal["met", "not_met", "unknown"]


@dataclass(frozen=True)
class RuleOutput:
    observations: tuple[Observation, ...]
    findings: tuple[FindingCandidate, ...]
    result: RuleResult


def observation(
    rule: str,
    entries: list[Entry],
    predicate: str,
    condition: Condition,
    details: dict[str, object],
    policy: PolicySpec | None = None,
) -> Observation:
    return Observation(
        rule_id=rule,
        rule_version=RULE_VERSION,
        unit_ids=tuple(e.unit.unit_id for e in entries),
        predicate=predicate,
        method="source-content-v1",
        policy_digest=policy.digest if policy else None,
        condition=condition,
        details_json=json.dumps(details, ensure_ascii=False),
    )


def policy_match(entry: Entry, policy: PolicySpec) -> Condition:
    if policy.source_pointer is not None and entry.location.source_pointer != policy.source_pointer:
        return "not_met"
    embedded = entry.location.embedded
    if policy.embedded_pointer is None and embedded is not None:
        return "not_met"
    if policy.embedded_pointer is not None and (
        embedded is None or embedded.pointer != policy.embedded_pointer
    ):
        return "not_met"
    if policy.representation is not None and entry.unit.representation != policy.representation:
        return "not_met"
    if policy.tool_name is not None or policy.tool_identity is not None:
        if entry.identity_status != "resolved":
            return "unknown"
        if policy.tool_name is not None and entry.tool_name != policy.tool_name:
            return "not_met"
        if policy.tool_identity is not None and entry.tool_identity != policy.tool_identity:
            return "not_met"
    return "met"


def check_policy(entry: Entry, policy: PolicySpec) -> tuple[Condition, dict[str, object]]:
    if policy.basis == "model_input" and entry.unit.participation.status != "included":
        return "unknown", {"reason": "MODEL_PARTICIPATION_UNPROVEN"}
    if policy.kind == "limit":
        actual = entry.measures.get(policy.unit or "")
        if actual is None:
            return "unknown", {"reason": "INCOMPATIBLE_UNIT", "unit": policy.unit}
        assert policy.limit is not None
        exceeded = actual > policy.limit if policy.operator == "gt" else actual >= policy.limit
        return ("met" if exceeded else "not_met"), {
            "actual": actual,
            "limit": policy.limit,
            "unit": policy.unit,
            "operator": policy.operator,
        }
    if policy.field_level == "object":
        rows = [entry.value]
    elif isinstance(entry.value, list):
        rows = entry.value
    else:
        return "unknown", {"reason": "EXPECTED_ARRAY"}
    if not all(isinstance(row, dict) for row in rows):
        return "unknown", {"reason": "EXPECTED_OBJECT_ROWS"}
    extras = [
        {"row": index, "fields": sorted(set(row) - set(policy.allowed_fields or ()))}
        for index, row in enumerate(rows)
        if isinstance(row, dict) and set(row) - set(policy.allowed_fields or ())
    ]
    return ("met" if extras else "not_met"), {
        "extra_fields": extras,
        "field_level": policy.field_level,
    }


def run_inventory_rule(
    rule: Literal["T1", "T2", "T4"],
    inventory: Inventory,
    policies: tuple[PolicySpec, ...],
    control: RunControl,
    *,
    capture_truncation: str,
    message_count: int,
) -> RuleOutput:
    facet = "tool_definition" if rule == "T1" else "tool_result"
    eligible = [
        e
        for e in inventory.entries
        if facet in e.unit.facets or (rule == "T1" and "tool_definition_field" in e.unit.facets)
    ]
    containers = [e for e in eligible if e.unit.parent_unit_id is None]
    ordered = (
        sorted(containers, key=lambda e: (-e.unit.measured_value, e.location.source_pointer))
        if rule != "T4"
        else containers
    )
    obs: list[Observation] = []
    findings: list[FindingCandidate] = []
    policy_conditions: list[Condition] = []
    components: dict[str, list[dict[str, object]]] = {}
    if rule == "T1":
        for child in eligible:
            if child.unit.container_unit_id and child.location.source_pointer.rsplit("/", 1)[
                -1
            ] in ("description", "parameters"):
                components.setdefault(child.unit.container_unit_id, []).append(
                    {
                        "unit_id": child.unit.unit_id,
                        "measures": child.measures,
                        "source_pointer": child.location.source_pointer,
                    }
                )
    for entry in ordered:
        control.checkpoint()
        details: dict[str, object] = {
            "measures": entry.measures,
            "tool_name": entry.tool_name,
            "tool_identity": entry.tool_identity,
            "identity_status": entry.identity_status,
            "participation": entry.unit.participation.status,
            "capture_truncation": capture_truncation,
            "token_contribution": None,
            "aggregation": "containers_only_shared_across_rules",
        }
        if rule == "T4":
            details["later_message_count"] = max(0, message_count - (entry.message_index or 0) - 1)
        if rule == "T1":
            details["components"] = components.get(entry.unit.unit_id, [])
        obs.append(observation(rule, [entry], "content_inventory", "met", details))
    if rule == "T1":
        descriptions: dict[str, list[Entry]] = {}
        for entry in eligible:
            if (
                entry.location.source_pointer.endswith("/description")
                and isinstance(entry.value, str)
                and entry.value
            ):
                control.consume("max_comparison_bytes", entry.measures["utf8_bytes"])
                descriptions.setdefault(entry.value, []).append(entry)
        for group in descriptions.values():
            if len(group) > 1:
                obs.append(
                    observation(
                        rule,
                        group,
                        "identical_descriptions",
                        "met",
                        {"occurrences": len(group), "deletion_safe": None},
                    )
                )
    for policy in policies:
        if policy.rule_id != rule:
            continue
        if policy.kind == "retain_last":
            targets = (
                containers
                if policy.retention_unit == "result_container"
                else [
                    e
                    for e in eligible
                    if "text_part" in e.unit.facets and e.location.embedded is None
                ]
            )
        elif policy.source_pointer is not None or policy.embedded_pointer is not None:
            targets = eligible
        else:
            targets = containers
        matched = [(e, policy_match(e, policy)) for e in targets]
        applicable = [e for e, match in matched if match == "met"]
        ambiguous = [e for e, match in matched if match == "unknown"]
        for entry in ambiguous:
            obs.append(
                observation(
                    rule,
                    [entry],
                    policy.kind,
                    "unknown",
                    {"reason": "TOOL_IDENTITY_UNPROVEN"},
                    policy,
                )
            )
            policy_conditions.append("unknown")
        if policy.kind == "retain_last":
            # An ambiguous scope cannot safely determine the last K members.
            assert policy.keep_last is not None
            cutoff = max(0, len(applicable) - policy.keep_last)
            for index, entry in enumerate(applicable):
                condition: Condition = (
                    "unknown" if ambiguous else "met" if index < cutoff else "not_met"
                )
                if policy.basis == "model_input" and entry.unit.participation.status != "included":
                    condition = "unknown"
                details = {
                    "keep_last": policy.keep_last,
                    "retention_unit": policy.retention_unit,
                    "scope_count": len(applicable),
                    "index": index,
                    "reason": "AMBIGUOUS_RETENTION_SCOPE" if ambiguous else None,
                }
                obs.append(observation(rule, [entry], policy.kind, condition, details, policy))
                policy_conditions.append(condition)
        else:
            for entry in applicable:
                control.checkpoint()
                condition, details = check_policy(entry, policy)
                obs.append(observation(rule, [entry], policy.kind, condition, details, policy))
                policy_conditions.append(condition)
    for item in obs:
        if item.policy_digest is not None and item.condition == "met":
            control.consume("max_candidates", 1)
            findings.append(
                FindingCandidate(
                    finding_id=stable_id("finding", {"observation": item.observation_id}),
                    rule_ids=(rule,),
                    observation_ids=(item.observation_id,),
                    title="内容超过明确业务策略",
                    category="policy_exceeded",
                    advice="核对完整证据与业务策略，提供明确保留或替换参数后离线评估；不自动删除。",
                )
            )
    condition = (
        "met"
        if "met" in policy_conditions
        else "unknown"
        if "unknown" in policy_conditions or not policy_conditions
        else "not_met"
    )
    return RuleOutput(
        tuple(obs),
        tuple(findings),
        RuleResult(
            rule_id=rule,
            status="completed"
            if containers
            or (rule == "T1" and any(f in inventory.source_fields for f in ("tools", "functions")))
            else "not_applicable",
            condition=condition,
            coverage=Coverage(checked=len(containers), eligible=len(containers), complete=True),
            reason_codes=("NO_APPLICABLE_POLICY",) if not policy_conditions else (),
        ),
    )

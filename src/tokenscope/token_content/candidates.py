"""Pending content edits: never executed without explicit parameters and business basis."""

import re

from tokenscope.analysis_common.contracts import (
    FindingCandidate,
    ModificationCandidate,
    Observation,
    stable_id,
)
from tokenscope.analysis_common.plugins import RunControl
from tokenscope.token_content.extraction import Inventory
from tokenscope.token_content.transformations import HANDLER_VERSION


def pending_candidates(
    inventory: Inventory,
    observations: tuple[Observation, ...],
    rules: tuple[str, ...],
    control: RunControl,
) -> tuple[tuple[FindingCandidate, ...], tuple[ModificationCandidate, ...]]:
    findings: list[FindingCandidate] = []
    candidates: list[ModificationCandidate] = []
    facts = {
        o.unit_ids[0]: o
        for o in observations
        if o.predicate == "content_inventory" and o.rule_id in ("T1", "T2")
    }
    for entry in inventory.entries:
        handlers: list[tuple[str, tuple[str, ...]]] = []
        rule = "T1" if "tool_definition_field" in entry.unit.facets else "T2"
        if rule not in rules:
            continue
        if (
            rule == "T1"
            and re.fullmatch(
                r"/(tools/(0|[1-9][0-9]*)/function|functions/(0|[1-9][0-9]*))/description",
                entry.location.source_pointer,
            )
            and isinstance(entry.value, str)
        ):
            handlers.append(("replace_tool_description", ("replacement_json",)))
        elif rule == "T2" and "tool_result" in entry.unit.facets:
            if isinstance(entry.value, str) and entry.location.embedded is None:
                handlers.append(("select_result_lines", ("start", "end")))
            elif entry.location.embedded is not None and entry.location.embedded.pointer == "":
                if isinstance(entry.value, (dict, list)):
                    handlers.append(("project_result_fields", ("fields", "field_level")))
                if isinstance(entry.value, list):
                    handlers.append(("select_result_items", ("start", "end")))
        if not handlers:
            continue
        container = entry.unit.container_unit_id or entry.unit.unit_id
        fact = facts.get(container)
        if fact is None:
            continue
        finding = FindingCandidate(
            finding_id=stable_id("finding", {"unit": entry.unit.unit_id, "kind": "explicit_edit"}),
            rule_ids=(rule,),
            observation_ids=(fact.observation_id,),
            title="内容修改待业务确认",
            category="optimization_opportunity",
            advice="这里只提供可选修改入口，不判定内容无用；明确保留内容和业务依据后再评估输入变化。",
        )
        findings.append(finding)
        for handler, parameters in handlers:
            control.consume("max_candidates", 1)
            candidates.append(
                ModificationCandidate(
                    candidate_id=stable_id(
                        "candidate",
                        {
                            "location": entry.location.location_id,
                            "handler": handler,
                            "version": HANDLER_VERSION,
                        },
                    ),
                    finding_refs=(finding.finding_id,),
                    handler_id=handler,
                    handler_version=HANDLER_VERSION,
                    action_class="hypothetical_content_removal",
                    locations=(entry.location,),
                    parameters_json="{}",
                    missing_parameters=parameters + ("business_basis_ref",),
                )
            )
    # Retention edits require an actual policy finding; no policy means inventory only.
    by_unit = {entry.unit.unit_id: entry for entry in inventory.entries}
    for item in observations:
        if item.rule_id != "T4" or item.predicate != "retain_last" or item.condition != "met":
            continue
        entry = by_unit[item.unit_ids[0]]
        control.consume("max_candidates", 1)
        finding_ref = stable_id("finding", {"observation": item.observation_id})
        candidates.append(
            ModificationCandidate(
                candidate_id=stable_id(
                    "candidate",
                    {
                        "location": entry.location.location_id,
                        "handler": "apply_retention_replacements",
                        "policy": item.policy_digest,
                    },
                ),
                finding_refs=(finding_ref,),
                handler_id="apply_retention_replacements",
                handler_version=HANDLER_VERSION,
                action_class="policy_based",
                locations=(entry.location,),
                parameters_json="{}",
                missing_parameters=("replacement_json", "business_basis_ref"),
            )
        )
    return tuple(findings), tuple(candidates)

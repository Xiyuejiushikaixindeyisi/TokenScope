"""Bounded pair evidence for dynamic prompts and drifting tool definitions."""

import json
from pathlib import Path
from typing import Any

from tokenscope.analysis_common.contracts import ModificationPlan, RequestComparison, stable_id
from tokenscope.analysis_common.modifications import value_digest
from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.runtime import TaskControl
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.prefix_analysis.candidates import CandidateIndex
from tokenscope.prefix_analysis.dynamic import (
    comparable_slots,
    dynamic_recipes,
    field_differences,
    locate_recipe,
)
from tokenscope.prefix_analysis.history import history_differences, representation_differences
from tokenscope.prefix_analysis.service import PrefixFinding, PrefixReport, replacement
from tokenscope.prefix_analysis.structure import common_prefix, tool_map


def pair_dynamics(left: dict[str, Any], right: dict[str, Any]) -> list[tuple[str, str, str | None]]:
    output: list[tuple[str, str, str | None]] = []
    left_slots = comparable_slots(left)
    for key, (path, value) in comparable_slots(right).items():
        if key not in left_slots:
            continue
        for recipe in dynamic_recipes(left_slots[key][1], value):
            recipe["slot_key"] = key
            output.append((key[:2], path, json.dumps(recipe, ensure_ascii=False)))
    before, after = tool_map(left), tool_map(right)
    if left.get("tools") in (None, []):
        before = {}
    if right.get("tools") in (None, []):
        after = {}
    if before is not None and after is not None:
        for name in sorted(set(before) | set(after)):
            if (
                name not in before
                or name not in after
                or value_digest(before[name]) != value_digest(after[name])
            ):
                output.append(("L3", "/tools", None))
                break
    return output


def collect_dynamics(
    source: ResolvedSource,
    directory: Path,
    *,
    candidate_limit: int,
    include_history: bool = False,
    control: TaskControl | None = None,
) -> PrefixReport:
    directory.mkdir(parents=True, exist_ok=False)
    index = CandidateIndex(
        directory / "candidates.sqlite3", source.scope.source.base_run_id, candidate_limit
    )
    findings = []
    checked = comparisons = 0
    partial = False
    reasons: tuple[str, ...] = ()
    try:
        for current in source.iter_requests():
            if control:
                control.request(current)
            body = json.loads(current.raw_body)
            roles = [m.get("role") for m in body.get("messages", [])[:2]]
            fingerprint = stable_id(
                "shape", [current.encoder_identity, current.effective_options_json, roles]
            )
            candidates, truncated = index.lookup("structure", fingerprint)
            partial |= truncated
            current_ids = None
            for key in candidates:
                prior = source.read_request(key)
                if control:
                    control.request(prior)
                    control.comparison(prior, current)
                previous = json.loads(prior.raw_body)
                comparisons += 1
                observations = pair_dynamics(previous, body)
                if include_history:
                    observations.extend(
                        ("L4", path, None) for path in history_differences(previous, body)
                    )
                    observations.extend(
                        ("L5", path, None) for path in representation_differences(previous, body)
                    )
                if not observations:
                    continue
                if current_ids is None:
                    current_ids = source.read_ids(current)
                prior_ids = source.read_ids(prior)
                if prior_ids == current_ids:
                    continue
                for rule, path, recipe in observations:
                    differences = (
                        tuple(field_differences(previous.get("tools"), body.get("tools"), "/tools"))
                        if path == "/tools"
                        else (path,)
                    )
                    if recipe is not None:
                        logical_key = json.loads(recipe)["slot_key"]
                        left_path = comparable_slots(previous)[logical_key][0]
                        differences = tuple(dict.fromkeys((left_path, path)))
                    comparison = RequestComparison(
                        left=prior.request_key,
                        right=current.request_key,
                        left_raw_sha256=prior.raw_sha256,
                        right_raw_sha256=current.raw_sha256,
                        difference_pointers=differences,
                        lcp_tokens=common_prefix(prior_ids, current_ids),
                    )
                    if control:
                        control.finding()
                    findings.append(
                        PrefixFinding(
                            finding_id=stable_id("finding", [rule, "1", comparison, recipe]),
                            rule_id=rule,
                            comparison=comparison,
                            source_pointer=path,
                            recipe_json=recipe,
                            evidence_status="needs_association"
                            if rule == "L4"
                            else "source_change_and_input_difference",
                            advice="评估删除已定位动态片段后的命中率，由业务决定采用。"
                            if recipe
                            else "可比请求历史内容不同；无可靠关联，不认定同一会话改写。"
                            if rule == "L4"
                            else "工具结果JSON结构一致、表示不同；查看两条完整请求。"
                            if rule == "L5"
                            else "工具定义或集合发生变化；查看完整差异，不假定版本变更错误。",
                        )
                    )
            index.insert(current.request_key, {"structure": fingerprint})
            checked += 1
    except ExecutionStopped as exc:
        if exc.code == "ANALYSIS_INTERRUPTED":
            raise
        partial = True
        reasons = (exc.code,)
    finally:
        index.close()
    return PrefixReport(
        scope_id=source.scope.scope_id,
        findings=tuple(findings),
        checked_requests=checked,
        candidate_comparisons=comparisons,
        candidate_coverage_partial=partial,
        reason_codes=reasons,
    )


def compile_dynamic_plan(
    source: ResolvedSource, finding: PrefixFinding, control: TaskControl | None = None
) -> ModificationPlan | None:
    if finding.rule_id not in ("L1", "L3") or finding.recipe_json is None:
        raise ValueError("Expected dynamic recipe")
    recipe = json.loads(finding.recipe_json)
    operations = []
    plan_bytes = 0
    for request in source.iter_requests():
        if control:
            control.request(request)
        target = locate_recipe(json.loads(request.raw_body), recipe)
        if target is not None:
            path, old, new = target
            operations.append(replacement(request, path, old, new, "low_hit.dynamic_remove"))
            plan_bytes += len(operations[-1].model_dump_json().encode())
            if control:
                control.plan(plan_bytes)
    if not operations:
        return None
    plan = ModificationPlan(
        plan_id=stable_id("plan", [source.scope.scope_id, recipe]),
        version="1",
        source_scope_id=source.scope.scope_id,
        transformation_digest=value_digest(recipe),
        direction="low_hit",
        action_class="business_information_preserving"
        if recipe["pattern"] == "billing_header"
        else "hypothetical_content_removal",
        finding_refs=(finding.finding_id,),
        operations=tuple(operations),
    )
    if control:
        control.plan(len(plan.model_dump_json().encode()))
    return plan

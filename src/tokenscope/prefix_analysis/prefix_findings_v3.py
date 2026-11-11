"""Existing dynamic-slot and tool-order behavior on the bounded V3 execution path."""

import json
from dataclasses import dataclass
from typing import Any, Literal, cast

from tokenscope.analysis_common.contracts import (
    Contract,
    Location,
    ModificationPlan,
    RequestComparison,
    RequestKey,
    RequestView,
    stable_id,
)
from tokenscope.analysis_common.modifications import value_digest
from tokenscope.analysis_common.runtime_v3 import BudgetLedger
from tokenscope.analysis_common.sample_source import SampleResolvedSource
from tokenscope.prefix_analysis.dynamic import (
    apply_recipe,
    comparable_slots,
    dynamic_recipes,
    slots_in_text,
)
from tokenscope.prefix_analysis.service import replacement
from tokenscope.prefix_analysis.session_clock_v3 import clock_fields, locate_clock_blocks
from tokenscope.prefix_analysis.structure import sorted_tools, tool_set_fingerprint


class PrefixRecipe3(Contract):
    version: Literal["prefix-transform-3.2"] = "prefix-transform-3.2"
    kind: Literal["dynamic_remove", "sort_tools"]
    slot_key: str | None = None
    pattern: str | None = None
    slot_index: int | None = None
    shape: tuple[str, ...] = ()
    set_digest: str | None = None


class PrefixFinding3(Contract):
    finding_id: str
    rule_id: Literal["L1", "L2", "L3"]
    rule_version: Literal["prefix-3.2"] = "prefix-3.2"
    comparison: RequestComparison
    left_locations: tuple[Location, ...]
    right_locations: tuple[Location, ...]
    recipe: PrefixRecipe3
    evidence_status: Literal[
        "source_change_and_input_difference", "source_change_input_identical"
    ] = "source_change_and_input_difference"
    advice: str
    before_fragments: tuple[str, ...]
    after_fragments: tuple[str, ...]


def dynamic_fields(body: dict[str, Any]) -> dict[str, tuple[str, str]]:
    # Logical role/ordinal is independent of unrelated intervening history.
    result = {
        "L1:" + f.logical_key: (f.pointer, f.text)
        for f in clock_fields(body)
        if f.locations.reason_code in (None, "CLOCK_NOT_PRESENT")
    }
    result.update({k: v for k, v in comparable_slots(body).items() if k.startswith("L3:")})
    return result


def outside_clock(text: str, index: int | None) -> bool:
    located = locate_clock_blocks(text)
    if located.reason_code not in (None, "CLOCK_NOT_PRESENT"):
        return False
    slots = slots_in_text(text)
    if index is None or not 0 <= index < len(slots):
        return False
    start, end, _, _ = slots[index]
    return not any(start < block.end and end > block.start for block in located.blocks)


def recipe_target(body: dict[str, Any], recipe: PrefixRecipe3) -> tuple[str, Any, Any] | None:
    if recipe.kind == "sort_tools":
        if tool_set_fingerprint(body) != recipe.set_digest:
            return None
        ordered = sorted_tools(body)
        return ("/tools", body["tools"], ordered) if ordered is not None else None
    target = dynamic_fields(body).get(recipe.slot_key or "")
    if target is None:
        return None
    pointer, old = target
    if not outside_clock(old, recipe.slot_index):
        return None
    new = apply_recipe(
        old,
        {"shape": list(recipe.shape), "pattern": recipe.pattern, "slot_index": recipe.slot_index},
    )
    return (pointer, old, new) if new is not None else None


def pair_prefix(
    left: RequestView,
    right: RequestView,
    x: dict[str, Any],
    y: dict[str, Any],
    comparison: RequestComparison,
    *,
    input_changed: bool = True,
) -> list[PrefixFinding3]:
    output = []
    recipes: list[tuple[str, str, str, PrefixRecipe3]] = []
    before = dynamic_fields(x)
    for key, (pointer, value) in dynamic_fields(y).items():
        if key not in before:
            continue
        for raw_recipe in dynamic_recipes(before[key][1], value):
            if not (
                outside_clock(before[key][1], raw_recipe["slot_index"])
                and outside_clock(value, raw_recipe["slot_index"])
            ):
                continue
            raw_recipe["shape"] = tuple(raw_recipe["shape"])
            recipes.append(
                (key[:2], before[key][0], pointer, PrefixRecipe3(slot_key=key, **raw_recipe))
            )
    fingerprint = tool_set_fingerprint(y)
    if (
        fingerprint is not None
        and fingerprint == tool_set_fingerprint(x)
        and value_digest(x["tools"]) != value_digest(y["tools"])
    ):
        recipes.append(
            ("L2", "/tools", "/tools", PrefixRecipe3(kind="sort_tools", set_digest=fingerprint))
        )
    for rule, left_pointer, right_pointer, recipe in recipes:
        target = recipe_target(y, recipe)
        assert target is not None
        _, old, new = target
        lhs, rhs = left, right
        # The representative right side may already be sorted; show a side that changes.
        if old == new and recipe.kind == "sort_tools":
            target = recipe_target(x, recipe)
            assert target is not None
            _, old, new = target
            lhs, rhs = right, left
        pair = comparison.model_copy(
            update={
                "difference_pointers": tuple(dict.fromkeys((left_pointer, right_pointer))),
                "left": lhs.request_key,
                "right": rhs.request_key,
                "left_raw_sha256": lhs.raw_sha256,
                "right_raw_sha256": rhs.raw_sha256,
            }
        )
        note = (
            "固定同一完整工具集合的排列，保留全部定义；仅样本参考，需业务确认。"
            if rule == "L2"
            else "仅删除匹配的动态槽；可能改变业务信息或时间感知，需业务确认。"
        )
        output.append(
            PrefixFinding3(
                finding_id=stable_id("finding", ["prefix-3.2", pair, recipe]),
                rule_id=cast(Literal["L1", "L2", "L3"], rule),
                comparison=pair,
                evidence_status="source_change_and_input_difference"
                if input_changed
                else "source_change_input_identical",
                left_locations=(
                    Location(
                        request_key=lhs.request_key,
                        raw_sha256=lhs.raw_sha256,
                        source_pointer=left_pointer,
                    ),
                ),
                right_locations=(
                    Location(
                        request_key=rhs.request_key,
                        raw_sha256=rhs.raw_sha256,
                        source_pointer=right_pointer,
                    ),
                ),
                recipe=recipe,
                advice=note,
                before_fragments=(
                    old if isinstance(old, str) else json.dumps(old, ensure_ascii=False),
                ),
                after_fragments=(
                    new if isinstance(new, str) else json.dumps(new, ensure_ascii=False),
                ),
            )
        )
    return output


@dataclass(frozen=True)
class PrefixPlanResult3:
    plan: ModificationPlan | None
    matched: tuple[RequestKey, ...]
    modified: tuple[RequestKey, ...]
    reason_code: str | None = None


def compile_prefix_plan(
    source: SampleResolvedSource, finding: PrefixFinding3, control: BudgetLedger
) -> PrefixPlanResult3:
    operations, matched, modified = [], [], []
    for request in source.iter_requests():
        target = recipe_target(json.loads(request.raw_body), finding.recipe)
        if target is None:
            continue
        pointer, old, new = target
        matched.append(request.request_key)
        if old == new:
            continue
        op = replacement(request, pointer, old, new, "low_hit." + finding.recipe.kind)
        control.reserve("plan_bytes", len(op.model_dump_json().encode()))
        operations.append(op)
        modified.append(request.request_key)
    if not operations:
        return PrefixPlanResult3(
            None, tuple(matched), (), "NO_MODIFICATION" if matched else "NO_APPLICABLE_TARGETS"
        )
    control.reserve("plans")
    return PrefixPlanResult3(
        ModificationPlan(
            plan_id=stable_id("plan", [source.scope.scope_id, finding.recipe]),
            version="3.2",
            source_scope_id=source.scope.scope_id,
            transformation_digest=value_digest(finding.recipe.model_dump(mode="json")),
            direction="low_hit",
            action_class="stabilization"
            if finding.rule_id == "L2"
            else "hypothetical_content_removal",
            finding_refs=(finding.finding_id,),
            operations=tuple(operations),
        ),
        tuple(matched),
        tuple(modified),
    )

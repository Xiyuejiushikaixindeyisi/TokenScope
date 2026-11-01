"""Deterministic contiguous pilot selection followed by full-scope replay."""

import hashlib
import json
from dataclasses import dataclass, replace
from pathlib import Path

from tokenscope.analysis_common.contracts import (
    AnalysisScope,
    EvaluationResult,
    ModificationPlan,
    RequestKey,
    TimeWindow,
    canonical_metadata,
    stable_id,
)
from tokenscope.analysis_common.evaluation import evaluate_plan
from tokenscope.analysis_common.modifications import value_digest
from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.runtime import TaskControl
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.errors import TokenScopeError
from tokenscope.prefix_analysis.detection import compile_dynamic_plan
from tokenscope.prefix_analysis.dynamic import comparable_slots, slots_in_text, text_shape
from tokenscope.prefix_analysis.service import PrefixFinding, compile_l2_plan, replacement


@dataclass(frozen=True)
class Experiment:
    finding_ids: tuple[str, ...]
    status: str
    pilot: EvaluationResult | None = None
    full: EvaluationResult | None = None
    selection_method: str = "contiguous-anchor-1"
    pilot_scope: AnalysisScope | None = None
    reason_codes: tuple[str, ...] = ()


def pilot_scope(
    source: ResolvedSource, finding: PrefixFinding, limit: int
) -> ResolvedSource | None:
    if limit < 2:
        raise ValueError("Pilot limit must allow a pair")
    rows = [(row["source_record_index"], row["time_ns"]) for row in source._rows()]
    keys = [index for index, _ in rows]
    left = keys.index(finding.comparison.left.source_record_index)
    right = keys.index(finding.comparison.right.source_record_index)
    begin, end = min(left, right), max(left, right) + 1
    if end - begin > limit:
        return None
    end = min(len(rows), begin + limit)
    start_ns, end_ns = rows[begin][1], rows[end - 1][1] + 1
    if end_ns > 2**63 - 1:
        return None
    selected = [index for index, time in rows if start_ns <= time < end_ns]
    if len(selected) > limit or len(selected) >= len(rows):
        return None
    digest = hashlib.sha256()
    for index in selected:
        digest.update(
            canonical_metadata(
                RequestKey(base_run_id=source.scope.source.base_run_id, source_record_index=index)
            )
            + b"\n"
        )
    scope = source.scope.model_copy(
        update={
            "window": TimeWindow(start_ns=start_ns, end_ns=end_ns),
            "request_count": len(selected),
            "request_keys_digest": digest.hexdigest(),
            "baseline_origin": "selected_window_recomputed",
        }
    )
    return replace(source, scope=scope)


def compile_combination(
    source: ResolvedSource,
    findings: tuple[PrefixFinding, ...],
    control: TaskControl | None = None,
) -> ModificationPlan | None:
    if len(findings) == 1:
        return (
            compile_l2_plan(source, findings[0], control)
            if findings[0].rule_id == "L2"
            else compile_dynamic_plan(source, findings[0], control)
        )
    recipes = [json.loads(f.recipe_json) for f in findings if f.recipe_json is not None]
    if len(recipes) != len(findings) or any(r["kind"] != "dynamic_remove" for r in recipes):
        raise ValueError("Combination requires explicit compatible dynamic recipes")
    operations = []
    plan_bytes = 0
    for request in source.iter_requests():
        if control:
            control.request(request)
        slots = comparable_slots(json.loads(request.raw_body))
        by_path: dict[str, tuple[str, set[int]]] = {}
        for recipe in recipes:
            entry = slots.get(recipe["slot_key"])
            if entry is None:
                continue
            path, value = entry
            parsed = slots_in_text(value)
            if text_shape(value, parsed) != recipe["shape"]:
                continue
            selected = recipe["slot_index"]
            if not 0 <= selected < len(parsed) or parsed[selected][2] != recipe["pattern"]:
                continue
            if path not in by_path:
                by_path[path] = (value, set())
            by_path[path][1].add(selected)
        for path, (value, indices) in by_path.items():
            parsed = slots_in_text(value)
            changed = value
            for i in sorted(indices, reverse=True):
                left, right, _, _ = parsed[i]
                changed = changed[:left] + changed[right:]
            operations.append(
                replacement(request, path, value, changed, "low_hit.dynamic_combination")
            )
            plan_bytes += len(operations[-1].model_dump_json().encode())
            if control:
                control.plan(plan_bytes)
    if not operations:
        return None
    digest = value_digest(recipes)
    plan = ModificationPlan(
        plan_id=stable_id("plan", [source.scope.scope_id, digest]),
        version="1",
        source_scope_id=source.scope.scope_id,
        transformation_digest=digest,
        direction="low_hit",
        action_class="hypothetical_content_removal",
        finding_refs=tuple(f.finding_id for f in findings),
        operations=tuple(operations),
        combination_refs=tuple(f.finding_id for f in findings),
    )
    if control:
        control.plan(len(plan.model_dump_json().encode()))
    return plan


def run_experiment(
    source: ResolvedSource,
    findings: tuple[PrefixFinding, ...],
    directory: Path,
    *,
    pilot_limit: int,
    control: TaskControl | None = None,
) -> Experiment:
    directory.mkdir(parents=True, exist_ok=False)
    finding_ids = tuple(f.finding_id for f in findings)
    small = pilot_scope(source, findings[0], pilot_limit)
    if small is None:
        return Experiment(finding_ids, "sample_insufficient")
    # Every anchor in a combination must be inside the same small scope.
    try:
        for finding in findings:
            small.read_request(finding.comparison.left)
            small.read_request(finding.comparison.right)
    except TokenScopeError:
        return Experiment(finding_ids, "sample_insufficient")
    try:
        plan = compile_combination(small, findings, control)
    except ExecutionStopped as exc:
        if exc.code == "ANALYSIS_INTERRUPTED":
            raise
        return Experiment(
            finding_ids, "pilot_not_run", pilot_scope=small.scope, reason_codes=(exc.code,)
        )
    if plan is None:
        return Experiment(finding_ids, "no_applicable_targets", pilot_scope=small.scope)
    (directory / "pilot-plan.json").write_text(plan.model_dump_json(), encoding="utf-8")
    pilot = evaluate_plan(small, plan, directory / "pilot", stage="pilot", control=control)
    if pilot.status != "available":
        return Experiment(
            finding_ids,
            "pilot_blocked",
            pilot,
            pilot_scope=small.scope,
            reason_codes=pilot.reason_codes,
        )
    if pilot.gate_passed is not True:
        return Experiment(finding_ids, "pilot_below_gate", pilot, pilot_scope=small.scope)
    try:
        full_plan = compile_combination(source, findings, control)
    except ExecutionStopped as exc:
        if exc.code == "ANALYSIS_INTERRUPTED":
            raise
        return Experiment(
            finding_ids, "full_not_run", pilot, pilot_scope=small.scope, reason_codes=(exc.code,)
        )
    if full_plan is None or full_plan.transformation_digest != plan.transformation_digest:
        return Experiment(finding_ids, "full_plan_mismatch", pilot, pilot_scope=small.scope)
    (directory / "full-plan.json").write_text(full_plan.model_dump_json(), encoding="utf-8")
    full = evaluate_plan(source, full_plan, directory / "full", stage="full", control=control)
    status = (
        "full_blocked"
        if full.status != "available"
        else "full_qualified"
        if full.gate_passed
        else "full_below_gate"
    )
    return Experiment(
        finding_ids, status, pilot, full, pilot_scope=small.scope, reason_codes=full.reason_codes
    )

"""Build recipe-level cards from actual full evaluations; never multiply a pair's gain."""

import json
from collections.abc import Iterable

from tokenscope.analysis_common.contracts import EvaluationResult, ModificationPlan, stable_id
from tokenscope.analysis_common.recommendation_grouping import digest
from tokenscope.analysis_common.recommendations import (
    Basis,
    BasisAuthority,
    Impact,
    ObjectRef,
    Recipe,
    Recommendation,
    SupportRef,
)
from tokenscope.prefix_analysis.recommendation_groups import recipe_groups
from tokenscope.prefix_analysis.service import PrefixFinding


def recipe_copy(finding: PrefixFinding, plan: ModificationPlan | None) -> tuple[str, str]:
    """Business wording is tied to the actual independent Plan, never inferred by the UI."""
    titles = {
        "L1": "请求前部动态内容影响相同指令复用",
        "L2": "相同工具集合的排列变化影响前缀复用",
        "L3": "工具定义中的动态内容影响前缀复用",
    }
    title = titles[finding.rule_id]
    if plan is None or not plan.operations:
        return title, "尚无完整修改方案；请先核对下面的问题位置和原始请求对照。"
    paths = sorted({op.target.location.source_pointer for op in plan.operations})
    location = "、".join(paths[:3])
    if len(paths) > 3:
        location += f"等{len(paths)}个请求位置"
    handlers = {op.handler_id for op in plan.operations}
    primitives = {op.public_primitive for op in plan.operations}
    if primitives != {"replace_value"}:
        return title, f"修改位置：{location}。请按局部证据核对具体操作及适用条件。"
    if finding.rule_id == "L2" and handlers == {"low_hit.sort_tools"}:
        return title, (
            f"在同一完整工具集合内，将{location}按工具名称固定排序，保留全部工具及其定义；"
            "适用于工具集合一致、仅排列变化的请求，具体顺序见前后证据。"
        )
    if finding.rule_id in ("L1", "L3") and handlers == {"low_hit.dynamic_remove"}:
        pattern = json.loads(finding.recipe_json or "{}").get("pattern")
        content = {
            "timestamp": "时间戳片段",
            "path": "路径片段",
            "billing_header": "动态计费头片段",
        }.get(pattern, "动态片段")
        preserved = "其余工具定义" if finding.rule_id == "L3" else "其余消息和指令"
        return title, (
            f"在业务不依赖该动态内容的前提下，删除{location}中下面已定位的{content}，"
            f"保留{preserved}；具体位置和删除前后内容见局部证据，是否采用由业务决定。"
        )
    return title, f"修改位置：{location}。请按已保存方案和局部证据核对具体操作及适用条件。"


def project_low_hit(
    findings: Iterable[PrefixFinding],
    evaluations: Iterable[EvaluationResult],
    plans: Iterable[ModificationPlan],
    *,
    task_id: str,
    scope_id: str,
    total_requests: int,
    members_complete: bool = False,
) -> tuple[Recommendation, ...]:
    plan_map = {p.plan_id: p for p in plans}
    evaluations = tuple(evaluations)
    output = []
    for order, group in enumerate(recipe_groups(findings)):
        finding = group[0]
        ids = {f.finding_id for f in group}
        # An independently evaluated combination cannot stand for any component recipe.
        candidates = [
            e
            for e in evaluations
            if e.stage in ("full", "direct_full")
            and e.scope_id == scope_id
            and e.direction == "low_hit"
            and e.plan_id in plan_map
            and plan_map[e.plan_id].source_scope_id == scope_id
            and plan_map[e.plan_id].direction == "low_hit"
            and set(plan_map[e.plan_id].finding_refs) <= ids
            and bool(plan_map[e.plan_id].finding_refs)
        ]
        if len(candidates) > 1:
            candidates.sort(key=lambda e: e.evaluation_id)
        ev = candidates[0] if candidates else None
        available = ev is not None and ev.status == "available"
        source_digest = digest([finding.rule_id, finding.rule_version, finding.recipe_json])
        basis = Basis(
            kind="offline_hypothesis",
            ref="approved-low-hit-offline",
            revision="AR-C1",
            digest=source_digest,
            scope_selector="{}",
            authority=BasisAuthority(
                source_kind="approved_design",
                source_ref="AR-C1",
                source_digest=source_digest,
                status="verified",
            ),
            assumptions=("Offline copy only; business decides adoption",),
        )
        rule = finding.rule_id
        assert rule in ("L1", "L2", "L3")
        title, change_summary = recipe_copy(finding, plan_map[ev.plan_id] if ev else None)
        recipe = Recipe(
            recipe_id=source_digest,
            revision=finding.rule_version,
            primary_rule="L1" if rule == "L1" else "L2" if rule == "L2" else "L3",
            category_rules=("L1" if rule == "L1" else "L2" if rule == "L2" else "L3",),
            handler_id="prefix-recipe",
            handler_version="1",
            selector_json=finding.recipe_json or "{}",
            parameter_generator_json="{}",
            basis=basis,
            title=title,
            change_summary=change_summary,
        )
        supports = {}
        for f in group:
            c = f.comparison
            for key, sha in ((c.left, c.left_raw_sha256), (c.right, c.right_raw_sha256)):
                ref = SupportRef(
                    kind="prefix_finding",
                    task_id=task_id,
                    scope_id=scope_id,
                    request_key=key,
                    raw_sha256=sha,
                    finding_ids=(f.finding_id,),
                )
                supports[(key.base_run_id, key.source_record_index, f.finding_id)] = ref
        refs = tuple(supports[k] for k in sorted(supports))
        support_digest = digest([s.model_dump(exclude={"task_id"}) for s in refs])
        matched = None
        modified = None
        plan_ref = eval_ref = None
        if available:
            assert ev is not None
            if ev.modified_before is None or ev.modified_after is None:
                raise ValueError("Complete evaluation has no modified counts")
            plan = plan_map[ev.plan_id]
            matched = len({op.target.location.request_key for op in plan.operations})
            modified = ev.modified_before.n
            plan_ref = ObjectRef(task_id=task_id, id=plan.plan_id)
            eval_ref = ObjectRef(task_id=task_id, id=ev.evaluation_id)
        recipe_key = stable_id("recipe", recipe)
        output.append(
            Recommendation(
                recommendation_id=stable_id(
                    "rec", [scope_id, "low_hit", recipe_key, support_digest]
                ),
                task_id=task_id,
                scope_id=scope_id,
                direction="low_hit",
                generator_identity="prefix-recommendations-1",
                recipe_key=recipe_key,
                group_basis_digest=source_digest,
                recipe=recipe,
                support_refs=refs,
                matched_set_digest=digest(
                    sorted({s.request_key.source_record_index for s in refs})
                ),
                support_set_digest=support_digest,
                members_complete=members_complete,
                impact=Impact(
                    total_requests=total_requests,
                    matched_requests=matched,
                    matched_checked_requests=total_requests if available else 0,
                    match_complete=available,
                    modified_requests=modified,
                    evaluation_complete=available,
                ),
                proposal_status="matched",
                preparation_status="prepared" if available else "not_run",
                evaluation_status="available" if available else "not_run",
                status="available" if available else "not_run",
                prepared_plan_ref=plan_ref,
                execution_plan_ref=plan_ref,
                evaluation_ref=eval_ref,
                evaluation=ev if available else None,
                display_qualification="low_hit_optimization"
                if available and ev and ev.display_eligible
                else "not_eligible",
                reason_codes=(() if available else ("NO_COMPLETE_FULL_EVALUATION",))
                + (() if members_complete else ("CANDIDATE_COVERAGE_PARTIAL",)),
                display_order=order,
            )
        )
    return tuple(output)

"""Low-hit evidence collection; candidate lookup never substitutes for cache replay."""

import json
from pathlib import Path

from tokenscope.analysis_common.contracts import (
    Contract,
    Location,
    ModificationPlan,
    PreparedMutation,
    RequestComparison,
    RequestView,
    TargetLocation,
    stable_id,
)
from tokenscope.analysis_common.modifications import value_digest
from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.runtime import TaskControl
from tokenscope.analysis_common.runtime_control import retain_finding
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.analysis_common.wire import to_wire
from tokenscope.prefix_analysis.candidates import CandidateIndex
from tokenscope.prefix_analysis.structure import common_prefix, sorted_tools, tool_set_fingerprint


class PrefixFinding(Contract):
    finding_id: str
    rule_id: str
    rule_version: str = "1"
    comparison: RequestComparison
    source_pointer: str
    advice: str
    recipe_json: str | None = None
    evidence_status: str


class PrefixReport(Contract):
    scope_id: str
    findings: tuple[PrefixFinding, ...]
    checked_requests: int
    candidate_comparisons: int
    candidate_coverage_partial: bool
    reason_codes: tuple[str, ...] = ()


def replacement(
    request: RequestView, pointer: str, old: object, new: object, handler: str
) -> PreparedMutation:
    return PreparedMutation(
        operation_id=stable_id("op", [request.request_key, pointer, handler]),
        handler_id=handler,
        handler_version="1",
        target=TargetLocation(
            location=Location(
                request_key=request.request_key,
                raw_sha256=request.raw_sha256,
                source_pointer=pointer,
            ),
            original_type="array" if isinstance(old, list) else "string",
            value_guard=value_digest(old),
        ),
        public_primitive="replace_value",
        replacement_json=json.dumps(new, ensure_ascii=False),
    )


def collect_l2(
    source: ResolvedSource,
    directory: Path,
    *,
    candidate_limit: int,
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
            fingerprint = tool_set_fingerprint(body)
            channels = {}
            if fingerprint is not None:
                channel_key = stable_id(
                    "tools", [current.encoder_identity, current.effective_options_json, fingerprint]
                )
                channels["tools"] = channel_key
                candidates, truncated = index.lookup("tools", channel_key)
                partial |= truncated
                if truncated and "CANDIDATE_LOOKUP_TRUNCATED" not in reasons:
                    reasons += ("CANDIDATE_LOOKUP_TRUNCATED",)
                current_ids = None
                for key in candidates:
                    prior = source.read_request(key)
                    if control:
                        control.request(prior)
                        control.comparison(prior, current)
                    previous = json.loads(prior.raw_body)
                    comparisons += 1
                    if value_digest(body["tools"]) == value_digest(previous["tools"]):
                        continue
                    if tool_set_fingerprint(previous) != fingerprint:
                        continue
                    if current_ids is None:
                        current_ids = source.read_ids(current)
                    prior_ids = source.read_ids(prior)
                    if current_ids == prior_ids:
                        continue
                    comparison = RequestComparison(
                        left=prior.request_key,
                        right=current.request_key,
                        left_raw_sha256=prior.raw_sha256,
                        right_raw_sha256=current.raw_sha256,
                        difference_pointers=("/tools",),
                        lcp_tokens=common_prefix(prior_ids, current_ids),
                    )
                    finding = PrefixFinding(
                        finding_id=stable_id("finding", ["L2", "1", comparison]),
                        rule_id="L2",
                        comparison=comparison,
                        source_pointer="/tools",
                        advice="对同一完整工具集合固定排列，保留全部定义。",
                        recipe_json=json.dumps({"kind": "sort_tools", "set_digest": fingerprint}),
                        evidence_status="source_order_and_input_difference",
                    )
                    if retain_finding(
                        control,
                        "L2",
                        len(json.dumps(to_wire(finding), ensure_ascii=False).encode()),
                    ):
                        findings.append(finding)
            index.insert(current.request_key, channels)
            checked += 1
    except ExecutionStopped as exc:
        if exc.code == "ANALYSIS_INTERRUPTED":
            raise
        partial = True
        reasons = tuple(dict.fromkeys((*reasons, exc.code)))
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


def compile_l2_plan(
    source: ResolvedSource, finding: PrefixFinding, control: TaskControl | None = None
) -> ModificationPlan | None:
    if finding.rule_id != "L2" or finding.recipe_json is None:
        raise ValueError("Expected L2 recipe")
    recipe = json.loads(finding.recipe_json)
    operations = []
    plan_bytes = 0
    for request in source.iter_requests():
        if control:
            control.request(request)
        body = json.loads(request.raw_body)
        if tool_set_fingerprint(body) != recipe["set_digest"]:
            continue
        ordered = sorted_tools(body)
        if ordered is not None and value_digest(ordered) != value_digest(body["tools"]):
            operations.append(
                replacement(request, "/tools", body["tools"], ordered, "low_hit.sort_tools")
            )
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
        action_class="stabilization",
        finding_refs=(finding.finding_id,),
        operations=tuple(operations),
    )
    if control:
        control.plan(len(plan.model_dump_json().encode()))
    return plan

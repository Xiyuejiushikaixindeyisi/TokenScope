"""Automatic L1 clock evidence and frozen, guarded sample transformations."""

import json
from dataclasses import dataclass
from typing import Literal

from tokenscope.analysis_common.contracts import (
    Contract,
    Location,
    ModificationPlan,
    RequestComparison,
    RequestKey,
    RequestView,
    TextRange,
    stable_id,
)
from tokenscope.analysis_common.modifications import value_digest
from tokenscope.analysis_common.runtime_v3 import BudgetLedger, TaskStopped
from tokenscope.analysis_common.sample_source import SampleResolvedSource
from tokenscope.prefix_analysis.candidates_v3 import CandidateSchedule, feature_keys
from tokenscope.prefix_analysis.history import history_differences, representation_differences
from tokenscope.prefix_analysis.prefix_findings_v3 import PrefixFinding3, pair_prefix
from tokenscope.prefix_analysis.service import replacement
from tokenscope.prefix_analysis.session_clock_v3 import (
    ClockField,
    ClockRecipe3,
    clock_fields,
    clock_shape,
    date_ranges,
    normalize_clock,
)
from tokenscope.prefix_analysis.structure import common_prefix, tool_map

BUSINESS_NOTE = (
    "固定session_clock会改变模型的时间感知；仅在样本副本评估，需业务确认，不承诺业务无损。"
)


class ClockFinding3(Contract):
    finding_id: str
    rule_id: Literal["L1"] = "L1"
    rule_version: Literal["clock-3.1"] = "clock-3.1"
    comparison: RequestComparison
    left_locations: tuple[Location, ...]
    right_locations: tuple[Location, ...]
    left_date_ranges: tuple[tuple[TextRange, ...], ...]
    right_date_ranges: tuple[tuple[TextRange, ...], ...]
    recipe: ClockRecipe3
    evidence_status: Literal["clock_change_and_input_difference"] = (
        "clock_change_and_input_difference"
    )
    advice: str = BUSINESS_NOTE
    before_fragments: tuple[str, ...]
    after_fragments: tuple[str, ...]


class EvidenceRequest3(Contract):
    request_key: RequestKey
    raw_sha256: str
    raw_body: str


class CauseGroup3(Contract):
    group_id: str
    rule_id: str
    pointers: tuple[str, ...]
    members: tuple[RequestKey, ...]
    observed_pairs: int
    input_changed: bool
    lcp_tokens: int
    context_status: str = "pair_evidence_only"
    comparison: RequestComparison | None = None


class ClockDiscovery3(Contract):
    scope_id: str
    findings: tuple[ClockFinding3 | PrefixFinding3, ...]
    cause_groups: tuple[CauseGroup3, ...] = ()
    evidence_requests: tuple[EvidenceRequest3, ...] = ()
    channel_visits: dict[str, int] = {}
    candidate_limit: int = 16
    checked_requests: int
    comparisons: int
    unsupported_fields: int
    reason_codes: tuple[str, ...] = ()
    complete: bool = True
    synthetic_fixture: bool = False


def pair_clock(
    left: RequestView,
    right: RequestView,
    before: ClockField,
    after: ClockField,
    left_ids: list[int],
    right_ids: list[int],
) -> ClockFinding3 | None:
    if (
        before.logical_key != after.logical_key
        or before.locations.reason_code
        or after.locations.reason_code
    ):
        return None
    a, b = before.locations.blocks, after.locations.blocks
    shape = clock_shape(after.text, b)
    if clock_shape(before.text, a) != shape or left_ids == right_ids:
        return None
    changed = tuple(
        i
        for i, (x, y) in enumerate(zip(a, b, strict=True))
        if x.dates
        and y.dates
        and before.text[x.inner_start : x.inner_end] != after.text[y.inner_start : y.inner_end]
    )
    if not changed:
        return None
    recipe = ClockRecipe3(logical_field=after.logical_key, field_shape=shape, block_indices=changed)
    comparison = RequestComparison(
        left=left.request_key,
        right=right.request_key,
        left_raw_sha256=left.raw_sha256,
        right_raw_sha256=right.raw_sha256,
        difference_pointers=tuple(dict.fromkeys((before.pointer, after.pointer))),
        lcp_tokens=common_prefix(left_ids, right_ids),
    )

    def locations(request: RequestView, field: ClockField) -> tuple[Location, ...]:
        return tuple(
            Location(
                request_key=request.request_key,
                raw_sha256=request.raw_sha256,
                source_pointer=field.pointer,
                text_range=TextRange(
                    start=field.locations.blocks[i].inner_start,
                    end=field.locations.blocks[i].inner_end,
                ),
            )
            for i in changed
        )

    return ClockFinding3(
        finding_id=stable_id("finding", ["clock-3.1", comparison, recipe]),
        comparison=comparison,
        left_locations=locations(left, before),
        right_locations=locations(right, after),
        left_date_ranges=tuple(date_ranges(a[i]) for i in changed),
        right_date_ranges=tuple(date_ranges(b[i]) for i in changed),
        recipe=recipe,
        before_fragments=tuple(after.text[b[i].inner_start : b[i].inner_end] for i in changed),
        after_fragments=tuple("NORMALIZED" for i in changed),
    )


def collect_clock(source: SampleResolvedSource, control: BudgetLedger) -> ClockDiscovery3:
    if source.role != "discovery":
        raise ValueError("Discovery must not inspect the independent review window")
    requests: list[RequestView] = []
    bodies = []
    fields = []
    buckets: dict[tuple[str, str], list[int]] = {}
    ids: dict[int, list[int]] = {}
    findings: dict[str, ClockFinding3 | PrefixFinding3] = {}
    evidence: dict[RequestKey, EvidenceRequest3] = {}
    evidence_bytes = 0
    group_counts: dict[str, int] = {}
    groups: dict[str, CauseGroup3] = {}
    members: dict[str, set[RequestKey]] = {}
    visits: dict[str, int] = {}
    compared: set[tuple[int, int]] = set()
    checked = comparisons = unsupported = 0
    reasons: list[str] = []
    complete = True
    try:
        for current in source.iter_requests():
            control.checkpoint()
            body = json.loads(current.raw_body)
            current_fields = clock_fields(body)
            for field in current_fields:
                if (
                    field.locations.reason_code
                    and field.locations.reason_code != "CLOCK_NOT_PRESENT"
                ):
                    unsupported += 1
                    reasons.append(field.locations.reason_code)
            for bucket_key in feature_keys(current, body):
                buckets.setdefault(bucket_key, []).append(len(requests))
            requests.append(current)
            bodies.append(body)
            fields.append({f.logical_key: f for f in current_fields})
            checked += 1
        for channel, i, j in CandidateSchedule(buckets).pairs():
            control.checkpoint()
            visits[channel] = visits.get(channel, 0) + 1
            if (i, j) in compared:
                continue
            left, right = requests[i], requests[j]
            control.reserve_many(
                {
                    "comparisons": 1,
                    "comparison_bytes": len(left.raw_body.encode()) + len(right.raw_body.encode()),
                }
            )
            comparisons += 1
            compared.add((i, j))
            for index in (i, j):
                if index not in ids:
                    ids[index] = source.read_ids(requests[index])
            changed = ids[i] != ids[j]
            lcp = common_prefix(ids[i], ids[j])
            causes: list[tuple[str, tuple[str, ...], str]] = []
            for logical, after in fields[j].items():
                before = fields[i].get(logical)
                if before is None:
                    continue
                finding = pair_clock(left, right, before, after, ids[i], ids[j])
                if finding:
                    key = value_digest(finding.recipe.model_dump(mode="json"))
                    if key not in findings:
                        control.reserve("result_bytes", len(finding.model_dump_json().encode()))
                        findings[key] = finding
                    causes.append(("L1", finding.comparison.difference_pointers, key))
            x, y = bodies[i], bodies[j]
            comparison = RequestComparison(
                left=left.request_key,
                right=right.request_key,
                left_raw_sha256=left.raw_sha256,
                right_raw_sha256=right.raw_sha256,
                difference_pointers=(),
                lcp_tokens=lcp,
            )
            for prefix_finding in pair_prefix(left, right, x, y, comparison, input_changed=changed):
                signature = value_digest(prefix_finding.recipe.model_dump(mode="json"))
                if signature not in findings:
                    control.reserve("result_bytes", len(prefix_finding.model_dump_json().encode()))
                    findings[signature] = prefix_finding
                causes.append(
                    (
                        prefix_finding.rule_id,
                        prefix_finding.comparison.difference_pointers,
                        signature,
                    )
                )
            xm = {} if x.get("tools") in (None, []) else tool_map(x)
            ym = {} if y.get("tools") in (None, []) else tool_map(y)
            if xm is not None and ym is not None:
                if xm != ym:
                    causes.append(("L3", ("/tools",), value_digest([xm, ym])))
            for rule, difference_paths in (
                ("L4", history_differences(x, y)),
                ("L5", representation_differences(x, y)),
            ):
                if difference_paths:
                    # Only identical complete request-pair content shares evidence.
                    # This is not an inferred conversation or session identity.
                    causes.append(
                        (
                            rule,
                            tuple(difference_paths),
                            stable_id("pair-content", sorted((left.raw_sha256, right.raw_sha256))),
                        )
                    )
            for rule, pointers, signature in causes:
                key = stable_id(
                    "cause",
                    [rule, left.encoder_identity, left.effective_options_json, pointers, signature],
                )
                existing = groups.get(key)
                if existing is None:
                    if group_counts.get(rule, 0) >= 128:
                        complete = False
                        if "CAUSE_EVIDENCE_TRUNCATED" not in reasons:
                            reasons.append("CAUSE_EVIDENCE_TRUNCATED")
                        continue
                    # New reports resolve exact evidence from sealed sample members on demand.
                    # Do not duplicate long raw requests inside every report checkpoint.
                    additions = (
                        [r for r in (left, right) if r.request_key not in evidence]
                        if control.profile.version == "bounded-runtime-3.1"
                        else []
                    )
                    records = [
                        EvidenceRequest3(
                            request_key=r.request_key, raw_sha256=r.raw_sha256, raw_body=r.raw_body
                        )
                        for r in additions
                    ]
                    size = sum(len(r.model_dump_json().encode()) for r in records)
                    if evidence_bytes + size > control.profile.sample.max_metadata_bytes // 4:
                        complete = False
                        if "EVIDENCE_BYTE_LIMIT" not in reasons:
                            reasons.append("EVIDENCE_BYTE_LIMIT")
                        continue
                    control.reserve("result_bytes", size)
                    evidence_bytes += size
                    evidence.update({r.request_key: r for r in records})
                    group_counts[rule] = group_counts.get(rule, 0) + 1
                prior_members = members.get(key, set())
                added = {left.request_key, right.request_key} - prior_members
                # Admission precedes retention; a cap stops with explicit incomplete.
                control.reserve("result_bytes", 256 + sum(len(k.model_dump_json()) for k in added))
                prior_members.update(added)
                members[key] = prior_members
                groups[key] = CauseGroup3(
                    comparison=existing.comparison
                    if existing
                    else comparison.model_copy(update={"difference_pointers": pointers}),
                    group_id=key,
                    rule_id=rule,
                    pointers=pointers,
                    members=(),
                    observed_pairs=(existing.observed_pairs if existing else 0) + 1,
                    input_changed=changed or bool(existing and existing.input_changed),
                    lcp_tokens=lcp if existing is None else min(existing.lcp_tokens, lcp),
                )
    except TaskStopped as exc:
        reasons.append(exc.code)
        complete = False
    return ClockDiscovery3(
        scope_id=source.scope.scope_id,
        synthetic_fixture=bool(bodies)
        and all(b.get("tokenscope_synthetic_fixture") == "huawei-shape-1" for b in bodies),
        findings=tuple(findings.values()),
        evidence_requests=tuple(evidence.values()),
        cause_groups=tuple(
            group.model_copy(
                update={"members": tuple(sorted(members[key], key=lambda k: k.source_record_index))}
            )
            for key, group in groups.items()
        ),
        channel_visits=visits,
        checked_requests=checked,
        comparisons=comparisons,
        unsupported_fields=unsupported,
        reason_codes=tuple(dict.fromkeys(reasons)),
        complete=complete,
    )


@dataclass(frozen=True)
class ClockPlanResult:
    plan: ModificationPlan | None
    matched: tuple[RequestKey, ...]
    modified: tuple[RequestKey, ...]
    reason_code: str | None = None


def compile_clock_plan(
    source: SampleResolvedSource,
    finding: ClockFinding3,
    control: BudgetLedger,
    *,
    counterfactual_allowed: bool = True,
) -> ClockPlanResult:
    if not counterfactual_allowed:
        return ClockPlanResult(None, (), (), "BUSINESS_FORBIDDEN")
    operations, matched, modified = [], [], []
    for request in source.iter_requests():
        for field in clock_fields(json.loads(request.raw_body)):
            changed = normalize_clock(field, finding.recipe)
            if changed is None:
                continue
            matched.append(request.request_key)
            if changed == field.text:
                continue
            operation = replacement(
                request, field.pointer, field.text, changed, "low_hit.session_clock_normalize"
            )
            operation = operation.model_copy(
                update={
                    "handler_version": "3.1",
                    "manifest_fragment_json": json.dumps(
                        {"business_effect": "changes_time_awareness"}
                    ),
                    "source_operations_json": json.dumps(
                        {"block_indices": finding.recipe.block_indices, "constant": "NORMALIZED"}
                    ),
                }
            )
            control.reserve("plan_bytes", len(operation.model_dump_json().encode()))
            operations.append(operation)
            modified.append(request.request_key)
    if not operations:
        return ClockPlanResult(
            None, tuple(matched), (), "NO_MODIFICATION" if matched else "NO_APPLICABLE_TARGETS"
        )
    control.reserve("plans")
    plan = ModificationPlan(
        plan_id=stable_id("plan", [source.scope.scope_id, finding.recipe]),
        version="3.1",
        source_scope_id=source.scope.scope_id,
        transformation_digest=value_digest(finding.recipe.model_dump(mode="json")),
        direction="low_hit",
        action_class="hypothetical_time_normalization",
        finding_refs=(finding.finding_id,),
        operations=tuple(operations),
    )
    return ClockPlanResult(plan, tuple(matched), tuple(modified))

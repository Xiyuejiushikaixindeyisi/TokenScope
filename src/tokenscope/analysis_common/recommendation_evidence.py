"""Bounded local examples prepared before sealing; GET never reconstructs evidence."""

import hashlib
import json
from collections import defaultdict
from collections.abc import Iterable

from tokenscope.analysis_common.contracts import (
    AnalysisFragment,
    Location,
    ModificationPlan,
    RequestKey,
    TextRange,
    stable_id,
)
from tokenscope.analysis_common.evidence_locator import (
    at_pointer,
    decoded_offsets,
    locate,
    parse_spans,
)
from tokenscope.analysis_common.modifications import apply_mutations
from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.recommendations import (
    DifferenceGroup,
    LocalEvidence,
    Recommendation,
    RecommendationBudget,
    RecommendationExample,
)
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.analysis_common.wire import to_wire
from tokenscope.domain import ModelSettings
from tokenscope.prefix_analysis.dynamic import locate_recipe
from tokenscope.prefix_analysis.service import PrefixFinding


def check_examples(
    items: Iterable[RecommendationExample], budget: RecommendationBudget
) -> tuple[RecommendationExample, ...]:
    import json

    result = tuple(items)
    size = sum(len(json.dumps(to_wire(i), ensure_ascii=False).encode()) for i in result)
    if len(result) > budget.max_examples_per_group or size > budget.max_example_bytes_per_group:
        raise ExecutionStopped("RECOMMENDATION_EXAMPLE_BUDGET_EXHAUSTED")
    return result


def focus_pair(
    left_raw: str,
    left: Location,
    right_raw: str,
    right: Location,
    budget: RecommendationBudget,
) -> tuple[LocalEvidence, LocalEvidence]:
    """Exact pointer-bound string diff; no substring search or reserialization."""

    def text(raw: str, loc: Location) -> str:
        if hashlib.sha256(raw.encode()).hexdigest() != loc.raw_sha256:
            raise ValueError("EVIDENCE_SOURCE_DIGEST_MISMATCH")
        node = at_pointer(parse_spans(raw), loc.source_pointer)
        if loc.embedded:
            raw, _ = decoded_offsets(raw, node)
            node = at_pointer(parse_spans(raw), loc.embedded.pointer)
        value, _ = decoded_offsets(raw, node)
        return value

    try:
        a, b = text(left_raw, left), text(right_raw, right)
        start = 0
        while start < min(len(a), len(b)) and a[start] == b[start]:
            start += 1
        if a != b:
            tail = 0
            while tail < min(len(a), len(b)) - start and a[-tail - 1] == b[-tail - 1]:
                tail += 1
            left = left.model_copy(update={"text_range": TextRange(start=start, end=len(a) - tail)})
            right = right.model_copy(
                update={"text_range": TextRange(start=start, end=len(b) - tail)}
            )
    except (ValueError, KeyError, IndexError, RecursionError):
        # Non-string/ambiguous values retain explicit locator semantics, never fake a diff.
        pass
    return locate(left_raw, left, budget), locate(right_raw, right, budget)


def advice_examples(
    rec: Recommendation,
    fragments: dict[str, AnalysisFragment],
    source: ResolvedSource,
    budget: RecommendationBudget,
) -> tuple[RecommendationExample, ...]:
    """Read verified support locations only; no modification, after, or gain."""
    examples: list[RecommendationExample] = []
    seen: set[RequestKey] = set()
    for support in rec.support_refs[: budget.max_examples_per_group]:
        if len(examples) >= budget.max_examples_per_group:
            break
        if support.request_key in seen:
            continue
        fragment = fragments.get(support.fragment_id or "")
        if fragment is None or fragment.request_key != support.request_key:
            raise ValueError("ADVICE_SUPPORT_FRAGMENT_MISMATCH")
        request = source.read_request(support.request_key)
        if request.raw_sha256 != support.raw_sha256:
            raise ValueError("ADVICE_SUPPORT_DIGEST_MISMATCH")
        locations = [loc for loc in fragment.locations if loc.location_id in support.location_ids]
        if not locations:
            continue
        loc = locations[0]
        examples.append(
            RecommendationExample(
                example_id=stable_id(
                    "example", [rec.recommendation_id, support.request_key, "advice"]
                ),
                task_id=rec.task_id,
                scope_id=rec.scope_id,
                owner_id=rec.recommendation_id,
                before=locate(request.raw_body, loc, budget),
            )
        )
        seen.add(support.request_key)
    return check_examples(examples, budget)


def difference_examples(
    group: DifferenceGroup,
    findings: dict[str, PrefixFinding],
    source: ResolvedSource,
    budget: RecommendationBudget,
) -> tuple[RecommendationExample, ...]:
    examples: list[RecommendationExample] = []
    for ident in group.finding_ids[: budget.max_examples_per_group]:
        f = findings[ident]
        comparison = f.comparison
        left = source.read_request(comparison.left)
        right = source.read_request(comparison.right)
        a = Location(
            request_key=left.request_key,
            raw_sha256=left.raw_sha256,
            source_pointer=f.source_pointer,
        )
        b = Location(
            request_key=right.request_key,
            raw_sha256=right.raw_sha256,
            source_pointer=f.source_pointer,
        )
        before, comparison_evidence = focus_pair(left.raw_body, a, right.raw_body, b, budget)
        examples.append(
            RecommendationExample(
                example_id=stable_id("example", [group.group_id, ident]),
                task_id=group.task_id,
                scope_id=group.scope_id,
                owner_id=group.group_id,
                before=before,
                comparison=comparison_evidence,
            )
        )
    return check_examples(examples, budget)


def counterpart_pointer(
    finding: PrefixFinding,
    current_raw: str,
    other_raw: str,
    current_pointer: str,
) -> str | None:
    """Resolve each side by logical recipe identity, never by a shared array index."""
    if finding.rule_id in ("L1", "L3"):
        if finding.recipe_json is None:
            return None
        try:
            recipe = json.loads(finding.recipe_json)
            current = locate_recipe(json.loads(current_raw), recipe)
            other = locate_recipe(json.loads(other_raw), recipe)
        except (ValueError, KeyError, IndexError, TypeError):
            return None
        if current is None or other is None or current[0] != current_pointer:
            return None
        return other[0]
    return current_pointer if finding.source_pointer == current_pointer else None


def edit_examples(
    rec: Recommendation,
    plan: ModificationPlan,
    source: ResolvedSource,
    budget: RecommendationBudget,
    findings: dict[str, PrefixFinding] | None = None,
) -> tuple[RecommendationExample, ...]:
    if rec.status != "available":
        return ()
    operations = defaultdict(list)
    for op in plan.operations:
        operations[op.target.location.request_key].append(op)
    examples: list[RecommendationExample] = []
    settings = ModelSettings.model_validate_json(source.scope.source.settings_json)
    keys: list[RequestKey] = sorted(
        operations, key=lambda k: (k.base_run_id, k.source_record_index)
    )
    for key in keys[: budget.max_examples_per_group]:
        request = source.read_request(key)
        ops = tuple(operations[key])
        raw, _ = apply_mutations(request, ops, settings)
        # Show one concrete operation for this request; all operations remain in the audited Plan.
        op = ops[0]
        before = locate(request.raw_body, op.target.location, budget)
        after_location = op.target.location.model_copy(
            update={"raw_sha256": hashlib.sha256(raw.encode()).hexdigest()}
        )
        after = (
            LocalEvidence(
                source=after_location, raw_span=None, excerpt="", reason_codes=("VALUE_REMOVED",)
            )
            if op.public_primitive == "remove_value"
            else locate(raw, after_location, budget)
        )
        if op.public_primitive != "remove_value":
            before, after = focus_pair(
                request.raw_body, op.target.location, raw, after_location, budget
            )
        comparison_evidence = None
        unresolved_comparison = False
        for ident in sorted({f for ref in rec.support_refs for f in ref.finding_ids}):
            finding = (findings or {}).get(ident)
            if finding is None:
                continue
            pair = finding.comparison
            if key not in (pair.left, pair.right):
                continue
            other = source.read_request(pair.right if key == pair.left else pair.left)
            expected = pair.left_raw_sha256 if key == pair.left else pair.right_raw_sha256
            other_expected = pair.right_raw_sha256 if key == pair.left else pair.left_raw_sha256
            if request.raw_sha256 != expected or other.raw_sha256 != other_expected:
                raise ValueError("EVIDENCE_SOURCE_DIGEST_MISMATCH")
            other_pointer = counterpart_pointer(
                finding, request.raw_body, other.raw_body, op.target.location.source_pointer
            )
            if other_pointer is None:
                unresolved_comparison = True
                continue
            counterpart = op.target.location.model_copy(
                update={
                    "request_key": other.request_key,
                    "raw_sha256": other.raw_sha256,
                    "text_range": None,
                    "source_pointer": other_pointer,
                }
            )
            _, comparison_evidence = focus_pair(
                request.raw_body,
                op.target.location,
                other.raw_body,
                counterpart,
                budget,
            )
            break
        if comparison_evidence is None and unresolved_comparison:
            before = before.model_copy(
                update={"reason_codes": (*before.reason_codes, "COMPARISON_TARGET_UNRESOLVED")}
            )
        examples.append(
            RecommendationExample(
                example_id=stable_id("example", [rec.recommendation_id, key]),
                task_id=rec.task_id,
                scope_id=rec.scope_id,
                owner_id=rec.recommendation_id,
                before=before,
                after=after,
                comparison=comparison_evidence,
            )
        )
    return check_examples(examples, budget)

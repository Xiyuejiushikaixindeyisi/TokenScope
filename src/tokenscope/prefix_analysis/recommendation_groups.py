"""Low-hit recipe and exact-context difference groups, independent of UI sampling."""

import hashlib
import json
from collections import defaultdict
from collections.abc import Callable, Iterable

from tokenscope.analysis_common.contracts import RequestKey, canonical_metadata, stable_id
from tokenscope.analysis_common.evidence_locator import Node, at_pointer, parse_spans
from tokenscope.analysis_common.recommendations import DifferenceGroup
from tokenscope.prefix_analysis.service import PrefixFinding


def recipe_groups(findings: Iterable[PrefixFinding]) -> tuple[tuple[PrefixFinding, ...], ...]:
    groups: dict[bytes, dict[str, PrefixFinding]] = defaultdict(dict)
    for finding in findings:
        if finding.rule_id not in ("L1", "L2", "L3") or finding.recipe_json is None:
            continue
        key = canonical_metadata([finding.rule_id, finding.rule_version, finding.recipe_json])
        groups[key][finding.finding_id] = finding
    return tuple(tuple(group[k] for k in sorted(group)) for _, group in sorted(groups.items()))


def _context(raw: str, finding: PrefixFinding) -> bytes:
    root = parse_spans(raw)
    selected = {at_pointer(root, p).start for p in finding.comparison.difference_pointers}

    def structure(node: Node) -> object:
        text = raw[node.start : node.end]
        if node.start in selected:
            if finding.rule_id == "L4":
                return ["difference", node.kind]
            if node.kind != "string":
                raise ValueError("L5 requires encoded JSON result")
            embedded = json.loads(text)
            inner = parse_spans(embedded)

            # Numbers keep their exact lexical value, objects sort only structural metadata.
            def inner_shape(n: Node) -> object:
                if n.kind in ("object", "array"):
                    return [n.kind, [(k, inner_shape(v)) for k, v in sorted(n.children.items())]]
                t = embedded[n.start : n.end]
                return [n.kind, json.loads(t) if n.kind == "string" else t]

            return ["json_representation", inner_shape(inner)]
        if node.kind in ("object", "array"):
            return [node.kind, [(k, structure(v)) for k, v in sorted(node.children.items())]]
        return [node.kind, json.loads(text) if node.kind == "string" else text]

    return canonical_metadata(structure(root))


def difference_groups(
    findings: Iterable[PrefixFinding],
    *,
    task_id: str,
    scope_id: str,
    read_raw: Callable[[RequestKey], str],
    complete: bool,
) -> tuple[DifferenceGroup, ...]:
    groups: dict[bytes, list[PrefixFinding]] = defaultdict(list)
    unresolved: set[bytes] = set()
    for finding in findings:
        if finding.rule_id not in ("L4", "L5"):
            continue
        comparison = finding.comparison
        try:
            left, right = read_raw(comparison.left), read_raw(comparison.right)
            if (
                hashlib.sha256(left.encode()).hexdigest(),
                hashlib.sha256(right.encode()).hexdigest(),
            ) != (comparison.left_raw_sha256, comparison.right_raw_sha256):
                raise ValueError("Evidence digest mismatch")
            a, b = _context(left, finding), _context(right, finding)
            if a != b:
                raise ValueError("Context differs outside explicit difference")
            key = canonical_metadata(
                [finding.rule_id, finding.rule_version, comparison.difference_pointers, a.decode()]
            )
        except (ValueError, KeyError, IndexError, RecursionError):
            key = canonical_metadata(["unresolved", finding.finding_id])
            unresolved.add(key)
        groups[key].append(finding)
    result = []
    for order, (key, members) in enumerate(sorted(groups.items())):
        requests = {k for f in members for k in (f.comparison.left, f.comparison.right)}
        rule = members[0].rule_id
        assert rule in ("L4", "L5")
        result.append(
            DifferenceGroup(
                group_id=stable_id("diff", [scope_id, key.decode()]),
                task_id=task_id,
                scope_id=scope_id,
                rule_id="L4" if rule == "L4" else "L5",
                title="历史内容差异" if rule == "L4" else "工具结果表示差异",
                change_summary=(
                    "对照相关工具返回的原始片段，保留 JSON 空白与数值词法差异"
                    if rule == "L5"
                    else members[0].advice
                ),
                group_basis_digest=hashlib.sha256(key).hexdigest(),
                finding_ids=tuple(sorted({f.finding_id for f in members})),
                member_requests=tuple(
                    sorted(requests, key=lambda k: (k.base_run_id, k.source_record_index))
                ),
                members_complete=complete,
                reason_codes=("GROUPING_UNRESOLVED",) if key in unresolved else (),
                display_order=order,
            )
        )
    return tuple(result)

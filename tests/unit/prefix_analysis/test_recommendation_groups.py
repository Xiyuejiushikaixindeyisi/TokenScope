import hashlib
import json
from itertools import combinations

from tokenscope.analysis_common.contracts import RequestComparison, RequestKey
from tokenscope.prefix_analysis.recommendation_groups import difference_groups, recipe_groups
from tokenscope.prefix_analysis.service import PrefixFinding


def corpus():
    return {
        RequestKey(base_run_id="r", source_record_index=i): json.dumps(
            {"messages": [{"role": "user", "content": str(i)}]}
        )
        for i in range(6)
    }


def findings(raws, rule):
    return tuple(
        PrefixFinding(
            finding_id=f"{rule}-{i}",
            rule_id=rule,
            comparison=RequestComparison(
                left=a,
                right=b,
                left_raw_sha256=hashlib.sha256(raws[a].encode()).hexdigest(),
                right_raw_sha256=hashlib.sha256(raws[b].encode()).hexdigest(),
                difference_pointers=("/messages/0/content",),
            ),
            source_pointer="/messages/0/content",
            advice="advice",
            evidence_status="observed",
            recipe_json='{"pattern":"dynamic","shape":"same"}' if rule == "L1" else None,
        )
        for i, (a, b) in enumerate(combinations(raws, 2))
    )


def test_thirty_findings_are_two_groups_six_requests():
    raw = corpus()
    observations = (*findings(raw, "L1"), *findings(raw, "L4"))
    assert len(observations) == 30
    groups = recipe_groups(observations)
    assert len(groups) == 1 and len(groups[0]) == 15
    diff = difference_groups(
        observations, task_id="t", scope_id="s", read_raw=raw.__getitem__, complete=True
    )
    assert len(diff) == 1 and len(diff[0].member_requests) == 6
    assert len(diff[0].finding_ids) == 15
    assert not diff[0].example_refs


def test_distinct_recipe_and_unknown_context_never_silently_merge():
    raw = corpus()
    original = findings(raw, "L1")
    changed = original[0].model_copy(
        update={"finding_id": "other", "recipe_json": '{"shape":"other"}'}
    )
    assert len(recipe_groups((*original, changed))) == 2
    diff = findings(raw, "L4")
    key = next(iter(raw))
    raw[key] = raw[key].replace('"user"', '"assistant"')
    groups = difference_groups(
        diff, task_id="t", scope_id="s", read_raw=raw.__getitem__, complete=False
    )
    assert len(groups) > 1
    assert any(g.reason_codes == ("GROUPING_UNRESOLVED",) for g in groups)
    assert sum(len(g.finding_ids) for g in groups) == 15
    assert all(not g.members_complete for g in groups)

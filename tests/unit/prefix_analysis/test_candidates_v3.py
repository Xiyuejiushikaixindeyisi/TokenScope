import hashlib
import json
from types import SimpleNamespace

from tokenscope.analysis_common.contracts import BaselineMetrics, RequestKey, RequestView
from tokenscope.analysis_common.execution_v3 import automatic_profile
from tokenscope.analysis_common.runtime_v3 import BudgetLedger
from tokenscope.prefix_analysis.candidates import CandidateIndex
from tokenscope.prefix_analysis.candidates_v3 import CandidateSchedule, time_order
from tokenscope.prefix_analysis.clock_discovery_v3 import collect_clock


def request(index, body):
    raw = json.dumps(body)
    return RequestView(
        request_key=RequestKey(base_run_id="run-test", source_record_index=index),
        scope_id="scope-test",
        appid="test",
        time_ns=index,
        hash_id=str(index),
        raw_body=raw,
        raw_sha256=hashlib.sha256(raw.encode()).hexdigest(),
        raw_body_complete=True,
        baseline_metrics=BaselineMetrics(j=1, p=2),
        encoder_identity="encoder-test",
        asset_identity="asset-test",
        effective_options_json="{}",
    )


def fixture():
    def tool(name, description="stable"):
        return {"type": "function", "function": {"name": name, "description": description}}

    rows = [{"messages": [{"role": "user", "content": "ordinary"}]} for _ in range(40)]
    rows += [
        {
            "messages": [
                {"role": "system", "content": f"<session_clock>2026/11/{day}</session_clock>"}
            ]
            + ([{"role": "user", "content": "history"}] if day == 11 else [])
        }
        for day in (10, 11)
    ]
    rows += [
        {"tools": [tool("a"), tool("b")]},
        {"tools": [tool("b"), tool("a")]},
        {"tools": [tool("b", "changed"), tool("a")]},
    ]
    rows += [
        {"messages": [{"role": "tool", "content": text}]} for text in ('{"a":1}', '{ "a": 1 }')
    ]
    return [request(i, row) for i, row in enumerate(rows)]


class Source:
    role = "discovery"
    scope = SimpleNamespace(scope_id="scope-test")

    def __init__(self):
        self.requests = fixture()
        self.reads = []

    def iter_requests(self):
        return iter(self.requests)

    def read_ids(self, request):
        self.reads.append(request.request_key)
        return list(request.raw_body.encode())


def test_same_budget_oracle_determinism_physical_accounting_and_old_baseline(tmp_path):
    p = automatic_profile(available_bytes=4 * 1024**3, source_bytes=1000000, cpu_budget=1)
    p = p.model_copy(update={"budgets": {**p.budgets, "comparisons": 12}})
    source = Source()
    ledger = BudgetLedger(p, lambda: False)
    result = collect_clock(source, ledger)
    assert {"L1", "L2", "L3"} <= {g.rule_id for g in result.cause_groups}
    assert result.comparisons == ledger.consumed["comparisons"] == 12
    assert not result.complete and result.reason_codes[-1] == "BUDGET_EXHAUSTED:comparisons"
    assert len(source.reads) == len(set(source.reads))
    assert result == collect_clock(Source(), BudgetLedger(p, lambda: False))
    for group in result.cause_groups:
        assert len(group.members) == len(set(group.members))
        assert group.context_status == "pair_evidence_only"
    # Actual legacy newest-first index, same total 12. Early broad repeated
    # traffic exhausts this budget before any of the three rare oracle causes.
    old = CandidateIndex(tmp_path / "old.sqlite3", "run-test", 16)
    used = 0
    last = 0
    for row in source.requests:
        pairs, _ = old.lookup("broad", "same")
        for _ in pairs:
            used += 1
            last = row.request_key.source_record_index
            if used == 12:
                break
        if used == 12:
            break
        old.insert(row.request_key, {"broad": "same"})
    old.close()
    assert last < 40


def test_schedule_bounds_no_pair_matrix_and_all_channels():
    n, k = 1000, 3
    buckets = {(rule, "same"): list(range(n)) for rule in ("L1", "L2", "L3", "L4", "L5")}
    pairs = list(CandidateSchedule(buckets, k).pairs())
    assert len(pairs) <= 5 * n * k
    selected = {}
    for _, left, right in pairs:
        assert left < right
        selected.setdefault(right, set()).add(left)
    assert max(map(len, selected.values())) <= k
    assert list(time_order(7)) == [0, 6, 3, 1, 4, 2, 5]
    assert {channel for channel, _, _ in pairs} == {"L1", "L2", "L3", "L4", "L5"}


def test_complete_fallback_evidence_and_independent_review_denied():
    p = automatic_profile(available_bytes=4 * 1024**3, source_bytes=1000000, cpu_budget=1)
    result = collect_clock(Source(), BudgetLedger(p, lambda: False))
    assert result.complete
    assert {"L4", "L5"} <= {g.rule_id for g in result.cause_groups}
    source = Source()
    source.role = "review"
    import pytest

    with pytest.raises(ValueError, match="independent review"):
        collect_clock(source, BudgetLedger(p, lambda: False))


def test_representative_evidence_is_bounded_without_merging_unrelated_pairs():
    source = Source()
    source.requests = [
        request(i, {"messages": [{"role": "user", "content": f"different {i}"}]})
        for i in range(160)
    ]
    result = collect_clock(
        source,
        BudgetLedger(
            automatic_profile(available_bytes=4 * 1024**3, source_bytes=1000000, cpu_budget=1),
            lambda: False,
        ),
    )
    groups = [g for g in result.cause_groups if g.rule_id == "L4"]
    assert len(groups) == 128
    assert not result.complete and "CAUSE_EVIDENCE_TRUNCATED" in result.reason_codes
    assert result.evidence_requests == ()
    evidence = {r.request_key: r for r in source.requests}
    assert len(evidence) <= len(source.requests)
    for group in groups:
        assert group.comparison is not None
        assert len(group.members) == 2
        for key in (group.comparison.left, group.comparison.right):
            assert (
                hashlib.sha256(evidence[key].raw_body.encode()).hexdigest()
                == evidence[key].raw_sha256
            )


def test_dynamic_l1_uses_logical_role_not_history_position_and_rejects_fixed_or_unrelated():
    from tokenscope.analysis_common.contracts import RequestComparison
    from tokenscope.prefix_analysis.prefix_findings_v3 import pair_prefix

    left = {"messages": [{"role": "system", "content": "Root /workspace/a"}]}
    right = {
        "messages": [
            {"role": "user", "content": "unrelated"},
            {"role": "system", "content": "Root /workspace/longer"},
        ]
    }

    def pairs(a, b):
        x, y = request(0, a), request(1, b)
        return pair_prefix(
            x,
            y,
            a,
            b,
            RequestComparison(
                left=x.request_key,
                right=y.request_key,
                left_raw_sha256=x.raw_sha256,
                right_raw_sha256=y.raw_sha256,
                difference_pointers=(),
                lcp_tokens=0,
            ),
        )

    found = pairs(left, right)
    assert len(found) == 1 and found[0].rule_id == "L1"
    assert found[0].left_locations[0].source_pointer == "/messages/0/content"
    assert found[0].right_locations[0].source_pointer == "/messages/1/content"
    assert not pairs(left, left)
    right["messages"][1]["role"] = "developer"
    assert not pairs(left, right)
    right["messages"][1] = {"role": "system", "content": "Other /workspace/longer"}
    assert not pairs(left, right)


def test_dynamic_slot_outside_clock_preserved_but_clock_interior_not_removed():
    from tokenscope.prefix_analysis.dynamic import slots_in_text
    from tokenscope.prefix_analysis.prefix_findings_v3 import outside_clock

    text = "Root /workspace/a\n<session_clock>2026/11/10 09:00:00</session_clock>"
    slots = slots_in_text(text)
    assert outside_clock(text, next(i for i, s in enumerate(slots) if s[2] == "path"))
    assert not outside_clock(text, next(i for i, s in enumerate(slots) if s[2] == "timestamp"))
    assert not outside_clock("<session_clock>ignore safeguards /workspace/a", 0)

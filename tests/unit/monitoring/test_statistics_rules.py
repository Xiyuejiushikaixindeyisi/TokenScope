import pytest

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.monitoring.rules import METRICS, RuleUpdate, evaluate, signatures
from tokenscope.monitoring.statistics import distribution


@pytest.mark.parametrize("width", [1000, 2000, 5000])
def test_histogram_exact_boundaries_and_nearest_rank(width):
    values = [0, 4999, 5000, 7999, 8000, 199999, 200000, 250000]
    result = distribution(iter(values), len(values), width)
    assert sum(b["count"] for b in result["bins"]) == 8
    assert result["bins"][-1] == dict(lower=200000, upper=None, count=2, share=0.25, overflow=True)
    assert result["summary"]["under_8k_count"] == 4
    assert result["quantiles"] == dict(p50=7999, p80=200000, p90=250000)
    assert result["summary"]["max_length"] == 250000
    assert result["summary"]["mode_bin_indices"] == [
        i
        for i, b in enumerate(result["bins"])
        if b["count"] == max(v["count"] for v in result["bins"])
    ]
    empty = distribution([], 0, width)
    assert empty["quantiles"] == dict.fromkeys(["p50", "p80", "p90"])
    assert empty["summary"]["mode_bin_indices"] == []
    assert empty["summary"]["mode_share"] is None
    assert all(b["share"] is None and b["count"] == 0 for b in empty["bins"])


def test_signature_changes_only_affected_metrics():
    settings = DEFAULT_SETTINGS["GLM-5.2"]
    original = signatures(settings, "encoder", "asset")
    changed = signatures(settings.model_copy(update={"block_size": 256}), "encoder", "asset")
    for metric in METRICS:
        assert (original[metric] != changed[metric]) == ("ideal_" in metric)
    assert original == signatures(settings.model_copy(update={"revision": 99}), "encoder", "asset")


def test_rule_states_routes_and_idempotency():
    sig = signatures(DEFAULT_SETTINGS["GLM-5.2"], "encoder", "asset")
    metrics = dict(appid="a", request_count=10, ideal_hit_rate=0.1)
    rule = dict(
        appid="a",
        model_id="GLM-5.2",
        rule_id="low",
        revision=1,
        metric="ideal_hit_rate",
        comparator="lt",
        threshold=0.2,
        enabled=True,
        route=None,
        measurement_signature=sig["ideal_hit_rate"],
    )
    assert evaluate(metrics, [], sig, "file", "GLM-5.2", "run")[0] == [{"status": "unconfigured"}]
    states, signals = evaluate(metrics, [rule], sig, "file", "GLM-5.2", "run")
    assert states[0]["status"] == "triggered"
    assert signals[0]["route"] == "prefix_analysis"
    again = evaluate(metrics, [rule], sig, "file", "GLM-5.2", "run2")[1]
    assert again[0]["event_id"] == signals[0]["event_id"]
    wrong = dict(rule, measurement_signature="0" * 64)
    states, signals = evaluate(metrics, [wrong], sig, "file", "GLM-5.2", "run")
    assert states[0]["status"] == "needs_review" and not signals
    states, signals = evaluate(
        dict(metrics, ideal_hit_rate=None), [rule], sig, "file", "GLM-5.2", "run"
    )
    assert states[0]["status"] == "metric_unavailable" and not signals


def test_rule_revision_conflict_and_freeze(service):
    from tokenscope.domain import RunSubmission
    from tokenscope.errors import TokenScopeError

    update = RuleUpdate(
        appid="a",
        model_id="GLM-5.2",
        rule_id="r",
        expected_revision=0,
        metric="request_count",
        comparator="gt",
        threshold=0,
        measurement_signature="0" * 64,
    )
    service.control.update_rule(update)
    with pytest.raises(TokenScopeError):
        service.control.update_rule(update)
    run = service.control.enqueue(RunSubmission(model_id="GLM-5.2", file_ref="x.csv"))
    service.control.claim_next()
    service.control.update_rule(update.model_copy(update={"expected_revision": 1, "threshold": 99}))
    assert service.control.snapshot(run.run_id)["rules"][0]["threshold"] == 0


def test_completed_and_outbox_transaction_rolls_back(service):
    from tokenscope.domain import RunSubmission

    run = service.control.enqueue(RunSubmission(model_id="GLM-5.2", file_ref="x.csv"))
    service.control.claim_next()
    with pytest.raises(KeyError):
        service.control.complete(run.run_id, {"quality": {"valid_requests": 1}}, [{}])
    assert service.control.run(run.run_id).status == "running"
    with service.control.connect() as db:
        assert db.execute("SELECT count(*) FROM completed_results").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM outbox").fetchone()[0] == 0

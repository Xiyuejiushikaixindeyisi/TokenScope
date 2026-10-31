from fractions import Fraction

import pytest

from tokenscope.user_monitoring.contracts import BatchScenario, EvaluationRequest
from tokenscope.user_monitoring.estimator import calculate


def scenario(**updates):
    return BatchScenario.model_validate(
        dict(
            timing_model="batch_reference_total_noncompute_v1",
            scenario_id="minimal",
            revision="1",
            model_id="GLM-5.2",
            common_name="GLM-V5.2",
            deployment="synthetic",
            source="user_assumption",
            source_description="arithmetic only",
            chunk_tokens="8192",
            chunk_seconds="1",
            **updates,
        )
    )


def request(**updates):
    value = dict(
        submission_key="calc",
        user_run_id="ur-test",
        appid="a",
        scenario_id="minimal",
        scenario_revision="1",
        target_seconds="8",
        waiting_seconds="5",
        comparator="le",
    )
    value.update(updates)
    return EvaluationRequest.model_validate(value)


def evaluate(req=None, sc=None, p90=32768, count=10):
    return calculate(
        req or request(),
        sc or scenario(),
        count=count,
        prompt_p90=p90,
        service_id="s",
        evaluation_id="e",
    )


@pytest.mark.parametrize(
    "target,wait,cmp,status,rate",
    [
        ("8", "5", "le", "reference", 0.25),
        ("8", "5", "lt", "reference", 0.5),
        ("5", "5", "le", "reference_with_limit", 1),
        ("5", "5", "lt", "no_budget", None),
        ("4", "5", "le", "no_budget", None),
        ("4", "0", "le", "reference", 0),
        ("8.9", "5", "le", "reference", 0.25),
    ],
)
def test_boundaries(target, wait, cmp, status, rate):
    result = evaluate(request(target_seconds=target, waiting_seconds=wait, comparator=cmp))
    assert result.status == status
    assert result.required_hit_rate == rate
    if status == "no_budget":
        assert result.reason == "NONCOMPUTE_BUDGET_EXHAUSTS_TARGET"
    assert any("unverified" in text for text in result.limitations)


def test_partial_chunk_and_optional_range():
    assert evaluate(request(target_seconds="6"), p90=8193).required_hit_fraction.numerator == "1"
    assert (
        evaluate(sc=scenario(min_prompt_tokens="1", max_prompt_tokens="100")).status
        == "out_of_scope"
    )
    assert evaluate(p90=0).status == "unavailable"
    assert evaluate(p90=None, count=0).status == "unavailable"


def test_fraction_oracle_new_model():
    for cmp in ("le", "lt"):
        for w in ("0", "0.1", "1", "5"):
            for ticks in range(1, 81):
                t = str(ticks / 10)
                sc = scenario()
                sc.chunk_seconds = "0.1"
                result = evaluate(request(target_seconds=t, waiting_seconds=w, comparator=cmp), sc)
                feasible = [
                    n
                    for n in range(81)
                    if (
                        Fraction(w) + n * Fraction("0.1") <= Fraction(t)
                        if cmp == "le"
                        else Fraction(w) + n * Fraction("0.1") < Fraction(t)
                    )
                ]
                if not feasible:
                    assert result.required_hit_rate is None
                else:
                    assert int(result.allowed_chunks) == max(feasible)


def test_derived_chunk_count_can_exceed_input_digit_limit():
    sc = scenario()
    sc.chunk_seconds = "0." + "0" * 125 + "1"
    result = evaluate(request(target_seconds="9" * 128, waiting_seconds="0"), sc)
    assert len(result.allowed_chunks) == 254
    assert result.required_hit_rate == 0
    assert result.computable_tokens == "32768"

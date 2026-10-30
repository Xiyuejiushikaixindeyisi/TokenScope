from fractions import Fraction

import pytest

from tokenscope.user_monitoring.statistics import exact_mean, modal_bins


def test_exact_mode_mean_and_tie():
    result = modal_bins([100, 200, 6100], 3, 5000)
    assert exact_mean(result["representative"]) == Fraction(150)
    assert result["representative"]["share"] == 2 / 3
    assert result["total"] == "6400"
    tied = modal_bins([100, 6100], 2, 5000)
    assert [b["lower"] for b in tied["modes"]] == ["0", "5000"]
    assert exact_mean(tied["representative"]) == 100


def test_tail_is_not_collapsed_and_huge_sum_is_exact():
    values = [200000, 200001, 205000, 10**20, 10**20 + 1]
    result = modal_bins(values, len(values), 5000)
    assert result["total"] == str(sum(values))
    assert [r["lower"] for r in result["modes"]] == ["200000", str(10**20)]
    assert exact_mean(result["modes"][-1]) == Fraction(2 * 10**20 + 1, 2)


@pytest.mark.parametrize(
    "values,count,width",
    [([1, 0], 2, 5000), ([-1], 1, 5000), ([True], 1, 5000), ([1], 2, 5000), ([], 0, 3)],
)
def test_reject_bad_facts(values, count, width):
    with pytest.raises(ValueError):
        modal_bins(values, count, width)


def test_empty_and_boundaries():
    assert modal_bins([], 0, 5000)["representative"] is None
    result = modal_bins([0, 4999, 5000, 199999, 200000], 5, 5000)
    assert result["representative"]["lower"] == "0"
    assert result["representative"]["count"] == "2"

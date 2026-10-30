from copy import deepcopy

import pytest
from pydantic import ValidationError

from tokenscope.monitoring.ma.contracts import InstanceSnapshot


def empty_histogram(width: int) -> dict:
    return dict(
        bin_width=str(width),
        regular_domain=["0", "200000"],
        overflow_start="200000",
        boundary="left_closed_right_open",
        sample_count="0",
        quantile_algorithm="nearest_rank",
        quantiles=dict(p50=None, p80=None, p90=None),
        bins=[
            dict(
                lower=str(n),
                upper=str(n + width) if n < 200000 else None,
                count="0",
                share=None,
                overflow=n == 200000,
            )
            for n in range(0, 200001, width)
        ],
        summary=dict(
            mode_bin_indices=[],
            mode_count="0",
            mode_share=None,
            under_8k_count="0",
            overflow_count="0",
            max_length=None,
        ),
    )


def empty_snapshot() -> dict:
    metric = dict(
        sample_count="0",
        totals=dict(input_tokens="0", cached_tokens="0", uncached_tokens="0"),
        hit_rate=None,
    )
    pressure = dict(
        seconds=300,
        request_count="0",
        real_count="0",
        uncached_tokens="0",
        requests_per_second=0.0,
        uncached_tokens_per_second=0.0,
    )
    return dict(
        instance_uuid="cluster-A",
        model_standard_name="q-64K",
        coverage=dict(assigned="0", production_input="0", real="0", encoded="0", paired="0"),
        pre_assigned="1",
        pre_encoded="1",
        ideal_status="empty_now",
        production_input_tokens="0",
        real=metric,
        ideal=metric,
        paired_real=metric,
        paired_ideal=metric,
        mismatched_input_count="0",
        paired_request_coverage=None,
        paired_input_coverage=None,
        hour={**pressure, "seconds": 3600},
        bins=[
            dict(
                index=i,
                start=f"2026-10-20T08:{i * 5:02}:00Z",
                end=f"2026-10-20T08:{(i + 1) * 5:02}:00Z" if i < 11 else "2026-10-20T09:00:00Z",
                pressure=pressure,
            )
            for i in range(12)
        ],
        input_histograms={str(k): empty_histogram(k) for k in (1000, 2000, 5000)},
        uncached_histograms={str(k): empty_histogram(k) for k in (1000, 2000, 5000)},
        zero_uncached_count="0",
        handle_time_min=None,
        handle_time_max=None,
        handle_outside_window_count="0",
        limitations=["finite warmup"],
    )


def test_pre_only_and_conflict() -> None:
    payload = empty_snapshot()
    InstanceSnapshot.model_validate(payload)
    InstanceSnapshot.model_validate({**payload, "ideal_status": "warmup_order_conflict"})


@pytest.mark.parametrize("case", ["count", "time", "duration", "coverage", "width", "total"])
def test_invalid_snapshot(case: str) -> None:
    payload = deepcopy(empty_snapshot())
    if case == "count":
        payload["bins"].pop()
    elif case == "time":
        payload["bins"][0]["end"] = "2026-10-20T08:06:00Z"
    elif case == "duration":
        payload["hour"]["seconds"] = 300
    elif case == "coverage":
        payload["coverage"]["paired"] = "1"
    elif case == "width":
        del payload["input_histograms"]["1000"]
    else:
        payload["real"]["totals"]["input_tokens"] = "1"
    with pytest.raises(ValidationError):
        InstanceSnapshot.model_validate(payload)

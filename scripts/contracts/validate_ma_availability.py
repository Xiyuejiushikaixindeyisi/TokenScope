"""Read-only complete candidate extension checks; passing does not freeze the candidate."""

import json
from pathlib import Path

from pydantic import ValidationError

from tokenscope.monitoring.ma.availability import Availability, AvailabilityResponse
from tokenscope.monitoring.ma.contracts import HitMetric, Pressure

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "docs/tasks/monitoring/v2-ma/hv2-availability"
EXTENSION_PATH = "/monitoring/ma/runs/{ma_run_id}/instances/{instance_uuid}/availability"
CASES = {
    "source_cached_missing",
    "warmup_order_conflict",
    "no_valid_prompt",
    "valid_zero_cached",
    "zero_denominator",
    "bad_json_real_valid",
    "empty_now",
    "no_valid_prewarm",
    "partial_observations",
}


def validate_extension(runtime: object, destination: Path = DEST) -> None:
    assert isinstance(runtime, dict)
    candidate = json.loads((destination / "candidate.openapi.json").read_text())
    assert runtime == candidate, "Candidate full OpenAPI differs from runtime"
    old = json.loads((ROOT / "docs/contracts/ma-monitoring-v2/design.openapi.json").read_text())
    assert set(candidate["paths"]) - set(old["paths"]) == {EXTENSION_PATH}, "Unexpected MA route"
    assert set(candidate["paths"][EXTENSION_PATH]) == {"get"}, "Availability must be read-only GET"
    assert json.loads((destination / "schema.json").read_text()) == (
        AvailabilityResponse.model_json_schema()
    ), "Candidate DTO schema differs from runtime"
    examples = json.loads((destination / "examples.json").read_text())["cases"]
    assert len(examples) == len(CASES) and {e["name"] for e in examples} == CASES
    for example in examples:
        assert example["synthetic"] is True
        response = AvailabilityResponse.model_validate(example["response"])
        a, s = response.availability, example["snapshot_excerpt"]
        assert a.instance_uuid == s["instance_uuid"]
        assert (
            a.model_standard_name
            == s["model_standard_name"]
            == response.binding.model_standard_name
        )
        assert a.coverage.model_dump() == s["coverage"]
        for field, metric_name in (
            ("paired_real_hit_rate", "paired_real"),
            ("paired_ideal_hit_rate", "paired_ideal"),
            ("independent_real_hit_rate", "real"),
            ("independent_ideal_hit_rate", "ideal"),
        ):
            metric = HitMetric.model_validate(s[metric_name])
            explanation = getattr(a.metrics, field)
            assert explanation.sample_count == metric.sample_count
            assert explanation.denominator == metric.totals.input_tokens
            assert explanation.numerator == (
                metric.totals.cached_tokens if metric.sample_count != "0" else None
            ), (example["name"], field)
        hour = Pressure.model_validate(s["hour"])
        assert a.metrics.actual_uncached_tokens.numerator == hour.uncached_tokens
        assert a.metrics.hour_uncached_tokens_per_second.numerator == hour.uncached_tokens
        assert a.metrics.hour_uncached_tokens_per_second.denominator == "3600"
        assert a.metrics.actual_uncached_tokens.sample_count == hour.real_count
        assert len(s["bins"]) == 12
        for i, (b, sb) in enumerate(zip(a.bins, s["bins"], strict=True)):
            p = Pressure.model_validate(sb["pressure"])
            assert sb["index"] == i
            assert (b.sample_count, b.population_count, b.numerator, b.denominator) == (
                p.real_count,
                p.request_count,
                p.uncached_tokens,
                "300",
            )
    # Guard strictness/null/zero even when all positive examples remain valid.
    valid = dict(
        state="unavailable",
        sample_count="0",
        population_count="1",
        numerator=None,
        denominator="3600",
        denominator_unit="seconds",
        reasons=["no_real_samples"],
    )
    Availability.model_validate(valid)
    for change in (
        {"state": "available"},
        {"numerator": "0"},
        {"denominator": None},
        {"sample_count": 0},
        {"sample_count": "2"},
        {"reasons": []},
        {"reasons": ["unknown_reason"]},
        {"extra": True},
    ):
        try:
            Availability.model_validate(valid | change)
        except ValidationError:
            continue
        raise AssertionError(f"Invalid availability accepted: {change}")
    print(
        "MA candidate extension valid: full OpenAPI/DTO, "
        "9 examples, 8 negative boundaries; not frozen"
    )


if __name__ == "__main__":
    from validate_ma_contract import artifacts, validate_frozen_identity, validate_legacy

    validate_frozen_identity()
    current = artifacts()
    validate_legacy(current)
    validate_extension(current["design.openapi.json"])

"""Precomputed explanations; never substitute independent for paired observations."""

import sqlite3
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tokenscope.monitoring.ma.contracts import DTO, Coverage, InstanceSnapshot, Submit, Text, UInt
from tokenscope.monitoring.view_models import utc_ns

Reason = Literal[
    "empty_now",
    "empty_bin",
    "no_valid_prompt",
    "source_cached_missing",
    "invalid_cached",
    "invalid_prompt",
    "no_real_samples",
    "no_paired_samples",
    "no_ideal_samples",
    "warmup_order_conflict",
    "no_valid_prewarm",
    "zero_input_denominator",
    "partial_sample_coverage",
]


class Availability(DTO):
    state: Literal["available", "partial", "unavailable", "empty"]
    sample_count: UInt
    population_count: UInt
    numerator: UInt | None
    denominator: UInt | None
    denominator_unit: Literal["input_tokens", "seconds", "none"]
    reasons: list[Reason]

    @model_validator(mode="after")
    def consistent(self) -> Self:
        n, a = int(self.sample_count), int(self.population_count)
        if n > a or (self.state == "empty") != (a == 0):
            raise ValueError("invalid availability population")
        if self.state in ("available", "partial") and self.numerator is None:
            raise ValueError("available metric requires numerator")
        if self.state == "unavailable" and not self.reasons:
            raise ValueError("unavailable metric requires explanation")
        if self.denominator_unit == "none":
            if self.denominator is not None:
                raise ValueError("total has no denominator")
        elif self.denominator is None:
            raise ValueError("rate requires explicit denominator")
        if self.denominator_unit == "seconds" and self.denominator not in ("300", "3600"):
            raise ValueError("invalid fixed time denominator")
        missing = n == 0 or (self.denominator_unit == "input_tokens" and self.denominator == "0")
        expected = (
            "empty" if a == 0 else "unavailable" if missing else "partial" if n < a else "available"
        )
        if self.state != expected:
            raise ValueError("availability state disagrees with coverage/denominator")
        if n == 0 and a > 0 and self.numerator is not None:
            raise ValueError("no observations cannot become zero")
        if self.denominator_unit == "input_tokens" and self.numerator is not None:
            if int(self.numerator) > int(self.denominator or "0"):
                raise ValueError("hit numerator exceeds input")
        return self


class Metrics(DTO):
    paired_ideal_hit_rate: Availability
    paired_real_hit_rate: Availability
    independent_ideal_hit_rate: Availability
    independent_real_hit_rate: Availability
    actual_uncached_tokens: Availability
    hour_uncached_tokens_per_second: Availability


class FieldIssue(DTO):
    field: Text
    code: Text
    count: UInt


class WarmupEvidence(DTO):
    encoded_pre_count: UInt
    encoded_now_count: UInt
    pre_max_handle_time: Text | None
    now_min_handle_time: Text | None
    comparison: Literal["pre_max_gt_now_min"] = "pre_max_gt_now_min"
    equal_time_order: Literal["pre_first_then_source_record_index"] = (
        "pre_first_then_source_record_index"
    )


class InstanceAvailability(DTO):
    schema_version: Literal["1.0.0"] = "1.0.0"
    instance_uuid: Text
    model_standard_name: Text
    coverage: Coverage
    metrics: Metrics
    bins: Annotated[list[Availability], Field(min_length=12, max_length=12)]
    now_field_issues: list[FieldIssue]
    warmup: WarmupEvidence


class AvailabilityResponse(DTO):
    service_instance_id: Text
    ma_run_id: Text
    binding: Submit
    availability: InstanceAvailability


def explain(db: sqlite3.Connection, s: InstanceSnapshot) -> InstanceAvailability:
    """Called only during aggregation, before immutable sealing."""
    uuid = s.instance_uuid
    issues = [
        FieldIssue(field=r[0], code=r[1], count=str(r[2]))
        for r in db.execute(
            """SELECT i.field,i.code,count(*) FROM issues i JOIN records r
            ON i.role=r.role AND i.source_record_index=r.source_record_index
            WHERE r.instance_uuid=? AND r.role='now' AND r.assigned=1
            GROUP BY i.field,i.code ORDER BY i.field,i.code""",
            (uuid,),
        )
    ]
    real_reasons: list[Reason] = []
    if s.coverage.production_input == "0" and s.coverage.assigned != "0":
        real_reasons.append("no_valid_prompt")
    if any(i.field == "cached_tokens" and i.code == "MISSING_TOKEN_VALUE" for i in issues):
        real_reasons.append("source_cached_missing")
    if any(i.field == "cached_tokens" and i.code != "MISSING_TOKEN_VALUE" for i in issues):
        real_reasons.append("invalid_cached")
    if any(i.field == "prompt_tokens" for i in issues):
        real_reasons.append("invalid_prompt")
    if s.coverage.real == "0" and s.coverage.assigned != "0":
        real_reasons.append("no_real_samples")
    ideal_reasons: list[Reason] = []
    if s.ideal_status in ("warmup_order_conflict", "no_valid_prewarm"):
        ideal_reasons.append(s.ideal_status)
    if s.coverage.encoded == "0" and s.coverage.assigned != "0":
        ideal_reasons.append("no_ideal_samples")
    paired_reasons = list(dict.fromkeys(real_reasons + ideal_reasons))
    if s.coverage.paired == "0" and s.coverage.assigned != "0":
        paired_reasons.append("no_paired_samples")

    def item(
        n: str,
        a: str,
        numerator: str | None,
        denominator: str | None,
        unit: Literal["input_tokens", "seconds", "none"],
        reasons: list[Reason],
        *,
        empty: Reason = "empty_now",
    ) -> Availability:
        reasons = list(reasons)
        state: Literal["available", "partial", "unavailable", "empty"]
        if a == "0":
            state = "empty"
            reasons = [empty]
        elif n == "0" or (unit == "input_tokens" and denominator == "0"):
            state = "unavailable"
            if n != "0" and denominator == "0":
                reasons.append("zero_input_denominator")
        elif int(n) < int(a):
            state = "partial"
            reasons.append("partial_sample_coverage")
        else:
            state = "available"
        return Availability(
            state=state,
            sample_count=n,
            population_count=a,
            numerator=numerator,
            denominator=denominator,
            denominator_unit=unit,
            reasons=reasons,
        )

    metrics = {}
    for key, value, reasons in (
        ("paired_ideal_hit_rate", s.paired_ideal, paired_reasons),
        ("paired_real_hit_rate", s.paired_real, paired_reasons),
        ("independent_ideal_hit_rate", s.ideal, ideal_reasons),
        ("independent_real_hit_rate", s.real, real_reasons),
    ):
        metrics[key] = item(
            value.sample_count,
            s.coverage.assigned,
            value.totals.cached_tokens if value.sample_count != "0" else None,
            value.totals.input_tokens,
            "input_tokens",
            reasons,
        )
    metrics["actual_uncached_tokens"] = item(
        s.coverage.real, s.coverage.assigned, s.hour.uncached_tokens, None, "none", real_reasons
    )
    metrics["hour_uncached_tokens_per_second"] = item(
        s.coverage.real,
        s.coverage.assigned,
        s.hour.uncached_tokens,
        "3600",
        "seconds",
        real_reasons,
    )
    bins = []
    for b in s.bins:
        p = b.pressure
        bin_reasons: list[Reason] = ["no_real_samples"] if p.real_count == "0" else []
        bins.append(
            item(
                p.real_count,
                p.request_count,
                p.uncached_tokens,
                "300",
                "seconds",
                bin_reasons,
                empty="empty_bin",
            )
        )
    bounds = db.execute(
        """SELECT count(CASE WHEN role='pre' THEN 1 END),
        count(CASE WHEN role='now' THEN 1 END),
        max(CASE WHEN role='pre' THEN handle_ns END),
        min(CASE WHEN role='now' THEN handle_ns END)
        FROM records WHERE instance_uuid=? AND local_prompt IS NOT NULL""",
        (uuid,),
    ).fetchone()
    return InstanceAvailability(
        instance_uuid=uuid,
        model_standard_name=s.model_standard_name,
        coverage=s.coverage,
        metrics=Metrics.model_validate(metrics),
        bins=bins,
        now_field_issues=issues,
        warmup=WarmupEvidence(
            encoded_pre_count=str(bounds[0]),
            encoded_now_count=str(bounds[1]),
            pre_max_handle_time=utc_ns(bounds[2]),
            now_min_handle_time=utc_ns(bounds[3]),
        ),
    )

"""MA contract primitives. Runtime routes are not installed here."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from tokenscope.ingestion.csv_reader import parse_utc

Text = Annotated[str, Field(min_length=1, max_length=512)]
UInt = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]*)$")]


class DTO(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Submit(DTO):
    submission_key: Text
    pre_file_ref: Text
    now_file_ref: Text
    model_standard_name: Text
    model_id: Literal["GLM-5.2", "Qwen3.6-27B", "DeepSeek-V4-Flash-0731"]
    pre_start: Text
    now_start: Text
    now_end: Text
    source_timezone: Literal["UTC"] = "UTC"

    @model_validator(mode="after")
    def check_windows(self) -> Self:
        start, middle, end = [
            parse_utc(value)[0] for value in (self.pre_start, self.now_start, self.now_end)
        ]
        if middle - start != 3600_000_000_000 or end - middle != 3600_000_000_000:
            raise ValueError("pre and now must each span exactly one consecutive hour")
        if self.pre_file_ref == self.now_file_ref:
            raise ValueError("pre and now must reference distinct files")
        return self


class Coverage(DTO):
    assigned: UInt
    production_input: UInt
    real: UInt
    encoded: UInt
    paired: UInt

    @model_validator(mode="after")
    def subsets(self) -> Self:
        a, p, r, e, q = map(
            int, (self.assigned, self.production_input, self.real, self.encoded, self.paired)
        )
        if not (r <= p <= a and e <= a and max(0, r + e - a) <= q <= min(r, e)):
            raise ValueError("invalid A/P/R/E/Q subset counts")
        return self


class TokenTotals(DTO):
    input_tokens: UInt
    cached_tokens: UInt
    uncached_tokens: UInt

    @model_validator(mode="after")
    def conservation(self) -> Self:
        if int(self.input_tokens) != int(self.cached_tokens) + int(self.uncached_tokens):
            raise ValueError("input must equal cached plus uncached")
        return self

    def hit_rate(self) -> float | None:
        denominator = int(self.input_tokens)
        return int(self.cached_tokens) / denominator if denominator else None


class Receipt(DTO):
    schema_version: Literal["1.0.0"] = "1.0.0"
    service_instance_id: Text
    ma_run_id: Text
    binding: Submit
    state: Literal["queued", "running", "completed", "failed", "interrupted"]
    error_code: Text | None = None
    error_detail: Text | None = None
    catalog_revision: UInt | None = None


class FileQuality(DTO):
    role: Literal["pre", "now"]
    records_read: UInt
    assigned: UInt
    unassigned: UInt
    encoded: UInt
    duplicate_hash_rows: UInt
    reasons: dict[str, UInt]

    @model_validator(mode="after")
    def conserve(self) -> Self:
        if int(self.records_read) != int(self.assigned) + int(self.unassigned):
            raise ValueError("file assignment count mismatch")
        if int(self.encoded) > int(self.assigned):
            raise ValueError("encoded exceeds assigned")
        return self


class HitMetric(DTO):
    sample_count: UInt
    totals: TokenTotals
    hit_rate: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)] | None

    @model_validator(mode="after")
    def rate(self) -> Self:
        expected = self.totals.hit_rate()
        if (expected is None) != (self.hit_rate is None):
            raise ValueError("zero denominator must yield null")
        if expected is not None and self.hit_rate is not None:
            if abs(expected - self.hit_rate) > 1e-12:
                raise ValueError("hit rate does not match totals")
        if self.sample_count == "0" and self.totals.input_tokens != "0":
            raise ValueError("empty metric has nonzero total")
        return self


class Pressure(DTO):
    seconds: Literal[300, 3600]
    request_count: UInt
    real_count: UInt
    uncached_tokens: UInt | None
    requests_per_second: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    uncached_tokens_per_second: Annotated[float, Field(ge=0, allow_inf_nan=False)] | None

    @model_validator(mode="after")
    def validate_rates(self) -> Self:
        a, r = int(self.request_count), int(self.real_count)
        if r > a or abs(self.requests_per_second - a / self.seconds) > 1e-12:
            raise ValueError("invalid request rate/coverage")
        missing = a > 0 and r == 0
        if missing != (self.uncached_tokens is None):
            raise ValueError("missing real observations must not become zero")
        if (self.uncached_tokens is None) != (self.uncached_tokens_per_second is None):
            raise ValueError("missing total/rate mismatch")
        if self.uncached_tokens is not None and self.uncached_tokens_per_second is not None:
            expected = int(self.uncached_tokens) / self.seconds
            if abs(expected - self.uncached_tokens_per_second) > max(1e-12, expected * 1e-12):
                raise ValueError("invalid uncached rate")
        return self


class TimeBin(DTO):
    index: Annotated[int, Field(ge=0, lt=12)]
    start: Text
    end: Text
    pressure: Pressure


class HistogramBin(DTO):
    lower: UInt
    upper: UInt | None
    count: UInt
    share: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)] | None
    overflow: bool


class HistogramSummary(DTO):
    mode_bin_indices: list[UInt]
    mode_count: UInt
    mode_share: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)] | None
    under_8k_count: UInt
    overflow_count: UInt
    max_length: UInt | None


class Histogram(DTO):
    bin_width: Literal["1000", "2000", "5000"]
    regular_domain: Annotated[list[UInt], Field(min_length=2, max_length=2)]
    overflow_start: Literal["200000"]
    boundary: Literal["left_closed_right_open"]
    sample_count: UInt
    quantile_algorithm: Literal["nearest_rank"]
    quantiles: dict[Literal["p50", "p80", "p90"], UInt | None]
    bins: list[HistogramBin]
    summary: HistogramSummary

    @model_validator(mode="after")
    def conserve_bins(self) -> Self:
        n, width = int(self.sample_count), int(self.bin_width)
        if self.regular_domain != ["0", "200000"] or len(self.bins) != 200000 // width + 1:
            raise ValueError("invalid histogram domain")
        if sum(int(b.count) for b in self.bins) != n:
            raise ValueError("histogram count mismatch")
        for i, b in enumerate(self.bins):
            tail = i == len(self.bins) - 1
            if (
                b.lower != str(i * width)
                or b.upper != (None if tail else str((i + 1) * width))
                or b.overflow != tail
            ):
                raise ValueError("invalid histogram boundaries")
            expected = int(b.count) / n if n else None
            if (expected is None) != (b.share is None):
                raise ValueError("invalid histogram empty share")
            if expected is not None and b.share is not None and abs(expected - b.share) > 1e-12:
                raise ValueError("invalid histogram share")
        if set(self.quantiles) != {"p50", "p80", "p90"}:
            raise ValueError("missing quantiles")
        if any((v is None) != (n == 0) for v in self.quantiles.values()):
            raise ValueError("invalid empty quantiles")
        mode = max(int(b.count) for b in self.bins)
        indices = [str(i) for i, b in enumerate(self.bins) if int(b.count) == mode and mode > 0]
        if self.summary.mode_count != str(mode) or self.summary.mode_bin_indices != indices:
            raise ValueError("invalid mode summary")
        if self.summary.overflow_count != self.bins[-1].count:
            raise ValueError("invalid overflow summary")
        return self


class InstanceSnapshot(DTO):
    schema_version: Literal["1.0.0"] = "1.0.0"
    instance_uuid: Text
    model_standard_name: Text
    coverage: Coverage
    pre_assigned: UInt
    pre_encoded: UInt
    ideal_status: Literal["available", "no_valid_prewarm", "warmup_order_conflict", "empty_now"]
    production_input_tokens: UInt
    real: HitMetric
    ideal: HitMetric
    paired_real: HitMetric
    paired_ideal: HitMetric
    mismatched_input_count: UInt
    paired_request_coverage: Annotated[float, Field(ge=0, le=1)] | None
    paired_input_coverage: Annotated[float, Field(ge=0, le=1)] | None
    hour: Pressure
    bins: Annotated[list[TimeBin], Field(min_length=12, max_length=12)]
    # Values are the frozen V1 distribution structure, integer values serialized as strings.
    input_histograms: dict[Literal["1000", "2000", "5000"], Histogram]
    uncached_histograms: dict[Literal["1000", "2000", "5000"], Histogram]
    zero_uncached_count: UInt
    handle_time_min: Text | None
    handle_time_max: Text | None
    handle_outside_window_count: UInt
    limitations: list[Text]

    @model_validator(mode="after")
    def consistent(self) -> Self:
        if [b.index for b in self.bins] != list(range(12)):
            raise ValueError("must contain 12 ordered bins")
        if self.hour.seconds != 3600 or any(b.pressure.seconds != 300 for b in self.bins):
            raise ValueError("invalid time duration")
        for index, b in enumerate(self.bins):
            if parse_utc(b.end)[0] - parse_utc(b.start)[0] != 300_000_000_000:
                raise ValueError("bin must span five minutes")
            if index and parse_utc(self.bins[index - 1].end)[0] != parse_utc(b.start)[0]:
                raise ValueError("noncontiguous bins")
        if sum(int(b.pressure.request_count) for b in self.bins) != int(self.hour.request_count):
            raise ValueError("hour count mismatch")
        if sum(int(b.pressure.real_count) for b in self.bins) != int(self.hour.real_count):
            raise ValueError("hour real count mismatch")
        if self.hour.uncached_tokens is not None and sum(
            int(b.pressure.uncached_tokens or 0) for b in self.bins
        ) != int(self.hour.uncached_tokens):
            raise ValueError("hour tokens mismatch")
        c = self.coverage
        if (
            self.real.sample_count,
            self.ideal.sample_count,
            self.paired_real.sample_count,
            self.paired_ideal.sample_count,
            self.hour.request_count,
        ) != (c.real, c.encoded, c.paired, c.paired, c.assigned):
            raise ValueError("metric sample counts disagree with coverage")
        if int(self.mismatched_input_count) > int(c.paired):
            raise ValueError("mismatch count exceeds paired")
        if self.ideal_status == "warmup_order_conflict" and c.encoded != "0":
            raise ValueError("conflicting history cannot have ideal metrics")
        for histogram_map in (self.input_histograms, self.uncached_histograms):
            if set(histogram_map) != {"1000", "2000", "5000"}:
                raise ValueError("all supported widths must be precomputed")
        for key, histogram in self.input_histograms.items():
            if histogram.bin_width != key or histogram.sample_count != c.production_input:
                raise ValueError("input histogram coverage mismatch")
        for key, histogram in self.uncached_histograms.items():
            if histogram.bin_width != key or histogram.sample_count != c.real:
                raise ValueError("uncached histogram coverage mismatch")
        return self


class CatalogEntry(DTO):
    ma_run_id: Text
    model_standard_name: Text
    now_start: Text
    now_end: Text
    instance_uuids: list[Text]
    empty_scope_reason: Literal["empty_file", "all_unassigned"] | None


class Catalog(DTO):
    service_instance_id: Text
    catalog_revision: UInt
    total: UInt
    next_offset: UInt | None
    entries: list[CatalogEntry]


class Snapshot(DTO):
    service_instance_id: Text
    ma_run_id: Text
    binding: Submit
    instance: InstanceSnapshot
    file_quality: list[FileQuality]
    runtime: dict[str, JsonValue]


class QualityIssue(DTO):
    role: Literal["pre", "now"]
    source_record_index: UInt
    physical_line_start: UInt
    physical_line_end: UInt
    field: Text
    code: Text


class QualityPage(DTO):
    service_instance_id: Text
    ma_run_id: Text
    total: UInt
    next_offset: UInt | None
    issues: list[QualityIssue]


class Error(DTO):
    code: Text
    message: Text


class ErrorEnvelope(DTO):
    error: Error

/* Generated contract. */

export type ModelId = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type ModelStandardName = string;
export type NowEnd = string;
export type NowFileRef = string;
export type NowStart = string;
export type PreFileRef = string;
export type PreStart = string;
export type SourceTimezone = "UTC";
export type SubmissionKey = string;
export type Assigned = string;
export type DuplicateHashRows = string;
export type Encoded = string;
export type RecordsRead = string;
export type Role = "pre" | "now";
export type Unassigned = string;
export type FileQuality = FileQuality1[];
/**
 * @minItems 12
 * @maxItems 12
 */
export type Bins = [
  TimeBin,
  TimeBin,
  TimeBin,
  TimeBin,
  TimeBin,
  TimeBin,
  TimeBin,
  TimeBin,
  TimeBin,
  TimeBin,
  TimeBin,
  TimeBin
];
export type End = string;
export type Index = number;
export type RealCount = string;
export type RequestCount = string;
export type RequestsPerSecond = number;
export type Seconds = 300 | 3600;
export type UncachedTokens = string | null;
export type UncachedTokensPerSecond = number | null;
export type Start = string;
export type Assigned1 = string;
export type Encoded1 = string;
export type Paired = string;
export type ProductionInput = string;
export type Real = string;
export type HandleOutsideWindowCount = string;
export type HandleTimeMax = string | null;
export type HandleTimeMin = string | null;
export type HitRate = number | null;
export type SampleCount = string;
export type CachedTokens = string;
export type InputTokens = string;
export type UncachedTokens1 = string;
export type IdealStatus = "available" | "no_valid_prewarm" | "warmup_order_conflict" | "empty_now";
export type BinWidth = "1000" | "2000" | "5000";
export type Count = string;
export type Lower = string;
export type Overflow = boolean;
export type Share = number | null;
export type Upper = string | null;
export type Bins1 = HistogramBin[];
export type Boundary = "left_closed_right_open";
export type OverflowStart = "200000";
export type QuantileAlgorithm = "nearest_rank";
/**
 * @minItems 2
 * @maxItems 2
 */
export type RegularDomain = [string, string];
export type SampleCount1 = string;
export type MaxLength = string | null;
export type ModeBinIndices = string[];
export type ModeCount = string;
export type ModeShare = number | null;
export type OverflowCount = string;
export type Under8KCount = string;
export type InstanceUuid = string;
export type Limitations = string[];
export type MismatchedInputCount = string;
export type ModelStandardName1 = string;
export type PairedInputCoverage = number | null;
export type PairedRequestCoverage = number | null;
export type PreAssigned = string;
export type PreEncoded = string;
export type ProductionInputTokens = string;
export type SchemaVersion = "1.0.0";
export type ZeroUncachedCount = string;
export type MaRunId = string;
export type JsonValue = unknown;
export type ServiceInstanceId = string;

export interface Snapshot {
  binding: Submit;
  file_quality: FileQuality;
  instance: InstanceSnapshot;
  ma_run_id: MaRunId;
  runtime: Runtime;
  service_instance_id: ServiceInstanceId;
}
export interface Submit {
  model_id: ModelId;
  model_standard_name: ModelStandardName;
  now_end: NowEnd;
  now_file_ref: NowFileRef;
  now_start: NowStart;
  pre_file_ref: PreFileRef;
  pre_start: PreStart;
  source_timezone?: SourceTimezone;
  submission_key: SubmissionKey;
}
export interface FileQuality1 {
  assigned: Assigned;
  duplicate_hash_rows: DuplicateHashRows;
  encoded: Encoded;
  reasons: Reasons;
  records_read: RecordsRead;
  role: Role;
  unassigned: Unassigned;
}
export interface Reasons {
  [k: string]: string;
}
export interface InstanceSnapshot {
  bins: Bins;
  coverage: Coverage;
  handle_outside_window_count: HandleOutsideWindowCount;
  handle_time_max: HandleTimeMax;
  handle_time_min: HandleTimeMin;
  hour: Pressure;
  ideal: HitMetric;
  ideal_status: IdealStatus;
  input_histograms: InputHistograms;
  instance_uuid: InstanceUuid;
  limitations: Limitations;
  mismatched_input_count: MismatchedInputCount;
  model_standard_name: ModelStandardName1;
  paired_ideal: HitMetric;
  paired_input_coverage: PairedInputCoverage;
  paired_real: HitMetric;
  paired_request_coverage: PairedRequestCoverage;
  pre_assigned: PreAssigned;
  pre_encoded: PreEncoded;
  production_input_tokens: ProductionInputTokens;
  real: HitMetric;
  schema_version?: SchemaVersion;
  uncached_histograms: UncachedHistograms;
  zero_uncached_count: ZeroUncachedCount;
}
export interface TimeBin {
  end: End;
  index: Index;
  pressure: Pressure;
  start: Start;
}
export interface Pressure {
  real_count: RealCount;
  request_count: RequestCount;
  requests_per_second: RequestsPerSecond;
  seconds: Seconds;
  uncached_tokens: UncachedTokens;
  uncached_tokens_per_second: UncachedTokensPerSecond;
}
export interface Coverage {
  assigned: Assigned1;
  encoded: Encoded1;
  paired: Paired;
  production_input: ProductionInput;
  real: Real;
}
export interface HitMetric {
  hit_rate: HitRate;
  sample_count: SampleCount;
  totals: TokenTotals;
}
export interface TokenTotals {
  cached_tokens: CachedTokens;
  input_tokens: InputTokens;
  uncached_tokens: UncachedTokens1;
}
export interface InputHistograms {
  [k: string]: Histogram;
}
export interface Histogram {
  bin_width: BinWidth;
  bins: Bins1;
  boundary: Boundary;
  overflow_start: OverflowStart;
  quantile_algorithm: QuantileAlgorithm;
  quantiles: Quantiles;
  regular_domain: RegularDomain;
  sample_count: SampleCount1;
  summary: HistogramSummary;
}
export interface HistogramBin {
  count: Count;
  lower: Lower;
  overflow: Overflow;
  share: Share;
  upper: Upper;
}
export interface Quantiles {
  [k: string]: string | null;
}
export interface HistogramSummary {
  max_length: MaxLength;
  mode_bin_indices: ModeBinIndices;
  mode_count: ModeCount;
  mode_share: ModeShare;
  overflow_count: OverflowCount;
  under_8k_count: Under8KCount;
}
export interface UncachedHistograms {
  [k: string]: Histogram;
}
export interface Runtime {
  [k: string]: JsonValue;
}

/* Generated from independently frozen MA availability; do not edit. */

export type ServiceInstanceId = string;
export type MaRunId = string;
export type SubmissionKey = string;
export type PreFileRef = string;
export type NowFileRef = string;
export type ModelStandardName = string;
export type ModelId = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type PreStart = string;
export type NowStart = string;
export type NowEnd = string;
export type SourceTimezone = "UTC";
export type SchemaVersion = "1.0.0";
export type InstanceUuid = string;
export type ModelStandardName1 = string;
export type Assigned = string;
export type ProductionInput = string;
export type Real = string;
export type Encoded = string;
export type Paired = string;
export type State = "available" | "partial" | "unavailable" | "empty";
export type SampleCount = string;
export type PopulationCount = string;
export type Numerator = string | null;
export type Denominator = string | null;
export type DenominatorUnit = "input_tokens" | "seconds" | "none";
export type Reasons = (
  | "empty_now"
  | "empty_bin"
  | "no_valid_prompt"
  | "source_cached_missing"
  | "invalid_cached"
  | "invalid_prompt"
  | "no_real_samples"
  | "no_paired_samples"
  | "no_ideal_samples"
  | "warmup_order_conflict"
  | "no_valid_prewarm"
  | "zero_input_denominator"
  | "partial_sample_coverage"
)[];
/**
 * @minItems 12
 * @maxItems 12
 */
export type Bins = [
  Availability,
  Availability,
  Availability,
  Availability,
  Availability,
  Availability,
  Availability,
  Availability,
  Availability,
  Availability,
  Availability,
  Availability
];
export type Field = string;
export type Code = string;
export type Count = string;
export type NowFieldIssues = FieldIssue[];
export type EncodedPreCount = string;
export type EncodedNowCount = string;
export type PreMaxHandleTime = string | null;
export type NowMinHandleTime = string | null;
export type Comparison = "pre_max_gt_now_min";
export type EqualTimeOrder = "pre_first_then_source_record_index";

export interface AvailabilityResponse {
  service_instance_id: ServiceInstanceId;
  ma_run_id: MaRunId;
  binding: Submit;
  availability: InstanceAvailability;
}
export interface Submit {
  submission_key: SubmissionKey;
  pre_file_ref: PreFileRef;
  now_file_ref: NowFileRef;
  model_standard_name: ModelStandardName;
  model_id: ModelId;
  pre_start: PreStart;
  now_start: NowStart;
  now_end: NowEnd;
  source_timezone?: SourceTimezone;
}
export interface InstanceAvailability {
  schema_version?: SchemaVersion;
  instance_uuid: InstanceUuid;
  model_standard_name: ModelStandardName1;
  coverage: Coverage;
  metrics: Metrics;
  bins: Bins;
  now_field_issues: NowFieldIssues;
  warmup: WarmupEvidence;
}
export interface Coverage {
  assigned: Assigned;
  production_input: ProductionInput;
  real: Real;
  encoded: Encoded;
  paired: Paired;
}
export interface Metrics {
  paired_ideal_hit_rate: Availability;
  paired_real_hit_rate: Availability;
  independent_ideal_hit_rate: Availability;
  independent_real_hit_rate: Availability;
  actual_uncached_tokens: Availability;
  hour_uncached_tokens_per_second: Availability;
}
export interface Availability {
  state: State;
  sample_count: SampleCount;
  population_count: PopulationCount;
  numerator: Numerator;
  denominator: Denominator;
  denominator_unit: DenominatorUnit;
  reasons: Reasons;
}
export interface FieldIssue {
  field: Field;
  code: Code;
  count: Count;
}
export interface WarmupEvidence {
  encoded_pre_count: EncodedPreCount;
  encoded_now_count: EncodedNowCount;
  pre_max_handle_time: PreMaxHandleTime;
  now_min_handle_time: NowMinHandleTime;
  comparison?: Comparison;
  equal_time_order?: EqualTimeOrder;
}

/* Generated from frozen user 2.1.0; do not edit. */

export type EvaluationId = string;
export type ServiceInstanceId = string;
export type ContractVersion = "2.1.0";
export type SubmissionKey = string;
export type UserRunId = string;
export type Appid = string;
export type IndexRevision = string;
export type TargetSeconds = string;
export type WaitingSeconds = string;
export type Comparator = "le" | "lt";
export type ChunkTokens = string | null;
export type DefaultRevision = string | null;
export type DatasetKind = "trace";
export type SourceKind = "user_v2";
export type BaseRunId = string;
export type UserRunId1 = string;
export type CommonName = string;
export type ModelId = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type IndexRevision1 = string;
export type InputSha256 = string;
export type ManifestSha256 = string;
export type SettingsSha256 = string;
export type EncoderIdentity = string;
export type AssetIdentity = string;
/**
 * @minItems 2
 * @maxItems 2
 */
export type FileObservedTimeRangeUtc = [string | null, string | null];
export type RangeKind = "entire_appid_valid_set";
export type CommonName1 = string;
export type ModelId1 = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type Revision = string;
export type ChunkTokens1 = string;
export type ChunkSeconds = string | null;
export type TauReferenceChunkTokens = string;
export type Source = "user_provided";
export type SourceDescription = string;
export type RecordedAt = string;
export type Calibrated = false;
export type ChunkTokensOrigin = "model_default" | "request_override";
export type TauScaled = false;
export type EvaluationId1 = string;
export type ServiceInstanceId1 = string;
export type SubmissionKey1 = string;
export type UserRunId2 = string;
export type Appid1 = string;
export type ScenarioId = string;
export type ScenarioRevision = string;
export type TargetSeconds1 = string;
export type WaitingSeconds1 = string;
export type Comparator1 = "le" | "lt";
export type Scenario = Scenario1 | BatchScenario;
export type ScenarioId1 = string;
export type Revision1 = string;
export type ModelId2 = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type CommonName2 = string;
export type Deployment = string;
export type Source1 = "user_assumption" | "verified_measurement";
export type SourceDescription1 = string;
export type EvidenceSha256 = string | null;
export type MeasurementBoundary = string;
export type WorkloadDescription = string;
export type ThinkingMode = string;
export type MinPromptTokens = string;
export type MaxPromptTokens = string;
export type ChunkTokens2 = string;
export type ChunkSeconds1 = string;
export type OverheadSeconds = string;
export type SampleCount = string;
export type CalibrationNotes = string;
export type TimingModel = "batch_reference_total_noncompute_v1";
export type ScenarioId2 = string;
export type Revision2 = string;
export type ModelId3 = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type CommonName3 = string;
export type Deployment1 = string;
export type Source2 = "user_assumption" | "verified_measurement";
export type SourceDescription2 = string;
export type ChunkTokens3 = string;
export type ChunkSeconds2 = string;
export type MeasurementBoundary1 = "GF dispatch to first token";
export type WorkloadDescription1 = string | null;
export type ThinkingMode1 = string | null;
export type MinPromptTokens1 = string | null;
export type MaxPromptTokens1 = string | null;
export type EvidenceSha2561 = string | null;
export type SampleCount1 = string | null;
export type CalibrationNotes1 = string | null;
export type Status = "reference" | "reference_with_limit" | "no_budget" | "out_of_scope" | "unavailable";
export type Reason = string | null;
export type RequestCount = string;
export type PromptP90 = string | null;
export type AllowedChunks = string | null;
export type ComputableTokens = string | null;
export type Numerator = string;
export type Denominator = string;
export type RequiredHitRate = number | null;
export type Limitations = string[];

export interface AutoEvaluation {
  evaluation_id: EvaluationId;
  service_instance_id: ServiceInstanceId;
  contract_version?: ContractVersion;
  request: AutoEvaluationRequest;
  source: TraceSource;
  defaults: DefaultConfig;
  chunk_tokens_origin: ChunkTokensOrigin;
  tau_scaled?: TauScaled;
  evaluation: Evaluation;
}
export interface AutoEvaluationRequest {
  submission_key: SubmissionKey;
  user_run_id: UserRunId;
  appid: Appid;
  index_revision: IndexRevision;
  target_seconds: TargetSeconds;
  waiting_seconds: WaitingSeconds;
  comparator?: Comparator;
  chunk_tokens?: ChunkTokens;
  default_revision?: DefaultRevision;
}
export interface TraceSource {
  dataset_kind?: DatasetKind;
  source_kind?: SourceKind;
  base_run_id: BaseRunId;
  user_run_id: UserRunId1;
  common_name: CommonName;
  model_id: ModelId;
  index_revision: IndexRevision1;
  input_sha256: InputSha256;
  manifest_sha256: ManifestSha256;
  settings_sha256: SettingsSha256;
  encoder_identity: EncoderIdentity;
  asset_identity: AssetIdentity;
  file_observed_time_range_utc: FileObservedTimeRangeUtc;
  range_kind?: RangeKind;
}
export interface DefaultConfig {
  common_name: CommonName1;
  model_id: ModelId1;
  revision: Revision;
  chunk_tokens: ChunkTokens1;
  chunk_seconds: ChunkSeconds;
  tau_reference_chunk_tokens: TauReferenceChunkTokens;
  source?: Source;
  source_description: SourceDescription;
  recorded_at: RecordedAt;
  calibrated?: Calibrated;
}
export interface Evaluation {
  evaluation_id: EvaluationId1;
  service_instance_id: ServiceInstanceId1;
  request: EvaluationRequest;
  scenario: Scenario;
  status: Status;
  reason: Reason;
  request_count: RequestCount;
  prompt_p90: PromptP90;
  allowed_chunks: AllowedChunks;
  computable_tokens: ComputableTokens;
  required_hit_fraction: Fraction | null;
  required_hit_rate: RequiredHitRate;
  limitations: Limitations;
}
export interface EvaluationRequest {
  submission_key: SubmissionKey1;
  user_run_id: UserRunId2;
  appid: Appid1;
  scenario_id: ScenarioId;
  scenario_revision: ScenarioRevision;
  target_seconds: TargetSeconds1;
  waiting_seconds: WaitingSeconds1;
  comparator: Comparator1;
}
export interface Scenario1 {
  scenario_id: ScenarioId1;
  revision: Revision1;
  model_id: ModelId2;
  common_name: CommonName2;
  deployment: Deployment;
  source: Source1;
  source_description: SourceDescription1;
  evidence_sha256: EvidenceSha256;
  measurement_boundary: MeasurementBoundary;
  workload_description: WorkloadDescription;
  thinking_mode: ThinkingMode;
  min_prompt_tokens: MinPromptTokens;
  max_prompt_tokens: MaxPromptTokens;
  chunk_tokens: ChunkTokens2;
  chunk_seconds: ChunkSeconds1;
  overhead_seconds: OverheadSeconds;
  sample_count: SampleCount;
  calibration_notes: CalibrationNotes;
}
/**
 * Explicit total-noncompute reference; batch budget is assumed per-request progress.
 */
export interface BatchScenario {
  timing_model: TimingModel;
  scenario_id: ScenarioId2;
  revision: Revision2;
  model_id: ModelId3;
  common_name: CommonName3;
  deployment: Deployment1;
  source: Source2;
  source_description: SourceDescription2;
  chunk_tokens: ChunkTokens3;
  chunk_seconds: ChunkSeconds2;
  measurement_boundary?: MeasurementBoundary1;
  workload_description?: WorkloadDescription1;
  thinking_mode?: ThinkingMode1;
  min_prompt_tokens?: MinPromptTokens1;
  max_prompt_tokens?: MaxPromptTokens1;
  evidence_sha256?: EvidenceSha2561;
  sample_count?: SampleCount1;
  calibration_notes?: CalibrationNotes1;
}
export interface Fraction {
  numerator: Numerator;
  denominator: Denominator;
}

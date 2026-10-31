/* Generated contract. */

export type EvaluationId = string;
export type ServiceInstanceId = string;
export type SubmissionKey = string;
export type UserRunId = string;
export type Appid = string;
export type ScenarioId = string;
export type ScenarioRevision = string;
export type TargetSeconds = string;
export type WaitingSeconds = string;
export type Comparator = "le" | "lt";
export type Scenario = Scenario1 | BatchScenario;
export type ScenarioId1 = string;
export type Revision = string;
export type ModelId = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type CommonName = string;
export type Deployment = string;
export type Source = "user_assumption" | "verified_measurement";
export type SourceDescription = string;
export type EvidenceSha256 = string | null;
export type MeasurementBoundary = string;
export type WorkloadDescription = string;
export type ThinkingMode = string;
export type MinPromptTokens = string;
export type MaxPromptTokens = string;
export type ChunkTokens = string;
export type ChunkSeconds = string;
export type OverheadSeconds = string;
export type SampleCount = string;
export type CalibrationNotes = string;
export type TimingModel = "batch_reference_total_noncompute_v1";
export type ScenarioId2 = string;
export type Revision1 = string;
export type ModelId1 = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type CommonName1 = string;
export type Deployment1 = string;
export type Source1 = "user_assumption" | "verified_measurement";
export type SourceDescription1 = string;
export type ChunkTokens1 = string;
export type ChunkSeconds1 = string;
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

export interface Evaluation {
  evaluation_id: EvaluationId;
  service_instance_id: ServiceInstanceId;
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
  submission_key: SubmissionKey;
  user_run_id: UserRunId;
  appid: Appid;
  scenario_id: ScenarioId;
  scenario_revision: ScenarioRevision;
  target_seconds: TargetSeconds;
  waiting_seconds: WaitingSeconds;
  comparator: Comparator;
}
export interface Scenario1 {
  scenario_id: ScenarioId1;
  revision: Revision;
  model_id: ModelId;
  common_name: CommonName;
  deployment: Deployment;
  source: Source;
  source_description: SourceDescription;
  evidence_sha256: EvidenceSha256;
  measurement_boundary: MeasurementBoundary;
  workload_description: WorkloadDescription;
  thinking_mode: ThinkingMode;
  min_prompt_tokens: MinPromptTokens;
  max_prompt_tokens: MaxPromptTokens;
  chunk_tokens: ChunkTokens;
  chunk_seconds: ChunkSeconds;
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
  revision: Revision1;
  model_id: ModelId1;
  common_name: CommonName1;
  deployment: Deployment1;
  source: Source1;
  source_description: SourceDescription1;
  chunk_tokens: ChunkTokens1;
  chunk_seconds: ChunkSeconds1;
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

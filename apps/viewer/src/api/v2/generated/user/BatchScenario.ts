/* Generated contract. */

export type TimingModel = "batch_reference_total_noncompute_v1";
export type ScenarioId = string;
export type Revision = string;
export type ModelId = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type CommonName = string;
export type Deployment = string;
export type Source = "user_assumption" | "verified_measurement";
export type SourceDescription = string;
export type ChunkTokens = string;
export type ChunkSeconds = string;
export type MeasurementBoundary = "GF dispatch to first token";
export type WorkloadDescription = string | null;
export type ThinkingMode = string | null;
export type MinPromptTokens = string | null;
export type MaxPromptTokens = string | null;
export type EvidenceSha256 = string | null;
export type SampleCount = string | null;
export type CalibrationNotes = string | null;

/**
 * Explicit total-noncompute reference; batch budget is assumed per-request progress.
 */
export interface BatchScenario {
  timing_model: TimingModel;
  scenario_id: ScenarioId;
  revision: Revision;
  model_id: ModelId;
  common_name: CommonName;
  deployment: Deployment;
  source: Source;
  source_description: SourceDescription;
  chunk_tokens: ChunkTokens;
  chunk_seconds: ChunkSeconds;
  measurement_boundary?: MeasurementBoundary;
  workload_description?: WorkloadDescription;
  thinking_mode?: ThinkingMode;
  min_prompt_tokens?: MinPromptTokens;
  max_prompt_tokens?: MaxPromptTokens;
  evidence_sha256?: EvidenceSha256;
  sample_count?: SampleCount;
  calibration_notes?: CalibrationNotes;
}

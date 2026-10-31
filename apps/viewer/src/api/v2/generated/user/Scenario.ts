/* Generated contract. */

export type ScenarioId = string;
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

export interface Scenario {
  scenario_id: ScenarioId;
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

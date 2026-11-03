/* Generated from frozen user 2.1.0; do not edit. */

export type ServiceInstanceId = string;
export type ContractVersion = "2.1.0";
export type CommonName = string;
export type ModelId = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type Revision = string;
export type ChunkTokens = string;
export type ChunkSeconds = string | null;
export type TauReferenceChunkTokens = string;
export type Source = "user_provided";
export type SourceDescription = string;
export type RecordedAt = string;
export type Calibrated = false;
export type Configs = DefaultConfig[];

export interface DefaultPage {
  service_instance_id: ServiceInstanceId;
  contract_version?: ContractVersion;
  configs: Configs;
}
export interface DefaultConfig {
  common_name: CommonName;
  model_id: ModelId;
  revision: Revision;
  chunk_tokens: ChunkTokens;
  chunk_seconds: ChunkSeconds;
  tau_reference_chunk_tokens: TauReferenceChunkTokens;
  source?: Source;
  source_description: SourceDescription;
  recorded_at: RecordedAt;
  calibrated?: Calibrated;
}

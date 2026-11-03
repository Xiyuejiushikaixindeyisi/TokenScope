/* Generated from frozen user 2.1.0; do not edit. */

export type ServiceInstanceId = string;
export type ContractVersion = "2.1.0";
export type Snapshot = string;
export type DefaultPolicy = "latest_registered_published_run_per_appid_model_service";
export type Total = string;
export type NextOffset = string | null;
export type DatasetKind = "trace";
export type SourceKind = "user_v2";
export type BaseRunId = string;
export type UserRunId = string;
export type CommonName = string;
export type ModelId = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type IndexRevision = string;
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
export type Appid = string | null;
export type State = "ready" | "empty";
export type RegistrationOrder = string;
export type IsDefault = boolean;
export type RequestCount = string;
export type PromptP90 = string | null;
export type Entries = DiscoveryEntry[];

export interface DiscoveryPage {
  service_instance_id: ServiceInstanceId;
  contract_version?: ContractVersion;
  snapshot: Snapshot;
  default_policy?: DefaultPolicy;
  total: Total;
  next_offset: NextOffset;
  entries: Entries;
}
export interface DiscoveryEntry {
  source: TraceSource;
  appid: Appid;
  state: State;
  registration_order: RegistrationOrder;
  is_default: IsDefault;
  request_count: RequestCount;
  prompt_p90: PromptP90;
}
export interface TraceSource {
  dataset_kind?: DatasetKind;
  source_kind?: SourceKind;
  base_run_id: BaseRunId;
  user_run_id: UserRunId;
  common_name: CommonName;
  model_id: ModelId;
  index_revision: IndexRevision;
  input_sha256: InputSha256;
  manifest_sha256: ManifestSha256;
  settings_sha256: SettingsSha256;
  encoder_identity: EncoderIdentity;
  asset_identity: AssetIdentity;
  file_observed_time_range_utc: FileObservedTimeRangeUtc;
  range_kind?: RangeKind;
}

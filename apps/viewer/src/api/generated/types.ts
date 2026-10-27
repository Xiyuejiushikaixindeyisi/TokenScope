/* Generated from S0 1.0.0. Do not edit; npm run generate. */

/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Settings".
 */
export type Settings = {
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  revision: string;
  block_size: string;
  block_size_unit: "simulation_input_tokens";
  cp_world_size: string;
  mtp: boolean;
  prefix_cache_enabled: boolean;
  hybrid_enabled: boolean;
  cache_mode: "full_block" | "full_block_approximation" | "qwen_hybrid" | "deepseek_hybrid";
  model_aliases: string[];
  encoding_profile: "default" | "thinking_enabled" | "thinking_disabled";
};
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Rule".
 */
export type Rule = {
  appid: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  rule_id: string;
  revision: string;
  metric:
    | "request_count"
    | "ideal_hit_rate"
    | "totals.json_tokens"
    | "totals.prompt_tokens"
    | "totals.ideal_cached_input_tokens"
    | "totals.ideal_compute_input_tokens"
    | "totals.completion_tokens"
    | "quantiles.json_tokens.p50"
    | "quantiles.json_tokens.p80"
    | "quantiles.json_tokens.p90"
    | "quantiles.prompt_tokens.p50"
    | "quantiles.prompt_tokens.p80"
    | "quantiles.prompt_tokens.p90"
    | "quantiles.ideal_compute_input_tokens.p50"
    | "quantiles.ideal_compute_input_tokens.p80"
    | "quantiles.ideal_compute_input_tokens.p90";
  comparator: "lt" | "le" | "gt" | "ge";
  threshold: string | number;
  value_kind: "integer" | "ratio" | "number";
  enabled: boolean;
  route: ("prefix_analysis" | "length_analysis" | "signal_only") | null;
  measurement_signature: string;
};
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "RuleUpdate".
 */
export type RuleUpdate = {
  appid: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  rule_id: string;
  metric:
    | "request_count"
    | "ideal_hit_rate"
    | "totals.json_tokens"
    | "totals.prompt_tokens"
    | "totals.ideal_cached_input_tokens"
    | "totals.ideal_compute_input_tokens"
    | "totals.completion_tokens"
    | "quantiles.json_tokens.p50"
    | "quantiles.json_tokens.p80"
    | "quantiles.json_tokens.p90"
    | "quantiles.prompt_tokens.p50"
    | "quantiles.prompt_tokens.p80"
    | "quantiles.prompt_tokens.p90"
    | "quantiles.ideal_compute_input_tokens.p50"
    | "quantiles.ideal_compute_input_tokens.p80"
    | "quantiles.ideal_compute_input_tokens.p90";
  comparator: "lt" | "le" | "gt" | "ge";
  threshold: string | number;
  value_kind: "integer" | "ratio" | "number";
  enabled: boolean;
  route: ("prefix_analysis" | "length_analysis" | "signal_only") | null;
  measurement_signature: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  expected_revision: string;
};
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "ThresholdState".
 */
export type ThresholdState =
  | {
      status: "unconfigured";
    }
  | {
      rule_id: string;
      revision: string;
      status: "clear" | "needs_review" | "metric_unavailable" | "triggered";
    };
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "EvidencePage".
 */
export type EvidencePage =
  | {
      service_instance_id: string;
      view_schema_version: "1";
      /**
       * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
       */
      offset: string;
      limit: number;
      /**
       * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
       */
      total: string;
      next_offset: string | null;
      run_id: string;
      appid: string;
      model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
      request_ref: RequestRef;
      summary: EvidenceSummary;
      section: "special_ranges";
      items: SpecialRange[];
    }
  | {
      service_instance_id: string;
      view_schema_version: "1";
      /**
       * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
       */
      offset: string;
      limit: number;
      /**
       * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
       */
      total: string;
      next_offset: string | null;
      run_id: string;
      appid: string;
      model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
      request_ref: RequestRef;
      summary: EvidenceSummary;
      section: "source_fields";
      items: SourceField[];
    };
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Signal".
 */
export type Signal = {
  run_id: string;
  appid: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  event_id: string;
  metric:
    | "request_count"
    | "ideal_hit_rate"
    | "totals.json_tokens"
    | "totals.prompt_tokens"
    | "totals.ideal_cached_input_tokens"
    | "totals.ideal_compute_input_tokens"
    | "totals.completion_tokens"
    | "quantiles.json_tokens.p50"
    | "quantiles.json_tokens.p80"
    | "quantiles.json_tokens.p90"
    | "quantiles.prompt_tokens.p50"
    | "quantiles.prompt_tokens.p80"
    | "quantiles.prompt_tokens.p90"
    | "quantiles.ideal_compute_input_tokens.p50"
    | "quantiles.ideal_compute_input_tokens.p80"
    | "quantiles.ideal_compute_input_tokens.p90";
  comparator: "lt" | "le" | "gt" | "ge";
  value_kind: "integer" | "ratio" | "number";
  observed_value: (string | number) | null;
  threshold: string | number;
  rule_id: string;
  revision: string;
  route: "prefix_analysis" | "length_analysis" | "signal_only";
  status: "pending_consumer";
  published_at: string;
};
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Receipt".
 */
export type Receipt = {
  service_instance_id: string;
  view_schema_version: "1";
  submission_key: string;
  run_id: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  status: "queued" | "running" | "completed" | "no_valid_rows" | "failed" | "interrupted";
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  error_code: string | null;
  run_url: string;
};
export type Executable = boolean;
export type Status = "available" | "disabled" | "not_supported";
export type Strategy = string;
export type SimulationSemantics = "full_block_rule" | "chained_approximation";
export type Location = (string | number)[];
export type Message = string;
export type ErrorType = string;
export type Detail = ValidationError[];
export type ModelId = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type Revision = number;
export type BlockSize = number;
export type BlockSizeUnit = "simulation_input_tokens";
export type CpWorldSize = number;
export type Mtp = boolean;
export type PrefixCacheEnabled = boolean;
export type HybridEnabled = boolean;
export type CacheMode = "full_block" | "full_block_approximation" | "qwen_hybrid" | "deepseek_hybrid";
export type ModelAliases = string[];
export type EncodingProfile = string;
export type Appid = string;
export type ModelId1 = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type RuleId = string;
export type ExpectedRevision = number;
export type Metric = string;
export type Comparator = "lt" | "le" | "gt" | "ge";
export type Threshold = number;
export type Enabled = boolean;
export type Route = ("prefix_analysis" | "length_analysis" | "signal_only") | null;
export type MeasurementSignature = string;
export type RunId = string;
export type FileRef = string;
export type ModelId2 = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type Status1 = "queued" | "running" | "completed" | "no_valid_rows" | "failed" | "interrupted";
export type CreatedAt = string;
export type StartedAt = string | null;
export type FinishedAt = string | null;
export type ErrorCode = string | null;
export type Snapshot = {
  [k: string]: unknown;
} | null;
export type Result = {
  [k: string]: unknown;
} | null;
export type FileRef1 = string;
export type ModelId3 = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type BlockSize1 = number | null;
export type CpWorldSize1 = number | null;
export type Mtp1 = boolean | null;
export type PrefixCacheEnabled1 = boolean | null;
export type HybridEnabled1 = boolean | null;
export type CacheMode1 = ("full_block" | "full_block_approximation" | "qwen_hybrid" | "deepseek_hybrid") | null;
export type ModelAliases1 = string[] | null;
export type EncodingProfile1 = string | null;
export type ExpectedRevision1 = number;
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LegacyModelsList".
 */
export type LegacyModelsList = ModelView[];

/**
 * S0 contract 1.0.0, view_schema=1; intended API, not implemented runtime OpenAPI.
 */
export interface ContractTypes {
  DataRange: DataRange;
  Quantiles: Quantiles;
  Capability: Capability;
  Settings: Settings;
  SettingsChanges: SettingsChanges;
  SettingsUpdate: SettingsUpdate;
  ModelSettingsResponse: ModelSettingsResponse;
  Rule: Rule;
  RuleUpdate: RuleUpdate;
  RuleResponse: RuleResponse;
  RulesPage: RulesPage;
  ThresholdState: ThresholdState;
  ThresholdComparison: ThresholdComparison;
  Totals: Totals;
  MeasurementSignatures: MeasurementSignatures;
  GroupMetrics: GroupMetrics;
  HistogramBin: HistogramBin;
  HistogramSummary: HistogramSummary;
  Histogram: Histogram;
  Distributions: Distributions;
  FileQuality: FileQuality;
  GroupQuality: GroupQuality;
  RuntimeIdentity: RuntimeIdentity;
  SnapshotIdentity: SnapshotIdentity;
  Provenance: Provenance;
  SignalSummary: SignalSummary;
  ViewCapabilities: ViewCapabilities;
  ViewLinks: ViewLinks;
  ViewSnapshot: ViewSnapshot;
  CatalogItem: CatalogItem;
  CatalogResponse: CatalogResponse;
  PublishedRun: PublishedRun;
  PublishedRunsResponse: PublishedRunsResponse;
  ResultPublishedEvent: ResultPublishedEvent;
  RunTerminalEvent: RunTerminalEvent;
  ResetEvent: ResetEvent;
  RequestRef: RequestRef;
  RequestFact: RequestFact;
  RequestRow: RequestRow;
  LengthFilter: LengthFilter;
  RequestSort: RequestSort;
  RequestsPage: RequestsPage;
  EvidenceSummary: EvidenceSummary;
  BodyPreview: BodyPreview;
  RequestDetail: RequestDetail;
  SpecialRange: SpecialRange;
  SourceField: SourceField;
  EvidencePage: EvidencePage;
  Signal: Signal;
  SignalsPage: SignalsPage;
  Submission: Submission;
  Receipt: Receipt;
  Error: Error;
  ExportMetadata: ExportMetadata;
  ExportRequest: ExportRequest;
  ExportSummary: ExportSummary;
  LegacyCapability: Capability1;
  LegacyHTTPValidationError: HTTPValidationError;
  LegacyModelSettings: ModelSettings;
  LegacyModelView: ModelView;
  LegacyRuleUpdate: RuleUpdate1;
  LegacyRunState: RunState;
  LegacyRunSubmission: RunSubmission;
  LegacySettingsChanges: SettingsChanges1;
  LegacySettingsUpdate: SettingsUpdate1;
  LegacyValidationError: ValidationError;
  LegacyModelsList: LegacyModelsList;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "DataRange".
 */
export interface DataRange {
  start: string | null;
  end: string | null;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Quantiles".
 */
export interface Quantiles {
  p50: string | null;
  p80: string | null;
  p90: string | null;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Capability".
 */
export interface Capability {
  executable: boolean;
  status: "available" | "disabled" | "not_supported";
  strategy: "full-block-mtp-v1" | "no-cache-v1" | "reserved_hybrid";
  simulation_semantics: "full_block_rule" | "chained_approximation";
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "SettingsChanges".
 */
export interface SettingsChanges {
  block_size?: string;
  cp_world_size?: string;
  mtp?: boolean;
  prefix_cache_enabled?: boolean;
  hybrid_enabled?: boolean;
  cache_mode?: "full_block" | "full_block_approximation" | "qwen_hybrid" | "deepseek_hybrid";
  model_aliases?: string[];
  encoding_profile?: "default" | "thinking_enabled" | "thinking_disabled";
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "SettingsUpdate".
 */
export interface SettingsUpdate {
  expected_revision: string;
  changes: SettingsChanges;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "ModelSettingsResponse".
 */
export interface ModelSettingsResponse {
  service_instance_id: string;
  view_schema_version: "1";
  settings: Settings;
  capability: Capability;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "RuleResponse".
 */
export interface RuleResponse {
  service_instance_id: string;
  view_schema_version: "1";
  rule: Rule;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  rules_revision: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "RulesPage".
 */
export interface RulesPage {
  service_instance_id: string;
  view_schema_version: "1";
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  offset: string;
  limit: number;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  total: string;
  next_offset: string | null;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  rules_revision: string;
  items: Rule[];
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "ThresholdComparison".
 */
export interface ThresholdComparison {
  rule: Rule;
  observed_value: (string | number) | null;
  state: "disabled" | "clear" | "needs_review" | "metric_unavailable" | "triggered";
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Totals".
 */
export interface Totals {
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  json_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  prompt_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  ideal_cached_input_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  ideal_compute_input_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  completion_tokens: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "MeasurementSignatures".
 */
export interface MeasurementSignatures {
  request_count: string;
  ideal_hit_rate: string;
  "totals.json_tokens": string;
  "totals.prompt_tokens": string;
  "totals.ideal_cached_input_tokens": string;
  "totals.ideal_compute_input_tokens": string;
  "totals.completion_tokens": string;
  "quantiles.json_tokens.p50": string;
  "quantiles.json_tokens.p80": string;
  "quantiles.json_tokens.p90": string;
  "quantiles.prompt_tokens.p50": string;
  "quantiles.prompt_tokens.p80": string;
  "quantiles.prompt_tokens.p90": string;
  "quantiles.ideal_compute_input_tokens.p50": string;
  "quantiles.ideal_compute_input_tokens.p80": string;
  "quantiles.ideal_compute_input_tokens.p90": string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "GroupMetrics".
 */
export interface GroupMetrics {
  appid: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  request_count: string;
  totals: Totals;
  quantiles: {
    json_tokens: Quantiles;
    prompt_tokens: Quantiles;
    ideal_compute_input_tokens: Quantiles;
  };
  ideal_hit_rate: number | null;
  json_to_prompt_delta: string;
  /**
   * @minItems 1
   */
  threshold_states: [ThresholdState, ...ThresholdState[]];
  measurement_signatures: MeasurementSignatures;
  capability: Capability;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "HistogramBin".
 */
export interface HistogramBin {
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  lower: string;
  upper: string | null;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  count: string;
  share: number | null;
  overflow: boolean;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "HistogramSummary".
 */
export interface HistogramSummary {
  /**
   * Items: Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  mode_bin_indices: string[];
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  mode_count: string;
  mode_share: number | null;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  under_8k_count: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  overflow_count: string;
  max_length: string | null;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Histogram".
 */
export interface Histogram {
  bin_width: 1000 | 2000 | 5000;
  regular_domain: ["0", "200000"];
  overflow_start: "200000";
  boundary: "left_closed_right_open";
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  sample_count: string;
  quantile_algorithm: "nearest_rank";
  quantiles: Quantiles;
  bins: HistogramBin[];
  summary: HistogramSummary;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Distributions".
 */
export interface Distributions {
  json_tokens: {
    "1000": Histogram;
    "2000": Histogram;
    "5000": Histogram;
  };
  prompt_tokens: {
    "1000": Histogram;
    "2000": Histogram;
    "5000": Histogram;
  };
  ideal_compute_input_tokens: {
    "1000": Histogram;
    "2000": Histogram;
    "5000": Histogram;
  };
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "FileQuality".
 */
export interface FileQuality {
  scope: "file";
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  records_read: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  valid_requests: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  skipped_rows: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  duplicate_hash_id_rows: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "GroupQuality".
 */
export interface GroupQuality {
  scope: "appid";
  coverage: "known_appid_rows_only";
  valid_requests: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  encoding_rejected_rows: string;
  skipped_rows: null;
  duplicate_scope: "appid";
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  duplicate_hash_id_rows_within_group: string;
  unattributed_skips_available_in: "file_quality";
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "RuntimeIdentity".
 */
export interface RuntimeIdentity {
  code_version: string;
  algorithm_version: string;
  asset_identity: string;
  encoder_identity: string;
  asset_revision: string;
  encoding_profile: string;
  profile_json: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "SnapshotIdentity".
 */
export interface SnapshotIdentity {
  service_instance_id: string;
  view_schema_version: "1";
  run_id: string;
  appid: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  publish_seq: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Provenance".
 */
export interface Provenance {
  data_range_utc: DataRange;
  file_data_range_utc: DataRange;
  published_at: string;
  source_label: string;
  input_sha256: string;
  settings: Settings;
  rules: Rule[];
  runtime: RuntimeIdentity;
  simulation_semantics: "full_block_rule" | "chained_approximation";
  metadata_origin: "stored_facts_projection";
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "SignalSummary".
 */
export interface SignalSummary {
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  count: string;
  event_ids_digest: string;
  view_signals_url: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "ViewCapabilities".
 */
export interface ViewCapabilities {
  original_json: boolean;
  light_evidence: boolean;
  requests: boolean;
  export: boolean;
  templated_text: false;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "ViewLinks".
 */
export interface ViewLinks {
  requests: string;
  view_signals: string;
  export_ndjson: string;
  export_csv: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "ViewSnapshot".
 */
export interface ViewSnapshot {
  identity: SnapshotIdentity;
  provenance: Provenance;
  metrics: GroupMetrics;
  distributions: Distributions;
  quality: {
    file_quality: FileQuality;
    group_quality: GroupQuality;
  };
  thresholds: ThresholdComparison[];
  signal_summary: SignalSummary;
  capabilities: ViewCapabilities;
  links: ViewLinks;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "CatalogItem".
 */
export interface CatalogItem {
  appid: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  active_run_id: string;
  publish_seq: string;
  published_at: string;
  data_range_utc: DataRange;
  snapshot_url: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "CatalogResponse".
 */
export interface CatalogResponse {
  service_instance_id: string;
  view_schema_version: "1";
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  offset: string;
  limit: number;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  total: string;
  next_offset: string | null;
  cursor: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  catalog_revision: string;
  items: CatalogItem[];
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "PublishedRun".
 */
export interface PublishedRun {
  run_id: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  publish_seq: string;
  published_at: string;
  status: "completed" | "no_valid_rows";
  file_data_range_utc: DataRange;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  group_count: string;
  input_sha256: string;
  source_label: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "PublishedRunsResponse".
 */
export interface PublishedRunsResponse {
  service_instance_id: string;
  view_schema_version: "1";
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  offset: string;
  limit: number;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  total: string;
  next_offset: string | null;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  catalog_revision: string;
  items: PublishedRun[];
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "ResultPublishedEvent".
 */
export interface ResultPublishedEvent {
  service_instance_id: string;
  view_schema_version: "1";
  run_id: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  publish_seq: string;
  published_at: string;
  status: "completed" | "no_valid_rows";
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "RunTerminalEvent".
 */
export interface RunTerminalEvent {
  service_instance_id: string;
  view_schema_version: "1";
  run_id: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  event_seq: string;
  status: "failed" | "interrupted";
  error_code: string;
  finished_at: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "ResetEvent".
 */
export interface ResetEvent {
  service_instance_id: string;
  view_schema_version: "1";
  reason: "expired" | "future_cursor" | "instance_changed" | "invalid_cursor";
  catalog_url: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "RequestRef".
 */
export interface RequestRef {
  run_id: string;
  source_record_index: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "RequestFact".
 */
export interface RequestFact {
  request_ref: RequestRef;
  hash_id: string;
  time_utc: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  json_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  prompt_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  ideal_cached_input_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  ideal_compute_input_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  completion_tokens: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "RequestRow".
 */
export interface RequestRow {
  request_ref: RequestRef;
  hash_id: string;
  time_utc: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  json_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  prompt_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  ideal_cached_input_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  ideal_compute_input_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  completion_tokens: string;
  position: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LengthFilter".
 */
export interface LengthFilter {
  metric: "json_tokens" | "prompt_tokens" | "ideal_compute_input_tokens";
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  lower: string;
  upper: string | null;
  hash_id: string | null;
  hash_match: "exact" | "prefix";
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "RequestSort".
 */
export interface RequestSort {
  by:
    | "time_ns"
    | "source_record_index"
    | "json_tokens"
    | "prompt_tokens"
    | "ideal_cached_input_tokens"
    | "ideal_compute_input_tokens"
    | "completion_tokens";
  order: "asc" | "desc";
  tie_breaker: "source_record_index_asc";
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "RequestsPage".
 */
export interface RequestsPage {
  service_instance_id: string;
  view_schema_version: "1";
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  offset: string;
  limit: number;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  total: string;
  next_offset: string | null;
  run_id: string;
  appid: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  filter: LengthFilter;
  sort: RequestSort;
  items: RequestRow[];
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "EvidenceSummary".
 */
export interface EvidenceSummary {
  raw_json_sha256: string;
  rendered_sha256: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  rendered_characters: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  rendered_utf8_bytes: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  special_ranges_count: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  source_fields_count: string;
  special_ranges_unit: "utf8_bytes_half_open";
  special_ranges_semantics: string;
  effective_options_json: string;
  source_attribution: "references_only_not_additive_token_contributions";
  source_attribution_status: "partial" | "unknown";
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "BodyPreview".
 */
export interface BodyPreview {
  text: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  total_utf8_bytes: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  preview_utf8_bytes: string;
  truncated: boolean;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "RequestDetail".
 */
export interface RequestDetail {
  service_instance_id: string;
  view_schema_version: "1";
  run_id: string;
  appid: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  request: RequestFact;
  body_preview: BodyPreview;
  evidence_summary: EvidenceSummary;
  capabilities: {
    original_json: boolean;
    light_evidence: boolean;
    templated_text: false;
  };
  links: {
    body: string;
    evidence: string;
  };
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "SpecialRange".
 */
export interface SpecialRange {
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  start: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  end: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "SourceField".
 */
export interface SourceField {
  json_pointer: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  characters: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  utf8_bytes: string;
  sha256: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "SignalsPage".
 */
export interface SignalsPage {
  service_instance_id: string;
  view_schema_version: "1";
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  offset: string;
  limit: number;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  total: string;
  next_offset: string | null;
  run_id: string;
  appid: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  items: Signal[];
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Submission".
 */
export interface Submission {
  file_ref: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  submission_key?: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "Error".
 */
export interface Error {
  error: {
    code: string;
    message: string;
  };
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "ExportMetadata".
 */
export interface ExportMetadata {
  type: "metadata";
  export_schema_version: "1";
  service_instance_id: string;
  view_schema_version: "1";
  run_id: string;
  appid: string;
  model_id: "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
  input_sha256: string;
  settings_sha256: string;
  data_range_utc: DataRange;
  filter: LengthFilter;
  sort: RequestSort;
  export_scope: "group" | "filtered";
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  expected_rows: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "ExportRequest".
 */
export interface ExportRequest {
  type: "request";
  request_ref: RequestRef;
  hash_id: string;
  time_utc: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  json_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  prompt_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  ideal_cached_input_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  ideal_compute_input_tokens: string;
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  completion_tokens: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "ExportSummary".
 */
export interface ExportSummary {
  type: "summary";
  /**
   * Nonnegative decimal integer, never a JSON number. Arithmetic is exact.
   */
  actual_rows: string;
  request_lines_sha256: string;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LegacyCapability".
 */
export interface Capability1 {
  executable: Executable;
  status: Status;
  strategy: Strategy;
  simulation_semantics: SimulationSemantics;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LegacyHTTPValidationError".
 */
export interface HTTPValidationError {
  detail?: Detail;
  [k: string]: unknown;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LegacyValidationError".
 */
export interface ValidationError {
  loc: Location;
  msg: Message;
  type: ErrorType;
  input?: Input;
  ctx?: Context;
  [k: string]: unknown;
}
export interface Input {
  [k: string]: unknown;
}
export interface Context {
  [k: string]: unknown;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LegacyModelSettings".
 */
export interface ModelSettings {
  model_id: ModelId;
  revision?: Revision;
  block_size: BlockSize;
  block_size_unit?: BlockSizeUnit;
  cp_world_size?: CpWorldSize;
  mtp?: Mtp;
  prefix_cache_enabled?: PrefixCacheEnabled;
  hybrid_enabled?: HybridEnabled;
  cache_mode: CacheMode;
  model_aliases?: ModelAliases;
  encoding_profile?: EncodingProfile;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LegacyModelView".
 */
export interface ModelView {
  settings: ModelSettings;
  capability: Capability1;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LegacyRuleUpdate".
 */
export interface RuleUpdate1 {
  appid: Appid;
  model_id: ModelId1;
  rule_id: RuleId;
  expected_revision: ExpectedRevision;
  metric: Metric;
  comparator: Comparator;
  threshold: Threshold;
  enabled?: Enabled;
  route?: Route;
  measurement_signature: MeasurementSignature;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LegacyRunState".
 */
export interface RunState {
  run_id: RunId;
  file_ref: FileRef;
  model_id: ModelId2;
  status: Status1;
  created_at: CreatedAt;
  started_at?: StartedAt;
  finished_at?: FinishedAt;
  settings?: ModelSettings | null;
  error_code?: ErrorCode;
  snapshot?: Snapshot;
  result?: Result;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LegacyRunSubmission".
 */
export interface RunSubmission {
  file_ref: FileRef1;
  model_id: ModelId3;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LegacySettingsChanges".
 */
export interface SettingsChanges1 {
  block_size?: BlockSize1;
  cp_world_size?: CpWorldSize1;
  mtp?: Mtp1;
  prefix_cache_enabled?: PrefixCacheEnabled1;
  hybrid_enabled?: HybridEnabled1;
  cache_mode?: CacheMode1;
  model_aliases?: ModelAliases1;
  encoding_profile?: EncodingProfile1;
}
/**
 * This interface was referenced by `ContractTypes`'s JSON-Schema
 * via the `definition` "LegacySettingsUpdate".
 */
export interface SettingsUpdate1 {
  expected_revision: ExpectedRevision1;
  changes: SettingsChanges1;
}

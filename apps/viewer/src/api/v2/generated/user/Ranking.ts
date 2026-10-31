/* Generated contract. */

export type ServiceInstanceId = string;
export type UserRunId = string;
export type CommonName = string;
export type IndexRevision = string;
export type BinWidth = 1000 | 2000 | 5000;
export type Total = string;
export type NextOffset = string | null;
export type ReadRows = string;
export type ValidRows = string;
export type SkippedRows = string;
export type Appid = string;
export type RequestCount = string;
export type TotalPromptTokens = string;
export type TotalIdealCachedTokens = string;
export type TotalIdealComputeTokens = string;
export type IdealHitRate = number | null;
export type PromptP90 = string;
export type Numerator = string;
export type Denominator = string;
export type Lower = string;
export type Upper = string;
export type Count = string;
export type SumComputeTokens = string;
export type Share = number;
export type TieCount = string;
export type Rows = RankRow[];

export interface Ranking {
  service_instance_id: ServiceInstanceId;
  user_run_id: UserRunId;
  common_name: CommonName;
  index_revision: IndexRevision;
  bin_width: BinWidth;
  total: Total;
  next_offset: NextOffset;
  file_quality: Quality;
  rows: Rows;
}
export interface Quality {
  read_rows: ReadRows;
  valid_rows: ValidRows;
  skipped_rows: SkippedRows;
}
export interface RankRow {
  appid: Appid;
  request_count: RequestCount;
  total_prompt_tokens: TotalPromptTokens;
  total_ideal_cached_tokens: TotalIdealCachedTokens;
  total_ideal_compute_tokens: TotalIdealComputeTokens;
  ideal_hit_rate: IdealHitRate;
  prompt_p90: PromptP90;
  typical_compute_tokens: Fraction;
  representative_bin: ModeBin;
  tie_count: TieCount;
}
export interface Fraction {
  numerator: Numerator;
  denominator: Denominator;
}
export interface ModeBin {
  lower: Lower;
  upper: Upper;
  count: Count;
  sum_compute_tokens: SumComputeTokens;
  share: Share;
  mean: Fraction;
}

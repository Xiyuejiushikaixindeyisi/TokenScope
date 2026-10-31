/* Generated contract. */

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

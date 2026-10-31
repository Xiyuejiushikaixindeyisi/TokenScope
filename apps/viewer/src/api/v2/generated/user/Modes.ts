/* Generated contract. */

export type UserRunId = string;
export type Appid = string;
export type IndexRevision = string;
export type BinWidth = 1000 | 2000 | 5000;
export type Total = string;
export type NextOffset = string | null;
export type Lower = string;
export type Upper = string;
export type Count = string;
export type SumComputeTokens = string;
export type Share = number;
export type Numerator = string;
export type Denominator = string;
export type Bins = ModeBin[];

export interface Modes {
  user_run_id: UserRunId;
  appid: Appid;
  index_revision: IndexRevision;
  bin_width: BinWidth;
  total: Total;
  next_offset: NextOffset;
  bins: Bins;
}
export interface ModeBin {
  lower: Lower;
  upper: Upper;
  count: Count;
  sum_compute_tokens: SumComputeTokens;
  share: Share;
  mean: Fraction;
}
export interface Fraction {
  numerator: Numerator;
  denominator: Denominator;
}

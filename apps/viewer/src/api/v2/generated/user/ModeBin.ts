/* Generated contract. */

export type Lower = string;
export type Upper = string;
export type Count = string;
export type SumComputeTokens = string;
export type Share = number;
export type Numerator = string;
export type Denominator = string;

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

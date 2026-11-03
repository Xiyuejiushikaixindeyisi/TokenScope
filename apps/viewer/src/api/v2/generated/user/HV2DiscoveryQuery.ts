/* Generated from frozen user 2.1.0; do not edit. */

export type Appid = string | null;
export type CommonName = string | null;
export type ModelId = ("GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731") | null;
export type UserRunId = string | null;
export type Snapshot = string | null;
export type Offset = string;
export type Limit = number;

export interface DiscoveryQuery {
  appid?: Appid;
  common_name?: CommonName;
  model_id?: ModelId;
  user_run_id?: UserRunId;
  snapshot?: Snapshot;
  offset?: Offset;
  limit?: Limit;
}

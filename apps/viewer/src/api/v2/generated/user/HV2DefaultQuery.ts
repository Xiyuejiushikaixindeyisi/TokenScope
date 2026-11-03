/* Generated from frozen user 2.1.0; do not edit. */

export type CommonName = string | null;
export type ModelId = ("GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731") | null;
export type Revision = string | null;

export interface DefaultQuery {
  common_name?: CommonName;
  model_id?: ModelId;
  revision?: Revision;
}

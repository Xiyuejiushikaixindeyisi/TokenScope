/* Generated contract. */

export type ServiceInstanceId = string;
export type UserRunId = string;
export type BaseRunId = string | null;
export type CommonName = string;
export type ModelId = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type UserState = "accepted" | "base_pending" | "indexing" | "ready" | "empty" | "failed" | "interrupted";
export type IndexRevision = string | null;
export type ErrorCode = string | null;

export interface Receipt {
  service_instance_id: ServiceInstanceId;
  user_run_id: UserRunId;
  base_run_id: BaseRunId;
  common_name: CommonName;
  model_id: ModelId;
  state: UserState;
  index_revision: IndexRevision;
  error_code: ErrorCode;
}

/* Generated from frozen user 2.1.0; do not edit. */

export type SubmissionKey = string;
export type UserRunId = string;
export type Appid = string;
export type IndexRevision = string;
export type TargetSeconds = string;
export type WaitingSeconds = string;
export type Comparator = "le" | "lt";
export type ChunkTokens = string | null;
export type DefaultRevision = string | null;

export interface AutoEvaluationRequest {
  submission_key: SubmissionKey;
  user_run_id: UserRunId;
  appid: Appid;
  index_revision: IndexRevision;
  target_seconds: TargetSeconds;
  waiting_seconds: WaitingSeconds;
  comparator?: Comparator;
  chunk_tokens?: ChunkTokens;
  default_revision?: DefaultRevision;
}

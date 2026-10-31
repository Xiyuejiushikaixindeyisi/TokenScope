/* Generated contract. */

export type SubmissionKey = string;
export type UserRunId = string;
export type Appid = string;
export type ScenarioId = string;
export type ScenarioRevision = string;
export type TargetSeconds = string;
export type WaitingSeconds = string;
export type Comparator = "le" | "lt";

export interface EvaluationRequest {
  submission_key: SubmissionKey;
  user_run_id: UserRunId;
  appid: Appid;
  scenario_id: ScenarioId;
  scenario_revision: ScenarioRevision;
  target_seconds: TargetSeconds;
  waiting_seconds: WaitingSeconds;
  comparator: Comparator;
}

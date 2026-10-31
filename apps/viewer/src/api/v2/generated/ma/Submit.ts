/* Generated contract. */

export type ModelId = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";
export type ModelStandardName = string;
export type NowEnd = string;
export type NowFileRef = string;
export type NowStart = string;
export type PreFileRef = string;
export type PreStart = string;
export type SourceTimezone = "UTC";
export type SubmissionKey = string;

export interface Submit {
  model_id: ModelId;
  model_standard_name: ModelStandardName;
  now_end: NowEnd;
  now_file_ref: NowFileRef;
  now_start: NowStart;
  pre_file_ref: PreFileRef;
  pre_start: PreStart;
  source_timezone?: SourceTimezone;
  submission_key: SubmissionKey;
}

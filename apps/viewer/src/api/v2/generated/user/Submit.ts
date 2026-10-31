/* Generated contract. */

export type SubmissionKey = string;
export type FileRef = string;
export type CommonName = string;
export type ModelId = "GLM-5.2" | "Qwen3.6-27B" | "DeepSeek-V4-Flash-0731";

export interface Submit {
  submission_key: SubmissionKey;
  file_ref: FileRef;
  common_name: CommonName;
  model_id: ModelId;
}

/* Generated contract. */

export type Code = string;
export type Field = string;
export type PhysicalLineEnd = string;
export type PhysicalLineStart = string;
export type Role = "pre" | "now";
export type SourceRecordIndex = string;
export type Issues = QualityIssue[];
export type MaRunId = string;
export type NextOffset = string | null;
export type ServiceInstanceId = string;
export type Total = string;

export interface QualityPage {
  issues: Issues;
  ma_run_id: MaRunId;
  next_offset: NextOffset;
  service_instance_id: ServiceInstanceId;
  total: Total;
}
export interface QualityIssue {
  code: Code;
  field: Field;
  physical_line_end: PhysicalLineEnd;
  physical_line_start: PhysicalLineStart;
  role: Role;
  source_record_index: SourceRecordIndex;
}

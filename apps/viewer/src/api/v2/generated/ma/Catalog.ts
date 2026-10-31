/* Generated contract. */

export type CatalogRevision = string;
export type EmptyScopeReason = ("empty_file" | "all_unassigned") | null;
export type InstanceUuids = string[];
export type MaRunId = string;
export type ModelStandardName = string;
export type NowEnd = string;
export type NowStart = string;
export type Entries = CatalogEntry[];
export type NextOffset = string | null;
export type ServiceInstanceId = string;
export type Total = string;

export interface Catalog {
  catalog_revision: CatalogRevision;
  entries: Entries;
  next_offset: NextOffset;
  service_instance_id: ServiceInstanceId;
  total: Total;
}
export interface CatalogEntry {
  empty_scope_reason: EmptyScopeReason;
  instance_uuids: InstanceUuids;
  ma_run_id: MaRunId;
  model_standard_name: ModelStandardName;
  now_end: NowEnd;
  now_start: NowStart;
}

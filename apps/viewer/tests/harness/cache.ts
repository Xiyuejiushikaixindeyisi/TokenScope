import { SnapshotCache, checkPacket } from '../../src/storage/snapshot-cache';
import { openSnapshotDb, diskGet, diskPut } from '../../src/storage/db';
import { scopeKey } from '../../src/domain/identity';
import type { Scope } from '../../src/domain/identity';
const api = { SnapshotCache, checkPacket, openSnapshotDb, diskGet, diskPut, scopeKey };
Object.assign(window, { cacheTest: api });
export type CacheTest = typeof api;
export type { Scope };

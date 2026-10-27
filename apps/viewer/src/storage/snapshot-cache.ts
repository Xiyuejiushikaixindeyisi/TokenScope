import { validateDto } from '../api/validate';
import type { Dto } from '../api/types';
import type { Scope } from '../domain/identity';
import { scopeKey } from '../domain/identity';
import { openSnapshotDb, diskGet, diskPut } from './db';
export interface SnapshotPacket { snapshot: Dto<'ViewSnapshot'>; raw: string; etag: string }
export async function checkPacket(raw: string, etag: string, scope: Scope): Promise<SnapshotPacket> {
  const bytes = new TextEncoder().encode(raw);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  const actual = '"' + [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('') + '"';
  if (actual !== etag) throw new Error('SNAPSHOT_DIGEST_MISMATCH');
  return { snapshot: validateDto('ViewSnapshot', JSON.parse(raw), scope), raw, etag };
}
export class SnapshotCache {
  private readonly memory = new Map<string, { packet: SnapshotPacket; bytes: number }>();
  private database: Promise<IDBDatabase> | undefined;
  private protectedKey: string | null = null;
  private persistent = true;
  constructor(private readonly warn: (message: string) => void, private readonly memoryBudget = 24 * 1024 * 1024, private readonly diskBudget = 64 * 1024 * 1024, private readonly open = openSnapshotDb) {}
  async last(): Promise<SnapshotPacket | undefined> {
    try {
      const raw = localStorage.getItem('tokenscope.viewer.last-snapshot.v1');
      if (!raw) return;
      const scope = JSON.parse(raw) as Scope;
      if (scope.view_schema_version !== '1' || !scope.service_instance_id || !scope.run_id || !scope.appid || !scope.model_id) return;
      return await this.get(scope);
    } catch { return; }
  }
  rememberLast(scope: Scope) {
    try { localStorage.setItem('tokenscope.viewer.last-snapshot.v1', JSON.stringify(scope)); }
    catch { this.warn('浏览器无法保存上次选择；刷新后需重新选择范围。'); }
  }
  protect(key: string | null) { this.protectedKey = key; this.trim(); }
  private trim() {
    let total = [...this.memory.values()].reduce((n, item) => n + item.bytes, 0);
    for (const [key, item] of this.memory) {
      if (total <= this.memoryBudget) break;
      if (key === this.protectedKey || key === [...this.memory.keys()].at(-1)) continue;
      this.memory.delete(key); total -= item.bytes;
    }
  }
  private remember(key: string, packet: SnapshotPacket) {
    this.memory.delete(key); this.memory.set(key, { packet, bytes: new TextEncoder().encode(packet.raw).length }); this.trim();
  }
  private db() { return this.database ??= this.open(); }
  private degrade() { this.persistent = false; this.warn('本地缓存不可用，当前结果仍可查看；刷新后需重新读取。'); }
  async get(scope: Scope): Promise<SnapshotPacket | undefined> {
    const key = scopeKey(scope), cached = this.memory.get(key);
    if (cached) { this.memory.delete(key); this.memory.set(key, cached); return cached.packet; }
    if (!this.persistent) return;
    try {
      const db = await this.db(), record = await diskGet(db, key);
      if (!record) return;
      const packet = await checkPacket(record.raw, record.etag, scope);
      this.remember(key, packet);
      await diskPut(db, { ...record, touched: Date.now() }, this.diskBudget, this.protectedKey);
      return packet;
    } catch { this.degrade(); return; }
  }
  async put(scope: Scope, packet: SnapshotPacket) {
    const key = scopeKey(scope); this.remember(key, packet);
    if (!this.persistent) return;
    try { await diskPut(await this.db(), { key, raw: packet.raw, etag: packet.etag, bytes: new TextEncoder().encode(packet.raw).length, touched: Date.now() }, this.diskBudget, this.protectedKey); }
    catch { this.degrade(); }
  }
}

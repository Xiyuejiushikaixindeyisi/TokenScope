import { apiPath, ApiError } from '../api/client';
import { singleFlight } from '../api/query-cache';
import type { Dto } from '../api/types';
import { scopeKey } from '../domain/identity';
import type { Scope } from '../domain/identity';
import { checkPacket } from '../storage/snapshot-cache';
import type { SnapshotCache, SnapshotPacket } from '../storage/snapshot-cache';
import type { ViewStore } from './view-store';
export async function fetchSnapshot(scope: Scope): Promise<SnapshotPacket> {
  const response = await fetch(apiPath(`/analysis-runs/${encodeURIComponent(scope.run_id!)}/view-snapshot`, { appid: scope.appid }), { redirect: 'error', credentials: 'same-origin' });
  if (!response.ok) throw new ApiError(response.status, 'SNAPSHOT_UNAVAILABLE', '完整结果暂不可读');
  if (!response.headers.get('content-type')?.includes('application/json')) throw new Error('INVALID_CONTENT_TYPE');
  const raw = new TextDecoder('utf-8', { fatal: true }).decode(await response.arrayBuffer());
  return checkPacket(raw, response.headers.get('etag') ?? '', scope);
}
export class SnapshotCoordinator {
  private epoch = 0;
  private readonly flight = singleFlight<SnapshotPacket>();
  constructor(readonly store: ViewStore, private readonly cache: Pick<SnapshotCache, 'get' | 'put' | 'protect' | 'last' | 'rememberLast'>, private readonly fetchPacket = fetchSnapshot) {}
  async restore() {
    const epoch = this.epoch;
    const packet = await this.cache.last();
    if (epoch !== this.epoch || this.store.getSnapshot().catalog || !packet) return;
    const { appid, model_id } = packet.snapshot.identity;
    this.store.update({ selection: { appid, model_id }, snapshot: packet.snapshot, cacheWarning: '上次缓存结果，待确认连接。' });
  }
  catalog(catalog: Dto<'CatalogResponse'>) {
    const old = this.store.getSnapshot();
    const priorInstance = old.catalog?.service_instance_id ?? old.snapshot?.identity.service_instance_id;
    const changed = priorInstance !== undefined && priorInstance !== catalog.service_instance_id;
    if (changed) { this.epoch++; this.cache.protect(null); this.store.update({ snapshot: null, pending: null, pinned: false }); }
    this.store.update({ catalog, ...(old.cacheWarning === '上次缓存结果，待确认连接。' ? { cacheWarning: null } : {}) });
    const selection = old.selection ?? (catalog.items[0] ? { appid: catalog.items[0].appid, model_id: catalog.items[0].model_id } : null);
    if (selection) void this.select(selection.appid, selection.model_id, true);
  }
  async select(appid: string, model_id: string, preservePin = false, historyRun?: string) {
    const epoch = ++this.epoch;
    const state = this.store.getSnapshot();
    const same = state.selection?.appid === appid && state.selection.model_id === model_id;
    if (!same) this.cache.protect(null);
    this.store.update({ selection: { appid, model_id }, ...(!same ? { snapshot: null, pending: null } : {}), pinned: historyRun !== undefined || (same && preservePin && state.pinned), loading: true, error: null });
    const catalog = state.catalog;
    const item = catalog?.items.find(i => i.appid === appid && i.model_id === model_id);
    if (!catalog || (!item && !historyRun)) { this.store.update({ snapshot: null, pending: null, loading: false }); return; }
    const scope: Scope = { service_instance_id: catalog.service_instance_id, view_schema_version: '1', run_id: historyRun ?? item!.active_run_id, appid, model_id };
    const key = scopeKey(scope);
    try {
      const packet = await this.flight(key, async () => {
        const cached = await this.cache.get(scope);
        if (cached) return cached;
        const fresh = await this.fetchPacket(scope);
        await this.cache.put(scope, fresh); return fresh;
      });
      if (epoch !== this.epoch) return;
      const current = this.store.getSnapshot();
      if (current.pinned && !historyRun && current.snapshot && current.snapshot.identity.run_id !== packet.snapshot.identity.run_id) {
        this.store.update({ pending: packet.snapshot, loading: false });
      } else {
        this.cache.protect(key); this.cache.rememberLast(scope);
        this.store.update({ snapshot: packet.snapshot, pending: null, loading: false });
      }
    } catch { if (epoch === this.epoch) this.store.update({ loading: false, error: '完整结果读取失败；保留当前范围已读取的结果，可手动重试。' }); }
  }
  pin(pinned: boolean) { this.store.update({ pinned }); }
  acceptPending() {
    const pending = this.store.getSnapshot().pending;
    if (pending) { this.cache.protect(scopeKey(pending.identity)); this.cache.rememberLast(pending.identity); this.store.update({ snapshot: pending, pending: null, pinned: false }); }
  }
  stop() { this.epoch++; }
}

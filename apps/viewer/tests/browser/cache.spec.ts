import { readFileSync } from 'node:fs';
import { test, expect } from '@playwright/test';
import type { CacheTest } from '../harness/cache';
import type { Scope } from '../../src/domain/identity';
declare global { interface Window { cacheTest: CacheTest } }
const fixture = JSON.parse(readFileSync(new URL('../../../../docs/contracts/examples/monitoring-view-s0/snapshot-normal.json', import.meta.url), 'utf8'));
test('real IndexedDB persists exact snapshot across reload; corrupt/rejected stores degrade safely', async ({ page }) => {
  await page.goto('/tests/harness/cache.html'); await page.waitForFunction(() => !!window.cacheTest);
  const identity: Scope = fixture.identity;
  const first = await page.evaluate(async snapshot => {
    const { SnapshotCache, checkPacket } = window.cacheTest;
    const raw = JSON.stringify(snapshot), hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(raw));
    const etag = '"' + [...new Uint8Array(hash)].map(b => b.toString(16).padStart(2, '0')).join('') + '"';
    const packet = await checkPacket(raw, etag, snapshot.identity);
    const warnings: string[] = []; const cache = new SnapshotCache(x => warnings.push(x));
    await cache.put(snapshot.identity, packet); cache.rememberLast(snapshot.identity);
    return { raw, etag, warnings };
  }, fixture);
  expect(first.warnings).toEqual([]);
  await page.reload(); await page.waitForFunction(() => !!window.cacheTest);
  const restored = await page.evaluate(async () => (await new window.cacheTest.SnapshotCache(() => {}).last())?.raw);
  expect(restored).toBe(first.raw);
  const degradation = await page.evaluate(async ({ identity, raw, etag }) => {
    const { SnapshotCache, checkPacket, openSnapshotDb, diskPut, scopeKey } = window.cacheTest;
    const packet = await checkPacket(raw, etag, identity);
    const warnings: string[] = [];
    const denied = new SnapshotCache(x => warnings.push(x), 1024, 1024, () => Promise.reject(new DOMException('Denied', 'SecurityError')));
    await denied.put(identity, packet);
    const retained = (await denied.get(identity))?.raw === raw;
    const db = await openSnapshotDb();
    await diskPut(db, { key: scopeKey(identity), raw: '{}', etag, bytes: 2, touched: Date.now() }, 1000000, null);
    const corrupt = await new SnapshotCache(x => warnings.push(x)).get(identity);
    db.close();
    return { retained, corrupt: corrupt === undefined, warnings: warnings.length };
  }, { identity, raw: first.raw, etag: first.etag });
  expect(degradation).toEqual({ retained: true, corrupt: true, warnings: 2 });
});
test('LRU eviction uses real browser transactions; independent tab restore', async ({ page, context }) => {
  await page.goto('/tests/harness/cache.html'); await page.waitForFunction(() => !!window.cacheTest);
  const result = await page.evaluate(async () => {
    const { openSnapshotDb, diskPut, diskGet } = window.cacheTest;
    const db = await openSnapshotDb();
    const tx = db.transaction('snapshots', 'readwrite'); tx.objectStore('snapshots').clear();
    await new Promise<void>((resolve, reject) => { tx.oncomplete = () => resolve(); tx.onabort = () => reject(tx.error); });
    await diskPut(db, { key: 'old', raw: '', etag: '', bytes: 10, touched: 1 }, 20, null);
    await diskPut(db, { key: 'current', raw: '', etag: '', bytes: 10, touched: 2 }, 20, 'current');
    await diskPut(db, { key: 'new', raw: '', etag: '', bytes: 10, touched: 3 }, 20, 'current');
    const values = [!!await diskGet(db, 'old'), !!await diskGet(db, 'current'), !!await diskGet(db, 'new')]; db.close(); return values;
  });
  expect(result).toEqual([false, true, true]);
  const second = await context.newPage(); await second.goto('/tests/harness/cache.html'); await second.waitForFunction(() => !!window.cacheTest);
  expect(await second.evaluate(async () => { const db = await window.cacheTest.openSnapshotDb(); const value = await window.cacheTest.diskGet(db, 'current'); db.close(); return !!value; })).toBe(true);
});

test('quota write failure retains memory result and does not touch receipts', async ({ page }) => {
  await page.goto('/tests/harness/cache.html'); await page.waitForFunction(() => !!window.cacheTest);
  const result = await page.evaluate(async snapshot => {
    const { SnapshotCache, checkPacket } = window.cacheTest;
    const raw = JSON.stringify(snapshot); const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(raw));
    const etag = '"' + [...new Uint8Array(digest)].map(v => v.toString(16).padStart(2, '0')).join('') + '"';
    const packet = await checkPacket(raw, etag, snapshot.identity);
    const original = IDBObjectStore.prototype.put;
    IDBObjectStore.prototype.put = function () { throw new DOMException('synthetic disk quota', 'QuotaExceededError'); };
    const warnings: string[] = []; const cache = new SnapshotCache(m => warnings.push(m));
    try { await cache.put(snapshot.identity, packet); }
    finally { IDBObjectStore.prototype.put = original; }
    return { retained: (await cache.get(snapshot.identity))?.raw === raw, warnings: warnings.length, databases: (await indexedDB.databases()).map(db => db.name) };
  }, fixture);
  expect(result.retained).toBe(true); expect(result.warnings).toBe(1);
  expect(result.databases).toEqual(['tokenscope-viewer-snapshots-v1']);
});
test('incompatible local store schema degrades without deleting any database', async ({ page }) => {
  await page.goto('/tests/harness/cache.html'); await page.waitForFunction(() => !!window.cacheTest);
  const result = await page.evaluate(async () => {
    await new Promise<void>((resolve, reject) => { const request = indexedDB.open('tokenscope-viewer-snapshots-v1', 1); request.onsuccess = () => { request.result.close(); resolve(); }; request.onerror = () => reject(request.error); });
    try { await window.cacheTest.openSnapshotDb(); return 'unexpected'; } catch (error) { return (error as Error).message; }
  });
  expect(result).toBe('CACHE_SCHEMA_INVALID');
});

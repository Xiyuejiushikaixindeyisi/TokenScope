// @vitest-environment node
import { readFileSync } from 'node:fs';
import { it, expect, vi } from 'vitest';
import { validateDto } from '../../src/api/validate';
import { ViewStore } from '../../src/state/view-store';
import { SnapshotCoordinator } from '../../src/state/snapshot-coordinator';
import { checkPacket } from '../../src/storage/snapshot-cache';
import { createHash } from 'node:crypto';
const file = (name: string) => JSON.parse(readFileSync(new URL(`../../../../docs/contracts/examples/monitoring-view-s0/${name}.json`, import.meta.url), 'utf8'));
const base = () => validateDto('ViewSnapshot', file('snapshot-normal'));
const cat = () => validateDto('CatalogResponse', file('catalog-normal'));
const packet = (appid = 'synthetic-app-1', run = cat().items[0]!.active_run_id) => { const snapshot = base(); snapshot.identity.appid = appid; snapshot.identity.run_id = run; return { snapshot, raw: '', etag: '' }; };
const cache = () => ({ get: vi.fn().mockResolvedValue(undefined), put: vi.fn().mockResolvedValue(undefined), protect: vi.fn(), last: vi.fn().mockResolvedValue(undefined), rememberLast: vi.fn() });
const tick = () => new Promise(resolve => setTimeout(resolve, 0));
it('deduplicates same key; late A never replaces B, failed B never displays A', async () => {
  const store = new ViewStore(), disk = cache();
  let release!: (value: ReturnType<typeof packet>) => void;
  const read = vi.fn().mockImplementationOnce(() => new Promise(resolve => { release = resolve; })).mockRejectedValueOnce(new Error('B unavailable'));
  const coordinator = new SnapshotCoordinator(store, disk, read);
  const catalog = cat(); catalog.items.push({ ...catalog.items[0]!, appid: 'B' }); catalog.total = '2';
  coordinator.catalog(catalog); const duplicate = coordinator.select('synthetic-app-1', 'GLM-5.2'); await tick(); expect(read).toHaveBeenCalledTimes(1);
  await coordinator.select('B', 'GLM-5.2'); release(packet()); await duplicate; await tick();
  expect(store.getSnapshot().selection?.appid).toBe('B'); expect(store.getSnapshot().snapshot).toBeNull(); expect(store.getSnapshot().error).not.toBeNull();
});
it('pinned view holds complete old result; accepts complete pending version atomically', async () => {
  const store = new ViewStore(), disk = cache(); const read = vi.fn().mockResolvedValueOnce(packet()).mockResolvedValueOnce(packet('synthetic-app-1', '33333333-3333-4333-8333-333333333333'));
  const coordinator = new SnapshotCoordinator(store, disk, read); coordinator.catalog(cat()); await tick(); coordinator.pin(true);
  const newer = cat(); newer.items[0]!.active_run_id = '33333333-3333-4333-8333-333333333333'; coordinator.catalog(newer); await tick();
  expect(store.getSnapshot().snapshot!.identity.run_id).toBe(cat().items[0]!.active_run_id);
  expect(store.getSnapshot().pending!.identity.run_id).toBe(newer.items[0]!.active_run_id);
  coordinator.acceptPending(); expect(store.getSnapshot().snapshot!.identity.run_id).toBe(newer.items[0]!.active_run_id); expect(store.getSnapshot().pending).toBeNull();
});
it('new instance withdraws old offline snapshot before fetching', async () => {
  const store = new ViewStore(), disk = cache(); disk.last.mockResolvedValue(packet());
  const coordinator = new SnapshotCoordinator(store, disk, vi.fn().mockRejectedValue(new Error('offline')));
  await coordinator.restore(); expect(store.getSnapshot().snapshot).not.toBeNull();
  const newer = cat(); newer.service_instance_id = '44444444-4444-4444-8444-444444444444'; coordinator.catalog(newer);
  expect(store.getSnapshot().snapshot).toBeNull(); await tick();
});
it('validates raw immutable snapshot digest before acceptance', async () => {
  const raw = JSON.stringify(base()); const etag = '"' + createHash('sha256').update(raw).digest('hex') + '"';
  expect((await checkPacket(raw, etag, base().identity)).snapshot).toEqual(base());
  await expect(checkPacket(raw + ' ', etag, base().identity)).rejects.toThrow('SNAPSHOT_DIGEST');
});

it('same-version navigation reuses cached package and all three widths without fetching', async () => {
  const store = new ViewStore(), disk = cache(); const value = packet();
  const read = vi.fn().mockResolvedValue(value);
  disk.put.mockImplementation(async () => { disk.get.mockResolvedValue(value); });
  const coordinator = new SnapshotCoordinator(store, disk, read); coordinator.catalog(cat()); await tick();
  await coordinator.select('synthetic-app-1', 'GLM-5.2');
  for (const width of ['1000', '2000', '5000'] as const) expect(store.getSnapshot().snapshot!.distributions.prompt_tokens[width]).toBeDefined();
  expect(read).toHaveBeenCalledTimes(1);
});
it('failed next version preserves complete old snapshot only in same scope', async () => {
  const store = new ViewStore(), disk = cache(); const value = packet();
  const read = vi.fn().mockResolvedValueOnce(value).mockRejectedValueOnce(new Error('bad digest'));
  const coordinator = new SnapshotCoordinator(store, disk, read); coordinator.catalog(cat()); await tick();
  const newer = cat(); newer.items[0]!.active_run_id = '33333333-3333-4333-8333-333333333333'; coordinator.catalog(newer); await tick();
  expect(store.getSnapshot().snapshot).toBe(value.snapshot); expect(store.getSnapshot().error).not.toBeNull();
});

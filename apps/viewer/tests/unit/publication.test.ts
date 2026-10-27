// @vitest-environment node
import { readFileSync } from 'node:fs';
import { it, expect, vi } from 'vitest';
import { PublicationClient } from '../../src/state/publication-client';
import type { EventStream } from '../../src/state/publication-client';
import { loadCatalog } from '../../src/state/catalog';
import { ApiError } from '../../src/api/client';
import type { getJson } from '../../src/api/client';
import { validateDto } from '../../src/api/validate';
const catalog = () => validateDto('CatalogResponse', JSON.parse(readFileSync(new URL('../../../../docs/contracts/examples/monitoring-view-s0/catalog-normal.json', import.meta.url), 'utf8')));
const tick = () => new Promise(resolve => setTimeout(resolve, 0));
function stream() {
  const target = new EventTarget();
  const close = vi.fn();
  const send = (type: string, data?: unknown, lastEventId = '') => target.dispatchEvent(new MessageEvent(type, { data: data === undefined ? '' : JSON.stringify(data), lastEventId }));
  return { addEventListener: target.addEventListener.bind(target), close, send };
}
it('subscribes after catalog cursor, ignores duplicate/late/heartbeat and exposes each open for R1', async () => {
  const s = stream(), read = vi.fn().mockResolvedValue(catalog()), ready = vi.fn(), terminal = vi.fn();
  const connect = vi.fn<(url: string) => EventStream>().mockReturnValue(s);
  const client = new PublicationClient({ catalog: vi.fn(), connection: vi.fn(), ready, terminal, error: vi.fn() }, read, connect);
  await client.start();
  expect(new URL(connect.mock.calls[0]![0], 'http://local').searchParams.get('after')).toBe(catalog().cursor);
  s.send('open'); await tick(); expect(ready).toHaveBeenCalledTimes(1);
  const before = read.mock.calls.length;
  s.send('heartbeat'); await tick(); expect(read).toHaveBeenCalledTimes(before);
  const data = { service_instance_id: catalog().service_instance_id, view_schema_version: '1', run_id: catalog().items[0]!.active_run_id, model_id: 'GLM-5.2', publish_seq: '43', published_at: '2026-10-27T00:00:00.000000000Z', status: 'completed' };
  const id = `${data.service_instance_id}:43`;
  s.send('result_published', data, id); await tick();
  s.send('result_published', data, id); s.send('result_published', { ...data, publish_seq: '42' }, `${data.service_instance_id}:42`); await tick();
  expect(terminal).toHaveBeenCalledTimes(1); expect(read).toHaveBeenCalledTimes(before + 1);
  s.send('error'); s.send('open'); await tick(); expect(ready).toHaveBeenCalledTimes(2);
  client.stop(); s.send('open'); expect(ready).toHaveBeenCalledTimes(2); expect(s.close).toHaveBeenCalled();
});
it.each(['expired', 'future_cursor', 'instance_changed', 'invalid_cursor'])('reset %s closes old epoch and ignores its callbacks', async reason => {
  const streams = [stream(), stream()]; let i = 0;
  const ready = vi.fn();
  const client = new PublicationClient({ catalog: vi.fn(), connection: vi.fn(), ready, error: vi.fn() }, vi.fn().mockResolvedValue(catalog()), () => streams[i++]!);
  await client.start();
  streams[0]!.send('reset', { service_instance_id: catalog().service_instance_id, view_schema_version: '1', reason, catalog_url: '/monitoring/catalog' }); await tick();
  expect(streams[0]!.close).toHaveBeenCalled(); streams[0]!.send('open'); expect(ready).not.toHaveBeenCalled();
  streams[1]!.send('open'); await tick(); expect(ready).toHaveBeenCalledTimes(1); client.stop();
});
it('catalog pagination restarts entire read after revision conflict', async () => {
  const page = catalog();
  const first = { ...page, total: '2', next_offset: '1' };
  const read = vi.fn().mockResolvedValueOnce(first).mockRejectedValueOnce(new ApiError(409, 'CATALOG_REVISION_CHANGED', 'changed')).mockResolvedValueOnce(page);
  const result = await loadCatalog(undefined, read as typeof getJson);
  expect(result.items).toHaveLength(1); expect(read).toHaveBeenCalledTimes(3);
  expect(read.mock.calls[1]![2]).toMatchObject({ offset: '1', catalog_revision: '42' });
  expect(read.mock.calls[2]![2]).toMatchObject({ offset: '0' });
});
it('two independent clients have one stream each and no timed polling', async () => {
  const read = vi.fn().mockResolvedValue(catalog()), connect = vi.fn(() => stream());
  const hooks = { catalog: vi.fn(), connection: vi.fn(), ready: vi.fn(), error: vi.fn() };
  const a = new PublicationClient(hooks, read, connect), b = new PublicationClient(hooks, read, connect);
  await Promise.all([a.start(), b.start()]); expect(connect).toHaveBeenCalledTimes(2);
  await tick(); expect(read).toHaveBeenCalledTimes(2); a.stop(); b.stop();
});

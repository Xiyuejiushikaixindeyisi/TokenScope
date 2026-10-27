// @vitest-environment node
import { it, expect, vi } from 'vitest';
import { apiPath, getJson } from '../../src/api/client';
it('uses root paths and encodes appid without changing literal text', () => {
  const path = apiPath('/monitoring/catalog', { appid: '租户/&?# +', limit: 50 });
  expect(new URL(path, 'https://example.invalid').searchParams.get('appid')).toBe('租户/&?# +');
  expect(path.startsWith('/monitoring/catalog?')).toBe(true);
  expect(() => apiPath('//other.invalid')).toThrow();
  expect(() => apiPath('/\\other.invalid')).toThrow();
});
it('preserves unknown error code, 404 is not a failed job, no retry', async () => {
  const fetcher = vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify({ error: { code: 'SUBMISSION_NOT_FOUND', message: '未确认' } }), { status: 404, headers: { 'Content-Type': 'application/json' } }));
  await expect(getJson('Receipt', '/analysis-submissions/key', {}, { fetcher })).rejects.toMatchObject({ status: 404, code: 'SUBMISSION_NOT_FOUND' });
  expect(fetcher).toHaveBeenCalledTimes(1);
});
it('passes cancellation and instance protection explicitly', async () => {
  const signal = new AbortController().signal;
  const fetcher = vi.fn<typeof fetch>().mockResolvedValue(new Response('{"error":{"code":"SERVICE_INSTANCE_CHANGED","message":"changed"}}', { status: 409, headers: { 'Content-Type': 'application/json' } }));
  await expect(getJson('Receipt', '/analysis-submissions/key', {}, { fetcher, signal, instanceId: 'test-instance' })).rejects.toMatchObject({ status: 409 });
  const options = fetcher.mock.calls[0]![1]!;
  expect(new Headers(options.headers).get('X-TokenScope-Instance-Id')).toBe('test-instance');
  expect(options.signal).toBe(signal);
  expect(options.redirect).toBe('error');
});

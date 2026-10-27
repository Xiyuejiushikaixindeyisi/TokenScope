// @vitest-environment node
import { readFileSync } from 'node:fs';
import { it, expect, vi } from 'vitest';
import { ReceiptStore, mergeReceipt } from '../../src/state/receipt-store';
import type { LocalSubmission } from '../../src/state/receipt-store';
import { SubmissionCoordinator } from '../../src/state/submission-coordinator';
import { validateDto } from '../../src/api/validate';
import { ApiError } from '../../src/api/client';
const receipt = (state: string) => validateDto('Receipt', JSON.parse(readFileSync(new URL(`../../../../docs/contracts/examples/monitoring-view-s0/receipt-${state}.json`, import.meta.url), 'utf8')));
const instance = receipt('queued').service_instance_id;
const record = (key = 'synthetic-key-1'): LocalSubmission => ({ instance, request: { model_id: 'GLM-5.2', file_ref: 'synthetic.csv', submission_key: key }, submittedAt: new Date().toISOString(), runId: receipt('queued').run_id, status: 'queued' });
const tick = () => new Promise(resolve => setTimeout(resolve, 0));
it.each(['completed','no_valid_rows','failed','interrupted'])('first ready restores %s before subscription, no repeated same-epoch reads', async status => {
  const store = new ReceiptStore(() => {}, undefined); await store.ready; await store.save(record());
  const value = { ...receipt(status), run_id: record().runId!, submission_key: record().request.submission_key };
  const read = vi.fn().mockResolvedValue(value), coordinator = new SubmissionCoordinator(store, read);
  await coordinator.ready(instance, 1); await coordinator.ready(instance, 1);
  expect(store.getSnapshot()[0]!.status).toBe(status); expect(read).toHaveBeenCalledTimes(1);
});
it('terminal beats late running GET and conflicting terminal is explicit', async () => {
  const store = new ReceiptStore(() => {}, undefined); await store.ready; await store.save(record());
  let release!: (value: ReturnType<typeof receipt>) => void;
  const read = vi.fn().mockImplementation(() => new Promise(resolve => { release = resolve; }));
  const coordinator = new SubmissionCoordinator(store, read); const aligning = coordinator.ready(instance, 1); await tick();
  await coordinator.terminal({ service_instance_id: instance, view_schema_version: '1', run_id: record().runId!, model_id: 'GLM-5.2', event_seq: '999', status: 'failed', error_code: 'FAILED', finished_at: '2026-10-27T00:00:00.000000000Z' });
  release({ ...receipt('running'), run_id: record().runId!, submission_key: record().request.submission_key }); await aligning;
  expect(store.getSnapshot()[0]!.status).toBe('failed');
  expect(() => mergeReceipt(store.getSnapshot()[0]!, { ...receipt('completed'), run_id: record().runId!, submission_key: record().request.submission_key })).toThrow('TERMINAL_CONFLICT');
});
it('404 remains unconfirmed; lost POST preserves key and same-key explicit retry', async () => {
  const store = new ReceiptStore(() => {}, undefined); await store.ready;
  const read = vi.fn().mockRejectedValue(new ApiError(404, 'SUBMISSION_NOT_FOUND', 'missing'));
  const write = vi.fn().mockRejectedValue(new Error('network response lost'));
  const coordinator = new SubmissionCoordinator(store, read, write); await coordinator.ready(instance, 1);
  const request = record().request;
  await coordinator.submit(request, instance); await coordinator.align(request.submission_key); await coordinator.submit(request, instance);
  expect(store.getSnapshot()).toHaveLength(1); expect(store.getSnapshot()[0]!.status).toBe('unconfirmed');
  expect(write.mock.calls[0]![3]).toEqual(write.mock.calls[1]![3]);
  await expect(coordinator.submit({ ...request, file_ref: 'different.csv' }, instance)).rejects.toThrow('SUBMISSION_KEY_CONFLICT');
});
it('at most four concurrent lookups, reset epoch aligns once, old instance never queried', async () => {
  const store = new ReceiptStore(() => {}, undefined); await store.ready;
  for (let i = 0; i < 9; i++) await store.save(record('key-' + i));
  const releases: (() => void)[] = []; let active = 0, peak = 0;
  const read = vi.fn().mockImplementation((_name, path: string) => new Promise(resolve => { active++; peak = Math.max(peak, active); releases.push(() => { active--; resolve({ ...receipt('running'), run_id: record().runId!, submission_key: path.split('/').at(-1)! }); }); }));
  const coordinator = new SubmissionCoordinator(store, read); const work = coordinator.ready(instance, 1); await tick(); expect(active).toBe(4);
  while (releases.length) { releases.shift()!(); await tick(); } await work; expect(peak).toBe(4);
  const before = read.mock.calls.length; await coordinator.ready('44444444-4444-4444-8444-444444444444', 2); expect(read).toHaveBeenCalledTimes(before);
});
it('memory save cannot regress terminal even if stale save races after merge', async () => {
  const store = new ReceiptStore(() => {}, undefined); await store.ready;
  await store.save({ ...record(), status: 'failed' }); await store.save({ ...record(), status: 'running' });
  expect(store.getSnapshot()[0]!.status).toBe('failed');
});

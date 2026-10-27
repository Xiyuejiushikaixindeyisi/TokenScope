import { getJson, writeJson, ApiError } from '../api/client';
import { validateDto } from '../api/validate';
import type { Dto } from '../api/types';
import { isTerminal, mergeReceipt } from './receipt-store';
import type { KeyedSubmission, LocalSubmission, ReceiptStore } from './receipt-store';
export class SubmissionCoordinator {
  private instance = '';
  private seen = new Set<string>();
  private inflight = new Map<string, Promise<void>>();
  private queue: (() => void)[] = [];
  private active = 0;
  constructor(readonly store: ReceiptStore, private readonly read = getJson, private readonly write = writeJson) {}
  async ready(instance: string, epoch: number) {
    this.instance = instance; await this.store.ready;
    const token = `${instance}:${epoch}`; if (this.seen.has(token)) return; this.seen.add(token);
    // Keep only recent connection identities; not a periodic job.
    if (this.seen.size > 32) this.seen.delete(this.seen.values().next().value!);
    await Promise.all(this.store.getSnapshot().filter(r => r.instance === instance && !isTerminal(r.status)).map(r => this.align(r.request.submission_key)));
  }
  async submit(request: KeyedSubmission, instance: string) {
    validateDto('Submission', request);
    if (!request.submission_key) throw new Error('SUBMISSION_KEY_REQUIRED');
    if (instance !== this.instance) throw new Error('SERVICE_INSTANCE_UNCONFIRMED');
    await this.store.ready;
    const existing = this.store.find(instance, request.submission_key);
    if (existing && JSON.stringify(existing.request) !== JSON.stringify(request)) throw new Error('SUBMISSION_KEY_CONFLICT');
    let record: LocalSubmission = existing ?? { instance, request, submittedAt: new Date().toISOString(), status: 'unconfirmed' };
    await this.store.save(record); // before POST, even if the response is lost
    try {
      const run = await this.write('LegacyRunState', 'POST', '/analysis-runs', request, instance);
      if (instance !== this.instance) return;
      record = this.store.find(instance, request.submission_key)!;
      if (!isTerminal(record.status)) await this.store.save({ ...record, runId: run.run_id, status: run.status });
      await this.align(request.submission_key);
    } catch (error) {
      const current = this.store.find(instance, request.submission_key)!;
      await this.store.save({ ...current, message: error instanceof ApiError ? `${error.code}：${error.message}` : '提交响应未确认，请查询回执或显式使用同一key重试。' });
    }
  }
  align(key: string): Promise<void> {
    const instance = this.instance, id = `${instance}:${key}`;
    const known = this.inflight.get(id); if (known) return known;
    const record = this.store.find(instance, key); if (!record) return Promise.resolve();
    const promise = new Promise<void>(resolve => {
      this.queue.push(() => {
        this.active++;
        void (async () => {
          try {
            if (this.instance !== instance) return;
            const receipt = await this.read('Receipt', `/analysis-submissions/${encodeURIComponent(key)}`, {}, { instanceId: instance, scope: { service_instance_id: instance, view_schema_version: '1' } });
            if (this.instance !== instance) return;
            const latest = this.store.find(instance, key)!;
            await this.store.save(mergeReceipt(latest, receipt));
          } catch (error) {
            const latest = this.store.find(instance, key);
            if (latest && this.instance === instance) await this.store.save({ ...latest, message: error instanceof ApiError && error.status === 404 ? '提交尚未确认（404）；可显式使用同一key重试。' : '回执校验或查询失败；保留原状态，请手动对齐。' });
          } finally { this.active--; this.inflight.delete(id); resolve(); this.drain(); }
        })();
      });
    });
    this.inflight.set(id, promise); this.drain(); return promise;
  }
  private drain() { while (this.active < 4 && this.queue.length) this.queue.shift()!(); }
  async terminal(event: Dto<'ResultPublishedEvent'> | Dto<'RunTerminalEvent'>) {
    if (event.service_instance_id !== this.instance) return;
    await this.store.ready;
    for (const record of this.store.getSnapshot().filter(r => r.instance === this.instance && r.runId === event.run_id)) {
      if (isTerminal(record.status) && record.status !== event.status) { await this.store.save({ ...record, message: '终态冲突，请手动对齐；未覆盖原终态。' }); continue; }
      await this.store.save({ ...record, status: event.status });
    }
  }
}

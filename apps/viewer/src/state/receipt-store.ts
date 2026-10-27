import type { Dto } from '../api/types';
import { validateDto } from '../api/validate';
export type KeyedSubmission = Dto<'Submission'> & { submission_key: string };
export interface LocalSubmission {
  instance: string;
  request: KeyedSubmission;
  submittedAt: string;
  runId?: string;
  status: 'unconfirmed' | Dto<'Receipt'>['status'];
  receipt?: Dto<'Receipt'>;
  message?: string;
}
export const isTerminal = (status: LocalSubmission['status']) => ['completed', 'no_valid_rows', 'failed', 'interrupted'].includes(status);
export function mergeReceipt(record: LocalSubmission, incoming: Dto<'Receipt'>): LocalSubmission {
  validateDto('Receipt', incoming, { service_instance_id: record.instance, view_schema_version: '1', model_id: record.request.model_id });
  if (incoming.submission_key !== record.request.submission_key || (record.runId && record.runId !== incoming.run_id)) throw new Error('RECEIPT_IDENTITY_CONFLICT');
  if (isTerminal(record.status)) {
    if (isTerminal(incoming.status) && record.status !== incoming.status) throw new Error('TERMINAL_CONFLICT');
    if (!isTerminal(incoming.status)) return record;
  }
  const merged = { ...record, runId: incoming.run_id, status: incoming.status, receipt: incoming }; delete merged.message; return merged;
}
/** Independent DB lifetime: snapshot cleanup never removes unresolved operations. */
export class ReceiptStore {
  private records: LocalSubmission[] = [];
  private listeners = new Set<() => void>();
  private database: Promise<IDBDatabase> | undefined;
  readonly ready: Promise<void>;
  constructor(private readonly warn: (message: string) => void, private readonly factory: IDBFactory | undefined = globalThis.indexedDB) { this.ready = this.restore(); }
  getSnapshot = () => this.records;
  subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private notify() { for (const listener of this.listeners) listener(); }
  private db() {
    return this.database ??= new Promise<IDBDatabase>((resolve, reject) => {
      if (!this.factory) { reject(new Error('IDB_UNAVAILABLE')); return; }
      const req = this.factory.open('tokenscope-viewer-receipts-v1', 1);
      req.onupgradeneeded = () => req.result.createObjectStore('receipts');
      req.onerror = () => reject(req.error); req.onblocked = () => reject(new Error('IDB_BLOCKED'));
      req.onsuccess = () => { const db = req.result; db.onversionchange = () => db.close(); resolve(db); };
    });
  }
  private async restore() {
    try {
      const db = await this.db();
      const loaded = await new Promise<LocalSubmission[]>((resolve, reject) => { const tx = db.transaction('receipts', 'readonly'), req = tx.objectStore('receipts').getAll(); tx.oncomplete = () => resolve(req.result as LocalSubmission[]); tx.onabort = () => reject(tx.error); });
      this.records = loaded.filter(record => {
        try { validateDto('Submission', record.request); if (record.receipt) validateDto('Receipt', record.receipt); return typeof record.request.submission_key === 'string' && record.request.submission_key.length > 0 && typeof record.instance === 'string' && typeof record.submittedAt === 'string' && ['unconfirmed','queued','running','completed','no_valid_rows','failed','interrupted'].includes(record.status); } catch { this.warn('一条本地回执无法读取，请按原提交key恢复。'); return false; }
      }); this.notify();
    } catch { this.warn('提交回执只能保留在当前页面；请保存显示的提交key，刷新后可能无法自动恢复。'); }
  }
  async save(record: LocalSubmission) {
    await this.ready;
    const current = this.find(record.instance, record.request.submission_key);
    if (current && isTerminal(current.status) && record.status !== current.status) {
      record = { ...current, ...(record.message ? { message: record.message } : {}) };
    }
    const key = JSON.stringify([record.instance, record.request.submission_key]);
    this.records = [...this.records.filter(item => JSON.stringify([item.instance, item.request.submission_key]) !== key), record]; this.notify();
    try { const db = await this.db(); await new Promise<void>((resolve, reject) => { const tx = db.transaction('receipts', 'readwrite'); tx.objectStore('receipts').put(record, key); tx.oncomplete = () => resolve(); tx.onabort = () => reject(tx.error); tx.onerror = () => reject(tx.error); }); }
    catch { this.warn('回执持久化失败，请保留提交key；当前页面仍可恢复状态。'); }
  }
  find(instance: string, key: string) { return this.records.find(item => item.instance === instance && item.request.submission_key === key); }
}

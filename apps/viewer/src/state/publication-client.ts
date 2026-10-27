import { apiPath } from '../api/client';
import { validateDto } from '../api/validate';
import type { Dto } from '../api/types';
import { loadCatalog } from './catalog';
export interface EventStream {
  addEventListener(type: string, listener: EventListener): void;
  close(): void;
}
export interface PublicationHooks {
  catalog(value: Dto<'CatalogResponse'>): void;
  connection(value: 'connecting' | 'connected' | 'disconnected'): void;
  ready(instance: string, epoch: number): void;
  terminal?(value: Dto<'ResultPublishedEvent'> | Dto<'RunTerminalEvent'>): void;
  error(message: string): void;
}
/** A persistent SSE log plus one-shot reconciliation; no timers and no metric polling. */
export class PublicationClient {
  private epoch = 0;
  private readyEpoch = 0;
  private source: EventStream | null = null;
  private abort: AbortController | null = null;
  private refreshing: Promise<void> | null = null;
  private dirty = false;
  private instance = '';
  private sequence = 0n;
  constructor(private readonly hooks: PublicationHooks, private readonly read = loadCatalog, private readonly connect: (url: string) => EventStream = url => new EventSource(url)) {}
  async start() {
    this.stop(); const epoch = this.epoch;
    this.abort = new AbortController();
    this.hooks.connection('connecting');
    try {
      const catalog = await this.read(this.abort.signal);
      if (epoch !== this.epoch) return;
      this.instance = catalog.service_instance_id;
      this.sequence = BigInt(catalog.cursor.slice(catalog.cursor.lastIndexOf(':') + 1));
      this.hooks.catalog(catalog);
      const source = this.connect(apiPath('/monitoring/events', { after: catalog.cursor }));
      this.source = source;
      const listen = (name: string, handler: (event: MessageEvent<string>) => void) => source.addEventListener(name, event => {
        if (epoch !== this.epoch) return;
        try { handler(event as MessageEvent<string>); } catch { this.hooks.error('事件不符合固定协议，请重新连接。'); }
      });
      listen('open', () => {
        this.hooks.connection('connected');
        this.hooks.ready(this.instance, ++this.readyEpoch);
        void this.reconcile(epoch);
      });
      listen('error', () => this.hooks.connection('disconnected'));
      listen('reset', event => { validateDto('ResetEvent', JSON.parse(event.data)); void this.start(); });
      const published = (event: MessageEvent<string>, kind: 'ResultPublishedEvent' | 'RunTerminalEvent') => {
        const data = validateDto(kind, JSON.parse(event.data), { service_instance_id: this.instance, view_schema_version: '1' });
        const seq = 'publish_seq' in data ? data.publish_seq : data.event_seq;
        if (event.lastEventId !== `${this.instance}:${seq}`) throw new Error('EVENT_ID_MISMATCH');
        if (BigInt(seq) <= this.sequence) return;
        this.sequence = BigInt(seq);
        this.hooks.terminal?.(data);
        if (kind === 'ResultPublishedEvent') void this.reconcile(epoch);
      };
      listen('result_published', event => published(event, 'ResultPublishedEvent'));
      listen('run_terminal', event => published(event, 'RunTerminalEvent'));
    } catch { if (epoch === this.epoch) { this.hooks.connection('disconnected'); this.hooks.error('目录暂不可读，可重新连接；已有结果保持。'); } }
  }
  private reconcile(epoch: number): Promise<void> {
    this.dirty = true;
    if (this.refreshing) return this.refreshing;
    const work = (async () => {
      while (this.dirty && epoch === this.epoch) {
        this.dirty = false;
        try {
          const catalog = await this.read(this.abort?.signal);
          if (epoch !== this.epoch) return;
          if (catalog.service_instance_id !== this.instance) { void this.start(); return; }
          this.hooks.catalog(catalog);
        } catch { if (epoch === this.epoch) this.hooks.error('目录同步失败，已保留完整结果；可手动重试。'); }
      }
    })();
    this.refreshing = work;
    void work.finally(() => { if (this.refreshing === work) this.refreshing = null; });
    return work;
  }
  stop() {
    this.epoch++; this.source?.close(); this.source = null;
    this.abort?.abort(); this.abort = null;
    this.refreshing = null; this.dirty = false;
  }
}

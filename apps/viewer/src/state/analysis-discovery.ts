import { AnalysisClient, obj, str, validate } from '../api/analysis/client';
import type { Catalog, Obj } from '../api/analysis/client';
import { apiPath } from '../api/client';
export interface Frame {
    event: string;
    id: string;
    data: string;
}
/** Incremental SSE decoder. Heartbeats have no data and never trigger a GET. */
export class SSEDecoder {
    private buffer = '';
    private event = '';
    private id = '';
    private data: string[] = [];
    push(chunk: string): Frame[] {
        this.buffer += chunk;
        const frames: Frame[] = [];
        for (;;) {
            const match = /\r\n|\n|\r(?!$)/.exec(this.buffer);
            if (!match)
                break;
            const line = this.buffer.slice(0, match.index);
            this.buffer = this.buffer.slice(match.index + match[0].length);
            if (line === '') {
                if (this.data.length)
                    frames.push({ event: this.event || 'message', id: this.id, data: this.data.join('\n') });
                this.event = '';
                this.id = '';
                this.data = [];
                continue;
            }
            if (line.startsWith(':'))
                continue;
            const split = line.indexOf(':');
            const key = split < 0 ? line : line.slice(0, split);
            let value = split < 0 ? '' : line.slice(split + 1);
            if (value.startsWith(' '))
                value = value.slice(1);
            if (key === 'event')
                this.event = value;
            if (key === 'id' && !value.includes('\0'))
                this.id = value;
            if (key === 'data')
                this.data.push(value);
        }
        return frames;
    }
}
export class DiscoverySession {
    private controller = new AbortController();
    private active: AbortController | null = null;
    private syncing = false;
    private dirty = false;
    constructor(private callbacks: {
        catalog: (api: AnalysisClient, c: Catalog) => void;
        status: (message: string) => void;
        terminal?: (value: Obj) => void;
    }, private fetcher: typeof fetch = (...args) => globalThis.fetch(...args), private includeSamples = false) { }
    stop() { this.controller.abort(); this.active?.abort(); }
    async run() {
        let attempts = 0;
        while (!this.controller.signal.aborted) {
            this.active = new AbortController();
            const signal = this.active.signal;
            try {
                this.callbacks.status('正在核对报告目录');
                const api = await AnalysisClient.connect(signal, this.fetcher, this.includeSamples);
                const cat = await api.catalog(signal);
                if (signal.aborted)
                    break;
                this.callbacks.catalog(api, cat);
                const response = await this.fetcher(apiPath('/diagnostics/discovery/events', { cursor: cat.cursor }), { method: 'GET', credentials: 'same-origin', redirect: 'error', signal, headers: { Accept: 'text/event-stream', 'x-tokenscope-service-instance': api.instance } });
                if (!response.ok || !response.body || !response.headers.get('content-type')?.includes('text/event-stream'))
                    throw Error(`通知连接不可用 (${response.status})`);
                this.callbacks.status('报告通知已连接');
                attempts = 0;
                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8', { fatal: true }), parser = new SSEDecoder();
                const seen = new Set<string>();
                try {
                    for (;;) {
                        const part = await reader.read();
                        if (part.done)
                            throw Error('通知连接中断');
                        for (const frame of parser.push(decoder.decode(part.value, { stream: true }))) {
                            if (frame.event === 'reset') {
                                validate('reset', JSON.parse(frame.data));
                                throw Error('通知目录需要重新对齐');
                            }
                            if (frame.event !== 'terminal')
                                continue;
                            const event = validate('terminal_event', JSON.parse(frame.data));
                            if (event.service_instance_id !== api.instance)
                                throw Error('SERVICE_INSTANCE_MISMATCH');
                            const id = str(event.event_id);
                            if (frame.id !== id)
                                throw Error('EVENT_ID_MISMATCH');
                            if (seen.has(id))
                                continue;
                            seen.add(id);
                            if (seen.size > 1000)
                                seen.delete(seen.values().next().value!);
                            this.callbacks.terminal?.(obj(event));
                            void this.align(api, signal);
                        }
                    }
                }
                finally {
                    await reader.cancel().catch(() => { });
                    reader.releaseLock();
                }
            }
            catch (e) {
                if (this.controller.signal.aborted)
                    break;
                this.callbacks.status(`通知未连接：${e instanceof Error ? e.message : String(e)}；保留已读报告，正在重连`);
            }
            this.active.abort();
            this.syncing = false;
            this.dirty = false;
            if (this.controller.signal.aborted)
                break;
            const delay = Math.min(30000, 1000 * 2 ** Math.min(attempts++, 5)) * (0.8 + Math.random() * 0.4);
            await new Promise<void>(resolve => { const done = () => { clearTimeout(timer); this.controller.signal.removeEventListener('abort', done); resolve(); }; const timer = setTimeout(done, delay); this.controller.signal.addEventListener('abort', done, { once: true }); });
        }
    }
    private async align(api: AnalysisClient, signal: AbortSignal) {
        this.dirty = true;
        if (this.syncing)
            return;
        this.syncing = true;
        try {
            do {
                this.dirty = false;
                const c = await api.catalog(signal);
                if (signal.aborted)
                    return;
                this.callbacks.catalog(api, c);
            } while (this.dirty && !signal.aborted);
        }
        catch (e) {
            if (!signal.aborted) {
                this.callbacks.status(`目录读取失败：${String(e)}；保留原报告`);
                this.active?.abort();
            }
        }
        finally {
            this.syncing = false;
        }
    }
}

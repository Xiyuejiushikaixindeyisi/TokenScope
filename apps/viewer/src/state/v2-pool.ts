/** Per-scope request pool; cancellation releases no new jobs from the old scope. */
export class RequestPool {
    private active = 0;
    private queue: (() => void)[] = [];
    private controller = new AbortController();
    constructor(private readonly limit = 4, private readonly scope?: AbortSignal) {
        if (scope?.aborted) this.stop();
        else scope?.addEventListener('abort', this.stop, { once: true });
    }
    run<T>(load: (signal: AbortSignal) => Promise<T>, done: (value: T) => void, fail: (error: unknown) => void) {
        this.queue.push(() => { this.active++; void load(this.controller.signal).then(v => { if (!this.controller.signal.aborted)
            done(v); }).catch(e => { if (!this.controller.signal.aborted)
            fail(e); }).finally(() => { this.active--; this.pump(); }); });
        this.pump();
    }
    private pump() { while (!this.controller.signal.aborted && this.active < this.limit && this.queue.length)
        this.queue.shift()!(); }
    stop = () => { this.queue = []; this.controller.abort(); this.scope?.removeEventListener('abort', this.stop); };
}

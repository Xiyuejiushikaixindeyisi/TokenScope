import { ApiError } from '../api/client';
export const POLL_MS = 60000;
export interface TaskReceipt {
    state: string;
    error_code?: string | null;
}
export interface TaskState<R, D> {
    receipt: R | null;
    displayed: D | null;
    busy: boolean;
    error: string | null;
    resultPending: boolean;
}
/** Tracks a task independently of the last complete displayed analysis. */
export class TaskTracker<R extends TaskReceipt, D> {
    private value: TaskState<R, D>;
    private listeners = new Set<() => void>();
    private timer: ReturnType<typeof setTimeout> | undefined;
    private controller: AbortController | undefined;
    private generation = 0;
    private stopped = true;
    constructor(private readonly read: (signal: AbortSignal) => Promise<R>, private readonly load: (receipt: R, signal: AbortSignal) => Promise<D>, displayed: D | null = null) {
        this.value = { receipt: null, displayed, busy: false, error: null, resultPending: false };
    }
    getSnapshot = () => this.value;
    setDisplayed = (displayed: D) => this.update({ displayed });
    subscribe = (fn: () => void) => { this.listeners.add(fn); return () => { this.listeners.delete(fn); }; };
    private update(patch: Partial<TaskState<R, D>>) { this.value = { ...this.value, ...patch }; this.listeners.forEach(fn => fn()); }
    stop = () => { this.stopped = true; this.generation++; clearTimeout(this.timer); this.controller?.abort(); this.controller = undefined; this.update({ busy: false }); };
    start = (receipt?: R) => {
        this.stop();
        this.stopped = false;
        if (receipt) {
            this.update({ receipt, error: null });
            if (this.terminal(receipt))
                void this.refresh();
            else
                this.schedule();
        }
        else
            void this.refresh();
    };
    private terminal(r: R) { return ['ready', 'empty', 'completed', 'failed', 'interrupted'].includes(r.state); }
    private schedule() { if (!this.stopped)
        this.timer = setTimeout(() => { void this.refresh(); }, POLL_MS); }
    refresh = async () => {
        if (this.stopped || this.controller)
            return;
        clearTimeout(this.timer);
        const generation = this.generation, controller = new AbortController();
        this.controller = controller;
        this.update({ busy: true, error: null });
        let terminal = false;
        try {
            const receipt = await this.read(controller.signal);
            if (this.stopped || generation !== this.generation)
                return;
            terminal = this.terminal(receipt);
            this.update({ receipt });
            if (['failed', 'interrupted'].includes(receipt.state)) {
                this.update({ error: receipt.error_code ?? receipt.state, resultPending: false });
            }
            else if (terminal) {
                this.update({ resultPending: true });
                const displayed = await this.load(receipt, controller.signal);
                if (this.stopped || generation !== this.generation)
                    return;
                this.update({ displayed, resultPending: false });
            }
        }
        catch (error) {
            if (generation !== this.generation || this.stopped)
                return;
            this.update({ error: error instanceof Error ? error.message : '读取失败' });
            if (error instanceof ApiError && ['INSTANCE_MISMATCH', 'SERVICE_INSTANCE_CHANGED'].includes(error.code))
                terminal = true;
        }
        finally {
            if (generation === this.generation) {
                this.controller = undefined;
                this.update({ busy: false });
                if (!terminal)
                    this.schedule();
            }
        }
    };
}

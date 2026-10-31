import { afterEach, expect, test, vi } from 'vitest';
import { TaskTracker } from '../../src/state/v2-task';
import { ApiError } from '../../src/api/client';
afterEach(() => vi.useRealTimers());
test('identity mismatch stops automatic reads, completed load is one atomic publication', async () => {
    vi.useFakeTimers();
    const read = vi.fn().mockRejectedValue(new ApiError(409, 'INSTANCE_MISMATCH', 'changed'));
    const task = new TaskTracker(read, async () => 'bad', 'old');
    task.start();
    await vi.advanceTimersByTimeAsync(180000);
    expect(read).toHaveBeenCalledTimes(1);
    expect(task.getSnapshot().displayed).toBe('old');
    task.stop();
});
test('60 second polling, failed/interrupted keep historical result; terminal stops', async () => {
    for (const state of ['failed', 'interrupted']) {
        vi.useFakeTimers();
        const read = vi.fn().mockResolvedValue({ state });
        const load = vi.fn();
        const task = new TaskTracker(read, load, 'history');
        task.start({ state: 'running' });
        await vi.advanceTimersByTimeAsync(59999);
        expect(read).not.toHaveBeenCalled();
        await vi.advanceTimersByTimeAsync(1);
        expect(read).toHaveBeenCalledTimes(1);
        expect(task.getSnapshot().displayed).toBe('history');
        await vi.advanceTimersByTimeAsync(180000);
        expect(read).toHaveBeenCalledTimes(1);
        expect(load).not.toHaveBeenCalled();
        task.stop();
    }
});
test('success atomically replaces only after result read; empty is terminal', async () => {
    vi.useFakeTimers();
    let finish!: (value: string) => void;
    const read = vi.fn().mockResolvedValue({ state: 'empty' });
    const task = new TaskTracker(read, () => new Promise<string>(resolve => { finish = resolve; }), 'old');
    task.start({ state: 'indexing' });
    await vi.advanceTimersByTimeAsync(60000);
    expect(task.getSnapshot().displayed).toBe('old');
    finish('empty-result');
    await vi.advanceTimersByTimeAsync(1);
    expect(task.getSnapshot().displayed).toBe('empty-result');
    await vi.advanceTimersByTimeAsync(180000);
    expect(read).toHaveBeenCalledTimes(1);
    task.stop();
});
test('result failure keeps old and stops automatic polling; explicit refresh can recover', async () => {
    vi.useFakeTimers();
    const read = vi.fn().mockResolvedValue({ state: 'ready' });
    const load = vi.fn().mockRejectedValueOnce(Error('result unavailable')).mockResolvedValue('new');
    const task = new TaskTracker(read, load, 'old');
    task.start();
    await vi.advanceTimersByTimeAsync(1);
    expect(task.getSnapshot().displayed).toBe('old');
    expect(task.getSnapshot().resultPending).toBe(true);
    await vi.advanceTimersByTimeAsync(120000);
    expect(read).toHaveBeenCalledTimes(1);
    await task.refresh();
    expect(task.getSnapshot().displayed).toBe('new');
    task.stop();
});
test('slow requests never overlap, stopped generations cannot publish', async () => {
    vi.useFakeTimers();
    let finish!: (v: {
        state: string;
    }) => void;
    const read = vi.fn(() => new Promise<{
        state: string;
    }>(resolve => { finish = resolve; }));
    const load = vi.fn().mockResolvedValue('new');
    const task = new TaskTracker(read, load, 'old');
    task.start();
    await vi.advanceTimersByTimeAsync(180000);
    await task.refresh();
    expect(read).toHaveBeenCalledTimes(1);
    task.stop();
    finish({ state: 'completed' });
    await vi.advanceTimersByTimeAsync(1);
    expect(load).not.toHaveBeenCalled();
    expect(task.getSnapshot().displayed).toBe('old');
});
test('transient read errors retry on next minute without losing history', async () => {
    vi.useFakeTimers();
    const read = vi.fn().mockRejectedValueOnce(Error('offline')).mockResolvedValue({ state: 'completed' });
    const task = new TaskTracker(read, async () => 'new', 'old');
    task.start();
    await vi.advanceTimersByTimeAsync(1);
    expect(task.getSnapshot().displayed).toBe('old');
    await vi.advanceTimersByTimeAsync(60000);
    expect(task.getSnapshot().displayed).toBe('new');
    task.stop();
});

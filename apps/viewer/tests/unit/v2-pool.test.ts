import { test, expect } from 'vitest';
import { RequestPool } from '../../src/state/v2-pool';
test('four in flight, individual failure releases slot, stopped scope never publishes', async () => {
    const pool = new RequestPool(), resolves: (() => void)[] = [], rejects: (() => void)[] = [];
    let active = 0, maximum = 0, done = 0, failed = 0;
    for (let i = 0; i < 10; i++)
        pool.run(() => new Promise<void>((resolve, reject) => { active++; maximum = Math.max(maximum, active); resolves.push(() => { active--; resolve(); }); rejects.push(() => { active--; reject(Error('row')); }); }), () => done++, () => failed++);
    expect(resolves).toHaveLength(4);
    rejects[0]!();
    await new Promise(r => setTimeout(r, 0));
    expect(resolves).toHaveLength(5);
    expect(failed).toBe(1);
    resolves[1]!();
    await new Promise(r => setTimeout(r, 0));
    expect(resolves).toHaveLength(6);
    expect(done).toBe(1);
    pool.stop();
    resolves[2]!();
    await new Promise(r => setTimeout(r, 0));
    expect(done).toBe(1);
    expect(resolves).toHaveLength(6);
    expect(maximum).toBe(4);
});

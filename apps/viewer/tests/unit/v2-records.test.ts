import { test, expect } from 'vitest';
import { V2Records } from '../../src/storage/v2-records';
test('scope isolation and preservation of damaged records', () => {
    localStorage.clear();
    const a = new V2Records('a', 'user'), b = new V2Records('b', 'user'), ma = new V2Records('a', 'ma');
    a.saveDisplayed('history', 'appid');
    a.saveIntent({ key: 'stable', path: '/runs', body: { file_ref: 'input.csv' } });
    a.remember('pending');
    expect(a.read().displayed?.run).toBe('history');
    expect(b.read().runs).toEqual([]);
    expect(ma.read().intent).toBeUndefined();
    localStorage.setItem('tokenscope.v2.1:user:a', '{"runs":[],"scenarios":[null]}');
    expect(() => a.read()).toThrow();
    expect(localStorage.getItem('tokenscope.v2.1:user:a')).toContain('[null]');
});

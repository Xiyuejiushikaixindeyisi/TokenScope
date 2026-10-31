import { expect, test, vi } from 'vitest';
import { V2Client, validateV2 } from '../../src/api/v2/client';
import { V2Records } from '../../src/storage/v2-records';
const receipt = { service_instance_id: 'service', user_run_id: 'u', base_run_id: null, common_name: 'c', model_id: 'GLM-5.2', state: 'accepted', index_revision: null, error_code: null };
test('strict validation and service boundary; no coercion or extra fields', async () => {
    expect(validateV2('user', 'Receipt', receipt)).toEqual(receipt);
    expect(() => validateV2('user', 'Receipt', { ...receipt, extra: 1 })).toThrow();
    const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...receipt, service_instance_id: 'other' }), { headers: { 'Content-Type': 'application/json' } }));
    await expect(new V2Client('service', fetcher).request('user', 'Receipt', '/runs/u')).rejects.toThrow('服务身份');
    expect(fetcher.mock.calls[0]?.[1].headers['X-TokenScope-Instance-Id']).toBe('service');
});
test('new minimal and old scenario schemas resolve local references', () => {
    const minimal = { timing_model: 'batch_reference_total_noncompute_v1', scenario_id: 's', revision: '1', model_id: 'GLM-5.2', common_name: 'c', deployment: 'd', source: 'user_assumption', source_description: 'manual', chunk_tokens: '8192', chunk_seconds: '1' };
    expect(validateV2('user', 'Scenario', minimal)).toEqual(minimal);
    expect(() => validateV2('user', 'Scenario', { ...minimal, overhead_seconds: '0' })).toThrow();
    expect(() => validateV2('user', 'Scenario', { ...minimal, timing_model: 'unknown' })).toThrow();
});
test('explicit POST preserves original body and has no implicit retry', async () => {
    const fetcher = vi.fn().mockRejectedValue(Error('offline'));
    const body = { submission_key: 'stable', file_ref: 'safe.csv' };
    await expect(new V2Client('service', fetcher).request('user', 'Receipt', '/runs', { body })).rejects.toThrow('offline');
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(fetcher.mock.calls[0]?.[1].body).toBe(JSON.stringify(body));
});
test('local recovery records isolated by service and kind, stable submission retained', () => {
    localStorage.clear();
    const store = new V2Records('a', 'user');
    store.saveIntent({ key: 'same', path: '/runs', body: { submission_key: 'same', file_ref: 'f' } });
    store.remember('run');
    expect(new V2Records('a', 'user').read().intent?.key).toBe('same');
    expect(new V2Records('b', 'user').read().runs).toEqual([]);
    expect(new V2Records('a', 'ma').read().runs).toEqual([]);
});

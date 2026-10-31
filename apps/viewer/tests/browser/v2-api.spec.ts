import { test, expect } from '@playwright/test';
test('V2 real service receipts use the frontend validated client and preserve submission keys', async ({ page }) => {
    test.skip(process.env.TOKENSCOPE_REAL_BACKEND !== '1', 'Requires isolated synthetic state');
    await page.goto('/');
    const result = await page.evaluate(async () => {
        const modulePath = '/src/api/v2/client.ts';
        const { V2Client } = await import(/* @vite-ignore */ modulePath);
        const catalog = await fetch('/monitoring/catalog').then(r => r.json());
        const api = new V2Client(catalog.service_instance_id);
        const body = { submission_key: 'mv2-f001-user', file_ref: 'model-1.csv', model_id: 'GLM-5.2', common_name: 'GLM-V5.2' };
        const first = await api.request('user', 'Receipt', '/runs', { body });
        const second = await api.request('user', 'Receipt', '/runs', { body });
        const receipt = await api.request('user', 'Receipt', '/runs/' + first.user_run_id);
        const maBody = { submission_key: 'mv2-f001-ma', pre_file_ref: 'model-1.csv', now_file_ref: 'model-2.csv', model_id: 'GLM-5.2', model_standard_name: 'GLM-V5.2-32K', pre_start: '2026-10-27T00:00:00Z', now_start: '2026-10-27T01:00:00Z', now_end: '2026-10-27T02:00:00Z', source_timezone: 'UTC' };
        const ma = await api.request('ma', 'Receipt', '/runs', { body: maBody });
        const restored = await api.request('ma', 'Receipt', '/submissions/' + maBody.submission_key);
        return { sameUser: first.user_run_id === second.user_run_id, readUser: receipt.user_run_id === first.user_run_id, sameMa: ma.ma_run_id === restored.ma_run_id };
    });
    expect(result).toEqual({ sameUser: true, readUser: true, sameMa: true });
});

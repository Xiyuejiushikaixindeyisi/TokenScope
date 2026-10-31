import { test, expect } from '@playwright/test';
test('real MA warmup conflict and empty published scope are distinct terminal views', async ({ page }) => {
    test.skip(process.env.TOKENSCOPE_REAL_BACKEND !== '1', 'isolated backend');
    test.setTimeout(90000);
    await page.goto('/#/ma');
    for (const kind of ['conflict', 'empty']) {
        const r = await page.evaluate(async (kind) => { const c = await fetch('/monitoring/catalog').then(r => r.json()); return fetch('/monitoring/ma/runs', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-TokenScope-Instance-Id': c.service_instance_id }, body: JSON.stringify({ submission_key: `mv2-f006-${kind}`, pre_file_ref: `mv2-${kind}-pre.csv`, now_file_ref: `mv2-${kind}-now.csv`, model_id: 'Qwen3.6-27B', model_standard_name: `synthetic-${kind}`, pre_start: '2026-10-20T07:00:00Z', now_start: '2026-10-20T08:00:00Z', now_end: '2026-10-20T09:00:00Z', source_timezone: 'UTC' }) }).then(r => r.json()); }, kind);
        expect(r.ma_run_id).toBeTruthy();
        await expect.poll(async () => page.evaluate(async (id) => (await fetch(`/monitoring/ma/runs/${id}`).then(r => r.json())).state, r.ma_run_id), { timeout: 40000, intervals: [1000] }).toBe('completed');
        if (kind === 'conflict')
            await page.getByText('按已知运行ID打开', { exact: true }).click();
        await page.getByLabel('MA运行ID').fill(r.ma_run_id);
        await page.getByRole('button', { name: '打开MA运行' }).click();
        if (kind === 'conflict') {
            await expect(page.locator('.ma-table tbody tr')).toHaveCount(1);
            await expect(page.locator('.ma-table')).toContainText('预热顺序冲突');
            await expect(page.locator('.ma-table')).toContainText('75');
        }
        else {
            await expect(page.locator('.ma-table tbody tr')).toHaveCount(0);
            await expect(page.getByText('空范围：empty_file。不虚构UUID，也不等于生产零流量。')).toBeVisible();
        }
    }
});

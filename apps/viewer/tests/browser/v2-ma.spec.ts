import { test, expect } from '@playwright/test';
test('real MA completion, all UUIDs, row retry, independent charts and quality', async ({ page }) => {
    test.skip(process.env.TOKENSCOPE_REAL_BACKEND !== '1', 'isolated synthetic backend');
    await page.goto('/#/ma');
    const r = await page.evaluate(async () => { const c = await fetch('/monitoring/catalog').then(r => r.json()); return fetch('/monitoring/ma/runs', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-TokenScope-Instance-Id': c.service_instance_id }, body: JSON.stringify({ submission_key: 'mv2-f005-real', pre_file_ref: 'mv2-pre.csv', now_file_ref: 'mv2-now.csv', model_id: 'Qwen3.6-27B', model_standard_name: 'synthetic-q-64K', pre_start: '2026-10-20T07:00:00Z', now_start: '2026-10-20T08:00:00Z', now_end: '2026-10-20T09:00:00Z', source_timezone: 'UTC' }) }).then(r => r.json()); });
    expect(r.ma_run_id).toBeTruthy();
    await expect.poll(async () => page.evaluate(async (id) => (await fetch(`/monitoring/ma/runs/${id}`).then(r => r.json())).state, r.ma_run_id), { timeout: 60000, intervals: [1000] }).toBe('completed');
    let once = true;
    await page.route('**/instances/uuid-00', async (route) => { if (once) {
        once = false;
        await route.abort();
    }
    else
        await route.continue(); });
    await page.getByText('按已知运行ID打开', { exact: true }).click();
    await page.getByLabel('MA运行ID').fill(r.ma_run_id);
    await page.getByRole('button', { name: '打开MA运行' }).click();
    await expect(page.locator('.ma-table tbody tr')).toHaveCount(13);
    const row = page.locator('.ma-table tbody tr').filter({ hasText: 'uuid-00' });
    await expect(row.getByRole('button', { name: '重试此行' })).toBeVisible();
    await row.getByRole('button', { name: '重试此行' }).click();
    await expect(row.getByRole('button', { name: '查看画像' })).toBeVisible();
    await row.getByRole('button', { name: '查看画像' }).click();
    await expect(page.getByRole('img', { name: '请求压力（req/s），12个5分钟桶' })).toBeVisible();
    await page.getByRole('button', { name: '长度分布', exact: true }).click();
    await expect(page.getByRole('img', { name: '实际未命中长度分布' })).toBeVisible();
    await page.getByLabel('MA分布箱宽').selectOption('1000');
    await page.getByRole('button', { name: '运行质量记录', exact: true }).click();
    await expect(page.getByText('整次运行pre/now质量记录，不按当前UUID过滤。')).toBeVisible();
    await expect(page.locator('table').last()).toContainText('now');
    await page.setViewportSize({ width: 390, height: 844 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

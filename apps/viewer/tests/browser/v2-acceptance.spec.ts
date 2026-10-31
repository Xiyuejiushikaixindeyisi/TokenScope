import { test, expect } from '@playwright/test';
import type { Page } from '@playwright/test';
async function user(page: Page, index = 1, key = `mv2-f006-user-${index}`) { return page.evaluate(async ({ index, key }) => { const c = await fetch('/monitoring/catalog').then(r => r.json()); return fetch('/monitoring/user-v2/runs', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-TokenScope-Instance-Id': c.service_instance_id }, body: JSON.stringify({ submission_key: key, file_ref: `model-${index}.csv`, model_id: ['GLM-5.2', 'Qwen3.6-27B', 'DeepSeek-V4-Flash-0731'][index - 1], common_name: ['GLM-V5.2', 'Qwen-V3.6-27B', 'DeepSeek-V4-Flash'][index - 1] }) }).then(r => r.json()); }, { index, key }); }
async function openUser(page: Page, id: string) { await page.getByRole('button', { name: '打开运行', exact: true }).click(); await page.locator('input[name=run]').fill(id); await page.getByRole('button', { name: '打开', exact: true }).click(); }
test.beforeEach(() => test.skip(process.env.TOKENSCOPE_REAL_BACKEND !== '1', 'isolated synthetic backend'));
test('three real models and read-only visual captures', async ({ page }) => {
    test.setTimeout(120000);
    await page.goto('/#/users');
    for (let i = 1; i <= 3; i++) {
        const r = await user(page, i);
        expect(r.user_run_id).toBeTruthy();
        await expect.poll(async () => page.evaluate(async (receipt) => (await fetch(`/monitoring/user-v2/runs/${receipt.user_run_id}`, { headers: { 'X-TokenScope-Instance-Id': receipt.service_instance_id } }).then(r => r.json())).state, r), { timeout: 60000, intervals: [1000] }).toBe('ready');
        await openUser(page, r.user_run_id);
        await expect(page.locator('.metric-grid .metric')).toHaveCount(6);
        await expect(page.locator('.filter-meta').first()).toContainText(r.user_run_id);
        if (i === 1) {
            await page.setViewportSize({ width: 1440, height: 1000 });
            await page.screenshot({ path: 'artifacts/validation/viewer/monitoring-v2/MV2-F006/user-desktop.png', fullPage: true });
            await page.screenshot({ path: 'artifacts/validation/viewer/monitoring-v2/MV2-F006/user-viewport.png' });
            await page.getByRole('button', { name: '设置评估条件' }).click();
            await page.getByRole('button', { name: '新建情景', exact: true }).click();
            await page.screenshot({ path: 'artifacts/validation/viewer/monitoring-v2/MV2-F006/scenario-desktop.png' });
            await page.getByRole('button', { name: '关闭弹窗' }).click();
            await page.setViewportSize({ width: 390, height: 844 });
            await page.screenshot({ path: 'artifacts/validation/viewer/monitoring-v2/MV2-F006/user-mobile.png', fullPage: true });
            await page.screenshot({ path: 'artifacts/validation/viewer/monitoring-v2/MV2-F006/user-mobile-viewport.png' });
            expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
            await page.setViewportSize({ width: 1440, height: 1000 });
        }
    }
});
test('active task checks once at 60 seconds, failure survives reload, later success replaces', async ({ page }) => {
    await page.goto('/#/users');
    const old = await user(page);
    await openUser(page, old.user_run_id);
    await expect(page.locator('.metric-grid')).toBeVisible();
    const oldMetrics = await page.locator('.metric-grid').innerText();
    let calls = 0;
    await page.route('**/monitoring/user-v2/runs/poll-fixture', route => { calls++; return route.fulfill({ json: { ...old, user_run_id: 'poll-fixture', state: calls === 1 ? 'indexing' : 'failed', error_code: calls === 1 ? null : 'SYNTHETIC_FAILURE' } }); });
    await page.clock.install();
    await openUser(page, 'poll-fixture');
    await page.clock.fastForward(59999);
    expect(calls).toBe(1);
    await page.clock.fastForward(1);
    await expect(page.getByRole('alert')).toContainText('SYNTHETIC_FAILURE');
    expect(calls).toBe(2);
    await page.clock.fastForward(180000);
    expect(calls).toBe(2);
    expect(await page.locator('.metric-grid').innerText()).toBe(oldMetrics);
    await page.reload();
    await expect(page.locator('.metric-grid')).toBeVisible();
    await expect(page.getByRole('alert')).toContainText('SYNTHETIC_FAILURE');
    expect(await page.locator('.metric-grid').innerText()).toBe(oldMetrics);
    const fresh = await user(page, 2);
    await openUser(page, fresh.user_run_id);
    await expect(page.locator('.filter-meta').first()).toContainText(fresh.user_run_id);
    await expect(page.locator('.filter-main')).toContainText('Qwen');
});
test('MA visual, failed task and reload preserve historical UUIDs', async ({ page }) => {
    await page.goto('/#/ma');
    const catalog = await page.evaluate(() => fetch('/monitoring/ma/catalog').then(r => r.json()));
    const entry = catalog.entries.find((e: {
        model_standard_name: string;
    }) => e.model_standard_name === 'synthetic-q-64K');
    expect(entry).toBeTruthy();
    await page.getByText('按已知运行ID打开', { exact: true }).click();
    await page.getByLabel('MA运行ID').fill(entry.ma_run_id);
    await page.getByRole('button', { name: '打开MA运行' }).click();
    await expect(page.locator('.ma-table tbody tr')).toHaveCount(13);
    await expect(page.getByRole('button', { name: '查看画像' })).toHaveCount(13);
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.screenshot({ path: 'artifacts/validation/viewer/monitoring-v2/MV2-F006/ma-desktop.png', fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: 'artifacts/validation/viewer/monitoring-v2/MV2-F006/ma-mobile.png', fullPage: true });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const r = await page.evaluate(id => fetch(`/monitoring/ma/runs/${id}`).then(r => r.json()), entry.ma_run_id);
    await page.route('**/monitoring/ma/runs/failed-fixture', route => route.fulfill({ json: { ...r, ma_run_id: 'failed-fixture', state: 'interrupted', error_code: 'SYNTHETIC_INTERRUPTION' } }));
    await page.getByLabel('MA运行ID').fill('failed-fixture');
    await page.getByRole('button', { name: '打开MA运行' }).click();
    await expect(page.getByRole('alert')).toContainText('SYNTHETIC_INTERRUPTION');
    await expect(page.locator('.ma-table tbody tr')).toHaveCount(13);
    await page.reload();
    await expect(page.locator('.ma-table tbody tr')).toHaveCount(13);
    await expect(page.getByRole('alert')).toContainText('SYNTHETIC_INTERRUPTION');
});
test('service identity change stops old scope without automatic submission', async ({ page }) => {
    await page.goto('/#/users');
    const r = await user(page);
    await openUser(page, r.user_run_id);
    await expect(page.locator('.metric-grid')).toBeVisible();
    let posts = 0;
    page.on('request', r => { if (r.method() === 'POST')
        posts++; });
    await page.route(`**/monitoring/user-v2/runs/${r.user_run_id}`, route => route.fulfill({ status: 409, json: { error: { code: 'INSTANCE_MISMATCH', message: 'changed' } } }));
    await page.getByRole('button', { name: '刷新状态', exact: true }).click();
    await expect(page.getByText('服务身份已变化，已停止旧任务查询。请重新连接并选择运行。')).toBeVisible();
    await expect(page.locator('.metric-grid')).toHaveCount(0);
    expect(posts).toBe(0);
});

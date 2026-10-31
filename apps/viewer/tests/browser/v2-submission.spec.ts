import { test, expect } from '@playwright/test';
test('user form lost response retries same key and supports historical binding', async ({ page }) => {
    test.skip(process.env.TOKENSCOPE_REAL_BACKEND !== '1', 'isolated backend');
    await page.goto('/#/users');
    await page.clock.install();
    let lost = true;
    const keys: string[] = [];
    let receipt: {
        user_run_id: string;
        base_run_id: string | null;
    } | undefined;
    await page.route('**/monitoring/user-v2/runs', async (route) => { keys.push(route.request().postDataJSON().submission_key); const response = await route.fetch(); receipt = await response.json(); if (lost) {
        lost = false;
        await route.abort();
    }
    else
        await route.fulfill({ response }); });
    await page.getByRole('button', { name: '新建分析', exact: true }).click();
    await page.locator('input[name=file_ref]').fill('model-1.csv');
    await page.locator('input[name=common_name]').fill('GLM-V5.2');
    await page.getByRole('button', { name: '确认提交' }).click();
    await expect(page.locator('dialog [role=alert]')).toContainText('提交结果待确认');
    await page.getByRole('button', { name: '确认提交' }).click();
    await expect.poll(() => keys.length).toBe(2);
    expect(keys[0]).toBe(keys[1]);
    await expect(page.getByRole('dialog')).toHaveCount(0);
    await expect(page.locator('.v2-task')).toContainText(receipt!.user_run_id);
    await expect.poll(async () => page.evaluate(async (id) => { const c = await fetch('/monitoring/catalog').then(r => r.json()); return (await fetch(`/monitoring/user-v2/runs/${id}`, { headers: { 'X-TokenScope-Instance-Id': c.service_instance_id } }).then(r => r.json())).state; }, receipt!.user_run_id), { timeout: 20000, intervals: [500] }).toBe('ready');
    await page.clock.fastForward(60000);
    await expect(page.locator('.metric-grid')).toBeVisible();
    const legacy = await page.evaluate(async () => { const c = await fetch('/monitoring/catalog').then(r => r.json()); const key = crypto.randomUUID(); const run = await fetch('/analysis-runs', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-TokenScope-Instance-Id': c.service_instance_id }, body: JSON.stringify({ submission_key: key, file_ref: 'model-1.csv', model_id: 'GLM-5.2' }) }).then(r => r.json()); return { key, run_id: run.run_id, instance: c.service_instance_id }; });
    await expect.poll(async () => page.evaluate(async (x) => (await fetch(`/analysis-submissions/${x.key}`, { headers: { 'X-TokenScope-Instance-Id': x.instance } }).then(r => r.json())).status, legacy), { timeout: 20000, intervals: [500] }).toBe('completed');
    const r = { base_run_id: legacy.run_id };
    await page.getByRole('button', { name: '打开运行', exact: true }).click();
    await page.getByRole('button', { name: '绑定基础结果', exact: true }).click();
    await page.locator('input[name=base_run_id]').fill(r.base_run_id);
    await page.locator('input[name=common_name]').fill('GLM-V5.2');
    await page.getByRole('button', { name: '确认提交' }).click();
    await expect(page.getByRole('dialog')).toHaveCount(0);
    await page.getByRole('button', { name: '刷新状态', exact: true }).click();
    await expect(page.locator('.metric-grid')).toBeVisible();
});
test('MA submission form accepts explicit continuous UTC windows', async ({ page }) => {
    test.skip(process.env.TOKENSCOPE_REAL_BACKEND !== '1', 'isolated backend');
    await page.goto('/#/ma');
    await page.getByRole('button', { name: '新建MA分析' }).click();
    for (const [k, v] of Object.entries({ pre_file_ref: 'mv2-pre.csv', now_file_ref: 'mv2-now.csv', model_standard_name: 'synthetic-q-form', pre_start: '2026-10-20T07:00:00Z', now_start: '2026-10-20T08:00:00Z', now_end: '2026-10-20T09:00:00Z' }))
        await page.locator(`input[name=${k}]`).fill(v);
    await page.locator('select[name=model_id]').selectOption('Qwen3.6-27B');
    await page.getByRole('button', { name: '提交MA分析' }).click();
    await expect(page.getByRole('dialog')).toHaveCount(0);
    await expect(page.locator('.v2-task')).toBeVisible();
    await page.getByRole('button', { name: '刷新状态', exact: true }).click();
});

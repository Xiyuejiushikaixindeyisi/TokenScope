import { test, expect, type Page } from '@playwright/test';
import { validateV2 } from '../../src/api/v2/client';
test.beforeEach(() => test.skip(process.env.TOKENSCOPE_REAL_BACKEND !== '1', 'Coordinator-owned cold HTTP environment only'));
async function seed(page: Page, key = 'hv2-ma-matrix') {
    const catalog = await (await page.request.get('/monitoring/catalog')).json();
    const headers = { 'X-TokenScope-Instance-Id': catalog.service_instance_id };
    const created = await page.request.post('/monitoring/ma/runs', { headers, data: { submission_key: key, pre_file_ref: 'hv2-ma-matrix-pre.csv', now_file_ref: 'hv2-ma-matrix-now.csv', model_id: 'Qwen3.6-27B', model_standard_name: key, pre_start: '2026-10-20T07:00:00Z', now_start: '2026-10-20T08:00:00Z', now_end: '2026-10-20T09:00:00Z', source_timezone: 'UTC' } });
    expect(created.ok()).toBe(true); const receipt = validateV2('ma', 'Receipt', await created.json());
    await expect.poll(async () => (await (await page.request.get(`/monitoring/ma/runs/${receipt.ma_run_id}`, { headers })).json()).state, { timeout: 90000, intervals: [500, 1000] }).toBe('completed');
    return { receipt, headers };
}
async function open(page: Page, id: string) {
    if (!await page.getByLabel('MA运行ID').isVisible()) await page.getByText('按已知运行ID打开', { exact: true }).click();
    await page.getByLabel('MA运行ID').fill(id); await page.getByRole('button', { name: '打开MA运行' }).click();
    await expect(page.locator('.filter-meta')).toContainText(id);
}
const pct = (n: number | null) => n === null ? '—' : `${(n * 100).toFixed(1)}%`;
test('real HTTP 13 UUIDs: independent/paired/partial/0/null match frozen responses and bins', async ({ page }, info) => {
    test.setTimeout(120000); await page.goto('/#/ma'); const { receipt, headers } = await seed(page); await open(page, receipt.ma_run_id);
    const rows = page.locator('.ma-table tbody tr'); await expect(rows).toHaveCount(13);
    const evidence = [];
    for (const row of await rows.all()) {
        const id = await row.locator('.uuid').innerText();
        const prefix = `/monitoring/ma/runs/${receipt.ma_run_id}/instances/${encodeURIComponent(id)}`;
        const snapshot = validateV2('ma', 'Snapshot', await (await page.request.get(prefix, { headers })).json());
        const availability = validateV2('ma', 'AvailabilityResponse', await (await page.request.get(prefix + '/availability', { headers })).json());
        await expect(row.locator('[data-availability]').first()).toBeVisible();
        await expect(row.locator('.hit-line b').nth(0)).toHaveText(pct(snapshot.instance.paired_ideal.hit_rate));
        await expect(row.locator('.hit-line b').nth(1)).toHaveText(pct(snapshot.instance.paired_real.hit_rate));
        await expect(row).toContainText(`独立理想 ${pct(snapshot.instance.ideal.hit_rate)}`);
        await expect(row).toContainText(`独立真实 ${pct(snapshot.instance.real.hit_rate)}`);
        await expect(row.locator('td').nth(5)).toContainText(snapshot.instance.hour.uncached_tokens ?? '—');
        await row.getByRole('button', { name: '展开详情' }).click();
        const detail = page.locator('.ma-detail'); await detail.getByText('独立指标、覆盖与运行条件', { exact: true }).click();
        await expect(detail).toContainText(`理想回放有效 E ${availability.availability.coverage.encoded}`);
        await detail.getByText('查看12桶数值', { exact: true }).nth(1).click();
        const bins = detail.locator('.trend-grid details').nth(1).locator('tbody tr'); await expect(bins).toHaveCount(12);
        for (let n = 0; n < 12; n++) await expect(bins.nth(n).locator('[data-availability]')).toHaveAttribute('data-availability', availability.availability.bins[n]!.state);
        evidence.push({ id, snapshot, availability });
        await row.getByRole('button', { name: '收起详情' }).click();
    }
    await info.attach('synthetic-real-http-matrix', { body: JSON.stringify(evidence), contentType: 'application/json' });
    await page.screenshot({ path: info.outputPath('ma-availability.png'), fullPage: true });
});
test('real snapshot plus injected historical409 /503/wrong UUID; only failed row retries', async ({ page }) => {
    test.setTimeout(120000); await page.goto('/#/ma'); const { receipt } = await seed(page);
    let failures = 0, posts = 0; page.on('request', r => { if (r.method() === 'POST') posts++; });
    await page.route('**/instances/*/availability', async route => {
        const id = route.request().url().split('/instances/')[1]!;
        if (id.startsWith('00-')) return route.fulfill({ status: 409, json: { error: { code: 'AVAILABILITY_NOT_RECORDED', message: 'synthetic historical fault injection' } } });
        if (id.startsWith('01-') && failures++ === 0) return route.fulfill({ status: 503, json: { error: { code: 'UNAVAILABLE', message: 'temporary' } } });
        const response = await route.fetch();
        if (id.startsWith('02-')) { const body = await response.json(); body.availability.instance_uuid = 'wrong'; return route.fulfill({ json: body }); }
        return route.fulfill({ response });
    });
    await open(page, receipt.ma_run_id);
    const rows = page.locator('.ma-table tbody tr');
    await expect(rows.filter({ hasText: '00-source_cached_missing' })).toContainText('历史结果未记录细化原因');
    const retry = rows.filter({ hasText: '01-warmup_order_conflict' }).getByRole('button', { name: '重试指标说明' });
    await retry.click(); await expect(retry).toHaveCount(0);
    await expect(rows.filter({ hasText: '02-no_valid_prompt' })).toContainText('范围不一致');
    await expect(rows).toHaveCount(13); expect(posts).toBe(0);
});
test('delayed real explanations: at most four, scope switch cancels queue, late response cannot restore', async ({ page }) => {
    test.setTimeout(120000); await page.goto('/#/ma'); const old = await seed(page), next = await seed(page, 'hv2-ma-second');
    const pending: (() => void)[] = []; let oldReads = 0, active = 0, maximum = 0;
    await page.route(`**/runs/${old.receipt.ma_run_id}/instances/*/availability`, async route => {
        oldReads++; active++; maximum = Math.max(maximum, active);
        const response = await route.fetch(); await new Promise<void>(resolve => pending.push(resolve));
        await route.fulfill({ response }).catch(() => {}); active--;
    });
    await open(page, old.receipt.ma_run_id); await expect(page.locator('.ma-table tbody tr')).toHaveCount(13);
    await expect.poll(() => pending.length).toBe(4); expect(oldReads).toBe(4);
    await open(page, next.receipt.ma_run_id);
    await expect(page.locator('.ma-table [data-availability]').first()).toBeVisible();
    pending.forEach(release => release()); await expect.poll(() => active).toBe(0);
    expect(oldReads).toBe(4); expect(maximum).toBe(4);
    await expect(page.locator('.filter-meta')).toContainText(next.receipt.ma_run_id);
});
test('real identity 409 on availability clears old MA scope without POST', async ({ page }) => {
    test.setTimeout(120000); await page.goto('/#/ma'); const { receipt } = await seed(page); let posts = 0;
    page.on('request', r => { if (r.method() === 'POST') posts++; });
    await page.route('**/instances/*/availability', async route => {
        const response = await route.fetch({ headers: { ...route.request().headers(), 'X-TokenScope-Instance-Id': 'expired' } });
        expect(response.status()).toBe(409); await route.fulfill({ response });
    });
    await open(page, receipt.ma_run_id).catch(() => {});
    await expect(page.getByRole('button', { name: '重新连接' })).toBeVisible();
    await expect(page.locator('.ma-table')).toHaveCount(0); expect(posts).toBe(0);
});

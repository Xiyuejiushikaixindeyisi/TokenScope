import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { test, expect } from '@playwright/test';
const sample = (name: string) => JSON.parse(readFileSync(new URL(`../../../../docs/contracts/examples/monitoring-view-s0/${name}.json`, import.meta.url), 'utf8'));
test('synthetic contract dashboard: scope, histogram cache, requests, safe detail and 390px', async ({ page }, testInfo) => {
  let snapshots = 0; const queries: string[] = []; const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.route('**/monitoring/catalog**', route => route.fulfill({ contentType: 'application/json', json: sample('catalog-normal') }));
  await page.route('**/monitoring/events**', route => route.fulfill({ contentType: 'text/event-stream', body: ': synthetic fixture\n\n' }));
  await page.route('**/monitoring/runs**', route => { const body = sample('runs-no-valid-rows'); body.items[0].status = 'completed'; body.items[0].group_count = '1'; return route.fulfill({ json: body }); });
  await page.route('**/analysis-runs/**', route => {
    const url = new URL(route.request().url()); queries.push(url.pathname + url.search);
    if (url.pathname.endsWith('/view-snapshot')) { snapshots++; const raw = JSON.stringify(sample('snapshot-normal')); return route.fulfill({ contentType: 'application/json', headers: { ETag: '"' + createHash('sha256').update(raw).digest('hex') + '"' }, body: raw }); }
    if (url.pathname.endsWith('/view-signals')) return route.fulfill({ json: sample('signals-normal') });
    if (url.pathname.endsWith('/evidence')) return route.fulfill({ json: sample('evidence-' + (url.searchParams.get('section') ?? 'special_ranges')) });
    if (url.pathname.endsWith('/requests')) { const body = sample('requests-duplicate-hash'); body.offset = url.searchParams.get('offset') ?? '0'; body.limit = Number(url.searchParams.get('limit') ?? '50'); body.sort.by = url.searchParams.get('sort_by') ?? 'prompt_tokens'; return route.fulfill({ json: body }); }
    if (/\/requests\/\d+$/.test(url.pathname)) { const body = sample('request-detail'); body.body_preview.text = '<img src=x onerror="window.injected=true">'; return route.fulfill({ json: body }); }
    return route.fulfill({ status: 404, json: { error: { code: 'REQUEST_NOT_FOUND', message: 'Synthetic fixture only' } } });
  });
  await page.goto('/#/overview'); await expect(page.getByText('理想命中率', { exact: true })).toBeVisible();
  await expect(page.getByText('0.00%', { exact: true })).toBeVisible();
  await expect(page.locator('.metric-grid')).toContainText('80');
  const snapshotCount = snapshots;
  await page.getByRole('link', { name: '请求长度分布' }).click();
  await page.getByLabel('分箱宽度').selectOption('1000'); await expect(page.locator('svg rect')).toHaveCount(603);
  await page.getByLabel('分箱宽度').selectOption('2000'); await expect(page.locator('svg rect')).toHaveCount(303);
  await page.getByLabel('分箱宽度').selectOption('5000'); await page.getByLabel('显示请求占比').check();
  expect(snapshots).toBe(snapshotCount);
  await page.getByRole('button', { name: /≥200K Token/ }).first().click();
  await expect(page.getByRole('heading', { name: '请求明细', exact: true }).first()).toBeVisible();
  await expect(page.locator('tbody tr')).toHaveCount(2);
  expect(queries.some(q => q.includes('lower=200000') && !q.includes('upper='))).toBe(true);
  await page.getByRole('button', { name: '查看请求 1', exact: true }).click(); await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('dialog')).toContainText('<img src=x'); expect(await page.evaluate(() => 'injected' in window)).toBe(false);
  await page.getByRole('button', { name: '关闭详情' }).click();
  await page.getByLabel('辅助排名图（每段至多1000点）').check(); await expect(page.locator('canvas')).toBeVisible();
  await page.getByRole('link', { name: '监控概览' }).click(); await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await testInfo.attach('monitoring-mobile', { body: await page.screenshot({ fullPage: true }), contentType: 'image/png' });
  await page.setViewportSize({ width: 1440, height: 1000 }); await testInfo.attach('monitoring-desktop', { body: await page.screenshot({ fullPage: true }), contentType: 'image/png' });
  await testInfo.attach('network', { body: JSON.stringify({ snapshots, queries, errors }), contentType: 'application/json' });
  expect(errors).toEqual([]);
});

test('F007 long scope and source labels do not overflow a narrow viewport', async ({ page }) => {
  const catalog = sample('catalog-normal'), snapshot = sample('snapshot-null-rate');
  const longApp = 'tenant-' + 'long-name-'.repeat(24);
  catalog.items[0].appid = longApp; snapshot.identity.appid = longApp;
  snapshot.provenance.source_label = 'source/' + 'long-file-name-'.repeat(30) + '.csv';
  await page.route('**/monitoring/catalog**', r => r.fulfill({ json: catalog }));
  await page.route('**/monitoring/events**', r => r.fulfill({ contentType: 'text/event-stream', body: ': fixture\n\n' }));
  await page.route('**/view-snapshot**', r => { const raw = JSON.stringify(snapshot); return r.fulfill({ contentType: 'application/json', headers: { ETag: '"' + createHash('sha256').update(raw).digest('hex') + '"' }, body: raw }); });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/#/overview'); await expect(page.locator('.metric')).toHaveCount(6);
  await expect(page.locator('.metric.hit strong')).toHaveText('—');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.getByText('数据质量与版本', { exact: true }).click();
  await expect(page.locator('.metadata-body')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

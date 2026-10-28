import { readFileSync } from 'node:fs';
import { test, expect } from '@playwright/test';
// Read-only real-service presentation checks; no POST/PUT/DELETE and no joint acceptance claim.
test('F007 approved reference, real-service layout, exact values and export entry', async ({ page, request, browser }, info) => {
  test.skip(process.env.TOKENSCOPE_VISUAL_REAL !== '1', 'Opt-in read-only real service');
  test.setTimeout(120000);
  const catalog = await (await request.get('/monitoring/catalog')).json();
  const errors: string[] = [], writes: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { if (!['GET', 'HEAD', 'OPTIONS'].includes(r.method())) writes.push(r.method() + ' ' + r.url()); });
  const reference = readFileSync(new URL('../../../../artifacts/prototypes/monitoring-v1/tokenscope-monitoring-demo.html', import.meta.url), 'utf8');
  await page.route('**/__f007-reference', r => r.fulfill({ contentType: 'text/html', body: reference }));
  for (const width of [1440, 1280, 390]) {
    await page.setViewportSize({ width, height: width === 1440 ? 900 : width === 1280 ? 800 : 844 });
    await page.goto('/__f007-reference');
    await expect(page.locator('#metricCards .metric')).toHaveCount(6);
    await info.attach(`reference-${width}`, { body: await page.screenshot({ fullPage: true, path: info.outputPath(`reference-${width}.png`) }), contentType: 'image/png' });
    await page.goto('/#/overview'); await expect(page.locator('.metric')).toHaveCount(6);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(await page.locator('.sidebar').evaluate(el => Math.round(el.getBoundingClientRect().width))).toBe(width > 760 ? 208 : width);
    expect(await page.locator('.metric-grid').evaluate(el => getComputedStyle(el).gridTemplateColumns.split(' ').length)).toBe(width > 900 ? 3 : 2);
    await expect(page.getByText('当前完整结果', { exact: true })).toHaveCount(0);
    await info.attach(`actual-${width}`, { body: await page.screenshot({ fullPage: true, path: info.outputPath(`actual-${width}.png`) }), contentType: 'image/png' });
  }
  await page.setViewportSize({ width: 1440, height: 900 });
  for (const model of ['GLM-5.2', 'Qwen3.6-27B', 'DeepSeek-V4-Flash-0731']) {
    const item = catalog.items.find((i: { model_id: string }) => i.model_id === model);
    await page.goto('/#/overview?' + new URLSearchParams({ appid: item.appid, model }));
    const snapshot = await (await request.get(`/analysis-runs/${item.active_run_id}/view-snapshot`, { params: { appid: item.appid } })).json();
    await expect(page.locator('.metadata-body')).toContainText(item.active_run_id);
    await page.getByText('查看精确 Token 总量', { exact: true }).click();
    for (const value of Object.values(snapshot.metrics.totals)) await expect(page.locator('.exact-values')).toContainText(BigInt(value as string).toLocaleString('zh-CN'));
    await page.getByText('查看精确 Token 总量', { exact: true }).click();
  }
  const anotherApp = catalog.items.find((i: { appid: string }) => i.appid !== catalog.items[0].appid).appid;
  await page.getByLabel('appid', { exact: true }).selectOption(anotherApp);
  await expect(page.getByLabel('appid', { exact: true })).toHaveValue(anotherApp);
  await expect(page.locator('.metric')).toHaveCount(6);
  await page.getByText('数据质量与版本', { exact: true }).click();
  await expect(page.locator('.metadata-body')).toBeVisible();
  await info.attach('actual-metadata', { body: await page.screenshot({ path: info.outputPath('actual-metadata.png') }), contentType: 'image/png' });
  await page.getByText('数据质量与版本', { exact: true }).click();
  await page.getByText('选择历史完整运行', { exact: true }).click();
  await expect(page.getByText('包含未产生有效请求的运行', { exact: true })).toBeVisible();
  await info.attach('actual-history', { body: await page.screenshot({ path: info.outputPath('actual-history.png') }), contentType: 'image/png' });
  await page.getByText('选择历史完整运行', { exact: true }).click();
  await page.getByText('导出', { exact: true }).click();
  await info.attach('actual-export', { body: await page.screenshot({ path: info.outputPath('actual-export.png') }), contentType: 'image/png' });
  await page.evaluate(() => Object.defineProperty(window, 'showSaveFilePicker', { value: undefined, configurable: true }));
  const downloaded = page.waitForEvent('download');
  await page.getByRole('button', { name: '导出 NDJSON', exact: true }).click();
  const file = await downloaded; await expect(page.getByRole('status')).toContainText('SHA256 与记录数一致');
  await file.saveAs(info.outputPath('readonly-export.ndjson'));
  await page.getByText('导出', { exact: true }).click();
  await page.getByRole('link', { name: '请求明细', exact: true }).click();
  await expect(page.locator('tbody tr')).toHaveCount(50);
  await page.locator('tbody button').first().click(); await expect(page.getByRole('dialog')).toBeVisible();
  await info.attach('actual-request-detail', { body: await page.screenshot({ path: info.outputPath('actual-request-detail.png') }), contentType: 'image/png' });
  await page.getByRole('button', { name: '关闭详情' }).click();
  await page.getByRole('link', { name: '运行设置', exact: true }).click(); await expect(page.getByLabel('Block size')).toBeVisible();
  await info.attach('actual-settings', { body: await page.screenshot({ fullPage: true, path: info.outputPath('actual-settings.png') }), contentType: 'image/png' });
  expect(errors).toEqual([]); expect(writes).toEqual([]);
  await info.attach('identity', { body: JSON.stringify({ browser: browser.version(), baseURL: info.project.use.baseURL, errors, writes, scopes: catalog.items.length }), contentType: 'application/json' });
});

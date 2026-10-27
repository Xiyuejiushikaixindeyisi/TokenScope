import { test, expect } from '@playwright/test';
test('real dev6: UI submission, SSE completion, 15 scopes, details and verified export', async ({ page, request }, info) => {
  test.skip(process.env.TOKENSCOPE_REAL_BACKEND !== '1', 'Opt-in independent synthetic state; not final joint acceptance'); test.setTimeout(120000);
  const errors: string[] = []; page.on('pageerror', e => errors.push(e.message));
  await page.goto('/#/submissions'); await expect(page.getByText('通知已连接', { exact: false })).toBeVisible();
  for (const [i, model] of ['GLM-5.2', 'Qwen3.6-27B', 'DeepSeek-V4-Flash-0731'].entries()) {
    await page.getByLabel('file_ref').fill(`model-${i+1}.csv`); await page.locator('.panel label').filter({ hasText: /^模型 / }).locator('select').selectOption(model); await page.getByLabel('确认启动该文件的监控计算').check(); await page.getByRole('button', { name: '提交监控任务', exact: true }).click();
    await expect(page.locator('.signal').filter({ hasText: `model-${i+1}.csv` })).toContainText('completed', { timeout: 60000 });
  }
  const catalog = await (await request.get('/monitoring/catalog')).json(); expect(catalog.items).toHaveLength(15);
  await page.getByRole('link', { name: '监控概览' }).click(); await expect(page.locator('.metric-grid')).toBeVisible();
  await page.locator('.scope-bar label').filter({ hasText: /^模型 / }).locator('select').selectOption('Qwen3.6-27B'); await expect(page.getByText('当前范围：', { exact: false })).toContainText('Qwen3.6-27B');
  await page.getByRole('link', { name: '请求明细' }).click(); await expect(page.locator('tbody tr')).toHaveCount(50); await page.locator('tbody button').first().click(); await expect(page.getByRole('dialog')).toContainText('synthetic-'); await page.getByRole('button', { name: '关闭详情' }).click();
  await page.evaluate(() => Object.defineProperty(window, 'showSaveFilePicker', { configurable: true, value: undefined }));
  const download = page.waitForEvent('download'); await page.getByRole('button', { name: '导出 NDJSON' }).click(); const result = await download; await expect(page.getByRole('status')).toContainText('SHA256 与记录数一致'); await result.saveAs(info.outputPath('real-requests.ndjson'));
  await page.getByRole('link', { name: '运行设置' }).click(); await expect(page.getByLabel('Block size')).toHaveValue('1536'); await page.getByRole('link', { name: '监控信号' }).click(); await expect(page.getByText('当前运行无监控信号。')).toBeVisible();
  await info.attach('real-dev6-desktop', { body: await page.screenshot({ fullPage: true }), contentType: 'image/png' }); await info.attach('catalog', { body: JSON.stringify(catalog), contentType: 'application/json' }); expect(errors).toEqual([]);
});

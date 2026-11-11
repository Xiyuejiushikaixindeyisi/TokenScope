// Real same-origin candidate only. No routes, API mocks, recipe injection or old state.
import { createRequire } from 'node:module';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
const project = '/home/zhangxiyue/TokenScope';
const require = createRequire(project + '/apps/viewer/package.json');
const { chromium, expect } = require('@playwright/test');
const root = process.argv[2], origin = process.argv[3];
const cases = JSON.parse(await readFile(path.join(root, 'cases.json'), 'utf8'));
const browser = await chromium.launch({ executablePath: project + '/env/browser-cache/chromium-1248/chrome-linux64/chrome', headless: true, env: { ...process.env, LD_LIBRARY_PATH: project + '/env/browser-deps-v3/root/usr/lib/x86_64-linux-gnu', FONTCONFIG_FILE: project + '/env/browser-deps-v3/fonts.conf' } });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
const page = await context.newPage();
const posts = [], errors = [], results = [];
page.on('request', request => { if (request.method() === 'POST') posts.push(request.url()); });
page.on('pageerror', error => errors.push(String(error)));
try {
  await page.goto(origin + '/#/analysis');
  await expect(page.getByLabel('小样本分析来源')).toBeVisible();
  await expect(page.getByRole('button', { name: '分析当前来源', exact: true })).toBeEnabled({ timeout: 30000 });
  if (posts.length) throw Error('Browse submitted analysis');
  await expect(page.locator('body')).not.toContainText('EXECUTION_CAPABILITY_MISMATCH');
  for (const item of cases) {
    await page.getByLabel('小样本来源APPID').fill(item.appid);
    await page.getByRole('button', { name: '筛选来源', exact: true }).click();
    await expect(page.getByLabel('小样本分析来源').locator('option').first()).toContainText(item.appid);
    const count = posts.length;
    await page.getByRole('button', { name: '分析当前来源', exact: true }).click();
    await expect(page.getByRole('button', { name: '分析当前来源', exact: true })).toBeEnabled({ timeout: 240000 });
    const report = page.getByRole('region', { name: '小样本实算报告' });
    await expect(report).toContainText(item.appid, { timeout: 30000 });
    if (!item.prefix_rule) await expect(report).toContainText('NORMALIZED');
    if (!item.evidence_only) await expect(report).toContainText('参考提升率');
    if (item.prefix_rule) {
      if (!item.evidence_only) await expect(report).toContainText('自动发现 ' + item.prefix_rule);
      await report.locator('summary').filter({ hasText: 'L1/L2/L3/L4/L5 差异请求对照' }).click();
      const evidence = report.locator('.sample-evidence').filter({ has: page.locator('summary').filter({ hasText: new RegExp('^' + item.prefix_rule + ' ·') }) }).first();
      await evidence.locator('summary').click();
      await expect(evidence.locator('pre')).toHaveCount(2);
      for (const pre of await evidence.locator('pre').all()) {
        const body = JSON.parse(await pre.innerText());
        if (!body.messages) throw Error('Missing complete request body');
      }
    }
    if (item.large) await expect(report).toContainText('已自动缩样');
    const task = await page.getByLabel('样本分析历史').inputValue();
    if (posts.length !== count + 2) throw Error('Expected one prepare and one diagnosis POST');
    await page.screenshot({ path: path.join(root, item.appid + '.png'), fullPage: true });
    const text = await report.innerText();
    await writeFile(path.join(root, item.appid + '-page.txt'), text, { flag: 'wx' });
    const beforeRefresh = posts.length;
    await page.reload();
    await expect(page.getByLabel('样本分析历史')).toHaveValue(task, { timeout: 30000 });
    await expect(page.getByRole('region', { name: '小样本实算报告' })).toContainText(item.appid);
    await context.setOffline(true);
    await page.getByRole('button', { name: '重新读取结果', exact: true }).click();
    await expect(page.getByRole('region', { name: '小样本实算报告' })).toContainText(item.appid);
    await context.setOffline(false);
    await page.getByRole('button', { name: '重新读取结果', exact: true }).click();
    await expect(page.getByRole('region', { name: '小样本实算报告' })).toContainText(item.evidence_only ? item.appid : '参考提升率');
    if (posts.length !== beforeRefresh) throw Error('Refresh/reconnect submitted analysis');
    results.push({ ...item, task, refresh_get_only: true });
  }
  if (errors.length) throw Error(errors.join('\n'));
  await writeFile(path.join(root, 'browser-results.json'), JSON.stringify({ results, posts, errors }, null, 2), { flag: 'wx' });
} catch (error) {
  await page.screenshot({ path: path.join(root, 'failure.png'), fullPage: true });
  await writeFile(path.join(root, 'failure.txt'), String(error) + '\n' + await page.locator('body').innerText(), { flag: 'wx' });
  throw error;
} finally { await browser.close(); }

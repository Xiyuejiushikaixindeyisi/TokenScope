import { createRequire } from 'node:module';
import { readFile, writeFile } from 'node:fs/promises';
const project = '/home/zhangxiyue/TokenScope';
const { chromium, expect } = createRequire(project + '/apps/viewer/package.json')('@playwright/test');
const root = process.argv[2], origin = process.argv[3];
const previous = JSON.parse(await readFile(root + '/browser-results.json', 'utf8'));
const browser = await chromium.launch({ executablePath: project + '/env/browser-cache/chromium-1248/chrome-linux64/chrome', headless: true,
  env: { ...process.env, LD_LIBRARY_PATH: project + '/env/browser-deps-v3/root/usr/lib/x86_64-linux-gnu', FONTCONFIG_FILE: project + '/env/browser-deps-v3/fonts.conf' } });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
const page = await context.newPage(), posts = [];
page.on('request', request => { if (request.method() === 'POST') posts.push(request.url()); });
try {
  await page.goto(origin + '/#/analysis');
  await expect(page.getByLabel('样本分析历史').locator('option')).toHaveCount(previous.results.length + 1, { timeout: 30000 });
  await expect(page.locator('body')).not.toContainText('EXECUTION_CAPABILITY_MISMATCH');
  for (const item of previous.results) {
    await page.getByLabel('样本分析历史').selectOption(item.task);
    await expect(page.getByRole('region', { name: '小样本实算报告' })).toContainText(item.appid);
    await expect(page.getByRole('region', { name: '小样本实算报告' })).toContainText(item.evidence_only ? item.appid : '参考提升率');
  }
  await page.getByRole('button', { name: 'Token异常分析', exact: true }).click();
  await expect(page.getByRole('heading', { name: '业务优化建议' })).toBeVisible();
  await page.getByRole('button', { name: '低命中率分析', exact: true }).click();
  await expect(page.getByRole('region', { name: '小样本实算报告' })).toBeVisible();
  if (posts.length) throw Error('Restart/history/direction switch submitted analysis');
  await page.screenshot({ path: root + '/restart-browser.png', fullPage: true });
  await writeFile(root + '/restart-browser.json', JSON.stringify({ passed: true, posts, tasks: previous.results.map(x => x.task) }, null, 2), { flag: 'wx' });
} finally { await browser.close(); }

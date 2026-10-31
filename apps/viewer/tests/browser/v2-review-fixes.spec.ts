import { test, expect, type Page } from '@playwright/test';
import { seedUser, seedMA } from './v2-fixtures';
test.beforeEach(() => test.skip(process.env.TOKENSCOPE_REAL_BACKEND !== '1', 'isolated backend required'));
async function openUser(page: Page, id: string) {
  await page.getByRole('button', { name: '打开运行', exact: true }).click();
  await page.locator('input[name=run]').fill(id);
  await page.getByRole('button', { name: '打开', exact: true }).click();
  await expect(page.locator('.filter-meta').first()).toContainText(id);
  await expect(page.locator('.metric-grid')).toBeVisible();
}
async function openMA(page: Page, id: string) {
  if (!await page.getByLabel('MA运行ID').isVisible()) await page.getByText('按已知运行ID打开', { exact: true }).click();
  await page.getByLabel('MA运行ID').fill(id);
  await page.getByRole('button', { name: '打开MA运行' }).click();
}
for (const path of ['catalog', 'snapshot', 'receipt'] as const) test(`RV2-01 real MA identity error: ${path}`, async ({ page }, info) => {
  test.setTimeout(90000);
  await page.goto('/#/ma'); const run = await seedMA(page);
  await openMA(page, run.ma_run_id);
  await expect(page.getByRole('button', { name: '查看画像' })).toHaveCount(13);
  await page.getByRole('button', { name: '查看画像' }).first().click();
  let posts = 0, requests = 0, errorCode = '';
  page.on('request', r => { if (r.method() === 'POST') posts++; });
  let release!: () => void; const gate = new Promise<void>(r => { release = r; });
  const pattern = path === 'catalog' ? '**/monitoring/ma/catalog?*' : path === 'receipt' ? `**/monitoring/ma/runs/${run.ma_run_id}` : '**/monitoring/ma/runs/*/instances/*';
  await page.route(pattern, async route => {
    const order = ++requests;
    if (order === 1) {
      const response = await route.fetch({ headers: { ...route.request().headers(), 'X-TokenScope-Instance-Id': 'expired-rv2-id' } });
      expect(response.status()).toBe(409); errorCode = (await response.json()).error.code;
      await route.fulfill({ response });
    } else {
      const response = await route.fetch(); await gate;
      await route.fulfill({ response }).catch(() => {});
    }
  });
  await page.clock.install(); await page.clock.pauseAt(new Date());
  if (path === 'catalog') await page.getByRole('button', { name: '刷新目录' }).click();
  else if (path === 'receipt') await page.getByRole('button', { name: '刷新状态' }).click();
  else await openMA(page, run.ma_run_id);
  await expect(page.getByRole('button', { name: '重新连接' })).toBeVisible();
  expect(errorCode).toBe('SERVICE_INSTANCE_CHANGED');
  await expect(page.locator('.ma-table')).toHaveCount(0);
  await expect(page.getByRole('button', { name: '查看画像' })).toHaveCount(0);
  const count = requests; release(); await page.clock.fastForward(180000);
  await expect(page.locator('.ma-table')).toHaveCount(0);
  expect(requests).toBe(count); expect(requests).toBeLessThanOrEqual(path === 'snapshot' ? 4 : 1); expect(posts).toBe(0);
  await page.screenshot({ path: info.outputPath(`identity-${path}.png`) });
});
test('RV2-01 ordinary 503 and offline catalog keep historical rows', async ({ page }) => {
  await page.goto('/#/ma'); const run = await seedMA(page); await openMA(page, run.ma_run_id);
  await expect(page.getByRole('button', { name: '查看画像' })).toHaveCount(13);
  let offline = false;
  await page.route('**/monitoring/ma/catalog?*', route => offline ? route.abort() : route.fulfill({ status: 503, json: { error: { code: 'UNAVAILABLE', message: 'temporary' } } }));
  for (const value of [false, true]) {
    offline = value; await page.getByRole('button', { name: '刷新目录' }).click();
    await expect(page.getByRole('alert')).toBeVisible();
    await expect(page.getByRole('button', { name: '刷新目录' })).toBeEnabled();
    await expect(page.getByRole('button', { name: '查看画像' })).toHaveCount(13);
    await expect(page.getByRole('button', { name: '重新连接' })).toHaveCount(0);
  }
});
test('RV2-01 active MA poll receives real identity error and never polls again', async ({ page }) => {
  await page.goto('/#/ma'); const run = await seedMA(page); await openMA(page, run.ma_run_id);
  await expect(page.getByRole('button', { name: '查看画像' })).toHaveCount(13);
  let reads = 0, posts = 0;
  page.on('request', r => { if (r.method() === 'POST') posts++; });
  await page.route(`**/monitoring/ma/runs/${run.ma_run_id}`, async route => {
    if (++reads === 1) return route.fulfill({ json: { ...run, state: 'running', error_code: null } });
    const response = await route.fetch({ headers: { ...route.request().headers(), 'X-TokenScope-Instance-Id': 'expired-rv2' } });
    expect(response.status()).toBe(409); await route.fulfill({ response });
  });
  await page.clock.install(); await page.clock.pauseAt(new Date());
  await openMA(page, run.ma_run_id); await expect(page.locator('.v2-task')).toContainText('处理中');
  await page.clock.fastForward(60000);
  await expect(page.getByRole('button', { name: '重新连接' })).toBeVisible();
  await page.clock.fastForward(180000); expect(reads).toBe(2); expect(posts).toBe(0);
  await expect(page.locator('.ma-table')).toHaveCount(0);
});
for (const format of ['NDJSON', 'CSV']) for (const sink of ['download', 'file-double']) for (const change of ['run', 'appid', 'identity', 'page']) test(`RV2-02 ${format} ${sink} cancel on ${change}`, async ({ page }, info) => {
  test.setTimeout(90000);
  // File picker/writable are controlled doubles. HTTP bytes and Worker validation are real.
  await page.addInitScript(mode => {
    const target = window as unknown as { showSaveFilePicker?: unknown; sinkEvents: string[] };
    target.sinkEvents = [];
    Object.defineProperty(window, 'showSaveFilePicker', { configurable: true, value: mode === 'download' ? undefined : async () => ({ createWritable: async () => ({ write: async () => { target.sinkEvents.push('write'); }, close: async () => { target.sinkEvents.push('close'); }, abort: async () => { target.sinkEvents.push('abort'); } }) }) });
  }, sink);
  await page.goto('/#/users'); const old = await seedUser(page, 1, 'multi-app.csv'), fresh = await seedUser(page, 2);
  await openUser(page, old.user_run_id);
  let release!: () => void; const gate = new Promise<void>(r => { release = r; });
  let fetched = false, released = false, downloads = 0;
  page.on('download', () => downloads++);
  await page.route('**/requests/export?*', async route => {
    const response = await route.fetch(); expect(response.status()).toBe(200); fetched = true;
    await gate; await route.fulfill({ response }).catch(() => {}); released = true;
  });
  await page.getByRole('button', { name: `导出 ${format}`, exact: true }).first().click();
  await expect.poll(() => fetched).toBe(true);
  if (change === 'run') await openUser(page, fresh.user_run_id);
  if (change === 'appid') { await page.getByLabel('用户APPID').selectOption('app-b'); await expect(page.getByLabel('用户APPID')).toHaveValue('app-b'); }
  if (change === 'page') await page.locator('.sidebar a[href="#/users/ranking"]').click();
  if (change === 'identity') {
    await page.route(`**/monitoring/user-v2/runs/${old.user_run_id}`, async route => {
      const response = await route.fetch({ headers: { ...route.request().headers(), 'X-TokenScope-Instance-Id': 'expired-rv2' } });
      expect(response.status()).toBe(409); expect((await response.json()).error.code).toBe('INSTANCE_MISMATCH'); await route.fulfill({ response });
    });
    await page.getByRole('button', { name: '刷新状态' }).click();
    await expect(page.getByRole('button', { name: '重新连接' })).toBeVisible();
  }
  await expect(page.getByRole('button', { name: '取消导出', includeHidden: true })).toHaveCount(0);
  release(); await expect.poll(() => released).toBe(true);
  if (sink === 'file-double') await expect.poll(() => page.evaluate(() => (window as unknown as { sinkEvents: string[] }).sinkEvents)).toContain('abort');
  // Flush callbacks and inspect the new scope, including hidden controls.
  await page.waitForTimeout(100);
  expect(downloads).toBe(0);
  expect(await page.evaluate(() => (window as unknown as { sinkEvents: string[] }).sinkEvents)).not.toContain('close');
  await expect(page.getByText(/条请求校验完成/, { exact: false })).toHaveCount(0);
  await page.screenshot({ path: info.outputPath('after-switch.png') });
});
test('RV2-03 fixed clock: initial/same search never reset page; debounce/Enter cancel stale timer', async ({ page }, info) => {
  await page.goto('/#/users'); const run = await seedUser(page);
  const rank = await page.evaluate(async r => fetch(`/monitoring/user-v2/runs/${r.user_run_id}/rankings`, { headers: { 'X-TokenScope-Instance-Id': r.service_instance_id } }).then(v => v.json()), run);
  await page.clock.install(); await page.clock.pauseAt(new Date());
  await openUser(page, run.user_run_id);
  const queries: { offset: string | null; search: string | null }[] = [];
  await page.route('**/rankings?*', route => {
    const q = new URL(route.request().url()).searchParams, offset = Number(q.get('offset'));
    queries.push({ offset: q.get('offset'), search: q.get('appid_contains') });
    return route.fulfill({ json: { ...rank, total: '25', next_offset: offset === 0 ? '20' : null, rows: Array.from({ length: offset === 0 ? 20 : 5 }, (_, j) => ({ ...rank.rows[0], appid: `APP-${offset+j}` })) } });
  });
  await page.locator('.sidebar a[href="#/users/ranking"]').click();
  const next = page.locator('.v2-pagination').getByRole('button', { name: '下一页' });
  await expect(next).toBeEnabled(); await next.click();
  await expect(page.locator('.v2-rank-table tbody tr')).toHaveCount(5);
  await page.clock.runFor(300);
  await expect(page.locator('.v2-pagination')).toContainText('第2页');
  expect(queries.map(q => q.offset)).toEqual(['0', '20']);
  const search = page.getByLabel('搜索APPID');
  await search.press('Enter'); await page.clock.runFor(300);
  await expect(page.locator('.v2-pagination')).toContainText('第2页');
  await search.fill('old'); await page.clock.runFor(200); await search.fill('%_'); await page.clock.runFor(299);
  await expect(page.locator('.v2-pagination')).toContainText('第2页');
  await page.clock.runFor(1); await expect(page.locator('.v2-pagination')).toContainText('第1页');
  expect(queries.at(-1)).toEqual({ offset: '0', search: '%_' });
  await search.fill('latest'); await search.press('Enter'); await expect(next).toBeEnabled();
  await next.click(); await expect(page.locator('.v2-rank-table tbody tr')).toHaveCount(5);
  await page.clock.runFor(300); await expect(page.locator('.v2-pagination')).toContainText('第2页');
  expect(queries.at(-1)).toEqual({ offset: '20', search: 'latest' });
  await info.attach('queries', { body: JSON.stringify(queries), contentType: 'application/json' });
});
for (const format of ['NDJSON', 'CSV']) for (const sink of ['download', 'file-double']) test(`RV2-02 ${format} ${sink} normal, integrity failures and active cancellation`, async ({ page }) => {
  await page.addInitScript(mode => {
    const target = window as unknown as { sinkEvents: string[] }; target.sinkEvents = [];
    Object.defineProperty(window, 'showSaveFilePicker', { configurable: true, value: mode === 'download' ? undefined : async () => ({ createWritable: async () => ({ write: async () => { target.sinkEvents.push('write'); }, close: async () => { target.sinkEvents.push('close'); }, abort: async () => { target.sinkEvents.push('abort'); } }) }) });
  }, sink);
  await page.goto('/#/users'); const run = await seedUser(page); await openUser(page, run.user_run_id);
  let downloads = 0; page.on('download', () => downloads++);
  const button = page.getByRole('button', { name: `导出 ${format}`, exact: true }).first();
  await button.click(); await expect(page.getByText(/30 条请求校验完成/)).toBeVisible();
  if (sink === 'download') await expect.poll(() => downloads).toBe(1);
  else expect(await page.evaluate(() => (window as unknown as { sinkEvents: string[] }).sinkEvents)).toContain('close');
  const modes = format === 'NDJSON' ? ['digest', 'count', 'offline', 'cancel'] : ['count', 'offline', 'cancel'];
  for (const mode of modes) {
    let release!: () => void; const gate = new Promise<void>(r => { release = r; }); let fetched = false;
    await page.route('**/requests/export?*', async route => {
      if (mode === 'offline') return route.abort();
      const response = await route.fetch(); let body = await response.text(); const headers = response.headers();
      if (mode === 'digest') body = body.replace(/("request_lines_sha256"\s*:\s*")[a-f0-9]{64}/, '$1' + '0'.repeat(64));
      if (mode === 'count') headers['x-export-row-count'] = '999';
      fetched = true;
      if (mode === 'cancel') await gate;
      await route.fulfill({ response, headers, body }).catch(() => {});
    });
    await button.click();
    if (mode === 'cancel') { await expect.poll(() => fetched).toBe(true); await page.getByRole('button', { name: '取消导出' }).click(); release(); await expect(page.getByText(/导出已取消/)).toBeVisible(); }
    else await expect(page.getByText(/导出未完成：/)).toBeVisible();
    await expect(button).toBeEnabled(); await page.unroute('**/requests/export?*');
  }
  expect(downloads).toBe(sink === 'download' ? 1 : 0);
  const events = await page.evaluate(() => (window as unknown as { sinkEvents: string[] }).sinkEvents);
  expect(events.filter(x => x === 'close')).toHaveLength(sink === 'download' ? 0 : 1);
  if (sink === 'file-double') expect(events.filter(x => x === 'abort')).toHaveLength(modes.length);
});

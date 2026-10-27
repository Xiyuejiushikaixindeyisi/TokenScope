import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { test, expect } from '@playwright/test';
const sample = (name: string) => JSON.parse(readFileSync(new URL(`../../../../docs/contracts/examples/monitoring-view-s0/${name}.json`, import.meta.url), 'utf8'));
for (const real of [false, true]) test(`30 cold/hot UI timings (${real ? 'real dev6' : 'contract fake'})`, async ({ browser }, info) => {
  test.skip(real && process.env.TOKENSCOPE_REAL_BACKEND !== '1', 'requires opt-in dev6 synthetic state'); test.setTimeout(180000);
  const timings: { cold: number; rows: number; hot: number }[] = [];
  for (let i = 0; i < 30; i++) {
    const context = await browser.newContext({ baseURL: process.env.TOKENSCOPE_TEST_BASE_URL ?? 'http://127.0.0.1:4173' }); const page = await context.newPage();
    if (!real) {
      await page.route('**/monitoring/catalog**', r => r.fulfill({ json: sample('catalog-normal') })); await page.route('**/monitoring/events**', r => r.fulfill({ contentType: 'text/event-stream', body: ': fixture\n\n' }));
      await page.route('**/view-snapshot**', r => { const raw = JSON.stringify(sample('snapshot-normal')); return r.fulfill({ contentType: 'application/json', headers: { ETag: '"'+createHash('sha256').update(raw).digest('hex')+'"' }, body: raw }); });
      await page.route('**/requests?**', r => { const v = sample('requests-duplicate-hash'); v.items = Array.from({ length: 50 }, (_, index) => ({ ...v.items[0], position: String(index+1), request_ref: { ...v.items[0].request_ref, source_record_index: String(index+1) } })); v.total = '50'; v.limit = 50; v.next_offset = null; return r.fulfill({ json: v }); });
    }
    await page.addInitScript(() => { const record = () => { const w = window as unknown as { uiCold?: number }; if (!w.uiCold && document.querySelector('.metric-grid')) w.uiCold = performance.now(); }; new MutationObserver(record).observe(document, { subtree: true, childList: true }); });
    await page.goto('/#/overview'); await expect(page.locator('.metric-grid')).toBeVisible(); const cold = await page.evaluate(() => (window as unknown as { uiCold: number }).uiCold);
    const rows = await page.evaluate(() => new Promise<number>(resolve => { const start = performance.now(), observer = new MutationObserver(() => { if (document.querySelectorAll('tbody tr').length === 50) { observer.disconnect(); resolve(performance.now() - start); } }); observer.observe(document, { childList: true, subtree: true }); location.hash = '/requests'; }));
    const hot = await page.evaluate(() => new Promise<number>(resolve => { const start = performance.now(), observer = new MutationObserver(() => { if (document.querySelector('.metric-grid')) { observer.disconnect(); resolve(performance.now()-start); } }); observer.observe(document, { childList: true, subtree: true }); location.hash = '/overview'; }));
    timings.push({ cold, rows, hot }); await context.close();
  }
  const quantile = (key: keyof typeof timings[number], p: number) => timings.map(x => x[key]).sort((a,b) => a-b)[Math.ceil(30*p)-1]!;
  const summary = Object.fromEntries((['cold','rows','hot'] as const).map(key => [key, { p50: quantile(key,.5), p95: quantile(key,.95) }]));
  await info.attach('timings', { body: JSON.stringify({ kind: real ? 'real_dev6_development_integration' : 'frontend_only_contract_fake', count: 30, method: 'Fresh context per cold sample; MutationObserver marks DOM commit. Cold includes navigation/modules/schema/snapshot; hot returns cached snapshot; 50 rows rendered.', timings, summary }), contentType: 'application/json' });
  expect(summary.cold!.p95).toBeLessThanOrEqual(1000); expect(summary.rows!.p95).toBeLessThanOrEqual(500); expect(summary.hot!.p95).toBeLessThanOrEqual(100);
});

import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { test, expect } from '@playwright/test';
const sample = (name: string) => JSON.parse(readFileSync(new URL(`../../../../docs/contracts/examples/monitoring-view-s0/${name}.json`, import.meta.url), 'utf8'));
test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    class SyntheticEventSource extends EventTarget { constructor() { super(); setTimeout(() => this.dispatchEvent(new Event('open')), 0); } close() {} }
    Object.assign(window, { EventSource: SyntheticEventSource });
  });
  await page.route('**/models', route => route.fulfill({ json: sample('models-legacy') }));
});
test('R1 persists original key before POST and restores terminal on page reload without reposting', async ({ page }) => {
  let posts = 0, lookups = 0, key = ''; let responseState = 'running';
  await page.route('**/monitoring/catalog**', route => route.fulfill({ json: sample('catalog-empty') }));
  await page.route('**/analysis-runs', async route => {
    posts++; const body = route.request().postDataJSON(); key = body.submission_key;
    const persisted = await page.evaluate(async () => new Promise<unknown[]>(resolve => { const req = indexedDB.open('tokenscope-viewer-receipts-v1', 1); req.onsuccess = () => { const db = req.result; const tx = db.transaction('receipts'); const all = tx.objectStore('receipts').getAll(); tx.oncomplete = () => { resolve(all.result); db.close(); }; }; }));
    expect(JSON.stringify(persisted)).toContain(key);
    const accepted = sample('submission-accepted'); accepted.run_id = sample('receipt-failed').run_id;
    await route.fulfill({ status: 202, json: accepted });
  });
  await page.route('**/analysis-submissions/**', route => { lookups++; const body = sample('receipt-' + responseState); body.run_id = sample('receipt-failed').run_id; body.submission_key = key; return route.fulfill({ json: body }); });
  await page.goto('/#/submissions'); await page.getByLabel('file_ref').fill('synthetic.csv');
  await page.getByLabel('确认启动该文件的监控计算').check(); await page.getByRole('button', { name: '提交监控任务', exact: true }).click();
  await expect(page.locator('.signal')).toContainText('running'); expect(posts).toBe(1); expect(lookups).toBe(1);
  responseState = 'failed';
  await page.reload(); await expect(page.locator('.signal')).toContainText(key); await expect(page.locator('.signal')).toContainText('failed'); expect(posts).toBe(1); expect(lookups).toBe(2);
});
test('settings CAS preserves large integer draft; rule integer writes remain strings', async ({ page }) => {
  let revision = '1', puts = 0; const writes: unknown[] = [];
  await page.route('**/monitoring/catalog**', route => route.fulfill({ json: sample('catalog-normal') }));
  await page.route('**/monitoring/runs**', route => route.fulfill({ json: { ...sample('runs-no-valid-rows'), items: [], total: '0' } }));
  await page.route('**/view-snapshot**', route => { const raw = JSON.stringify(sample('snapshot-normal')); return route.fulfill({ contentType: 'application/json', headers: { etag: '"' + createHash('sha256').update(raw).digest('hex') + '"' }, body: raw }); });
  await page.route('**/monitoring/models/**/settings', route => {
    if (route.request().method() === 'PUT') {
      const body = route.request().postDataJSON(); writes.push(body); puts++;
      if (puts === 1) { revision = '2'; return route.fulfill({ status: 409, json: { error: { code: 'REVISION_CONFLICT', message: 'synthetic competing update' } } }); }
      const result = sample('settings-glm'); result.settings = { ...result.settings, ...body.changes, revision: '3' }; return route.fulfill({ json: result });
    }
    const result = sample('settings-glm'); result.settings.revision = revision; return route.fulfill({ json: result });
  });
  await page.route('**/monitoring/threshold-rules**', route => {
    if (route.request().method() === 'PUT') { const body = route.request().postDataJSON(); writes.push(body); const rest = { ...body }; delete rest.expected_revision; return route.fulfill({ json: { service_instance_id: sample('catalog-normal').service_instance_id, view_schema_version: '1', rules_revision: '2', rule: { ...rest, revision: '1' } } }); }
    return route.fulfill({ json: sample('rules-empty') });
  });
  await page.goto('/#/settings'); await page.getByLabel('Block size', { exact: true }).fill('9007199254740993');
  await page.getByRole('button', { name: '保存下一运行设置' }).click();
  await expect(page.getByText('设置已被更新，当前草稿已保留。请对照服务器新版本后决定是否重新保存。')).toBeVisible();
  await expect(page.getByLabel('Block size', { exact: true })).toHaveValue('9007199254740993');
  await page.getByRole('button', { name: '确认以新版本保存当前草稿' }).click();
  await expect(page.getByText('已保存，仅对下一次启动运行生效；当前结果保持原设置。')).toBeVisible();
  expect(writes[1]).toMatchObject({ expected_revision: '2', changes: { block_size: '9007199254740993' } });
  await page.getByRole('button', { name: '新增阈值规则' }).click(); await page.getByRole('combobox', { name: '指标', exact: true }).selectOption('request_count');
  await page.getByLabel('阈值', { exact: true }).fill('9007199254740993'); await page.getByRole('button', { name: '保存阈值规则' }).click();
  await expect(page.getByText('规则已保存，仅影响下一次运行。')).toBeVisible();
  expect(writes.at(-1)).toMatchObject({ value_kind: 'integer', threshold: '9007199254740993' });
});

test('rule CAS reload retains the draft and requires explicit new-revision confirmation', async ({ page }) => {
  let revision = '1'; const writes: Record<string, unknown>[] = [];
  await page.route('**/monitoring/catalog**', r => r.fulfill({ json: sample('catalog-normal') }));
  await page.route('**/view-snapshot**', r => { const raw = JSON.stringify(sample('snapshot-normal')); return r.fulfill({ contentType: 'application/json', headers: { etag: '"'+createHash('sha256').update(raw).digest('hex')+'"' }, body: raw }); });
  await page.route('**/monitoring/models/**/settings', r => r.fulfill({ json: sample('settings-glm') }));
  await page.route('**/monitoring/threshold-rules**', r => {
    const data = sample('rules-page'); data.items[0].revision = revision; data.rules_revision = revision;
    if (r.request().method() === 'GET') return r.fulfill({ json: data });
    const body = r.request().postDataJSON(); writes.push(body);
    if (writes.length === 1) { revision = '2'; return r.fulfill({ status: 409, json: { error: { code: 'REVISION_CONFLICT', message: 'synthetic conflict' } } }); }
    return r.fulfill({ json: { service_instance_id: data.service_instance_id, view_schema_version: '1', rules_revision: '3', rule: { ...data.items[0], threshold: body.threshold, revision: '3' } } });
  });
  await page.goto('/#/settings'); await page.getByRole('button', { name: '编辑规则 long-p50' }).click(); await page.getByLabel('阈值', { exact: true }).fill('9007199254740993'); await page.getByRole('button', { name: '保存阈值规则' }).click();
  await expect(page.getByText('规则版本冲突', { exact: false })).toBeVisible(); await page.getByRole('button', { name: '重读规则列表' }).click();
  await expect(page.getByLabel('阈值', { exact: true })).toHaveValue('9007199254740993'); await page.getByRole('button', { name: '确认按新规则版本保存当前草稿' }).click();
  await expect(page.getByText('规则已保存，仅影响下一次运行。')).toBeVisible(); expect(writes[1]).toMatchObject({ expected_revision: '2', threshold: '9007199254740993' });
});

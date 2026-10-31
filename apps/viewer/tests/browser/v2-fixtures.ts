import { expect, type Page } from '@playwright/test';
export async function readyUser(page: Page, receipt: { user_run_id: string; service_instance_id: string }) {
  await expect.poll(async () => page.evaluate(async r => (await fetch(`/monitoring/user-v2/runs/${r.user_run_id}`, { headers: { 'X-TokenScope-Instance-Id': r.service_instance_id } }).then(v => v.json())).state, receipt), { timeout: 60000, intervals: [250, 500, 1000] }).toBe('ready');
}
export async function seedUser(page: Page, index = 1, file?: string) {
  const r = await page.evaluate(async ({ index, file }) => {
    const c = await fetch('/monitoring/catalog').then(r => r.json());
    const response = await fetch('/monitoring/user-v2/runs', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-TokenScope-Instance-Id': c.service_instance_id }, body: JSON.stringify({ submission_key: `rv2-fix-${index}-${file ?? 'default'}`, file_ref: file ?? `model-${index}.csv`, common_name: ['GLM-V5.2', 'Qwen-V3.6-27B', 'DeepSeek-V4-Flash'][index - 1], model_id: ['GLM-5.2', 'Qwen3.6-27B', 'DeepSeek-V4-Flash-0731'][index - 1] }) });
    if (!response.ok) throw Error(await response.text()); return response.json();
  }, { index, file });
  await readyUser(page, r); return r;
}
export async function seedMA(page: Page) {
  const r = await page.evaluate(async () => {
    const c = await fetch('/monitoring/catalog').then(r => r.json());
    const response = await fetch('/monitoring/ma/runs', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-TokenScope-Instance-Id': c.service_instance_id }, body: JSON.stringify({ submission_key: 'mv2-f005-real', pre_file_ref: 'mv2-pre.csv', now_file_ref: 'mv2-now.csv', model_id: 'Qwen3.6-27B', model_standard_name: 'synthetic-q-64K', pre_start: '2026-10-20T07:00:00Z', now_start: '2026-10-20T08:00:00Z', now_end: '2026-10-20T09:00:00Z', source_timezone: 'UTC' }) });
    if (!response.ok) throw Error(await response.text()); return response.json();
  });
  await expect.poll(async () => page.evaluate(async r => (await fetch(`/monitoring/ma/runs/${r.ma_run_id}`, { headers: { 'X-TokenScope-Instance-Id': r.service_instance_id } }).then(v => v.json())).state, r), { timeout: 60000, intervals: [500, 1000] }).toBe('completed');
  return r;
}

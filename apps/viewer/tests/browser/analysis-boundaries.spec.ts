import { test, expect, type Page, type Route } from '@playwright/test';
import fs from 'node:fs';
import legacy from '../../../../docs/tasks/prefix-analysis/FRONTEND_READONLY_EXAMPLES.json' with { type: 'json' };
import schemas from '../../src/api/analysis/generated/analysis-recommendations-1.json' with { type: 'json' };
import { catalogV2, executionCapabilities, legacyExecution, scopeBinding, taskFromPath } from './analysis-v2-fixtures';
type O = Record<string, unknown>;
type Sample = { task_id: string; report_sha256: string; report: O; responses: Record<string, O>; examples: Record<string, O> };
const datasets = (JSON.parse(fs.readFileSync('../../docs/tasks/prefix-analysis/FRONTEND_REWORK_READABILITY_EXAMPLES_ARL4.json', 'utf8')) as { datasets: { name: string; tasks: Sample[] }[] }).datasets;
const source = datasets[0]!.tasks.find(x => (x.report.scope as O).appid === 'a')!;
const base = legacy.ready_chain.responses['/diagnostics/discovery/catalog'].body;
const item = { ...base.items[0]!, task_id: source.task_id, scope: source.report.scope, scope_id: source.report.scope_id, report_digest: source.report_sha256, directions: ['low_hit'], binding: scopeBinding(source.report.scope as O) };
const initial = { ...base, items: [item], defaults: [{ ...base.defaults.find(x => x.direction === 'low_hit')!, task_id: source.task_id }] };
const recommendation = (source.responses.recommendations!.items as O[])[0]!;
function rebind(value: unknown, task: string): unknown {
    if (Array.isArray(value)) return value.map(x => rebind(x, task));
    if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, k === 'task_id' ? task : rebind(v, task)]));
    return value;
}
async function intercept(page: Page, options: { catalog?: () => unknown; event?: (route: Route) => Promise<void>; failTask?: string; examplesFail?: () => boolean } = {}) {
    const calls: string[] = [];
    let directory = catalogV2(initial);
    await page.route('**/diagnostics/**', async route => {
        const req = route.request(), u = new URL(req.url()), p = decodeURIComponent(u.pathname); calls.push(req.method() + ' ' + p);
        if (p === '/diagnostics/v3/capabilities') return route.fulfill({ status: 404, json: { error: { code: 'NOT_FOUND' } } });
        if (p === '/diagnostics/v2/capabilities') return route.fulfill({ json: executionCapabilities });
        if (p === '/diagnostics/recommendations/capabilities') return route.fulfill({ json: { version: 'analysis-recommendations-1', service_instance_id: 'fixture-instance', read_only: true, token_rule_ids: ['T2', 'T3', 'T4'], schemas: schemas.models } });
        if (p.endsWith('/capabilities')) return route.fulfill({ json: p.includes('/discovery/') ? { version: 'diagnostics-discovery-1', service_instance_id: 'fixture-instance' } : { contract_version: 'analysis-common-1.0', http_version: 'diagnostics-http-1', service_instance_id: 'fixture-instance' } });
        if (p.endsWith('/events')) { if (options.event) await options.event(route); return; }
        if (p === '/diagnostics/v2/catalog') { directory = catalogV2(options.catalog?.() ?? initial); return route.fulfill({ json: directory }); }
        const task = taskFromPath(p);
        if (!task) return route.fulfill({ status: 404, json: { error: { code: 'NOT_FOUND', message: 'unknown diagnostic route' } } });
        if (task === options.failTask) return route.fulfill({ status: 503, json: { error: { code: 'UNAVAILABLE', message: 'history read failure' } } });
        if (p === `/diagnostics/v2/tasks/${task}/execution`) {
            const selected = directory.items.find(x => x.task_id === task);
            return selected ? route.fulfill({ json: legacyExecution(selected) }) : route.fulfill({ status: 404, json: { error: { code: 'NOT_FOUND', message: 'unknown task' } } });
        }
        const original = p.replace('/' + task + '/', '/' + source.task_id + '/');
        let response: unknown;
        if (p.endsWith('/report')) response = source.report;
        else if (source.examples[original]) {
            if (options.examplesFail?.() && original.includes(String(recommendation.id))) return route.fulfill({ status: 503, json: { error: { code: 'UNAVAILABLE', message: 'evidence read failure' } } });
            response = source.examples[original];
        } else if (source.responses[p.split('/').at(-1)!]) response = source.responses[p.split('/').at(-1)!];
        else if (p.endsWith('/' + String(recommendation.id))) response = recommendation.data;
        else return route.fulfill({ status: 404, json: { error: { code: 'NOT_FOUND', message: 'not found' } } });
        return route.fulfill({ json: rebind(response, task) });
    });
    return calls;
}

test('history failure retains current result, time and a refreshable detail route', async ({ page }) => {
    const later = { ...item, task_id: 'unreadable', status: 'partial', default_eligible: false, analysis_completed_at: '2026-11-01T00:00:00.000Z' };
    await intercept(page, { catalog: () => ({ ...initial, items: [item, later] }), failTask: 'unreadable' });
    await page.goto('/#/analysis'); await expect(page.locator('.solution-card')).toHaveCount(2); const before = await page.locator('.scope-window').innerText();
    await page.getByLabel('历史报告', { exact: true }).selectOption('unreadable'); await expect(page.getByRole('alert')).toContainText('history read failure'); expect(await page.locator('.scope-window').innerText()).toBe(before); await expect(page.locator('.solution-card')).toHaveCount(2);
    await page.getByRole('button', { name: '查看最新', exact: true }).first().click(); await page.locator('.solution-card[data-rule="L1"] button').click(); await page.reload(); await expect(page.locator('.finding-body')).toContainText('预期命中率提升'); await page.getByRole('button', { name: '← 返回卡片列表' }).click(); await expect(page.locator('.solution-card')).toHaveCount(2);
});

test('first published partial is automatically readable with partial status and can be pinned explicitly', async ({ page }) => {
    await intercept(page, { catalog: () => ({ ...initial, items: [{ ...item, status: 'partial', default_eligible: false }], defaults: [] }) });
    await page.goto('/#/analysis'); await expect(page.locator('.solution-card')).toHaveCount(2); await expect(page.locator('.notice').filter({ hasText: '部分结果' }).first()).toBeVisible(); await expect(page.getByText('当前没有默认完整报告，请选择历史报告。')).toHaveCount(0); await expect(page.getByLabel('历史报告', { exact: true })).toHaveValue(source.task_id); await page.getByLabel('历史报告', { exact: true }).selectOption(source.task_id); await expect(page.locator('.solution-card')).toHaveCount(2); expect(page.url()).toContain('mode=history'); expect(page.url()).toContain(source.task_id);
});

test('evidence read failure keeps benefit and retries only the local examples', async ({ page }) => {
    let fail = true; const calls = await intercept(page, { examplesFail: () => fail });
    await page.goto('/#/analysis'); await page.locator('.solution-card[data-rule="L1"] .key-evidence').scrollIntoViewIfNeeded(); await expect(page.getByRole('alert')).toContainText('局部证据读取失败'); await expect(page.locator('.solution-card[data-rule="L1"] .impact-strip')).toContainText('预期命中率提升');
    fail = false; await page.getByRole('button', { name: '重新读取证据' }).click(); await expect(page.locator('.solution-card[data-rule="L1"] .key-evidence code')).toContainText('2026'); await expect(page.getByRole('alert')).toHaveCount(0); expect(calls.every(x => x.startsWith('GET '))).toBe(true); expect(calls.some(x => /\/requests\/|\/items\//.test(x))).toBe(false);
});

test('completion notification aligns directory while preserving detail until explicit latest', async ({ page }) => {
    let published = false, emit = false, streams = 0, catalogs = 0;
    const newer = { ...item, task_id: 'new-report', sequence: '2', analysis_completed_at: '2026-11-01T00:00:00.000Z' };
    const { scope: ignored, ...eventFields } = newer; void ignored;
    const event = { ...eventFields, version: base.version, service_instance_id: base.service_instance_id, event_id: 'fixture-instance:fixture-epoch:2' };
    const calls = await intercept(page, { catalog: () => { catalogs++; return published ? { ...initial, snapshot: event.event_id, event_cursor: event.event_id, items: [item, newer], defaults: initial.defaults.map(d => ({ ...d, task_id: 'new-report', sequence: '2' })) } : initial; }, event: async route => { streams++; if (streams > 1) return; await expect.poll(() => emit).toBe(true); published = true; await route.fulfill({ contentType: 'text/event-stream', body: `event: terminal\nid: ${event.event_id}\ndata: ${JSON.stringify(event)}\n\n` }); } });
    const q = new URLSearchParams({ binding: item.binding_id, direction: 'low_hit', mode: 'history', task: source.task_id, item: String(recommendation.id) });
    await page.goto('/#/analysis?' + q); await expect(page.locator('.finding-body')).toBeVisible(); emit = true;
    await expect(page.getByText('有新报告可查看；当前阅读位置已保留。')).toBeVisible(); expect(page.url()).toContain(source.task_id); expect(catalogs).toBeGreaterThanOrEqual(2);
    await page.getByRole('button', { name: '← 返回卡片列表' }).click(); await expect(page.locator('.solution-card')).toHaveCount(2); expect(page.url()).toContain(source.task_id);
    await page.getByRole('button', { name: '查看最新', exact: true }).first().click(); await expect(page.locator('.scope-window')).toContainText('2026/11/1'); expect(calls.every(x => x.startsWith('GET '))).toBe(true); expect(calls.some(x => /\/tasks\/[^/]+$/.test(x))).toBe(false);
});

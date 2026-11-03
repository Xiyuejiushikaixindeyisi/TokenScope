import { test, expect, type Page, type Route } from '@playwright/test';
import fs from 'node:fs';
import legacy from '../../../../docs/tasks/prefix-analysis/FRONTEND_READONLY_EXAMPLES.json' with { type: 'json' };
import schemas from '../../src/api/analysis/generated/analysis-recommendations-1.json' with { type: 'json' };
import { catalogV2, executionCapabilities, legacyExecution, scopeBinding, taskFromPath } from './analysis-v2-fixtures';

type O = Record<string, unknown>;
type Sample = { task_id: string; report_sha256: string; report: O; responses: Record<string, O>; examples: Record<string, O> };
const datasets = JSON.parse(fs.readFileSync('../../docs/tasks/prefix-analysis/FRONTEND_REWORK_READABILITY_EXAMPLES_ARL4.json', 'utf8')) as { datasets: { tasks: Sample[] }[] };
const samples = datasets.datasets[0]!.tasks;
const a = samples.find(x => (x.report.scope as O).appid === 'a')!;
const b = samples.find(x => (x.report.scope as O).appid === 'representation')!;
const base = legacy.ready_chain.responses['/diagnostics/discovery/catalog'].body;
const entry = (s: Sample, i: number) => ({ ...base.items[0]!, task_id: s.task_id, scope: s.report.scope, scope_id: s.report.scope_id, report_digest: s.report_sha256, sequence: String(i + 1), directions: ['low_hit'], binding_id: `review-binding-${i}`, binding: scopeBinding(s.report.scope as O) });
const items = [entry(a, 0), entry(b, 1)];
const catalog = { ...base, items, defaults: items.map(x => ({ ...base.defaults.find(d => d.direction === 'low_hit')!, binding_id: x.binding_id, task_id: x.task_id, sequence: x.sequence })) };
const delay = (ms: number) => new Promise<void>(resolve => setTimeout(resolve, ms));

async function intercept(page: Page, options: { catalog?: unknown; report?: (route: Route) => Promise<void>; recommendations?: (route: Route, body: O) => Promise<void> } = {}) {
    const calls: string[] = [];
    const directory = catalogV2(options.catalog ?? catalog);
    await page.route('**/diagnostics/**', async route => {
        const u = new URL(route.request().url()), p = decodeURIComponent(u.pathname);
        calls.push(p);
        if (p === '/diagnostics/v2/capabilities') return route.fulfill({ json: executionCapabilities });
        if (p === '/diagnostics/recommendations/capabilities') return route.fulfill({ json: { version: 'analysis-recommendations-1', service_instance_id: 'fixture-instance', read_only: true, token_rule_ids: ['T2', 'T3', 'T4'], schemas: schemas.models } });
        if (p.endsWith('/capabilities')) return route.fulfill({ json: p.includes('/discovery/') ? { version: 'diagnostics-discovery-1', service_instance_id: 'fixture-instance' } : { contract_version: 'analysis-common-1.0', http_version: 'diagnostics-http-1', service_instance_id: 'fixture-instance' } });
        // Hold the subscription open; these tests exercise UI races, not synthetic SSE completion.
        if (p.endsWith('/events')) return;
        if (p === '/diagnostics/v2/catalog') return route.fulfill({ json: directory });
        const task = taskFromPath(p);
        const s = samples.find(x => x.task_id === task);
        if (!s) return route.fulfill({ status: 404, json: { error: { code: 'NOT_FOUND', message: 'unknown task' } } });
        if (p === `/diagnostics/v2/tasks/${task}/execution`) {
            const selected = directory.items.find(x => x.task_id === task);
            return selected ? route.fulfill({ json: legacyExecution(selected) }) : route.fulfill({ status: 404, json: { error: { code: 'NOT_FOUND', message: 'task absent from directory' } } });
        }
        if (p.endsWith('/report')) return options.report ? options.report(route) : route.fulfill({ json: s.report });
        if (s.examples[p]) return route.fulfill({ json: s.examples[p] });
        const kind = p.split('/').at(-1)!;
        if (kind === 'recommendations') {
            const original = s.responses.recommendations!;
            const body = { ...original, items: (original.items as O[]).filter(x => (x.data as O).direction === u.searchParams.get('direction')) };
            return options.recommendations ? options.recommendations(route, body) : route.fulfill({ json: body });
        }
        if (s.responses[kind]) return route.fulfill({ json: s.responses[kind] });
        return route.fulfill({ status: 404, json: { error: { code: 'NOT_FOUND', message: 'unknown item' } } });
    });
    return calls;
}

test('cancelled report read clears loading when the selected direction has no report', async ({ page }) => {
    let pending: Route | undefined;
    await intercept(page, { report: async route => { pending = route; } });
    await page.goto('/#/analysis');
    await expect(page.getByText('正在读取报告…', { exact: true })).toBeVisible();
    await expect.poll(() => !!pending).toBe(true);
    await page.getByRole('button', { name: 'Token异常分析', exact: true }).click();
    await expect(page.getByText('当前应用暂无Token异常分析报告。', { exact: true })).toBeVisible();
    await expect(page.getByText('正在读取报告…', { exact: true })).toHaveCount(0);
    await pending!.fulfill({ json: a.report }).catch(() => {});
    await expect(page.locator('.solution-card')).toHaveCount(0);
});

test('failed report error is removed after switching to an unrelated empty direction', async ({ page }) => {
    await intercept(page, { report: route => route.fulfill({ status: 503, json: { error: { code: 'UNAVAILABLE', message: 'review report failure' } } }) });
    await page.goto('/#/analysis');
    await expect(page.getByRole('alert')).toContainText('review report failure');
    await page.getByRole('button', { name: 'Token异常分析', exact: true }).click();
    await expect(page.getByText('当前应用暂无Token异常分析报告。', { exact: true })).toBeVisible();
    await expect(page.getByRole('alert')).toHaveCount(0);
});

test('late pagination failure cannot change the new application report', async ({ page }) => {
    let pending: Route | undefined;
    await intercept(page, { recommendations: async (route, body) => {
        const u = new URL(route.request().url());
        if (!u.pathname.includes(a.task_id)) return route.fulfill({ json: body });
        if (u.searchParams.get('offset') === '1') { pending = route; return; }
        return route.fulfill({ json: { ...body, next_offset: '1' } });
    } });
    await page.goto('/#/analysis');
    await page.getByRole('button', { name: '加载更多', exact: true }).click();
    await expect.poll(() => !!pending).toBe(true);
    await page.getByLabel('业务应用', { exact: true }).selectOption('representation');
    await expect(page.locator('.solution-card[data-rule="L5"]')).toBeVisible();
    await pending!.fulfill({ status: 503, json: { error: { code: 'UNAVAILABLE', message: 'review old page failure' } } }).catch(() => {});
    await delay(100);
    await expect(page.getByRole('alert')).toHaveCount(0);
    await expect(page.getByLabel('业务应用', { exact: true })).toHaveValue('representation');
});

test('late monitoring-source lookup cannot navigate after the application changes', async ({ page }) => {
    await intercept(page);
    let pending: Route | undefined;
    await page.route('**/monitoring/catalog', async route => { pending = route; });
    await page.goto('/#/analysis');
    await expect(page.locator('.solution-card[data-rule="L1"]')).toBeVisible();
    await page.getByRole('button', { name: '查看原报告监控来源', exact: true }).click();
    await expect.poll(() => !!pending).toBe(true);
    await page.getByLabel('业务应用', { exact: true }).selectOption('representation');
    await expect(page.locator('.solution-card[data-rule="L5"]')).toBeVisible();
    await pending!.fulfill({ json: { service_instance_id: 'fixture-instance', view_schema_version: '1', offset: '0', limit: 100, total: '0', next_offset: null, catalog_revision: '0', items: [], cursor: 'fixture-instance:0' } }).catch(() => {});
    await delay(100);
    expect(page.url()).toContain('#/analysis');
    await expect(page.getByLabel('业务应用', { exact: true })).toHaveValue('representation');
});

test('disabled browser storage does not prevent subscription or trigger reconnect requests', async ({ page }) => {
    await page.addInitScript(() => Object.defineProperty(window, 'localStorage', { configurable: true, get() { throw new DOMException('review storage denied', 'SecurityError'); } }));
    const calls = await intercept(page);
    await page.goto('/#/analysis');
    await expect(page.locator('.solution-card')).toHaveCount(2);
    await expect.poll(() => calls.filter(x => x.endsWith('/events')).length).toBe(1);
    const initialConnections = calls.filter(x => x === '/diagnostics/capabilities').length;
    await delay(1600);
    expect(calls.filter(x => x === '/diagnostics/capabilities')).toHaveLength(initialConnections);
    await expect(page.locator('.connection-status')).not.toContainText('review storage denied');
});

test('direction-only entry chooses a binding with that direction and an obsolete link can recover', async ({ page }) => {
    const mixed = { ...catalog, items: [items[0], { ...items[1], directions: ['token_content'] }], defaults: [catalog.defaults[0], { ...catalog.defaults[1], direction: 'token_content' }] };
    await intercept(page, { catalog: mixed });
    await page.goto('/#/analysis?direction=token_content');
    await expect(page.getByLabel('业务应用', { exact: true })).toHaveValue('representation');
    await expect(page.getByRole('heading', { name: 'Token 优化建议', exact: true })).toBeVisible();
    await page.goto('/#/analysis?binding=removed-binding&direction=low_hit');
    await expect(page.getByText('原报告链接不属于当前报告目录。', { exact: false })).toBeVisible();
    await page.getByRole('button', { name: '返回报告目录', exact: true }).click();
    await expect(page.getByLabel('业务应用', { exact: true })).toHaveValue('a');
    await expect(page.locator('.solution-card[data-rule="L1"]')).toBeVisible();
});

test('switching direction within a historical dual-direction task preserves task and time', async ({ page }) => {
    const dual = { ...catalog, items: [{ ...items[0], directions: ['low_hit', 'token_content'] }, items[1]], defaults: [...catalog.defaults, { ...catalog.defaults[0], direction: 'token_content' }] };
    await intercept(page, { catalog: dual });
    await page.goto('/#/analysis?' + new URLSearchParams({ binding: items[0]!.binding_id, direction: 'low_hit', mode: 'history', task: a.task_id }));
    await expect(page.locator('.solution-card[data-rule="L1"]')).toBeVisible();
    const time = await page.locator('.scope-window').innerText();
    await page.getByRole('button', { name: 'Token异常分析', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Token 优化建议', exact: true })).toBeVisible();
    expect(page.url()).toContain(a.task_id);
    expect(page.url()).toContain('mode=history');
    expect(await page.locator('.scope-window').innerText()).toBe(time);
    await page.getByRole('button', { name: '低命中率分析', exact: true }).click();
    await expect(page.locator('.solution-card[data-rule="L1"]')).toBeVisible();
    expect(page.url()).toContain(a.task_id);
});

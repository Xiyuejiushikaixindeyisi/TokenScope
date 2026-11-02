import { test, expect, type Page } from '@playwright/test';
import fs from 'node:fs';

interface SourceEntry {
    task_id: string;
    binding_id: string;
    scope: { appid: string; source: { base_run_id: string; user_run_id: string | null; model_id: string } };
}
interface Fixture {
    service_instance_id: string;
    user: SourceEntry;
    base: SourceEntry;
    other: { user_run_id: string; appid: string };
}
const path = process.env.TOKENSCOPE_SOURCE_LINK_FIXTURE;
const fixture: Fixture | undefined = path ? JSON.parse(fs.readFileSync(path, 'utf8')) as Fixture : undefined;
test.skip(!fixture, 'read-only real backend source fixture required');
const pageErrors = new WeakMap<Page, string[]>();

async function openReport(page: Page, entry: SourceEntry) {
    await page.goto('/#/analysis?' + new URLSearchParams({ binding: entry.binding_id, direction: 'token_content', mode: 'history', task: entry.task_id }));
    await expect(page.getByLabel('历史报告', { exact: true })).toHaveValue(entry.task_id);
    await expect(page.getByRole('button', { name: '查看原报告监控来源', exact: true })).toBeVisible();
}
async function selectedUser(page: Page, run: string, appid: string) {
    await expect(page.locator('.filter-meta').filter({ hasText: '展示运行' })).toContainText(run);
    await expect(page.getByLabel('用户APPID', { exact: true })).toHaveValue(appid);
    const query = new URLSearchParams(new URL(page.url()).hash.split('?')[1]);
    expect(query.get('run')).toBe(run);
    expect(query.get('appid')).toBe(appid);
    expect(query.has('user_run_id')).toBe(false);
}
test.beforeEach(async ({ page }) => {
    const errors: string[] = [];
    pageErrors.set(page, errors);
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => {
        if (/\/(monitoring|diagnostics|analysis-runs|analysis-submissions)\//.test(request.url())) expect(request.method()).toBe('GET');
    });
    const response = await page.request.get('/monitoring/catalog');
    expect((await response.json()).service_instance_id).toBe(fixture!.service_instance_id);
});
test.afterEach(async ({ page }) => { expect(pageErrors.get(page)).toEqual([]); });

test('cold browser opens the original user run and preserves it on refresh', async ({ page }) => {
    const entry = fixture!.user;
    await openReport(page, entry);
    expect(await page.evaluate(instance => localStorage.getItem(`tokenscope.v2.1:user:${instance}`), fixture!.service_instance_id)).toBeNull();
    await page.getByRole('button', { name: '查看原报告监控来源', exact: true }).click();
    await selectedUser(page, entry.scope.source.user_run_id!, entry.scope.appid);
    await page.reload();
    await selectedUser(page, entry.scope.source.user_run_id!, entry.scope.appid);
});

test('a different recent monitoring run cannot replace the historical source', async ({ page }) => {
    const { user, other, service_instance_id: instance } = fixture!;
    expect(other.user_run_id).not.toBe(user.scope.source.user_run_id);
    await page.goto('/#/users?' + new URLSearchParams({ run: other.user_run_id, appid: other.appid }));
    await selectedUser(page, other.user_run_id, other.appid);
    expect(await page.evaluate(id => JSON.parse(localStorage.getItem(`tokenscope.v2.1:user:${id}`)!).runs[0], instance)).toBe(other.user_run_id);
    await openReport(page, user);
    await page.getByRole('button', { name: '查看原报告监控来源', exact: true }).click();
    await selectedUser(page, user.scope.source.user_run_id!, user.scope.appid);
    await page.reload();
    await selectedUser(page, user.scope.source.user_run_id!, user.scope.appid);
});

test('base reports still open the exact S0 overview source', async ({ page }) => {
    const entry = fixture!.base;
    expect(entry.scope.source.user_run_id).toBeNull();
    const snapshots: string[] = [];
    page.on('response', response => { if (response.url().includes('/view-snapshot')) snapshots.push(response.url()); });
    await openReport(page, entry);
    await page.getByRole('button', { name: '查看原报告监控来源', exact: true }).click();
    await expect(page).toHaveURL(/#\/overview\?/);
    await expect(page.getByRole('region', { name: '核心指标' })).toBeVisible();
    const query = new URLSearchParams(new URL(page.url()).hash.split('?')[1]);
    expect(query.get('run')).toBe(entry.scope.source.base_run_id);
    expect(query.get('model')).toBe(entry.scope.source.model_id);
    expect(query.get('appid')).toBe(entry.scope.appid);
    expect(snapshots.some(url => url.includes(`/analysis-runs/${entry.scope.source.base_run_id}/view-snapshot`) && new URL(url).searchParams.get('appid') === entry.scope.appid)).toBe(true);
});

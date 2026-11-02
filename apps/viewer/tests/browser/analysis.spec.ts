import { test, expect, type Page } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
const out = path.resolve(process.env.TOKENSCOPE_ANALYSIS_SCREENSHOTS ?? '../../artifacts/validation/viewer/analysis/rv2-20261101/browser');
const lowURL = process.env.TOKENSCOPE_TEST_BASE_URL ?? 'http://localhost:4191';
const tokenURL = lowURL; // Both directions must use the same service and origin.
async function shot(page: Page, options: Parameters<Page['screenshot']>[0]) { const y = await page.evaluate(() => scrollY); await page.evaluate(() => scrollTo(0, 0)); await page.screenshot(options); await page.evaluate(value => scrollTo(0, value), y); }
test.beforeEach(() => { test.skip(process.env.TOKENSCOPE_ANALYSIS_REAL !== '1', 'real sealed backend states required'); fs.mkdirSync(out, { recursive: true }); });

test('UI-04 low-hit solution, local differences and return position', async ({ page }) => {
    const errors: string[] = [], reads: string[] = []; page.on('pageerror', e => errors.push(e.message)); page.on('request', r => { if (r.url().includes('/diagnostics/')) { expect(r.method()).toBe('GET'); reads.push(r.url()); } });
    await page.setViewportSize({ width: 1440, height: 1050 }); await page.goto(lowURL + '/#/analysis');
    await page.getByLabel('业务应用', { exact: true }).selectOption('synthetic-orders');
    const card = page.locator('.solution-card[data-rule="L1"]'); await expect(card).toHaveCount(1);
    await expect(card.locator('.key-evidence code')).toContainText('2026-');
    await expect(card.locator('.impact-strip')).toContainText('6'); await expect(card.locator('.impact-strip')).not.toContainText('Token');
    await expect(page.locator('.solution-card')).toHaveCount(3);
    await expect(page.locator('.solution-card[data-rule="L4"]')).toHaveCount(1);
    await expect(page.locator('.solution-card[data-rule="L5"]')).toHaveCount(1);
    await expect(page.getByRole('button', { name: '加载更多', exact: true })).toHaveCount(0);
    await page.locator('.solution-card[data-rule="L4"]').scrollIntoViewIfNeeded();
    await expect(page.locator('.solution-card[data-rule="L4"] .key-evidence code')).toBeVisible();
    await expect(page.locator('.solution-card[data-rule="L5"] .key-evidence code')).toBeVisible();
    await shot(page, { path: path.join(out, 'low-list-1440.png'), fullPage: true });
    await card.getByRole('button').click(); await expect(page.locator('.example-block')).toHaveCount(3);
    await expect(page.locator('.finding-body')).toContainText('两个请求的原内容对照'); await expect(page.locator('.finding-body')).toContainText('同一个请求的对照');
    const lengths = await page.locator('.report-code').evaluateAll(nodes => nodes.map(n => (n.textContent ?? '').length)); expect(Math.max(...lengths)).toBeLessThan(400);
    await expect(page.getByText('查看完整请求原文与位置', { exact: true })).toHaveCount(0); await shot(page, { path: path.join(out, 'low-detail-1440.png'), fullPage: true });
    await page.getByRole('button', { name: '← 返回卡片列表' }).click(); await expect(card.getByRole('button')).toBeFocused();
    await page.locator('.solution-card[data-rule="L4"] button').first().click(); await expect(page.locator('.example-block')).toHaveCount(3); await expect(page.locator('.finding-body .impact-strip')).toHaveCount(0);
    await shot(page, { path: path.join(out, 'l4-detail.png'), fullPage: true }); await page.getByRole('button', { name: '← 返回卡片列表' }).click();
    await page.locator('.solution-card[data-rule="L5"] button').click(); await expect(page.locator('.example-block').first()).toBeVisible(); expect(await page.locator('.example-block').count()).toBeLessThanOrEqual(3); await expect(page.locator('.report-code').first()).toContainText('id'); await shot(page, { path: path.join(out, 'l5-detail.png'), fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 }); await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true); await shot(page, { path: path.join(out, 'low-detail-390.png'), fullPage: true });
    expect(reads.some(x => /\/items\/(finding|fragment|evaluation)|\/requests\/|\/comparisons\//.test(x))).toBe(false); expect(errors).toEqual([]);
});

test('UI-04 Token concrete recommendations and precise quantified effects', async ({ page }) => {
    const errors: string[] = []; page.on('pageerror', e => errors.push(e.message));
    await page.setViewportSize({ width: 1440, height: 1050 }); await page.goto(tokenURL + '/#/analysis?direction=token_content');
    await expect(page.locator('.solution-card')).toHaveCount(4); await expect(page.locator('.key-evidence code').first()).toBeVisible(); await expect(page.locator('.solution-card[data-rule="T1"]')).toHaveCount(0);
    await expect(page.locator('.report-detail summary').first()).toContainText('3 个探测器'); expect(await page.locator('.report-detail').first().getAttribute('open')).toBeNull();
    await expect(page.locator('.solution-card[data-rule="T2"]')).toContainText('5,310'); await expect(page.locator('.solution-card[data-rule="T2"]')).toContainText('debug_log'); await shot(page, { path: path.join(out, 'token-list-1440.png'), fullPage: true });
    for (const index of [0, 1, 2, 3]) {
        await page.locator('.solution-card button').nth(index).click(); await expect(page.locator('.example-block')).toHaveCount(3); await expect(page.locator('.finding-body')).toContainText('影响请求'); await expect(page.locator('.finding-body')).toContainText('修改方案');
        await expect(page.getByText('查看修改方案与评估身份', { exact: true })).toHaveCount(0); await expect(page.getByRole('button', { name: /提交|执行评估|单项评估/ })).toHaveCount(0);
        await shot(page, { path: path.join(out, `token-detail-${index}.png`), fullPage: true });
        if (index === 0) { await page.setViewportSize({ width: 390, height: 844 }); await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true); await shot(page, { path: path.join(out, 'token-detail-390.png'), fullPage: true }); await page.setViewportSize({ width: 1440, height: 1050 }); }
        await page.getByRole('button', { name: '← 返回卡片列表' }).click(); await expect(page.locator('.solution-card button').nth(index)).toBeFocused();
    }
    await page.setViewportSize({ width: 390, height: 844 }); await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true); await shot(page, { path: path.join(out, 'token-list-390.png'), fullPage: true });
    const saved = await page.evaluate(() => localStorage.getItem('tokenscope.analysis.metadata.v1')); expect(saved).not.toContain('debug_log'); expect(saved).not.toContain('raw_body'); expect(saved).not.toContain('profile_json'); expect(errors).toEqual([]);
});

test('completed report waits for notifications without polling; reconnect preserves content', async ({ page }) => {
    test.setTimeout(45000); await page.goto(tokenURL + '/#/analysis?direction=token_content'); await page.locator('.key-evidence').first().scrollIntoViewIfNeeded(); await expect(page.locator('.key-evidence code').first()).toBeVisible(); await expect(page.getByRole('status').filter({ hasText: '报告通知已连接' })).toBeVisible();
    const reads: string[] = []; page.on('request', r => { if (r.url().includes('/diagnostics/')) reads.push(r.url()); }); const before = await page.locator('.scope-window').innerText();
    await page.waitForTimeout(21000); expect(reads).toEqual([]);
    await page.context().setOffline(true); await expect(page.locator('.solution-card')).toHaveCount(4); expect(await page.locator('.scope-window').innerText()).toBe(before);
    await page.context().setOffline(false); await page.getByRole('button', { name: '重新连接', exact: true }).click(); await expect(page.getByRole('status').filter({ hasText: '报告通知已连接' })).toBeVisible(); expect(await page.locator('.scope-window').innerText()).toBe(before);
});

test('analysis navigation preserves monitoring and MA routes', async ({ page }) => {
    const errors: string[] = []; page.on('pageerror', e => errors.push(e.message)); await page.goto(tokenURL + '/#/analysis?direction=token_content'); await expect(page.locator('.solution-card')).toHaveCount(4);
    await page.getByRole('link', { name: '返回监控', exact: true }).click(); await expect(page.locator('.shell.v2')).toBeVisible(); await page.goto(tokenURL + '/#/ma'); await expect(page.locator('.shell.v2')).toBeVisible(); await page.goto(tokenURL + '/#/overview'); await expect(page.getByRole('heading', { level: 1 })).toHaveText('监控概览'); await expect(page.locator('.sidebar a')).toHaveText(['用户监控','搜索与排行','异常分析','MA集群监控']); await expect(page.locator('.sidebar-bottom')).not.toContainText('V1'); expect(errors).toEqual([]);
});

test('one origin keeps both directions, pinned history and ready default after partial', async ({ page }) => {
    const fixture = JSON.parse(fs.readFileSync('../../docs/tasks/prefix-analysis/UNIFIED_ACCEPTANCE_RV1_EXAMPLES.json', 'utf8'));
    const latest = fixture.catalog.defaults[0].task_id as string;
    const history = fixture.catalog.items.find((x: { status: string; task_id: string }) => x.status === 'ready' && x.task_id !== latest).task_id as string;
    const partial = fixture.catalog.items.find((x: { status: string }) => x.status === 'partial').task_id as string;
    const instances = new Set<string>(), origins = new Set<string>();
    page.on('request', r => { if (r.url().includes('/diagnostics/')) {
        expect(r.method()).toBe('GET'); origins.add(new URL(r.url()).origin);
        const instance = r.headers()['x-tokenscope-service-instance']; if (instance) instances.add(instance);
    } });
    await page.goto(lowURL + '/#/analysis');
    await expect(page.locator('.solution-card[data-rule="L1"]')).toHaveCount(1);
    await expect(page.getByLabel('历史报告', { exact: true })).toHaveValue(latest);
    const scope = await page.locator('.scope-window').innerText();
    for (let i = 0; i < 3; i++) {
        await page.getByRole('button', { name: 'Token异常分析', exact: true }).click();
        await expect(page.locator('.solution-card')).toHaveCount(4);
        await expect(page.getByLabel('业务应用', { exact: true })).toHaveValue('synthetic-orders');
        expect(await page.locator('.scope-window').innerText()).toBe(scope);
        await page.getByRole('button', { name: '低命中率分析', exact: true }).click();
        await expect(page.locator('.solution-card[data-rule="L1"]')).toHaveCount(1);
    }
    await page.getByLabel('历史报告', { exact: true }).selectOption(history);
    await expect(page.getByLabel('历史报告', { exact: true })).toHaveValue(history);
    await page.getByRole('button', { name: 'Token异常分析', exact: true }).click();
    await expect(page.locator('.solution-card')).toHaveCount(4);
    await expect(page.getByLabel('历史报告', { exact: true })).toHaveValue(history);
    await page.locator('.solution-card button').first().click(); await page.reload();
    await expect(page.locator('.finding-body')).toBeVisible(); expect(page.url()).toContain(history);
    await page.getByRole('button', { name: '← 返回卡片列表' }).click();
    await page.getByLabel('历史报告', { exact: true }).selectOption(partial);
    await expect(page.getByLabel('历史报告', { exact: true })).toHaveValue(partial);
    await expect(page.getByText('正在读取报告…', { exact: true })).toHaveCount(0);
    await expect(page.getByText(/当前为 部分结果/)).toBeVisible();
    await page.getByRole('button', { name: '查看最新', exact: true }).first().click();
    await expect(page.locator('.solution-card')).toHaveCount(4);
    await expect(page.getByLabel('历史报告', { exact: true })).toHaveValue(latest);
    expect([...origins]).toEqual([new URL(lowURL).origin]);
    expect([...instances]).toEqual([fixture.service_instance_id]);
});

test('retired Token port is stopped and unified entry preserves both directions', async ({ page }) => {
    await expect(page.request.get('http://localhost:4193/', { timeout: 3000 })).rejects.toThrow();
    await page.goto(lowURL + '/#/analysis?direction=token_content');
    await expect(page).toHaveURL(new RegExp('^' + lowURL.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '/#'));
    await expect(page.locator('.solution-card')).toHaveCount(4);
    await page.getByRole('button', { name: '低命中率分析', exact: true }).click();
    await expect(page.locator('.solution-card[data-rule="L1"]')).toHaveCount(1);
});

test('old difference links open the detector overview and return to two difference cards', async ({ page }) => {
    await page.goto(lowURL + '/#/analysis?binding=f860b372ec762939acba36cbffbfebab82e97836215f52df683a96900b0e2256&direction=low_hit&mode=history&task=4f5a4bd6-c09e-4ac4-a5aa-9f5fdd832633&item=diff%3Ae1ffd9070eb25c7f0a011ff45e7d769f3c84976df53a332175b9ca89b3174642');
    await expect(page.locator('.finding-body[data-rule="L4"]')).toBeVisible();
    await expect(page.locator('.example-block').first()).toBeVisible();
    expect(await page.locator('.example-block').count()).toBeLessThanOrEqual(3);
    await page.getByRole('button', { name: '← 返回卡片列表' }).click();
    await expect(page.locator('.solution-card[data-rule="L4"]')).toHaveCount(1);
    await expect(page.locator('.solution-card[data-rule="L5"]')).toHaveCount(1);
    await page.locator('.solution-card[data-rule="L5"] button').click();
    await page.reload();
    await expect(page.locator('.finding-body[data-rule="L5"]')).toBeVisible();
    expect(await page.locator('.example-block').count()).toBeLessThanOrEqual(3);
});

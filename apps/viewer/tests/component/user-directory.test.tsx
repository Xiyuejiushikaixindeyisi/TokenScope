import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, expect, test, vi } from 'vitest';
import { V2Client, validateV2 } from '../../src/api/v2/client';
import { UserMonitor } from '../../src/features/v2/UserMonitor';
import { entryKey, modelScopeKey, type DiscoveryEntry } from '../../src/features/v2/user-discovery';
import examples from '../../../../docs/contracts/user-monitoring-v2/2.1.0/examples.json';
import oldExamples from '../../../../docs/contracts/user-monitoring-v2/2.0.0/examples.json';
const mocks = vi.hoisted(() => ({ snapshot: vi.fn() }));
vi.mock('../../src/api/client', async importOriginal => ({ ...await importOriginal<object>(), getJson: mocks.snapshot }));
vi.mock('../../src/features/overview/Overview', () => ({ Overview: () => null }));
vi.mock('../../src/features/distributions/Distributions', () => ({ Distributions: () => null }));
vi.mock('../../src/features/requests/Requests', () => ({ Requests: () => null }));
vi.mock('../../src/features/exports/Exports', () => ({ Exports: () => null }));
vi.mock('../../src/features/signals/Signals', () => ({ Signals: () => null }));
vi.mock('../../src/features/v2/Ranking', () => ({ Ranking: () => null }));
vi.mock('../../src/features/v2/TTFT', () => ({ TTFT: ({ receipt, appid }: { receipt: { user_run_id: string }; appid: string }) => <p data-testid="shown">{receipt.user_run_id}/{appid}</p> }));
const page = validateV2('user', 'DiscoveryPage', examples.find(e => e.model === 'DiscoveryPage')!.value);
const ranking = validateV2('user', 'Ranking', oldExamples.find(e => e.model === 'Ranking' && e.valid)!.value);
const json = (x: unknown, status = 200) => new Response(JSON.stringify(x), { status, headers: { 'Content-Type': 'application/json' } });
function entry(run: string, model: 'Qwen3.6-27B' | 'GLM-5.2', isDefault = true): DiscoveryEntry {
    const e = structuredClone(page.entries[0]!); e.source.user_run_id = run; e.source.base_run_id = `base-${run}`; e.source.model_id = model; e.source.common_name = model === 'GLM-5.2' ? 'GLM-V5.2' : 'Qwen-V3.6-27B'; e.is_default = isDefault; return e;
}
function setup(initial: DiscoveryEntry[], options: { delayDirectory?: boolean; delayReceipt?: boolean } = {}) {
    let entries = initial, release: (() => void) | undefined, releaseReceipt: (() => void) | undefined, receiptHeld = false;
    const all = [...initial];
    mocks.snapshot.mockImplementation(async (_: string, path: string, query: { appid: string }) => {
        const e = all.find(x => path.includes(x.source.base_run_id))!;
        // Only the unrelated S0 presentation leaves are stubbed; V2 HTTP uses real validators.
        return { identity: { run_id: e.source.base_run_id, appid: query.appid, model_id: e.source.model_id }, provenance: { data_range_utc: { start: '2026-10-20T07:00:00.000000000Z', end: '2026-10-20T08:00:00.000000000Z' }, runtime: {} }, quality: { file_quality: { skipped_rows: '0' }, group_quality: { valid_requests: '2' } } };
    });
    const fetcher = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = new URL(String(input), 'http://localhost'), path = url.pathname;
        if (path === '/monitoring/user-v2/runs') {
            if (options.delayDirectory) await new Promise<void>(r => { release = r; });
            return json({ ...page, entries, total: String(entries.length), next_offset: null });
        }
        const e = all.find(x => path.includes(`/runs/${x.source.user_run_id}`));
        if (!e) return json({ error: { code: 'RUN_NOT_FOUND', message: 'history unavailable' } }, 404);
        if (path.endsWith('/rankings')) return json({ ...ranking, service_instance_id: page.service_instance_id, user_run_id: e.source.user_run_id, common_name: e.source.common_name, index_revision: e.source.index_revision, rows: ranking.rows.map(r => ({ ...r, appid: e.appid })) });
        expect(init?.method).toBe('GET');
        if (options.delayReceipt && !receiptHeld) { receiptHeld = true; await new Promise<void>(resolve => { releaseReceipt = resolve; }); }
        return json({ service_instance_id: page.service_instance_id, ...Object.fromEntries(['user_run_id', 'base_run_id', 'model_id', 'common_name', 'index_revision'].map(k => [k, e.source[k as keyof typeof e.source]])), state: e.state, error_code: null });
    });
    const view = render(<UserMonitor api={new V2Client(page.service_instance_id, fetcher)} page="users"/>);
    return { ...view, fetcher, replace(next: DiscoveryEntry[]) { entries = next; all.push(...next.filter(e => !all.some(x => x.source.user_run_id === e.source.user_run_id))); }, release: () => release?.(), receiptPending: () => !!releaseReceipt, releaseReceipt: () => releaseReceipt?.() };
}
beforeEach(() => { localStorage.clear(); history.replaceState(null, '', '#/users'); HTMLDialogElement.prototype.showModal = function () { this.open = true; }; HTMLDialogElement.prototype.close = function () { this.open = false; }; });
test('cold browser discovers every model for same appid without stored runs or POST', async () => {
    const q = entry('q-new', 'Qwen3.6-27B'), g = entry('g-new', 'GLM-5.2'); const { fetcher } = setup([q, g]);
    await screen.findByText('q-new/shared');
    expect(screen.getByLabelText('用户模型服务').querySelectorAll('option')).toHaveLength(3);
    fireEvent.change(screen.getByLabelText('用户模型服务'), { target: { value: modelScopeKey(g) } }); await screen.findByText('g-new/shared');
    expect(fetcher.mock.calls.every(c => c[1]?.method === 'GET')).toBe(true);
});
test('explicit old run remains fixed across refresh, model switch and browser remount', async () => {
    const old = entry('q-old', 'Qwen3.6-27B', false), q = entry('q-new', 'Qwen3.6-27B'), g = entry('g-new', 'GLM-5.2');
    localStorage.setItem(`tokenscope.v2.fixed:${page.service_instance_id}`, JSON.stringify({ [modelScopeKey(old)]: entryKey(old) }));
    const view = setup([q, old, g]); await screen.findByText('q-old/shared');
    const newest = entry('q-newest', 'Qwen3.6-27B'); view.replace([newest, { ...q, is_default: false }, old, g]);
    fireEvent.click(screen.getByRole('button', { name: '打开运行' })); fireEvent.click(screen.getByText('刷新目录'));
    await waitFor(() => expect(screen.getByText(/q-newest · 默认/)).toBeVisible());
    expect(screen.getByTestId('shown')).toHaveTextContent('q-old/shared'); fireEvent.click(screen.getByRole('button', { name: '关闭弹窗' }));
    fireEvent.change(screen.getByLabelText('用户模型服务'), { target: { value: modelScopeKey(g) } }); await screen.findByText('g-new/shared');
    fireEvent.change(screen.getByLabelText('用户模型服务'), { target: { value: modelScopeKey(q) } }); await screen.findByText('q-old/shared');
    expect(location.hash).toContain(`revision=${old.source.index_revision}`); view.unmount();
    setup([newest, old, g]); await screen.findByText('q-old/shared');
});
test('fixed history missing never silently selects newer default', async () => {
    const old = entry('q-old', 'Qwen3.6-27B', false), q = entry('q-new', 'Qwen3.6-27B');
    localStorage.setItem(`tokenscope.v2.fixed:${page.service_instance_id}`, JSON.stringify({ [modelScopeKey(old)]: entryKey(old) }));
    setup([q]); await screen.findByText(/固定历史运行已不可读/); expect(screen.queryByTestId('shown')).not.toBeInTheDocument();
});
test('unknown appid does not select another tenant; empty run is not a tenant', async () => {
    history.replaceState(null, '', '#/users?appid=missing'); const e = entry('empty', 'GLM-5.2'); e.appid = null; e.state = 'empty'; e.request_count = '0'; e.prompt_p90 = null;
    setup([e, entry('q', 'Qwen3.6-27B')]); await screen.findByText(/此APPID没有已发布结果/); expect(screen.queryByTestId('shown')).not.toBeInTheDocument();
    expect(screen.getByLabelText('用户APPID').querySelector('option[value="null"]')).toBeNull();
});
test('late cold directory cannot overwrite explicit known-run selection', async () => {
    const q = entry('q', 'Qwen3.6-27B'), g = entry('g', 'GLM-5.2'); const view = setup([q, g], { delayDirectory: true });
    fireEvent.click(screen.getByRole('button', { name: '打开运行' })); fireEvent.change(screen.getByLabelText('用户运行ID'), { target: { value: 'g' } }); fireEvent.click(screen.getByRole('button', { name: '打开' }));
    await screen.findByText('g/shared'); await act(async () => view.release()); expect(screen.getByTestId('shown')).toHaveTextContent('g/shared');
});
for (const restore of ['directory', 'url']) test(`delayed ${restore} automatic receipt must preserve later-opened form and typed input`, async () => {
    if (restore === 'url') history.replaceState(null, '', '#/users?run=q&appid=shared');
    const view = setup([entry('q', 'Qwen3.6-27B')], { delayReceipt: true });
    await waitFor(() => expect(view.receiptPending()).toBe(true));
    fireEvent.click(screen.getByRole('button', { name: '打开运行' }));
    fireEvent.change(screen.getByLabelText('用户运行ID'), { target: { value: 'draft-run-not-submitted' } });
    await act(async () => view.releaseReceipt()); await screen.findByText('q/shared');
    expect(screen.getByRole('dialog')).toBeVisible(); expect(screen.getByLabelText('用户运行ID')).toHaveValue('draft-run-not-submitted');
    expect(view.fetcher.mock.calls.every(c => c[1]?.method === 'GET')).toBe(true);
});
test('automatic selection started after new-analysis form opens also preserves its input', async () => {
    const view = setup([entry('q', 'Qwen3.6-27B')], { delayDirectory: true, delayReceipt: true });
    fireEvent.click(screen.getByRole('button', { name: '新建分析' }));
    fireEvent.change(screen.getByLabelText('输入目录内文件引用'), { target: { value: 'draft.csv' } });
    await act(async () => view.release()); await waitFor(() => expect(view.receiptPending()).toBe(true));
    await act(async () => view.releaseReceipt()); await screen.findByText('q/shared');
    expect(screen.getByLabelText('输入目录内文件引用')).toHaveValue('draft.csv');
});
test('explicit open success still closes the form after receipt resolves', async () => {
    const view = setup([entry('q', 'Qwen3.6-27B')], { delayDirectory: true, delayReceipt: true });
    fireEvent.click(screen.getByRole('button', { name: '打开运行' }));
    fireEvent.change(screen.getByLabelText('用户运行ID'), { target: { value: 'q' } });
    fireEvent.click(screen.getByRole('button', { name: '打开' }));
    await waitFor(() => expect(view.receiptPending()).toBe(true)); expect(screen.getByRole('dialog')).toBeVisible();
    await act(async () => view.releaseReceipt()); await screen.findByText('q/shared');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument(); await act(async () => view.release());
});

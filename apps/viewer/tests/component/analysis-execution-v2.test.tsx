import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AnalysisClient, obj } from '../../src/api/analysis/client';
import type { Catalog, Obj } from '../../src/api/analysis/client';
import { AnalysisApp } from '../../src/features/analysis/AnalysisApp';
import { ExecutionStatus, executionReason } from '../../src/features/analysis/ExecutionStatus';
import type { LoadedReport } from '../../src/features/analysis/model';
import { client, entry, low } from '../unit/analysis/recommendation-fixtures';
import example from '../../src/api/analysis/generated/diagnostics-execution-2.examples.json';

const bus = vi.hoisted(() => ({ listener: null as null | ((api: AnalysisClient, c: Catalog) => void), starts: 0 }));
vi.mock('../../src/state/analysis-discovery', () => ({ DiscoverySession: class {
    constructor(private callbacks: { catalog: (api: AnalysisClient, c: Catalog) => void; status: (s: string) => void }) {}
    run() { bus.starts++; bus.listener = this.callbacks.catalog; this.callbacks.status('报告通知已连接'); }
    stop() { bus.listener = null; }
} }));

function fixture(task = low.task_id, instance = 'fixture', block?: Promise<void>) {
    const sample = structuredClone(low);
    // Replace all task references, keeping evidence and scope from a documented synthetic backend fixture.
    const t = JSON.parse(JSON.stringify(sample).replaceAll(low.task_id, task)) as typeof low;
    const original = client(t, (path, r) => path.endsWith('/recommendation-summary') ? { ...r, configured_recipe_count: '0', recommendation_count: '0' } : path.endsWith('/recommendations') ? { ...r, items: [], next_offset: null } : path.endsWith('/recommendations/capabilities') ? { ...r, service_instance_id: instance } : r).api;
    const e: Obj = { ...entry(t), binding_id: 'binding', binding: { appid: obj(t.report.scope).appid, model_id: 'GLM-5.2', common_name: null }, status: 'partial', directions: ['low_hit'], analysis_completed_at: '2026-11-03T11:00:00Z' };
    const api = new AnalysisClient(instance, async (input, init) => {
        if (block) await block;
        const path = new URL(String(input), 'http://fixture').pathname;
        if (path.endsWith('/execution')) return Response.json({ ...example.execution, task_id: task, scope_id: e.scope_id });
        if (path.endsWith('/items/rule_coverage')) return Response.json({ offset: '0', items: [] });
        return original.fetcher(input, init);
    }, 'diagnostics-execution-2');
    const catalog: Catalog = { snapshot: 'fixed', cursor: 'cursor', defaults: [], selected_reports: [{ binding_id: 'binding', direction: 'low_hit', task_id: task }], items: [e] };
    return { api, catalog, e };
}
async function publish(f: ReturnType<typeof fixture>) { await act(async () => { bus.listener!(f.api, f.catalog); }); }
beforeEach(() => { bus.starts = 0; bus.listener = null; localStorage.clear(); history.replaceState(null, '', '/#/analysis'); });

describe('partial-first discovery in approved analysis UI', () => {
    it('cold bare entry with no local metadata reads partial cards and preserves approved grouping', async () => {
        const f = fixture(); const { container } = render(<AnalysisApp/>); await publish(f);
        await waitFor(() => expect(container.querySelectorAll('.solution-card').length).toBeGreaterThan(0));
        expect(container).toHaveTextContent('发现的差异'); expect(container).toHaveTextContent('部分');
        expect(container).not.toHaveTextContent('当前没有默认完整报告');
        const rules = [...container.querySelectorAll('.solution-card')].map(e => e.getAttribute('data-rule'));
        expect(new Set(rules).size).toBe(rules.length);
        expect(screen.getByRole('combobox', { name: '历史报告' })).toHaveValue(low.task_id);
        expect(screen.getByRole('button', { name: '查看最新' })).toBeEnabled();
    });
    it('explicit history and refresh stay pinned when a new selected report arrives', async () => {
        const f = fixture(), newer = fixture('new-task');
        history.replaceState(null, '', `/#/analysis?binding=binding&direction=low_hit&mode=history&task=${low.task_id}`);
        const view = render(<AnalysisApp/>); await publish(f);
        await waitFor(() => expect(screen.getByRole('combobox', { name: '历史报告' })).toHaveValue(low.task_id));
        await publish({ ...f, catalog: { ...newer.catalog, items: [f.e, newer.e] } });
        expect(screen.getByRole('combobox', { name: '历史报告' })).toHaveValue(low.task_id);
        expect(screen.getByText(/有新报告可查看/)).toBeInTheDocument();
        expect(location.hash).toContain(`task=${low.task_id}`);
        view.unmount(); render(<AnalysisApp/>); await publish({ ...f, catalog: { ...newer.catalog, items: [f.e, newer.e] } });
        await waitFor(() => expect(screen.getByRole('combobox', { name: '历史报告' })).toHaveValue(low.task_id));
    });
    it('late old instance responses cannot replace the new service selection', async () => {
        let release!: () => void; const blocked = new Promise<void>(resolve => { release = resolve; });
        const old = fixture(low.task_id, 'old', blocked), fresh = fixture('fresh-task', 'fresh');
        render(<AnalysisApp/>); await publish(old); await publish(fresh);
        await waitFor(() => expect(screen.getByRole('combobox', { name: '历史报告' })).toHaveValue('fresh-task'));
        await act(async () => { release(); await blocked; });
        expect(screen.getByRole('combobox', { name: '历史报告' })).toHaveValue('fresh-task');
    });
    it('switching to an unselected direction never borrows low-hit results', async () => {
        const f = fixture(); render(<AnalysisApp/>); await publish(f);
        await waitFor(() => expect(screen.getByRole('combobox', { name: '历史报告' })).toHaveValue(low.task_id));
        fireEvent.click(screen.getByRole('button', { name: 'Token异常分析' }));
        await waitFor(() => expect(screen.getByText(/暂无Token异常分析报告/)).toBeInTheDocument());
        expect(screen.queryByText('相同位置的消息出现内容差异')).not.toBeInTheDocument();
    });
    it('keeps appended pages through detail/back and cached re-entry, including return focus', async () => {
        Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', { configurable: true, value: vi.fn() });
        const scroll = vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
        const f = fixture();
        const first = obj((low.responses.recommendations!.items as Obj[])[0]);
        const second = structuredClone(first); second.id = 'second-page-result';
        obj(second.data).recommendation_id = second.id;
        obj(obj(second.data).recipe).title = '第二页修改建议';
        obj(second.data).example_refs = [];
        let pageReads = 0;
        const api = new AnalysisClient('fixture', async (input, init) => {
            const url = new URL(String(input), 'http://fixture');
            if (url.pathname.endsWith('/recommendation-summary')) return Response.json({ ...low.responses['recommendation-summary'], recommendation_count: '2' });
            if (url.pathname.endsWith('/recommendations')) {
                pageReads++;
                const offset = url.searchParams.get('offset')!;
                return Response.json({ ...low.responses.recommendations, offset, items: [offset === '0' ? first : second], next_offset: offset === '0' ? '1' : null });
            }
            return f.api.fetcher(input, init);
        }, 'diagnostics-execution-2');
        render(<AnalysisApp/>); await publish({ ...f, api });
        fireEvent.click(await screen.findByRole('button', { name: '加载更多' }));
        const title = await screen.findByRole('heading', { name: '第二页修改建议' });
        fireEvent.click(within(title.closest('article')!).getByRole('button', { name: /查看证据与改法/ }));
        fireEvent.click(await screen.findByRole('button', { name: '← 返回卡片列表' }));
        const restored = await screen.findByRole('heading', { name: '第二页修改建议' });
        await waitFor(() => expect(within(restored.closest('article')!).getByRole('button', { name: /查看证据与改法/ })).toHaveFocus());
        fireEvent.click(screen.getByRole('button', { name: 'Token异常分析' }));
        await screen.findByText(/暂无Token异常分析报告/);
        fireEvent.click(screen.getByRole('button', { name: '低命中率分析' }));
        expect(await screen.findByRole('heading', { name: '第二页修改建议' })).toBeInTheDocument();
        expect(pageReads).toBe(2); // Re-entry uses the expanded report, never the first-page snapshot.
        scroll.mockRestore();
    });
});

describe('honest execution limits without a telemetry dashboard', () => {
    const data = { direction: 'low_hit', execution: example.execution, summary: {}, ruleCoverage: [{ supported_rules: ['L4'], candidate_comparisons: '9007199254740993', applicable_pairs: null }] } as unknown as LoadedReport;
    it('keeps partial retention distinct from complete scanning and null applicable pairs from zero', () => {
        const { container } = render(<ExecutionStatus data={data}/>);
        expect(container).toHaveTextContent('不等于扫描已停止');
        expect(container).toHaveTextContent('扫描：完整'); expect(container).toHaveTextContent('证据保存：未完整');
        expect(container).toHaveTextContent('适用对数 未单独统计'); expect(container).toHaveTextContent('9,007,199,254,740,993');
        expect(container).not.toHaveTextContent('总耗时');
    });
    it('no recipes, incomplete fragments and retention limits have different explanations', () => {
        const codes = ['NO_CONFIGURED_RECIPES', 'TOKEN_FRAGMENT_INCOMPLETE', 'FRAGMENT_RETENTION_TRUNCATED', 'FINDING_RETENTION_TRUNCATED', 'CANDIDATE_LOOKUP_TRUNCATED', 'COMPARISON_COUNT_BUDGET_EXHAUSTED', 'ENCODING_BUDGET_EXHAUSTED', 'RECIPE_BASIS_MISSING', 'REFERENCE_MAPPING_MISSING'];
        expect(new Set(codes.map(executionReason)).size).toBe(codes.length);
        const token = { ...data, direction: 'token_content', execution: { ...example.execution, selected_directions: ['token_content'], stages: [{ direction: 'token_content', checked_requests: '0', eligible_requests: null, reason_codes: codes, rule_status_counts: { T2: { not_checked: '2' } } }] } } as LoadedReport;
        const { container } = render(<ExecutionStatus data={token}/>);
        for (const code of codes) expect(container).toHaveTextContent(executionReason(code));
        expect(container).toHaveTextContent('已检查请求：0 / 未提供'); expect(container).toHaveTextContent('T2：未检查 2');
    });
    it('legacy execution is explicit and not falsely described as fully checked', () => {
        const { container } = render(<ExecutionStatus data={{ ...data, execution: { availability: 'not_computed' } }}/>);
        expect(container).toHaveTextContent('历史报告未记录新版执行状态');
        expect(container).not.toHaveTextContent('扫描：完整');
    });
});

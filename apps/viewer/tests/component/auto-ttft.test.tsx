import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, expect, test, vi } from 'vitest';
import { TTFT } from '../../src/features/v2/TTFT';
import { V2Client, validateV2 } from '../../src/api/v2/client';
import type { Receipt } from '../../src/api/v2/generated/user';
import type { AutoEvaluation } from '../../src/api/v2/generated/user/HV2AutoEvaluation';
import examples from '../../../../docs/contracts/user-monitoring-v2/2.1.0/examples.json';
const sample = validateV2('user', 'AutoEvaluation', examples.find(e => e.model === 'AutoEvaluation' && e.valid)!.value);
const configs = validateV2('user', 'DefaultPage', examples.find(e => e.model === 'DefaultPage')!.value).configs;
const receipt: Receipt = { service_instance_id: sample.service_instance_id, user_run_id: sample.source.user_run_id, base_run_id: sample.source.base_run_id, model_id: sample.source.model_id, common_name: sample.source.common_name, index_revision: sample.source.index_revision, state: 'ready', error_code: null };
const json = (x: unknown, status = 200) => new Response(JSON.stringify(x), { status, headers: { 'Content-Type': 'application/json' } });
function response(body: Record<string, string>): AutoEvaluation {
    const value = structuredClone(sample);
    Object.assign(value.request, body); Object.assign(value.evaluation.request, Object.fromEntries(Object.entries(body).filter(([k]) => ['submission_key', 'user_run_id', 'appid', 'target_seconds', 'waiting_seconds', 'comparator'].includes(k))));
    value.defaults.revision = body.default_revision!; value.source.user_run_id = body.user_run_id!;
    value.evaluation.scenario.chunk_tokens = body.chunk_tokens ?? value.defaults.chunk_tokens;
    value.chunk_tokens_origin = body.chunk_tokens ? 'request_override' : 'model_default';
    return value;
}
function setup(options: { empty?: boolean; nullTau?: boolean; model?: typeof receipt.model_id; post?: (body: Record<string, string>, init: RequestInit) => Promise<Response> } = {}) {
    const config = structuredClone(configs.find(c => c.model_id === (options.model ?? receipt.model_id))!);
    if (options.nullTau) config.chunk_seconds = null;
    const r = { ...receipt, model_id: config.model_id, common_name: config.common_name };
    const bodies: Record<string, string>[] = [];
    const fetcher = vi.fn(async (url: RequestInfo | URL, init?: RequestInit) => {
        const path = String(url);
        if (path.includes('/ttft/defaults')) return json({ service_instance_id: receipt.service_instance_id, contract_version: '2.1.0', configs: options.empty ? [] : [config] });
        if (init?.method === 'POST') { const body = JSON.parse(String(init.body)) as Record<string, string>; bodies.push(body); return options.post ? options.post(body, init) : json(response(body)); }
        if (path.includes('/ttft/evaluations/')) return json(sample);
        if (path.includes('/evaluations/')) return json(sample.evaluation);
        throw Error(`Unexpected ${path}`);
    });
    const api = new V2Client(receipt.service_instance_id, fetcher);
    const view = render(<TTFT api={api} receipt={r} appid={sample.request.appid}/>);
    return { ...view, fetcher, bodies, config, api, r };
}
async function fill() {
    await screen.findByText('模型默认 revision 1');
    fireEvent.change(screen.getByLabelText('TTFT目标秒'), { target: { value: '8' } });
    fireEvent.change(screen.getByLabelText('非计算耗时W'), { target: { value: '0' } });
}
beforeEach(() => { localStorage.clear(); HTMLDialogElement.prototype.showModal = function () { this.open = true; }; HTMLDialogElement.prototype.close = function () { this.open = false; }; });
for (const model of ['GLM-5.2', 'Qwen3.6-27B', 'DeepSeek-V4-Flash-0731'] as const) test(`backend default ${model}; missing W disabled, explicit zero enabled`, async () => {
    const { config, fetcher } = setup({ model }); await screen.findByText('模型默认 revision 1');
    fireEvent.change(screen.getByLabelText('TTFT目标秒'), { target: { value: '8' } });
    expect(screen.getByRole('button', { name: '评估' })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('非计算耗时W'), { target: { value: '0' } });
    expect(screen.getByRole('button', { name: '评估' })).toBeEnabled();
    fireEvent.click(screen.getByText('设置评估条件'));
    expect(screen.getByText(new RegExp(`τ=${config.chunk_seconds}s`))).toBeVisible();
    expect(screen.getByText(/用户提供 · .*尚未校准/)).toBeVisible();
    expect(String(fetcher.mock.calls[0]![0])).toContain(`model_id=${model}`);
    expect(fetcher.mock.calls).toHaveLength(1);
});
for (const missing of ['unknown', 'null']) test(`${missing} model parameters never fall back`, async () => {
    setup(missing === 'unknown' ? { empty: true } : { nullTau: true });
    await screen.findByText(/当前模型未配置τ/);
    expect(screen.getByRole('button', { name: '评估' })).toBeDisabled();
});
test('auto POST binds revision; K override and restoration do not inject scenario/model/O or scale tau', async () => {
    const { bodies } = setup(); await fill();
    fireEvent.click(screen.getByText('设置评估条件')); fireEvent.change(screen.getByLabelText('覆盖K'), { target: { value: '4096' } });
    fireEvent.click(screen.getByText('按当前条件评估')); await screen.findByText(/评估ID/);
    expect(bodies[0]).toMatchObject({ chunk_tokens: '4096', default_revision: '1', index_revision: receipt.index_revision, waiting_seconds: '0', comparator: 'le' });
    for (const key of ['scenario_id', 'model_id', 'overhead_seconds', 'chunk_seconds']) expect(bodies[0]).not.toHaveProperty(key);
    expect(screen.getByText(/K=4096 · τ=1s/)).toBeVisible();
    fireEvent.click(screen.getByText('设置评估条件')); fireEvent.click(screen.getByText('恢复模型默认K')); fireEvent.click(screen.getByText('按当前条件评估')); await screen.findByText(/评估ID/);
    expect(bodies[1]).not.toHaveProperty('chunk_tokens'); expect(bodies[1]!.submission_key).not.toBe(bodies[0]!.submission_key);
});
test('failed request retries same key; refreshed parameter revision starts new intent', async () => {
    let calls = 0;
    const { bodies, config } = setup({ post: async body => { if (++calls === 1) throw Error('offline'); return json(response(body)); } }); await fill();
    fireEvent.click(screen.getByRole('button', { name: '评估' })); await screen.findByText(/offline/);
    fireEvent.click(screen.getByRole('button', { name: '评估' })); await screen.findByText(/评估ID/);
    expect(bodies[0]!.submission_key).toBe(bodies[1]!.submission_key);
    config.revision = '2'; fireEvent.click(screen.getByText('设置评估条件')); fireEvent.click(screen.getByText('刷新模型默认参数'));
    await screen.findByText('模型默认 revision 2'); fireEvent.click(screen.getByText('按当前条件评估')); await screen.findByText(/评估ID/);
    expect(bodies[2]!.submission_key).not.toBe(bodies[1]!.submission_key); expect(bodies[2]!.default_revision).toBe('2');
});
test('old success/finally after changed inputs cannot end or overwrite a new task', async () => {
    const pending: { body: Record<string, string>; init: RequestInit; resolve: (r: Response) => void }[] = [];
    setup({ post: (body, init) => new Promise(resolve => pending.push({ body, init, resolve })) }); await fill();
    fireEvent.click(screen.getByRole('button', { name: '评估' }));
    fireEvent.change(screen.getByLabelText('非计算耗时W'), { target: { value: '1' } });
    fireEvent.click(screen.getByRole('button', { name: '评估' }));
    expect(pending[0]!.init.signal!.aborted).toBe(true);
    await act(async () => pending[0]!.resolve(json(response(pending[0]!.body))));
    expect(screen.getByRole('button', { name: '评估中…' })).toBeDisabled(); expect(screen.queryByText(/评估ID/)).not.toBeInTheDocument();
    await act(async () => pending[1]!.resolve(json(response(pending[1]!.body)))); await screen.findByText(/W=1s/);
});
test('scope switch aborts previous run result even if response ignores cancellation', async () => {
    let release!: (r: Response) => void; let body!: Record<string, string>; let signal!: AbortSignal;
    const view = setup({ post: (b, init) => { body = b; signal = init.signal!; return new Promise(r => { release = r; }); } }); await fill();
    fireEvent.click(screen.getByRole('button', { name: '评估' }));
    view.rerender(<TTFT api={view.api} receipt={{ ...receipt, user_run_id: 'next' }} appid="next-app"/>);
    expect(signal.aborted).toBe(true); await act(async () => release(json(response(body))));
    expect(screen.queryByText(/评估ID/)).not.toBeInTheDocument(); expect(screen.getByLabelText('非计算耗时W')).toHaveValue('');
});
for (const state of ['large', 'zero', 'one', 'no_budget', 'unavailable'] as const) test(`authoritative ${state} fraction and null remain exact`, async () => {
    setup({ post: async body => { const v = response(body); v.evaluation.prompt_p90 = '900719925474099312345';
        if (state === 'large') { v.evaluation.required_hit_fraction = { numerator: '900719925474099312344', denominator: '900719925474099312345' }; v.evaluation.required_hit_rate = 1; }
        else if (state === 'zero' || state === 'one') { v.evaluation.required_hit_fraction = { numerator: state === 'zero' ? '0' : '1', denominator: '1' }; v.evaluation.required_hit_rate = state === 'zero' ? 0 : 1; }
        else { v.evaluation.status = state; v.evaluation.required_hit_fraction = null; v.evaluation.required_hit_rate = null; v.evaluation.prompt_p90 = state === 'unavailable' ? null : v.evaluation.prompt_p90; }
        return json(v); } }); await fill(); fireEvent.click(screen.getByRole('button', { name: '评估' })); await screen.findByText(/评估ID/);
    expect(screen.getByText(new RegExp(state === 'large' ? '900719925474099312344/900719925474099312345' : state === 'zero' ? '精确比例 0/1' : state === 'one' ? '精确比例 1/1' : '精确比例 —'))).toBeVisible();
});
test('automatic history uses new namespace; legacy remains read-only', async () => {
    const { fetcher } = setup(); await fill(); fireEvent.click(screen.getByText('设置评估条件')); fireEvent.click(screen.getByText('历史评估与情景（只读）'));
    fireEvent.change(screen.getByLabelText('历史ID'), { target: { value: sample.evaluation_id } }); fireEvent.click(screen.getByText('读取历史'));
    await screen.findByText(/只读快照/); expect(String(fetcher.mock.calls.at(-1)![0])).toContain('/ttft/evaluations/');
    fireEvent.change(screen.getByLabelText('历史类型'), { target: { value: 'legacy' } }); fireEvent.click(screen.getByText('读取历史'));
    await waitFor(() => expect(String(fetcher.mock.calls.at(-1)![0])).toContain(`/user-v2/evaluations/${sample.evaluation_id}`));
    expect(fetcher.mock.calls.every(c => c[1]?.method !== 'POST')).toBe(true);
});

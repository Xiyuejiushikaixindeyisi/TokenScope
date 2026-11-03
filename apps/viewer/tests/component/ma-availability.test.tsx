import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import { V2Client } from '../../src/api/v2/client';
import { MAMonitor } from '../../src/features/v2/MAMonitor';
import { MACharts } from '../../src/features/v2/MACharts';
import { maCase } from '../fixtures/ma-availability';
import openapi from '../../../../docs/tasks/monitoring/v2-ma/hv2-availability/candidate.openapi.json';
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
function setup(name: string, count = 1, availability?: (id: string, signal: AbortSignal) => Promise<Response>) {
    localStorage.clear(); const { snapshot, response } = maCase(name); location.hash = `/ma?run=${snapshot.ma_run_id}`;
    const ids = Array.from({ length: count }, (_, n) => `uuid-${n}`);
    const fetcher = vi.fn(async (url: RequestInfo | URL, options?: RequestInit) => {
        const path = String(url);
        if (path.endsWith('/openapi.json')) return json(openapi);
        if (path.includes('/catalog')) return json({ service_instance_id: snapshot.service_instance_id, catalog_revision: '1', total: '1', next_offset: null, entries: [{ ma_run_id: snapshot.ma_run_id, model_standard_name: snapshot.binding.model_standard_name, now_start: snapshot.binding.now_start, now_end: snapshot.binding.now_end, instance_uuids: ids, empty_scope_reason: null }] });
        if (path.includes('/instances/')) {
            const id = path.split('/instances/')[1]!.split('/')[0]!;
            if (path.endsWith('/availability')) return availability ? availability(id, options!.signal as AbortSignal) : json({ ...response, availability: { ...response.availability, instance_uuid: id } });
            return json({ ...snapshot, instance: { ...snapshot.instance, instance_uuid: id } });
        }
        return json({ schema_version: '1.0.0', service_instance_id: snapshot.service_instance_id, ma_run_id: snapshot.ma_run_id, binding: snapshot.binding, state: 'completed', error_code: null, error_detail: null, catalog_revision: '1' });
    });
    return { api: new V2Client(snapshot.service_instance_id, fetcher), fetcher, response, snapshot };
}
test('DS shape: paired null stays null, independent ideal visible, reasons per UUID; snapshot not hidden', async () => {
    const { api, fetcher } = setup('source_cached_missing'); const { container } = render(<MAMonitor api={api}/>);
    await waitFor(() => expect(container.querySelector('[data-availability="unavailable"]')).not.toBeNull());
    const row = container.querySelector('.ma-table tbody tr')!;
    expect(row.querySelectorAll('.hit-line b')[0]).toHaveTextContent('—');
    expect(row.querySelectorAll('.hit-line b')[1]).toHaveTextContent('—');
    expect(row).toHaveTextContent('独立理想 75.0%'); expect(row).toHaveTextContent('本实例源 cached_tokens 缺失');
    fireEvent.click(screen.getByRole('button', { name: '展开详情' }));
    expect(screen.getByText(/成功编码输入 pre/)).toHaveTextContent('理想回放有效 E 1');
    expect(fetcher.mock.calls.every(([, o]) => o?.method !== 'POST')).toBe(true);
});
test('GLM conflict: keep real 25%, hour known 75 and fixed 3600, E differs from encoded count', async () => {
    const { api } = setup('warmup_order_conflict'); const { container } = render(<MAMonitor api={api}/>);
    await waitFor(() => expect(container.querySelector('[data-availability="available"]')).not.toBeNull());
    const row = container.querySelector('.ma-table tbody tr')!;
    expect(row).toHaveTextContent('独立真实 25.0%'); expect(row).toHaveTextContent('预热顺序冲突');
    expect(row.children[5]).toHaveTextContent('75'); expect(row.children[4]).toHaveTextContent('3600 秒');
    fireEvent.click(screen.getByRole('button', { name: '展开详情' }));
    expect(screen.getByText(/成功编码输入 pre/)).toHaveTextContent('now 1；理想回放有效 E 0');
});
for (const name of ['partial_observations', 'valid_zero_cached', 'zero_denominator', 'empty_now']) test(`metric/12-bin semantics ${name}`, () => {
    const { snapshot, response } = maCase(name);
    const { container } = render(<MACharts snapshot={snapshot} explanation={{ state: 'ready', value: response.availability }}/>);
    const table = container.querySelectorAll('.trend-grid details table')[1]!;
    expect(table.querySelectorAll('tr')).toHaveLength(12);
    for (let n = 0; n < 12; n++) expect(table.querySelectorAll('tr')[n]!.querySelector('[data-availability]')).toHaveAttribute('data-availability', response.availability.bins[n]!.state);
    if (name === 'partial_observations') expect(container).toHaveTextContent('仅已知子集，不外推全量');
    if (name === 'valid_zero_cached') expect(container).toHaveTextContent('独立真实命中率 0.0%');
    if (name === 'zero_denominator') expect(container).toHaveTextContent('输入总量为0');
    if (name === 'empty_now') expect(table.querySelector('tr td:nth-child(2)')).toHaveTextContent('0');
});
test('legacy 409 keeps values; transient explanation error retries one row without POST', async () => {
    let attempts = 0;
    const { api, response, fetcher } = setup('source_cached_missing', 2, async id => {
        if (id === 'uuid-0') return json({ error: { code: 'AVAILABILITY_NOT_RECORDED', message: 'old' } }, 409);
        if (++attempts === 1) return json({ error: { code: 'UNAVAILABLE', message: 'temporary' } }, 503);
        return json({ ...response, availability: { ...response.availability, instance_uuid: id } });
    });
    const { container } = render(<MAMonitor api={api}/>);
    await screen.findByText(/历史结果未记录细化原因/);
    fireEvent.click(await screen.findByRole('button', { name: '重试指标说明' }));
    await waitFor(() => expect(screen.queryByRole('button', { name: '重试指标说明' })).not.toBeInTheDocument());
    expect(attempts).toBe(2); expect(container.querySelectorAll('.ma-table tbody tr')).toHaveLength(2);
    expect(fetcher.mock.calls.filter(([u]) => String(u).endsWith('uuid-0/availability'))).toHaveLength(1);
    expect(fetcher.mock.calls.every(([, o]) => o?.method !== 'POST')).toBe(true);
});
test('13 placeholders, at most four explanation reads; unmount cancels queue and late results', async () => {
    const pending: { id: string; signal: AbortSignal; resolve(r: Response): void }[] = [];
    const { api, response } = setup('source_cached_missing', 13, (id, signal) => new Promise(resolve => pending.push({ id, signal, resolve })));
    const view = render(<MAMonitor api={api}/>);
    await waitFor(() => expect(view.container.querySelectorAll('.ma-table tbody tr')).toHaveLength(13));
    await waitFor(() => expect(pending).toHaveLength(4));
    view.unmount(); expect(pending.every(p => p.signal.aborted)).toBe(true);
    await act(async () => { pending.forEach(p => p.resolve(json({ ...response, availability: { ...response.availability, instance_uuid: p.id } }))); });
    expect(pending).toHaveLength(4); expect(view.container).toBeEmptyDOMElement();
});
test('wrong binding explanation is rejected while original snapshot remains', async () => {
    const { api, response } = setup('source_cached_missing', 1, async id => json({ ...response, binding: { ...response.binding, model_id: 'GLM-5.2' }, availability: { ...response.availability, instance_uuid: id } }));
    const { container } = render(<MAMonitor api={api}/>);
    await screen.findByRole('button', { name: '重试指标说明' });
    expect(within(container).getByRole('alert')).toHaveTextContent('范围不一致');
    expect(container.querySelector('.ma-table')).toHaveTextContent('独立理想 75.0%');
});

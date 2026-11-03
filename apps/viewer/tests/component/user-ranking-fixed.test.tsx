import { act, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import { Ranking } from '../../src/features/v2/Ranking';
import { V2Client, validateV2 } from '../../src/api/v2/client';
import type { Receipt } from '../../src/api/v2/generated/user';
import examples from '../../../../docs/contracts/user-monitoring-v2/2.0.0/examples.json';
const base = validateV2('user', 'Ranking', examples.find(x => x.model === 'Ranking' && x.valid)!.value);
const receipt: Receipt = { service_instance_id: base.service_instance_id, user_run_id: base.user_run_id, base_run_id: 'base', model_id: 'Qwen3.6-27B', common_name: base.common_name, index_revision: base.index_revision, state: 'ready', error_code: null };
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
afterEach(() => vi.useRealTimers());
test('fixed clock: initial and unchanged search cannot reset page; Enter cancels old debounce', async () => {
    vi.useFakeTimers(); const reads: URLSearchParams[] = [];
    const fetcher = vi.fn(async (input: RequestInfo | URL) => {
        const q = new URL(String(input), 'http://localhost').searchParams; reads.push(q); const offset = Number(q.get('offset'));
        return json({ ...base, total: '25', next_offset: offset === 0 ? '20' : null, rows: Array.from({ length: offset === 0 ? 20 : 5 }, (_, i) => ({ ...base.rows[0], appid: `APP-${i + offset}`, total_prompt_tokens: '900719925474099312345', ideal_hit_rate: null })) });
    });
    const view = render(<Ranking api={new V2Client(base.service_instance_id, fetcher)} receipt={receipt} active select={() => {}}/>);
    await act(async () => {}); expect(view.container.querySelectorAll('tbody tr')).toHaveLength(20);
    fireEvent.click(screen.getByText('下一页')); await act(async () => {}); expect(view.container.querySelectorAll('tbody tr')).toHaveLength(5);
    await act(async () => vi.advanceTimersByTime(300)); expect(screen.getByText(/第2页/)).toBeVisible(); expect(reads.map(q => q.get('offset'))).toEqual(['0', '20']);
    fireEvent.keyDown(screen.getByLabelText('搜索APPID'), { key: 'Enter' }); await act(async () => vi.advanceTimersByTime(300)); expect(screen.getByText(/第2页/)).toBeVisible();
    fireEvent.change(screen.getByLabelText('搜索APPID'), { target: { value: 'old' } }); await act(async () => vi.advanceTimersByTime(100));
    fireEvent.change(screen.getByLabelText('搜索APPID'), { target: { value: 'latest' } }); await act(async () => vi.advanceTimersByTime(299)); expect(screen.getByText(/第2页/)).toBeVisible();
    await act(async () => vi.advanceTimersByTime(1)); expect(screen.getByText(/第1页/)).toBeVisible(); expect(reads.at(-1)!.get('appid_contains')).toBe('latest');
    fireEvent.change(screen.getByLabelText('搜索APPID'), { target: { value: 'enter' } }); fireEvent.keyDown(screen.getByLabelText('搜索APPID'), { key: 'Enter' }); await act(async () => {});
    fireEvent.click(screen.getByText('下一页')); await act(async () => {}); await act(async () => vi.advanceTimersByTime(300));
    expect(screen.getByText(/第2页/)).toBeVisible(); expect(reads.at(-1)!.get('appid_contains')).toBe('enter'); expect(reads.at(-1)!.get('offset')).toBe('20');
});
test('revision conflict retries once with fixed historical revision, never adopts returned new index', async () => {
    const fetcher = vi.fn().mockImplementationOnce(() => Promise.resolve(json({ error: { code: 'INDEX_REVISION_CONFLICT', message: 'changed' } }, 409))).mockImplementation(() => Promise.resolve(json({ ...base, index_revision: 'new-index' })));
    render(<Ranking api={new V2Client(base.service_instance_id, fetcher)} receipt={receipt} active select={() => {}}/>);
    await screen.findByText('排行范围不一致'); expect(fetcher).toHaveBeenCalledTimes(2);
    expect(fetcher.mock.calls.every(c => String(c[0]).includes(`index_revision=${base.index_revision}`))).toBe(true);
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
});

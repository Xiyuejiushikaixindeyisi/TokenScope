import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { SourceLink } from '../../src/features/analysis/SourceLink';

const api = vi.hoisted(() => ({ catalog: vi.fn(), receipt: vi.fn(), contract: vi.fn() }));
vi.mock('../../src/api/client', () => ({ getJson: api.catalog }));
vi.mock('../../src/api/v2/client', () => ({
    verifyUserContract: api.contract,
    V2Client: class { request = api.receipt; },
}));

const source = { user_run_id: 'ur-original', base_run_id: 'base-original', common_name: 'service-original', model_id: 'GLM-5.2' };
const entry = { scope: { appid: 'search & long', source } };
const origin = '#/analysis?task=original';
function deferred<T>() {
    let resolve!: (value: T) => void;
    const promise = new Promise<T>(done => { resolve = done; });
    return { promise, resolve };
}
const click = () => fireEvent.click(screen.getByRole('button', { name: '查看原报告监控来源' }));

beforeEach(() => {
    vi.resetAllMocks();
    history.replaceState(null, '', `/${origin}`);
    api.catalog.mockResolvedValue({ service_instance_id: 'instance-original' });
    api.contract.mockResolvedValue(undefined);
    api.receipt.mockResolvedValue(source);
});

describe('historical monitoring source navigation', () => {
    it('uses the user monitor run parameter and preserves the exact appid', async () => {
        render(<SourceLink entry={entry} />);
        click();
        await waitFor(() => expect(location.hash).toMatch(/^#\/users\?/));
        const query = new URLSearchParams(location.hash.split('?')[1]);
        expect(query.get('run')).toBe(source.user_run_id);
        expect(query.get('appid')).toBe(entry.scope.appid);
        expect(query.has('user_run_id')).toBe(false);
        expect(api.receipt).toHaveBeenCalledWith('user', 'Receipt', '/runs/ur-original', { signal: expect.any(AbortSignal) });
    });

    it('keeps base sources on overview with their original run and model', async () => {
        const base = { base_run_id: source.base_run_id, common_name: source.common_name, model_id: source.model_id };
        render(<SourceLink entry={{ scope: { ...entry.scope, source: base } }} />);
        click();
        await waitFor(() => expect(location.hash).toMatch(/^#\/overview\?/));
        const query = new URLSearchParams(location.hash.split('?')[1]);
        expect(query.get('run')).toBe(base.base_run_id);
        expect(query.get('model')).toBe(base.model_id);
        expect(query.get('appid')).toBe(entry.scope.appid);
        expect(api.contract).not.toHaveBeenCalled();
        expect(api.receipt).not.toHaveBeenCalled();
    });

    it.each(['base_run_id', 'common_name', 'model_id'] as const)('refuses a mismatched %s without navigating', async field => {
        api.receipt.mockResolvedValue({ ...source, [field]: 'different' });
        render(<SourceLink entry={entry} />);
        click();
        expect(await screen.findByRole('alert')).toHaveTextContent('监控来源身份不匹配');
        expect(location.hash).toBe(origin);
        expect(screen.getByRole('button')).toBeEnabled();
    });

    it('cancels a late old receipt and cannot replace the newly selected source', async () => {
        const late = deferred<typeof source>();
        const next = { ...source, user_run_id: 'ur-next', base_run_id: 'base-next' };
        api.receipt.mockImplementationOnce(() => late.promise).mockResolvedValue(next);
        const view = render(<SourceLink entry={entry} />);
        click();
        await waitFor(() => expect(api.receipt).toHaveBeenCalledTimes(1));
        const signal = api.receipt.mock.calls[0]![3].signal as AbortSignal;
        view.rerender(<SourceLink entry={{ scope: { ...entry.scope, source: next } }} />);
        expect(signal.aborted).toBe(true);
        click();
        await waitFor(() => expect(new URLSearchParams(location.hash.split('?')[1]).get('run')).toBe(next.user_run_id));
        const selected = location.hash;
        await act(async () => { late.resolve(source); await late.promise; });
        expect(location.hash).toBe(selected);
        expect(screen.queryByRole('alert')).toBeNull();
    });

    it('does not navigate after unmount while the contract check is pending', async () => {
        const late = deferred<void>();
        api.contract.mockImplementation(() => late.promise);
        const view = render(<SourceLink entry={entry} />);
        click();
        await waitFor(() => expect(api.contract).toHaveBeenCalledTimes(1));
        view.unmount();
        await act(async () => { late.resolve(); await late.promise; });
        expect(api.receipt).not.toHaveBeenCalled();
        expect(location.hash).toBe(origin);
    });

    it('does not navigate a late base source after unmount', async () => {
        const late = deferred<{ service_instance_id: string }>();
        api.catalog.mockImplementation(() => late.promise);
        const view = render(<SourceLink entry={{ scope: { ...entry.scope, source: { base_run_id: 'base-original', model_id: 'GLM-5.2' } } }} />);
        click();
        const signal = api.catalog.mock.calls[0]![3].signal as AbortSignal;
        view.unmount();
        expect(signal.aborted).toBe(true);
        await act(async () => { late.resolve({ service_instance_id: 'instance-original' }); await late.promise; });
        expect(location.hash).toBe(origin);
    });
});

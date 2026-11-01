import { describe, it, expect } from 'vitest';
import { obj, arr } from '../../../src/api/analysis/client';
import { cardFromRow, loadReport, getCard, checks } from '../../../src/features/analysis/model';
import { resultExamples, resultPage } from '../../../src/api/analysis/recommendations';
import { allTasks, samples, low, token, client, entry } from './recommendation-fixtures';

describe('published recommendation reports', () => {
    it('consumes every actual report without scanning findings, fragments or old evaluations', async () => {
        for (const t of allTasks) for (const direction of ['low_hit', 'token_content'] as const) {
            const { api, calls } = client(t); const r = await loadReport(api, entry(t), direction);
            expect(r.summary.availability).toBe(t.responses['recommendation-summary']!.availability);
            expect(calls.every(x => !/items\/|comparisons\/|requests\//.test(x))).toBe(true);
            expect(r.cards.every(x => x.rule !== 'T1')).toBe(true);
        }
        expect(checks.token_content).toHaveLength(3);
    });
    it('shows one low-hit solution with N=6 and counts L4 members separately from its three examples', async () => {
        const { api } = client(low); const r = await loadReport(api, entry(low), 'low_hit');
        const solutions = r.cards.filter(x => x.kind === 'recommendation');
        expect(solutions).toHaveLength(1); expect(solutions[0]!.affected).toBe('6'); expect(solutions[0]!.total).toBe('6');
        const difference = r.cards.find(x => x.rule === 'L4')!;
        expect(BigInt(difference.affected!)).toBeGreaterThan(BigInt(arr(difference.data.example_refs).length));
        expect(difference.metrics).toBeNull();
    });
    it('preserves zero, negative gains, missing values and independent bases sharing an evaluation', async () => {
        const r = await loadReport(client(token).api, entry(token), 'token_content');
        expect(r.cards.some(c => c.affected === '0' && c.metrics?.input_tokens_delta === '0')).toBe(true);
        expect(r.cards.some(c => c.affected === null && c.metrics === null && c.limitation.includes('业务依据'))).toBe(true);
        expect(r.cards.some(c => c.metrics && BigInt(String(c.metrics.input_tokens_delta)) > 0n)).toBe(true);
        expect(r.cards.filter(c => c.evaluation?.evaluation_id === r.cards[0]!.evaluation!.evaluation_id)).toHaveLength(2);
        const t = samples.find(x => x.name === 'test_less_input_can_increase_f0')!.tasks[0]!;
        const c = (await loadReport(client(t).api, entry(t), 'token_content')).cards[0]!;
        expect(c.metrics?.input_tokens_delta).toBe('-4'); expect(c.metrics?.compute_tokens_delta).toBe('124');
    });
    it('rejects cross-scope results and inconsistent metrics instead of displaying borrowed benefit', async () => {
        const a = client(low, (path, r) => path.endsWith('/recommendations') ? { ...r, scope_id: 'other' } : r);
        await expect(loadReport(a.api, entry(low), 'low_hit')).rejects.toThrow('IDENTITY');
        const row = structuredClone((low.responses.recommendations!.items as { id: string; data: Record<string, unknown> }[])[0]!);
        obj(row.data.metrics).input_tokens_delta = '999999';
        expect(() => cardFromRow(row, 'recommendation', entry(low), 'low_hit')).toThrow('DELTA');
    });
    it('rejects page cycles and wrong evidence owners; resolves opaque difference deep links', async () => {
        const a = client(low, (path, r) => path.endsWith('/recommendations') ? { ...r, next_offset: '0' } : r);
        await expect(resultPage(a.api, entry(low), 'recommendation', 'low_hit')).rejects.toThrow('CYCLE');
        const normal = client(low); const r = await loadReport(normal.api, entry(low), 'low_hit');
        const d = r.cards.find(x => x.kind === 'difference_group')!;
        expect((await getCard(normal.api, { ...r, cards: [] }, d.id)).id).toBe(d.id);
        const bad = client(low, (path, response) => { if (!path.endsWith('/examples')) return response; const copied = structuredClone(response); obj(obj(arr(copied.items)[0]).data).owner_id = 'other'; return copied; });
        await expect(resultExamples(bad.api, entry(low), d.kind, d.data)).rejects.toThrow('OWNER');
    });
    it('keeps legacy reports explicitly uncomputed', async () => {
        const t = samples.find(x => x.name === 'test_legacy_is_not_computed_an0')!.tasks[0]!;
        const r = await loadReport(client(t).api, entry(t), 'token_content');
        expect(r.summary.availability).toBe('not_computed'); expect(r.cards).toEqual([]); expect(r.hasMore).toBe(false);
    });
});

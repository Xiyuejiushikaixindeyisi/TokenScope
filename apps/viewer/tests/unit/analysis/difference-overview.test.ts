import { describe, expect, it } from 'vitest';
import { AnalysisClient, arr, obj, str } from '../../../src/api/analysis/client';
import { getCard, loadCardExamples, loadReport } from '../../../src/features/analysis/model';
import { client, entry, low } from './recommendation-fixtures';

function fixture(complete = true, countMismatch = false) {
    const original = client(low).api;
    const first = obj(arr(low.responses['difference-groups']!.items)[0]);
    const group = obj(first.data), members = arr(group.member_requests);
    const rows = Array.from({ length: 5 }, (_, i) => {
        const id = `overview-fixture-${i}`;
        return { id, data: { ...group, group_id: id, rule_id: i === 4 ? 'L5' : 'L4', members_complete: complete || i !== 1,
            member_requests: i % 2 ? members.slice(1, 4) : members.slice(0, 2),
            example_refs: arr(group.example_refs).map((ref, n) => ({ ...obj(ref), id: `${id}-example-${n}` })) } };
    });
    const calls: string[] = [];
    const api = new AnalysisClient('fixture', async (input, init) => {
        const u = new URL(String(input), 'http://fixture'); calls.push(u.pathname + u.search);
        if (u.pathname.endsWith('/difference-groups')) {
            const offset = Number(u.searchParams.get('offset'));
            return Response.json({ ...low.responses['difference-groups'], offset: String(offset), items: rows.slice(offset, offset + 2), next_offset: offset + 2 < rows.length ? String(offset + 2) : null });
        }
        if (u.pathname.endsWith('/recommendation-summary')) return Response.json({ ...low.responses['recommendation-summary'], difference_group_count: countMismatch ? '4' : '5' });
        if (u.pathname.includes('/difference-groups/') && u.pathname.endsWith('/examples')) {
            const id = u.pathname.split('/').at(-2)!;
            const response = obj(await (await original.fetcher(`/diagnostics/tasks/${low.task_id}/difference-groups/${str(first.id)}/examples`, init)).json());
            const items = arr(response.items).map((value, i) => {
                const data = obj(obj(value).data);
                return { id: `${id}-example-${i}`, data: { ...data, example_id: `${id}-example-${i}`, owner_id: id,
                    ...(id.endsWith('-1') ? { before: data.comparison, comparison: data.before } : {}) } };
            });
            return Response.json({ ...response, items });
        }
        return original.fetcher(input, init);
    });
    return { api, calls, rows };
}

describe('detector-level difference cards', () => {
    it('merges every metadata page, deduplicates requests and preserves incomplete discovery', async () => {
        const { api, calls } = fixture(false);
        const r = await loadReport(api, entry(low), 'low_hit');
        expect(r.cards.map(x => x.rule)).toEqual(['L1', 'L4', 'L5']);
        const l4 = r.cards.find(x => x.rule === 'L4')!;
        expect(l4.affected).toBe('4'); expect(l4.limitation).toContain('未完整');
        expect(r.cards.find(x => x.rule === 'L5')!.limitation).toBe('');
        expect(r.hasMore).toBe(false);
        expect(calls.filter(x => x.includes('difference-groups?'))).toHaveLength(3);
        expect(calls.some(x => x.endsWith('/examples'))).toBe(false);
    });
    it('reads at most three representative owners and removes swapped-pair duplicate examples', async () => {
        const { api, calls } = fixture(); const r = await loadReport(api, entry(low), 'low_hit');
        const card = r.cards.find(x => x.rule === 'L4')!;
        const examples = await loadCardExamples(api, r, card);
        expect(examples).toHaveLength(3);
        expect(examples.map(x => x.owner_id)).toEqual(Array(3).fill('overview-fixture-0'));
        expect(calls.filter(x => x.endsWith('/examples'))).toHaveLength(3);
        expect(calls.some(x => x.includes('/overview-fixture-3/examples'))).toBe(false);
    });
    it('resolves a historical group deep link to its one detector card', async () => {
        const { api, rows } = fixture(); const r = await loadReport(api, entry(low), 'low_hit');
        const card = await getCard(api, r, rows[3]!.id);
        expect(card.id).toBe('difference-detector:L4'); expect(card.affected).toBe('4');
    });
    it('rejects missing metadata instead of presenting an incomplete count as a full overview', async () => {
        const { api } = fixture(true, true);
        await expect(loadReport(api, entry(low), 'low_hit')).rejects.toThrow('DIFFERENCE_COUNT_MISMATCH');
    });
});

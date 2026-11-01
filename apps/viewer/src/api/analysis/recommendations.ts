import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import schemas from './generated/analysis-recommendations-1.json';
import { arr, canonical, obj, str, taskPath } from './client';
import type { AnalysisClient, Item, Obj } from './client';

export const RECOMMENDATIONS_VERSION = 'analysis-recommendations-1';
export type ResultKind = 'recommendation' | 'difference_group';
export type Direction = 'low_hit' | 'token_content';
const paths: Record<ResultKind, string> = { recommendation: 'recommendations', difference_group: 'difference-groups' };
const ajv = new Ajv({ strict: false, allErrors: true });
addFormats(ajv);
ajv.addKeyword({ keyword: 'x-integer-minimum', type: 'string', validate: (minimum: string, value: string) => /^-?\d+$/.test(value) && BigInt(value) >= BigInt(minimum) });
const validators = Object.fromEntries(Object.entries(schemas.models).map(([name, schema]) => [name, ajv.compile(schema)]));
export function validateResult(kind: string, value: unknown): Obj {
    if (!validators[kind]?.(value)) throw Error(`INVALID_RECOMMENDATION_RESPONSE:${kind}`);
    return obj(value);
}
export function bound(value: Obj, entry: Obj) {
    if (value.task_id !== entry.task_id || value.scope_id !== entry.scope_id) throw Error('RECOMMENDATION_IDENTITY_MISMATCH');
}
const capabilities = new WeakSet<AnalysisClient>();
export async function checkRecommendations(api: AnalysisClient, signal?: AbortSignal) {
    if (capabilities.has(api)) return;
    const c = await api.get('/diagnostics/recommendations/capabilities', {}, signal);
    if (c.version !== RECOMMENDATIONS_VERSION || c.service_instance_id !== api.instance || c.read_only !== true || canonical(c.token_rule_ids) !== canonical(['T2', 'T3', 'T4'])) throw Error('RECOMMENDATION_CAPABILITY_MISMATCH');
    if (canonical(c.schemas) !== canonical(schemas.models)) throw Error('RECOMMENDATION_SCHEMA_MISMATCH');
    capabilities.add(api);
}
export function verifyItem(kind: ResultKind, row: Item, entry: Obj, direction: Direction) {
    const r = validateResult(kind, row.data);
    bound(r, entry);
    if (r[kind === 'recommendation' ? 'recommendation_id' : 'group_id'] !== row.id) throw Error('RESULT_ID_MISMATCH');
    for (const ref of arr(r.example_refs).map(obj)) if (ref.task_id !== entry.task_id) throw Error('EXAMPLE_REFERENCE_MISMATCH');
    if (kind === 'difference_group') {
        const keys = arr(r.member_requests).map(canonical);
        if (new Set(keys).size !== keys.length || keys.length > BigInt(str(obj(entry.scope).request_count))) throw Error('DIFFERENCE_MEMBERS_MISMATCH');
        if (arr(r.member_requests).some(x => obj(x).base_run_id !== obj(obj(entry.scope).source).base_run_id)) throw Error('DIFFERENCE_SOURCE_MISMATCH');
        return;
    }
    if (r.direction !== direction) throw Error('RECOMMENDATION_DIRECTION_MISMATCH');
    const impact = obj(r.impact), total = BigInt(str(impact.total_requests));
    if (impact.total_requests !== obj(entry.scope).request_count) throw Error('IMPACT_SCOPE_MISMATCH');
    for (const key of ['matched_requests', 'matched_checked_requests', 'modified_requests']) if (impact[key] !== null && BigInt(str(impact[key])) > total) throw Error('IMPACT_COUNT_MISMATCH');
    for (const ref of arr(r.support_refs).map(obj)) {
        bound(ref, entry);
        if (obj(ref.request_key).base_run_id !== obj(obj(entry.scope).source).base_run_id) throw Error('SUPPORT_SOURCE_MISMATCH');
    }
    for (const key of ['prepared_plan_ref', 'execution_plan_ref', 'evaluation_ref']) if (r[key] && obj(r[key]).task_id !== entry.task_id) throw Error('PLAN_TASK_MISMATCH');
    if (r.evaluation) {
        const e = obj(r.evaluation);
        if (e.scope_id !== entry.scope_id || e.direction !== direction || e.evaluation_id !== obj(r.evaluation_ref).id || e.plan_id !== obj(r.execution_plan_ref).id) throw Error('EVALUATION_REFERENCE_MISMATCH');
        if (impact.evaluation_complete === true && (obj(e.before).n !== impact.total_requests || obj(e.after).n !== impact.total_requests || obj(e.modified_before).n !== impact.modified_requests || obj(e.modified_after).n !== impact.modified_requests)) throw Error('EVALUATION_COUNT_MISMATCH');
        if (r.metrics) {
            const m = obj(r.metrics), before = obj(e.before), after = obj(e.after);
            for (const [field, metric] of [['p', 'input_tokens'], ['c', 'compute_tokens']] as const) {
                const b = BigInt(str(before[field])), a = BigInt(str(after[field]));
                if (BigInt(str(m[metric + '_delta'])) !== a - b) throw Error('METRIC_DELTA_MISMATCH');
                const ratio = m[metric + '_ratio'];
                if (b === 0n ? ratio !== null : ratio === null || BigInt(str(obj(ratio).numerator)) * b !== (a - b) * BigInt(str(obj(ratio).denominator))) throw Error('METRIC_RATIO_MISMATCH');
            }
            const p0 = BigInt(str(before.p)), p1 = BigInt(str(after.p)), g = m.gain_percentage_points;
            if (p0 && p1 && (!g || BigInt(str(obj(g).numerator)) * p0 * p1 !== 100n * (BigInt(str(after.h)) * p0 - BigInt(str(before.h)) * p1) * BigInt(str(obj(g).denominator)))) throw Error('HIT_GAIN_MISMATCH');
        }
    }
}
export async function summary(api: AnalysisClient, entry: Obj, signal?: AbortSignal) {
    await checkRecommendations(api, signal);
    const s = validateResult('recommendation_summary', await api.get(`${taskPath(str(entry.task_id))}/recommendation-summary`, {}, signal));
    bound(s, entry);
    return s;
}
export interface ResultPage { items: Item[]; next: string | null; availability: string }
export async function resultPage(api: AnalysisClient, entry: Obj, kind: ResultKind, direction: Direction, offset = '0', signal?: AbortSignal, limit = 20): Promise<ResultPage> {
    const p = await api.get(`${taskPath(str(entry.task_id))}/${paths[kind]}`, { offset, limit, ...(kind === 'recommendation' ? { direction } : {}) }, signal);
    bound(p, entry);
    if (p.version !== RECOMMENDATIONS_VERSION || p.offset !== offset || !['computed', 'not_computed'].includes(str(p.availability))) throw Error('RESULT_PAGE_MISMATCH');
    const next = p.next_offset === null ? null : str(p.next_offset);
    if (next !== null && (!/^(0|[1-9]\d*)$/.test(next) || BigInt(next) <= BigInt(offset))) throw Error('RESULT_PAGE_CYCLE');
    const items = arr(p.items).map(value => { const r = obj(value); const row = { id: str(r.id), data: obj(r.data) }; verifyItem(kind, row, entry, direction); return row; });
    if (new Set(items.map(x => x.id)).size !== items.length || (p.availability === 'not_computed' && (items.length || next !== null))) throw Error('INVALID_RESULT_PAGE');
    return { items, next, availability: str(p.availability) };
}
export async function resultExamples(api: AnalysisClient, entry: Obj, kind: ResultKind, owner: Obj, signal?: AbortSignal): Promise<Obj[]> {
    const id = str(owner[kind === 'recommendation' ? 'recommendation_id' : 'group_id']);
    const p = await api.get(`${taskPath(str(entry.task_id))}/${paths[kind]}/${encodeURIComponent(id)}/examples`, {}, signal);
    bound(p, entry);
    if (p.version !== RECOMMENDATIONS_VERSION || p.next_offset !== null) throw Error('EXAMPLES_PAGE_MISMATCH');
    const refs = arr(owner.example_refs).map(x => str(obj(x).id));
    const rows = arr(p.items).map(obj);
    if (rows.length > 3 || canonical(rows.map(x => x.id)) !== canonical(refs)) throw Error('EXAMPLES_REFERENCE_MISMATCH');
    return rows.map(row => {
        const e = validateResult('recommendation_example', row.data);
        bound(e, entry);
        if (e.owner_id !== id || row.id !== e.example_id) throw Error('EXAMPLE_OWNER_MISMATCH');
        for (const side of ['before', 'comparison', 'after']) if (e[side]) {
            const source = obj(obj(e[side]).source);
            if (obj(source.request_key).base_run_id !== obj(obj(entry.scope).source).base_run_id) throw Error('EXAMPLE_SOURCE_MISMATCH');
        }
        if (e.after && canonical(obj(obj(e.after).source).request_key) !== canonical(obj(obj(e.before).source).request_key)) throw Error('EXAMPLE_AFTER_REQUEST_MISMATCH');
        return e;
    });
}

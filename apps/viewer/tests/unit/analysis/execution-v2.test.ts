import { describe, expect, it } from 'vitest';
import { AnalysisClient, canonical, obj, arr, verifySelectedReports } from '../../../src/api/analysis/client';
import type { Obj } from '../../../src/api/analysis/client';
import { schemaSignature, validateExecution, verifyExecutionCapabilities } from '../../../src/api/analysis/execution';
import wire from '../../../src/api/analysis/generated/diagnostics-execution-2.json';
import examples from '../../../src/api/analysis/generated/diagnostics-execution-2.examples.json';
import { cardFromRow, loadReport } from '../../../src/features/analysis/model';
import { client, entry, low } from './recommendation-fixtures';
import { readFileSync } from 'node:fs';
import { analysisReportKey } from '../../../src/state/analysis-cache-key';
import { ANALYSIS_METADATA_V2, readAnalysisMetadata, saveAnalysisMetadata } from '../../../src/state/analysis-metadata';
import { CACHE_KEY } from '../../../src/storage/analysis-cache';

const base = examples.catalog;
const item = base.items[0]!;
export const capabilities = { service_instance_id: base.service_instance_id, version: 'diagnostics-execution-2', discovery_version: 'diagnostics-discovery-2', directions: ['low_hit', 'token_content'], minimum_selected_directions: '1', legacy_read_compatible: true, submission_url: '/diagnostics/v2/tasks', catalog_url: '/diagnostics/v2/catalog', partial_policy: 'ready_preferred_published_partial_fallback', budget_semantics: 'direction_isolated_compute_rule_reserved_retention', schemas: wire };
function apiFor(handler: (u: URL) => unknown) {
    return new AnalysisClient(base.service_instance_id, async (input, init) => {
        expect(init?.method).toBe('GET');
        expect(new Headers(init?.headers).get('x-tokenscope-service-instance')).toBe(base.service_instance_id);
        return Response.json(handler(new URL(String(input), 'http://fixture')));
    }, 'diagnostics-execution-2');
}
const selection = (e: Obj, direction = 'low_hit') => ({ binding_id: e.binding_id, direction, task_id: e.task_id, sequence: e.sequence, status: e.status, selection_kind: e.status === 'ready' ? 'ready' : 'published_partial_fallback' });

describe('frozen diagnostics v2 consumer', () => {
    it('persists v2 metadata under its actual contract without rewriting legacy cache or storing source bodies', async () => {
        localStorage.clear(); localStorage.setItem(CACHE_KEY, '[]');
        const api = apiFor(() => base), catalog = await api.catalog();
        saveAnalysisMetadata(api, catalog, localStorage, 100);
        const raw = localStorage.getItem(ANALYSIS_METADATA_V2)!;
        expect(raw).toContain('diagnostics-discovery-2/diagnostics-execution-2');
        expect(raw).not.toContain('profile_json'); expect(raw).not.toContain('settings_json');
        expect(localStorage.getItem(CACHE_KEY)).toBe('[]');
        expect(readAnalysisMetadata(localStorage, 101)[0]?.task).toBe(item.task_id);
        expect(readAnalysisMetadata(localStorage, 8 * 86400000)).toEqual([]);
        const denied = { getItem() { throw Error('denied'); }, setItem() { throw Error('denied'); } } as unknown as Storage;
        expect(() => saveAnalysisMetadata(api, catalog, denied)).not.toThrow();
        expect(readAnalysisMetadata(denied)).toEqual([]);
    });
    it('isolates cache identities by actual version, instance, task, scope, digest and direction', () => {
        const v2 = apiFor(() => ({})), v1 = new AnalysisClient(v2.instance);
        const key = analysisReportKey(v2, item, 'low_hit');
        expect(analysisReportKey(v1, item, 'low_hit')).not.toBe(key);
        expect(analysisReportKey(new AnalysisClient('new', v2.fetcher, v2.executionVersion), item, 'low_hit')).not.toBe(key);
        for (const field of ['task_id', 'scope_id', 'report_digest']) expect(analysisReportKey(v2, { ...item, [field]: 'other' }, 'low_hit')).not.toBe(key);
        expect(analysisReportKey(v2, item, 'token_content')).not.toBe(key);
    });
    it('accepts the published TestClient sample with exact schema and selection checks', async () => {
        const actual = process.env.TOKENSCOPE_ANALYSIS_ACTUAL_EXAMPLES ? JSON.parse(readFileSync(process.env.TOKENSCOPE_ANALYSIS_ACTUAL_EXAMPLES, 'utf8')) as typeof examples : examples;
        validateExecution('catalog', actual.catalog); validateExecution('execution', actual.execution);
        verifySelectedReports(actual.catalog.items, actual.catalog.selected_reports);
        const api = new AnalysisClient(actual.catalog.service_instance_id, async () => Response.json(actual.execution), 'diagnostics-execution-2');
        expect((await api.execution(actual.catalog.items[0]!))?.availability).toBe('computed');
    });
    it('validates frozen catalog/execution and enforces decimal strings and nonnegative telemetry', () => {
        validateExecution('catalog', base); validateExecution('execution', examples.execution);
        const bad = structuredClone(examples.execution); bad.telemetry.counts['source.rows_read'] = '-1';
        expect(() => validateExecution('execution', bad)).toThrow('INVALID_EXECUTION');
        expect(() => validateExecution('execution', { ...examples.execution, stages: [{ ...examples.execution.stages[0], checked_requests: 0 }] })).toThrow();
    });
    it('uses explicit v2 handshake and refuses unavailable v2 instead of silently downgrading', async () => {
        const calls: string[] = [];
        const fetcher: typeof fetch = async path => {
            const url = String(path); calls.push(url);
            return Response.json(url.endsWith('/v2/capabilities') ? capabilities : url.includes('discovery') ? { version: 'diagnostics-discovery-1', service_instance_id: base.service_instance_id } : { contract_version: 'analysis-common-1.0', http_version: 'diagnostics-http-1', service_instance_id: base.service_instance_id });
        };
        expect((await AnalysisClient.connect(undefined, fetcher)).executionVersion).toBe('diagnostics-execution-2');
        expect(calls).toContain('/diagnostics/v2/capabilities');
        await expect(AnalysisClient.connect(undefined, async (p, init) => String(p).includes('/v2/') ? new Response('', { status: 404 }) : fetcher(p, init))).rejects.toThrow('404');
    });
    it('resolves local renamed refs while refusing real field-constraint drift', () => {
        verifyExecutionCapabilities(capabilities, base.service_instance_id);
        const renamed = JSON.parse(JSON.stringify(wire).replaceAll('StageV2', 'AppStage'));
        verifyExecutionCapabilities({ ...capabilities, schemas: renamed }, base.service_instance_id);
        renamed.execution.$defs.AppStage.properties.checked_requests.anyOf[0]['x-integer-minimum'] = '-1';
        expect(() => verifyExecutionCapabilities({ ...capabilities, schemas: renamed }, base.service_instance_id)).toThrow('SCHEMA_MISMATCH');
        expect(() => schemaSignature({ $ref: '#/absent' })).toThrow('MISSING_SCHEMA');
        expect(() => verifyExecutionCapabilities({ ...capabilities, service_instance_id: 'other' }, base.service_instance_id)).toThrow('CAPABILITY');
    });
    it('resolves selected references on later pages under a single fixed snapshot', async () => {
        const paths: string[] = [];
        const api = apiFor(u => { paths.push(u.pathname); return { ...base, items: u.searchParams.get('after') === '0' ? [] : [item], next_after: u.searchParams.get('after') === '0' ? '1' : null }; });
        const c = await api.catalog();
        expect(c.defaults).toEqual([]); expect(c.selected_reports?.[0]?.task_id).toBe(item.task_id);
        expect(paths).toEqual(['/diagnostics/v2/catalog', '/diagnostics/v2/catalog']);
    });
    it.each(['snapshot', 'selection', 'duplicate', 'cycle'])('rejects %s corruption across pages', async fault => {
        const api = apiFor(u => {
            const first = u.searchParams.get('after') === '0';
            return { ...base, items: fault === 'duplicate' || !first ? [item] : [], next_after: first ? '1' : fault === 'cycle' ? '1' : null,
                snapshot: !first && fault === 'snapshot' ? base.snapshot + 'x' : base.snapshot,
                selected_reports: !first && fault === 'selection' ? [] : base.selected_reports };
        });
        await expect(api.catalog()).rejects.toThrow();
    });
    it.each(['appid', 'model_id', 'common_name', 'source_kind'])('rejects a borrowed catalog binding %s', async field => {
        const api = apiFor(() => ({ ...base, items: [{ ...item, binding: { ...item.binding, [field]: field === 'source_kind' ? 'user_v2' : 'another' } }] }));
        await expect(api.catalog()).rejects.toThrow('CATALOG_BINDING_MISMATCH');
    });
    it('preserves ready priority, latest publication within status and direction isolation', () => {
        const ready = { ...item, task_id: 'ready', status: 'ready', sequence: '2', default_eligible: true };
        const newer = { ...item, task_id: 'newer-partial', sequence: '3' };
        const token = { ...item, task_id: 'token-only', sequence: '4', directions: ['token_content'] };
        const list = [item, ready, newer, token];
        expect(() => verifySelectedReports(list, [selection(ready), selection(token, 'token_content')])).not.toThrow();
        expect(() => verifySelectedReports(list, [selection(newer), selection(token, 'token_content')])).toThrow();
        expect(() => verifySelectedReports(list, [selection(ready)])).toThrow('MISSING');
        expect(() => verifySelectedReports([item, newer], [selection(newer)])).not.toThrow();
        expect(() => verifySelectedReports([item], [selection(item), selection(item)])).toThrow();
        for (const changed of [{ legacy: true }, { status: 'failed' }, { task_kind: 'evaluation' }, { report_published: false }]) {
            expect(() => verifySelectedReports([{ ...item, ...changed }], [])).not.toThrow();
        }
    });
    it('validates execution task, scope, status and explicit selected direction', async () => {
        expect((await apiFor(() => examples.execution).execution(item))?.status).toBe('partial');
        for (const change of [{ task_id: 'other' }, { scope_id: 'other' }, { status: 'ready' }, { selected_directions: ['token_content'] }]) {
            await expect(apiFor(() => ({ ...examples.execution, ...change })).execution(item)).rejects.toThrow();
        }
        const legacy = { ...examples.execution, availability: 'not_computed', selected_directions: null, telemetry: null, stages: [] };
        expect((await apiFor(() => legacy).execution(item))?.availability).toBe('not_computed');
    });
    it('computed empty recommendations and zero recipes still read existing difference groups', async () => {
        const { api, calls } = client(low, (path, response) => path.endsWith('/recommendation-summary') ? { ...response, recommendation_count: '0', configured_recipe_count: '0' } : path.endsWith('/recommendations') ? { ...response, items: [], next_offset: null } : response);
        const r = await loadReport(api, entry(low), 'low_hit');
        expect(r.cards.length).toBeGreaterThan(0);
        expect(r.cards.every(c => c.kind === 'difference_group')).toBe(true);
        expect(calls.some(p => p.endsWith('/difference-groups'))).toBe(true);
        expect(canonical(r.entry)).toBe(canonical(entry(low)));
    });
    it('reads legacy not_computed difference pages without inventing results or relaxing availability consistency', async () => {
        const summaryOverride = (r: Obj) => ({ ...r, availability: 'not_computed', recommendation_count: '0', configured_recipe_count: null, difference_group_count: '0' });
        const good = client(low, (path, r) => path.endsWith('/recommendation-summary') ? summaryOverride(r) : path.endsWith('/difference-groups') ? { ...r, availability: 'not_computed', items: [], next_offset: null } : r);
        expect((await loadReport(good.api, entry(low), 'low_hit')).cards).toEqual([]);
        expect(good.calls.some(p => p.endsWith('/difference-groups'))).toBe(true);
        const inconsistent = client(low, (path, r) => path.endsWith('/recommendation-summary') ? { ...r, availability: 'not_computed' } : r);
        await expect(loadReport(inconsistent.api, entry(low), 'low_hit')).rejects.toThrow('SUMMARY_PAGE_MISMATCH');
    });
    it('keeps the strict >1pp and complete-evaluation gates with algebraically valid metrics', () => {
        function row(h: number, numerator: string, denominator: string) {
            const raw = structuredClone(obj(arr(low.responses.recommendations!.items)[0]));
            const data = obj(raw.data), evaluation = obj(data.evaluation), metrics = obj(data.metrics);
            Object.assign(obj(evaluation.before), { p: '10000', h: '2000', c: '8000' });
            Object.assign(obj(evaluation.after), { p: '10000', h: String(h), c: String(10000 - h) });
            Object.assign(metrics, { input_tokens_delta: '0', input_tokens_ratio: { numerator: '0', denominator: '10000' }, compute_tokens_delta: String(2000 - h), compute_tokens_ratio: { numerator: String(2000 - h), denominator: '8000' }, gain_percentage_points: { numerator, denominator } });
            return { id: String(raw.id), data };
        }
        expect(() => cardFromRow(row(2050, '1', '2'), 'recommendation', entry(low), 'low_hit')).toThrow('INVALID_LOW_HIT_QUALIFICATION');
        expect(() => cardFromRow(row(2100, '1', '1'), 'recommendation', entry(low), 'low_hit')).toThrow('INVALID_LOW_HIT_QUALIFICATION');
        const valid = row(2110, '11', '10');
        expect(cardFromRow(valid, 'recommendation', entry(low), 'low_hit')).not.toBeNull();
        obj(obj(valid.data.evaluation).coverage).complete = false;
        expect(() => cardFromRow(valid, 'recommendation', entry(low), 'low_hit')).toThrow('INVALID_LOW_HIT_QUALIFICATION');
    });
});
it('accepts exact frozen v2 read-only capability while keeping schemas strict', () => {
    expect(() => verifyExecutionCapabilities({ ...capabilities, directions: [], execution_enabled: false }, base.service_instance_id)).not.toThrow();
    expect(() => verifyExecutionCapabilities({ ...capabilities, directions: [], execution_enabled: true }, base.service_instance_id)).toThrow();
    expect(() => verifyExecutionCapabilities({ ...capabilities, directions: [], execution_enabled: false, schemas: {} }, base.service_instance_id)).toThrow();
});

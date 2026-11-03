import { expect, test, vi } from 'vitest';
import Ajv2020 from 'ajv/dist/2020';
import schemas from '../../src/api/v2/generated/user/hv2-schemas.json';
import examples from '../../../../docs/contracts/user-monitoring-v2/2.1.0/examples.json';
import contract from '../../src/api/v2/generated/user/hv2.openapi.json';
import runtime from '../fixtures/user-runtime.openapi.json';
import { assertUserContract } from '../../src/api/v2/user-contract';
import { V2Client, validateV2 } from '../../src/api/v2/client';
import { discoverUsers, analysisSource, monitorSourceUrl } from '../../src/features/v2/user-discovery';
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const page = validateV2('user', 'DiscoveryPage', examples.find(e => e.model === 'DiscoveryPage' && e.valid)!.value);
test('2.1.0 exact fourteen operations preserves nine original signatures', () => { expect(() => assertUserContract(contract)).not.toThrow(); });
test('actual aggregate create_app OpenAPI satisfies user contract and legacy signatures', () => { expect(() => assertUserContract(runtime)).not.toThrow(); });
for (const kind of ['version', 'response', 'request', 'constraint']) test(`user handshake rejects ${kind} drift`, () => {
    const copy = structuredClone(contract);
    if (kind === 'version') copy.paths['/monitoring/user-v2/runs'].get['x-user-contract-version'] = '2.0.0';
    if (kind === 'response') delete (copy.paths['/monitoring/user-v2/runs'].get.responses as Record<string, unknown>)['200'];
    if (kind === 'request') copy.components.schemas.AutoEvaluationRequest.required = [];
    if (kind === 'constraint') copy.components.schemas.AutoEvaluationRequest.additionalProperties = true;
    expect(() => assertUserContract(copy)).toThrow();
});
for (const example of examples) test(`strict user 2.1 fixture ${example.model} valid=${example.valid} ${examples.indexOf(example)}`, () => {
    const schema = (schemas as Record<string, object>)[example.model]!;
    const validator = new Ajv2020({ strict: false, coerceTypes: false, useDefaults: false }).compile(schema);
    expect(validator(example.value)).toBe(example.valid);
    if (example.valid) expect(validator({ ...example.value, extra: true })).toBe(false);
});
test('complete snapshot pagination carries fingerprint and does not POST', async () => {
    const fetcher = vi.fn().mockResolvedValueOnce(json({ ...page, entries: [page.entries[0]], next_offset: '1' })).mockResolvedValueOnce(json({ ...page, entries: [page.entries[1]] }));
    const result = await discoverUsers(new V2Client(page.service_instance_id, fetcher), new AbortController().signal);
    expect(result).toEqual(page.entries);
    expect(fetcher.mock.calls[1]![0]).toContain(`snapshot=${page.snapshot}`);
    expect(fetcher.mock.calls[1]![0]).toContain('offset=1');
    expect(fetcher.mock.calls.every(c => c[1].method === 'GET')).toBe(true);
});
test('snapshot conflict discards partial page and starts bounded fresh collection', async () => {
    const next = { ...page, snapshot: 'b'.repeat(64), entries: [page.entries[1]], total: '1' };
    const fetcher = vi.fn().mockResolvedValueOnce(json({ ...page, entries: [page.entries[0]], next_offset: '1' })).mockResolvedValueOnce(json({ error: { code: 'DISCOVERY_SNAPSHOT_CONFLICT', message: 'changed' } }, 409)).mockResolvedValueOnce(json(next));
    expect(await discoverUsers(new V2Client(page.service_instance_id, fetcher), new AbortController().signal)).toEqual(next.entries);
    expect(fetcher.mock.calls[2]![0]).not.toContain('snapshot=');
    const fail = vi.fn().mockImplementation(() => Promise.resolve(json({ error: { code: 'DISCOVERY_SNAPSHOT_CONFLICT', message: 'changed' } }, 409)));
    await expect(discoverUsers(new V2Client(page.service_instance_id, fail), new AbortController().signal)).rejects.toThrow(); expect(fail).toHaveBeenCalledTimes(3);
});
test('cancelled late directory page cannot continue pagination', async () => {
    let release!: (r: Response) => void;
    const fetcher = vi.fn(() => new Promise<Response>(r => { release = r; }));
    const c = new AbortController(); const pending = discoverUsers(new V2Client(page.service_instance_id, fetcher), c.signal);
    c.abort(); release(json({ ...page, next_offset: '1' })); await expect(pending).rejects.toThrow(); expect(fetcher).toHaveBeenCalledTimes(1);
});
test('identity failure invalidates directory client, ordinary 503 does not retry', async () => {
    for (const code of ['INSTANCE_MISMATCH', 'UNAVAILABLE']) {
        const fetcher = vi.fn().mockImplementation(() => Promise.resolve(json({ error: { code, message: 'fault' } }, code === 'UNAVAILABLE' ? 503 : 409)));
        const api = new V2Client(page.service_instance_id, fetcher);
        await expect(discoverUsers(api, new AbortController().signal)).rejects.toThrow();
        expect(api.signal.aborted).toBe(code === 'INSTANCE_MISMATCH'); expect(fetcher).toHaveBeenCalledTimes(1);
    }
});
test('analysis selection is complete Trace appid set, never base-run or file-time window', () => {
    const entry = page.entries[0]!;
    expect(analysisSource(entry)).toEqual({ source_kind: 'user_v2', user_run_id: entry.source.user_run_id, appid: entry.appid, expected_index_revision: entry.source.index_revision, window: null });
    expect(() => analysisSource({ ...entry, appid: null })).toThrow();
    const query = new URLSearchParams(monitorSourceUrl(entry).split('?')[1]);
    expect(query.get('run')).toBe(entry.source.user_run_id); expect(query.get('revision')).toBe(entry.source.index_revision);
    expect(query.has('base_run_id')).toBe(false); expect(query.has('window')).toBe(false);
});

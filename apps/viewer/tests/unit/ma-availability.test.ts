import { expect, test, vi } from 'vitest';
import { V2Client, validateV2 } from '../../src/api/v2/client';
import { assertAvailabilityScope, readMAAvailability } from '../../src/features/v2/MAAvailability';
import { availabilityCases, maCase } from '../fixtures/ma-availability';
import openapi from '../../../../docs/tasks/monitoring/v2-ma/hv2-availability/candidate.openapi.json';
import runtime from '../fixtures/ma-availability-runtime.openapi.json';
import { resolvedOperationSignature } from '../../src/api/v2/openapi-equivalence';
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const availabilityPath = '/monitoring/ma/runs/{ma_run_id}/instances/{instance_uuid}/availability';
test('real create_app aggregate OpenAPI resolves renamed output and module-qualified schemas', async () => {
    const { snapshot, response } = maCase('source_cached_missing');
    const fetcher = vi.fn().mockResolvedValueOnce(json(runtime)).mockResolvedValueOnce(json(response));
    expect((await readMAAvailability(new V2Client(snapshot.service_instance_id, fetcher), snapshot, new AbortController().signal)).state).toBe('ready');
    expect(fetcher).toHaveBeenCalledTimes(2);
});
for (const drift of ['field', 'constraint', 'response', 'route', 'parameter']) test(`aggregate OpenAPI rejects ${drift} drift before reading availability`, async () => {
    const altered = structuredClone(runtime);
    const operation = altered.paths[availabilityPath].get;
    if (drift === 'field') altered.components.schemas.AvailabilityResponse.properties.ma_run_id.type = 'number';
    if (drift === 'constraint') altered.components.schemas.AvailabilityResponse.additionalProperties = true;
    if (drift === 'response') delete (operation.responses as Record<string, unknown>)['503'];
    if (drift === 'route') delete (altered.paths as Record<string, unknown>)[availabilityPath];
    if (drift === 'parameter') operation.parameters[0]!.required = false;
    const { snapshot } = maCase('source_cached_missing');
    const fetcher = vi.fn().mockResolvedValue(json(altered));
    expect((await readMAAvailability(new V2Client(snapshot.service_instance_id, fetcher), snapshot, new AbortController().signal)).state).toBe('error');
    expect(fetcher).toHaveBeenCalledTimes(1);
});
test('reference resolution rejects cycles, missing/external references and siblings', () => {
    const ref = { $ref: '#/components/schemas/A' };
    expect(() => resolvedOperationSignature(ref, { A: ref })).toThrow();
    expect(() => resolvedOperationSignature(ref, {})).toThrow();
    expect(() => resolvedOperationSignature({ $ref: 'https://example.invalid/schema' }, {})).toThrow();
    expect(() => resolvedOperationSignature({ ...ref, nullable: true }, { A: { type: 'string' } })).toThrow();
});
for (const item of availabilityCases) test(`strict frozen availability + original snapshot ${item.name}`, () => {
    const { snapshot, response } = maCase(item.name);
    expect(() => assertAvailabilityScope(snapshot, response)).not.toThrow();
    expect(() => validateV2('ma', 'AvailabilityResponse', { ...response, invented: 1 })).toThrow();
    expect(() => validateV2('ma', 'AvailabilityResponse', { ...response, availability: { ...response.availability, schema_version: '2.0.0' } })).toThrow();
    expect(() => validateV2('ma', 'AvailabilityResponse', { ...response, availability: { ...response.availability, bins: [] } })).toThrow();
});
for (const field of ['service', 'run', 'uuid', 'model', 'binding', 'coverage']) test(`reject wrong ${field} association`, () => {
    const { snapshot, response } = maCase('source_cached_missing');
    if (field === 'service') response.service_instance_id = 'other';
    if (field === 'run') response.ma_run_id = 'other';
    if (field === 'uuid') response.availability.instance_uuid = 'other';
    if (field === 'model') response.availability.model_standard_name = 'other';
    if (field === 'binding') response.binding.now_start = '2026-10-20T09:00:00Z';
    if (field === 'coverage') response.availability.coverage.encoded = '42';
    expect(() => assertAvailabilityScope(snapshot, response)).toThrow('范围不一致');
});
test('additive handshake verifies schema; all reads keep identity and no-store; old 409 preserves snapshot', async () => {
    const { snapshot, response } = maCase('source_cached_missing');
    const fetcher = vi.fn().mockResolvedValueOnce(json(openapi)).mockResolvedValueOnce(json({ error: { code: 'AVAILABILITY_NOT_RECORDED', message: 'legacy' } }, 409)).mockResolvedValueOnce(json(response));
    const api = new V2Client(snapshot.service_instance_id, fetcher);
    expect(await readMAAvailability(api, snapshot, new AbortController().signal)).toEqual({ state: 'legacy' });
    expect((await readMAAvailability(api, snapshot, new AbortController().signal)).state).toBe('ready');
    expect(fetcher).toHaveBeenCalledTimes(3);
    for (const [, options] of fetcher.mock.calls.slice(1)) { expect(options.method).toBe('GET'); expect(options.cache).toBe('no-store'); expect(options.headers['X-TokenScope-Instance-Id']).toBe(snapshot.service_instance_id); }
    expect(snapshot.instance.ideal.hit_rate).toBe(0.75);
});
test('bad handshake or 503 are retryable errors, never legacy or automatic POST', async () => {
    const { snapshot } = maCase('warmup_order_conflict');
    const fetcher = vi.fn().mockResolvedValueOnce(json({ paths: {} })).mockResolvedValueOnce(json(openapi)).mockResolvedValueOnce(json({ error: { code: 'UNAVAILABLE', message: 'temporary' } }, 503));
    const api = new V2Client(snapshot.service_instance_id, fetcher);
    expect((await readMAAvailability(api, snapshot, new AbortController().signal)).state).toBe('error');
    expect((await readMAAvailability(api, snapshot, new AbortController().signal)).state).toBe('error');
    expect(fetcher).toHaveBeenCalledTimes(3);
});
test('abort during handshake starts no old availability request', async () => {
    const { snapshot } = maCase('source_cached_missing'); let finish!: (r: Response) => void;
    const fetcher = vi.fn(() => new Promise<Response>(r => { finish = r; }));
    const api = new V2Client(snapshot.service_instance_id, fetcher), controller = new AbortController();
    const pending = readMAAvailability(api, snapshot, controller.signal);
    controller.abort(); finish(json(openapi));
    await expect(pending).rejects.toThrow(); expect(fetcher).toHaveBeenCalledTimes(1);
});

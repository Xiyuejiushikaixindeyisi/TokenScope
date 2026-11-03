import { afterEach, expect, it, vi } from 'vitest';
import { DiscoverySession } from '../../../src/state/analysis-discovery';
import wire from '../../../src/api/analysis/generated/diagnostics-execution-2.json';
import sample from '../../../src/api/analysis/generated/diagnostics-execution-2.examples.json';

afterEach(() => vi.useRealTimers());
it('aligns v2 catalog on terminal/reset/reconnect, ignores heartbeat and duplicates, and aborts on stop', async () => {
    vi.useFakeTimers();
    let instance = sample.catalog.service_instance_id;
    let stream!: ReadableStreamDefaultController<Uint8Array>;
    let reads = 0;
    const paths: string[] = [];
    const states: string[] = [];
    const fetched: typeof fetch = async (input, init) => {
        const u = new URL(String(input), 'http://test'); paths.push(u.pathname);
        if (u.pathname.endsWith('/v2/capabilities')) return Response.json({ service_instance_id: instance, version: 'diagnostics-execution-2', discovery_version: 'diagnostics-discovery-2', directions: ['low_hit', 'token_content'], minimum_selected_directions: '1', legacy_read_compatible: true, submission_url: '/diagnostics/v2/tasks', catalog_url: '/diagnostics/v2/catalog', partial_policy: 'ready_preferred_published_partial_fallback', budget_semantics: 'direction_isolated_compute_rule_reserved_retention', schemas: wire });
        if (u.pathname === '/diagnostics/capabilities') return Response.json({ contract_version: 'analysis-common-1.0', http_version: 'diagnostics-http-1', service_instance_id: instance });
        if (u.pathname.endsWith('/discovery/capabilities')) return Response.json({ version: 'diagnostics-discovery-1', service_instance_id: instance });
        expect(init?.method).toBe('GET');
        expect(new Headers(init?.headers).get('x-tokenscope-service-instance')).toBe(instance);
        if (u.pathname.endsWith('/v2/catalog')) { reads++; return Response.json({ ...sample.catalog, service_instance_id: instance }); }
        if (u.pathname.endsWith('/discovery/events')) {
            expect(u.searchParams.get('cursor')).toBe(sample.catalog.event_cursor);
            return new Response(new ReadableStream<Uint8Array>({ start(controller) { stream = controller; init?.signal?.addEventListener('abort', () => { try { controller.close(); } catch { /* already cancelled */ } }, { once: true }); } }), { headers: { 'Content-Type': 'text/event-stream' } });
        }
        throw Error(`Unexpected GET: ${u.pathname}`);
    };
    const session = new DiscoverySession({ catalog: api => { states.push(api.instance); }, status: () => {} }, fetched);
    const run = session.run();
    const settle = async () => { for (let i = 0; i < 200; i++) await Promise.resolve(); };
    const send = (s: string) => stream.enqueue(new TextEncoder().encode(s));
    try {
        await vi.waitFor(() => expect(stream).toBeDefined()); expect(reads).toBe(1);
        send(': heartbeat\n\n'); await vi.waitFor(() => expect(stream).toBeDefined()); expect(reads).toBe(1);
        const { scope: _scope, ...item } = sample.catalog.items[0]!; void _scope;
        const event = { ...item, version: 'diagnostics-discovery-1', service_instance_id: instance, event_id: 'opaque-next' };
        const frame = `event: terminal\nid: opaque-next\ndata: ${JSON.stringify(event)}\n\n`;
        send(frame); await settle(); expect(reads).toBe(2);
        send(frame); await settle(); expect(reads).toBe(2);
        send(`event: reset\ndata: ${JSON.stringify({ version: 'diagnostics-discovery-1', service_instance_id: instance, reason: 'reset', catalog_url: '/diagnostics/discovery/catalog' })}\n\n`);
        await settle(); instance = 'new-service'; await vi.advanceTimersByTimeAsync(1300); await settle();
        expect(states.at(-1)).toBe('new-service'); expect(reads).toBe(3);
        stream.close(); await settle(); await vi.advanceTimersByTimeAsync(1300); await settle();
        expect(reads).toBe(4);
        expect(paths.some(p => p === '/diagnostics/discovery/catalog' || p.includes('/tasks/'))).toBe(false);
    } finally { session.stop(); await run; }
    const final = reads; await vi.advanceTimersByTimeAsync(31000); expect(reads).toBe(final);
});

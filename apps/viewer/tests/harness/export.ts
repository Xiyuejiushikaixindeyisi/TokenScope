import { CSV_HEADER } from '../../src/domain/export-protocol';
import { exportStream, beginExport } from '../../src/features/exports/export-controller';
const scope = { service_instance_id: '11111111-1111-4111-8111-111111111111', view_schema_version: '1' as const, run_id: '22222222-2222-4222-8222-222222222222', model_id: 'GLM-5.2', appid: 'app' };
const expected = { format: 'csv' as const, scope, filter: { metric: 'prompt_tokens' as const, lower: '0', upper: null, hash_id: null, hash_match: 'exact' as const }, sort: { by: 'prompt_tokens' as const, order: 'desc' as const, tie_breaker: 'source_record_index_asc' as const } };
const encoder = new TextEncoder();
function response(rows: number, rowSize = 1024, bad = false, targetBytes?: number) {
  const head = encoder.encode(CSV_HEADER + '\r\n');
  const first = `${scope.service_instance_id},1,${scope.run_id},GLM-5.2,app,${'a'.repeat(64)},1,`;
  const last = ',2026-10-27T00:00:00Z,100,90,80,10,0\r\n';
  const row = encoder.encode(first + 'x'.repeat(rowSize - first.length - last.length) + last);
  const lastRow = targetBytes ? encoder.encode(first + 'x'.repeat(targetBytes - head.length - (rows - 1) * rowSize - first.length - last.length) + last) : row;
  let sent = 0, headerOffset = 0, rowOffset = 0;
  const body = new ReadableStream<Uint8Array>({ type: 'bytes', pull(controller) {
    const c = controller as ReadableByteStreamController, request = c.byobRequest!;
    const view = new Uint8Array(request.view!.buffer, request.view!.byteOffset, request.view!.byteLength); let used = 0;
    while (used < view.length) {
      if (headerOffset < head.length) { const n = Math.min(head.length - headerOffset, view.length - used); view.set(head.subarray(headerOffset, headerOffset + n), used); used += n; headerOffset += n; }
      else if (sent < rows) { const current = sent === rows - 1 ? lastRow : row; const n = Math.min(current.length - rowOffset, view.length - used); view.set(current.subarray(rowOffset, rowOffset + n), used); used += n; rowOffset += n; if (rowOffset === current.length) { sent++; rowOffset = 0; } }
      else break;
    }
    if (used) request.respond(used);
    else { if (bad) { c.enqueue(encoder.encode('truncated')); } c.close(); if (!bad) request.respond(0); }
  } }, { highWaterMark: 0 });
  return new Response(body, { headers: { 'Content-Type': 'text/csv;charset=utf-8', 'Cache-Control': 'no-store', 'Content-Disposition': 'attachment; filename="test.csv"', 'X-Export-Schema-Version': '1', 'X-Export-Row-Count': String(rows), 'X-TokenScope-Instance-Id': scope.service_instance_id, 'X-Export-Run-Id': scope.run_id, 'X-CSV-Text-Escaping': 'apostrophe' } });
}
async function run(options: { rows: number; rowSize?: number; targetBytes?: number; fallback?: boolean; bad?: boolean; cancelAt?: number; failAt?: number; slow?: boolean; begin?: boolean }) {
  const abort = new AbortController(); let writes = 0, closed = 0, aborted = 0, outstanding = 0, maxWrites = 0;
  const root = await navigator.storage.getDirectory(); const handle = await root.getFileHandle('export-test.csv', { create: true }); const writable = options.fallback ? undefined : await handle.createWritable();
  const sink = writable ? { async write(bytes: Uint8Array) { outstanding++; maxWrites = Math.max(maxWrites, outstanding); writes++; if (options.failAt === writes) { outstanding--; throw new Error('SYNTHETIC_DISK_ERROR'); } if (options.slow) await new Promise(resolve => setTimeout(resolve, 2)); await writable.write(bytes as Uint8Array<ArrayBuffer>); outstanding--; if (options.cancelAt === writes) abort.abort(); }, async close() { closed++; await writable.close(); }, async abort() { aborted++; await writable.abort(); } } : undefined;
  try {
    let result;
    if (options.begin) { Object.defineProperty(window, 'showSaveFilePicker', { configurable: true, value: () => Promise.resolve({ createWritable: () => Promise.resolve(sink) }) }); const first = beginExport('/synthetic-export', 'test.csv', expected, abort.signal, (async () => response(options.rows, options.rowSize, options.bad, options.targetBytes)) as typeof fetch); let concurrency = ''; try { await beginExport('/synthetic-export', 'test.csv', expected, abort.signal); } catch (e) { concurrency = String(e); } result = await first; return { ...result, blob: undefined, closed, aborted, writes, maxWrites, concurrency, fileSize: (await handle.getFile()).size }; }
    result = await exportStream(response(options.rows, options.rowSize, options.bad, options.targetBytes), expected, abort.signal, sink);
    return { ...result, blob: undefined, blobSize: result.blob?.size, closed, aborted, writes, maxWrites, fileSize: (await handle.getFile()).size };
  } catch (e) { return { error: String(e), closed, aborted, writes, maxWrites }; }
}
Object.assign(window, { runExport: run, exportReady: true });

async function fixture(bytes: number[], metadata: { service_instance_id: string; view_schema_version: '1'; run_id: string; model_id: string; appid: string; expected_rows: string; filter: typeof expected.filter; sort: typeof expected.sort }, format: 'ndjson' | 'csv', broken = false) {
  let offset = 0, closed = 0, aborted = 0;
  const root = await navigator.storage.getDirectory(), handle = await root.getFileHandle('fixture.' + format, { create: true }), writable = await handle.createWritable();
  const source = new ReadableStream<Uint8Array>({ pull(c) { if (offset === bytes.length) { if (broken) c.error(new Error('SYNTHETIC_NETWORK_DISCONNECT')); else c.close(); return; } c.enqueue(Uint8Array.from(bytes.slice(offset, offset + 17))); offset = Math.min(bytes.length, offset + 17); } }, { highWaterMark: 0 });
  const res = new Response(source, { headers: { 'Content-Type': format === 'csv' ? 'text/csv' : 'application/x-ndjson', 'Cache-Control': 'no-store', 'Content-Disposition': 'attachment', 'X-Export-Schema-Version': '1', 'X-Export-Row-Count': metadata.expected_rows, 'X-TokenScope-Instance-Id': metadata.service_instance_id, 'X-Export-Run-Id': metadata.run_id, 'X-CSV-Text-Escaping': 'apostrophe' } });
  try { const result = await exportStream(res, { format, scope: metadata, filter: metadata.filter, sort: metadata.sort }, new AbortController().signal, { write: b => writable.write(b as Uint8Array<ArrayBuffer>), async close() { closed++; await writable.close(); }, async abort() { aborted++; await writable.abort(); } }); return { ...result, closed, aborted, bytesEqual: JSON.stringify([...new Uint8Array(await (await handle.getFile()).arrayBuffer())]) === JSON.stringify(bytes) }; }
  catch (e) { return { error: String(e), closed, aborted }; }
}
Object.assign(window, { verifyFixture: fixture });

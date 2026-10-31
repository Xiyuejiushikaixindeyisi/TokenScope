import { MAX_CHUNK_BYTES, FALLBACK_BYTES } from '../../domain/export-protocol';
import type { ExportExpected } from '../../domain/export-protocol';
export interface FileSink { write(chunk: Uint8Array): Promise<void>; close(): Promise<void>; abort(): Promise<void> }
export interface ExportResult { rows: string; verification: string; bytes: number; maxInflight: number; saved: boolean; blob?: Blob }
let active = false;
function workerValidator() {
  const worker = new Worker(new URL('../../workers/export-validator.ts', import.meta.url), { type: 'module' });
  let sequence = 0; let recycled: ArrayBuffer | undefined;
  const pending = new Map<number, { resolve(value?: { rows: string; verification: string }): void; reject(error: Error): void }>();
  worker.onmessage = (event: MessageEvent<{ id: number; error?: string; buffer?: ArrayBuffer; result?: { rows: string; verification: string } }>) => { if (event.data.buffer) recycled = event.data.buffer; const task = pending.get(event.data.id); if (!task) return; pending.delete(event.data.id); if (event.data.error) task.reject(new Error(event.data.error)); else task.resolve(event.data.result); };
  worker.onerror = () => { for (const task of pending.values()) task.reject(new Error('EXPORT_WORKER_FAILED')); pending.clear(); };
  return {
    send(kind: 'init' | 'chunk' | 'finish', expected?: ExportExpected, bytes?: Uint8Array) {
      const id = ++sequence;
      let buffer: ArrayBuffer | undefined;
      if (bytes) { buffer = recycled?.byteLength === bytes.byteLength ? recycled : new ArrayBuffer(bytes.byteLength); recycled = undefined; new Uint8Array(buffer).set(bytes); }
      return new Promise<{ rows: string; verification: string } | undefined>((resolve, reject) => { pending.set(id, { resolve, reject }); worker.postMessage({ id, kind, expected, buffer }, buffer ? [buffer] : []); });
    },
    close() { worker.terminate(); for (const task of pending.values()) task.reject(new Error('EXPORT_CANCELLED')); pending.clear(); },
  };
}
/** Sequential ack/write gives one in-flight application chunk (within the approved max four). */
export async function exportStream(response: Response, expected: Omit<ExportExpected, 'rows'>, signal: AbortSignal, sink?: FileSink): Promise<ExportResult> {
  try {
  const rowCount = response.headers.get('X-Export-Row-Count') ?? '';
  if (!response.ok || !response.body || response.headers.get('Cache-Control')?.includes('no-store') !== true || response.headers.get('X-Export-Schema-Version') !== '1' || response.headers.get('X-TokenScope-Instance-Id') !== expected.scope.service_instance_id || response.headers.get('X-Export-Run-Id') !== expected.scope.run_id) throw new Error('EXPORT_HEADERS_INVALID');
  if (!response.headers.get('Content-Disposition') || !response.headers.get('Content-Type')?.includes(expected.format === 'csv' ? 'text/csv' : 'application/x-ndjson') || (expected.format === 'csv' && response.headers.get('X-CSV-Text-Escaping') !== 'apostrophe')) throw new Error('EXPORT_HEADERS_INVALID');
  const validator = workerValidator();
  let byob: ReadableStreamBYOBReader | undefined;
  try { byob = response.body.getReader({ mode: 'byob' }); } catch { /* Older engines expose only a default reader. */ }
  const reader = byob ?? response.body.getReader();
  let readBuffer: ArrayBuffer = new ArrayBuffer(MAX_CHUNK_BYTES);
  const chunks: Uint8Array<ArrayBuffer>[] = []; let bytes = 0;
  const cancel = () => { void reader.cancel().catch(() => {}); validator.close(); };
  signal.addEventListener('abort', cancel, { once: true });
  try {
    if (signal.aborted) throw new Error('EXPORT_CANCELLED');
    await validator.send('init', { ...expected, rows: rowCount });
    while (true) {
      if (signal.aborted) throw new Error('EXPORT_CANCELLED');
      const item = byob ? await byob.read(new Uint8Array(readBuffer)) : await (reader as ReadableStreamDefaultReader<Uint8Array>).read(); if (item.done) break;
      if (byob) readBuffer = item.value.buffer as ArrayBuffer;
      for (let start = 0; start < item.value.byteLength; start += MAX_CHUNK_BYTES) {
        const chunk = item.value.subarray(start, Math.min(start + MAX_CHUNK_BYTES, item.value.byteLength)); bytes += chunk.byteLength;
        if (!sink && bytes > FALLBACK_BYTES) throw new Error('FALLBACK_EXCEEDS_16MIB');
        await validator.send('chunk', undefined, chunk);
        if (signal.aborted) throw new Error('EXPORT_CANCELLED');
        if (sink) await sink.write(chunk); else chunks.push(chunk.slice());
      }
    }
    if (signal.aborted) throw new Error('EXPORT_CANCELLED');
    const result = await validator.send('finish');
    if (!result) throw new Error('EXPORT_NO_VALIDATION_RESULT');
    if (signal.aborted) throw new Error('EXPORT_CANCELLED');
    if (sink) await sink.close();
    return { ...result, bytes, maxInflight: 1, saved: !!sink, ...(!sink ? { blob: new Blob(chunks, { type: expected.format === 'csv' ? 'text/csv;charset=utf-8' : 'application/x-ndjson' }) } : {}) };
  } catch (error) { await reader.cancel().catch(() => {}); throw error; }
  finally { signal.removeEventListener('abort', cancel); reader.releaseLock(); validator.close(); }
  } catch (error) {
    // Header/init failures also own the unread HTTP body; release it explicitly.
    if (response.body && !response.body.locked) await response.body.cancel().catch(() => {});
    if (sink) await sink.abort().catch(() => {});
    throw error;
  }
}
interface SaveHandle { createWritable(): Promise<FileSink> }
export async function beginExport(url: string, filename: string, expected: Omit<ExportExpected, 'rows'>, signal: AbortSignal, fetcher: typeof fetch = fetch): Promise<ExportResult> {
  if (active) throw new Error('EXPORT_ALREADY_ACTIVE'); active = true;
  let sink: FileSink | undefined; let handedOff = false;
  try {
    const picker = (window as Window & { showSaveFilePicker?: (options: { suggestedName: string }) => Promise<SaveHandle> }).showSaveFilePicker;
    if (window.isSecureContext && picker) {
      const handlePromise = picker.call(window, { suggestedName: filename }); // before network await, preserving activation
      const handle = await handlePromise;
      signal.throwIfAborted();
      if (typeof handle.createWritable !== 'function') throw new Error('FILE_WRITE_UNAVAILABLE');
      sink = await handle.createWritable();
    }
    signal.throwIfAborted();
    const response = await fetcher(url, { signal, credentials: 'same-origin', redirect: 'error', cache: 'no-store', headers: { 'X-TokenScope-Instance-Id': expected.scope.service_instance_id } });
    handedOff = true;
    const result = await exportStream(response, expected, signal, sink);
    signal.throwIfAborted();
    if (result.blob) { const objectUrl = URL.createObjectURL(result.blob), link = document.createElement('a'); link.href = objectUrl; link.download = filename; link.click(); setTimeout(() => URL.revokeObjectURL(objectUrl), 1000); }
    return result;
  } catch (error) { if (sink && !handedOff) await sink.abort().catch(() => {}); throw error; }
  finally { active = false; }
}

import { ExportValidator } from '../domain/export-protocol';
import type { ExportExpected } from '../domain/export-protocol';
let validator: ExportValidator | undefined;
self.onmessage = async (event: MessageEvent<{ id: number; kind: 'init' | 'chunk' | 'finish'; expected?: ExportExpected; buffer?: ArrayBuffer }>) => {
  const { id, kind } = event.data;
  try {
    if (kind === 'init') validator = new ExportValidator(event.data.expected!, event.data.expected!.format === 'ndjson' ? (await import('../api/validate')).validateDto : undefined);
    else if (kind === 'chunk') { if (!validator) throw new Error('NOT_INITIALIZED'); validator.push(new Uint8Array(event.data.buffer!)); }
    else { if (!validator) throw new Error('NOT_INITIALIZED'); self.postMessage({ id, result: validator.finish() }); return; }
    const buffer = event.data.buffer;
    (self as unknown as { postMessage(message: unknown, transfer: Transferable[]): void }).postMessage({ id, buffer }, buffer ? [buffer] : []);
  } catch (error) { self.postMessage({ id, error: error instanceof Error ? error.message : 'EXPORT_INVALID' }); }
};

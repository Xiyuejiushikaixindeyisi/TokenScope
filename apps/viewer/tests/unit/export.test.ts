// @vitest-environment node
import { readFileSync } from 'node:fs';
import { expect, it } from 'vitest';
import { validateDto } from '../../src/api/validate';
import { ExportValidator, MAX_RECORD_BYTES } from '../../src/domain/export-protocol';
import type { ExportExpected } from '../../src/domain/export-protocol';
const fixture = (name: string, format = 'ndjson') => readFileSync(new URL(`../../../../docs/contracts/examples/monitoring-view-v0.2/${name}.${format}`, import.meta.url));
function expected(name = 'normal', format: 'ndjson' | 'csv' = 'ndjson'): ExportExpected { const m = JSON.parse(fixture(name).toString().split('\n')[0]!); return { scope: m, format, filter: m.filter, sort: m.sort, rows: m.expected_rows }; }
function verify(bytes: Uint8Array, e = expected(), width = 64 * 1024) { const validator = new ExportValidator(e, validateDto); for (let i = 0; i < bytes.length; i += width) validator.push(bytes.subarray(i, i + width)); return validator.finish(); }
for (const format of ['ndjson', 'csv'] as const) for (const name of ['normal', 'empty']) it(`${name} ${format} every single-byte boundary including UTF8/quotes/CRLF`, () => { expect(verify(fixture(name, format), expected(name, format), 1).rows).toBe(expected(name).rows); });
it('all two-way chunk splits preserve NDJSON raw-byte digest', () => { const bytes = fixture('normal'); for (let i = 1; i < bytes.length; i++) { const v = new ExportValidator(expected(), validateDto); v.push(bytes.subarray(0, i)); v.push(bytes.subarray(i)); expect(v.finish().rows).toBe('4'); } });
for (const [name, mutate] of Object.entries({ missing_summary: (s: string) => s.slice(0, s.lastIndexOf('{"actual_rows"')), truncated: (s: string) => s.slice(0, -1), extra: (s: string) => s + '\n', digest: (s: string) => s.replace('e836c082', 'a836c082'), wrong_count: (s: string) => s.replace('"actual_rows":"4"', '"actual_rows":"3"'), wrong_run: (s: string) => s.replace('22222222-2222-4222-8222-222222222222', '33333333-3333-4333-8333-333333333333') })) it(`rejects ${name}`, () => { expect(() => verify(new TextEncoder().encode(mutate(fixture('normal').toString())))).toThrow(); });
it('rejects invalid UTF8 and oversized record/chunk', () => { const invalid = Uint8Array.from(fixture('normal')); invalid[4] = 255; expect(() => verify(invalid)).toThrow(); const long = new Uint8Array(MAX_RECORD_BYTES + 1).fill(32); expect(() => verify(long)).toThrow('RECORD_EXCEEDS_1MIB'); expect(() => new ExportValidator(expected(), validateDto).push(long)).toThrow('CHUNK_LIMIT_EXCEEDED'); });
it('rejects CSV truncation, bad escaping, wrong columns and header', () => { const data = fixture('normal', 'csv').toString(); for (const s of [data.slice(0, -1), data.replace('service_instance_id', 'wrong'), data.replace(',view_schema_version', ''), data.replaceAll('\r\n', '\n')]) expect(() => verify(new TextEncoder().encode(s), expected('normal', 'csv'), 1)).toThrow(); });
it('rejects filter and sort identity drift', () => { const e = expected(); e.filter = { ...e.filter, lower: '1' }; expect(() => verify(fixture('normal'), e)).toThrow('FILTER'); const s = expected(); s.sort = { ...s.sort, order: 'asc' }; expect(() => verify(fixture('normal'), s)).toThrow('SORT'); });


it('invalid export headers cancel unread HTTP body and abort the file before worker creation', async () => {
  const { exportStream } = await import('../../src/features/exports/export-controller');
  let cancelled = 0, aborted = 0, closed = 0;
  const response = new Response(new ReadableStream({ cancel() { cancelled++; } }));
  await expect(exportStream(response, expected(), new AbortController().signal, {
    async write() { throw new Error('must not write'); },
    async close() { closed++; }, async abort() { aborted++; },
  })).rejects.toThrow('EXPORT_HEADERS_INVALID');
  expect({ cancelled, aborted, closed }).toEqual({ cancelled: 1, aborted: 1, closed: 0 });
});

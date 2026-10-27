import { sha256 } from '@noble/hashes/sha2.js';
import type { DtoName } from '../api/types';
import { assertScope } from './identity';
import type { Dto } from '../api/types';
import type { Scope } from './identity';
export const MAX_RECORD_BYTES = 1024 * 1024;
export const MAX_CHUNK_BYTES = 64 * 1024;
export const FALLBACK_BYTES = 16 * 1024 * 1024;
export interface ExportExpected {
  format: 'ndjson' | 'csv'; scope: Scope; rows: string;
  filter: Dto<'LengthFilter'>; sort: Dto<'RequestSort'>;
}
export const CSV_HEADER = 'service_instance_id,view_schema_version,run_id,model_id,appid,settings_sha256,source_record_index,hash_id,time_utc,json_tokens,prompt_tokens,ideal_cached_input_tokens,ideal_compute_input_tokens,completion_tokens';
export class ExportValidator {
  private readonly buffer = new Uint8Array(MAX_RECORD_BYTES);
  private used = 0;
  private readonly hash = sha256.create();
  private phase: 'start' | 'requests' | 'summary' = 'start';
  private count = 0n;
  private quoted = false; private afterQuote = false; private fieldStart = true; private cr = false;
  private finished = false;
  private csvColumns = 1;
  private readonly csvPrefix: string;
  private readonly decoder = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });
  constructor(private readonly expected: ExportExpected, private readonly validate?: <K extends DtoName>(name: K, value: unknown) => Dto<K>) { const encode = (s: string) => /[\",\r\n]/.test(s) ? '"' + s.replaceAll('"', '""') + '"' : s; const app = expected.scope.appid ?? ''; this.csvPrefix = [expected.scope.service_instance_id, '1', expected.scope.run_id ?? '', expected.scope.model_id ?? '', /^[=+\-@\t\r\n]/.test(app) ? "'" + app : app].map(encode).join(',') + ','; if (!/^(0|[1-9][0-9]*)$(?![\s\S])/.test(expected.rows)) throw new Error('INVALID_EXPECTED_ROWS'); }
  push(chunk: Uint8Array) {
    if (this.finished) throw new Error('ALREADY_FINISHED');
    if (chunk.byteLength > MAX_CHUNK_BYTES) throw new Error('CHUNK_LIMIT_EXCEEDED');
    for (const byte of chunk) {
      if (this.phase === 'summary') throw new Error('BYTES_AFTER_SUMMARY');
      if (this.used === MAX_RECORD_BYTES) throw new Error('RECORD_EXCEEDS_1MIB');
      this.buffer[this.used++] = byte;
      if (this.expected.format === 'ndjson') { if (byte === 10) this.jsonLine(); continue; }
      if (this.cr) { if (byte !== 10) throw new Error('CSV_EXPECTED_LF'); this.csvLine(); continue; }
      if (this.quoted) { if (byte === 34) { this.quoted = false; this.afterQuote = true; } continue; }
      if (this.afterQuote) {
        if (byte === 34) { this.quoted = true; this.afterQuote = false; continue; }
        if (byte !== 44 && byte !== 13) throw new Error('CSV_AFTER_QUOTE');
        this.afterQuote = false;
      } else if (byte === 34) { if (!this.fieldStart) throw new Error('CSV_UNEXPECTED_QUOTE'); this.quoted = true; this.fieldStart = false; continue; }
      if (byte === 44) this.csvColumns++;
      if (byte === 13) this.cr = true;
      else if (byte === 10) throw new Error('CSV_EXPECTED_CRLF');
      else this.fieldStart = byte === 44;
    }
  }
  private text(length: number) { return this.decoder.decode(this.buffer.subarray(0, length)); }
  private jsonLine() {
    if (this.used < 2 || this.buffer[this.used - 2] === 13) throw new Error('INVALID_NDJSON_LINE');
    if (!this.validate) throw new Error('JSON_VALIDATOR_REQUIRED');
    const value: unknown = JSON.parse(this.text(this.used - 1));
    if (this.phase === 'start') {
      const metadata = this.validate('ExportMetadata', value);
      assertScope({ ...metadata }, this.expected.scope);
      for (const key of Object.keys(this.expected.filter) as (keyof Dto<'LengthFilter'>)[]) if (metadata.filter[key] !== this.expected.filter[key]) throw new Error('FILTER_MISMATCH');
      for (const key of Object.keys(this.expected.sort) as (keyof Dto<'RequestSort'>)[]) if (metadata.sort[key] !== this.expected.sort[key]) throw new Error('SORT_MISMATCH');
      if (metadata.expected_rows !== this.expected.rows) throw new Error('HEADER_ROW_COUNT_MISMATCH');
      this.phase = 'requests';
    } else if ((value as { type?: unknown })?.type === 'request') {
      const row = this.validate('ExportRequest', value);
      if (row.request_ref.run_id !== this.expected.scope.run_id) throw new Error('REQUEST_RUN_MISMATCH');
      this.hash.update(this.buffer.subarray(0, this.used)); this.count++;
      if (this.count > BigInt(this.expected.rows)) throw new Error('TOO_MANY_RECORDS');
    } else {
      const summary = this.validate('ExportSummary', value);
      if (this.count.toString() !== summary.actual_rows || summary.actual_rows !== this.expected.rows) throw new Error('ROW_COUNT_MISMATCH');
      const hash = [...this.hash.digest()].map(b => b.toString(16).padStart(2, '0')).join('');
      if (hash !== summary.request_lines_sha256) throw new Error('REQUEST_SHA256_MISMATCH');
      this.phase = 'summary';
    }
    this.used = 0;
  }
  private csvLine() {
    const text = this.text(this.used - 2);
    if (this.phase === 'start') { if (text !== CSV_HEADER) throw new Error('CSV_HEADER_MISMATCH'); this.phase = 'requests'; }
    else if (text.startsWith(this.csvPrefix)) {
      if (this.csvColumns !== 14) throw new Error('CSV_COLUMN_COUNT');
      this.count++; if (this.count > BigInt(this.expected.rows)) throw new Error('TOO_MANY_RECORDS');
    } else {
      const fields: string[] = []; let columns = 0, begin = 0, quote = false;
      for (let i = 0; i <= text.length; i++) {
        const ch = text[i];
        if (ch === '"') { if (quote && text[i + 1] === '"') i++; else quote = !quote; }
        else if ((ch === ',' && !quote) || i === text.length) { columns++; if (columns <= 5) { let field = text.slice(begin, i); if (field.startsWith('"')) field = field.slice(1, -1).replaceAll('""', '"'); fields.push(field); } begin = i + 1; }
      }
      if (columns !== 14) throw new Error('CSV_COLUMN_COUNT');
      const scope = this.expected.scope;
      const safe = (value: string) => /^[=+\-@\t\r\n]/.test(value) ? "'" + value : value;
      if (fields[0] !== scope.service_instance_id || fields[1] !== '1' || fields[2] !== scope.run_id || fields[3] !== scope.model_id || fields[4] !== safe(scope.appid!)) throw new Error('CSV_SCOPE_MISMATCH');
      this.count++; if (this.count > BigInt(this.expected.rows)) throw new Error('TOO_MANY_RECORDS');
    }
    this.used = 0; this.csvColumns = 1; this.cr = false; this.fieldStart = true; this.afterQuote = false;
  }
  finish() {
    if (this.finished) throw new Error('ALREADY_FINISHED');
    this.finished = true;
    if (this.used !== 0 || this.quoted || this.cr || this.afterQuote) throw new Error('TRUNCATED_EXPORT');
    if (this.expected.format === 'ndjson' ? this.phase !== 'summary' : this.phase !== 'requests') throw new Error('INCOMPLETE_EXPORT');
    if (this.count.toString() !== this.expected.rows) throw new Error('ROW_COUNT_MISMATCH');
    return { rows: this.count.toString(), verification: this.expected.format === 'ndjson' ? 'sha256_and_count' : 'structure_and_count' };
  }
}

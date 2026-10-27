// @vitest-environment node
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { it, expect } from 'vitest';
import { validateDto, decodeJson } from '../../src/api/validate';
import type { DtoName } from '../../src/api/types';
const contracts = new URL('../../../../docs/contracts/', import.meta.url);
const read = (path: string): unknown => JSON.parse(readFileSync(new URL(path, contracts), 'utf8'));
const cases = read('examples/monitoring-view-s0/cases.json') as { cases: { name: string; schema: DtoName; path: string }[] };
for (const entry of cases.cases) {
  it(`S0 complete synthetic example: ${entry.name}`, () => {
    const value = read(entry.path);
    expect(validateDto(entry.schema, value)).toEqual(value);
  });
}
it('rejects unknown schema, undeclared fields and imprecise integers', () => {
  const base = read('examples/monitoring-view-s0/catalog-normal.json') as Record<string, unknown>;
  for (const patch of [{ view_schema_version: '2' }, { total: 1 }, { total: '1\n' }, { extra: true }, { limit: 1001 }, { limit: 0 }]) {
    expect(() => validateDto('CatalogResponse', { ...base, ...patch })).toThrow();
  }
});
it('rejects response from another instance or appid', () => {
  const value = read('examples/monitoring-view-s0/snapshot-normal.json');
  expect(() => validateDto('ViewSnapshot', value, { service_instance_id: 'other', view_schema_version: '1' })).toThrow('SCOPE_MISMATCH');
  expect(() => validateDto('ViewSnapshot', value, { service_instance_id: '11111111-1111-4111-8111-111111111111', view_schema_version: '1', appid: 'another-app' })).toThrow('SCOPE_MISMATCH');
});
it('rejects malformed UTF8 and preserves Unicode text', () => {
  expect(() => decodeJson(new Uint8Array([0xff]))).toThrow();
  expect(decodeJson(new TextEncoder().encode('{"appid":"租户 🧪"}'))).toEqual({ appid: '租户 🧪' });
});
it('validates bin width and cursor shape', () => {
  const snapshot = validateDto('ViewSnapshot', read('examples/monitoring-view-s0/snapshot-normal.json'));
  const histogram = snapshot.distributions.prompt_tokens['5000'];
  expect(() => validateDto('Histogram', { ...histogram, bin_width: 4000 })).toThrow();
  const cat = read('examples/monitoring-view-s0/catalog-normal.json') as Record<string, unknown>;
  expect(() => validateDto('CatalogResponse', { ...cat, cursor: 'not-a-cursor' })).toThrow();
});
for (const name of ['normal', 'empty']) {
  it(`R2 ${name}: original request bytes match summary; not a browser export test`, () => {
    const bytes = readFileSync(new URL(`examples/monitoring-view-v0.2/${name}.ndjson`, contracts));
    const lines = bytes.toString('utf8').trimEnd().split('\n');
    const metadata = validateDto('ExportMetadata', JSON.parse(lines[0]!));
    const summary = validateDto('ExportSummary', JSON.parse(lines.at(-1)!));
    const requests = lines.slice(1, -1);
    for (const line of requests) validateDto('ExportRequest', JSON.parse(line));
    expect(summary.actual_rows).toBe(String(requests.length));
    expect(metadata.expected_rows).toBe(summary.actual_rows);
    expect(createHash('sha256').update(requests.map(line => line + '\n').join('')).digest('hex')).toBe(summary.request_lines_sha256);
  });
}

it('preserves opaque cursor and rejects cross-instance and malformed sequence', () => {
  const cat = read('examples/monitoring-view-s0/catalog-normal.json') as Record<string, unknown>;
  const instance = String(cat.service_instance_id);
  for (const seq of ['0', '18446744073709551615']) {
    const cursor = `${instance}:${seq}`;
    expect(validateDto('CatalogResponse', { ...cat, cursor }).cursor).toBe(cursor);
  }
  for (const cursor of [`${instance}:-1`, `${instance}:01`, `${instance}:1\n`, `${instance}:1.2`, '22222222-2222-4222-8222-222222222222:42']) {
    expect(() => validateDto('CatalogResponse', { ...cat, cursor })).toThrow();
  }
});

it('uses only declared scope fields when snapshot identity also contains publish_seq', () => {
  const snapshot = validateDto('ViewSnapshot', read('examples/monitoring-view-s0/snapshot-normal.json'));
  const requests = read('examples/monitoring-view-s0/requests-normal.json');
  expect(validateDto('RequestsPage', requests, snapshot.identity)).toEqual(requests);
});

import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { compile } from 'json-schema-to-typescript';
const root = new URL('../../../', import.meta.url);
const read = async path => JSON.parse(await readFile(new URL(path, root), 'utf8'));
const freeze = await read('docs/tasks/delivery/HV2_MA_FREEZE_20261103.json');
const identity = createHash('sha256').update(JSON.stringify(Object.fromEntries(Object.entries(freeze.files).sort(([a], [b]) => a.localeCompare(b))))).digest('hex');
if (identity !== '9b48fb244963ce153b009a9a2d0d9050d084bd6c1bb43eec27ddf49f313fd9fa') throw Error('MA freeze identity changed');
for (const [path, sha] of Object.entries(freeze.files)) {
  if (createHash('sha256').update(await readFile(new URL(path, root))).digest('hex') !== sha) throw Error(`MA freeze drift: ${path}`);
}
const folder = 'docs/tasks/monitoring/v2-ma/hv2-availability/';
const schema = await read(folder + 'schema.json'), openapi = await read(folder + 'candidate.openapi.json');
const path = '/monitoring/ma/runs/{ma_run_id}/instances/{instance_uuid}/availability';
const operation = openapi.paths[path].get, components = {};
function visit(value) {
  if (!value || typeof value !== 'object') return;
  if (typeof value.$ref === 'string' && value.$ref.startsWith('#/components/schemas/')) {
    const name = value.$ref.split('/').at(-1);
    if (!(name in components)) { components[name] = openapi.components.schemas[name]; visit(components[name]); }
  }
  Object.values(value).forEach(visit);
}
visit(operation);
const dir = new URL('../src/api/v2/generated/ma/', import.meta.url);
await writeFile(new URL('AvailabilityResponse.json', dir), JSON.stringify(schema));
await writeFile(new URL('AvailabilityResponse.ts', dir), await compile(schema, 'AvailabilityResponse', { bannerComment: '/* Generated from independently frozen MA availability; do not edit. */' }));
await writeFile(new URL('availability.openapi.json', dir), JSON.stringify({ path, operation, components }));
console.log('Verified MA freeze and generated additive availability DTO/handshake; old schemas untouched.');

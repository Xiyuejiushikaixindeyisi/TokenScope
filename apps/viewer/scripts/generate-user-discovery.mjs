import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { compile } from 'json-schema-to-typescript';
const root = new URL('../../../', import.meta.url);
const read = async p => JSON.parse(await readFile(new URL(p, root), 'utf8'));
const freeze = await read('docs/tasks/delivery/HV2_USER_FREEZE_20261103.json');
const digest = v => createHash('sha256').update(v).digest('hex');
if (digest(JSON.stringify(Object.fromEntries(Object.entries(freeze.files).sort()))) !== '4d9e2e5d6c7031ff0aaa266114b92dbcb8684b9a80d722d2cfae9de8ad1d7dc0') throw Error('User freeze identity changed');
for (const [p, h] of Object.entries(freeze.files)) if (digest(await readFile(new URL(p, root))) !== h) throw Error(`Frozen file changed: ${p}`);
const folder = 'docs/contracts/user-monitoring-v2/2.1.0/';
const raw = await read(folder + 'schema.json');
const dir = new URL('../src/api/v2/generated/user/', import.meta.url);
const schemas = {};
// json-schema-to-typescript consumes draft-07 tuple syntax. Runtime AJV keeps
// the original 2020-12 prefixItems schema byte-for-byte in hv2-schemas.json.
function typeSchema(value) {
  if (Array.isArray(value)) return value.map(typeSchema);
  if (!value || typeof value !== 'object') return value;
  const result = Object.fromEntries(Object.entries(value).map(([k, v]) => [k, typeSchema(v)]));
  if (result.prefixItems) { result.items = result.prefixItems; delete result.prefixItems; }
  return result;
}
for (const key of Object.keys(raw.$defs)) {
  const schema = { $defs: raw.$defs, $ref: `#/$defs/${key}` };
  schemas[key] = schema;
  // Separate prefix preserves the original 2.0.0 generated contracts.
  await writeFile(new URL(`HV2${key}.ts`, dir), await compile(typeSchema(schema), key, { bannerComment: '/* Generated from frozen user 2.1.0; do not edit. */' }));
}
await writeFile(new URL('hv2-schemas.json', dir), JSON.stringify(schemas));
await writeFile(new URL('hv2.openapi.json', dir), JSON.stringify(await read(folder + 'runtime.openapi.json')));
await writeFile(new URL('legacy.openapi.json', dir), JSON.stringify(await read('docs/contracts/user-monitoring-v2/2.0.0/runtime.openapi.json')));
console.log('Verified user freeze; generated additive 2.1.0 DTOs and both handshake contracts.');

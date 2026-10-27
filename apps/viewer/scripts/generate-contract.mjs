import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { compile } from 'json-schema-to-typescript';
const root = new URL('../../../', import.meta.url);
const manifestBytes = await readFile(new URL('docs/tasks/monitoring/batches/B005.1/S0_MANIFEST.json', root));
const manifest = JSON.parse(manifestBytes);
for (const entry of manifest.files) {
  const bytes = await readFile(new URL(entry.path, root));
  if (createHash('sha256').update(bytes).digest('hex') !== entry.sha256) throw new Error(`S0 digest mismatch: ${entry.path}`);
}
const schemaBytes = await readFile(new URL('docs/contracts/schemas/monitoring-view-v1.schema.json', root));
const schema = JSON.parse(schemaBytes);
const names = Object.keys(schema.$defs);
const dir = new URL('../src/api/generated/', import.meta.url);
await mkdir(dir, { recursive: true });
const types = await compile({ ...schema, title: 'ContractTypes', type: 'object', properties: Object.fromEntries(names.map(name => [name, { $ref: `#/$defs/${name}` }])), required: names, additionalProperties: false }, 'ContractTypes', { bannerComment: '/* Generated from S0 1.0.0. Do not edit; npm run generate. */', unreachableDefinitions: true });
await writeFile(new URL('types.ts', dir), types);
await writeFile(new URL('schema.json', dir), schemaBytes);
await writeFile(new URL('../contract-lock.json', dir), JSON.stringify({ contract_version: manifest.contract_version, runtime_implemented: false, manifest_sha256: createHash('sha256').update(manifestBytes).digest('hex'), definitions: names, inputs: manifest.files }, null, 2) + '\n');
console.log(`Generated ${names.length} DTO definitions from verified S0 ${manifest.contract_version}`);

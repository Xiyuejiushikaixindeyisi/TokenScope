import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const root = new URL('../../../', import.meta.url);
const hash = b => createHash('sha256').update(b).digest('hex');
const identities = {
  COMMON: '9ac3e7fd5c5fea9556f957871bb03a0791e79e9404b207462a1cf8e184d7cb8e',
  USER: '4d9e2e5d6c7031ff0aaa266114b92dbcb8684b9a80d722d2cfae9de8ad1d7dc0',
  TOKEN: '14419e5bba5af85a3ffa20d6330b3fa29c2d926bd81ef1f3462e30b118b4f00d',
  LOW_HIT: '10f643bc56fa59936dcfd7d17f4aabf1163aba4d479c47662366d13c879e011b',
};
const files = {};
for (const [name, identity] of Object.entries(identities)) {
  const freeze = JSON.parse(await readFile(new URL(`docs/tasks/delivery/HV2_${name}_FREEZE_20261103.json`, root)));
  if (freeze.identity !== identity || hash(JSON.stringify(Object.fromEntries(Object.entries(freeze.files).sort()))) !== identity) throw Error(`Freeze identity changed: ${name}`);
  Object.assign(files, freeze.files); // The accepted private second gate supersedes initial adapters.
}
for (const [p, expected] of Object.entries(files)) if (hash(await readFile(new URL(p, root))) !== expected) throw Error(`Frozen dependency changed: ${p}`);
const dir = new URL('../src/api/analysis/generated/', import.meta.url);
const resources = {};
for (const [source, target] of [['wire.json', 'diagnostics-execution-2.json'], ['examples.json', 'diagnostics-execution-2.examples.json']]) {
  const bytes = await readFile(new URL(`docs/contracts/diagnostics-execution-2/${source}`, root));
  await writeFile(new URL(target, dir), bytes);
  resources[target] = hash(bytes);
}
await writeFile(new URL('../src/api/analysis/execution-2-lock.json', import.meta.url), JSON.stringify({ identities, resources }, null, 2) + '\n');
console.log(`Verified ${Object.keys(files).length} frozen dependencies; generated additive diagnostics v2 resources.`);

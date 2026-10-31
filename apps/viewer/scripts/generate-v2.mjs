import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { compile } from 'json-schema-to-typescript';
const root = new URL('../../../', import.meta.url);
for (const [name, folder] of [['user','docs/contracts/user-monitoring-v2/2.0.0/'], ['ma','docs/contracts/ma-monitoring-v2/']]) {
  const manifest = JSON.parse(await readFile(new URL(folder+'manifest.json',root),'utf8'));
  for (const [file, expected] of Object.entries(manifest)) {
    const bytes = await readFile(new URL(file.startsWith('docs/') || file.startsWith('src/') ? file : folder+file,root));
    if (createHash('sha256').update(bytes).digest('hex')!==expected) throw Error(`Digest mismatch: ${file}`);
  }
  const raw = JSON.parse(await readFile(new URL(folder+'schema.json',root),'utf8'));
  // MA ships six self-contained schemas, each with its own local definitions.
  const schemas = name==='user' ? Object.fromEntries(Object.keys(raw.$defs).map(k=>[k,{$defs:raw.$defs,$ref:`#/$defs/${k}`}])) : raw;
  const dir = new URL(`../src/api/v2/generated/${name}/`,import.meta.url); await mkdir(dir,{recursive:true});
  let text='/* Generated from verified backend contract; do not edit. */\n';
  for(const [key,value] of Object.entries(schemas)) {
    await writeFile(new URL(key+'.json',dir),JSON.stringify(value));
    // A separate module prevents colliding nested definition names across MA schemas.
    await writeFile(new URL(key+'.ts',dir),await compile(value,key,{bannerComment:'/* Generated contract. */'}));
    text+=`export type { ${key} } from './${key}';\n`;
  }
  await writeFile(new URL('index.ts',dir),text);
  await writeFile(new URL('schemas.json',dir),JSON.stringify(schemas));
  await writeFile(new URL('manifest.json',dir),JSON.stringify(manifest,null,2)+'\n');
}

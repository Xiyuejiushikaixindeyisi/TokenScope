import { readFile, readdir } from 'node:fs/promises';
import assert from 'node:assert/strict';
const dist = new URL('../dist/', import.meta.url);
const html = await readFile(new URL('index.html', dist), 'utf8');
const refs = [...html.matchAll(/(?:src|href)="([^"]+)"/g)].map(match => match[1]);
assert(refs.length >= 2);
for (const ref of refs) {
  assert(!/^(?:[a-z]+:)?\/\//i.test(ref), `Remote asset: ${ref}`);
  await readFile(new URL(ref, dist));
}
for (const file of await readdir(new URL('assets/', dist))) {
  if (!file.endsWith('.css')) continue;
  const css = await readFile(new URL(`assets/${file}`, dist), 'utf8');
  assert(!/@import|url\(\s*['"]?(?:https?:)?\/\//i.test(css), 'External stylesheet/font');
}
console.log('Build asset references are local; no remote CSS/fonts. Browser network check is separate.');

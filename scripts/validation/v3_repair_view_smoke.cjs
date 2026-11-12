// Browser presentation smoke only. Uses recorded API fixtures; not E2E replay evidence.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('../../apps/viewer/node_modules/playwright');
const root = process.cwd();
const run = path.join(root, process.argv[2]);
const dist = path.join(root, process.argv[3]);
fs.mkdirSync(run, { recursive: false });
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const wire = read('apps/viewer/src/api/analysis/generated/diagnostics-execution-2.json');
const schemas = read('apps/viewer/src/api/analysis/generated/diagnostics-report-3.json');
const sampling = read('apps/viewer/src/api/analysis/generated/diagnostics-sampling-3.json');
const report = read('apps/viewer/tests/fixtures/sample-v3/positive.json');
const cat = read('apps/viewer/src/api/analysis/generated/diagnostics-execution-2.examples.json').catalog;
cat.items = []; cat.defaults = []; cat.selected_reports = []; cat.next_after = null;
const instance = cat.service_instance_id;
const task = report.task_id;
const scope = report.sample.parent_scope;
const errors = [], calls = [];
(async () => {
 const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
 const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
 page.on('pageerror', e => errors.push(String(e)));
 await page.route('http://repair.test/**', async route => {
  const req = route.request(), url = new URL(req.url()), p = url.pathname;
  calls.push({ method: req.method(), path: p });
  if (req.method() !== 'GET') throw Error('Unexpected analysis write');
  let value;
  if (p === '/diagnostics/capabilities') value = { contract_version: 'analysis-common-1.0', http_version: 'diagnostics-http-1', service_instance_id: instance };
  else if (p === '/diagnostics/discovery/capabilities') value = { version: 'diagnostics-discovery-1', service_instance_id: instance };
  else if (p === '/diagnostics/v2/capabilities') value = { service_instance_id: instance, version: 'diagnostics-execution-2', discovery_version: 'diagnostics-discovery-2', directions: [], execution_enabled: false, minimum_selected_directions: '1', legacy_read_compatible: true, submission_url: '/diagnostics/v2/tasks', catalog_url: '/diagnostics/v2/catalog', partial_policy: 'ready_preferred_published_partial_fallback', budget_semantics: 'direction_isolated_compute_rule_reserved_retention', schemas: wire };
  else if (p === '/diagnostics/v3/capabilities') value = { service_instance_id: instance, schemas: { report: schemas.SampleReport3, execution: schemas.Execution3, receipt: sampling.receipt } };
  else if (p === '/diagnostics/v2/catalog') value = cat;
  else if (p === '/diagnostics/v3/tasks') value = { service_instance_id: instance, next_offset: null, items: [{ execution: { task_id: task, state: 'completed', checkpoints: [{ kind: 'report', sha256: 'a'.repeat(64) }] }, source: { source_kind: 'base', base_run_id: scope.source.base_run_id, appid: scope.appid }, sample_metadata: { sample_id: report.sample_id, manifest_sha256: report.manifest_sha256, scope, selected_count: String(report.sample.decision.windows.reduce((n,w)=>n+w.members.length,0)) } }] };
  else if (p.endsWith('/report')) value = report;
  else if (p === '/diagnostics/discovery/events') return route.fulfill({ contentType: 'text/event-stream', body: ': fixture\n\n' });
  else if (p === '/' || p.startsWith('/assets/')) {
   const file = path.join(dist, p === '/' ? 'index.html' : p.slice(1));
   return route.fulfill({ contentType: p.endsWith('.js') ? 'text/javascript' : p.endsWith('.css') ? 'text/css' : 'text/html', body: fs.readFileSync(file) });
  } else return route.fulfill({ status: 404, contentType: 'application/json', body: '{}' });
  return route.fulfill({ contentType: 'application/json', body: JSON.stringify(value) });
 });
 try {
  await page.goto('http://repair.test/#/analysis');
  await page.getByRole('heading', { name: '固定 session_clock，稳定公共前缀' }).waitFor();
  if (await page.locator('.sample-diagnostics').count()) throw Error('Parallel module remains');
  await page.screenshot({ path: path.join(run, 'desktop.png'), fullPage: true });
  await page.getByRole('button', { name: /查看证据与改法/ }).first().click();
  await page.getByRole('heading', { name: '局部证据与具体改法' }).waitFor();
  await page.screenshot({ path: path.join(run, 'detail.png'), fullPage: true });
  await page.getByRole('button', { name: /返回卡片列表/ }).click();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: path.join(run, 'mobile.png'), fullPage: true });
  if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw Error('Horizontal overflow');
  if (errors.length) throw Error(errors.join('\n'));
  fs.writeFileSync(path.join(run, 'PASS.json'), JSON.stringify({ mock_api: true, actual_replay: false, calls, errors }, null, 2), { flag: 'wx' });
 } catch (e) {
  fs.writeFileSync(path.join(run, 'FAIL.json'), JSON.stringify({ error: String(e), errors, calls, text: await page.locator('body').innerText() }, null, 2), { flag: 'wx' }); throw e;
 } finally { await browser.close(); }
})();

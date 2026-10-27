import { test, expect, chromium } from '@playwright/test';
import { execFileSync } from 'node:child_process';
const stress: { rows: number; delta: number }[] = [];
for (const rows of [262144, 1048576]) for (const repeat of [1, 2, 3]) test(`real Worker + OPFS ${rows / 1024}MiB repeat ${repeat}`, async ({}, info) => {
  test.skip(process.platform !== 'win32', 'Whole-browser RSS collector is Windows-specific; do not claim memory acceptance on an unmeasured platform');
  test.setTimeout(180000);
  const context = await chromium.launchPersistentContext('', { executablePath: process.env.TOKENSCOPE_BROWSER_EXECUTABLE!, headless: true, baseURL: process.env.TOKENSCOPE_TEST_BASE_URL ?? 'http://127.0.0.1:4173' });
  const page = context.pages()[0]!, browser = context.browser()!;
  try {
  await page.goto('/tests/harness/export.html'); await page.waitForFunction(() => (window as unknown as { exportReady: boolean }).exportReady);
  type Options = { rows: number; rowSize?: number; targetBytes?: number; fallback?: boolean; bad?: boolean; cancelAt?: number; failAt?: number; slow?: boolean; begin?: boolean };
  const run = (options: Options) => page.evaluate(async o => (window as unknown as { runExport(o: Options): Promise<Record<string, unknown>> }).runExport(o), options);
  const warm = await run({ rows: 64 }); expect(warm.closed).toBe(1);
  const cdp = await browser.newBrowserCDPSession();
  const ids = ((await cdp.send('SystemInfo.getProcessInfo')).processInfo as { id: number; type: string }[]).map(p => p.id);
  const memory: { elapsedMs: number; rssBytes: number; processes: unknown }[] = []; const start = Date.now();
  const sample = () => { if (process.platform !== 'win32') return; const text = execFileSync('powershell.exe', ['-NoProfile', '-Command', `Get-Process -Id ${ids.join(',')} -ErrorAction SilentlyContinue | Select-Object Id,WorkingSet64,PrivateMemorySize64 | ConvertTo-Json -Compress`], { encoding: 'utf8', windowsHide: true }); const processes = JSON.parse(text) as { WorkingSet64: number }[]; memory.push({ elapsedMs: Date.now() - start, rssBytes: processes.reduce((n,p) => n + p.WorkingSet64, 0), processes }); };
  sample(); const timer = setInterval(sample, 1000);
  let large; try { large = await run({ rows, slow: false, begin: true }); } finally { clearInterval(timer); sample(); }
  expect(large.error).toBeUndefined(); expect(large.bytes).toBeGreaterThanOrEqual(256 * 1024 * 1024); expect(large.fileSize).toBe(large.bytes); expect(large.closed).toBe(1); expect(large.aborted).toBe(0); expect(large.maxWrites).toBe(1); expect(large.concurrency).toContain('EXPORT_ALREADY_ACTIVE');
  const delta = Math.max(...memory.map(m => m.rssBytes)) - memory[0]!.rssBytes;
  await info.attach('export-memory', { body: JSON.stringify({ methodology: 'Windows WorkingSet64 summed over this isolated browser SystemInfo process IDs; warm 64 records before baseline; 1s samples, main+renderer+utility/GPU; no forced GC. Persistent browser profile avoids incognito memory-only OPFS; OPFS is real disk-backed writable; file picker is stubbed.', ids, memory, peakDeltaBytes: delta, large }), contentType: 'application/json' });
  stress.push({ rows, delta }); expect(delta).toBeLessThanOrEqual(256 * 1024 * 1024);
  const slow = await run({ rows: 256, slow: true }); expect(slow.maxWrites).toBe(1); expect(slow.closed).toBe(1);
  for (const options of [{ rows: 256, cancelAt: 2 }, { rows: 256, failAt: 2 }, { rows: 64, bad: true }]) { const result = await run(options); expect(result.error).toBeTruthy(); expect(result.closed).toBe(0); expect(result.aborted).toBe(1); }
  // Header is 209 bytes; use exact dynamically observed size to hit decoded-byte boundary.
  const small = await run({ rows: 0, fallback: true }); const header = Number(small.bytes);
  const below = await run({ rows: 16383, fallback: true }); expect(below.error).toBeUndefined(); expect(below.blobSize).toBe(16383 * 1024 + header);
  const exact = await run({ rows: 16384, targetBytes: 16 * 1024 * 1024, fallback: true }); expect(exact.blobSize).toBe(16 * 1024 * 1024);
  const oneOver = await run({ rows: 16384, targetBytes: 16 * 1024 * 1024 + 1, fallback: true }); expect(oneOver.error).toContain('FALLBACK_EXCEEDS_16MIB');
  const above = await run({ rows: 16384, fallback: true }); expect(above.error).toContain('FALLBACK_EXCEEDS_16MIB'); expect(above.closed).toBe(0);
  const badFallback = await run({ rows: 1, fallback: true, bad: true }); expect(badFallback.error).toContain('TRUNCATED');
  const oversized = await run({ rows: 1, rowSize: 1024 * 1024 + 1 }); expect(oversized.error).toContain('RECORD_EXCEEDS_1MIB'); expect(oversized.closed).toBe(0);
  } finally { await context.close(); }
});

test.afterAll(() => { const median = (rows: number) => stress.filter(x => x.rows === rows).map(x => x.delta).sort((a,b) => a-b)[1]!; if (stress.length === 6) expect(median(1048576)).toBeLessThan(3 * Math.max(32 * 1024 * 1024, median(262144))); });

import { readFileSync } from 'node:fs';
import { test, expect } from '@playwright/test';
test('real Worker exact bytes: NDJSON SHA/summary, CSV quotes/UTF8, and network abort', async ({ page }) => {
  await page.goto('/tests/harness/export.html'); await page.waitForFunction(() => 'verifyFixture' in window);
  const load = (name: string, format: string) => readFileSync(new URL(`../../../../docs/contracts/examples/monitoring-view-v0.2/${name}.${format}`, import.meta.url));
  for (const name of ['normal', 'empty']) for (const format of ['ndjson', 'csv'] as const) {
    const data = load(name, format), metadata = JSON.parse(load(name, 'ndjson').toString().split('\n')[0]!);
    const run = (bytes: number[], broken = false) => page.evaluate(async arg => (window as unknown as { verifyFixture(...args: unknown[]): Promise<Record<string, unknown>> }).verifyFixture(arg.bytes, arg.metadata, arg.format, arg.broken), { bytes, metadata, format, broken });
    const valid = await run([...data]); expect(valid.error).toBeUndefined(); expect(valid.closed).toBe(1); expect(valid.bytesEqual).toBe(true);
    const bad = await run([...data.subarray(0, -1)]); expect(bad.closed).toBe(0); expect(bad.aborted).toBe(1);
    const disconnected = await run([...data], true); expect(disconnected.closed).toBe(0); expect(disconnected.aborted).toBe(1);
    if (format === 'ndjson') { const changed = data.toString().replace('request_lines_sha256":"', 'request_lines_sha256":"f'); const badSha = await run([...Buffer.from(changed)]); expect(badSha.closed).toBe(0); expect(badSha.aborted).toBe(1); }
  }
});

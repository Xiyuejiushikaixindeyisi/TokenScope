import { defineConfig } from '@playwright/test';
const executablePath = process.env.TOKENSCOPE_BROWSER_EXECUTABLE;
export default defineConfig({
  testDir: './tests/browser', fullyParallel: false, retries: 0,
  use: { baseURL: process.env.TOKENSCOPE_TEST_BASE_URL ?? 'http://127.0.0.1:4173', browserName: 'chromium',
    ...(executablePath ? { launchOptions: { executablePath } } : { channel: 'chromium' }),
    trace: 'retain-on-failure' },
  ...(process.env.TOKENSCOPE_EXTERNAL_PREVIEW === '1' ? {} : {
    // Harness pages import the actual source modules; production-build validation uses an explicit preview URL.
    webServer: { command: 'npm run dev -- --port 4173 --strictPort', url: 'http://127.0.0.1:4173', reuseExistingServer: false },
  }),
});

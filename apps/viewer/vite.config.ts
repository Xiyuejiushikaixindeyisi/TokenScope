import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
const target = process.env.TOKENSCOPE_BACKEND_URL ?? 'http://127.0.0.1:8000';
export default defineConfig({
  plugins: [react()],
  base: './',
  server: { proxy: Object.fromEntries(['/openapi.json', '/models', '/monitoring', '/analysis-runs', '/analysis-submissions'].map(path => [path, { target }])) },
  build: { target: 'es2022' },
  test: { environment: 'jsdom', include: ['tests/unit/**/*.test.ts', 'tests/component/**/*.test.tsx'], setupFiles: ['tests/setup.ts'] },
});

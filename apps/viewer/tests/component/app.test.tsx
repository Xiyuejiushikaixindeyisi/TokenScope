import { render, screen, act } from '@testing-library/react';
import { it, expect, vi, afterEach } from 'vitest';
import { App } from '../../src/app';
afterEach(() => vi.unstubAllGlobals());
it('hash navigation changes page without fake metrics', () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('synthetic offline')));
  window.location.hash = '#/overview';
  render(<App />);
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('监控概览');
  expect(screen.getByText('尚未接入监控数据')).toBeInTheDocument();
  act(() => { window.location.hash = '#/distributions'; window.dispatchEvent(new HashChangeEvent('hashchange')); });
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('请求长度分布');
  expect(screen.getByRole('link', { name: '请求长度分布' })).toHaveAttribute('aria-current', 'page');
});

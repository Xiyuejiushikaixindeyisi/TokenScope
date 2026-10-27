import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { render, screen, fireEvent } from '@testing-library/react';
import { it, expect, vi } from 'vitest';
import { Overview } from '../../src/features/overview/Overview';
import { Distributions } from '../../src/features/distributions/Distributions';
import { validateDto } from '../../src/api/validate';
const sample = (name = 'snapshot-normal') => validateDto('ViewSnapshot', JSON.parse(readFileSync(resolve(process.cwd(), '../../docs/contracts/examples/monitoring-view-s0', name + '.json'), 'utf8')));
it('shows authoritative totals and null rate without inventing zero', () => {
  const s = sample('snapshot-large-integer'); const { container } = render(<Overview snapshot={s} />);
  for (const value of Object.values(s.metrics.totals)) expect(container.textContent).toContain(BigInt(value).toLocaleString('zh-CN'));
});
it('null hit rate remains unavailable', () => { render(<Overview snapshot={sample('snapshot-null-rate')} />); expect(screen.getByText('理想命中率').closest('article')).toHaveTextContent('—'); });
it('highlights all backend mode indices and puts percentiles outside SVG', () => {
  const s = sample(); for (const key of ['json_tokens', 'prompt_tokens', 'ideal_compute_input_tokens'] as const) s.distributions[key]['5000'].summary.mode_bin_indices = ['0', '1'];
  const { container } = render(<Distributions snapshot={s} onSelect={vi.fn()} />);
  expect(container.querySelectorAll('rect[data-mode="true"]')).toHaveLength(6);
  for (const svg of container.querySelectorAll('svg')) expect(svg.textContent).not.toContain('P50');
  expect(screen.getAllByText(/P50/)).toHaveLength(3);
});
it('selects half-open ordinary and open overflow ranges via keyboard', () => {
  const select = vi.fn(); const { container } = render(<Distributions snapshot={sample()} onSelect={select} />);
  fireEvent.keyDown(container.querySelector('rect')!, { key: 'Enter' });
  expect(select).toHaveBeenLastCalledWith({ metric: 'json_tokens', lower: '0', upper: '5000' });
  fireEvent.click(screen.getAllByRole('button', { name: /≥200K Token/ })[0]!);
  expect(select).toHaveBeenLastCalledWith({ metric: 'json_tokens', lower: '200000', upper: null });
  fireEvent.change(screen.getByLabelText('分箱宽度'), { target: { value: '1000' } });
  expect(container.querySelectorAll('rect')).toHaveLength(603);
});

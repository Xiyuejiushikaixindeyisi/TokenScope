import cch from '../fixtures/sample-v3/repair-cch.json';
import timestamp from '../fixtures/sample-v3/repair-plain_timestamp.json';
import workspace from '../fixtures/sample-v3/repair-workspace.json';
import order from '../fixtures/sample-v3/repair-tool_order.json';
import description from '../fixtures/sample-v3/repair-tool_description.json';
import added from '../fixtures/sample-v3/repair-tool_added.json';
import representation from '../fixtures/sample-v3/repair-representation.json';
import schemas from "../../src/api/analysis/generated/diagnostics-report-3.json";
import sampling from "../../src/api/analysis/generated/diagnostics-sampling-3.json";
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import positive from '../fixtures/sample-v3/positive.json';
import zero from '../fixtures/sample-v3/zero.json';
import { SampleDiagnostics, SampleReport } from '../../src/features/analysis/SampleDiagnostics';
import { validateSampleReport } from '../../src/api/analysis/sample-v3';
import { arr, obj } from '../../src/api/analysis/client';

afterEach(() => { vi.unstubAllGlobals(); sessionStorage.clear(); });

it('renders real backend clock evidence, A/B rates, and zero without old full filter', () => {
  render(<SampleReport report={validateSampleReport(zero)}/>);
  expect(screen.getByRole('heading', { name: /固定化/ })).toBeInTheDocument();
  expect(screen.getAllByText(/实算无提升/)).toHaveLength(2);
  expect(screen.getAllByText(/参考提升率：0.00/)).toHaveLength(2);
  expect(screen.getByText('NORMALIZED')).toBeInTheDocument();
  expect(screen.getByText('/messages/0/content')).toBeInTheDocument();
  expect(screen.getByText(/改变模型的?时间感知/)).toBeInTheDocument();
});

it('checks recipe, independent window identity, denominators and exact rational gain', () => {
  expect(validateSampleReport(positive)).toBeTruthy();
  for (const fault of ['gain', 'recipe', 'scope', 'overlap', 'partial', 'negative', 'finding']) {
    const report = structuredClone(positive), r = obj(arr(report.recommendations)[0]), w = obj(arr(r.windows)[0]);
    if (fault === 'negative') w.modified = '-1';
    if (fault === 'finding') obj(r.finding).finding_id = 'finding:wrong';
    if (fault === 'gain') obj(w.improvement_pp).numerator = '999999';
    if (fault === 'recipe') obj(obj(r.finding).recipe).constant = 'OTHER';
    if (fault === 'scope') w.n = '999999';
    if (fault === 'overlap') obj(arr(obj(report.sample.decision).windows)[1]).members = obj(arr(obj(report.sample.decision).windows)[0]).members;
    if (fault === 'partial') w.complete = false;
    expect(() => validateSampleReport(report)).toThrow();
  }
});

it('partial results retain A and distinguish review budget from zero', () => {
  const report = structuredClone(positive), w = obj(arr(obj(arr(report.recommendations)[0]).windows)[1]);
  Object.assign(w, { status: 'budget_exhausted', complete: false, before: null, after: null, improvement_pp: null, rows_ref: null, plan_ref: null, reason_code: 'BUDGET_EXHAUSTED:encoding_calls' });
  render(<SampleReport report={validateSampleReport(report)}/>);
  expect(screen.getByText(/B 独立复核：预算不足/)).toBeInTheDocument();
  expect(screen.getAllByText(/参考提升率/)).toHaveLength(1);
});

it('mount, refresh and history reads never send analysis POST', async () => {
  const fetcher = vi.fn(async (input: RequestInfo | URL, options?: RequestInit) => {
    expect(options?.method ?? 'GET').toBe('GET');
    const path = String(input);
    const value = path.endsWith('/capabilities') ? { service_instance_id: 'test', execution_enabled: true, schemas: { report: schemas.SampleReport3, execution: schemas.Execution3, receipt: sampling.receipt } }
      : path === '/monitoring/catalog' ? { items: [] }
      : path === '/monitoring/user-v2/runs' ? { entries: [] }
      : { service_instance_id: 'test', items: [], next_offset: null };
    return new Response(JSON.stringify(value), { headers: { 'Content-Type': 'application/json' } });
  });
  vi.stubGlobal('fetch', fetcher);
  render(<SampleDiagnostics/>);
  await waitFor(() => expect(screen.getByText(/选择来源后显式启动/)).toBeInTheDocument());
  fireEvent.click(screen.getByText('刷新历史'));
  await waitFor(() => expect(fetcher.mock.calls.length).toBe(5));
  expect(screen.getByText('分析当前来源')).toBeDisabled();
});
it('an older service without V3 keeps the legacy reader usable', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => new Response('{}', { status: 404 })));
  render(<SampleDiagnostics/>);
  await waitFor(() => expect(screen.getByText(/当前服务没有小样本分析入口/)).toBeInTheDocument());
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(screen.getByText('分析当前来源')).toBeDisabled();
});

for (const [name, fixture] of Object.entries({ cch, timestamp, workspace, order, description })) {
  it(`normal backend ${name} publishes an automatic proposal and actual reference`, () => {
    render(<SampleReport report={validateSampleReport(fixture)}/>);
    expect(screen.getByRole('heading', { name: /自动发现 L[123]/ })).toBeInTheDocument();
    expect(screen.getAllByText(/参考提升率/).length).toBeGreaterThan(0);
  });
}
for (const [name, fixture] of Object.entries({ added, representation })) {
  it(`${name} preserves complete pair requests without inventing a proposal`, () => {
    const report = validateSampleReport(fixture);
    expect(arr(report.recommendations)).toHaveLength(0);
    const { container } = render(<SampleReport report={report}/>);
    const raw = container.querySelector('.sample-evidence pre')?.textContent;
    expect(raw).toBeTruthy();
    expect(JSON.parse(raw!).messages).toBeTruthy();
    const bad = structuredClone(fixture);
    obj(arr(obj(bad.discovery).evidence_requests)[0]).raw_body = '{}';
    expect(() => validateSampleReport(bad)).toThrow('EVIDENCE_DIGEST');
  });
}

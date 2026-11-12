import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import positive from '../fixtures/sample-v3/positive.json';
import { arr, obj, AnalysisClient, type Obj } from '../../src/api/analysis/client';
import { sampleCards, sampleExamples } from '../../src/features/analysis/sample-model';
import { Metrics } from '../../src/features/analysis/Reports';
import { mergeSampleCatalog } from '../../src/api/analysis/sample-catalog';
import { validateSampleReport } from '../../src/api/analysis/sample-v3';
import type { LoadedReport } from '../../src/features/analysis/model';

describe('approved V2 layout sample adapter', () => {
  it.each([['1', '2', '+0.5'], ['0', '1', '0'], ['-1', '2', '-0.5']])('displays signed sample gain %s/%s without full or 1pp gates', (n, d, expected) => {
    // Controlled component state only, not a real replay result.
    const report = structuredClone(positive), w = obj(arr(obj(arr(report.recommendations)[0]).windows)[0]);
    w.improvement_pp = { numerator: n, denominator: d };
    const card = sampleCards(report)[0]!;
    const { container } = render(<Metrics card={card}/>);
    expect(container).toHaveTextContent(expected + '个百分点');
    expect(screen.getByText('样本参考提升')).toBeInTheDocument();
    if (n === '-1') expect(container).not.toHaveTextContent('+-');
  });
  it.each(['no_targets', 'no_op', 'not_evaluated', 'budget_exhausted', 'cancelled'])('does not turn %s into zero gain', status => {
    const report = structuredClone(positive), w = obj(arr(obj(arr(report.recommendations)[0]).windows)[0]);
    Object.assign(w, { complete: false, status, before: null, after: null, improvement_pp: null });
    const card = sampleCards(report)[0]!;
    const { container } = render(<Metrics card={card}/>);
    expect(card.metrics).toBeNull();
    expect(container).not.toHaveTextContent('0个百分点');
    expect(container).not.toHaveTextContent('0% →');
  });
  it('aggregates L4/L5 separately, preserving affected union and at most three owners', () => {
    const report = structuredClone(positive) as unknown as Obj;
    obj(report.discovery).cause_groups = Array.from({ length: 8 }, (_, i) => ({ group_id: 'g' + i, rule_id: i < 4 ? 'L4' : 'L5', members: [{ source_record_index: String(i) }], comparison: {} }));
    const cards = sampleCards(report).filter(c => c.kind === 'difference_group');
    expect(cards).toHaveLength(2);
    expect(cards.map(c => c.affected)).toEqual(['4', '4']);
    expect(cards.every(c => c.differenceGroups!.length === 3)).toBe(true);
  });
  it('merges multiple catalog pages and checks binding without loading any report', async () => {
    const report = validateSampleReport(positive), scope = obj(obj(report.sample).parent_scope), source = obj(scope.source);
    const api = new AnalysisClient('test');
    const get = vi.spyOn(api, 'get').mockImplementation(async (path, query) => {
      expect(path).toBe('/diagnostics/v3/tasks');
      const i = query?.offset === '0' ? 'a' : 'b';
      return { service_instance_id: 'test', next_offset: i === 'a' ? '1' : null, items: [{
        execution: { task_id: 'diag-' + i.repeat(32), state: 'completed', checkpoints: [{ kind: 'report', sha256: 'f'.repeat(64) }] },
        source: { source_kind: 'base', base_run_id: source.base_run_id, appid: scope.appid },
        sample_metadata: { sample_id: report.sample_id, manifest_sha256: report.manifest_sha256, scope, selected_count: '8' },
      }] };
    });
    const result = await mergeSampleCatalog(api, { snapshot: 's', cursor: '0', items: [], defaults: [] });
    expect(get).toHaveBeenCalledTimes(2); expect(result.items).toHaveLength(2);
    expect(result.items[0]!.binding_id).toBe(result.items[1]!.binding_id);
    expect(result.selected_reports?.[0]?.task_id).toBe('diag-' + 'a'.repeat(32));
  });
  it('reads only sealed evidence and rejects wrong task identity', async () => {
    const report = validateSampleReport(positive);
    report.evidence_mode = 'sealed_examples';
    const api = new AnalysisClient('test', vi.fn(async (_url, options) => {
      expect(options?.method).toBe('GET');
      return new Response(JSON.stringify({ task_id: 'wrong', sample_id: report.sample_id, owner_id: 'wrong', examples: [] }));
    }));
    const data = { sample: report } as LoadedReport;
    await expect(sampleExamples(api, data, sampleCards(report)[0]!)).rejects.toThrow('EVIDENCE_IDENTITY');
  });
});

import { arr, canonical, obj, str, type AnalysisClient, type Obj } from '../../api/analysis/client';
import { SampleClient3 } from '../../api/analysis/sample-v3';
import { checks, type Card, type LoadedReport } from './model';

const statuses: Record<string, string> = { no_targets: '无适用对象', no_op: '没有实际修改', unavailable: '参考率不可计算', not_evaluated: '尚未评估', budget_exhausted: '资源不足，未完成评估', cancelled: '已取消，未完成评估', failed: '评估失败' };
export function sampleCards(report: Obj): Card[] {
  const discovery = obj(report.discovery), sample = obj(report.sample), decision = obj(sample.decision);
  const window = arr(decision.windows).map(obj).find(x => x.role === 'discovery')!;
  const total = String(arr(window.members).length), synthetic = discovery.synthetic_fixture === true;
  const cards: Card[] = arr(report.recommendations).map(obj).map(r => {
    const f = obj(r.finding), clock = f.rule_version === 'clock-3.1', rule = str(f.rule_id);
    const w = arr(r.windows).map(obj).find(x => x.role === 'discovery');
    const metrics = w?.complete && w.improvement_pp ? { gain_percentage_points: w.improvement_pp } : null;
    const title = clock ? '固定 session_clock，稳定公共前缀' : rule === 'L2' ? '统一相同工具集合的排列' : rule === 'L3' ? '移除工具描述中变化的路径' : '移除前部动态字段';
    const limitation = metrics ? '' : statuses[str(w?.status ?? 'not_evaluated')] ?? '尚未完成评估';
    return { id: str(f.finding_id), kind: 'recommendation', rule, title, tag: checks.low_hit.find(x => x[0]!.startsWith(rule))![0]!,
      description: clock ? '同一模板的 session_clock 随请求变化，打断相同前缀的复用。' : rule === 'L3' ? '可比工具的定义字段存在变化，可能影响前缀复用。' : '同类前部字段或排列存在差异。',
      advice: clock ? '仅将合法 session_clock 标签内的内容固定为 NORMALIZED，保留标签和外部内容。' : str(f.advice),
      conditions: [str(f.advice), '仅为选定样本的参考结果，不能外推为全量业务收益。各方案独立计算，收益不可相加。'],
      synthetic, data: { ...r, direction: 'low_hit', sample_v3: true, status_label: limitation, example_refs: [] },
      evaluation: w?.complete ? w : null, metrics, affected: w?.complete ? str(w.modified) : w?.status === 'no_targets' || w?.status === 'no_op' ? '0' : null,
      total, limitation };
  });
  const refs = obj(report.evidence_refs ?? {});
  for (const rule of ['L4', 'L5']) {
    const groups = arr(discovery.cause_groups).map(obj).filter(x => x.rule_id === rule);
    if (!groups.length) continue;
    const members = new Set(groups.flatMap(g => arr(g.members).map(canonical)));
    const owners = groups.filter(g => report.evidence_mode !== 'sealed_examples' || refs[str(g.group_id)]).slice(0, 3);
    cards.push({ id: `difference-detector:${rule}`, kind: 'difference_group', rule,
      title: rule === 'L4' ? '相同位置的消息出现内容差异' : '相同工具结果，JSON 的写法不一致',
      tag: checks.low_hit.find(x => x[0]!.startsWith(rule))![0]!,
      description: rule === 'L4' ? '可比请求的消息内容不同；当前证据不认定这些请求属于同一次会话。' : '工具结果的 JSON 结构一致，但空格或写法不同。',
      advice: '', conditions: [], synthetic, data: { sample_v3: true, example_refs: [] }, evaluation: null, metrics: null,
      affected: String(members.size), total, differenceGroups: owners,
      limitation: discovery.complete ? '' : '仅统计已发现涉及的请求，不代表穷尽全部差异。' });
  }
  return cards;
}
export async function loadSampleReport(api: AnalysisClient, entry: Obj, signal?: AbortSignal): Promise<LoadedReport> {
  const report = await new SampleClient3(api.instance, api.fetcher).report(str(entry.task_id), signal);
  if (report.sample_id !== entry.sample_id || report.manifest_sha256 !== entry.manifest_sha256 || canonical(obj(report.sample).parent_scope) !== canonical(entry.scope)) throw Error('SAMPLE_REPORT_SOURCE');
  return { entry, report, summary: { availability: 'computed' }, direction: 'low_hit', cards: sampleCards(report),
    sample: report, execution: obj(entry.execution), offsets: { recommendation: null, difference_group: null }, hasMore: false };
}
export async function sampleExamples(api: AnalysisClient, data: LoadedReport, card: Card, signal?: AbortSignal): Promise<Obj[]> {
  const report = data.sample!, owners = card.differenceGroups ?? [obj(card.data.finding)];
  if (report.evidence_mode === 'sealed_examples') {
    const client = new SampleClient3(api.instance, api.fetcher);
    const results = await Promise.all(owners.map(owner => client.evidence(str(report.task_id), str(report.sample_id), str(owner.finding_id ?? owner.group_id), signal)));
    return results.flat().slice(0, 3);
  }
  // Older inline evidence is already digest-verified by validateSampleReport.
  const records = new Map(arr(obj(report.discovery).evidence_requests ?? []).map(obj).map(r => [canonical(r.request_key), r]));
  return owners.flatMap(owner => {
    if (!owner.comparison) return [];
    const pair = obj(owner.comparison), a = records.get(canonical(pair.left)), b = records.get(canonical(pair.right));
    if (!a || !b) return [];
    const pointers = arr(pair.difference_pointers).map(str);
    function pane(record: Obj, pointer: string): Obj {
      let value: unknown = JSON.parse(str(record.raw_body));
      try { for (const key of pointer.split('/').slice(1)) value = (value as Record<string, unknown>)[key.replaceAll('~1', '/').replaceAll('~0', '~')]; } catch { value = undefined; }
      const excerpt = typeof value === 'string' ? value : value === undefined ? '' : JSON.stringify(value);
      return { source: { request_key: record.request_key, source_pointer: pointer, text_range: null }, excerpt: Array.from(excerpt).slice(0, 1000).join(''),
        context_before: '', context_after: '', reason_codes: value === undefined ? ['EVIDENCE_LOCATION_UNAVAILABLE'] : [], raw_span: null, decoded_span: null, omitted_after: excerpt.length > 1000 };
    }
    const leftPointer = owner.left_locations ? str(obj(arr(owner.left_locations)[0]).source_pointer) : pointers[0]!;
    const rightPointer = owner.right_locations ? str(obj(arr(owner.right_locations)[0]).source_pointer) : pointers[0]!;
    return [{ example_id: owner.finding_id ?? owner.group_id, before: pane(a, leftPointer), comparison: pane(b, rightPointer), after: null }];
  });
}

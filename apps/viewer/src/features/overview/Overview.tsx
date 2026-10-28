import type { Dto } from '../../api/types';
import { formatInteger, scaleInteger } from '../../domain/integer';
export const tokenLabels = { json_tokens: '原始 JSON Token', prompt_tokens: '模板后输入 Token', ideal_cached_input_tokens: '理想复用 Token', ideal_compute_input_tokens: '输入重算 Token', completion_tokens: '输出 Token' } as const;
function compact(value: string): string {
  const n = BigInt(value), unit = n >= 1000000n ? 1000000n : n >= 1000n ? 1000n : 1n;
  if (unit === 1n) return formatInteger(value);
  const rounded = (n * 100n + unit / 2n) / unit;
  return `${rounded / 100n}.${(rounded % 100n).toString().padStart(2, '0')}${unit === 1000000n ? 'M' : 'K'}`;
}
export function Overview({ snapshot: s }: { snapshot: Dto<'ViewSnapshot'> }) {
  const rate = s.metrics.ideal_hit_rate, totals = s.metrics.totals;
  const keys = ['json_tokens', 'prompt_tokens', 'ideal_compute_input_tokens', 'completion_tokens'] as const;
  const hitWidth = scaleInteger(totals.ideal_cached_input_tokens, totals.prompt_tokens, 10000) / 100;
  return <section aria-label="核心指标"><div className="group-title"><h2>监控概览</h2><span className="badge">{s.identity.model_id === 'GLM-5.2' ? '完整块链式' : '普通链式近似'} · 无限容量</span></div>
    <div className="metric-grid"><article className="metric hit"><span>理想命中率</span><strong>{rate === null ? '—' : `${(rate * 100).toFixed(2)}%`}</strong><small>按输入 Token 总量计算 · 本窗口空缓存开始</small></article><article className="metric"><span>请求数量</span><strong>{formatInteger(s.metrics.request_count)}<em>条</em></strong><small>当前租户与模型的有效请求</small></article>{keys.map(key => <article className={`metric ${key === 'ideal_compute_input_tokens' ? 'compute' : ''}`} key={key}><span>{tokenLabels[key]}</span><strong title={formatInteger(totals[key])}>{compact(totals[key])}</strong><small>{key === 'json_tokens' ? '套模板前 · 含 JSON 字段与参数' : key === 'prompt_tokens' ? '模型实际输入的计量口径' : key === 'ideal_compute_input_tokens' ? '模板后输入 − 理想命中' : '来自 completion_tokens · 单独统计'}</small></article>)}</div>
    <div className="bar-panel"><div className="bar-title">输入 Token 去向<small>模板后输入 = 已命中 + 需重算</small></div><div><div className="tokenbar" aria-label="命中与重算占比"><span style={{ width: `${hitWidth}%` }} /><span style={{ width: `${totals.prompt_tokens === '0' ? 0 : 100 - hitWidth}%` }} /></div><div className="bar-legend"><span>理想复用 Token <b>{formatInteger(totals.ideal_cached_input_tokens)}</b></span><span>输入重算 <b>{formatInteger(totals.ideal_compute_input_tokens)}</b></span></div></div></div>
    <details className="exact-values"><summary>查看精确 Token 总量</summary><dl>{Object.entries(tokenLabels).map(([key, label]) => <div key={key}><dt>{label}</dt><dd>{formatInteger(totals[key as keyof typeof tokenLabels])}</dd></div>)}</dl></details>
  </section>;
}

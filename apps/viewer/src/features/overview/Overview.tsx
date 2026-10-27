import { Exports } from '../exports/Exports';
import type { Dto } from '../../api/types';
import { formatInteger } from '../../domain/integer';
import { formatBeijing } from '../../domain/time';
export const tokenLabels = { json_tokens: '原始 JSON Token', prompt_tokens: '模板后输入 Token', ideal_cached_input_tokens: '理想复用 Token', ideal_compute_input_tokens: '输入重算 Token', completion_tokens: '输出 Token' } as const;
export function Overview({ snapshot: s }: { snapshot: Dto<'ViewSnapshot'> }) {
  const rate = s.metrics.ideal_hit_rate;
  return <><div className="metric-grid"><article className="metric"><span>理想命中率</span><strong>{rate === null ? '—' : `${(rate * 100).toFixed(2)}%`}</strong><small>输入 Token 加权 · 本窗口空缓存开始</small></article><article className="metric"><span>请求数量</span><strong>{formatInteger(s.metrics.request_count)}</strong></article>{Object.entries(tokenLabels).map(([key, label]) => <article className="metric" key={key}><span>{label}</span><strong>{formatInteger(s.metrics.totals[key as keyof typeof tokenLabels])}</strong></article>)}</div>
    <section className="panel identity"><h2>当前完整结果</h2><p>组数据：{formatBeijing(s.provenance.data_range_utc.start)} — {formatBeijing(s.provenance.data_range_utc.end)}</p><p>整文件：{formatBeijing(s.provenance.file_data_range_utc.start)} — {formatBeijing(s.provenance.file_data_range_utc.end)}</p><p>生成时间：{formatBeijing(s.provenance.published_at)} · {s.provenance.source_label}</p>
    <p>Block size {s.provenance.settings.block_size} · CP {s.provenance.settings.cp_world_size} · MTP {s.provenance.settings.mtp ? '开启' : '关闭'}{s.identity.model_id !== 'GLM-5.2' && ' · 普通链式近似，未模拟 hybrid cache'}</p>
    <details><summary>数据质量与版本</summary><p>整文件无效行 {formatInteger(s.quality.file_quality.skipped_rows)}；本组有效请求 {formatInteger(s.quality.group_quality.valid_requests)}；本组重复 ID 提示 {formatInteger(s.quality.group_quality.duplicate_hash_id_rows_within_group)}。</p><p>无法归属的无效行不分摊到本组。本组跳过行：{formatInteger(s.quality.group_quality.skipped_rows)}</p><p>run：{s.identity.run_id} · 设置版本 {s.provenance.settings.revision}</p><pre>{JSON.stringify(s.provenance.runtime, null, 2)}</pre></details><Exports snapshot={s} /></section></>;
}

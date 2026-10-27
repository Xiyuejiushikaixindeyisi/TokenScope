import { useState } from 'react';
import type { Dto } from '../../api/types';
import { formatInteger, scaleInteger } from '../../domain/integer';
export type LengthMetric = 'json_tokens' | 'prompt_tokens' | 'ideal_compute_input_tokens';
export interface BinSelection { metric: LengthMetric; lower: string; upper: string | null }
const labels: Record<LengthMetric, string> = { json_tokens: '原始 JSON 长度', prompt_tokens: '模板后输入长度', ideal_compute_input_tokens: '输入重算长度' };
export function Distributions({ snapshot, onSelect }: { snapshot: Dto<'ViewSnapshot'>; onSelect(value: BinSelection): void }) {
  const [width, setWidth] = useState<'1000' | '2000' | '5000'>('5000');
  const [share, setShare] = useState(false);
  const keys = Object.keys(labels) as LengthMetric[];
  const max = keys.flatMap(key => snapshot.distributions[key][width].bins).reduce((n, bin) => BigInt(bin.count) > n ? BigInt(bin.count) : n, 0n).toString();
  return <section><div className="toolbar"><label>分箱宽度 <select value={width} onChange={event => setWidth(event.target.value as typeof width)}><option value="1000">1K</option><option value="2000">2K</option><option value="5000">5K</option></select></label><label><input type="checkbox" checked={share} onChange={event => setShare(event.target.checked)} />显示请求占比</label><span className="muted">K = 1000 Token · 所有图共用纵轴尺度</span></div>
    <div className="chart-grid">{keys.map(metric => {
      const histogram = snapshot.distributions[metric][width], q = snapshot.metrics.quantiles[metric];
      const modes = new Set(histogram.summary.mode_bin_indices);
      return <article className="panel chart" key={metric}><h2>{labels[metric]}</h2><p className="muted">纵轴：{share ? '请求占比' : '请求数'}；横轴：Token 长度区间</p>
        <svg role="group" aria-label={`${labels[metric]}直方图`} viewBox="0 0 640 230"><text x="0" y="14" fontSize="22">{share ? `${((snapshot.metrics.request_count === '0' ? 0 : Number(BigInt(max) * 10000n / BigInt(snapshot.metrics.request_count))) / 100).toFixed(2)}%` : formatInteger(max)}</text>
          {histogram.bins.map((bin, index) => { const h = scaleInteger(bin.count, max, 170), w = 580 / histogram.bins.length, label = bin.upper === null ? '≥200K' : `${formatInteger(bin.lower)}–${formatInteger(bin.upper)}`; const activate = () => onSelect({ metric, lower: bin.lower, upper: bin.upper });
            return <g key={bin.lower}><rect data-mode={modes.has(String(index)) ? 'true' : 'false'} role="button" tabIndex={0} aria-label={`${label} Token：${formatInteger(bin.count)} 个请求`} x={45 + index * w} y={195 - Math.max(h, 2)} width={Math.max(1, w - 1)} height={Math.max(h, 2)} fill={modes.has(String(index)) ? '#3468e8' : '#b6c9ed'} onClick={activate} onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); activate(); } }}><title>{label} Token；{formatInteger(bin.count)} 请求；占比 {bin.share === null ? '—' : `${(bin.share * 100).toFixed(2)}%`}</title></rect></g>;
          })}<text x="45" y="220" fontSize="22">0</text><text x="310" y="220" fontSize="22">100K</text><text x="540" y="220" fontSize="22">≥200K</text></svg>
        <p className="mode">众数区间：{histogram.summary.mode_bin_indices.length ? histogram.summary.mode_bin_indices.map(index => { const bin = histogram.bins[Number(index)]!; return bin.upper === null ? '≥200K' : `${formatInteger(bin.lower)}–${formatInteger(bin.upper)}`; }).join('、') : '—'}</p>
        <p className="quantiles">P50 <b>{formatInteger(q.p50)}</b>　P80 <b>{formatInteger(q.p80)}</b>　P90 <b>{formatInteger(q.p90)}</b></p><p className="muted">&lt;8K：{formatInteger(histogram.summary.under_8k_count)}　≥200K：{formatInteger(histogram.summary.overflow_count)}</p>
      </article>;
    })}</div></section>;
}

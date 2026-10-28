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
  return <section className="distributions"><div className="group-title"><h2>请求长度分布</h2><span className="muted">5K 默认分箱 · 高亮众数区间</span></div><div className="toolbar"><label>分箱宽度 <select value={width} onChange={event => setWidth(event.target.value as typeof width)}><option value="1000">1K</option><option value="2000">2K</option><option value="5000">5K</option></select></label><label><input type="checkbox" checked={share} onChange={event => setShare(event.target.checked)} />显示请求占比</label><span className="muted">K = 1000 Token · 所有图共用纵轴尺度</span></div>
    <div className="chart-grid">{keys.map(metric => {
      const histogram = snapshot.distributions[metric][width], q = snapshot.metrics.quantiles[metric];
      const modes = new Set(histogram.summary.mode_bin_indices);
      return <article className="panel chart" key={metric}><h2>{labels[metric]}</h2><p className="muted">纵轴：{share ? '请求占比' : '请求数'}；横轴：Token 长度区间</p>
        <div className="quantiles">{(['p50', 'p80', 'p90'] as const).map(key => <div className="quantile" key={key}><small>{key.toUpperCase()}</small><b>{formatInteger(q[key])}</b></div>)}</div>
        <p className="mode">众数区间：{histogram.summary.mode_bin_indices.length ? histogram.summary.mode_bin_indices.map(index => { const bin = histogram.bins[Number(index)]!; return bin.upper === null ? '≥200K' : `${formatInteger(bin.lower)}–${formatInteger(bin.upper)}`; }).join('、') : '—'}</p>
        <svg role="group" aria-label={`${labels[metric]}直方图`} viewBox="0 0 400 240"><text x="0" y="17" fontSize="11">{share ? `${((snapshot.metrics.request_count === '0' ? 0 : Number(BigInt(max) * 10000n / BigInt(snapshot.metrics.request_count))) / 100).toFixed(2)}%` : formatInteger(max)}</text>
          {[0, 1, 2, 3, 4].map(i => <line key={i} x1="35" x2="385" y1={195 - i * 40} y2={195 - i * 40} stroke="#e9eef5" strokeWidth="1" />)}
          {histogram.bins.map((bin, index) => { const h = scaleInteger(bin.count, max, 160), w = 350 / histogram.bins.length, label = bin.upper === null ? '≥200K' : `${formatInteger(bin.lower)}–${formatInteger(bin.upper)}`; const activate = () => onSelect({ metric, lower: bin.lower, upper: bin.upper });
            return <g key={bin.lower}><rect data-mode={modes.has(String(index)) ? 'true' : 'false'} role="button" tabIndex={0} aria-label={`${label} Token：${formatInteger(bin.count)} 个请求`} x={35 + index * w} y={195 - Math.max(h, 2)} width={Math.max(1, w - 1)} height={Math.max(h, 2)} fill={modes.has(String(index)) ? '#3468e8' : metric === 'ideal_compute_input_tokens' ? '#8dcac3' : '#b6c9ed'} onClick={activate} onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); activate(); } }}><title>{label} Token；{formatInteger(bin.count)} 请求；占比 {bin.share === null ? '—' : `${(bin.share * 100).toFixed(2)}%`}</title></rect></g>;
          })}<text x="35" y="215" fontSize="11">0K</text><text x="115" y="215" fontSize="11">50K</text><text x="195" y="215" fontSize="11">100K</text><text x="280" y="215" fontSize="11">150K</text><text x="350" y="215" fontSize="11">≥200K</text><text x="285" y="235" fontSize="10">长度区间 (Token)</text></svg>

        <p className="muted">&lt;8K：{formatInteger(histogram.summary.under_8k_count)}　≥200K：{formatInteger(histogram.summary.overflow_count)}</p>
      </article>;
    })}</div></section>;
}

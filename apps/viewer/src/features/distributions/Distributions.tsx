import { useState } from 'react';
import { useRead } from '../../components/useRead';
import { RankChart } from '../requests/Requests';
import type { Dto } from '../../api/types';
import { formatInteger, scaleInteger } from '../../domain/integer';
export type LengthMetric = 'json_tokens' | 'prompt_tokens' | 'ideal_compute_input_tokens';
export interface BinSelection { metric: LengthMetric; lower: string; upper: string | null }
const labels: Record<LengthMetric, string> = { json_tokens: '原始 JSON 长度', prompt_tokens: '模板后输入长度', ideal_compute_input_tokens: '输入重算长度' };
export function Distributions({ snapshot, onSelect }: { snapshot: Dto<'ViewSnapshot'>; onSelect(value: BinSelection): void }) {
  const [width, setWidth] = useState<'1000' | '2000' | '5000'>('5000');
  const [share, setShare] = useState(false);
  const [view,setView] = useState('histogram');
  const keys = Object.keys(labels) as LengthMetric[];
  const max = keys.flatMap(key => snapshot.distributions[key][width].bins).reduce((n, bin) => BigInt(bin.count) > n ? BigInt(bin.count) : n, 0n).toString();
  return <section className="distributions"><div className="group-title"><h2>请求长度分布</h2><span className="muted">5K 默认分箱 · 高亮众数区间</span></div><div className="toolbar distribution-tools"><label>视图<select aria-label="分布视图" value={view} onChange={e => setView(e.target.value)}><option value="histogram">长度分布 · 直方图</option><option value="rank">降序明细 · 辅助视图</option></select></label><label hidden={view !== 'histogram'}>区间宽度 <select aria-label="分箱宽度" value={width} onChange={event => setWidth(event.target.value as typeof width)}><option value="1000">1K Token</option><option value="2000">2K Token</option><option value="5000">5K Token</option></select></label><label hidden={view !== 'histogram'}>纵轴<select aria-label="分布纵轴" value={share ? 'share' : 'count'} onChange={e=>setShare(e.target.value === 'share')}><option value="share">请求占比</option><option value="count">请求数</option></select></label><span className="muted">P50 / P80 / P90 仅展示数值 · K = 1000 Token</span></div>
    <div className="chart-grid">{keys.map(metric => {
      const histogram = snapshot.distributions[metric][width], q = snapshot.metrics.quantiles[metric];
      const modes = new Set(histogram.summary.mode_bin_indices);
      return <article className="panel chart" key={metric}><h2>{labels[metric]}</h2><p className="muted">{view === 'rank' ? '纵轴：Token；横轴：请求排名（当前范围降序）' : `纵轴：${share ? '请求占比' : '请求数'}；横轴：Token 长度区间`}</p>
        <div className="quantiles">{(['p50', 'p80', 'p90'] as const).map(key => <div className="quantile" key={key}><small>{key.toUpperCase()}</small><b>{formatInteger(q[key])}</b></div>)}</div>
        <p className="mode mode-summary">众数区间：{histogram.summary.mode_bin_indices.length ? histogram.summary.mode_bin_indices.map(index => { const bin = histogram.bins[Number(index)]!; return bin.upper === null ? '≥200K' : `${formatInteger(bin.lower)}–${formatInteger(bin.upper)}`; }).join('、') : '—'} · 每个峰 {formatInteger(histogram.summary.mode_count)} 条（{histogram.summary.mode_share === null ? '—' : `${(histogram.summary.mode_share*100).toFixed(2)}%`}）</p>
        {view === 'rank' ? <DistributionRank key={snapshot.identity.run_id + snapshot.identity.appid + metric} snapshot={snapshot} metric={metric}/> : <svg role="group" aria-label={`${labels[metric]}直方图`} viewBox="0 0 400 240"><text x="0" y="17" fontSize="11">{share ? `${((snapshot.metrics.request_count === '0' ? 0 : Number(BigInt(max) * 10000n / BigInt(snapshot.metrics.request_count))) / 100).toFixed(2)}%` : formatInteger(max)}</text>
          {[0, 1, 2, 3, 4].map(i => <g key={i}><line x1="35" x2="385" y1={195 - i * 40} y2={195 - i * 40} stroke="#e9eef5" strokeWidth="1"/><text x="31" y={198-i*40} textAnchor="end" fontSize="10" fill="#69778a">{share ? `${(snapshot.metrics.request_count==='0'?0:Number(BigInt(max)*BigInt(i)*1000n/(4n*BigInt(snapshot.metrics.request_count)))/10).toFixed(1)}%` : formatInteger((BigInt(max)*BigInt(i)/4n).toString())}</text></g>)}
          {histogram.bins.map((bin, index) => { const h = scaleInteger(bin.count, max, 160), w = 350 / histogram.bins.length, label = bin.upper === null ? '≥200K' : `${formatInteger(bin.lower)}–${formatInteger(bin.upper)}`; const activate = () => onSelect({ metric, lower: bin.lower, upper: bin.upper });
            return <g key={bin.lower}><rect data-mode={modes.has(String(index)) ? 'true' : 'false'} role="button" tabIndex={0} aria-label={`${label} Token：${formatInteger(bin.count)} 个请求`} x={35 + index * w} y={195 - Math.max(h, 2)} width={Math.max(1, w - 1)} height={Math.max(h, 2)} fill={modes.has(String(index)) ? '#3468e8' : metric === 'ideal_compute_input_tokens' ? '#8dcac3' : '#b6c9ed'} onClick={activate} onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); activate(); } }}><title>{label} Token；{formatInteger(bin.count)} 请求；占比 {bin.share === null ? '—' : `${(bin.share * 100).toFixed(2)}%`}</title></rect></g>;
          })}<text x="35" y="215" fontSize="11">0K</text><text x="115" y="215" fontSize="11">50K</text><text x="195" y="215" fontSize="11">100K</text><text x="280" y="215" fontSize="11">150K</text><text x="350" y="215" fontSize="11">≥200K</text><text x="285" y="235" fontSize="10">长度区间 (Token)</text></svg>}

        <p className="muted">&lt;8K：{formatInteger(histogram.summary.under_8k_count)}　≥200K：{formatInteger(histogram.summary.overflow_count)}</p>
      </article>;
    })}</div></section>;
}

function DistributionRank({snapshot,metric}:{snapshot:Dto<'ViewSnapshot'>;metric:LengthMetric}) {
 const [offset,setOffset]=useState('0');
 const {data,error,reload}=useRead('RequestsPage',`/analysis-runs/${snapshot.identity.run_id}/requests`,{appid:snapshot.identity.appid,sort_by:metric,sort_order:'desc',offset,limit:1000},snapshot.identity);
 return <>{error && <p role="alert">{error}<button onClick={reload}>重读曲线</button></p>}{data ? <><RankChart key={offset} page={data} metric={metric}/><div className="toolbar"><button disabled={offset==='0'} onClick={()=>setOffset((BigInt(offset)>1000n?BigInt(offset)-1000n:0n).toString())}>上一段</button><span>当前段 {data.items.length ? formatInteger((BigInt(offset)+1n).toString()) : '0'}–{formatInteger((BigInt(offset)+BigInt(data.items.length)).toString())} / 共 {formatInteger(data.total)} 条</span><button disabled={!data.next_offset} onClick={()=>data.next_offset&&setOffset(data.next_offset)}>下一段</button></div></> : !error && <p role="status">读取降序明细…</p>}</>;
}

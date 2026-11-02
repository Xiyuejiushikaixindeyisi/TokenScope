import { Exports } from '../exports/Exports';
import { useEffect, useRef, useState } from 'react';
import type { Dto } from '../../api/types';
import { apiPath } from '../../api/client';
import { useRead } from '../../components/useRead';
import { formatInteger, scaleInteger } from '../../domain/integer';
import { formatBeijing } from '../../domain/time';
import type { BinSelection, LengthMetric } from '../distributions/Distributions';
import { tokenLabels } from '../overview/Overview';
const metrics: LengthMetric[] = ['json_tokens', 'prompt_tokens', 'ideal_compute_input_tokens'];
export function Requests({ snapshot, filter, onDetail }: { snapshot: Dto<'ViewSnapshot'>; filter: BinSelection | null; onDetail(open: boolean): void }) {
  const [offset, setOffset] = useState('0'), [metric, setMetric] = useState<LengthMetric>(filter?.metric ?? 'prompt_tokens');
  const [order, setOrder] = useState<'desc' | 'asc'>('desc'), [hash, setHash] = useState(''), [search, setSearch] = useState(''), [match, setMatch] = useState<'exact' | 'prefix'>('exact');
  const [rank, setRank] = useState(false), [detail, setDetail] = useState<string | null>(null);
  const limit = rank ? 1000 : 50;
  useEffect(() => { const timer = setTimeout(() => { setSearch(hash); setOffset('0'); }, 250); return () => clearTimeout(timer); }, [hash]);
  useEffect(() => { onDetail(detail !== null); return () => onDetail(false); }, [detail, onDetail]);
  const query = { appid: snapshot.identity.appid, metric: filter?.metric ?? metric, lower: filter?.lower ?? '0', upper: filter?.upper ?? undefined, sort_by: metric, sort_order: rank ? 'desc' : order, hash_id: search || undefined, hash_match: match, offset, limit };
  const { data, error, reload } = useRead('RequestsPage', `/analysis-runs/${snapshot.identity.run_id}/requests`, query, snapshot.identity);
  return <section className="panel"><h2>请求明细</h2><div className="toolbar"><label>排序 <select value={metric} onChange={e => { setMetric(e.target.value as LengthMetric); setOffset('0'); }}>{metrics.map(m => <option key={m} value={m}>{tokenLabels[m]}</option>)}</select></label><label>顺序 <select disabled={rank} value={order} onChange={e => { setOrder(e.target.value as typeof order); setOffset('0'); }}><option value="desc">从长到短</option><option value="asc">从短到长</option></select></label><label>hash_id <input value={hash} onChange={e => setHash(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') { setSearch(hash); setOffset('0'); } }} /></label><select aria-label="ID匹配方式" value={match} onChange={e => { setMatch(e.target.value as typeof match); setOffset('0'); }}><option value="exact">精确</option><option value="prefix">文字前缀</option></select><label><input type="checkbox" checked={rank} onChange={e => { setRank(e.target.checked); setOffset('0'); }} />辅助排名图（每段至多1000点）</label></div>
    {filter && <p className="muted">当前区间：{tokenLabels[filter.metric]} [{formatInteger(filter.lower)}, {filter.upper === null ? '+∞' : formatInteger(filter.upper)})</p>}
    {error && <p role="alert">{error}<button onClick={reload}>重读请求页</button></p>}{!data && !error && <p>正在读取完整请求页…</p>}
    {data && <>{rank && <RankChart key={metric + offset} page={data} metric={metric} />}<p className="muted">当前第 {data.items.length ? formatInteger((BigInt(offset) + 1n).toString()) : '0'}–{formatInteger((BigInt(offset) + BigInt(data.items.length)).toString())} 条 / 共 {formatInteger(data.total)} 条；每行是同一请求，重复 ID 保留。</p><div className="table-scroll"><table><thead><tr><th>位置</th><th>hash_id / 北京时间</th>{Object.values(tokenLabels).map(v => <th key={v}>{v}</th>)}<th>详情</th></tr></thead><tbody>{data.items.map(row => <tr key={row.request_ref.source_record_index}><td>{formatInteger(row.position)}</td><td><span className="wrap">{row.hash_id}</span><small>{formatBeijing(row.time_utc)}</small></td>{Object.keys(tokenLabels).map(key => <td key={key}>{formatInteger(row[key as keyof typeof tokenLabels])}</td>)}<td><button onClick={() => setDetail(row.request_ref.source_record_index)}>查看请求 {row.request_ref.source_record_index}</button></td></tr>)}</tbody></table></div>{!data.items.length && <p>该筛选范围没有请求。</p>}<div className="toolbar"><button disabled={offset === '0'} onClick={() => setOffset((BigInt(offset) > BigInt(limit) ? BigInt(offset) - BigInt(limit) : 0n).toString())}>上一页</button><button disabled={data.next_offset === null} onClick={() => setOffset(data.next_offset!)}>下一页</button></div></>}
    <Exports snapshot={snapshot} filter={{ metric: query.metric, lower: query.lower, upper: query.upper ?? null, hash_id: search || null, hash_match: match }} sort={{ by: metric, order: rank ? 'desc' : order, tie_breaker: 'source_record_index_asc' }} />
    {detail && <RequestDetail snapshot={snapshot} index={detail} onClose={() => setDetail(null)} />}
  </section>;
}
const rankColors: Record<LengthMetric, string> = { json_tokens: '#6c87a7', prompt_tokens: '#4277e6', ideal_compute_input_tokens: '#098e80' };
/** Axis labels are approximate; selected values remain exact decimal integers. */
function rankTick(n: bigint) {
  for (const [unit, suffix] of [[1000000000000n, 'T'], [1000000000n, 'B'], [1000000n, 'M'], [1000n, 'K']] as const)
    if (n >= unit) return `${n / unit}${n % unit * 10n / unit ? '.' + (n % unit * 10n / unit) : ''}${suffix}`;
  return n.toString();
}
export function rankPointerIndex(svg: SVGSVGElement, clientX: number, clientY: number, last: number): number | null {
  try {
    const matrix = svg.getScreenCTM();
    if (!matrix || last < 0) return null;
    const point = svg.createSVGPoint();
    point.x = clientX; point.y = clientY;
    const local = point.matrixTransform(matrix.inverse());
    if (!Number.isFinite(local.x) || !Number.isFinite(local.y)) return null;
    return Math.max(0, Math.min(last, Math.round((local.x - 51) / 333 * last)));
  } catch { return null; }
}
export function RankChart({ page, metric }: { page: Dto<'RequestsPage'>; metric: LengthMetric }) {
  const [selected, setSelected] = useState(0);
  const rows = page.items, color = rankColors[metric], last = rows.length - 1;
  const max = rows.reduce((n, row) => BigInt(row[metric]) > n ? BigInt(row[metric]) : n, 0n);
  const ceiling = max === 0n ? 1n : (max * 109n + 99n) / 100n;
  const x = (i: number) => 51 + i * 333 / Math.max(1, last);
  const y = (n: string) => 182 - scaleInteger(n, ceiling.toString(), 158);
  const ticks = [...new Set([0, Math.floor(last / 3), Math.floor(last * 2 / 3), last])].filter(i => i >= 0);
  const index = Math.min(selected, Math.max(0, last)), current = rows[index];
  const path = rows.map((row, i) => `${i ? 'L' : 'M'}${x(i)} ${y(row[metric])}`).join(' ');
  const rank = (i: number) => (BigInt(page.offset) + BigInt(i) + 1n).toString();
  return <figure className="rank-chart" style={{ margin: 0 }}>
    {!rows.length ? <p>当前范围没有请求。</p> : <><svg viewBox="0 0 400 220" role="img" tabIndex={0} aria-label={`${tokenLabels[metric]}，Token 纵轴、请求排名横轴；左右方向键查看当前段精确值`}
      onKeyDown={event => { if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') { event.preventDefault(); setSelected(Math.max(0, Math.min(last, index + (event.key === 'ArrowRight' ? 1 : -1)))); } }}
      onPointerMove={event => { const next = rankPointerIndex(event.currentTarget, event.clientX, event.clientY, last); if (next !== null) setSelected(next); }}>
      <g fontSize="10" fill="#8c98a8">{[0,1,2,3,4].map(i => <g key={i}><line x1="51" x2="384" y1={182-i*39.5} y2={182-i*39.5} stroke="#e9edf3"/><text x="43" y={185-i*39.5} textAnchor="end">{rankTick(ceiling*BigInt(i)/4n)}</text></g>)}
      {ticks.map(i => <text key={i} x={x(i)} y="201" textAnchor={i===0?'start':i===last?'end':'middle'}>{formatInteger(rank(i))}</text>)}<text x="51" y="12">Token</text><text x="384" y="217" textAnchor="end">请求排名</text></g>
      <path d={path + ` L ${x(last)} 182 L 51 182 Z`} fill={color} opacity=".045"/><path d={path} fill="none" stroke={color} strokeWidth="1.6"/>
      {rows.map((row,i)=><circle key={i} cx={x(i)} cy={y(row[metric])} r="1.25" fill={color}><title>排名 #{formatInteger(rank(i))} · {row.hash_id} · {formatInteger(row[metric])} Token</title></circle>)}
      {current && <><line x1={x(index)} x2={x(index)} y1="24" y2="182" stroke="#a6b6ca" strokeDasharray="3 3"/><circle cx={x(index)} cy={y(current[metric])} r="4" fill={color} stroke="white" strokeWidth="2"/></>}
    </svg>{current && <p className="muted wrap" aria-live="polite">排名 #{formatInteger(rank(index))} · {current.hash_id} · 源记录 {formatInteger(current.request_ref.source_record_index)}：<strong>{formatInteger(current[metric])} Token</strong></p>}</>}
    <figcaption className="muted">当前段最多1000条，非全量曲线；悬停或聚焦图表后按左右键查看本段精确值。排名相对于当前筛选范围。</figcaption>
  </figure>;
}
function RequestDetail({ snapshot, index, onClose }: { snapshot: Dto<'ViewSnapshot'>; index: string; onClose(): void }) {
  const dialog = useRef<HTMLDialogElement>(null); const scope = snapshot.identity;
  const path = `/analysis-runs/${scope.run_id}/requests/${index}`;
  const { data, error } = useRead('RequestDetail', path, { appid: scope.appid }, scope, false);
  const [section, setSection] = useState<'special_ranges' | 'source_fields'>('special_ranges'), [offset, setOffset] = useState('0');
  const evidence = useRead('EvidencePage', path + '/evidence', { appid: scope.appid, section, offset, limit: 256 }, scope, false);
  const [body, setBody] = useState<string | null>(null), [bodyNote, setBodyNote] = useState('');
  const controller = useRef<AbortController | null>(null);
  useEffect(() => { const d = dialog.current!; d.showModal(); return () => { controller.current?.abort(); d.close(); }; }, []);
  const readBody = async () => {
    controller.current?.abort(); const abort = new AbortController(); controller.current = abort;
    try {
      const response = await fetch(apiPath(path + '/body', { appid: scope.appid }), { signal: abort.signal, cache: 'no-store', redirect: 'error', headers: { 'X-TokenScope-Instance-Id': scope.service_instance_id } });
      if (!response.ok || !response.body) throw new Error();
      const reader = response.body.getReader(), decoder = new TextDecoder('utf-8', { fatal: true }); let size = 0, text = '', truncated = false;
      try { while (true) { const next = await reader.read(); if (next.done) { text += decoder.decode(); break; } const allowed = 1024 * 1024 - size; if (next.value.length > allowed) { text += decoder.decode(next.value.subarray(0, allowed), { stream: true }); truncated = true; await reader.cancel(); break; } size += next.value.length; text += decoder.decode(next.value, { stream: true }); } }
      finally { reader.releaseLock(); }
      if (!abort.signal.aborted) { setBody(text); setBodyNote(truncated ? '已达到1MiB预览上限；此处不是完整原文。' : '已读取完整原始JSON，仅本次打开保留。'); }
    } catch { if (!abort.signal.aborted) setBodyNote('原文读取失败，可重试。'); }
  };
  return <dialog ref={dialog} onCancel={onClose} aria-label="请求详情"><div className="toolbar"><h2>请求详情 · {index}</h2><button onClick={onClose}>关闭详情</button></div>{error && <p role="alert">{error}</p>}{data && <><p>{data.request.hash_id}</p><p>原始 JSON 预览：{formatInteger(data.body_preview.preview_utf8_bytes)} / {formatInteger(data.body_preview.total_utf8_bytes)} UTF8 字节{data.body_preview.truncated && '（已截断）'}</p><pre>{body ?? data.body_preview.text}</pre>{data.capabilities.original_json && <button onClick={() => void readBody()}>按需读取原文（预览上限1MiB）</button>}<p>{bodyNote}</p><p className="muted">未保存模板正文。特殊区间是模板 UTF8 字节位置；来源字段不能相加作为 Token 归因。</p></>}
    <label>轻证据 <select value={section} onChange={e => { setSection(e.target.value as typeof section); setOffset('0'); }}><option value="special_ranges">特殊 Token 字节区间</option><option value="source_fields">来源字段</option></select></label>{evidence.error && <p>{evidence.error}</p>}{evidence.data && <><pre>{JSON.stringify(evidence.data.items, null, 2)}</pre><button disabled={offset === '0'} onClick={() => setOffset((BigInt(offset) >= 256n ? BigInt(offset) - 256n : 0n).toString())}>上一组证据</button><button disabled={!evidence.data.next_offset} onClick={() => setOffset(evidence.data!.next_offset!)}>下一组证据</button></>}
  </dialog>;
}

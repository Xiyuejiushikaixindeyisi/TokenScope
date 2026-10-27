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
    {data && <>{rank && <RankChart page={data} metric={metric} />}<p className="muted">当前第 {data.items.length ? formatInteger((BigInt(offset) + 1n).toString()) : '0'}–{formatInteger((BigInt(offset) + BigInt(data.items.length)).toString())} 条 / 共 {formatInteger(data.total)} 条；每行是同一请求，重复 ID 保留。</p><div className="table-scroll"><table><thead><tr><th>位置</th><th>hash_id / 北京时间</th>{Object.values(tokenLabels).map(v => <th key={v}>{v}</th>)}<th>详情</th></tr></thead><tbody>{data.items.map(row => <tr key={row.request_ref.source_record_index}><td>{formatInteger(row.position)}</td><td><span className="wrap">{row.hash_id}</span><small>{formatBeijing(row.time_utc)}</small></td>{Object.keys(tokenLabels).map(key => <td key={key}>{formatInteger(row[key as keyof typeof tokenLabels])}</td>)}<td><button onClick={() => setDetail(row.request_ref.source_record_index)}>查看请求 {row.request_ref.source_record_index}</button></td></tr>)}</tbody></table></div>{!data.items.length && <p>该筛选范围没有请求。</p>}<div className="toolbar"><button disabled={offset === '0'} onClick={() => setOffset((BigInt(offset) > BigInt(limit) ? BigInt(offset) - BigInt(limit) : 0n).toString())}>上一页</button><button disabled={data.next_offset === null} onClick={() => setOffset(data.next_offset!)}>下一页</button></div></>}
    <Exports snapshot={snapshot} filter={{ metric: query.metric, lower: query.lower, upper: query.upper ?? null, hash_id: search || null, hash_match: match }} sort={{ by: metric, order: rank ? 'desc' : order, tie_breaker: 'source_record_index_asc' }} />
    {detail && <RequestDetail snapshot={snapshot} index={detail} onClose={() => setDetail(null)} />}
  </section>;
}
function RankChart({ page, metric }: { page: Dto<'RequestsPage'>; metric: LengthMetric }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current, ctx = canvas?.getContext('2d'); if (!canvas || !ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height); const max = page.items.reduce((n, r) => BigInt(r[metric]) > n ? BigInt(r[metric]) : n, 0n).toString();
    ctx.strokeStyle = '#3468e8'; ctx.beginPath(); page.items.forEach((row, i) => { const x = 20 + i * 760 / Math.max(1, page.items.length - 1), y = 180 - scaleInteger(row[metric], max, 160); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }); ctx.stroke();
  }, [page, metric]);
  return <figure><canvas ref={ref} width={800} height={200} aria-label="当前页请求长度降序曲线，精确值见下表" role="img" /><figcaption>当前段最多1000条，非全量曲线；精确值见下表。</figcaption></figure>;
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

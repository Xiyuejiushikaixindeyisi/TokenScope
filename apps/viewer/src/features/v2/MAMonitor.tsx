import { useEffect, useRef, useState } from 'react';
import type { V2Client } from '../../api/v2/client';
import { segment } from '../../api/v2/client';
import { ApiError } from '../../api/client';
import type { Receipt, Snapshot, QualityPage } from '../../api/v2/generated/ma';
import type { CatalogEntry } from '../../api/v2/generated/ma/Catalog';
import { TaskTracker } from '../../state/v2-task';
import { RequestPool } from '../../state/v2-pool';
import { V2Records } from '../../storage/v2-records';
import type { Intent } from '../../storage/v2-records';
import { Modal, models, fields, errorText, percent, stateLabel } from './common';
import { MACharts, maTime, rate, idealLabel } from './MACharts';
type Display = {
    receipt: Receipt;
    entry: CatalogEntry;
};
type Row = {
    state: 'loading' | 'failed' | 'ready';
    snapshot?: Snapshot;
    error?: string;
};
async function directory(api: V2Client, signal?: AbortSignal) {
    for (let attempt = 0; attempt < 2; attempt++) {
        const entries: CatalogEntry[] = [];
        let offset = '0', revision: string | undefined;
        const seen = new Set<string>();
        try {
            for (;;) {
                if (seen.has(offset))
                    throw Error('目录分页未前进');
                seen.add(offset);
                const page = await api.request('ma', 'Catalog', '/catalog', { query: { offset, limit: 100, catalog_revision: revision }, ...(signal ? { signal } : {}) });
                if (revision && revision !== page.catalog_revision)
                    throw Error('目录版本不一致');
                revision = page.catalog_revision;
                entries.push(...page.entries);
                if (!page.next_offset)
                    return entries;
                offset = page.next_offset;
            }
        }
        catch (e) {
            if (attempt === 0 && e instanceof ApiError && e.code === 'CATALOG_REVISION_CONFLICT')
                continue;
            throw e;
        }
    }
    throw Error('目录版本持续变化，请手动重试');
}
export function MAMonitor({ api }: {
    api: V2Client;
}) {
    const [catalog, setCatalog] = useState<CatalogEntry[]>([]), [catalogError, setCatalogError] = useState(''), [catalogBusy, setCatalogBusy] = useState(false), [model, setModel] = useState('');
    const [display, setDisplay] = useState<Display | null>(null), [receipt, setReceipt] = useState<Receipt | null>(null), [rows, setRows] = useState<Record<string, Row>>({}), [selected, setSelected] = useState('');
    const [error, setError] = useState(''), [busy, setBusy] = useState(false), [pending, setPending] = useState(false), [modal, setModal] = useState(false), [intent, setIntent] = useState<Intent | undefined>();
    const [qualityOpen, setQualityOpen] = useState(false), [quality, setQuality] = useState<QualityPage | null>(null), [qualityOffset, setQualityOffset] = useState('0'), [qualityError, setQualityError] = useState('');
    const displayRef = useRef<Display | null>(null);
    displayRef.current = display;
    const records = useRef(new V2Records(api.instance, 'ma')), tracker = useRef<TaskTracker<Receipt, Display> | null>(null), unsubscribe = useRef<() => void>(() => { }), pool = useRef<RequestPool | null>(null), sequence = useRef(0), catalogSequence = useRef(0);
    async function refreshCatalog() { const token = ++catalogSequence.current; setCatalogBusy(true); setCatalogError(''); try {
        const entries = await directory(api);
        if (token === catalogSequence.current)
            setCatalog(entries);
    }
    catch (e) {
        if (token === catalogSequence.current)
            setCatalogError(errorText(e));
    }
    finally {
        if (token === catalogSequence.current)
            setCatalogBusy(false);
    } }
    function follow(r: Receipt) { tracker.current?.stop(); unsubscribe.current(); const current = new TaskTracker<Receipt, Display>(async (signal) => { const value = await api.request('ma', 'Receipt', `/runs/${segment(r.ma_run_id)}`, { signal }); if (value.ma_run_id !== r.ma_run_id)
        throw Error('MA receipt identity mismatch'); return value; }, async (next, signal) => { if (next.ma_run_id !== r.ma_run_id)
        throw Error('MA任务身份不一致'); const entries = await directory(api, signal); const entry = entries.find(x => x.ma_run_id === next.ma_run_id); if (!entry)
        throw Error('任务完成，但发布目录尚不可读；请重试读取结果'); if (entry.model_standard_name !== next.binding.model_standard_name)
        throw Error('MA规格不一致'); return { receipt: next, entry }; }, displayRef.current); tracker.current = current; unsubscribe.current = current.subscribe(() => { const state = current.getSnapshot(); setReceipt(state.receipt); setBusy(state.busy); setError(state.error ?? ''); setPending(state.resultPending); if (state.displayed)
        setDisplay(state.displayed); }); current.start(r); setModal(false); try {
        records.current.remember(r.ma_run_id);
    }
    catch (e) {
        setError(errorText(e));
    } history.replaceState(null, '', `#/ma?run=${encodeURIComponent(r.ma_run_id)}`); }
    async function open(id: string) { const token = ++sequence.current; tracker.current?.stop(); setBusy(true); setError(''); try {
        const r = await api.request('ma', 'Receipt', `/runs/${segment(id)}`);
        if (token === sequence.current) {
            if (r.ma_run_id !== id)
                throw Error('MA任务身份不一致');
            follow(r);
        }
    }
    catch (e) {
        if (token === sequence.current)
            setError(errorText(e));
    }
    finally {
        if (token === sequence.current)
            setBusy(false);
    } }
    async function submit(body: Record<string, string>, previous?: Intent) { const token = ++sequence.current; tracker.current?.stop(); setBusy(true); setError(''); try {
        if (body.pre_file_ref === body.now_file_ref)
            throw Error('pre和now必须是不同文件');
        const a = Date.parse(body.pre_start!), b = Date.parse(body.now_start!), c = Date.parse(body.now_end!);
        if (!Number.isFinite(a) || b - a !== 3600000 || c - b !== 3600000)
            throw Error('请提供UTC时间，pre与now必须分别连续1小时');
        const saved = previous ?? (intent && !intent.runId && Object.entries(body).every(([k, v]) => intent.body[k] === v) ? intent : { key: crypto.randomUUID(), path: '/runs', body: { ...body, source_timezone: 'UTC' } });
        records.current.saveIntent(saved);
        setIntent(saved);
        const r = await api.request('ma', 'Receipt', '/runs', { body: { ...saved.body, submission_key: saved.key } });
        if (token !== sequence.current)
            return;
        const confirmed = { ...saved, runId: r.ma_run_id };
        records.current.saveIntent(confirmed);
        setIntent(confirmed);
        follow(r);
    }
    catch (e) {
        if (token === sequence.current)
            setError(errorText(e));
    }
    finally {
        if (token === sequence.current)
            setBusy(false);
    } }
    async function recover() { if (!intent)
        return; if (intent.runId) {
        await open(intent.runId);
        return;
    } const token = ++sequence.current; setBusy(true); try {
        const r = await api.request('ma', 'Receipt', `/submissions/${segment(intent.key)}`);
        if (token === sequence.current) {
            const confirmed = { ...intent, runId: r.ma_run_id };
            records.current.saveIntent(confirmed);
            setIntent(confirmed);
            follow(r);
        }
    }
    catch (e) {
        if (token === sequence.current)
            setError(`${errorText(e)}；如服务尚未受理，可重试原提交。`);
    }
    finally {
        if (token === sequence.current)
            setBusy(false);
    } }
    function loadRow(id: string, scope: Display, requests: RequestPool) { setRows(old => ({ ...old, [id]: { state: 'loading' } })); requests.run(signal => api.request('ma', 'Snapshot', `/runs/${segment(scope.entry.ma_run_id)}/instances/${segment(id)}`, { signal }), snapshot => { if (snapshot.ma_run_id !== scope.entry.ma_run_id || snapshot.instance.instance_uuid !== id || snapshot.instance.model_standard_name !== scope.entry.model_standard_name) {
        setRows(old => ({ ...old, [id]: { state: 'failed', error: '快照范围不一致' } }));
        return;
    } setRows(old => ({ ...old, [id]: { state: 'ready', snapshot } })); }, e => setRows(old => ({ ...old, [id]: { state: 'failed', error: errorText(e) } }))); }
    useEffect(() => { void refreshCatalog(); const token = sequence.current; void (async () => { try {
        const saved = records.current.read();
        setIntent(saved.intent);
        const url = new URLSearchParams(location.hash.split('?')[1]);
        const run = url.get('run') ?? saved.runs[0] ?? saved.intent?.runId;
        if (saved.displayed && saved.displayed.run !== run) {
            const [old, entries] = await Promise.all([api.request('ma', 'Receipt', `/runs/${segment(saved.displayed.run)}`), directory(api)]);
            const entry = entries.find(x => x.ma_run_id === old.ma_run_id);
            if (token !== sequence.current)
                return;
            if (old.state === 'completed' && entry) {
                const previous = { receipt: old, entry };
                displayRef.current = previous;
                setDisplay(previous);
            }
        }
        if (token === sequence.current && run)
            void open(run);
    }
    catch (e) {
        if (token === sequence.current)
            setError(errorText(e));
    } })(); const visibility = () => { if (document.visibilityState === 'visible' && tracker.current?.getSnapshot().receipt && ['queued', 'running'].includes(tracker.current.getSnapshot().receipt!.state))
        void tracker.current.refresh(); }; document.addEventListener('visibilitychange', visibility); return () => { sequence.current++; catalogSequence.current++; tracker.current?.stop(); unsubscribe.current(); pool.current?.stop(); document.removeEventListener('visibilitychange', visibility); }; }, []);
    useEffect(() => { pool.current?.stop(); if (!display)
        return; try {
        records.current.saveDisplayed(display.entry.ma_run_id);
    }
    catch (e) {
        setError(errorText(e));
    } const requests = new RequestPool(4, api.signal); pool.current = requests; setRows(Object.fromEntries(display.entry.instance_uuids.map(id => [id, { state: 'loading' }]))); setSelected(''); setModel(display.entry.model_standard_name); setQualityOffset('0'); setQuality(null); setQualityOpen(false); for (const id of display.entry.instance_uuids)
        loadRow(id, display, requests); return () => requests.stop(); }, [display]);
    useEffect(() => { if (!qualityOpen || !display)
        return; let live = true; const c = new AbortController(); setQuality(null); setQualityError(''); void api.request('ma', 'QualityPage', `/runs/${segment(display.entry.ma_run_id)}/quality`, { signal: c.signal, query: { offset: qualityOffset, limit: 20 } }).then(v => { if (live) {
        if (v.ma_run_id !== display.entry.ma_run_id)
            throw Error('质量报告范围不一致');
        setQuality(v);
    } }).catch(e => { if (live)
        setQualityError(errorText(e)); }); return () => { live = false; c.abort(); }; }, [api, display, qualityOpen, qualityOffset]);
    const snapshot = rows[selected]?.snapshot;
    return <><div className="page-head"><div><h1>MA集群 Token 监控</h1><p>按模型规格 × 实例UUID，查看真实表现与同范围复用潜力</p></div><button className="primary" onClick={() => setModal(true)}>新建MA分析</button></div>{receipt && <section className="v2-task"><span>任务 {receipt.ma_run_id} · {stateLabel(receipt.state)}</span><span>处理中每1分钟更新</span><button disabled={busy} onClick={() => void tracker.current?.refresh()}>刷新状态</button>{display && receipt.ma_run_id !== display.entry.ma_run_id && <small>下方仍为历史分析 {display.entry.ma_run_id}</small>}</section>}{error && <p role="alert" className="notice">{pending ? '新任务完成，结果读取失败；历史分析保持。' : ''}{error}</p>}{intent && !intent.runId && <div className="toolbar"><button disabled={busy} onClick={() => void recover()}>查找原提交</button><button disabled={busy} onClick={() => void submit(intent.body, intent)}>重试原提交</button></div>}
 <section className="filter-panel"><div className="filter-main"><label className="filter-field">模型规格<select aria-label="MA模型规格" value={model} onChange={e => { setModel(e.target.value); pool.current?.stop(); const entry = catalog.find(x => !e.target.value || x.model_standard_name === e.target.value); if (entry)
        void open(entry.ma_run_id);
    else {
        tracker.current?.stop();
        setDisplay(null);
        setReceipt(null);
    } }}><option value="">全部规格</option>{[...new Set([...catalog.map(x => x.model_standard_name), ...(display ? [display.entry.model_standard_name] : [])])].map(x => <option key={x}>{x}</option>)}</select></label><label className="filter-field">历史结果<select aria-label="MA历史结果" value={display?.entry.ma_run_id ?? ''} onChange={e => e.target.value && void open(e.target.value)}><option value="">选择已完成结果</option>{display && !catalog.some(x => x.ma_run_id === display.entry.ma_run_id) && <option value={display.entry.ma_run_id}>{maTime(display.entry.now_start)} — {maTime(display.entry.now_end)} · {display.entry.ma_run_id}</option>}{catalog.filter(x => !model || x.model_standard_name === model).map(x => <option key={x.ma_run_id} value={x.ma_run_id}>{maTime(x.now_start)} — {maTime(x.now_end)} · {x.ma_run_id}</option>)}</select></label><button disabled={catalogBusy} onClick={() => void refreshCatalog()}>刷新目录</button></div><div className="filter-meta"><span>GF · 同UUID跨租户共享</span><span>展示规格 {display?.entry.model_standard_name ?? '—'} · {display?.entry.ma_run_id ?? '—'}</span></div></section>{catalogError && <p role="alert">{catalogError}</p>}<details className="v2-pad"><summary>按已知运行ID打开</summary><form onSubmit={e => { e.preventDefault(); void open(fields(e.currentTarget).ma_run_id!); }}><input aria-label="MA运行ID" name="ma_run_id" required/><button disabled={busy}>打开MA运行</button></form></details>
 {display ? <><section className="panel ma-summary"><div><span className="mini-label">本次运行的MA实例</span><strong>{display.entry.instance_uuids.length} UUID</strong></div><div><span className="mini-label">当前统计时长</span><strong>1 小时 · now</strong></div><div><span className="mini-label">预热时长</span><strong>1 小时 · pre</strong></div><div className="summary-end">pre从空缓存预热，仅统计now<br />条件式对照，不假设理想≥真实</div></section><section className="panel"><div className="panel-head"><h2>实例概览</h2><span>逐实例读取 · 失败可单独重试</span></div><div className="table-wrap"><table className="ma-table"><thead><tr><th>实例UUID</th><th>配对命中率</th><th>窗口请求数</th><th>整小时req/s</th><th>整小时重算Token/s</th><th>实际重算Token</th><th>对照覆盖 / 条件</th><th>操作</th></tr></thead><tbody>{display.entry.instance_uuids.map(id => { const row = rows[id], i = row?.snapshot?.instance; return <tr key={id} className={selected === id ? 'active-row' : ''}><td><span className="uuid">{id}</span></td>{i ? <><td><div className="hit-pair">{[['理想', i.paired_ideal.hit_rate], ['真实', i.paired_real.hit_rate]].map(([label, value]) => <div key={label as string} className={`hit-line ${label === '真实' ? 'actual' : ''}`}><span>{label}</span><span className="hit-track"><i style={{ width: typeof value === 'number' ? `${value * 100}%` : '0%' }}/></span><b>{percent(typeof value === 'number' ? value : null)}</b></div>)}</div></td><td>{i.coverage.assigned}</td><td>{rate(i.hour.requests_per_second)}</td><td>{rate(i.hour.uncached_tokens_per_second)}</td><td>{i.real.sample_count === '0' ? '—' : i.real.totals.uncached_tokens}</td><td>Q {percent(i.paired_request_coverage)}<small className="cell-sub">R {percent(i.paired_input_coverage)}</small><span className="pill">{idealLabel(i.ideal_status)}{i.mismatched_input_count !== '0' ? ' · 输入计量不一致' : ''}</span></td><td><button onClick={() => setSelected(selected === id ? '' : id)}>查看画像</button></td></> : <td colSpan={7}>{row?.state === 'failed' ? <><span role="alert">{row.error}</span><button onClick={() => pool.current && loadRow(id, display, pool.current)}>重试此行</button></> : <span role="status">正在加载…</span>}</td>}</tr>; })}</tbody></table></div>{!display.entry.instance_uuids.length && <p className="v2-pad">空范围：{display.entry.empty_scope_reason ?? '无实例'}。不虚构UUID，也不等于生产零流量。</p>}</section>{snapshot && <MACharts key={`${display.entry.ma_run_id}/${selected}`} snapshot={snapshot}/>}<section className="panel v2-pad"><button onClick={() => setQualityOpen(v => !v)}>运行质量记录</button><p className="muted">整次运行pre/now质量记录，不按当前UUID过滤。</p>{qualityOpen && (qualityError ? <p role="alert">{qualityError}<button onClick={() => { setQualityOpen(false); }}>关闭后重试</button></p> : quality ? <><p>共 {quality.total} 条记录</p><div className="table-wrap"><table><thead><tr><th>文件</th><th>源记录</th><th>物理行</th><th>字段</th><th>原因</th></tr></thead><tbody>{quality.issues.map((q, j) => <tr key={j}><td>{q.role}</td><td>{q.source_record_index}</td><td>{q.physical_line_start}–{q.physical_line_end}</td><td>{q.field}</td><td>{q.code}</td></tr>)}</tbody></table></div><button disabled={qualityOffset === '0'} onClick={() => setQualityOffset((BigInt(qualityOffset) > 20n ? BigInt(qualityOffset) - 20n : 0n).toString())}>上一页</button><button disabled={!quality.next_offset} onClick={() => quality.next_offset && setQualityOffset(quality.next_offset)}>下一页</button></> : <p role="status">读取质量记录…</p>)}</section></> : <section className="panel v2-pad"><h2>尚未选择MA分析</h2><p>从历史目录打开结果，或新建两份文件的连续小时分析。排队/运行中的任务不会出现在完成目录。</p></section>}
 {modal && <Modal title="新建MA分析" close={() => setModal(false)}><form className="v2-form" onSubmit={e => { e.preventDefault(); void submit(fields(e.currentTarget)); }}>{[['pre_file_ref', 'pre文件引用'], ['now_file_ref', 'now文件引用'], ['model_standard_name', '模型规格'], ['pre_start', 'pre开始 UTC（ISO 8601，以Z结尾）'], ['now_start', 'now开始 UTC（ISO 8601，以Z结尾）'], ['now_end', 'now结束 UTC（ISO 8601，以Z结尾）']].map(([name, label]) => <label key={name}>{label}<input name={name} required pattern={name?.endsWith('start') || name?.endsWith('end') ? '.*Z' : undefined}/></label>)}<label>编码模型<select name="model_id">{models.map(m => <option key={m}>{m}</option>)}</select></label><p>使用受控输入目录内两个不同CSV。pre与now各1小时，前后连续；此处不采集或上传文件。</p><button className="primary" disabled={busy}>提交MA分析</button>{error && <p role="alert">{error}</p>}</form></Modal>}</>;
}

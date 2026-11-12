import { AppShell } from '../../components/AppShell';
import { nanos, statusLabel } from './format';
import { useEffect, useState, useRef } from 'react';
import { arr, obj, str, text } from '../../api/analysis/client';
import type { Catalog, Obj, AnalysisClient } from '../../api/analysis/client';
import { readRoute, navigate } from './navigation';
import './analysis.css';
import { SourceLink } from './SourceLink';
import { ReportCache } from '../../storage/analysis-cache';
import { readAnalysisMetadata as readMetadata, saveAnalysisMetadata } from '../../state/analysis-metadata';
import { analysisReportKey } from '../../state/analysis-cache-key';
import { DiscoverySession } from '../../state/analysis-discovery';
import { loadReport, moreReport } from './model';
import { ExecutionStatus } from './ExecutionStatus';
import type { LoadedReport } from './model';
import { ReportCards, ReportDetail, DetectorHelp } from './Reports';
export function completed(entry: Obj) { if (entry.sample_v3) return '样本报告 · ' + str(entry.task_id).slice(-8); return entry.analysis_completed_at ? new Date(str(entry.analysis_completed_at)).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false }) + ' · 北京时间' : '完成时间未提供'; }
export function windowText(entry: Obj) { const scope = obj(entry.scope); if (entry.sample_v3) return `样本 ${str(entry.selected_count)} / ${str(scope.request_count)} 条`; return scope.window ? `${nanos(obj(scope.window).start_ns)} — ${nanos(obj(scope.window).end_ns)} · 北京时间` : '原报告选定范围'; }
export function AnalysisApp() {
    const [route, setRoute] = useState(readRoute);
    const [api, setApi] = useState<AnalysisClient | null>(null), [catalog, setCatalog] = useState<Catalog | null>(null);
    const [loaded, setLoaded] = useState<LoadedReport | null>(null), [loading, setLoading] = useState(false), [readError, setReadError] = useState(''), [readRetry, setReadRetry] = useState(0);
    const [pageLoading, setPageLoading] = useState(false), [pageError, setPageError] = useState('');
    const pageRequest = useRef<AbortController | null>(null);
    const cache = useRef(new ReportCache());
    const apiRef = useRef<AnalysisClient | null>(null);
    const [returnNotice,setReturnNotice]=useState('');
    const [connection, setConnection] = useState('正在核对报告目录');
    const [error, setError] = useState(''), [retry, setRetry] = useState(0);
    useEffect(() => { const changed = () => setRoute(readRoute()); window.addEventListener('hashchange', changed); return () => window.removeEventListener('hashchange', changed); }, []);
    useEffect(() => { let session: DiscoverySession | null = null; const start = () => { session?.stop(); if (document.hidden) {
        setConnection('页面已隐藏，返回时对齐目录');
        return;
    } session = new DiscoverySession({ catalog: (client, cat) => { if (apiRef.current?.instance !== client.instance || apiRef.current?.executionVersion !== client.executionVersion) {
            apiRef.current = client;
            setApi(client);
            setLoaded(null);
            cache.current.clear();
        } setCatalog(cat); saveAnalysisMetadata(client, cat); setError(''); }, status: setConnection, terminal: () => { /* Analysis publication is reconciled through the catalog. */ } }, undefined, true); void session.run(); }; start(); document.addEventListener('visibilitychange', start); return () => { session?.stop(); document.removeEventListener('visibilitychange', start); }; }, [retry]);
    const bindings = [...new Map((catalog?.items ?? []).map(x => [str(x.binding_id), obj(x.binding)])).entries()];
    const requestedTask = catalog?.items.find(x => x.task_id === route.task && arr(x.directions).includes(route.direction));
    const directionDefault = (catalog?.selected_reports ?? catalog?.defaults)?.find(x => x.direction === route.direction);
    const directionEntry = catalog?.items.find(x => arr(x.directions).includes(route.direction));
    const binding = route.binding || (requestedTask ? str(requestedTask.binding_id) : directionDefault ? str(directionDefault.binding_id) : directionEntry ? str(directionEntry.binding_id) : bindings[0]?.[0] || '');
    const selectedBinding = bindings.find(x => x[0] === binding)?.[1];
    const apps = [...new Set(bindings.map(x => str(x[1].appid)))];
    const entries = (catalog?.items ?? []).filter(x => x.binding_id === binding && arr(x.directions).includes(route.direction));
    const defaultTask = (catalog?.selected_reports ?? catalog?.defaults)?.find(x => x.binding_id === binding && x.direction === route.direction)?.task_id;
    const target = entries.find(x => x.task_id === (route.task || defaultTask));
    const targetKey = api && target ? analysisReportKey(api, target, route.direction) : '';
    useEffect(() => {
        const c = new AbortController();
        pageRequest.current?.abort(); setPageLoading(false); setPageError(''); setReadError('');
        if (!api || !target) { setLoaded(null); setLoading(false); return; }
        setLoading(true);
        const cached = cache.current.get(targetKey);
        void (cached ? Promise.resolve(cached) : loadReport(api, target, route.direction, c.signal)).then(data => {
            if (!c.signal.aborted) { cache.current.put(targetKey, data); setLoaded(data); }
        }).catch(e => { if (!c.signal.aborted) setReadError(String(e)); })
            .finally(() => { if (!c.signal.aborted) setLoading(false); });
        return () => { c.abort(); pageRequest.current?.abort(); };
    }, [api, targetKey, route.direction, readRetry]);
    const shown = loaded && loaded.entry.binding_id === binding && loaded.direction === route.direction ? loaded : null;
    const selected = shown?.entry;
    const open = (id: string) => { setReturnNotice('');history.replaceState({ ...history.state, analysisReturn: { instance: api?.instance, binding, direction: route.direction, task: shown?.entry.task_id, id, scroll: window.scrollY } }, ''); navigate({ binding, direction: route.direction, mode: route.mode, task: str(shown!.entry.task_id), item: id }); };
    const back = () => { navigate({ binding, direction: route.direction, mode: 'history', task: str(shown!.entry.task_id), item: '' }); };
    const more = async () => {
        if (!api || !shown || pageLoading) return;
        const c = new AbortController(); pageRequest.current?.abort(); pageRequest.current = c;
        setPageLoading(true); setPageError('');
        try {
            const next = await moreReport(api, shown, c.signal);
            if (c.signal.aborted) return;
            cache.current.put(analysisReportKey(api, shown.entry, shown.direction), next);
            setLoaded(old => old === shown ? next : old);
        } catch (e) { if (!c.signal.aborted) setPageError(String(e)); }
        finally { if (!c.signal.aborted) setPageLoading(false); }
    };
    useEffect(() => { if (route.item || !shown)
        return; const r = history.state?.analysisReturn; if (!r || r.instance !== api?.instance || r.binding !== binding || r.direction !== route.direction || r.task !== shown.entry.task_id)
        return; const frame = requestAnimationFrame(() => { const el = document.getElementById('analysis-card-' + encodeURIComponent(r.id)); if (el) {
        window.scrollTo(0, typeof r.scroll === 'number' ? r.scroll : 0);
        el.querySelector('button')?.focus({ preventScroll: true });
    }
    else { window.scrollTo(0,0);setReturnNotice('原卡片页已回收，已返回同一报告顶部，可继续加载报告内容。'); }
        history.replaceState({ ...history.state, analysisReturn: undefined }, '');
    }); return () => cancelAnimationFrame(frame); }, [route.item, route.direction, binding, api, shown]);
    const changeBinding = (id: string) => { setReturnNotice(''); navigate({ binding: id, direction: route.direction, mode: 'latest', task: '', item: '' }); };
    const changeDirection = (direction: typeof route.direction) => {
        setReturnNotice('');
        const sameReport = route.task && catalog?.items.some(x => x.task_id === route.task && x.binding_id === binding && arr(x.directions).includes(direction));
        navigate({ binding, direction, mode: sameReport ? 'history' : 'latest', task: sameReport ? route.task : '', item: '' });
    };
    const retryReport = () => { if (targetKey) cache.current.delete(targetKey); setReadRetry(x => x + 1); };
    const returnToDirectory = () => navigate({ binding: '', direction: route.direction, mode: 'latest', task: '', item: '' });
    return <AppShell page="analysis" variant="analysis"><main id="analysis-main"><div id="reportPage"><div className="page-head"><div><h1>业务优化建议</h1><p>先看影响范围与预期变化，再看证据与具体改法</p></div><a className="btn" href="#/users">返回监控</a></div>{error && <div role="alert" className="analysis-error">{error}<button onClick={() => setRetry(x => x + 1)}>重新读取</button></div>}{!catalog && !error && <p role="status">正在核对报告目录…</p>}<p role="status" className="analysis-status connection-status">{connection} <button onClick={() => setRetry(x => x + 1)}>重新连接</button></p>{!catalog && readMetadata().length > 0 && <details className="report-detail"><summary>离线查看已缓存报告目录 · 尚未核对服务身份</summary>{readMetadata().map(x => <p key={x.instance + x.task}>{x.appid} · {x.model} · {x.completed ?? '完成时间未提供'} · {x.status}（仅缓存元数据，连接后读取内容）</p>)}</details>}<section className="report-filters business-scope"><label>业务应用 · APPID<select aria-label="业务应用" value={selectedBinding ? str(selectedBinding.appid) : ''} onChange={e => changeBinding(bindings.find(x => x[1].appid === e.target.value)?.[0] ?? '')}><option value="" disabled>选择有历史报告的应用</option>{apps.map(x => <option key={x}>{x}</option>)}</select></label><label>当前应用使用的模型<select aria-label="模型服务" value={binding} onChange={e => changeBinding(e.target.value)}>{bindings.filter(x => x[1].appid === selectedBinding?.appid).map(([id, b]) => <option key={id} value={id}>{text(b.model_id)}{b.common_name ? ` · ${text(b.common_name)}` : ''}</option>)}</select></label><div className="scope-window"><small>报告范围</small><strong>{selected ? windowText(selected) : '请选择报告'}</strong><small>{selected?.sample_v3 ? '报告标识' : '分析时间'}：{selected ? completed(selected) : '未提供'}</small></div></section><div className="business-tabs" role="group" aria-label="分析类别">{(['low_hit', 'token_content'] as const).map(d => <button key={d} className={route.direction === d ? 'active' : ''} aria-pressed={route.direction === d} onClick={() => changeDirection(d)}>{d === 'low_hit' ? '低命中率分析' : 'Token异常分析'}</button>)}</div><div className="analysis-history"><label>报告 <select aria-label="历史报告" value={selected ? str(selected.task_id) : ''} onChange={e => navigate({ binding, direction: route.direction, mode: 'history', task: e.target.value, item: '' })}><option value="" disabled>请选择历史报告</option>{entries.map(x => <option key={str(x.task_id)} value={str(x.task_id)}>{completed(x)} · {statusLabel[str(x.status)] ?? text(x.status)} · {windowText(x)}</option>)}</select></label>{route.mode === 'history' && <span>查看历史报告</span>}<button disabled={!defaultTask} onClick={() => navigate({ binding, direction: route.direction, mode: 'latest', task: '', item: '' })}>查看最新</button></div><DetectorHelp direction={route.direction}/>{!!defaultTask && !!route.task && defaultTask !== route.task && <p className="notice">有新报告可查看；当前阅读位置已保留。<button onClick={() => navigate({ binding, direction: route.direction, mode: 'latest', task: '', item: '' })}>查看最新</button></p>}<div id="businessContent">{returnNotice&&!route.item&&<p className="notice">{returnNotice}</p>}{readError && <p role="alert">{shown ? '目标读取失败，保留原报告：' : '报告读取失败：'}{readError}<button onClick={retryReport}>重新读取</button></p>}{pageError && <p role="alert">后续内容读取失败，已读内容保留。<button disabled={pageLoading} onClick={() => void more()}>重新读取后续内容</button></p>}{loading && <p role="status">正在读取报告…</p>}{shown && api ? <>{shown.entry.status !== 'ready' && <p className="notice">当前为 {statusLabel[str(shown.entry.status)]??text(shown.entry.status)}，请注意未完成或空范围限制。</p>}<ExecutionStatus data={shown}/>{!shown.execution && arr(shown.report.stages).map(obj).some(x=>x.status!=='completed'||x.candidate_coverage_partial===true)&&<p className="notice">本报告有部分检查未完成，当前仅展示已保存的结果。</p>}{route.item && shown.entry.task_id===route.task ? <ReportDetail api={api} data={shown} id={route.item} back={back}/> : <ReportCards api={api} data={shown} open={open} more={() => void more()} loading={loading || pageLoading}/>}</> : !loading && catalog && <div className="panel analysis-empty">{route.binding && !selectedBinding ? <>原报告链接不属于当前报告目录。<button onClick={returnToDirectory}>返回报告目录</button></> : route.task && !target ? <>指定历史报告不存在或已清理。<button onClick={returnToDirectory}>返回报告目录</button></> : entries.length ? '当前没有默认完整报告，请选择历史报告。' : `当前${selectedBinding ? '应用' : '目录'}暂无${route.direction === 'low_hit' ? '低命中率' : 'Token异常'}分析报告。`}</div>}</div>{shown && api && <SourceLink key={api.instance + ':' + str(shown.entry.task_id)} entry={shown.entry}/>}<p className="report-footer">浏览报告不会运行分析 · 单项收益不可相加</p></div></main></AppShell>;
}

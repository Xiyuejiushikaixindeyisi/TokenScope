import { useEffect, useRef, useState } from 'react';
import { segment } from '../../api/v2/client';
import type { V2Client } from '../../api/v2/client';
import type { Receipt, Ranking as RankingDto } from '../../api/v2/generated/user';
import { getJson, ApiError } from '../../api/client';
import type { Dto } from '../../api/types';
import { TaskTracker } from '../../state/v2-task';
import { V2Records } from '../../storage/v2-records';
import type { Intent } from '../../storage/v2-records';
import { Overview } from '../overview/Overview';
import { Distributions } from '../distributions/Distributions';
import type { BinSelection } from '../distributions/Distributions';
import { Requests } from '../requests/Requests';
import { Exports } from '../exports/Exports';
import { Signals } from '../signals/Signals';
import { formatBeijing } from '../../domain/time';
import { Modal, models, fields, errorText, stateLabel } from './common';
import { Ranking } from './Ranking';
import { TTFT } from './TTFT';
import { discoverUsers, entryKey, modelScopeKey, monitorSourceUrl, type DiscoveryEntry } from './user-discovery';
export interface UserDisplay {
    receipt: Receipt;
    ranking: RankingDto | null;
    snapshot: Dto<'ViewSnapshot'> | null;
}
export function UserMonitor({ api, page }: {
    api: V2Client;
    page: string;
}) {
    const [display, setDisplay] = useState<UserDisplay | null>(null), [receipt, setReceipt] = useState<Receipt | null>(null);
    const [directory, setDirectory] = useState<DiscoveryEntry[]>([]), [directoryError, setDirectoryError] = useState(''), [directoryBusy, setDirectoryBusy] = useState(false);
    const directoryRequest = useRef<AbortController | null>(null);
    const fixed = useRef<Record<string, string>>({});
    const fixedKey = `tokenscope.v2.fixed:${api.instance}`;
    const [error, setError] = useState(''), [warning, setWarning] = useState(''), [busy, setBusy] = useState(false), [resultPending, setResultPending] = useState(false);
    const [modal, setModal] = useState(false), [mode, setMode] = useState('open'), [recent, setRecent] = useState<string[]>([]), [intent, setIntent] = useState<Intent | undefined>();
    const [filter, setFilter] = useState<BinSelection | null>(null), [appid, setAppid] = useState('');
    const tracker = useRef<TaskTracker<Receipt, UserDisplay> | null>(null), unsubscribe = useRef<() => void>(() => { }), sequence = useRef(0);
    const store = useRef(new V2Records(api.instance, 'user'));
    const displayedRef = useRef<UserDisplay | null>(null);
    displayedRef.current = display;
    const stop = () => { sequence.current++; tracker.current?.stop(); unsubscribe.current(); };
    async function chooseEntry(entry: DiscoveryEntry, closeDialog = true) {
        fixed.current[modelScopeKey(entry)] = entryKey(entry);
        try { localStorage.setItem(fixedKey, JSON.stringify(fixed.current)); } catch { /* Selection still held for this session. */ }
        await open(entry.source.user_run_id, entry.appid ?? undefined, entry.source.index_revision, entry, closeDialog);
    }
    function chooseModel(entries: DiscoveryEntry[], closeDialog = true) {
        const first = entries[0];
        if (!first) { setError('此APPID没有已发布模型结果'); return; }
        const key = fixed.current[modelScopeKey(first)];
        const target = key ? entries.find(e => entryKey(e) === key) : entries.find(e => e.is_default);
        if (!target) { setError('固定历史运行已不可读；请显式选择其他历史，不自动换成最新结果'); return; }
        void chooseEntry(target, closeDialog);
    }
    async function refreshDirectory(initial = false) {
        directoryRequest.current?.abort();
        const controller = new AbortController(); directoryRequest.current = controller;
        const selection = sequence.current;
        setDirectoryBusy(true); setDirectoryError('');
        try {
            const entries = await discoverUsers(api, controller.signal);
            if (controller.signal.aborted || directoryRequest.current !== controller) return;
            setDirectory(entries);
            const q = new URLSearchParams(location.hash.split('?')[1]);
            if (initial && !q.get('run') && !displayedRef.current && selection === sequence.current) {
                const app = q.get('appid');
                const first = entries.find(e => e.appid !== null && (!app || e.appid === app) && e.is_default);
                if (first) chooseModel(entries.filter(e => modelScopeKey(e) === modelScopeKey(first)), false);
                else if (app) setDirectoryError('此APPID没有已发布结果（不等同于生产零流量）');
            }
        } catch (e) { if (!controller.signal.aborted) { setDirectory([]); setDirectoryError(errorText(e)); } }
        finally { if (directoryRequest.current === controller) setDirectoryBusy(false); }
    }
    const persist = (fn: () => void) => { try {
        fn();
        setRecent(store.current.read().runs);
    }
    catch (e) {
        setWarning(errorText(e));
    } };
    async function load(r: Receipt, signal: AbortSignal, requestedApp?: string): Promise<UserDisplay> {
        if (r.state === 'empty')
            return { receipt: r, ranking: null, snapshot: null };
        const ranking = await api.request('user', 'Ranking', `/runs/${segment(r.user_run_id)}/rankings`, { query: { limit: 1000, index_revision: r.index_revision ?? undefined }, signal });
        if (ranking.user_run_id !== r.user_run_id || ranking.index_revision !== r.index_revision || ranking.common_name !== r.common_name) throw Error('用户运行或索引版本不一致');
        const selected = requestedApp || ranking.rows[0]?.appid;
        if (!r.base_run_id || !selected)
            return { receipt: r, ranking, snapshot: null };
        const snapshot = await getJson('ViewSnapshot', `/analysis-runs/${segment(r.base_run_id)}/view-snapshot`, { appid: selected }, { instanceId: api.instance, signal });
        if (snapshot.identity.run_id !== r.base_run_id || snapshot.identity.appid !== selected || snapshot.identity.model_id !== r.model_id)
            throw Error('基础结果身份不一致');
        return { receipt: r, ranking, snapshot };
    }
    function follow(r: Receipt, requestedApp?: string) {
        stop();
        setError('');
        setFilter(null);
        setReceipt(r);
        persist(() => store.current.remember(r.user_run_id));
        const next = new TaskTracker<Receipt, UserDisplay>(async (signal) => { const value = await api.request('user', 'Receipt', `/runs/${segment(r.user_run_id)}`, { signal }); if (value.user_run_id !== r.user_run_id)
            throw Error('任务身份不一致'); return value; }, (value, signal) => { if (r.index_revision && value.index_revision !== r.index_revision) throw Error('固定历史索引版本已变化；未自动替换结果'); return load(value, signal, requestedApp); }, displayedRef.current);
        tracker.current = next;
        unsubscribe.current = next.subscribe(() => { const state = next.getSnapshot(); setReceipt(state.receipt); setError(state.error ?? ''); setBusy(state.busy); setResultPending(state.resultPending); if (state.displayed) {
            setDisplay(state.displayed);
            setAppid(state.displayed.snapshot?.identity.appid ?? '');
        } });
        next.start(r);
        const q = new URLSearchParams({ run: r.user_run_id, ...(r.index_revision ? { revision: r.index_revision } : {}), ...(requestedApp ? { appid: requestedApp } : {}) });
        const view = location.hash.split('?')[0] === '#/users/ranking' ? 'users/ranking' : 'users';
        history.replaceState(null, '', `#/${view}?${q}`);
    }
    async function open(run: string, requestedApp?: string, revision?: string, entry?: DiscoveryEntry, closeDialog = true) {
        stop();
        const token = sequence.current;
        setBusy(true);
        setError('');
        try {
            const r = await api.request('user', 'Receipt', `/runs/${segment(run)}`);
            if (token !== sequence.current)
                return;
            if (revision && r.index_revision !== revision) throw Error('固定历史索引版本已变化，请重新选择；未自动读取新版本');
            if (entry && (r.base_run_id !== entry.source.base_run_id || r.model_id !== entry.source.model_id || r.common_name !== entry.source.common_name)) throw Error('目录与运行来源身份不一致');
            follow(r, requestedApp);
            // Background restoration does not own a form opened by the user.
            if (closeDialog) setModal(false);
        }
        catch (e) {
            if (token === sequence.current)
                setError(errorText(e));
        }
        finally {
            if (token === sequence.current)
                setBusy(false);
        }
    }
    async function submit(path: string, body: Record<string, string>, recovery?: Intent) {
        stop();
        const token = sequence.current;
        setBusy(true);
        setError('');
        const saved = recovery ?? (intent && !intent.runId && intent.path === path && Object.entries(body).every(([k, v]) => intent.body[k] === v) ? intent : { key: crypto.randomUUID(), path, body });
        const complete = { ...saved, body: { ...saved.body, submission_key: saved.key } };
        setIntent(complete);
        persist(() => store.current.saveIntent(complete));
        try {
            const r = await api.request('user', 'Receipt', path, { body: complete.body });
            if (token !== sequence.current)
                return;
            const updated = { ...complete, runId: r.user_run_id };
            setIntent(updated);
            persist(() => store.current.saveIntent(updated));
            follow(r);
            setModal(false);
        }
        catch (e) {
            if (token === sequence.current)
                setError(e instanceof ApiError && e.status >= 400 && e.status < 500 ? `提交未受理：${errorText(e)}。请核对输入后再提交。` : `提交结果待确认：${errorText(e)}。可重试原提交以恢复同一任务。`);
        }
        finally {
            if (token === sequence.current)
                setBusy(false);
        }
    }
    useEffect(() => {
        try { const raw: unknown = JSON.parse(localStorage.getItem(fixedKey) ?? '{}'); fixed.current = raw && typeof raw === 'object' && !Array.isArray(raw) ? Object.fromEntries(Object.entries(raw).filter(([, v]) => typeof v === 'string')) : {}; } catch { fixed.current = {}; }
        void refreshDirectory(true);
        const token = sequence.current;
        const controller = new AbortController();
        void (async () => { try {
            const saved = store.current.read();
            setRecent(saved.runs);
            setIntent(saved.intent);
            const q = new URLSearchParams(location.hash.split('?')[1]);
            const id = q.get('run') ?? undefined;
            if (id && saved.displayed && saved.displayed.run !== id) {
                try {
                    const r = await api.request('user', 'Receipt', `/runs/${segment(saved.displayed.run)}`, { signal: controller.signal });
                    if (['ready', 'empty'].includes(r.state)) {
                        const previous = await load(r, controller.signal, saved.displayed.appid);
                        if (token !== sequence.current)
                            return;
                        displayedRef.current = previous;
                        setDisplay(previous);
                        setAppid(previous.snapshot?.identity.appid ?? '');
                    }
                }
                catch (e) {
                    if (!controller.signal.aborted)
                        setWarning(`历史结果恢复失败：${errorText(e)}`);
                }
            }
            if (token === sequence.current && id)
                void open(id, q.get('appid') ?? undefined, q.get('revision') ?? undefined, undefined, false);
        }
        catch (e) {
            if (token === sequence.current)
                setWarning(errorText(e));
        } })();
        const visible = () => { if (!document.hidden && tracker.current) {
            const r = tracker.current.getSnapshot().receipt;
            if (r && !['ready', 'empty', 'failed', 'interrupted'].includes(r.state))
                void tracker.current.refresh();
        } };
        document.addEventListener('visibilitychange', visible);
        return () => { controller.abort(); directoryRequest.current?.abort(); stop(); document.removeEventListener('visibilitychange', visible); };
        // Component is keyed by service identity; callbacks always belong to that service.
    }, []);
    useEffect(() => { if (display) {
        persist(() => store.current.saveDisplayed(display.receipt.user_run_id, display.snapshot?.identity.appid));
        const r = display.receipt, app = display.snapshot?.identity.appid;
        if (app && r.index_revision) {
            fixed.current[JSON.stringify([app, r.model_id, r.common_name])] = JSON.stringify([r.user_run_id, app, r.index_revision]);
            try { localStorage.setItem(fixedKey, JSON.stringify(fixed.current)); } catch { /* optional persistence */ }
            const q = new URLSearchParams(location.hash.split('?')[1]);
            if (q.get('run') === r.user_run_id) { q.set('revision', r.index_revision); q.set('appid', app); history.replaceState(null, '', `${location.hash.split('?')[0]}?${q}`); }
        }
        setFilter(null);
    } }, [display?.receipt.user_run_id, display?.snapshot?.identity.appid]);
    async function selectApp(next: string) {
        const scope = receipt?.state === 'indexing' ? receipt : display?.receipt;
        if (!scope?.base_run_id || !next)
            return;
        tracker.current?.stop();
        const token = ++sequence.current;
        setBusy(true);
        setError('');
        setFilter(null);
        try {
            const snapshot = await getJson('ViewSnapshot', `/analysis-runs/${segment(scope.base_run_id)}/view-snapshot`, { appid: next }, { instanceId: api.instance });
            if (token === sequence.current) {
                const updated = { receipt: scope, ranking: display?.receipt.user_run_id === scope.user_run_id ? display.ranking : null, snapshot };
                displayedRef.current = updated;
                setDisplay(updated);
                setAppid(next);
                if (receipt)
                    follow(receipt, next);
                history.replaceState(null, '', `#/users?${new URLSearchParams({ run: scope.user_run_id, appid: next, ...(scope.index_revision ? { revision: scope.index_revision } : {}) })}`);
            }
        }
        catch (e) {
            if (token === sequence.current)
                setError(errorText(e));
        }
        finally {
            if (token === sequence.current)
                setBusy(false);
        }
    }
    const snapshot = display?.snapshot;
    const selectedEntry = directory.find(e => e.source.user_run_id === display?.receipt.user_run_id && e.appid === appid && e.source.index_revision === display?.receipt.index_revision);
    const appEntries = directory.filter(e => e.appid === appid);
    const modelEntries = [...new Map(appEntries.map(e => [modelScopeKey(e), e])).values()];
    const apps = [...new Set([...directory.flatMap(e => e.appid === null ? [] : [e.appid]), ...(display?.ranking?.rows.map(e => e.appid) ?? []), ...(appid ? [appid] : [])])];

    return <><div hidden={page === 'users/ranking'}>
    <div className="page-head"><div><h1>用户 Token 监控</h1><p>按 appid × 模型服务，查看用量、复用潜力与长度分布</p></div><div className="actions"><a className="btn" href={`#/settings${snapshot ? '?' + new URLSearchParams({appid:snapshot.identity.appid,model:snapshot.identity.model_id,run:snapshot.identity.run_id}) : ''}`}>运行设置</a>{snapshot && page !== 'users/ranking' && <details className="action-menu"><summary className="btn">导出</summary><div className="popover"><Exports key={display.receipt.user_run_id} snapshot={snapshot}/></div></details>}<button onClick={() => { setMode('open'); setModal(true); }}>打开运行</button><button className="primary" onClick={() => { setMode('new'); setModal(true); }}>新建分析</button></div></div>
    {directoryError && <p role="alert">目录读取失败或无匹配：{directoryError}</p>}{warning && <p className="notice">{warning}（本机记录不可用时仍可用运行ID打开）</p>}
    {receipt && <section className="v2-task" aria-label="任务状态"><span>任务 {receipt.user_run_id} · {stateLabel(receipt.state)}</span><span>处理中每1分钟更新</span><button disabled={busy} onClick={() => void tracker.current?.refresh()}>刷新状态</button>{display && display.receipt.user_run_id !== receipt.user_run_id && <small>下方仍为历史分析 {display.receipt.user_run_id}</small>}</section>}
    {error && <p role="alert" className="notice">{resultPending ? '新分析已完成，结果加载失败；历史分析保持。' : ''}{error}</p>}
    {intent && !intent.runId && <button disabled={busy} onClick={() => void submit(intent.path, intent.body, intent)}>重试原提交</button>}
    <section className="filter-panel"><div className="filter-main"><div><span className="field-caption">模型服务 · common_name</span><select aria-label="用户模型服务" value={selectedEntry ? modelScopeKey(selectedEntry) : ""} onChange={e => chooseModel(appEntries.filter(x => modelScopeKey(x) === e.target.value))}><option value="">{display?.receipt.common_name ?? "请选择模型"}</option>{modelEntries.map(e => <option key={modelScopeKey(e)} value={modelScopeKey(e)}>{e.source.common_name} · {e.source.model_id}</option>)}</select></div><label className="filter-field">租户 APPID<select aria-label="用户APPID" disabled={busy} value={appid} onChange={e => { const matches = directory.filter(x => x.appid === e.target.value); const same = matches.filter(x => x.source.model_id === display?.receipt.model_id && x.source.common_name === display?.receipt.common_name); if (matches.length) chooseModel(same.length ? same : matches.filter(x => modelScopeKey(x) === modelScopeKey(matches[0]!))); else void selectApp(e.target.value); }}><option value="" disabled>请选择APPID</option>{apps.map(id => <option key={id}>{id}</option>)}</select></label><button className="run" onClick={() => { setMode('open'); setModal(true); }}>{snapshot ? `${formatBeijing(snapshot.provenance.data_range_utc.start)} — ${formatBeijing(snapshot.provenance.data_range_utc.end)}` : '选择分析结果'}</button></div><div className="filter-meta"><span>GB · 租户服务级复用潜力</span><span>展示运行 {display?.receipt.user_run_id ?? '—'}</span></div></section>
    {busy && <p role="status">正在读取…</p>}
    {(display || receipt?.state === 'indexing') && <details className="v2-pad"><summary>按APPID打开基础结果</summary><form onSubmit={e => { e.preventDefault(); void selectApp(fields(e.currentTarget).appid!); }}><label>APPID<input name="appid" required maxLength={4096}/></label><button disabled={busy}>读取基础结果</button></form><p className="muted">索引准备中可按已知APPID读取完成的基础结果；排行和估算等待索引就绪。</p></details>}
    {display?.receipt.state === 'empty' && <section className="panel v2-pad"><h2>本次没有有效用户组</h2><p>不将无效或缺失记录解释为生产零流量。可从本机记录返回历史分析。</p></section>}
    {snapshot && <><Overview snapshot={snapshot}/><TTFT key={`${display.receipt.user_run_id}/${snapshot.identity.appid}`} api={api} receipt={display.receipt} appid={snapshot.identity.appid} p90={selectedEntry?.prompt_p90 ?? display.ranking?.rows.find(r => r.appid === snapshot.identity.appid)?.prompt_p90} count={selectedEntry?.request_count ?? display.ranking?.rows.find(r => r.appid === snapshot.identity.appid)?.request_count}/><Distributions snapshot={snapshot} onSelect={setFilter}/><section className="panel v2-pad"><details><summary>数据质量与版本</summary><p>整文件无效行 {snapshot.quality.file_quality.skipped_rows}；本组有效 {snapshot.quality.group_quality.valid_requests}。整文件坏行不分摊给APPID。</p><p>基础运行 {snapshot.identity.run_id} · 用户运行 {display.receipt.user_run_id}</p>{selectedEntry && <><p>Trace完整APPID有效集；文件观察时间不是租户裁剪窗口。</p><p>模型规格 {selectedEntry.source.model_id} · 索引版本 {selectedEntry.source.index_revision}</p><p>输入SHA256 {selectedEntry.source.input_sha256}</p><p>Manifest SHA256 {selectedEntry.source.manifest_sha256} · 设置SHA256 {selectedEntry.source.settings_sha256}</p><p>编码器 {selectedEntry.source.encoder_identity} · 制品 {selectedEntry.source.asset_identity}</p><p>文件观察范围（UTC）{selectedEntry.source.file_observed_time_range_utc.map(x => x ?? '—').join(' — ')}</p><a href={monitorSourceUrl(selectedEntry)}>固定监控来源链接</a></>}<pre>{JSON.stringify(snapshot.provenance.runtime, null, 2)}</pre></details></section><Signals snapshot={snapshot}/>{page !== 'users/ranking' && <Requests key={`${snapshot.identity.run_id}/${snapshot.identity.appid}/${JSON.stringify(filter)}`} snapshot={snapshot} filter={filter} onDetail={() => { }}/>}</>}
    {!display && !busy && <section className="panel v2-pad"><h2>暂无历史分析</h2><p>打开已知用户运行，或新建/绑定基础结果。不会自动提交分析。</p></section>}
    {modal && <Modal title="分析结果" close={() => setModal(false)}><div className="toolbar">{[['open', '打开运行'], ['new', '新建分析'], ['bind', '绑定基础结果']].map(([id, label]) => <button key={id} onClick={() => setMode(id!)} aria-pressed={mode === id}>{label}</button>)}</div>
      {mode === 'open' ? <><form onSubmit={e => { e.preventDefault(); void open(fields(e.currentTarget).run!); }}><label>用户运行ID<input name="run" required maxLength={4096}/></label><button disabled={busy}>打开</button></form><h3>服务端运行目录</h3><button disabled={directoryBusy} onClick={() => void refreshDirectory()}>刷新目录</button>{directoryBusy && <p role="status">正在读取完整目录…</p>}{directory.map(e => <button className="v2-record" key={entryKey(e)} onClick={() => void chooseEntry(e)}>{e.appid ?? '空运行'} · {e.source.common_name} · {e.source.user_run_id} · {e.is_default ? '默认' : '历史'} · {e.source.index_revision}</button>)}{!directoryBusy && !directory.length && !directoryError && <p>服务端暂无已发布运行</p>}<h3>本机最近打开</h3><p className="muted">仅此浏览器记录，不是全服务运行目录。</p>{recent.map(id => <button className="v2-record" key={id} onClick={() => void open(id)}>{id}</button>)}</> : <form className="v2-form" onSubmit={e => { e.preventDefault(); void submit(mode === 'bind' ? '/bindings' : '/runs', fields(e.currentTarget)); }}><label>{mode === 'bind' ? '基础运行ID' : '输入目录内文件引用'}<input name={mode === 'bind' ? 'base_run_id' : 'file_ref'} required maxLength={4096}/></label><label>模型服务 common_name<input name="common_name" required maxLength={4096}/></label>{mode === 'new' && <label>编码模型<select name="model_id">{models.map(m => <option key={m}>{m}</option>)}</select></label>}<p className="muted">文件需预先放入受控输入目录；此处不上传本机文件。绑定不重新编码。</p><button className="primary" disabled={busy}>确认提交</button></form>}
      {error && <p role="alert">{error}</p>}</Modal>}
  </div>{display ? <Ranking key={display.receipt.user_run_id} api={api} receipt={display.receipt} active={page === 'users/ranking'} select={id => { void selectApp(id); location.hash = '/users'; }}/> : page === 'users/ranking' && <section className="panel v2-pad"><h1>搜索与排行</h1><p>请先打开用户运行。</p><a href="#/users">打开用户监控</a></section>}</>;
}

import { useCallback, useEffect, useState, useSyncExternalStore } from 'react';
import { ViewStore } from './state/view-store';
import { SnapshotCache } from './storage/snapshot-cache';
import { SnapshotCoordinator } from './state/snapshot-coordinator';
import { PublicationClient } from './state/publication-client';
import { Overview } from './features/overview/Overview';
import { Distributions } from './features/distributions/Distributions';
import type { BinSelection } from './features/distributions/Distributions';
import { Requests } from './features/requests/Requests';
import { Signals } from './features/signals/Signals';
import { Exports } from './features/exports/Exports';
import { formatBeijing } from './domain/time';
import { formatInteger } from './domain/integer';
import { History } from './components/History';
import { ReceiptStore } from './state/receipt-store';
import { SubmissionCoordinator } from './state/submission-coordinator';
import { Submissions } from './features/submissions/Submissions';
import { Settings } from './features/settings/Settings';
import { V2App } from './features/v2/V2App';
const pages = [ ['overview', '监控概览'], ['distributions', '请求长度分布'], ['requests', '请求明细'], ['signals', '监控信号'], ['settings', '运行设置'], ['submissions', '提交任务'] ] as const;
function subscribe(listener: () => void) {
  window.addEventListener('hashchange', listener);
  return () => window.removeEventListener('hashchange', listener);
}
function currentPage() { return window.location.hash.slice(2) || 'overview'; }
export function App() {
  const route = useSyncExternalStore(subscribe, currentPage);
  const page = route.split('?')[0] ?? 'users';
  if (!window.location.hash || page.startsWith('users') || page.startsWith('ma')) return <V2App page={page}/>;
  return <LegacyApp/>;
}
function LegacyApp() {
  const route = useSyncExternalStore(subscribe, currentPage);
  const [page = 'overview', query = ''] = route.split('?');
  const [bin, setBin] = useState<(BinSelection & { run: string }) | null>(null);
  const [runtime] = useState(() => {
    const store = new ViewStore();
    const cache = new SnapshotCache(message => store.update({ cacheWarning: message }));
    const coordinator = new SnapshotCoordinator(store, cache);
    const receipts = new ReceiptStore(message => store.update({ cacheWarning: message }));
    const submissions = new SubmissionCoordinator(receipts);
    const publication = new PublicationClient({
      catalog: value => coordinator.catalog(value),
      connection: value => store.update({ connection: value }),
      ready: (instance, epoch) => { void submissions.ready(instance, epoch); },
      terminal: event => { void submissions.terminal(event); },
      error: message => store.update({ error: message }),
    });
    return { store, coordinator, publication, submissions };
  });
  const state = useSyncExternalStore(runtime.store.subscribe, runtime.store.getSnapshot);
  useEffect(() => {
    void runtime.coordinator.restore(); void runtime.publication.start();
    const restore = () => { if (!document.hidden) void runtime.publication.start(); };
    window.addEventListener('pageshow', restore);
    return () => { runtime.publication.stop(); runtime.coordinator.stop(); window.removeEventListener('pageshow', restore); };
  }, [runtime]);
  const routeScope = new URLSearchParams(query);
  const appid = routeScope.get('appid'), model = routeScope.get('model'), historyRun = routeScope.get('run');
  useEffect(() => { if (state.catalog && appid && model) void runtime.coordinator.select(appid, model, false, historyRun ?? undefined); }, [runtime, state.catalog?.service_instance_id, appid, model, historyRun]);
  useEffect(() => { runtime.coordinator.pin(historyRun !== null || page === 'settings'); }, [runtime, historyRun, page, state.selection?.appid, state.selection?.model_id, state.snapshot?.identity.run_id]);
  const onDetail = useCallback((open: boolean) => runtime.coordinator.pin(open || historyRun !== null || page === 'settings'), [runtime, historyRun, page]);
  const navigate = (nextPage: string, nextApp = state.selection?.appid, nextModel = state.selection?.model_id, run?: string) => {
    const q = new URLSearchParams(); if (nextApp) q.set('appid', nextApp); if (nextModel) q.set('model', nextModel); if (run) q.set('run', run);
    window.location.hash = `/${nextPage}${q.size ? '?' + q : ''}`;
  };
  const snapshot = state.snapshot;
  const title = pages.find(([id]) => id === page)?.[1];
  return <div className="shell">
    <a className="skip" href="#main">跳至内容</a>
    <aside className="sidebar"><div className="brand"><span className="brandmark" aria-hidden="true"><i /><i /><i /></span>TokenScope</div><nav aria-label="监控导航"><div className="nav-caption">WORKSPACE</div>{pages.map(([id, label], index) => <a className="nav-item" key={id} href={`#/${id}${query ? '?' + query : ''}`} aria-current={page === id ? 'page' : undefined}><svg className="icon" viewBox="0 0 24 24" aria-hidden="true"><path d={['M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z', 'M3 3v18h18 M7 16v-4 M12 16V7 M17 16V4', 'M8 6h13 M8 12h13 M8 18h13 M3 6h1 M3 12h1 M3 18h1', 'M5 17h14l-2-3V9a5 5 0 0 0-10 0v5z M10 21h4', 'M4 6h16 M4 12h16 M4 18h16 M8 3v6 M16 9v6 M10 15v6', 'M12 4v16 M4 12h16'][index]} /></svg>{label}</a>)}</nav><div className="sidebar-bottom"><b>Token 监控 · V1</b><p>按租户与模型观察<br />输入规模与前缀复用</p></div></aside>
    <div className="workspace"><header className="topbar"><div className="crumb">工作空间 <span>/</span><strong>Token 监控</strong></div><span className={`badge ${state.connection === 'connected' ? 'success' : ''}`}>{state.connection === 'connected' ? '通知已连接' : '通知待连接'}</span></header>
    <main id="main" tabIndex={-1}>
      <div className="page-head"><div><h1>{title ?? '页面不存在'}</h1><p>按租户与模型查看输入规模、前缀复用和长度分布</p></div><div className="actions"><details className="action-menu"><summary className="btn">指标口径</summary><div className="popover"><h2>指标口径</h2><p>原始 JSON 包含字段名、标点、空白和参数；模板后输入为模型实际输入。理想命中率 = 理想复用 Token / 模板后输入 Token。</p><p>每个 CSV 从空缓存开始，租户隔离、无限容量，前请求可缓存输入立即可用。输出量单独统计。</p></div></details>{snapshot && page === 'overview' && <details className="action-menu" key={snapshot.identity.run_id + snapshot.identity.appid}><summary className="btn">导出</summary><div className="popover"><Exports snapshot={snapshot} /></div></details>}<button className="primary" onClick={() => navigate('submissions')}>提交任务</button></div></div>
      {state.error && <p role="alert">{state.error} <button onClick={() => void runtime.publication.start()}>重新连接</button></p>}
      {state.cacheWarning && <p className="muted">{state.cacheWarning}</p>}
      {state.catalog && <section className="filter-panel" aria-label="结果范围"><div className="filter-main"><div className="model-field"><span className="field-caption">模型</span><div className="model-tabs" role="group" aria-label="选择模型">{state.catalog.items.filter(i => i.appid === state.selection?.appid).map(item => <button key={item.model_id} aria-pressed={state.selection?.model_id === item.model_id} onClick={() => navigate(page, state.selection?.appid, item.model_id)}>{item.model_id}</button>)}</div></div><label className="filter-field"><span className="field-caption">租户 APPID</span><select aria-label="appid" value={state.selection?.appid ?? ''} onChange={event => { const first = state.catalog!.items.find(i => i.appid === event.target.value); if (first) navigate(page, first.appid, first.model_id); }}>{[...new Set(state.catalog.items.map(i => i.appid))].map(id => <option key={id}>{id}</option>)}</select></label><div className="filter-field run"><span className="field-caption">分析结果 · 北京时间</span>{snapshot && <span className="window-label">{formatBeijing(snapshot.provenance.data_range_utc.start)} — {formatBeijing(snapshot.provenance.data_range_utc.end)}</span>}<History catalog={state.catalog} appid={state.selection?.appid} model={state.selection?.model_id} onSelect={run => navigate(page, state.selection?.appid, state.selection?.model_id, run)} />{historyRun && <button onClick={() => navigate(page)}>返回最新完整结果</button>}{state.loading && <span role="status">正在读取完整版本…</span>}</div></div>
      {snapshot && <div className="filter-meta"><div className="source-meta"><span title={snapshot.provenance.source_label}>{snapshot.provenance.source_label}</span><details className="metadata-details"><summary>数据质量与版本</summary><div className="metadata-body"><p>组数据：{formatBeijing(snapshot.provenance.data_range_utc.start)} — {formatBeijing(snapshot.provenance.data_range_utc.end)}</p><p>整文件：{formatBeijing(snapshot.provenance.file_data_range_utc.start)} — {formatBeijing(snapshot.provenance.file_data_range_utc.end)}</p><p>生成时间：{formatBeijing(snapshot.provenance.published_at)}</p><p>整文件无效行 {formatInteger(snapshot.quality.file_quality.skipped_rows)}；本组有效请求 {formatInteger(snapshot.quality.group_quality.valid_requests)}；本组重复 ID 提示 {formatInteger(snapshot.quality.group_quality.duplicate_hash_id_rows_within_group)}。</p><p>无法归属的无效行不分摊到本组。本组跳过行：{formatInteger(snapshot.quality.group_quality.skipped_rows)}</p><p>run：{snapshot.identity.run_id} · 设置版本 {snapshot.provenance.settings.revision}</p><pre>{JSON.stringify(snapshot.provenance.runtime, null, 2)}</pre></div></details>{snapshot.quality.file_quality.skipped_rows !== '0' && <span className="badge warn">文件有跳过行</span>}{snapshot.quality.group_quality.duplicate_hash_id_rows_within_group !== '0' && <span className="badge warn">重复 ID 已保留</span>}</div><div className="config-meta"><span>本次 r{snapshot.provenance.settings.revision} · Block {snapshot.provenance.settings.block_size} · MTP {snapshot.provenance.settings.mtp ? '开' : '关'} · CP {snapshot.provenance.settings.cp_world_size}</span><button className="linkbutton" onClick={() => navigate('settings')}>设置</button></div><small>生成于 {formatBeijing(snapshot.provenance.published_at)}</small></div>}</section>}
      {state.pending && <p className="notice">新结果可查看。<button onClick={() => { setBin(null); runtime.coordinator.acceptPending(); navigate(page); }}>切换到新完整结果</button></p>}

      {snapshot && page === 'overview' && <Overview snapshot={snapshot} />}
      {snapshot && (page === 'overview' || page === 'distributions') && <Distributions snapshot={snapshot} onSelect={value => { setBin({ ...value, run: snapshot.identity.run_id }); navigate('requests', undefined, undefined, historyRun ?? undefined); }} />}
      {snapshot && page === 'requests' && <><button onClick={() => setBin(null)}>清除长度区间筛选</button><Requests key={JSON.stringify(snapshot.identity) + JSON.stringify(bin)} snapshot={snapshot} filter={bin?.run === snapshot.identity.run_id ? bin : null} onDetail={onDetail} /></>}
      {snapshot && page === 'signals' && <Signals key={JSON.stringify(snapshot.identity)} snapshot={snapshot} />}
      {state.catalog && page === 'settings' && <Settings key={(state.selection?.model_id ?? 'GLM-5.2') + state.catalog.service_instance_id} model={state.selection?.model_id ?? 'GLM-5.2'} instance={state.catalog.service_instance_id} snapshot={snapshot} />}
      {state.catalog && page === 'submissions' && <Submissions coordinator={runtime.submissions} instance={state.catalog.service_instance_id} connected={state.connection === 'connected'} />}
      {((!snapshot && !(['settings', 'submissions'].includes(page) && state.catalog)) || !title) && <section aria-label="数据状态" className="panel">
        <h2>{title ? (state.snapshot ? '完整结果已读取' : '尚未接入监控数据') : '请选择监控页面'}</h2>
        <p>{title ? '完整计算结果发布后，指标和分布将在同一版本下展示。' : '可以通过上方导航返回监控概览。'}</p>
        <p className="muted">只展示已发布的完整结果</p>
      </section>}
    </main>
    <footer><span>时间展示：北京时间（UTC+8）</span><span>每个 CSV 从空缓存开始 · appid 隔离 · 无限容量</span></footer></div>
  </div>;
}

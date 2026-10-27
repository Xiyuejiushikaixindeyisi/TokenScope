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
import { History } from './components/History';
import { ReceiptStore } from './state/receipt-store';
import { SubmissionCoordinator } from './state/submission-coordinator';
import { Submissions } from './features/submissions/Submissions';
import { Settings } from './features/settings/Settings';
const pages = [ ['overview', '监控概览'], ['distributions', '请求长度分布'], ['requests', '请求明细'], ['signals', '监控信号'], ['settings', '运行设置'], ['submissions', '提交任务'] ] as const;
function subscribe(listener: () => void) {
  window.addEventListener('hashchange', listener);
  return () => window.removeEventListener('hashchange', listener);
}
function currentPage() { return window.location.hash.slice(2) || 'overview'; }
export function App() {
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
    <header><strong className="brand">TokenScope</strong><span>Token 监控</span></header>
    <nav aria-label="监控导航">{pages.map(([id, label]) => <a key={id} href={`#/${id}${query ? '?' + query : ''}`} aria-current={page === id ? 'page' : undefined}>{label}</a>)}</nav>
    <main id="main" tabIndex={-1}>
      <div className="eyebrow">appid × 模型</div><h1>{title ?? '页面不存在'}</h1>
      {state.error && <p role="alert">{state.error} <button onClick={() => void runtime.publication.start()}>重新连接</button></p>}
      {state.cacheWarning && <p className="muted">{state.cacheWarning}</p>}
      {state.catalog && <p className="muted">已读取 {state.catalog.total} 个 appid × 模型范围 · {state.connection === 'connected' ? '通知已连接' : '通知待连接'}</p>}
      {state.catalog && <div className="scope-bar"><label>appid <select value={state.selection?.appid ?? ''} onChange={event => { const first = state.catalog!.items.find(i => i.appid === event.target.value); if (first) navigate(page, first.appid, first.model_id); }}>{[...new Set(state.catalog.items.map(i => i.appid))].map(id => <option key={id}>{id}</option>)}</select></label><label>模型 <select value={state.selection?.model_id ?? ''} onChange={event => navigate(page, state.selection?.appid, event.target.value)}>{state.catalog.items.filter(i => i.appid === state.selection?.appid).map(item => <option key={item.model_id}>{item.model_id}</option>)}</select></label>{state.loading && <span>正在读取完整版本…</span>}{<History catalog={state.catalog} appid={state.selection?.appid} model={state.selection?.model_id} onSelect={run => navigate(page, state.selection?.appid, state.selection?.model_id, run)} />}{historyRun && <button onClick={() => navigate(page)}>返回最新完整结果</button>}</div>}
      {state.pending && <p className="notice">新结果可查看。<button onClick={() => { setBin(null); runtime.coordinator.acceptPending(); navigate(page); }}>切换到新完整结果</button></p>}
      {snapshot && <p className="muted">当前范围：{snapshot.identity.appid} × {snapshot.identity.model_id} · run {snapshot.identity.run_id}</p>}
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
    <footer>时间展示：北京时间（UTC+8）</footer>
  </div>;
}

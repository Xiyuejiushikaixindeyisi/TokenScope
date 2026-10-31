import { useEffect, useRef, useState } from 'react';
import { getJson } from '../../api/client';
import { V2Client, verifyUserContract } from '../../api/v2/client';
import { UserMonitor } from './UserMonitor';
import { MAMonitor } from './MAMonitor';
import { errorText } from './common';
import './v2.css';
export function V2App({ page }: {
    page: string;
}) {
    const [api, setApi] = useState<V2Client | null>(null), [error, setError] = useState('');
    const connection = useRef(0);
    async function connect() { const token = ++connection.current; try {
        await verifyUserContract();
        if (token !== connection.current) return;
        const catalog = await getJson('CatalogResponse', '/monitoring/catalog');
        if (token !== connection.current) return;
        setApi(new V2Client(catalog.service_instance_id));
        setError('');
    }
    catch (e) {
        if (token === connection.current) setError(errorText(e));
    } }
    useEffect(() => { void connect(); const changed = () => { connection.current++; setApi(null); setError('服务身份已变化，已停止旧任务查询。请重新连接并选择运行。'); }; window.addEventListener('tokenscope-instance-changed', changed); return () => { connection.current++; window.removeEventListener('tokenscope-instance-changed', changed); }; }, []);
    return <div className="shell v2"><a className="skip" href="#main">跳至内容</a><aside className="sidebar"><div className="brand"><span className="brandmark"><i /><i /><i /></span>TokenScope</div><nav aria-label="监控导航"><div className="nav-caption">用户工作台</div><a className="nav-item" aria-current={page === 'users' ? 'page' : undefined} href="#/users">▦　用户监控</a><a className="nav-item" aria-current={page==='users/ranking'?'page':undefined} href="#/users/ranking">☷　搜索与排行</a><div className="nav-caption">同事工作台</div><a className="nav-item" aria-current={page.startsWith('ma')?'page':undefined} href="#/ma">▦　MA集群监控</a><a className="nav-item" href="#/settings">⚙　运行设置</a><a className="nav-item" href="#/overview">↗　V1监控</a></nav><div className="sidebar-bottom"><b>Token监控 · V2</b><p>已发布分析结果<br />不在页面访问时重新分析</p></div></aside><div className="workspace"><header className="topbar"><span className="crumb">工作台 / <strong>Token监控</strong></span><span className="badge">北京时间 UTC+8</span></header><nav className="v2-mobile"><a href="#/users">用户监控</a><a href="#/users/ranking">搜索排行</a><a href="#/ma">MA集群</a></nav><main id="main">{error && <p role="alert">{error}<button onClick={() => void connect()}>重新连接</button></p>}{api ? (page.startsWith('ma') ? <MAMonitor key={api.instance} api={api}/> : <UserMonitor key={api.instance} api={api} page={page}/>) : <p role="status">正在连接服务…</p>}</main></div></div>;
}

import { AppShell } from '../../components/AppShell';
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
    return <AppShell page={page}><main id="main">{error && <p role="alert">{error}<button onClick={() => void connect()}>重新连接</button></p>}{api ? (page.startsWith('ma') ? <MAMonitor key={api.instance} api={api}/> : <UserMonitor key={api.instance} api={api} page={page}/>) : <p role="status">正在连接服务…</p>}</main></AppShell>;
}

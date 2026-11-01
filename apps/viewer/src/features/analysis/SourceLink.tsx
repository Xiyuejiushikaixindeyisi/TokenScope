import { useEffect, useRef, useState } from 'react';
import { getJson } from '../../api/client';
import { V2Client, verifyUserContract } from '../../api/v2/client';
import { obj, str } from '../../api/analysis/client';
import type { Obj } from '../../api/analysis/client';
/** A source link is historical evidence, never a claim about the latest monitoring run. */
export function SourceLink({ entry }: {
    entry: Obj;
}) {
    const [error, setError] = useState(''), [busy, setBusy] = useState(false);
    const pending = useRef<AbortController | null>(null);
    useEffect(() => {
        setError(''); setBusy(false);
        return () => pending.current?.abort();
    }, [entry]);
    async function open() {
        pending.current?.abort();
        const request = new AbortController(); pending.current = request;
        const signal = request.signal;
        setBusy(true);
        setError('');
        try {
            const scope = obj(entry.scope), source = obj(scope.source);
            const q = new URLSearchParams({ appid: str(scope.appid) });
            const catalog = await getJson('CatalogResponse', '/monitoring/catalog', {}, { signal });
            if (source.user_run_id) {
                await verifyUserContract();
                signal.throwIfAborted();
                const client = new V2Client(catalog.service_instance_id);
                const receipt = await client.request('user', 'Receipt', `/runs/${encodeURIComponent(str(source.user_run_id))}`, { signal });
                if (receipt.base_run_id !== source.base_run_id || receipt.common_name !== source.common_name || receipt.model_id !== source.model_id)
                    throw Error('监控来源身份不匹配');
                q.set('user_run_id', str(source.user_run_id));
                signal.throwIfAborted();
                location.hash = `#/users?${q}`;
            }
            else {
                // Existing S0 reader verifies run/app/model identity after navigation.
                q.set('run', str(source.base_run_id));
                q.set('model', str(source.model_id));
                signal.throwIfAborted();
                location.hash = `#/overview?${q}`;
            }
        }
        catch (e) {
            if (!signal.aborted) setError(`原报告来源暂不可用：${String(e)}。可返回监控选择其他运行。`);
        }
        finally {
            if (!signal.aborted) setBusy(false);
        }
    }
    return <><button className="btn" disabled={busy} onClick={() => void open()}>{busy ? '正在核对来源…' : '查看原报告监控来源'}</button>{error && <p role="alert">{error}</p>}</>;
}

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
                if (receipt.user_run_id !== source.user_run_id || receipt.base_run_id !== source.base_run_id || receipt.common_name !== source.common_name || receipt.model_id !== source.model_id || !receipt.index_revision)
                    throw Error('监控来源身份不匹配');
                const directory = await client.request('user', 'DiscoveryPage', '/runs', { signal, query: { user_run_id: str(source.user_run_id), appid: str(scope.appid), offset: '0', limit: 100 } });
                const match = directory.entries[0];
                if (directory.total !== '1' || directory.next_offset !== null || directory.entries.length !== 1 || !match || match.appid !== scope.appid || match.source.user_run_id !== source.user_run_id || match.source.index_revision !== receipt.index_revision || match.source.base_run_id !== source.base_run_id || match.source.common_name !== source.common_name || match.source.model_id !== source.model_id || match.source.manifest_sha256 !== source.manifest_sha256 || match.source.asset_identity !== source.asset_identity || match.source.encoder_identity !== source.encoder_identity) throw Error('监控来源发布身份不匹配');
                q.set('run', str(source.user_run_id));
                // SourceIdentity has no original index revision. Pin the currently
                // verified immutable run/index, after matching its sealed source.
                q.set('revision', str(receipt.index_revision));
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

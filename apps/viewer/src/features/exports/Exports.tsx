import { useEffect, useRef, useState } from 'react';
import type { Dto } from '../../api/types';
import { apiPath } from '../../api/client';
import { beginExport } from './export-controller';
export function Exports({ snapshot, filter, sort }: { snapshot: Dto<'ViewSnapshot'>; filter?: Dto<'LengthFilter'>; sort?: Dto<'RequestSort'> }) {
  const [busy, setBusy] = useState(false), [note, setNote] = useState('');
  const controller = useRef<AbortController | null>(null);
  useEffect(() => () => controller.current?.abort(), []);
  useEffect(() => { if (!busy) return; const warn = (e: BeforeUnloadEvent) => { e.preventDefault(); }; window.addEventListener('beforeunload', warn); return () => window.removeEventListener('beforeunload', warn); }, [busy]);
  const run = async (format: 'ndjson' | 'csv') => {
    const abort = new AbortController(); controller.current = abort; setBusy(true); setNote('正在校验并导出；切换页面将取消导出。');
    const f = filter ?? { metric: 'prompt_tokens', lower: '0', upper: null, hash_id: null, hash_match: 'exact' };
    const s = sort ?? { by: 'prompt_tokens', order: 'desc', tie_breaker: 'source_record_index_asc' };
    try {
      const result = await beginExport(apiPath(`/analysis-runs/${snapshot.identity.run_id}/requests/export`, { appid: snapshot.identity.appid, format, metric: f.metric, lower: f.lower, upper: f.upper ?? undefined, hash_id: f.hash_id ?? undefined, hash_match: f.hash_match, sort_by: s.by, sort_order: s.order }), `tokenscope-${snapshot.identity.run_id}.${format}`, { format, scope: snapshot.identity, filter: f, sort: s }, abort.signal);
      setNote(`${result.rows} 条请求校验完成，${result.saved ? '文件已保存' : '已发起浏览器下载'}。${format === 'ndjson' ? 'SHA256 与记录数一致。' : 'CSV 结构与记录数一致（不含摘要校验）。'}`);
    } catch (error) { setNote(abort.signal.aborted ? '导出已取消，未提交文件；文件选择器可能留下空占位文件。' : `导出未完成：${error instanceof Error ? error.message : '请重试'}；未提交文件。`); }
    finally { setBusy(false); }
  };
  const saveSnapshot = () => { const url = URL.createObjectURL(new Blob([JSON.stringify(snapshot)], { type: 'application/json' })); const link = document.createElement('a'); link.href = url; link.download = `snapshot-${snapshot.identity.run_id}.json`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); };
  return <div className="export-controls"><div className="toolbar">{!filter && <button disabled={busy} onClick={saveSnapshot}>下载当前展示快照 JSON</button>}<span>{filter ? '当前筛选的全部请求' : '当前 appid × 模型的全部请求'}：</span><button disabled={busy} onClick={() => void run('ndjson')}>导出 NDJSON</button><button disabled={busy} onClick={() => void run('csv')}>导出 CSV</button>{busy && <button onClick={() => controller.current?.abort()}>取消导出</button>}</div><p role="status" className="muted">{note || '仅含请求身份和计量数据；无文件写入 API 时，校验后下载上限为16MiB。'}</p></div>;
}

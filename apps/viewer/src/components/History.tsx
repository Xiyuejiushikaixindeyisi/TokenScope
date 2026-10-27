import { useState } from 'react';
import type { Dto } from '../api/types';
import { useRead } from './useRead';
import { formatBeijing } from '../domain/time';
export function History({ catalog, appid, model, onSelect }: { catalog: Dto<'CatalogResponse'>; appid?: string | undefined; model?: string | undefined; onSelect(run: string): void }) {
  const [offset, setOffset] = useState('0'), [open, setOpen] = useState(false), [all, setAll] = useState(false);
  const { data, error, reload } = useRead('PublishedRunsResponse', '/monitoring/runs', { appid: all ? undefined : appid, model_id: model, offset, limit: 50, catalog_revision: catalog.catalog_revision }, { service_instance_id: catalog.service_instance_id, view_schema_version: '1' }, false, open);
  return <details onToggle={e => setOpen(e.currentTarget.open)}><summary>选择历史完整运行</summary><label><input type="checkbox" checked={all} onChange={e => { setAll(e.target.checked); setOffset('0'); }} />包含未产生有效请求的运行</label>{error && <p>{error}目录可能已更新。<button onClick={reload}>重读历史</button></p>}{data?.items.map(run => <p key={run.run_id}><button disabled={run.status === 'no_valid_rows' || all || !appid} onClick={() => onSelect(run.run_id)}>{formatBeijing(run.published_at)} · {run.source_label} · {run.status === 'no_valid_rows' ? '无有效请求' : run.run_id}</button></p>)}<button disabled={offset === '0'} onClick={() => setOffset((BigInt(offset) >= 50n ? BigInt(offset) - 50n : 0n).toString())}>上一页</button><button disabled={!data?.next_offset} onClick={() => setOffset(data!.next_offset!)}>下一页</button></details>;
}

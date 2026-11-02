import { useState } from 'react';
import type { Dto } from '../../api/types';
import { useRead } from '../../components/useRead';
import { formatBeijing } from '../../domain/time';
import { formatInteger } from '../../domain/integer';
export function Signals({ snapshot }: { snapshot: Dto<'ViewSnapshot'> }) {
  const [offset, setOffset] = useState('0');
  const { data, error, reload } = useRead('SignalsPage', `/analysis-runs/${snapshot.identity.run_id}/view-signals`, { appid: snapshot.identity.appid, offset, limit: 50 }, snapshot.identity, false);
  return <section className="panel signals-panel"><h2>监控信号</h2><p className="muted">仅显示当前完整运行关联的信号。待消费不代表分析器已启动。</p>{error && <p role="alert">{error}<button onClick={reload}>重读信号</button></p>}{data?.items.map(signal => <article className="signal" key={signal.event_id}><strong>{signal.metric}</strong><p>观测 {typeof signal.observed_value === 'string' ? formatInteger(signal.observed_value, true) : String(signal.observed_value)} · 阈值 {typeof signal.threshold === 'string' ? formatInteger(signal.threshold, true) : String(signal.threshold)} · {signal.comparator}</p><p>{formatBeijing(signal.published_at)} · {signal.status}</p></article>)}{data?.items.length === 0 && <div className="signal-empty"><svg className="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8a6 6 0 0 1 12 0v5l3 4H3l3-4ZM9 21h6"/></svg><p>当前运行无监控信号。</p><a className="btn" href={`#/settings?${new URLSearchParams({appid:snapshot.identity.appid,model:snapshot.identity.model_id,run:snapshot.identity.run_id})}`}>配置监控阈值</a></div>}<div className="toolbar" hidden={data?.items.length === 0 && offset === '0'}><button disabled={offset === '0'} onClick={() => setOffset((BigInt(offset) >= 50n ? BigInt(offset) - 50n : 0n).toString())}>上一页</button><button disabled={!data?.next_offset} onClick={() => setOffset(data!.next_offset!)}>下一页</button></div></section>;
}

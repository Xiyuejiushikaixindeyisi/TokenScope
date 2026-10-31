import { useEffect, useRef, useState } from 'react';
import type { V2Client } from '../../api/v2/client';
import { segment } from '../../api/v2/client';
import { ApiError } from '../../api/client';
import type { Receipt, Ranking as RankingDto, Modes } from '../../api/v2/generated/user';
import { formatInteger } from '../../domain/integer';
import { sortNames, fractionText, rangeQuery } from './numbers';
import { Modal, errorText, percent } from './common';
export function Ranking({ api, receipt, active, select }: {
    api: V2Client;
    receipt: Receipt;
    active: boolean;
    select(appid: string): void;
}) {
    const [search, setSearch] = useState(''), [querySearch, setQuerySearch] = useState(''), [sort, setSort] = useState('request_count'), [direction, setDirection] = useState('desc'), [width, setWidth] = useState('5000');
    const [draft, setDraft] = useState<Record<string, string>>({}), [applied, setApplied] = useState<Record<string, string>>({}), [offset, setOffset] = useState('0');
    const [data, setData] = useState<RankingDto | null>(null), [error, setError] = useState(''), [rangeError, setRangeError] = useState(''), [busy, setBusy] = useState(false), [refresh, setRefresh] = useState(0);
    const revisionRetries = useRef(0);
    const revision = useRef<string | undefined>(receipt.index_revision ?? undefined);
    const [modeApp, setModeApp] = useState<string | null>(null), [modes, setModes] = useState<Modes | null>(null), [modeOffset, setModeOffset] = useState('0'), [modeError, setModeError] = useState('');
    useEffect(() => { const t = setTimeout(() => { setQuerySearch(search); setOffset('0'); }, 300); return () => clearTimeout(t); }, [search]);
    useEffect(() => {
        if (!active || receipt.state !== 'ready')
            return;
        const controller = new AbortController();
        let live = true;
        setBusy(true);
        setError('');
        setData(null);
        void api.request('user', 'Ranking', `/runs/${segment(receipt.user_run_id)}/rankings`, { signal: controller.signal, query: { appid_contains: querySearch, sort, direction, bin_width: width, offset, limit: 20, index_revision: revision.current, ...applied } }).then(value => { if (live) {
            if (value.user_run_id !== receipt.user_run_id || value.common_name !== receipt.common_name)
                throw Error('排行范围不一致');
            revision.current = value.index_revision;
            revisionRetries.current = 0;
            setData(value);
        } }).catch(e => { if (!live)
            return; if (e instanceof ApiError && e.code === 'INDEX_REVISION_CONFLICT' && revisionRetries.current++ < 1) {
            revision.current = undefined;
            setOffset('0');
            setRefresh(n => n + 1);
            setError('结果版本已更新，正在重新读取首屏');
        }
        else
            setError(errorText(e)); }).finally(() => { if (live)
            setBusy(false); });
        return () => { live = false; controller.abort(); };
    }, [api, receipt, active, querySearch, sort, direction, width, offset, applied, refresh]);
    useEffect(() => {
        if (!modeApp)
            return;
        let live = true;
        const c = new AbortController();
        setModes(null);
        setModeError('');
        void api.request('user', 'Modes', `/runs/${segment(receipt.user_run_id)}/modes`, { signal: c.signal, query: { appid: modeApp, bin_width: width, index_revision: revision.current, offset: modeOffset, limit: 20 } }).then(v => { if (live) {if(v.user_run_id!==receipt.user_run_id||v.appid!==modeApp||v.index_revision!==revision.current)throw Error('Mode scope mismatch');setModes(v);} }).catch(e => { if (live)
            setModeError(errorText(e)); });
        return () => { live = false; c.abort(); };
    }, [api, receipt.user_run_id, modeApp, modeOffset, width]);
    const change = (setter: (s: string) => void) => (value: string) => { setter(value); setOffset('0'); };
    return <section hidden={!active}><div className="page-head"><div><h1>搜索与排行</h1><p>{receipt.common_name} · 同一运行内比较APPID</p></div><a className="btn" href="#/users">返回当前监控</a></div><section className="panel"><div className="v2-rank-controls"><label>搜索 APPID<input aria-label="搜索APPID" value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') {
        setQuerySearch(search);
        setOffset('0');
    } }} placeholder="区分大小写 · 字面子串" maxLength={4096}/></label><label>模型服务<input readOnly value={receipt.common_name}/></label><label>排序指标<select aria-label="排行排序" value={sort} onChange={e => change(setSort)(e.target.value)}>{Object.entries(sortNames).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></label><label>顺序<select aria-label="排行顺序" value={direction} onChange={e => change(setDirection)(e.target.value)}><option value="desc">从高到低</option><option value="asc">从低到高</option></select></label></div>
 <div className="toolbar"><label>众数箱宽<select aria-label="众数箱宽" value={width} onChange={e => change(setWidth)(e.target.value)}>{['5000', '2000', '1000'].map(w => <option key={w} value={w}>{Number(w) / 1000}K Token</option>)}</select></label><span className="muted">理想重算C · 超过200K仍等宽分箱</span></div>
 <details className="v2-pad"><summary>数值条件 · {Object.keys(applied).length}个边界生效</summary><div className="v2-ranges">{Object.entries(sortNames).map(([k, label]) => <label key={k}>{label}{k === 'ideal_hit_rate' ? '（%）' : ''}<div>{['min', 'max'].map(side => <input key={side} aria-label={`${label}${side === 'min' ? '下限' : '上限'}`} inputMode="decimal" value={draft[k + '_' + side] ?? ''} placeholder={side === 'min' ? '下限' : '上限'} onChange={e => setDraft({ ...draft, [k + '_' + side]: e.target.value })}/>)}</div></label>)}</div><button onClick={() => { try {
        setApplied(rangeQuery(draft));
        setOffset('0');
        setRangeError('');
    }
    catch (e) {
        setRangeError(errorText(e));
    } }}>应用条件</button><button onClick={() => { setDraft({}); setApplied({}); setOffset('0'); setRangeError(''); }}>清空数值条件</button>{rangeError && <p role="alert">{rangeError}</p>}</details>
 <div className="filter-meta"><span>运行 {receipt.user_run_id}</span><button disabled={busy} onClick={() => setRefresh(n => n + 1)}>刷新排行</button></div>{error && <p role="alert" className="v2-pad">{error}</p>}{busy && <p role="status" className="v2-pad">正在查询排行…</p>}
 {receipt.state !== 'ready' ? <p className="v2-pad">{receipt.state === 'indexing' ? '索引准备中，基础监控仍可查看' : '本次运行无可用排行'}</p> : data && <><div className="table-wrap"><table className="v2-rank-table"><thead><tr><th>APPID</th><th>模型服务</th><th>请求数</th><th>理想命中率</th><th>模板后输入</th><th>理想重算总量</th><th>典型重算长度<br />众数区间均值</th><th>{sortNames[sort as keyof typeof sortNames]}</th><th /></tr></thead><tbody>{data.rows.map(row => <tr key={row.appid}><td className="v2-id">{row.appid}</td><td>{receipt.common_name}</td><td>{formatInteger(row.request_count)}</td><td>{percent(row.ideal_hit_rate)}</td><td>{formatInteger(row.total_prompt_tokens)}</td><td>{formatInteger(row.total_ideal_compute_tokens)}</td><td>{fractionText(row.typical_compute_tokens)} Token<small className="v2-sub">[{formatInteger(row.representative_bin.lower)}, {formatInteger(row.representative_bin.upper)}) · {percent(row.representative_bin.share)}</small><button className="linkbutton" onClick={() => { setModeApp(row.appid); setModeOffset('0'); }}>查看 {row.tie_count} 个众数区间</button></td><td>{sort === 'ideal_hit_rate' ? percent(row.ideal_hit_rate) : sort === 'typical_ideal_compute_tokens' ? fractionText(row.typical_compute_tokens) : formatInteger(sort === 'request_count' ? row.request_count : row.total_ideal_compute_tokens)}</td><td><button onClick={() => select(row.appid)}>查看监控 →</button></td></tr>)}</tbody></table></div>{data.rows.length === 0 && <p className="v2-pad">没有匹配的APPID，当前运行保持不变。</p>}<div className="v2-pagination"><span>{data.total} 个匹配 · 每页20条 · 第{(BigInt(offset) / 20n + 1n).toString()}页</span><button disabled={offset === '0' || busy} onClick={() => setOffset((BigInt(offset) > 20n ? BigInt(offset) - 20n : 0n).toString())}>上一页</button><button disabled={!data.next_offset || busy} onClick={() => data.next_offset && setOffset(data.next_offset)}>下一页</button></div></>}
 </section><p className="muted v2-pad">代表值取最低起点众数箱内均值，保留全部并列峰；不是整体平均。单服务单运行比较。</p>
 {modeApp && <Modal title={`${modeApp} · 众数区间`} close={() => setModeApp(null)}>{modeError ? <p role="alert">{modeError}<button onClick={() => { setModeApp(null); revision.current = undefined; setOffset('0'); setRefresh(n => n + 1); }}>关闭并刷新排行</button></p> : modes ? <><p>全部并列峰共 {modes.total} 个，按起点排序；当前显示本页。</p><div className="table-wrap"><table><thead><tr><th>区间</th><th>请求数</th><th>占比</th><th>箱内均值</th></tr></thead><tbody>{modes.bins.map(b => <tr key={b.lower}><td>[{b.lower}, {b.upper})</td><td>{b.count}</td><td>{percent(b.share)}</td><td>{fractionText(b.mean)}</td></tr>)}</tbody></table></div><button disabled={modeOffset === '0'} onClick={() => setModeOffset((BigInt(modeOffset) > 20n ? BigInt(modeOffset) - 20n : 0n).toString())}>上一页</button><button disabled={!modes.next_offset} onClick={() => modes.next_offset && setModeOffset(modes.next_offset)}>下一页</button></> : <p role="status">读取众数…</p>}</Modal>}
 </section>;
}

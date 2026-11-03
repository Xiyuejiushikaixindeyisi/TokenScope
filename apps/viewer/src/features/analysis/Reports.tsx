import { useEffect, useRef, useState } from 'react';
import { arr, obj, str } from '../../api/analysis/client';
import type { AnalysisClient, Obj } from '../../api/analysis/client';
import { decimalRatio, hit } from './format';
import type { Card, LoadedReport } from './model';
import { checks, getCard } from './model';
import { EvidencePreview, EvidenceDetails } from './Evidence';

export const integer = (value: string) => BigInt(value).toLocaleString('en-US');
const compact = (value: string) => value.replace(/\.00$/, '').replace(/(\.\d)0$/, '$1');
export function ratio(value: Obj | null, percent = false) { return value ? compact(decimalRatio(str(value.numerator), str(value.denominator), percent ? 100n : 1n)) + (percent ? '%' : '') : '—'; }
export function Metrics({ card }: { card: Card }) {
    const c = card;
    if (c.kind === 'difference_group') return <div className="diff-metric"><span>已发现涉及</span><strong>{integer(c.affected!)}</strong><span>条 / 本报告 {integer(c.total)} 条</span><span className="case-count">{c.differenceGroups ? c.differenceGroups.length ? '最多 3 个代表例子' : '暂无可展示例子' : `${arr(c.data.example_refs).length} 个例子`}</span></div>;
    const impact = <div><small>影响请求</small><strong>{c.affected === null ? '待评估' : integer(c.affected)}{c.affected !== null && <em>条</em>}</strong><span className="explain">本报告 {integer(c.total)} 条{c.affected !== null && BigInt(c.total) > 0n ? `中的 ${compact(decimalRatio(c.affected, c.total, 100n))}%` : ''}</span></div>;
    if (!c.metrics || !c.evaluation) return <><div className="impact-strip">{impact}<div><small>预期变化</small><strong className="review-noafter">尚未评估</strong></div></div><p className="condition">{c.limitation}</p></>;
    if (c.data.direction === 'low_hit') return <div className="impact-strip">{impact}<div><small>预期命中率提升</small><strong className="good">+{ratio(obj(c.metrics.gain_percentage_points))}<em>个百分点</em></strong><span className="explain">{hit(c.evaluation.before)} → {hit(c.evaluation.after)}</span></div></div>;
    return <div className="impact-strip three">{impact}{[['input_tokens', 'p', '输入 Token'], ['compute_tokens', 'c', '计算 Token']].map(([key, field, label]) => {
        const delta = BigInt(str(c.metrics![key + '_delta'])), ratioValue = c.metrics![key + '_ratio'];
        return <div key={key}><small>预期{label}{delta < 0n ? '减少' : delta > 0n ? '增加' : '变化'}</small><strong className={delta < 0n ? 'good' : delta > 0n ? 'caution' : ''}>{delta < 0n ? '−' : delta > 0n ? '+' : ''}{integer(String(delta < 0n ? -delta : delta))}</strong><span className="explain">{integer(str(obj(c.evaluation!.before)[field!]))} → {integer(str(obj(c.evaluation!.after)[field!]))}<br/>{ratioValue ? ratio({ ...obj(ratioValue), numerator: String(BigInt(str(obj(ratioValue).numerator)) < 0n ? -BigInt(str(obj(ratioValue).numerator)) : BigInt(str(obj(ratioValue).numerator))) }, true) + (delta < 0n ? ' 减少' : delta > 0n ? ' 增加' : ' 变化') : '前值为 0，比例不适用'}</span></div>;
    })}</div>;
}
function Caution({ card }: { card: Card }) { return card.data.direction === 'token_content' && card.metrics && BigInt(str(card.metrics.compute_tokens_delta)) > 0n ? <p className="warn-line">计算量增加，该方案不代表计算成本降低。输入与计算 Token 的变化分别展示。</p> : null; }
function Conditions({ card }: { card: Card }) { return <>{card.synthetic && <p className="condition">构造策略验证 · 使用真实离线回放，非生产业务收益。</p>}{card.conditions.length > 0 && <details className="report-detail conditions"><summary>适用前提与说明</summary><div className="a-pad">{card.conditions.map((s, i) => <p key={i}>{s}</p>)}</div></details>}</>; }
export function ReportCards({ api, data, open, more, loading }: { api: AnalysisClient; data: LoadedReport; open: (id: string) => void; more: () => void; loading: boolean }) {
    const groups = data.direction === 'low_hit' ? [['优化建议', data.cards.filter(x => x.kind === 'recommendation')], ['发现的差异', data.cards.filter(x => x.kind === 'difference_group')]] as const : [['Token 优化建议', data.cards]] as const;
    return <>{data.summary.availability === 'not_computed' && <p className="notice">这份历史报告尚未生成新版建议；已发布的差异仍可查看。浏览页面不会重新运行分析。</p>}{groups.map(([title, cards]) => <section key={title}><div className="group-title"><div className="label"><h2>{title}</h2><span>{title === '发现的差异' ? 'L4 / L5 · 发现即可查看' : `已显示 ${cards.length} 项 · 各方案独立对比`}</span></div></div><div className={`solution-grid ${data.direction === 'low_hit' && title === '优化建议' && cards.length === 1 ? 'low-single' : ''}`}>
        {cards.map(c => <article className={`solution-card focus-card ${data.direction === 'low_hit' && c.kind === 'recommendation' && cards.length === 1 ? 'featured' : ''}`} id={`analysis-card-${encodeURIComponent(c.id)}`} tabIndex={-1} key={c.id} data-rule={c.rule}>
            <div className="solution-card-top"><span className="report-type">{c.tag}</span><span className="badge">{c.kind === 'difference_group' ? '差异线索' : c.metrics ? '建议方案' : '未完成评估'}</span></div>
            <h2>{c.title}</h2><p className="solution-description">{c.description}</p><Metrics card={c}/><Caution card={c}/>
            {c.advice && <div className="solution-advice"><small>修改方案</small><p>{c.advice}</p></div>}
            <EvidencePreview api={api} data={data} card={c}/>
            {c.synthetic && <p className="condition">构造策略验证 · 非生产业务收益</p>}{c.kind === 'difference_group' && c.limitation && <p className="scope-note">{c.limitation}</p>}
            <div className="solution-card-foot"><small>{c.kind === 'difference_group' ? '仅记录观察到的差异' : '原报告范围 · 单项离线对比'}</small><button className="btn" onClick={() => open(c.id)}>{c.kind === 'difference_group' ? '查看具体差异' : '查看证据与改法'} →</button></div>
        </article>)}
    </div>{!cards.length && <p className="analysis-status empty-results">{title === '优化建议' ? '当前没有达到展示条件的优化建议。' : title === '发现的差异' ? '本报告暂未提供此类差异结果。' : data.summary.configured_recipe_count === '0' ? '本报告未配置可用的自动修改依据，暂未生成 Token 优化建议。' : '本报告尚未生成 Token 优化建议。'}{data.hasMore ? '可继续加载其余结果。' : ''}</p>}</section>)}{data.hasMore && <button className="btn load-more" onClick={more} disabled={loading}>{loading ? '正在加载…' : '加载更多'}</button>}</>;
}
export function DetectorHelp({ direction }: { direction: LoadedReport['direction'] }) { return <details className="report-detail"><summary>{direction === 'low_hit' ? '低命中率' : 'Token 异常'}：{checks[direction].length} 个探测器 · 查看作用与检查内容</summary><div className="a-pad">{checks[direction].map(([title, desc]) => <p key={title}><strong>{title}</strong><br/>{desc}</p>)}</div></details>; }
export function ReportDetail({ api, data, id, back }: { api: AnalysisClient; data: LoadedReport; id: string; back: () => void }) {
    const [card, setCard] = useState<Card | null>(null), [error, setError] = useState(''), [attempt, setAttempt] = useState(0);
    const title = useRef<HTMLHeadingElement>(null);
    useEffect(() => {
        const c = new AbortController(); setCard(null); setError('');
        const known = data.cards.find(x => x.id === id);
        void (known ? Promise.resolve(known) : getCard(api, data, id, c.signal)).then(value => { if (!c.signal.aborted) setCard(value); }).catch(e => { if (!c.signal.aborted) setError(String(e)); });
        return () => c.abort();
    }, [api, data, id, attempt]);
    useEffect(() => { if (card) { title.current?.focus({ preventScroll: true }); title.current?.scrollIntoView({ block: 'start' }); } }, [card]);
    return <><button className="btn text report-back" onClick={back}>← 返回卡片列表</button>{error && <p role="alert">这项结果读取失败或已不可用。<button className="btn" onClick={() => setAttempt(x => x + 1)}>重新读取</button></p>}{card ? <article className="finding-body detail-summary" data-rule={card.rule}><span className="report-type">{card.tag}</span><div className="detail-top"><h2 tabIndex={-1} ref={title}>{card.title}</h2></div><p>{card.description}</p><Metrics card={card}/><Caution card={card}/><p className="scope-note">{card.kind === 'difference_group' ? '数量为已发现涉及的不同请求；最多展示 3 个例子，例子数不代表全部影响范围。' : `影响请求指采用方案后原文发生变化的请求。预期变化按本报告全部 ${integer(card.total)} 条请求对比，包含未修改请求。`}</p>
        {card.advice && <section className="report-section"><h3>修改方案</h3><p>{card.advice}</p><Conditions card={card}/></section>}
        <section className="report-section"><h3>{card.kind === 'difference_group' ? '具体差异' : '局部证据与具体改法'}</h3><p className="local-note">只展示与本项结果有关的字段、内容和附近上下文。</p><EvidenceDetails api={api} data={data} card={card}/></section>
        {card.kind === 'difference_group' ? <section className="report-section"><h3>如何理解</h3><p>{card.rule === 'L4' ? '这些例子仅说明消息内容存在差异；没有可靠会话关联时，不能据此认定历史被改写。' : '这些例子记录 JSON 的表示差异；本轮不据此估算命中率提升。'}</p></section> : card.metrics && <section className="report-section"><h3>预期效果说明</h3><p>以上为该方案在原报告范围的离线对比。各方案独立计算，收益不能相加；实际变更后可在用户监控查看当前指标。</p></section>}
    </article> : !error && <p role="status">正在读取详情…</p>}</>;
}

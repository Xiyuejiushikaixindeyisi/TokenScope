import { useEffect, useRef, useState } from 'react';
import { arr, obj, str, canonical } from '../../api/analysis/client';
import type { AnalysisClient, Obj } from '../../api/analysis/client';
import { loadCardExamples } from './model';
import type { Card, LoadedReport } from './model';

// Local snippets stay in bounded memory only. Never persist request content to browser storage.
const cache = new WeakMap<AnalysisClient, Map<string, Obj[]>>();
export function useExamples(api: AnalysisClient, data: LoadedReport, card: Card, enabled = true) {
    const [rows, setRows] = useState<Obj[] | null>(null), [error, setError] = useState(''), [attempt, setAttempt] = useState(0);
    useEffect(() => {
        const c = new AbortController(); setRows(null); setError('');
        if (!enabled) return () => c.abort();
        const key = canonical([api.executionVersion, data.direction, data.entry.task_id, data.entry.scope_id, data.entry.report_digest, card.kind, card.id]);
        const saved = cache.get(api)?.get(key);
        const read = saved && !attempt ? Promise.resolve(saved) : loadCardExamples(api, data, card, c.signal);
        void read.then(value => {
            if (c.signal.aborted) return;
            const map = cache.get(api) ?? new Map<string, Obj[]>(); map.delete(key); map.set(key, value);
            while (map.size > 48) map.delete(map.keys().next().value!);
            cache.set(api, map); setRows(value);
        }).catch(e => { if (!c.signal.aborted) setError(String(e)); });
        return () => c.abort();
    }, [api, data.entry.task_id, data.entry.scope_id, data.entry.report_digest, card, attempt, enabled]);
    return { rows, error, retry: () => setAttempt(x => x + 1) };
}
export function excerptText(e: Obj) {
    const raw = str(e.excerpt);
    // Decode a complete JSON string, never parse its embedded JSON/object or reserialize numbers.
    if (raw.startsWith('"') && raw.endsWith('"')) {
        try { const value: unknown = JSON.parse(raw); if (typeof value === 'string') return value; } catch { /* A clipped raw fragment remains literal. */ }
    }
    if (e.source && obj(e.source).embedded) {
        // An embedded JSON slice is still escaped inside the outer request string.
        // Decode that string layer only; never parse or normalize the embedded numbers.
        try { const value: unknown = JSON.parse('"' + raw + '"'); if (typeof value === 'string') return value; } catch { /* Preserve an incomplete escape sequence verbatim. */ }
    }
    return raw;
}
export function locationLabel(e: Obj) {
    const source = obj(e.source), pointer = str(source.source_pointer), message = /^\/messages\/(\d+)(.*)$/.exec(pointer);
    let label = pointer.startsWith('/tools') ? '工具定义' : '相关输入';
    if (message) label = `第 ${BigInt(message[1]!) + 1n} 条消息 · ${message[2]!.includes('arguments') ? '工具调用参数' : message[2]!.includes('content') ? '消息内容' : '消息片段'}`;
    if (source.embedded) { const parts = str(obj(source.embedded).pointer).split('/').filter(Boolean); if (parts.length) label += ` · ${parts.at(-1)!.replaceAll('~1', '/').replaceAll('~0', '~')} 字段`; }
    return label;
}
function ReadFailure({ retry }: { retry: () => void }) { return <p className="local-note" role="alert">局部证据读取失败，问题与收益仍可查看。<button className="btn text" onClick={retry}>重新读取证据</button></p>; }
export function EvidencePreview({ api, data, card }: { api: AnalysisClient; data: LoadedReport; card: Card }) {
    const element = useRef<HTMLDivElement>(null), [visible, setVisible] = useState(false);
    useEffect(() => {
        if (!('IntersectionObserver' in globalThis)) { setVisible(true); return; }
        const observer = new IntersectionObserver(entries => {
            if (entries.some(entry => entry.isIntersecting)) { setVisible(true); observer.disconnect(); }
        }, { rootMargin: '160px' });
        if (element.current) observer.observe(element.current);
        return () => observer.disconnect();
    }, []);
    const result = useExamples(api, data, card, visible), first = result.rows?.[0];
    if (result.error) return <div className="key-evidence" ref={element}><ReadFailure retry={result.retry}/></div>;
    if (!result.rows) return <div className="key-evidence" ref={element} role={visible ? 'status' : undefined}><small>{visible ? '正在读取局部证据…' : '滚动至此处查看局部证据'}</small></div>;
    if (!first) return <div className="key-evidence" ref={element}><small>此报告未保存可展示的局部证据</small></div>;
    const before = obj(first.before);
    const preview = (value: Obj) => {
        const excerpt = excerptText(value);
        const nearby = excerpt !== value.excerpt ? excerpt : Array.from(str(value.context_before)).slice(-45).join('') + excerpt + Array.from(str(value.context_after)).slice(0, 24).join('');
        const characters = Array.from(nearby);
        return characters.slice(0, 150).join('') + (characters.length > 150 ? ' …' : '');
    };
    return <div className="key-evidence" ref={element}><small>证据片段 · {locationLabel(before)}</small><code>{first.comparison ? <>请求 A：{preview(before)}<br/>请求 B：{preview(obj(first.comparison))}</> : preview(before)}</code></div>;
}
function Pane({ label, value }: { label: string; value: Obj }) {
    const decoded = excerptText(value), isDecoded = decoded !== value.excerpt;
    const located = value.raw_span !== null && arr(value.reason_codes).length === 0;
    const selected = located && !isDecoded && (obj(value.source).text_range !== null || value.decoded_span !== null);
    const incomplete = arr(value.reason_codes).length > 0;
    return <div className="evidence-pane"><small>{label} · {locationLabel(value)}</small><pre className="report-code" tabIndex={0}>{!isDecoded && str(value.context_before)}{decoded === '' && located ? <span className="empty-excerpt">（此处为空）</span> : selected ? <mark>{decoded}</mark> : decoded}{!isDecoded && str(value.context_after)}</pre><span className="omission">{incomplete ? '该位置未能完整定位，保留可读取片段。' : isDecoded ? '展示原文字符串内容，保留空白与数值写法。' : '仅展示相关片段与附近原文。'}{(value.omitted_before === true || value.omitted_after === true) && '其余内容已省略。'}</span></div>;
}
export function EvidenceDetails({ api, data, card }: { api: AnalysisClient; data: LoadedReport; card: Card }) {
    const result = useExamples(api, data, card);
    if (result.error) return <ReadFailure retry={result.retry}/>;
    if (!result.rows) return <p role="status">正在读取局部证据…</p>;
    if (!result.rows.length) return <p className="local-note">此报告未保存可展示的局部证据；当前建议与预期变化按已发布结果保留。</p>;
    return <>{result.rows.map((ex, i) => <details className="example-block" open={i === 0} key={str(ex.example_id)}>
        <summary className="example-caption"><strong>例子 {i + 1}</strong><span>展开 / 收起相关片段</span></summary>
        {ex.comparison ? <><p className="local-note">问题证据 · 两个请求的原内容对照</p><div className="diff-grid"><Pane label={`请求 A · 第 ${str(obj(obj(obj(ex.before).source).request_key).source_record_index)} 条`} value={obj(ex.before)}/><Pane label={`请求 B · 第 ${str(obj(obj(obj(ex.comparison).source).request_key).source_record_index)} 条`} value={obj(ex.comparison)}/></div></> : null}
        {ex.after ? <><p className="local-note">建议修改前后 · 同一个请求的对照</p><div className="diff-grid before-after"><Pane label="修改前" value={obj(ex.before)}/><Pane label="按建议修改后" value={obj(ex.after)}/></div></> : !ex.comparison ? <Pane label="问题证据 · 原始内容" value={obj(ex.before)}/> : null}
    </details>)}</>;
}

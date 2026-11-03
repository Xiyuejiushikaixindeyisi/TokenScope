import { useEffect, useRef, useState } from 'react';
import { segment, type V2Client } from '../../api/v2/client';
import type { Receipt, Evaluation, Scenario, BatchScenario } from '../../api/v2/generated/user';
import type { DefaultConfig } from '../../api/v2/generated/user/HV2DefaultConfig';
import type { AutoEvaluation } from '../../api/v2/generated/user/HV2AutoEvaluation';
import { Modal, errorText, fields, percent } from './common';
import { decimalText } from './numbers';
type Props = { api: V2Client; receipt: Receipt; appid: string; p90?: string | undefined; count?: string | undefined };
type Conditions = { target_seconds: string; waiting_seconds: string; chunk_tokens: string };
const statuses = { reference: '参考估算', reference_with_limit: '参考估算 · 完全复用可行性未证实', no_budget: '无计算预算', out_of_scope: '超出适用范围', unavailable: '暂不可评估' };
export function TTFT(props: Props) {
    return <TTFTScope key={JSON.stringify([props.api.instance, props.receipt.user_run_id, props.receipt.index_revision, props.appid, props.receipt.model_id, props.receipt.common_name])} {...props}/>;
}
function ResultDetails({ value }: { value: Evaluation }) {
    return <><p>{statuses[value.status]} · {value.reason}</p><p>精确比例 {value.required_hit_fraction ? `${value.required_hit_fraction.numerator}/${value.required_hit_fraction.denominator}` : '—'} · 可计算Token {value.computable_tokens ?? '—'} · 块数 {value.allowed_chunks ?? '—'}</p><p>T={value.request.target_seconds}s · W={value.request.waiting_seconds}s · {value.request.comparator === 'lt' ? '＜' : '≤'} · K={value.scenario.chunk_tokens} · τ={value.scenario.chunk_seconds}s · P90={value.prompt_p90 ?? '—'}{'overhead_seconds' in value.scenario ? ` · 历史O=${value.scenario.overhead_seconds}s` : ''}</p>{value.limitations.map(x => <p key={x}>{x}</p>)}</>;
}
function TTFTScope({ api, receipt, appid, p90, count }: Props) {
    const [conditions, setConditions] = useState<Conditions>({ target_seconds: '', waiting_seconds: '', chunk_tokens: '' });
    const [config, setConfig] = useState<DefaultConfig | null>(null), [result, setResult] = useState<AutoEvaluation | null>(null);
    const [history, setHistory] = useState<AutoEvaluation | Evaluation | null>(null), [scenario, setScenario] = useState<Scenario | BatchScenario | null>(null);
    const [modal, setModal] = useState(false), [error, setError] = useState(''), [busy, setBusy] = useState(false), [defaultsBusy, setDefaultsBusy] = useState(false);
    const task = useRef<AbortController | null>(null), defaultsTask = useRef<AbortController | null>(null), generation = useRef(0);
    const intent = useRef<{ signature: string; body: Record<string, string> } | null>(null);
    const intentKey = `tokenscope.v2.auto-ttft:${api.instance}:${receipt.user_run_id}:${receipt.index_revision}:${appid}`;
    function invalidate() { generation.current++; task.current?.abort(); setBusy(false); setResult(null); setError(''); }
    function change(next: Conditions) { invalidate(); setConditions(next); intent.current = null; try { localStorage.removeItem(intentKey); } catch { /* in-memory retry remains available */ } }
    async function defaults() {
        invalidate(); defaultsTask.current?.abort();
        const controller = new AbortController(); defaultsTask.current = controller;
        setDefaultsBusy(true); setConfig(null);
        try {
            const page = await api.request('user', 'DefaultPage', '/ttft/defaults', { signal: controller.signal, query: { model_id: receipt.model_id, common_name: receipt.common_name } });
            if (controller.signal.aborted) return;
            if (page.configs.length > 1 || page.configs.some(c => c.model_id !== receipt.model_id || c.common_name !== receipt.common_name)) throw Error('默认参数模型范围不一致');
            const value = page.configs[0] ?? null;
            setConfig(value);
            if (!value || value.chunk_seconds === null) setError('当前模型未配置τ，暂不可计算；不会借用其他模型参数');
        } catch (e) { if (!controller.signal.aborted) setError(errorText(e)); }
        finally { if (defaultsTask.current === controller) setDefaultsBusy(false); }
    }
    useEffect(() => {
        try {
            const saved = JSON.parse(localStorage.getItem(intentKey) ?? 'null') as typeof intent.current;
            if (saved?.body.user_run_id === receipt.user_run_id && saved.body.appid === appid && saved.body.index_revision === receipt.index_revision && saved.body.submission_key) {
                intent.current = saved;
                setConditions({ target_seconds: saved.body.target_seconds ?? '', waiting_seconds: saved.body.waiting_seconds ?? '', chunk_tokens: saved.body.chunk_tokens ?? '' });
            }
        } catch { /* Invalid local data cannot select a model or supply defaults. */ }
        void defaults();
        return () => { generation.current++; task.current?.abort(); defaultsTask.current?.abort(); };
        // The outer component keys the complete data/model/service identity.
    }, []);
    async function evaluate() {
        invalidate(); const token = generation.current, controller = new AbortController(); task.current = controller; setBusy(true);
        try {
            if (receipt.state !== 'ready' || !receipt.index_revision || !config || config.chunk_seconds === null) throw Error('当前索引或模型参数不可用');
            const inputs: Record<string, string> = { user_run_id: receipt.user_run_id, appid, index_revision: receipt.index_revision, target_seconds: decimalText(conditions.target_seconds), waiting_seconds: decimalText(conditions.waiting_seconds), comparator: 'le', default_revision: config.revision };
            if (conditions.chunk_tokens.trim()) inputs.chunk_tokens = decimalText(conditions.chunk_tokens, true, true);
            const signature = JSON.stringify(inputs);
            const saved = intent.current?.signature === signature ? intent.current : { signature, body: { ...inputs, submission_key: crypto.randomUUID() } };
            intent.current = saved;
            try { localStorage.setItem(intentKey, JSON.stringify(saved)); } catch { /* No automatic POST on storage failure. */ }
            const value = await api.request('user', 'AutoEvaluation', '/ttft/evaluations', { body: saved.body, signal: controller.signal });
            if (token !== generation.current || controller.signal.aborted) return;
            if (Object.entries(saved.body).some(([k, v]) => (value.request as unknown as Record<string, unknown>)[k] !== v) || value.source.base_run_id !== receipt.base_run_id || value.evaluation_id !== value.evaluation.evaluation_id || value.source.user_run_id !== receipt.user_run_id || value.source.index_revision !== receipt.index_revision || value.source.model_id !== receipt.model_id || value.source.common_name !== receipt.common_name || value.defaults.revision !== config.revision || value.defaults.model_id !== receipt.model_id || value.defaults.common_name !== receipt.common_name || ['submission_key', 'target_seconds', 'waiting_seconds', 'comparator'].some(k => (value.evaluation.request as unknown as Record<string, unknown>)[k] !== saved.body[k]) || value.evaluation.request.appid !== appid || value.evaluation.request.user_run_id !== receipt.user_run_id || value.evaluation.service_instance_id !== api.instance) throw Error('评估数据或参数范围不一致');
            setResult(value); setModal(false);
        } catch (e) { if (token === generation.current && !controller.signal.aborted) setError(errorText(e)); }
        finally { if (token === generation.current) setBusy(false); }
    }
    async function readHistory(form: HTMLFormElement) {
        invalidate(); const token = generation.current, controller = new AbortController(); task.current = controller; setBusy(true); setHistory(null); setScenario(null);
        const values = fields(form);
        try {
            if (values.kind === 'scenario') {
                const value = await api.request('user', 'Scenario', `/scenarios/${segment(values.id!)}/${segment(values.revision!)}`, { signal: controller.signal });
                if (value.scenario_id !== values.id || value.revision !== values.revision) throw Error('历史情景身份不一致');
                if (token === generation.current) setScenario(value);
            } else {
                const value = values.kind === 'legacy' ? await api.request('user', 'Evaluation', `/evaluations/${segment(values.id!)}`, { signal: controller.signal }) : await api.request('user', 'AutoEvaluation', `/ttft/evaluations/${segment(values.id!)}`, { signal: controller.signal });
                if (value.evaluation_id !== values.id) throw Error('历史评估身份不一致');
                if (token === generation.current) setHistory(value);
            }
        } catch (e) { if (token === generation.current && !controller.signal.aborted) setError(errorText(e)); }
        finally { if (token === generation.current) setBusy(false); }
    }
    const value = result?.evaluation;
    const canEvaluate = receipt.state === 'ready' && !!receipt.index_revision && config?.chunk_seconds != null && conditions.waiting_seconds.trim() !== '' && conditions.target_seconds.trim() !== '' && !busy && !defaultsBusy;
    return <><section className="panel ttft-panel"><div className="panel-head"><div><h2>P90长度请求所需参考前缀命中率</h2><p>{appid} × {receipt.common_name} · 性能校准待完成</p></div><button className="linkbutton" onClick={() => setModal(true)}>设置评估条件</button></div><div className="ttft-body"><div><label>首Token目标（秒）<div className="ttft-target-row"><span>≤</span><input aria-label="TTFT目标秒" inputMode="decimal" value={conditions.target_seconds} onChange={e => change({ ...conditions, target_seconds: e.target.value })}/></div></label><label>首Token前非计算耗时 W（秒）<input aria-label="非计算耗时W" inputMode="decimal" value={conditions.waiting_seconds} onChange={e => change({ ...conditions, waiting_seconds: e.target.value })}/></label><button disabled={!canEvaluate} onClick={() => void evaluate()}>{busy ? '评估中…' : '评估'}</button><small>{config ? `模型默认 revision ${config.revision}` : '模型默认参数不可用'}</small></div><div><span className="mini-label">所需参考前缀命中率</span><strong>{percent(value?.required_hit_rate)}</strong><small>{value ? statuses[value.status] : '待评估 · 条件变化后需重新评估'}</small></div><div><span className="mini-label">P90模板后输入长度</span><strong className="ttft-length">{value ? value.prompt_p90 ?? '—' : p90 ?? '—'}</strong><small>本组 {value?.request_count ?? count ?? '—'} 条 · 由服务读取当前范围</small></div></div><div className="ttft-foot">{value && result && <><ResultDetails value={value}/><p>评估ID {result.evaluation_id} · 参数revision {result.defaults.revision} · {result.chunk_tokens_origin === 'model_default' ? '模型默认K' : '本次覆盖K'} · τ未缩放</p></>}<p>W覆盖首Token前全部非计算耗时，不含GF发出前GB排队，不重复扣O。空值不是0；用户提供默认参数尚未校准，参考比例不保证生产SLO。</p>{error && <p role="alert">{error}</p>}</div></section>
    {modal && <Modal title="评估条件" close={() => setModal(false)}><div className="v2-form"><label>可选每块Token数 K<input aria-label="覆盖K" inputMode="numeric" value={conditions.chunk_tokens} placeholder={config?.chunk_tokens} onChange={e => change({ ...conditions, chunk_tokens: e.target.value })}/></label><button onClick={() => change({ ...conditions, chunk_tokens: '' })}>恢复模型默认K</button><p>更改K不会缩放τ，是否适用由后端结果的限制说明给出。</p><button disabled={defaultsBusy} onClick={() => void defaults()}>刷新模型默认参数</button>{config && <details open><summary>默认参数来源与版本</summary><p>K={config.chunk_tokens} · τ={config.chunk_seconds ?? '未配置'}s · τ适用K={config.tau_reference_chunk_tokens} · revision={config.revision}</p><p>用户提供 · {config.source_description} · 尚未校准</p></details>}<button disabled={!canEvaluate} onClick={() => void evaluate()}>按当前条件评估</button></div><details><summary>历史评估与情景（只读）</summary><form onSubmit={e => { e.preventDefault(); void readHistory(e.currentTarget); }}><label>历史类型<select name="kind"><option value="auto">自动评估</option><option value="legacy">旧评估（含lt/W+O）</option><option value="scenario">旧情景</option></select></label><label>历史ID<input name="id" required/></label><label>情景版本（读取情景时填写）<input name="revision"/></label><button disabled={busy}>读取历史</button></form>{history && <article className="notice"><h3>只读快照 · {history.evaluation_id}</h3><p>运行 {history.request.user_run_id} · APPID {history.request.appid}</p><ResultDetails value={'evaluation' in history ? history.evaluation : history}/>{'defaults' in history && <p>原参数revision {history.defaults.revision} · 原索引 {history.source.index_revision}</p>}</article>}{scenario && <article className="notice"><h3>历史情景 · 只读</h3><pre>{JSON.stringify(scenario, null, 2)}</pre></article>}</details>{error && <p role="alert">{error}</p>}</Modal>}</>;
}

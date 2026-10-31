import { useEffect, useRef, useState } from 'react';
import type { V2Client } from '../../api/v2/client';
import { segment } from '../../api/v2/client';
import type { Receipt, Scenario, BatchScenario, Evaluation } from '../../api/v2/generated/user';
import { V2Records } from '../../storage/v2-records';
import { Modal, errorText, fields, percent } from './common';
import { decimalText, compareDecimal } from './numbers';
type Conditions = {
    scenario_id: string;
    scenario_revision: string;
    target_seconds: string;
    waiting_seconds: string;
    comparator: 'le' | 'lt';
};
const blank: Conditions = { scenario_id: '', scenario_revision: '', target_seconds: '', waiting_seconds: '', comparator: 'le' };
const statuses = { reference: '参考估算', reference_with_limit: '参考估算 · 完全复用可行性未证实', no_budget: '无计算预算', out_of_scope: '超出适用范围', unavailable: '暂不可评估' };
export function TTFT({ api, receipt, appid, p90, count }: {
    api: V2Client;
    receipt: Receipt;
    appid: string;
    p90?: string | undefined;
    count?: string | undefined;
}) {
    const [conditions, setConditions] = useState<Conditions>(blank), [scenario, setScenario] = useState<Scenario | BatchScenario | null>(null), [result, setResult] = useState<Evaluation | null>(null), [history, setHistory] = useState<Evaluation | null>(null);
    const [modal, setModal] = useState(false), [register, setRegister] = useState(false), [busy, setBusy] = useState(false), [error, setError] = useState(''), [recent, setRecent] = useState<{
        id: string;
        revision: string;
    }[]>([]);
    const generation = useRef(0), intent = useRef<{
        body: Record<string, string>;
        signature: string;
    } | null>(null);
    const records = useRef(new V2Records(api.instance, 'user'));
    const intentKey = `tokenscope.v2.ttft:${api.instance}:${receipt.user_run_id}:${appid}`;
    useEffect(() => { try {
        setRecent(records.current.read().scenarios);
        const raw = localStorage.getItem(intentKey);
        if (raw) {
            const saved = JSON.parse(raw) as {
                body: Record<string, string>;
                signature: string;
            };
            if (saved.body?.user_run_id === receipt.user_run_id && saved.body.appid === appid && typeof saved.body.submission_key === 'string') {
                intent.current = saved;
                setConditions({ scenario_id: saved.body.scenario_id!, scenario_revision: saved.body.scenario_revision!, target_seconds: saved.body.target_seconds!, waiting_seconds: saved.body.waiting_seconds!, comparator: saved.body.comparator === 'lt' ? 'lt' : 'le' });
            }
        }
    }
    catch (e) {
        setError(errorText(e));
    } return () => { generation.current++; }; }, [intentKey, receipt.user_run_id, appid]);
    function change(next: Conditions) { generation.current++; setConditions(next); setResult(null); setError(''); setBusy(false); intent.current = null; try {
        localStorage.removeItem(intentKey);
    }
    catch { /* existing record remains recoverable */ } if (next.scenario_id !== conditions.scenario_id || next.scenario_revision !== conditions.scenario_revision)
        setScenario(null); }
    async function openScenario(id: string, revision: string) { const token = ++generation.current; setBusy(true); setError(''); setResult(null); try {
        const s = await api.request('user', 'Scenario', `/scenarios/${segment(id)}/${segment(revision)}`);
        if (token !== generation.current)
            return;
        if (s.scenario_id !== id || s.revision !== revision)
            throw Error('情景身份不一致');
        setScenario(s);
        setConditions(c => ({ ...c, scenario_id: id, scenario_revision: revision }));
        const data = records.current.read();
        const entries = [{ id, revision }, ...data.scenarios.filter(x => x.id !== id || x.revision !== revision)].slice(0, 50);
        records.current.write({ ...data, scenarios: entries });
        setRecent(entries);
    }
    catch (e) {
        if (token === generation.current)
            setError(errorText(e));
    }
    finally {
        if (token === generation.current)
            setBusy(false);
    } }
    async function create(form: HTMLFormElement) { const token = ++generation.current; setBusy(true); setError(''); try {
        const raw = fields(form);
        const body: Record<string, string> = { ...raw, timing_model: 'batch_reference_total_noncompute_v1', model_id: receipt.model_id, common_name: receipt.common_name, source: 'user_assumption', chunk_tokens: decimalText(raw.chunk_tokens!, true, true), chunk_seconds: decimalText(raw.chunk_seconds!, true) };
        for (const k of Object.keys(body))
            if (body[k] === '')
                delete body[k];
        for (const k of ['min_prompt_tokens', 'max_prompt_tokens', 'sample_count'])
            if (body[k])
                body[k] = decimalText(body[k]!, k === 'sample_count', true);
        if (body.min_prompt_tokens && body.max_prompt_tokens && compareDecimal(body.min_prompt_tokens, body.max_prompt_tokens) > 0)
            throw Error('适用长度下限不能大于上限');
        const s = await api.request('user', 'Scenario', '/scenarios', { body });
        if (token === generation.current) {
            setRegister(false);
            await openScenario(s.scenario_id, s.revision);
        }
    }
    catch (e) {
        if (token === generation.current)
            setError(errorText(e));
    }
    finally {
        if (token === generation.current)
            setBusy(false);
    } }
    async function evaluate() { const token = ++generation.current; setBusy(true); setError(''); setResult(null); try {
        if (receipt.state !== 'ready')
            throw Error('索引尚未就绪');
        if (!scenario || !('timing_model' in scenario))
            throw Error('请读取新模型情景；旧口径仅用于历史查阅');
        if (scenario.model_id !== receipt.model_id || scenario.common_name !== receipt.common_name)
            throw Error('情景与当前模型服务不匹配');
        const inputs = { ...conditions, target_seconds: decimalText(conditions.target_seconds, true), waiting_seconds: decimalText(conditions.waiting_seconds), user_run_id: receipt.user_run_id, appid };
        const signature = JSON.stringify(inputs);
        const saved = intent.current?.signature === signature ? intent.current : { signature, body: { ...inputs, submission_key: crypto.randomUUID() } };
        intent.current = saved;
        localStorage.setItem(intentKey, JSON.stringify(saved));
        const value = await api.request('user', 'Evaluation', '/evaluations', { body: saved.body });
        if (token !== generation.current)
            return;
        if (value.request.user_run_id !== receipt.user_run_id || value.request.appid !== appid || value.request.submission_key !== saved.body.submission_key)
            throw Error('评估范围不一致');
        setResult(value);
        setModal(false);
    }
    catch (e) {
        if (token === generation.current)
            setError(errorText(e));
    }
    finally {
        if (token === generation.current)
            setBusy(false);
    } }
    async function openHistory(id: string) { const token = ++generation.current; setBusy(true); setError(''); try {
        const value = await api.request('user', 'Evaluation', `/evaluations/${segment(id)}`);
        if (token === generation.current) {
            if (value.evaluation_id !== id)
                throw Error('历史评估身份不一致');
            setHistory(value);
        }
    }
    catch (e) {
        if (token === generation.current)
            setError(errorText(e));
    }
    finally {
        if (token === generation.current)
            setBusy(false);
    } }
    const isNew = scenario && 'timing_model' in scenario;
    const canEvaluate = receipt.state === 'ready' && isNew && conditions.target_seconds.trim() !== '' && conditions.waiting_seconds.trim() !== '' && !busy;
    return <><section className="panel ttft-panel"><div className="panel-head"><div><h2>P90长度请求所需参考前缀命中率</h2><p>{appid} × {receipt.common_name} · 代码完成，性能校准待完成</p></div><button className="linkbutton" onClick={() => setModal(true)}>设置评估条件</button></div><div className="ttft-body"><div><label>首Token目标（秒）<div className="ttft-target-row"><select aria-label="TTFT比较符" value={conditions.comparator} onChange={e => change({ ...conditions, comparator: e.target.value as 'le' | 'lt' })}><option value="le">≤</option><option value="lt">＜</option></select><input aria-label="TTFT目标秒" inputMode="decimal" value={conditions.target_seconds} onChange={e => change({ ...conditions, target_seconds: e.target.value })}/></div></label><button disabled={!canEvaluate} onClick={() => void evaluate()}>{busy ? '评估中…' : '评估'}</button><small>{scenario ? `${scenario.scenario_id} / ${scenario.revision}` : '尚未选择情景'}</small></div><div><span className="mini-label">所需参考前缀命中率</span><strong>{percent(result?.required_hit_rate)}</strong><small>{result ? statuses[result.status] : '待评估 · 条件变化后需重新评估'}</small></div><div><span className="mini-label">P90模板后输入长度</span><strong className="ttft-length">{result?.prompt_p90 ?? p90 ?? '—'}</strong><small>本组 {result?.request_count ?? count ?? '—'} 条 · 由服务读取当前范围</small></div></div><div className="ttft-foot">{result ? <><p>{result.reason} · 可计算Token {result.computable_tokens ?? '—'} · 块数 {result.allowed_chunks ?? '—'}</p>{result.limitations.map(x => <p key={x}>{x}</p>)}<p>T={result.request.target_seconds}s，W={result.request.waiting_seconds}s，K={result.scenario.chunk_tokens}，τ={result.scenario.chunk_seconds}s · 评估ID {result.evaluation_id}</p></> : <p>W覆盖首Token前全部非计算耗时（含等待等），不含GF发出前GB排队。K/τ需明确输入；此参考不保证生产SLO。</p>}<p>人工W与实测τ组合仍为假设情景。{scenario?.min_prompt_tokens == null || scenario.max_prompt_tokens == null ? '适用范围未验证。' : ''}不能与聚合理想命中率直接判达标。</p>{error && <p role="alert">{error}</p>}</div></section>
 {modal && <Modal title={register ? '登记新情景' : '评估条件'} close={() => { setModal(false); setRegister(false); }}>{register ? <form className="v2-form" onSubmit={e => { e.preventDefault(); void create(e.currentTarget); }}><p>当前服务 {receipt.common_name} · {receipt.model_id} · 人工假设。更改口径或τ必须新revision。</p>{[['scenario_id', '情景ID'], ['revision', '版本'], ['deployment', '固定部署配置'], ['source_description', '假设或测量来源说明'], ['chunk_tokens', '每块Token数 K（明确整数）'], ['chunk_seconds', '每块耗时 τ（秒）']].map(([k, label]) => <label key={k}>{label}<input name={k} required maxLength={4096}/></label>)}<details><summary>选填证据与适用范围</summary>{[['min_prompt_tokens', '最小模板后Token'], ['max_prompt_tokens', '最大模板后Token'], ['sample_count', '样本数'], ['evidence_sha256', '证据SHA256'], ['workload_description', '工作负载'], ['thinking_mode', 'Thinking模式'], ['calibration_notes', '校准说明']].map(([k, label]) => <label key={k}>{label}<input name={k} maxLength={4096}/></label>)}</details><div><button type="button" onClick={() => setRegister(false)}>返回条件</button><button className="primary" disabled={busy}>登记情景</button></div></form> : <><div className="v2-form"><label>情景ID<input aria-label="情景ID" value={conditions.scenario_id} onChange={e => change({ ...conditions, scenario_id: e.target.value })}/></label><label>情景版本<input aria-label="情景版本" value={conditions.scenario_revision} onChange={e => change({ ...conditions, scenario_revision: e.target.value })}/></label><button disabled={busy || !conditions.scenario_id || !conditions.scenario_revision} onClick={() => void openScenario(conditions.scenario_id, conditions.scenario_revision)}>读取情景</button><button onClick={() => setRegister(true)}>新建情景</button><label>首Token前非计算耗时预算（含等待等）W，秒<input aria-label="非计算耗时W" value={conditions.waiting_seconds} onChange={e => change({ ...conditions, waiting_seconds: e.target.value })}/></label></div>{scenario && <p>{isNew ? '总非计算耗时口径' : '历史W+O口径，只读，不用于新评估'} · K={scenario.chunk_tokens} · τ={scenario.chunk_seconds}s · {scenario.source_description}</p>}{recent.length > 0 && <details><summary>本机最近情景</summary>{recent.map(s => <button className="v2-record" key={`${s.id}/${s.revision}`} onClick={() => void openScenario(s.id, s.revision)}>{s.id} / {s.revision}</button>)}</details>}<button className="primary" disabled={!canEvaluate} onClick={() => void evaluate()}>按当前条件评估</button><form onSubmit={e => { e.preventDefault(); void openHistory(fields(e.currentTarget).evaluation_id!); }}><label>历史评估ID<input name="evaluation_id" required/></label><button disabled={busy}>读取历史评估</button></form>{history && <article className="notice"><h3>{'timing_model' in history.scenario ? '历史总非计算耗时口径' : '历史W+O口径'} · 只读快照</h3><p>运行 {history.request.user_run_id} · APPID {history.request.appid}</p><p>{statuses[history.status]} · {percent(history.required_hit_rate)} · {history.reason}</p><p>T={history.request.target_seconds}s · W={history.request.waiting_seconds}s · {'overhead_seconds' in history.scenario ? `O=${history.scenario.overhead_seconds}s · ` : ''}K={history.scenario.chunk_tokens} · τ={history.scenario.chunk_seconds}s · P90={history.prompt_p90 ?? '—'}</p>{history.limitations.map(x => <p key={x}>{x}</p>)}</article>}</>}{error && <p role="alert">{error}</p>}</Modal>}</>;
}

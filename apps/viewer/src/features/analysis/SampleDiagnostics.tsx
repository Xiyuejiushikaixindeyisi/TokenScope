import { useEffect, useRef, useState } from 'react';
import { arr, obj, str, text, type Obj } from '../../api/analysis/client';
import { SampleClient3, integer, ratio, verifySampleCapabilities } from '../../api/analysis/sample-v3';

const labels: Record<string, string> = { positive: '参考提升', zero: '实算无提升', negative: '实算下降', no_targets: '无适用对象', no_op: '没有需要修改的内容', unavailable: '不可用', budget_exhausted: '预算不足', cancelled: '已取消', failed: '计算失败', not_evaluated: '未评估', queued: '排队中', running: '计算中', completed: '任务完成', stopped: '已停止', interrupted: '任务中断' };
const terminal = (value: Obj) => !['queued', 'running'].includes(str(value.state));
const pause = () => new Promise(resolve => window.setTimeout(resolve, 700));

function pinnedTask(instance: string, task?: string): string | null {
  try {
    const key = `sample-v3:${instance}`;
    if (task !== undefined) sessionStorage.setItem(key, task);
    return sessionStorage.getItem(key);
  } catch { return null; }
}

export function SampleReport({ report }: { report: Obj }) {
  const sample = obj(report.sample), decision = obj(sample.decision), source = obj(obj(sample.parent_scope).source);
  const windows = arr(decision.windows).map(obj), count = windows.reduce((n, w) => n + BigInt(arr(w.members).length), 0n);
  return <section className="panel sample-report" aria-label="小样本实算报告">
    <h2>{arr(report.recommendations).some(r => obj(obj(r).finding).rule_version === 'clock-3.1') ? 'session_clock 固定化及其他改法' : '低命中率改法'} · 样本参考结果</h2>
    <p>{text(obj(sample.parent_scope).appid)} · {text(source.model_id)} · {text(report.task_id)}</p>
    <p>{count < integer(decision.parent_count) ? '已自动缩样' : '当前来源在样本上限内'}：来源 {text(decision.parent_count)} 条，实际选取 {String(count)} 条；排除 {text(decision.excluded_count)} 条。</p>
    <p>抽样依据：请求数、原文大小和 Token 总量上限；排除原因：{Object.entries(obj(decision.exclusion_counts)).map(([key, value]) => `${key}=${text(value)}`).join("、") || "无"}。各窗口独立从空缓存回放，结果不代表全量业务收益。</p>
    {windows.map(w => { const members = arr(w.members).map(obj); return <p key={str(w.role)}>{w.role === 'discovery' ? 'A 发现窗口' : 'B 独立复核窗口'}：{members.length} 条，时间戳范围 {text(members[0]?.time_ns)} — {text(members.at(-1)?.time_ns)} ns。</p>; })}
    <p className="notice">{text(report.business_note)}</p>
    {obj(report.discovery).complete !== true && <p role="status">候选覆盖未完成：{arr(obj(report.discovery).reason_codes).map(text).join('、')}。已观察人数只是下界。</p>}
    {!arr(report.recommendations).length && <p>{arr(obj(report.discovery).findings).length ? '已发现可执行差异，评估尚未完成；请查看任务状态。' : '当前已检查样本没有发现可用的改法证据，不等于业务没有优化空间。'}</p>}
    {arr(report.recommendations).map(obj).map(recommendation => {
      const finding = obj(recommendation.finding), comparison = obj(finding.comparison), evaluated = arr(recommendation.windows).map(obj);
      return <article className="report-detail" key={str(finding.finding_id)}>
        <h3>{finding.rule_version === 'clock-3.1' ? '自动发现 L1 → 固定 session_clock 内容为 NORMALIZED' : `自动发现 ${text(finding.rule_id)} → ${obj(finding.recipe).kind === 'sort_tools' ? '固定工具排列' : '删除动态槽（' + text(obj(finding.recipe).pattern) + '）'}`}</h3>
        <p>请求对：{text(obj(comparison.left).source_record_index)} → {text(obj(comparison.right).source_record_index)}；实际 Token 公共前缀 {text(comparison.lcp_tokens)}。</p>
        {arr(finding.right_locations).map(obj).map((location, i) => <div key={i}><p>精确位置：<code>{text(location.source_pointer)}</code>{location.text_range ? `，字符范围 ${text(obj(location.text_range).start)}–${text(obj(location.text_range).end)}` : '（字段原值守卫）'}</p>
          <div className="sample-diff"><div>修改前<pre>{text(arr(finding.before_fragments)[i])}</pre></div><div>修改后<pre>{text(arr(finding.after_fragments)[i])}</pre></div></div></div>)}
        <p>{text(finding.advice)}</p>{finding.evidence_status === 'source_change_input_identical' && <p>原文有差异，但编码输入相同；不认定输入失配，以下按实际样本计算。</p>}
        {evaluated.map(w => <section key={str(w.role)} aria-label={w.role === 'discovery' ? 'A 实算' : 'B 复核'}>
          <h4>{w.role === 'discovery' ? 'A 同样本实算' : 'B 独立复核'}：{labels[str(w.status)] ?? text(w.status)}</h4>
          {w.complete === true ? <><p>样本 {text(w.n)} 条；匹配 {text(w.matched)} 条；修改 {text(w.modified)} 条。</p>
            <table><thead><tr><th>指标</th><th>修改前</th><th>修改后</th></tr></thead><tbody>{['p', 'h', 'c'].map(k => <tr key={k}><th>{k.toUpperCase()}</th><td>{text(obj(w.before)[k])}</td><td>{text(obj(w.after)[k])}</td></tr>)}
              <tr><th>命中率</th>{[obj(w.before), obj(w.after)].map((m, i) => <td key={i}>{ratio(String(integer(m.h) * 100n), m.p)}%</td>)}</tr></tbody></table>
            <p><strong>参考提升率：{w.improvement_pp ? `${ratio(obj(w.improvement_pp).numerator, obj(w.improvement_pp).denominator)} 个百分点` : '分母为零，不可计算'}</strong></p></> : <p>本窗口没有完整实算结果：{text(w.reason_code)}。不使用 0 代替未评估。</p>}
          <small>评估引用：{text(w.rows_ref)}</small>
        </section>)}
        {!evaluated.some(w => w.role === 'review') && <p>B 独立复核未完成；只保留已完成的 A 结果。</p>}
        <details><summary>证据身份</summary><p>finding：{text(finding.finding_id)}</p><p>冻结改法摘要：{text(recommendation.transformation_digest)}</p><p>样本：{text(report.sample_id)}；manifest：{text(report.manifest_sha256)}</p></details>
      </article>;
    })}
    <details><summary>L1/L2/L3/L4/L5 差异请求对照</summary>{arr(obj(report.discovery).cause_groups).map(obj).map(g => {
      const pair = obj(g.comparison ?? {}), records = arr(obj(report.discovery).evidence_requests ?? []).map(obj);
      const sides = ['left', 'right'].map(side => records.find(r => str(obj(r.request_key).base_run_id) === str(obj(pair[side]).base_run_id) && str(obj(r.request_key).source_record_index) === str(obj(pair[side]).source_record_index)));
      return <details className="sample-evidence" key={str(g.group_id)}><summary>{text(g.rule_id)} · {arr(g.pointers).map(text).join('、')} · 已观察 {arr(g.members).length} 个请求</summary>
        <p>仅代表请求对证据，不推断会话关系；实际 Token 公共前缀 {text(g.lcp_tokens)}。</p>
        {sides.every(Boolean) ? <div className="sample-diff">{sides.map((record, i) => <div key={i}>请求 {i === 0 ? 'A' : 'B'} · 第 {text(obj(record?.request_key).source_record_index)} 条<p>SHA256：{text(record?.raw_sha256)}</p><pre tabIndex={0}>{text(record?.raw_body)}</pre></div>)}</div> : <p>这份历史结果未保存完整请求对照，不以路径摘要替代原文。</p>}
      </details>;
    })}</details>
  </section>;
}

export function SampleDiagnostics() {
  const [client, setClient] = useState<SampleClient3 | null>(null), [sources, setSources] = useState<Obj[]>([]), [sourceIndex, setSourceIndex] = useState('0');
  const [tasks, setTasks] = useState<Obj[]>([]), [selected, setSelected] = useState(''), [report, setReport] = useState<Obj | null>(null);
  const [enabled, setEnabled] = useState(false), [filter, setFilter] = useState(""), [next, setNext] = useState<string | null>(null);
  const [error, setError] = useState(''), [status, setStatus] = useState('正在读取小样本分析入口'), [busy, setBusy] = useState(false);
  const [current, setCurrent] = useState<{ path: string; id: string } | null>(null);
  const live = useRef(true), cancelled = useRef(false), selectedRef = useRef('');
  const readReport = async (api: SampleClient3, id: string) => {
    selectedRef.current = id; setSelected(id); setError('');
    try { const result = await api.report(id); if (live.current && selectedRef.current === id) setReport(result); }
    catch (e) { if (live.current) setError(`读取失败，保留已读结果：${String(e)}`); }
  };
  const history = async (api: SampleClient3, offset = "0") => {
    const page = await api.request('/diagnostics/v3/tasks', undefined, undefined, { offset });
    if (live.current) setNext(page.next_offset === null ? null : str(page.next_offset));
    if (page.service_instance_id !== api.instance) throw Error('SERVICE_INSTANCE_MISMATCH');
    const items = arr(page.items).map(obj); if (live.current) setTasks(items);
    return items;
  };
  useEffect(() => {
    live.current = true;
    void (async () => {
      const response = await fetch('/diagnostics/v3/capabilities');
      if (response.status === 404) { if (live.current) setStatus('当前服务没有小样本分析入口；已有历史报告仍可读取。'); return; }
      if (!response.ok) throw Error('V3_CAPABILITIES_UNAVAILABLE');
      const caps = obj(await response.json());
      verifySampleCapabilities(caps);
      setEnabled(caps.execution_enabled === true);
      const api = new SampleClient3(str(caps.service_instance_id));
      if (!live.current) return;
      setClient(api);
      const [base, user, items] = await Promise.all([api.request('/monitoring/catalog'), api.request('/monitoring/user-v2/runs'), history(api)]);
      if (!live.current) return;
      const choices: Obj[] = arr(base.items).map(obj).map(item => ({ label: `${text(item.appid)} · ${text(item.model_id)} · 基础来源`, source: { source_kind: 'base', base_run_id: item.active_run_id, appid: item.appid } }));
      for (const item of arr(user.entries).map(obj)) if (item.state === 'ready' && item.appid) { const s = obj(item.source); choices.push({ label: `${text(item.appid)} · ${text(s.model_id)} · ${text(s.common_name)}`, source: { source_kind: 'user_v2', user_run_id: s.user_run_id, appid: item.appid, expected_index_revision: s.index_revision } }); }
      setSources(choices); setStatus(caps.execution_enabled === true ? '选择来源后显式启动；数据过大时自动小样本分析。' : '当前服务仅支持读取');
      const pinned = pinnedTask(api.instance);
      const first = items.find(item => obj(item.execution).task_id === pinned) ?? items.find(item => obj(item.execution).state === 'completed');
      if (first) await readReport(api, str(obj(first.execution).task_id));
    })().catch(e => { if (live.current) setError(String(e)); });
    return () => { live.current = false; };
  }, []);
  const filterSources = async () => {
    if (!client) return;
    try {
      const query = filter ? { appid: filter } : {};
      const base = await client.request('/monitoring/catalog', undefined, undefined, query);
      const user = await client.request('/monitoring/user-v2/runs', undefined, undefined, query);
      const choices: Obj[] = arr(base.items).map(obj).map(item => ({ label: `${text(item.appid)} · ${text(item.model_id)} · 基础来源`, source: { source_kind: 'base', base_run_id: item.active_run_id, appid: item.appid } }));
      for (const item of arr(user.entries).map(obj)) if (item.state === 'ready' && item.appid) { const s = obj(item.source); choices.push({ label: `${text(item.appid)} · ${text(s.model_id)} · ${text(s.common_name)}`, source: { source_kind: 'user_v2', user_run_id: s.user_run_id, appid: item.appid, expected_index_revision: s.index_revision } }); }
      setSources(choices); setSourceIndex('0'); setError('');
    } catch (e) { setError(String(e)); }
  };
  const start = async () => {
    if (!enabled || !client || !sources[Number(sourceIndex)] || busy) return;
    setBusy(true); cancelled.current = false; setError('');
    try {
      let receipt = await client.receipt('/diagnostics/v3/source-preparations', { submission_key: crypto.randomUUID(), source: sources[Number(sourceIndex)]!.source });
      const prep = str(receipt.preparation_id), prepPath = `/diagnostics/v3/source-preparations/${prep}`;
      setCurrent({ path: prepPath, id: prep });
      while (!terminal(receipt) && live.current && !cancelled.current) { setStatus(`自动准备小样本：${labels[str(receipt.state)]}`); await pause(); receipt = await client.receipt(prepPath); }
      if (!live.current || cancelled.current) return;
      if (receipt.state !== 'completed') throw Error(text(receipt.reason_code));
      let execution = await client.execution('/diagnostics/v3/tasks', { preparation_id: prep, submission_key: crypto.randomUUID() });
      const id = str(execution.task_id), path = `/diagnostics/v3/tasks/${id}`;
      setCurrent({ path, id }); selectedRef.current = id; setSelected(id);
      while (!terminal(execution) && live.current) { setStatus(`发现 clock → 固定化 → 实算：${labels[str(execution.state)]}`); await pause(); execution = await client.execution(path); }
      if (!live.current) return;
      setStatus(`${labels[str(execution.state)]} ${text(execution.reason_code ?? '')}`);
      await history(client); if (selectedRef.current === id) { await readReport(client, id); pinnedTask(client.instance, id); }
    } catch (e) { if (live.current) setError(String(e)); }
    finally { if (live.current) { setBusy(false); setCurrent(null); } }
  };
  return <section className="sample-diagnostics" aria-label="有界样本分析">
    <div className="panel"><h2>低命中率 · 自动小样本分析</h2><label>按 APPID 筛选<input aria-label="小样本来源APPID" value={filter} onChange={e => setFilter(e.target.value)}/></label><button disabled={!client || busy} onClick={() => void filterSources()}>筛选来源</button><small>每类最多列出 100 个来源；可输入完整 APPID 缩小范围。</small><label>分析来源<select aria-label="小样本分析来源" value={sourceIndex} disabled={busy} onChange={e => setSourceIndex(e.target.value)}>{sources.map((s, i) => <option key={i} value={i}>{text(s.label)}</option>)}</select></label>
      <button disabled={!enabled || !client || !sources.length || busy} onClick={() => void start()}>分析当前来源</button>
      {busy && current && <button onClick={() => { cancelled.current = true; void client!.request(`${current.path}/cancel`, {}).then(() => setStatus('取消已提交')).catch(e => setError(String(e))); }}>取消分析</button>}
      <p role="status">{status}</p>{error && <p role="alert">{error}</p>}
      <label>样本分析历史<select aria-label="样本分析历史" value={selected} onChange={e => { const id = e.target.value; pinnedTask(client!.instance, id); void readReport(client!, id); }}><option value="">选择已封存结果</option>{tasks.map(item => { const e = obj(item.execution); return <option key={str(e.task_id)} value={str(e.task_id)}>{text(obj(item.source).appid)} · {labels[str(e.state)]} · {text(e.task_id)}</option>; })}</select></label>
      <button disabled={!client} onClick={() => void history(client!).catch(e => setError(String(e)))}>刷新历史</button>
      {next && <button disabled={!client} onClick={() => void history(client!, next).catch(e => setError(String(e)))}>更早记录</button>}
      <button disabled={!client || !selected} onClick={() => void readReport(client!, selected)}>重新读取结果</button>
    </div>{report && <SampleReport report={report}/>}
  </section>;
}

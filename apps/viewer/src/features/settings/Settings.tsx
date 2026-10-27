import { useState } from 'react';
import type { Dto } from '../../api/types';
import { getJson, writeJson, ApiError } from '../../api/client';
import { validateDto } from '../../api/validate';
import { useRead } from '../../components/useRead';
export function Settings({ model, instance, snapshot }: { model: string; instance: string; snapshot: Dto<'ViewSnapshot'> | null }) {
  const [selected, setSelected] = useState(model);
  const models = useRead('LegacyModelsList', '/models', {}, undefined, false);
  const response = useRead('ModelSettingsResponse', `/monitoring/models/${encodeURIComponent(selected)}/settings`, {}, { service_instance_id: instance, view_schema_version: '1' }, false);
  return <><label>设置模型 <select value={selected} onChange={e => setSelected(e.target.value)}>{models.data?.map(item => <option key={item.settings.model_id}>{item.settings.model_id}</option>)}</select></label>{response.error && <p role="alert">{response.error}<button onClick={response.reload}>重读设置</button></p>}{response.data && <ModelForm key={selected + instance} initial={response.data} instance={instance} />}{snapshot && snapshot.identity.model_id === selected && <Rules key={snapshot.identity.appid + selected} snapshot={snapshot} />}</>;
}
function ModelForm({ initial, instance }: { initial: Dto<'ModelSettingsResponse'>; instance: string }) {
  const { model_id, revision, block_size, cp_world_size, mtp, prefix_cache_enabled, hybrid_enabled, cache_mode, encoding_profile, model_aliases } = initial.settings;
  const [base, setBase] = useState(revision), [draft, setDraft] = useState({ block_size, cp_world_size, mtp, prefix_cache_enabled, hybrid_enabled, cache_mode, encoding_profile, model_aliases });
  const [newer, setNewer] = useState<Dto<'ModelSettingsResponse'> | null>(null), [message, setMessage] = useState(''), [busy, setBusy] = useState(false);
  const save = async (expected = base) => { setBusy(true); try {
    const body = validateDto('SettingsUpdate', { expected_revision: expected, changes: draft });
    const result = await writeJson('ModelSettingsResponse', 'PUT', `/monitoring/models/${encodeURIComponent(model_id)}/settings`, body, instance);
    validateDto('ModelSettingsResponse', result, { service_instance_id: instance, view_schema_version: '1' });
    setBase(result.settings.revision); setNewer(null); setMessage('已保存，仅对下一次启动运行生效；当前结果保持原设置。');
  } catch (error) {
    if (error instanceof ApiError && error.code === 'REVISION_CONFLICT') {
      setMessage('设置已被更新，当前草稿已保留。请对照服务器新版本后决定是否重新保存。');
      try { setNewer(await getJson('ModelSettingsResponse', `/monitoring/models/${encodeURIComponent(model_id)}/settings`, {}, { scope: { service_instance_id: instance, view_schema_version: '1' } })); } catch { setMessage('版本冲突且读取新版本失败；草稿保留，请稍后重试。'); }
    } else setMessage(error instanceof Error ? error.message : '保存失败，草稿保留。');
  } finally { setBusy(false); } };
  return <section className="panel"><h2>下一运行设置 · {model_id}</h2><p>编辑版本 {base}；历史结果不会改变。hybrid为预留配置，首版不能执行该仿真。</p><div className="form-grid"><label>Block size <input inputMode="numeric" value={draft.block_size} onChange={e => setDraft({ ...draft, block_size: e.target.value })} /></label><label>CP <input inputMode="numeric" value={draft.cp_world_size} onChange={e => setDraft({ ...draft, cp_world_size: e.target.value })} /></label>{(['mtp','prefix_cache_enabled','hybrid_enabled'] as const).map(key => <label key={key}><input type="checkbox" checked={draft[key]} onChange={e => setDraft({ ...draft, [key]: e.target.checked })} />{key}</label>)}<label>cache mode <select value={draft.cache_mode} onChange={e => setDraft({ ...draft, cache_mode: e.target.value as typeof cache_mode })}>{['full_block','full_block_approximation','qwen_hybrid','deepseek_hybrid'].map(mode => <option key={mode}>{mode}</option>)}</select></label><label>模板模式 <select value={draft.encoding_profile} onChange={e => setDraft({ ...draft, encoding_profile: e.target.value as typeof encoding_profile })}>{['default','thinking_enabled','thinking_disabled'].map(mode => <option key={mode}>{mode}</option>)}</select></label></div><button disabled={busy} onClick={() => void save()}>保存下一运行设置</button><p role="status">{message}</p>{newer && <><h3>服务器当前值（版本 {newer.settings.revision}）</h3><pre>{JSON.stringify(newer.settings, null, 2)}</pre><button disabled={busy} onClick={() => void save(newer.settings.revision)}>确认以新版本保存当前草稿</button></>}</section>;
}
function Rules({ snapshot }: { snapshot: Dto<'ViewSnapshot'> }) {
  const s = snapshot.identity;
  const [offset, setOffset] = useState('0'), [revision, setRevision] = useState<string | undefined>();
  const response = useRead('RulesPage', '/monitoring/threshold-rules', { appid: s.appid, model_id: s.model_id, offset, limit: 50, rules_revision: revision }, { service_instance_id: s.service_instance_id, view_schema_version: '1' }, false);
  const [draft, setDraft] = useState<Dto<'RuleUpdate'> | null>(null), [value, setValue] = useState(''), [message, setMessage] = useState('');
  const metrics = Object.keys(snapshot.metrics.measurement_signatures) as Dto<'RuleUpdate'>['metric'][];
  const create = () => { const metric = 'ideal_hit_rate'; setDraft({ appid: s.appid, model_id: s.model_id, rule_id: crypto.randomUUID(), metric, comparator: 'lt', threshold: 0, value_kind: 'ratio', enabled: false, route: 'prefix_analysis', measurement_signature: snapshot.metrics.measurement_signatures[metric], expected_revision: '0' }); setValue(''); setMessage('请输入由稳态流量确定的阈值；系统不预设报警阈值。'); };
  const save = async (expected = draft?.expected_revision) => { if (!draft) return; try {
    if (!value.trim()) throw new Error('请输入阈值');
    const threshold = draft.value_kind === 'integer' ? value : Number(value);
    if (typeof threshold === 'number' && !Number.isFinite(threshold)) throw new Error('阈值必须为有限数值');
    const body = validateDto('RuleUpdate', { ...draft, threshold, expected_revision: expected });
    const result = await writeJson('RuleResponse', 'PUT', '/monitoring/threshold-rules', body, s.service_instance_id);
    validateDto('RuleResponse', result, { service_instance_id: s.service_instance_id, view_schema_version: '1' });
    setDraft({ ...body, expected_revision: result.rule.revision }); setMessage('规则已保存，仅影响下一次运行。'); response.reload();
  } catch (error) { setMessage(error instanceof ApiError && error.code === 'REVISION_CONFLICT' ? '规则版本冲突，草稿保留。请重读规则并对照新版本后，明确确认保存当前草稿。' : error instanceof Error ? error.message : '保存失败'); } };
  return <section className="panel"><h2>阈值规则 · {s.appid} × {s.model_id}</h2><p>阈值由稳态流量确定；没有默认报警阈值。</p>{response.error && <p role="alert">{response.error}</p>}<div className="toolbar"><button onClick={create}>新增阈值规则</button><button onClick={() => { setOffset('0'); setRevision(undefined); response.reload(); }}>重读规则列表</button></div>{response.data?.items.map(rule => <p key={rule.rule_id}>{rule.metric} · {String(rule.threshold)} · {rule.enabled ? '启用' : '停用'} <button onClick={() => { const { revision: version, ...rest } = rule; setDraft({ ...rest, expected_revision: version }); setValue(String(rule.threshold)); }}>编辑规则 {rule.rule_id}</button></p>)}<button disabled={offset === '0'} onClick={() => setOffset((BigInt(offset) >= 50n ? BigInt(offset) - 50n : 0n).toString())}>上一页</button><button disabled={!response.data?.next_offset} onClick={() => { setRevision(response.data!.rules_revision); setOffset(response.data!.next_offset!); }}>下一页</button>
    {draft && response.data?.items.find(rule => rule.rule_id === draft.rule_id && rule.revision !== draft.expected_revision) && <div className="notice"><pre>{JSON.stringify(response.data.items.find(rule => rule.rule_id === draft.rule_id), null, 2)}</pre><button onClick={() => void save(response.data!.items.find(rule => rule.rule_id === draft.rule_id)!.revision)}>确认按新规则版本保存当前草稿</button></div>}{draft && <div className="form-grid"><label>指标 <select value={draft.metric} onChange={e => { const metric = e.target.value as typeof draft.metric; setDraft({ ...draft, metric, value_kind: metric === 'ideal_hit_rate' ? 'ratio' : 'integer', measurement_signature: snapshot.metrics.measurement_signatures[metric] }); }}>{metrics.map(m => <option key={m}>{m}</option>)}</select></label><label>比较 <select value={draft.comparator} onChange={e => setDraft({ ...draft, comparator: e.target.value as typeof draft.comparator })}>{['lt','le','gt','ge'].map(c => <option key={c}>{c}</option>)}</select></label><label>阈值 <input value={value} onChange={e => setValue(e.target.value)} /></label><label><input type="checkbox" checked={draft.enabled} onChange={e => setDraft({ ...draft, enabled: e.target.checked })} />启用规则</label><label>信号路由 <select value={draft.route ?? 'signal_only'} onChange={e => setDraft({ ...draft, route: e.target.value as typeof draft.route })}>{['prefix_analysis','length_analysis','signal_only'].map(route => <option key={route}>{route}</option>)}</select></label><button onClick={() => void save()}>保存阈值规则</button></div>}<p role="status">{message}</p>
  </section>;
}

import { useState, useSyncExternalStore } from 'react';
import type { SubmissionCoordinator } from '../../state/submission-coordinator';
import { isTerminal } from '../../state/receipt-store';
import { useRead } from '../../components/useRead';
import type { Dto } from '../../api/types';
export function Submissions({ coordinator, instance, connected }: { coordinator: SubmissionCoordinator; instance: string; connected: boolean }) {
  const records = useSyncExternalStore(coordinator.store.subscribe, coordinator.store.getSnapshot);
  const models = useRead('LegacyModelsList', '/models', {}, undefined, false);
  const [file, setFile] = useState(''), [model, setModel] = useState<Dto<'Submission'>['model_id']>('GLM-5.2');
  const [busy, setBusy] = useState(false), [error, setError] = useState('');
  const [confirm, setConfirm] = useState(false);
  const submit = async () => { setBusy(true); setError(''); try { await coordinator.submit({ file_ref: file, model_id: model, submission_key: crypto.randomUUID() }, instance); setConfirm(false); } catch { setError('提交未完成，请检查连接和输入。'); } finally { setBusy(false); } };
  return <section className="panel"><h2>提交 CSV 监控任务</h2><p>先将CSV放到后端允许的数据目录，再填写相对文件引用。这里不上传文件。</p><div className="toolbar"><label>file_ref <input value={file} onChange={e => setFile(e.target.value)} placeholder="例如 samples/model.csv" /></label><label>模型 <select value={model} onChange={e => setModel(e.target.value as typeof model)}>{models.data?.map(item => <option key={item.settings.model_id}>{item.settings.model_id}</option>)}</select></label></div><label><input type="checkbox" checked={confirm} onChange={e => setConfirm(e.target.checked)} />确认启动该文件的监控计算</label><p><button disabled={!connected || !file || !confirm || busy || !models.data?.some(item => item.settings.model_id === model)} onClick={() => void submit()}>提交监控任务</button></p>{error && <p role="alert">{error}</p>}{models.error && <p>{models.error}<button onClick={models.reload}>重读模型列表</button></p>}
    <h3>提交记录</h3>{records.map(record => <article className="signal" key={record.instance + record.request.submission_key}><p>{record.request.file_ref} · {record.request.model_id}</p><p>提交时间：{new Date(record.submittedAt).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}（北京时间）</p><p>key：<code>{record.request.submission_key}</code> · {record.status === 'unconfirmed' ? '提交尚未确认' : record.status}</p>{record.message && <p role="status">{record.message}</p>}{record.instance !== instance ? <p>其他服务实例的历史提交，不向当前服务发送。</p> : <div className="toolbar"><button disabled={!connected} onClick={() => void coordinator.align(record.request.submission_key)}>查询当前回执</button>{!isTerminal(record.status) && <button disabled={!connected} onClick={() => void coordinator.submit(record.request, instance)}>使用原key重试提交</button>}</div>}</article>)}</section>;
}

import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
export const models = ['GLM-5.2', 'Qwen3.6-27B', 'DeepSeek-V4-Flash-0731'] as const;
export const serviceNames = ['GLM-V5.2', 'Qwen-V3.6-27B', 'DeepSeek-V4-Flash'];
export const errorText = (error: unknown) => error instanceof Error ? error.message : '操作失败，请重试';
export const percent = (value: number | null | undefined) => value == null ? '—' : `${(value * 100).toFixed(1)}%`;
export function Modal({ title, children, close }: {
    title: string;
    children: ReactNode;
    close(): void;
}) {
    const ref = useRef<HTMLDialogElement>(null);
    useEffect(() => { ref.current?.showModal(); }, []);
    return <dialog ref={ref} className="v2-dialog" onCancel={close}><div className="panel-head"><h2>{title}</h2><button aria-label="关闭弹窗" onClick={close}>×</button></div><div className="dialog-body">{children}</div></dialog>;
}
export function fields(form: HTMLFormElement): Record<string, string> { return Object.fromEntries([...new FormData(form)].map(([k, v]) => [k, String(v).trim()])); }
export function stateLabel(value: string) { return ({ accepted: '已受理', base_pending: '基础分析处理中', indexing: '索引准备中', ready: '已完成', empty: '无有效用户组', queued: '排队中', running: '处理中', completed: '已完成', failed: '失败', interrupted: '已中断' } as Record<string, string>)[value] ?? value; }

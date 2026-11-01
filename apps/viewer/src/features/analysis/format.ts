import { obj, str } from '../../api/analysis/client';
import type { Obj } from '../../api/analysis/client';
export function decimalRatio(numerator: string, denominator: string, scale = 1n) {
    const n = BigInt(numerator) * scale, d = BigInt(denominator);
    if (d <= 0n)
        return '—';
    const sign = n < 0n ? '-' : '';
    const absolute = n < 0n ? -n : n;
    const rounded = (absolute * 100n + d / 2n) / d;
    return `${sign}${rounded / 100n}.${String(rounded % 100n).padStart(2, '0')}`;
}
export function hit(metrics: unknown) { const m = obj(metrics); const r=decimalRatio(str(m.h),str(m.p),100n);return r==='—'?r:r+'%'; }
export function gain(e: Obj) { const g = obj(e.gain_percentage_points); return decimalRatio(str(g.numerator), str(g.denominator)); }
export function nanos(value: unknown) {
    const ns = BigInt(str(value));
    const ms = ns / 1000000n;
    if (ms > 8640000000000000n || ms < -8640000000000000n)
        return `${ns} ns`;
    return new Date(Number(ms)).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false });
}
export const statusLabel: Record<string, string> = { ready: '完整报告', partial: '部分结果', empty: '范围无可分析请求', failed: '分析失败', interrupted: '分析中断' };

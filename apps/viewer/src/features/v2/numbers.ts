export function decimalText(value: string, positive = false, integer = false): string {
    const v = value.trim();
    if (v.length > 128 || !(integer ? /^(0|[1-9][0-9]*)$/ : /^(0|[1-9][0-9]*)(\.[0-9]+)?$/).test(v))
        throw Error('请输入规范的非负十进制数，不接受空值、指数或超过128字符');
    if (positive && !/[1-9]/.test(v))
        throw Error('此参数必须大于0');
    return v;
}
export function compareDecimal(a: string, b: string) { const [ai, af = ''] = a.split('.'), [bi, bf = ''] = b.split('.'); const n = Math.max(af.length, bf.length); const x = BigInt(ai! + af.padEnd(n, '0')), y = BigInt(bi! + bf.padEnd(n, '0')); return x < y ? -1 : x > y ? 1 : 0; }
export function percentageInput(value: string) { const v = decimalText(value); if (compareDecimal(v, '100') > 0)
    throw Error('命中率须在0–100%之间'); const [i, f = ''] = v.split('.'); const all = i!.padStart(3, '0'); return `${BigInt(all.slice(0, -2))}.${all.slice(-2)}${f}`; }
export function fractionText(value: {
    numerator: string;
    denominator: string;
}) { const d = BigInt(value.denominator); if (!d)
    return '—'; const n = (BigInt(value.numerator) * 100n + d / 2n) / d; return `${(n / 100n).toLocaleString('en-US')}.${(n % 100n).toString().padStart(2, '0')}`; }
export const sortNames = { request_count: '请求数', ideal_hit_rate: '理想命中率', total_ideal_compute_tokens: '理想重算Token总量', typical_ideal_compute_tokens: '典型重算长度' };
export function rangeQuery(draft: Record<string, string>) { const result: Record<string, string> = {}; for (const k of Object.keys(sortNames)) {
    for (const side of ['min', 'max']) {
        const raw = draft[k + '_' + side]?.trim();
        if (raw)
            result[k + '_' + side] = k === 'ideal_hit_rate' ? percentageInput(raw) : decimalText(raw, false, ['request_count', 'total_ideal_compute_tokens'].includes(k));
    }
    const lo = result[k + '_min'], hi = result[k + '_max'];
    if (lo !== undefined && hi !== undefined && compareDecimal(lo, hi) > 0)
        throw Error('下限不能大于上限');
} return result; }

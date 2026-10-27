const unsigned = /^(0|[1-9][0-9]*)$/;
const signed = /^(0|-?[1-9][0-9]*)$/;
export function integer(value: string, allowNegative = false): bigint {
  if (!(allowNegative ? signed : unsigned).test(value) || value.includes('\n')) throw new Error('INVALID_INTEGER');
  return BigInt(value);
}
export function formatInteger(value: string | null, allowNegative = false): string {
  return value === null ? '—' : integer(value, allowNegative).toLocaleString('zh-CN');
}
/** Only a bounded pixel coordinate may become a Number; never the source value. */
export function scaleInteger(value: string, max: string, pixels: number): number {
  if (!Number.isSafeInteger(pixels) || pixels < 0) throw new Error('INVALID_PIXEL_RANGE');
  const n = integer(value), total = integer(max);
  if (n > total) throw new Error('VALUE_EXCEEDS_SCALE');
  return total === 0n ? 0 : Number(n * BigInt(pixels) / total);
}

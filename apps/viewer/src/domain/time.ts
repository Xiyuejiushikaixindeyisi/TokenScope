const utc = /^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$/;
export function utcNanoseconds(value: string): string {
  if (!utc.test(value) || value.includes('\n')) throw new Error('INVALID_UTC_TIME');
  const ms = value.slice(0, 23) + 'Z';
  const date = new Date(ms);
  if (!Number.isFinite(date.getTime()) || date.toISOString() !== ms) throw new Error('INVALID_UTC_TIME');
  return value;
}
export function formatBeijing(value: string | null): string {
  if (value === null) return '—';
  utcNanoseconds(value);
  return new Intl.DateTimeFormat('zh-CN', { timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23' }).format(new Date(value));
}
export function compareUtc(a: string, b: string): number {
  utcNanoseconds(a); utcNanoseconds(b);
  return a === b ? 0 : a < b ? -1 : 1;
}

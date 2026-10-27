import { describe, it, expect } from 'vitest';
import { integer, formatInteger, scaleInteger } from '../../src/domain/integer';
import { utcNanoseconds, formatBeijing, compareUtc } from '../../src/domain/time';
import { scopeKey } from '../../src/domain/identity';
describe('exact integers', () => {
  it.each(['0', '9007199254740991', '9007199254740992', '9007199254740993', '18446744073709551615'])('preserves %s', value => {
    expect(integer(value).toString()).toBe(value);
    expect(formatInteger(value).replaceAll(',', '')).toBe(value);
  });
  it('keeps negative deltas and null distinct', () => {
    expect(formatInteger('-9007199254740993', true)).toBe('-9,007,199,254,740,993');
    expect(formatInteger(null)).toBe('—');
    expect(formatInteger('0')).toBe('0');
  });
  it.each(['01', '-1', '1.1', '1e3', '1\n', ' 1', '+1'])('rejects invalid unsigned %j', value => expect(() => integer(value)).toThrow());
  it('scales only bounded final pixels', () => expect(scaleInteger('9223372036854775807', '18446744073709551615', 1000)).toBe(499));
});
it('keeps nanosecond source and sorts without millisecond rounding', () => {
  const a = '2026-10-27T00:00:00.123456789Z';
  expect(utcNanoseconds(a)).toBe(a);
  expect(formatBeijing(a)).toContain('08:00:00');
  expect(compareUtc(a, '2026-10-27T00:00:00.123456790Z')).toBe(-1);
  expect(() => utcNanoseconds('2026-02-30T00:00:00.000000000Z')).toThrow();
});
it('scope key is unambiguous for arbitrary appid text', () => {
  const base = { service_instance_id: 'instance', view_schema_version: '1' as const };
  expect(scopeKey({ ...base, appid: 'a/b', model_id: 'c' })).not.toBe(scopeKey({ ...base, appid: 'a', model_id: 'b/c' }));
});

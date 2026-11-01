import { it, expect } from 'vitest';
import { decimalRatio, nanos } from '../../../src/features/analysis/format';
import { excerptText } from '../../../src/features/analysis/Evidence';
it('formats exact rational values without unsafe integer conversion', () => { expect(decimalRatio('9007199254740993','9007199254740993',100n)).toBe('100.00'); expect(decimalRatio('-1','2')).toBe('-0.50'); expect(decimalRatio('0','0')).toBe('—'); expect(nanos('1793404800000000000')).toContain('2026'); });
it('decodes only a complete string and preserves embedded whitespace, large integers and clipped raw evidence', () => {
    const text = '{ "id": 9007199254740993, "emoji": "😀" }';
    expect(excerptText({ excerpt: JSON.stringify(text) })).toBe(text);
    expect(excerptText({ excerpt: text })).toBe(text);
    expect(excerptText({ excerpt: '"clipped \\u' })).toBe('"clipped \\u');
});

it("decodes an escaped embedded string layer without parsing its large numeric contents", () => { const text = '{ "id": 9007199254740993, "name": "😀" }'; const escaped = JSON.stringify(text).slice(1,-1); expect(excerptText({ excerpt: escaped, source: { embedded: { pointer: "" } } })).toBe(text); });

import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import schemas from './generated/diagnostics-execution-2.json';

export const EXECUTION_VERSION = 'diagnostics-execution-2';
export const DISCOVERY_VERSION = 'diagnostics-discovery-2';
const ajv = new Ajv({ strict: false, allErrors: true, coerceTypes: false, useDefaults: false });
addFormats(ajv);
ajv.addKeyword({ keyword: 'x-integer-minimum', type: 'string', validate: (min: string, v: string) => /^-?\d+$/.test(v) && BigInt(v) >= BigInt(min) });
const validators = Object.fromEntries(Object.entries(schemas).map(([name, schema]) => [name, ajv.compile(schema)]));
export function validateExecution(name: keyof typeof schemas, value: unknown): Record<string, unknown> {
    if (!validators[name]!(value)) throw Error(`INVALID_EXECUTION_RESPONSE:${name}`);
    return value as Record<string, unknown>;
}
// Resolve local refs completely: aggregate OpenAPI may rename definitions, but
// every field constraint must still match. Only non-validation annotations differ.
export function schemaSignature(schema: unknown): string {
    const root = schema as Record<string, unknown>;
    function expand(value: unknown, refs: string[] = []): unknown {
        if (Array.isArray(value)) return value.map(v => expand(v, refs));
        if (!value || typeof value !== 'object') return value;
        const o = value as Record<string, unknown>;
        if (o.$ref !== undefined) {
            if (typeof o.$ref !== 'string' || !o.$ref.startsWith('#/') || refs.includes(o.$ref)) throw Error('UNSUPPORTED_SCHEMA_REFERENCE');
            const resolved = o.$ref.slice(2).split('/').reduce<unknown>((v, key) => (v as Record<string, unknown>)?.[key.replace(/~1/g, '/').replace(/~0/g, '~')], root);
            if (!resolved) throw Error('MISSING_SCHEMA_REFERENCE');
            const siblings = Object.fromEntries(Object.entries(o).filter(([k]) => k !== '$ref'));
            const base = expand(resolved, [...refs, o.$ref]);
            return Object.keys(siblings).length ? { allOf: [base, expand(siblings, refs)] } : base;
        }
        return Object.fromEntries(Object.entries(o).filter(([k]) => !['$defs', 'definitions', 'title', 'description', 'examples', '$id', '$schema'].includes(k)).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => [k, expand(v, refs)]));
    }
    return JSON.stringify(expand(schema));
}
export function verifyExecutionCapabilities(c: Record<string, unknown>, instance: string) {
    if (c.service_instance_id !== instance || c.version !== EXECUTION_VERSION || c.discovery_version !== DISCOVERY_VERSION || c.minimum_selected_directions !== '1' || c.legacy_read_compatible !== true || c.catalog_url !== '/diagnostics/v2/catalog' || c.submission_url !== '/diagnostics/v2/tasks' || c.partial_policy !== 'ready_preferred_published_partial_fallback' || c.budget_semantics !== 'direction_isolated_compute_rule_reserved_retention' || JSON.stringify(c.directions) !== JSON.stringify(['low_hit', 'token_content'])) throw Error('EXECUTION_CAPABILITY_MISMATCH');
    const advertised = c.schemas as Record<string, unknown> | undefined;
    for (const [key, schema] of Object.entries(schemas)) if (!advertised?.[key] || schemaSignature(advertised[key]) !== schemaSignature(schema)) throw Error(`EXECUTION_SCHEMA_MISMATCH:${key}`);
}

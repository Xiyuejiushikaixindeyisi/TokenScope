import { ProtocolError } from '../validate';

/** Resolve local references structurally; component names are not wire contracts.
 * Fail closed on cycles, remote/missing refs, siblings, or excessive expansion.
 * Every non-ref field (including constraints and error responses) is retained.
 */
export function resolvedOperationSignature(operation: unknown, schemas: Record<string, unknown>): string {
    let budget = 50000;
    const visit = (value: unknown, stack: string[], depth: number): unknown => {
        if (--budget < 0 || depth > 100) throw new ProtocolError('OpenAPI reference expansion limit');
        if (Array.isArray(value)) return value.map(item => visit(item, stack, depth + 1));
        if (!value || typeof value !== 'object') return value;
        const object = value as Record<string, unknown>;
        if ('$ref' in object) {
            const ref = object.$ref;
            if (typeof ref !== 'string' || !ref.startsWith('#/components/schemas/') || Object.keys(object).length !== 1 || stack.includes(ref)) throw new ProtocolError('Unsupported OpenAPI reference');
            const name = ref.slice('#/components/schemas/'.length).replace(/~1/g, '/').replace(/~0/g, '~');
            if (!Object.hasOwn(schemas, name)) throw new ProtocolError('Missing OpenAPI reference');
            return visit(schemas[name], [...stack, ref], depth + 1);
        }
        return Object.fromEntries(Object.keys(object).sort().map(key => [key, visit(object[key], stack, depth + 1)]));
    };
    if (!operation || typeof operation !== 'object') throw new ProtocolError('Missing OpenAPI operation');
    return JSON.stringify(visit(operation, [], 0));
}

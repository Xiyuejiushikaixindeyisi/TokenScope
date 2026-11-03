import contract from './generated/user/hv2.openapi.json';
import legacy from './generated/user/legacy.openapi.json';
import { resolvedOperationSignature } from './openapi-equivalence';
import { ProtocolError } from '../validate';
type Document = { paths?: Record<string, Record<string, unknown>>; components?: { schemas?: Record<string, unknown> } };
export function assertUserContract(document: Document) {
    const operations = (d: Document) => Object.entries(d.paths ?? {}).filter(([p]) => p.startsWith('/monitoring/user-v2/')).flatMap(([p, methods]) => Object.entries(methods).filter(([m]) => ['get', 'post'].includes(m)).map(([m, o]) => ({ p, m, o })));
    if (operations(document).length !== 14) throw new ProtocolError('用户2.1.0接口操作不完整');
    for (const { p, m, o } of operations(contract)) {
        const actual = document.paths?.[p]?.[m];
        if (resolvedOperationSignature(actual, document.components?.schemas ?? {}) !== resolvedOperationSignature(o, contract.components.schemas)) throw new ProtocolError(`用户2.1.0契约失配 ${m} ${p}`);
    }
    // The version marker alone changes on the original nine operations.
    const oldOperations = operations(legacy);
    if (oldOperations.length !== 9) throw new ProtocolError('旧用户契约不完整');
    for (const { p, m, o } of oldOperations) {
        const upgraded = { ...(o as object), 'x-user-contract-version': '2.1.0' };
        if (resolvedOperationSignature(document.paths?.[p]?.[m], document.components?.schemas ?? {}) !== resolvedOperationSignature(upgraded, legacy.components.schemas)) throw new ProtocolError(`用户旧操作不兼容 ${m} ${p}`);
    }
}

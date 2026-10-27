import Ajv2020 from 'ajv/dist/2020';
import addFormats from 'ajv-formats';
import schema from './generated/schema.json';
import type { Dto, DtoName } from './types';
import { assertScope } from '../domain/identity';
import type { Scope } from '../domain/identity';
const id = 'https://tokenscope.invalid/contracts/monitoring-view/1.0.0';
const ajv = new Ajv2020({ strict: false, allErrors: true, coerceTypes: false, useDefaults: false, removeAdditional: false });
addFormats(ajv);
ajv.addSchema({ ...schema, $id: id });
export class ProtocolError extends Error {
  constructor(readonly schemaName: string) { super(`服务响应不符合协议：${schemaName}`); }
}
export function validateDto<K extends DtoName>(name: K, value: unknown, expected?: Scope): Dto<K> {
  const validate = ajv.getSchema(`${id}#/$defs/${name}`);
  if (!validate || !validate(value)) throw new ProtocolError(name);
  // S0 specifies cursor semantics separately from the structural Schema.
  // Validate the boundary but preserve the original string for storage/replay.
  if (name === 'CatalogResponse') {
    const catalog = value as Dto<'CatalogResponse'>;
    const prefix = `${catalog.service_instance_id}:`;
    const sequence = catalog.cursor.slice(prefix.length);
    if (!catalog.cursor.startsWith(prefix) || !/^(0|[1-9][0-9]*)$(?![\s\S])/.test(sequence)) throw new ProtocolError(name);
  }
  if (expected) {
    const record = value as Record<string, unknown>;
    assertScope((record.identity ?? record) as Record<string, unknown>, expected);
  }
  return value as Dto<K>;
}
export function decodeJson(bytes: Uint8Array): unknown {
  return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)) as unknown;
}

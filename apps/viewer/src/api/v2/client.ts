import Ajv2020 from 'ajv/dist/2020';
import addFormats from 'ajv-formats';
import userSchemas from './generated/user/schemas.json';
import maSchemas from './generated/ma/schemas.json';
import { apiPath, ApiError } from '../client';
import { ProtocolError } from '../validate';
import type * as U from './generated/user';
import type * as M from './generated/ma';
export type Kind = 'user' | 'ma';
type User = {
    Receipt: U.Receipt;
    Ranking: U.Ranking;
    Modes: U.Modes;
    Scenario: U.Scenario | U.BatchScenario;
    Evaluation: U.Evaluation;
};
type Ma = {
    Receipt: M.Receipt;
    Catalog: M.Catalog;
    Snapshot: M.Snapshot;
    QualityPage: M.QualityPage;
};
type Contract = {
    user: User;
    ma: Ma;
};
const ajv = new Ajv2020({ strict: false, coerceTypes: false, useDefaults: false });
addFormats(ajv);
const validators = new Map<string, ReturnType<typeof ajv.compile>>();
export function validateV2<K extends Kind, N extends keyof Contract[K] & string>(kind: K, name: N, value: unknown): Contract[K][N] {
    const key = `${kind}/${name}`;
    let validator = validators.get(key);
    if (!validator) {
        const schemas: Record<string, object> = kind === 'user' ? userSchemas : maSchemas;
        const schema = kind === 'user' && name === 'Scenario' ? { $defs: userSchemas.Scenario.$defs, anyOf: [{ $ref: '#/$defs/Scenario' }, { $ref: '#/$defs/BatchScenario' }] } : schemas[name];
        if (!schema)
            throw new ProtocolError(key);
        validator = ajv.compile(schema);
        validators.set(key, validator);
    }
    if (!validator(value))
        throw new ProtocolError(key);
    return value as Contract[K][N];
}
export class V2Client {
    private readonly lifetime = new AbortController();
    get signal() { return this.lifetime.signal; }
    private identityChanged() {
        if (this.lifetime.signal.aborted) return;
        this.lifetime.abort();
        globalThis.dispatchEvent?.(new Event('tokenscope-instance-changed'));
    }
    constructor(readonly instance: string, private readonly fetcher: typeof fetch = (...args) => globalThis.fetch(...args)) { }
    async request<K extends Kind, N extends keyof Contract[K] & string>(kind: K, name: N, suffix: string, options: {
        query?: Record<string, string | number | undefined>;
        body?: unknown;
        signal?: AbortSignal;
    } = {}): Promise<Contract[K][N]> {
        const signal = options.signal ? AbortSignal.any([options.signal, this.lifetime.signal]) : this.lifetime.signal;
        signal.throwIfAborted();
        const path = `/monitoring/${kind === 'user' ? 'user-v2' : 'ma'}${suffix}`;
        const response = await this.fetcher(apiPath(path, options.query), {
            method: options.body === undefined ? 'GET' : 'POST', credentials: 'same-origin', redirect: 'error', cache: 'no-store',
            headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'X-TokenScope-Instance-Id': this.instance },
            ...(options.body === undefined ? {} : { body: JSON.stringify(options.body) }), signal,
        });
        if (!response.headers.get('content-type')?.includes('application/json'))
            throw new ProtocolError('Content-Type');
        const payload: unknown = await response.json();
        signal.throwIfAborted();
        if (!response.ok) {
            // Error envelopes have the same stable code/message projection in both namespaces.
            const schema = kind === 'user' ? userSchemas.ErrorEnvelope : maSchemas.ErrorEnvelope;
            if (!ajv.validate(schema, payload))
                throw new ProtocolError('ErrorEnvelope');
            const error = (payload as {
                error: {
                    code: string;
                    message: string;
                };
            }).error;
            if (error.code === 'INSTANCE_MISMATCH' || error.code === 'SERVICE_INSTANCE_CHANGED')
                this.identityChanged();
            throw new ApiError(response.status, error.code, error.message);
        }
        const value = validateV2(kind, name, payload);
        if (value && typeof value === 'object' && 'service_instance_id' in value && value.service_instance_id !== this.instance) {
            this.identityChanged();
            throw new ApiError(409, 'INSTANCE_MISMATCH', '服务身份已变化，请重新选择运行');
        }
        return value;
    }
}
export const segment = (value: string) => encodeURIComponent(value);
export async function verifyUserContract() {
    const response = await fetch(apiPath('/openapi.json'), { cache: 'no-store', credentials: 'same-origin', redirect: 'error' });
    if (!response.ok)
        throw new ProtocolError('OpenAPI');
    const document = await response.json() as {
        paths?: Record<string, Record<string, {
            'x-user-contract-version'?: string;
        }>>;
    };
    let count = 0;
    for (const [path, methods] of Object.entries(document.paths ?? {}))
        if (path.startsWith('/monitoring/user-v2/'))
            for (const [method, operation] of Object.entries(methods))
                if (['get', 'post'].includes(method)) {
                    count++;
                    if (operation['x-user-contract-version'] !== '2.0.0')
                        throw new ProtocolError('用户接口版本不是2.0.0');
                }
    if (count !== 9)
        throw new ProtocolError('用户接口操作不完整');
}

import Ajv2020 from 'ajv/dist/2020';
import addFormats from 'ajv-formats';
import userSchemas from './generated/user/schemas.json';
import hv2Schemas from './generated/user/hv2-schemas.json';
import type { DiscoveryPage } from './generated/user/HV2DiscoveryPage';
import type { DefaultPage } from './generated/user/HV2DefaultPage';
import type { AutoEvaluation } from './generated/user/HV2AutoEvaluation';
import { assertUserContract } from './user-contract';
import maSchemas from './generated/ma/schemas.json';
import maAvailability from './generated/ma/AvailabilityResponse.json';
import maAvailabilityContract from './generated/ma/availability.openapi.json';
import type { AvailabilityResponse } from './generated/ma/AvailabilityResponse';
import { apiPath, ApiError } from '../client';
import { ProtocolError } from '../validate';
import { resolvedOperationSignature } from './openapi-equivalence';
import type * as U from './generated/user';
import type * as M from './generated/ma';
export type Kind = 'user' | 'ma';
type User = {
    DiscoveryPage: DiscoveryPage;
    DefaultPage: DefaultPage;
    AutoEvaluation: AutoEvaluation;
    Receipt: U.Receipt;
    Ranking: U.Ranking;
    Modes: U.Modes;
    Scenario: U.Scenario | U.BatchScenario;
    Evaluation: U.Evaluation;
};
type Ma = {
    AvailabilityResponse: AvailabilityResponse;
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
        const schemas: Record<string, object> = kind === 'user' ? { ...hv2Schemas, ...userSchemas } : { ...maSchemas, AvailabilityResponse: maAvailability };
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
    private maAvailabilityHandshake: Promise<void> | undefined;
    private verifyMAAvailability() {
        return this.maAvailabilityHandshake ??= (async () => {
            const response = await this.fetcher(apiPath('/openapi.json'), { signal: this.signal, cache: 'no-store', credentials: 'same-origin', redirect: 'error' });
            if (!response.ok) throw new ProtocolError('MA availability OpenAPI');
            const doc = await response.json() as { paths?: Record<string, { get?: unknown }>; components?: { schemas?: Record<string, unknown> } };
            if (resolvedOperationSignature(doc.paths?.[maAvailabilityContract.path]?.get, doc.components?.schemas ?? {}) !== resolvedOperationSignature(maAvailabilityContract.operation, maAvailabilityContract.components)) throw new ProtocolError('MA availability contract mismatch');
        })().catch(error => { this.maAvailabilityHandshake = undefined; throw error; });
    }
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
        if (kind === 'ma' && name === 'AvailabilityResponse') { await this.verifyMAAvailability(); signal.throwIfAborted(); }
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
    assertUserContract(await response.json());
}

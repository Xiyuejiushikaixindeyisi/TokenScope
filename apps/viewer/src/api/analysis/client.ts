import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import common from './generated/analysis-common-1.0.json';
import discovery from './generated/diagnostics-discovery-1.json';
import { apiPath, ApiError } from '../client';
export type Obj = Record<string, unknown>;
export function obj(value: unknown): Obj {
    if (!value || typeof value !== 'object' || Array.isArray(value))
        throw new Error('INVALID_OBJECT');
    return value as Obj;
}
export function arr(value: unknown): unknown[] { if (!Array.isArray(value))
    throw new Error('INVALID_ARRAY'); return value; }
export function str(value: unknown): string { if (typeof value !== 'string')
    throw new Error('INVALID_STRING'); return value; }
export function text(value: unknown): string { return value == null ? '未提供' : typeof value === 'string' ? value : JSON.stringify(value); }
const ajv = new Ajv({ strict: false, allErrors: true });
addFormats(ajv);
const schemas: Record<string, object> = { ...common.models, ...discovery };
const validators = new Map<string, ReturnType<typeof ajv.compile>>();
export function validate(name: string, value: unknown): Obj {
    let validator = validators.get(name);
    if (!validator) {
        const schema = schemas[name];
        if (!schema)
            throw new Error(`UNKNOWN_SCHEMA:${name}`);
        validator = ajv.compile(schema);
        validators.set(name, validator);
    }
    if (!validator(value))
        throw new Error(`INVALID_RESPONSE:${name}`);
    return obj(value);
}
export interface Item {
    id: string;
    data: Obj;
}
export interface Catalog {
    snapshot: string;
    cursor: string;
    items: Obj[];
    defaults: Obj[];
}
export const taskPath = (task: string) => `/diagnostics/tasks/${encodeURIComponent(task)}`;
export class AnalysisClient {
    constructor(readonly instance: string, readonly fetcher: typeof fetch = (...args) => globalThis.fetch(...args)) { }
    async get(path: string, query: Record<string, string | number | undefined> = {}, signal?: AbortSignal): Promise<Obj> {
        const r = await this.fetcher(apiPath(path, query), { method: 'GET', credentials: 'same-origin', redirect: 'error', headers: { Accept: 'application/json', 'x-tokenscope-service-instance': this.instance }, ...(signal ? { signal } : {}) });
        if (!r.headers.get('content-type')?.includes('application/json'))
            throw new Error('INVALID_CONTENT_TYPE');
        const data = obj(JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(await r.arrayBuffer())));
        if (!r.ok) {
            const e = obj(data.error);
            throw new ApiError(r.status, str(e.code), str(e.message));
        }
        if (data.service_instance_id !== undefined && data.service_instance_id !== this.instance)
            throw new ApiError(409, 'SERVICE_INSTANCE_MISMATCH', '服务身份已变化');
        return data;
    }
    static async connect(signal?: AbortSignal, fetcher: typeof fetch = (...args) => globalThis.fetch(...args)) {
        const read = async (path: string) => {
            const r = await fetcher(path, { method: 'GET', redirect: 'error', credentials: 'same-origin', ...(signal ? { signal } : {}) });
            if (!r.ok)
                throw new Error(`连接失败 (${r.status})`);
            return obj(await r.json());
        };
        const a = await read('/diagnostics/capabilities');
        const b = await read('/diagnostics/discovery/capabilities');
        if (a.contract_version !== 'analysis-common-1.0' || a.http_version !== 'diagnostics-http-1' || b.version !== 'diagnostics-discovery-1' || a.service_instance_id !== b.service_instance_id)
            throw new Error('诊断接口版本或实例不兼容');
        return new AnalysisClient(str(a.service_instance_id), fetcher);
    }
    async catalog(signal?: AbortSignal): Promise<Catalog> {
        let snapshot: string | undefined, cursor = '', after = '0';
        const items = new Map<string, Obj>();
        let defaults: Obj[] = [];
        const seen = new Set<string>();
        do {
            if (seen.has(after))
                throw new Error('CATALOG_PAGE_CYCLE');
            seen.add(after);
            const p = validate('catalog', await this.get('/diagnostics/discovery/catalog', { snapshot, after, limit: 100 }, signal));
            if (snapshot && (p.snapshot !== snapshot || p.event_cursor !== cursor || JSON.stringify(p.defaults) !== JSON.stringify(defaults)))
                throw new Error('CATALOG_SNAPSHOT_CHANGED');
            snapshot = str(p.snapshot);
            cursor = str(p.event_cursor);
            defaults = arr(p.defaults).map(obj);
            for (const item of arr(p.items).map(obj))
                items.set(str(item.task_id), item);
            if (p.next_after === null)
                break;
            after = str(p.next_after);
        } while (true);
        for (const d of defaults) {
            const item = items.get(str(d.task_id));
            if (!item || item.binding_id !== d.binding_id || !arr(item.directions).includes(d.direction) || item.default_eligible !== true)
                throw new Error('INVALID_DEFAULT_REFERENCE');
        }
        return { snapshot: snapshot!, cursor, items: [...items.values()], defaults };
    }
    async report(entry: Obj, signal?: AbortSignal) {
        const r = await this.get(`${taskPath(str(entry.task_id))}/report`, {}, signal);
        if (r.version !== 'diagnostics-report-1' || r.scope_id !== entry.scope_id)
            throw new Error('REPORT_IDENTITY_MISMATCH');
        validate('AnalysisScope', r.scope);
        arr(r.stages);
        if (JSON.stringify(r.scope) !== JSON.stringify(entry.scope)) {
            // Object key ordering is not identity. Compare canonically.
            if (canonical(r.scope) !== canonical(entry.scope))
                throw new Error('REPORT_SCOPE_MISMATCH');
        }
        return r;
    }
    async page(task: string, kind: string, offset: number, signal?: AbortSignal): Promise<Item[]> {
        const p = await this.get(`${taskPath(task)}/items/${encodeURIComponent(kind)}`, { offset, limit: 100 }, signal);
        if (p.offset !== String(offset))
            throw new Error('PAGE_OFFSET_MISMATCH');
        return arr(p.items).map(value => { const row = obj(value); const data = obj(row.data); if (kind === 'fragment')
            validate('AnalysisFragment', data); return { id: str(row.id), data }; });
    }
    async all(task: string, kind: string, signal?: AbortSignal): Promise<Item[]> {
        const rows: Item[] = [];
        const seen = new Set<string>();
        for (let offset = 0;; offset += 100) {
            const page = await this.page(task, kind, offset, signal);
            for (const row of page) {
                if (seen.has(row.id))
                    throw new Error('DUPLICATE_ITEM');
                seen.add(row.id);
                rows.push(row);
            }
            if (page.length < 100)
                return rows;
        }
    }
}
export function canonical(value: unknown): string {
    if (Array.isArray(value))
        return `[${value.map(canonical).join(',')}]`;
    if (value && typeof value === 'object')
        return `{${Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => `${JSON.stringify(k)}:${canonical(v)}`).join(',')}}`;
    return JSON.stringify(value);
}

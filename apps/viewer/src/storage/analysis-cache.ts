import { obj, str } from '../api/analysis/client';
import type { Catalog } from '../api/analysis/client';
import type { LoadedReport } from '../features/analysis/model';
export const CACHE_KEY = 'tokenscope.analysis.metadata.v1';
const MAX_BYTES = 2 * 1024 * 1024, MAX_AGE = 7 * 86400000;
export interface Metadata {
    instance: string;
    contract: string;
    used: number;
    task: string;
    binding: string;
    appid: string;
    model: string;
    service: string | null;
    direction: string[];
    status: string;
    completed: string | null;
    scope: string;
    digest: string | null;
    count: string;
    window: unknown;
}
export function readMetadata(storage?: Storage, now = Date.now()): Metadata[] {
    try {
        storage ??= localStorage;
        const raw = storage.getItem(CACHE_KEY);
        if (!raw || new TextEncoder().encode(raw).length > MAX_BYTES)
            return [];
        const list: unknown = JSON.parse(raw);
        if (!Array.isArray(list))
            return [];
        return list.filter((x): x is Metadata => !!x && typeof x === 'object' && typeof x.used === 'number' && now - x.used < MAX_AGE && now >= x.used && typeof x.task === 'string' && typeof x.instance === 'string' && x.contract === 'analysis-common-1.0/diagnostics-http-1/diagnostics-discovery-1').slice(0, 100).map(x=>({instance:str(x.instance),contract:str(x.contract),used:x.used,task:str(x.task),binding:str(x.binding),appid:str(x.appid),model:str(x.model),service:x.service==null?null:str(x.service),direction:x.direction.map(str),status:str(x.status),completed:x.completed==null?null:str(x.completed),scope:str(x.scope),digest:x.digest==null?null:str(x.digest),count:str(x.count),window:x.window?{start_ns:str(obj(x.window).start_ns),end_ns:str(obj(x.window).end_ns)}:null}));
    }
    catch {
        return [];
    }
}
export function saveMetadata(instance: string, catalog: Catalog, storage?: Storage, now = Date.now()) {
    try {
        storage ??= localStorage;
        const rows: Metadata[] = [...catalog.items].sort((a,b)=>BigInt(str(a.sequence))>BigInt(str(b.sequence))?-1:1).map(x => { const b = obj(x.binding), s = obj(x.scope); const w = s.window ? obj(s.window) : null; return { instance, contract: 'analysis-common-1.0/diagnostics-http-1/diagnostics-discovery-1', used: now, task: str(x.task_id), binding: str(x.binding_id), appid: str(b.appid), model: str(b.model_id), service: b.common_name == null ? null : str(b.common_name), direction: (x.directions as string[]).slice(), status: str(x.status), completed: x.analysis_completed_at == null ? null : str(x.analysis_completed_at), scope: str(x.scope_id), digest: x.report_digest == null ? null : str(x.report_digest), count: str(s.request_count), window: w ? { start_ns: w.start_ns, end_ns: w.end_ns } : null }; });
        const keys = new Set(rows.map(x => `${x.instance}:${x.task}`));
        const all = [...rows, ...readMetadata(storage, now).filter(x => !keys.has(`${x.instance}:${x.task}`))].sort((a, b) => b.used - a.used).slice(0, 100);
        while (all.length && new TextEncoder().encode(JSON.stringify(all)).length > MAX_BYTES)
            all.pop();
        storage.setItem(CACHE_KEY, JSON.stringify(all));
    }
    catch { /* Quota / disabled storage: network and memory remain usable. */ }
}
export function reportKey(instance: string, task: string, scope: string, digest: string, direction: string) { return JSON.stringify([instance, 'analysis-common-1.0/diagnostics-http-1/diagnostics-discovery-1/analysis-recommendations-1', task, scope, digest, direction]); }
export class ReportCache {
    private values = new Map<string, {
        value: LoadedReport;
        bytes: number;
    }>();
    constructor(private count = 3, private bytes = 16 * 1024 * 1024) { }
    get(key: string) { const hit = this.values.get(key); if (hit) {
        this.values.delete(key);
        this.values.set(key, hit);
    } return hit?.value; }
    put(key: string, value: LoadedReport) { const bytes = new TextEncoder().encode(JSON.stringify(value)).length; this.values.delete(key); if (bytes > this.bytes)
        return; this.values.set(key, { value, bytes }); while (this.values.size > this.count || [...this.values.values()].reduce((n, x) => n + x.bytes, 0) > this.bytes)
        this.values.delete(this.values.keys().next().value!); }
    clear() { this.values.clear(); }
    delete(key: string) { this.values.delete(key); }
}

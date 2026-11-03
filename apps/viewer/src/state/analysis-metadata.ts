import { arr, obj, str } from '../api/analysis/client';
import type { AnalysisClient, Catalog } from '../api/analysis/client';
import { readMetadata, saveMetadata } from '../storage/analysis-cache';
import type { Metadata } from '../storage/analysis-cache';

export const ANALYSIS_METADATA_V2 = 'tokenscope.analysis.metadata.v2';
const contract = 'analysis-common-1.0/diagnostics-http-1/diagnostics-discovery-2/diagnostics-execution-2';
const maxBytes = 2 * 1024 * 1024, maxAge = 7 * 86400000;
function project(x: Metadata): Metadata {
    const w = x.window == null ? null : obj(x.window);
    return { instance: str(x.instance), contract, used: x.used, task: str(x.task), binding: str(x.binding), appid: str(x.appid), model: str(x.model), service: x.service == null ? null : str(x.service), direction: arr(x.direction).map(str), status: str(x.status), completed: x.completed == null ? null : str(x.completed), scope: str(x.scope), digest: x.digest == null ? null : str(x.digest), count: str(x.count), window: w ? { start_ns: str(w.start_ns), end_ns: str(w.end_ns) } : null };
}
export function readAnalysisMetadata(storage?: Storage, now = Date.now()): Metadata[] {
    try {
        storage ??= localStorage;
        const legacy = readMetadata(storage, now), raw = storage.getItem(ANALYSIS_METADATA_V2);
        if (!raw || new TextEncoder().encode(raw).length > maxBytes) return legacy;
        const values = arr(JSON.parse(raw)).map(obj).filter(x => x.contract === contract && typeof x.used === 'number' && x.used <= now && now - x.used < maxAge).slice(0, 100).map(x => project(x as unknown as Metadata));
        const keys = new Set(values.map(x => `${x.instance}:${x.task}`));
        return [...values, ...legacy.filter(x => !keys.has(`${x.instance}:${x.task}`))].slice(0, 100);
    } catch { return readMetadata(storage, now); }
}
export function saveAnalysisMetadata(api: AnalysisClient, catalog: Catalog, storage?: Storage, now = Date.now()) {
    if (!api.executionVersion) { saveMetadata(api.instance, catalog, storage, now); return; }
    try {
        storage ??= localStorage;
        const rows = [...catalog.items].sort((a, b) => BigInt(str(a.sequence)) > BigInt(str(b.sequence)) ? -1 : 1).map(x => {
            const b = obj(x.binding), s = obj(x.scope);
            return project({ instance: api.instance, contract, used: now, task: str(x.task_id), binding: str(x.binding_id), appid: str(b.appid), model: str(b.model_id), service: b.common_name == null ? null : str(b.common_name), direction: arr(x.directions).map(str), status: str(x.status), completed: x.analysis_completed_at == null ? null : str(x.analysis_completed_at), scope: str(x.scope_id), digest: x.report_digest == null ? null : str(x.report_digest), count: str(s.request_count), window: s.window });
        });
        const keys = new Set(rows.map(x => `${x.instance}:${x.task}`));
        const values = [...rows, ...readAnalysisMetadata(storage, now).filter(x => x.contract === contract && !keys.has(`${x.instance}:${x.task}`))].slice(0, 100);
        while (values.length && new TextEncoder().encode(JSON.stringify(values)).length > maxBytes) values.pop();
        storage.setItem(ANALYSIS_METADATA_V2, JSON.stringify(values));
    } catch { /* Optional offline directory only; never suppress a network report. */ }
}

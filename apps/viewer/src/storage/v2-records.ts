import type { Kind } from '../api/v2/client';
export interface Intent {
    key: string;
    path: string;
    body: Record<string, string>;
    runId?: string;
}
export interface Records {
    runs: string[];
    scenarios: {
        id: string;
        revision: string;
    }[];
    intent?: Intent;
    displayed?: {
        run: string;
        appid?: string;
    };
}
/** Small navigation/recovery metadata only. Never stores request bodies from CSV. */
export class V2Records {
    constructor(private readonly instance: string, private readonly kind: Kind, private readonly storage: Storage = localStorage) { }
    private get key() { return `tokenscope.v2.1:${this.kind}:${this.instance}`; }
    read(): Records {
        const raw = this.storage.getItem(this.key);
        if (!raw)
            return { runs: [], scenarios: [] };
        const value: unknown = JSON.parse(raw);
        if (!value || typeof value !== 'object' || !('runs' in value) || !Array.isArray(value.runs) || !value.runs.every(x => typeof x === 'string') || !('scenarios' in value) || !Array.isArray(value.scenarios))
            throw Error('本机记录格式不可用；原记录已保留，可用运行ID重新打开');
        const record = value as Records;
        if (!record.scenarios.every(x => x && typeof x.id === 'string' && typeof x.revision === 'string') || (record.displayed && typeof record.displayed.run !== 'string') || (record.intent && (typeof record.intent.key !== 'string' || typeof record.intent.path !== 'string' || !record.intent.body || typeof record.intent.body !== 'object' || !Object.values(record.intent.body).every(x => typeof x === 'string'))))
            throw Error('本机恢复记录格式不可用；原记录已保留');
        return record;
    }
    write(value: Records) { this.storage.setItem(this.key, JSON.stringify(value)); }
    remember(run: string) { const value = this.read(); this.write({ ...value, runs: [run, ...value.runs.filter(x => x !== run)].slice(0, 50) }); }
    saveIntent(intent: Intent) { this.write({ ...this.read(), intent }); }
    saveDisplayed(run: string, appid?: string) { this.write({ ...this.read(), displayed: { run, ...(appid ? { appid } : {}) } }); }
}

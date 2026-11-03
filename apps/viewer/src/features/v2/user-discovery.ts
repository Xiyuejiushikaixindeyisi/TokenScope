import { ApiError } from '../../api/client';
import type { V2Client } from '../../api/v2/client';
import type { DiscoveryEntry } from '../../api/v2/generated/user/HV2DiscoveryEntry';
export type { DiscoveryEntry };
/** Publish only complete snapshots. A conflict restarts from zero, never appends. */
export async function discoverUsers(api: V2Client, signal: AbortSignal, filters: Record<string, string> = {}): Promise<DiscoveryEntry[]> {
    for (let attempt = 0; attempt < 3; attempt++) {
        const entries: DiscoveryEntry[] = [], offsets = new Set<string>();
        let offset = '0', snapshot: string | undefined, total: string | undefined;
        try {
            for (;;) {
                signal.throwIfAborted();
                if (offsets.has(offset)) throw Error('目录分页未前进');
                offsets.add(offset);
                const page = await api.request('user', 'DiscoveryPage', '/runs', { query: { ...filters, offset, limit: 100, snapshot }, signal });
                signal.throwIfAborted();
                if (snapshot && (snapshot !== page.snapshot || total !== page.total)) throw Error('目录快照不一致');
                snapshot = page.snapshot; total = page.total; entries.push(...page.entries);
                if (BigInt(entries.length) > BigInt(total)) throw Error('目录记录数超出快照');
                if (page.next_offset === null) {
                    if (BigInt(entries.length) !== BigInt(total)) throw Error('目录记录数不一致');
                    return entries;
                }
                if (!page.entries.length || BigInt(page.next_offset) <= BigInt(offset) || BigInt(page.next_offset) > BigInt(total)) throw Error('目录分页未前进或超出快照');
                offset = page.next_offset;
            }
        } catch (e) {
            if (!(e instanceof ApiError && e.code === 'DISCOVERY_SNAPSHOT_CONFLICT') || attempt === 2) throw e;
        }
    }
    throw Error('目录快照持续变化，请手动刷新');
}
export const modelScopeKey = (entry: DiscoveryEntry) => JSON.stringify([entry.appid, entry.source.model_id, entry.source.common_name]);
export const entryKey = (entry: DiscoveryEntry) => JSON.stringify([entry.source.user_run_id, entry.appid, entry.source.index_revision]);
export function analysisSource(entry: DiscoveryEntry) {
    if (entry.appid === null) throw Error('空运行没有APPID分析范围');
    return { source_kind: 'user_v2' as const, user_run_id: entry.source.user_run_id, appid: entry.appid, expected_index_revision: entry.source.index_revision, window: null };
}
export function monitorSourceUrl(entry: DiscoveryEntry) {
    const source = analysisSource(entry);
    return `#/users?${new URLSearchParams({ run: source.user_run_id, appid: source.appid, revision: source.expected_index_revision })}`;
}

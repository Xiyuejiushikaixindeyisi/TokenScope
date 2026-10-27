import { useEffect, useState } from 'react';
import { getJson } from '../api/client';
import type { Dto, DtoName } from '../api/types';
import type { Scope } from '../domain/identity';
import { singleFlight } from '../api/query-cache';
const flight = singleFlight<unknown>();
const memory = new Map<string, { value: unknown; bytes: number }>();
/** At most 8MiB of paged read-only DTOs; no body or detail persistence. */
export function useRead<K extends DtoName>(name: K, path: string, query: Record<string, string | number | undefined>, scope?: Scope, cache = true, enabled = true) {
  const [revision, setRevision] = useState(0);
  const key = JSON.stringify([name, path, query, scope, revision]);
  const [state, setState] = useState<{ key: string; data: Dto<K> | null; error: string | null }>({ key, data: null, error: null });
  useEffect(() => {
    if (!enabled) return;
    let active = true;
    const load = async () => {
      const hit = cache ? memory.get(key) : undefined;
      if (hit) { memory.delete(key); memory.set(key, hit); return hit.value; }
      return flight(key, async () => {
        const value = await getJson(name, path, query, scope ? { scope } : {});
        if (cache) {
          memory.set(key, { value, bytes: new TextEncoder().encode(JSON.stringify(value)).length });
          let total = [...memory.values()].reduce((n, item) => n + item.bytes, 0);
          for (const [old, entry] of memory) { if (total <= 8 * 1024 * 1024) break; memory.delete(old); total -= entry.bytes; }
        }
        return value;
      });
    };
    void load().then(data => { if (active) setState({ key, data: data as Dto<K>, error: null }); }, () => { if (active) setState({ key, data: null, error: '读取失败，请重试。' }); });
    return () => { active = false; };
    // key is the complete immutable request identity; objects intentionally reconstructed by callers.
  }, [key, enabled]);
  return { ...(state.key === key ? state : { key, data: null, error: null }), reload: () => setRevision(value => value + 1) };
}

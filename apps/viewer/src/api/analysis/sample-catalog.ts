import { sha256 } from '@noble/hashes/sha2.js';
import { bytesToHex } from '@noble/hashes/utils.js';
import { arr, canonical, obj, str, validate, type AnalysisClient, type Catalog, type Obj } from './client';

export async function mergeSampleCatalog(api: AnalysisClient, old: Catalog, signal?: AbortSignal): Promise<Catalog> {
  const samples: Obj[] = [], seen = new Set<string>(), offsets = new Set<string>();
  let offset: string | null = '0';
  while (offset !== null) {
    if (offsets.has(offset)) throw Error('SAMPLE_CATALOG_CYCLE');
    offsets.add(offset);
    const page = await api.get('/diagnostics/v3/tasks', { offset, limit: 100 }, signal);
    if (page.service_instance_id !== api.instance) throw Error('SAMPLE_INSTANCE');
    for (const raw of arr(page.items)) {
      const item = obj(raw), execution = obj(item.execution), task = str(execution.task_id);
      if (seen.has(task) || !/^diag-[a-f0-9]{32}$/.test(task)) throw Error('SAMPLE_CATALOG_IDENTITY');
      seen.add(task);
      if (!item.sample_metadata) continue; // Older service metadata is not guessed from appid.
      const metadata = obj(item.sample_metadata), scope = validate('AnalysisScope', metadata.scope), source = obj(scope.source), selection = obj(item.source);
      if (scope.appid !== selection.appid || (selection.source_kind === 'base' ? selection.base_run_id !== source.base_run_id : selection.user_run_id !== source.user_run_id)) throw Error('SAMPLE_CATALOG_SOURCE');
      const binding = { appid: scope.appid, model_id: source.model_id, common_name: source.common_name, source_kind: source.user_run_id ? 'user_v2' : 'base' };
      const serialized = '{' + Object.entries(binding).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => JSON.stringify(k) + ': ' + JSON.stringify(v)).join(', ') + '}';
      const bindingId = bytesToHex(sha256(new TextEncoder().encode(serialized)));
      const reports = arr(execution.checkpoints ?? []).map(obj).filter(x => x.kind === 'report');
      const digest = reports.at(-1)?.sha256 ?? metadata.manifest_sha256;
      const status = execution.state === 'completed' ? 'ready' : reports.length ? 'partial' : execution.state;
      samples.push({ sample_v3: true, task_id: task, task_kind: 'analysis', binding_id: bindingId, binding,
        scope, scope_id: metadata.sample_id, sample_id: metadata.sample_id, manifest_sha256: metadata.manifest_sha256,
        selected_count: metadata.selected_count, report_digest: digest, status, directions: ['low_hit'],
        report_published: reports.length > 0, default_eligible: status === 'ready', legacy: false,
        analysis_completed_at: null, sequence: '0', execution });
    }
    offset = page.next_offset === null ? null : str(page.next_offset);
  }
  const maximum = old.items.reduce((n, e) => BigInt(str(e.sequence)) > n ? BigInt(str(e.sequence)) : n, 0n);
  samples.forEach((s, i) => { s.sequence = String(maximum + BigInt(samples.length - i)); });
  const selected = [...(old.selected_reports ?? old.defaults)];
  for (const binding of new Set(samples.map(x => str(x.binding_id)))) {
    const eligible = samples.filter(x => x.binding_id === binding && x.report_published);
    const entry = eligible.find(x => x.status === 'ready') ?? eligible[0];
    if (!entry) continue;
    const i = selected.findIndex(x => x.binding_id === binding && x.direction === 'low_hit');
    const value = { binding_id: binding, direction: 'low_hit', task_id: entry.task_id, sequence: entry.sequence };
    if (i < 0) selected.push(value); else selected[i] = value;
  }
  return { ...old, items: [...samples, ...old.items], selected_reports: selected,
    snapshot: canonical([old.snapshot, samples.map(x => [x.task_id, x.report_digest, x.status])]) };
}

import wire from '../../src/api/analysis/generated/diagnostics-execution-2.json' with { type: 'json' };

type O = Record<string, unknown>;
export const executionCapabilities = {
    service_instance_id: 'fixture-instance', version: 'diagnostics-execution-2',
    discovery_version: 'diagnostics-discovery-2', directions: ['low_hit', 'token_content'],
    minimum_selected_directions: '1', legacy_read_compatible: true,
    submission_url: '/diagnostics/v2/tasks', catalog_url: '/diagnostics/v2/catalog',
    partial_policy: 'ready_preferred_published_partial_fallback',
    budget_semantics: 'direction_isolated_compute_rule_reserved_retention', schemas: wire,
};

/** Synthetic directory bindings must describe the same frozen source as the report. */
export function scopeBinding(scope: O) {
    const source = scope.source as O;
    return { appid: scope.appid, model_id: source.model_id, common_name: source.common_name, source_kind: source.user_run_id ? 'user_v2' : 'base' };
}

/** Extend the test's existing v1 directory, retaining its explicit defaults/statuses. */
export function catalogV2(value: unknown) {
    const catalog = value as O;
    const selected = new Map<string, O>();
    const items = catalog.items as O[];
    for (const item of [...items].sort((a, b) => BigInt(String(a.sequence)) < BigInt(String(b.sequence)) ? -1 : 1)) {
        if (item.legacy !== false || item.report_published !== true || item.task_kind !== 'analysis' || !['ready', 'partial'].includes(String(item.status))) continue;
        for (const direction of item.directions as string[]) {
            const key = JSON.stringify([item.binding_id, direction]);
            if (item.status === 'partial' && selected.get(key)?.status === 'ready') continue;
            selected.set(key, { binding_id: item.binding_id, direction, task_id: item.task_id, sequence: item.sequence, status: item.status, selection_kind: item.status === 'ready' ? 'ready' : 'published_partial_fallback' });
        }
    }
    return { ...catalog, version: 'diagnostics-discovery-2', items, selected_reports: [...selected.values()] };
}

/** The report fixtures predate execution telemetry. Do not invent v2 scan statistics. */
export function legacyExecution(entry: O) {
    return { version: 'diagnostics-execution-2', task_id: entry.task_id, scope_id: entry.scope_id, status: entry.status, availability: 'not_computed', selected_directions: null, stages: [], telemetry: null };
}

export function taskFromPath(path: string): string | undefined {
    return /^\/diagnostics\/(?:v2\/)?tasks\/([^/]+)(?:\/|$)/.exec(path)?.[1];
}

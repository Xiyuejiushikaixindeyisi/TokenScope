export interface Scope {
  service_instance_id: string;
  view_schema_version: '1';
  run_id?: string;
  model_id?: string;
  appid?: string;
}
export function scopeKey(scope: Scope): string {
  return JSON.stringify([scope.service_instance_id, scope.view_schema_version, scope.run_id ?? null, scope.appid ?? null, scope.model_id ?? null]);
}
export function assertScope(actual: Record<string, unknown>, expected: Scope): void {
  for (const key of ['service_instance_id', 'view_schema_version', 'run_id', 'model_id', 'appid'] as const) {
    if (expected[key] !== undefined && actual[key] !== expected[key]) throw new Error(`SCOPE_MISMATCH:${key}`);
  }
}

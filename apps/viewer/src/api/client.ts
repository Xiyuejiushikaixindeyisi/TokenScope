import type { Dto, DtoName } from './types';
import { validateDto } from './validate';
import type { Scope } from '../domain/identity';
/** Root-relative paths only: never send instance headers to an external origin. */
export function apiPath(path: string, query: Record<string, string | number | undefined> = {}): string {
  if (!path.startsWith('/') || path.startsWith('//') || /[\\?#\s]/.test(path)) throw new Error('INVALID_API_PATH');
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) if (value !== undefined) params.set(key, String(value));
  return path + (params.size ? `?${params}` : '');
}
export class ApiError extends Error {
  constructor(readonly status: number, readonly code: string, message: string) { super(message); }
}
export interface JsonRequestOptions {
  signal?: AbortSignal;
  scope?: Scope;
  instanceId?: string;
  fetcher?: typeof fetch;
}
/** One request per explicit call. No retries, polling, refocus fetching or analysis side effects. */
export async function getJson<K extends DtoName>(name: K, path: string, query: Record<string, string | number | undefined> = {}, options: JsonRequestOptions = {}): Promise<Dto<K>> {
  const headers = new Headers({ Accept: 'application/json' });
  if (options.instanceId) headers.set('X-TokenScope-Instance-Id', options.instanceId);
  const response = await (options.fetcher ?? fetch)(apiPath(path, query), { method: 'GET', headers, credentials: 'same-origin', redirect: 'error', ...(options.signal ? { signal: options.signal } : {}) });
  const contentType = response.headers.get('Content-Type') ?? '';
  if (!contentType.toLowerCase().includes('application/json')) throw new ApiError(response.status, 'INVALID_CONTENT_TYPE', '响应格式不可用');
  const payload: unknown = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(await response.arrayBuffer()));
  if (!response.ok) {
    const error = validateDto('Error', payload);
    throw new ApiError(response.status, error.error.code, error.error.message);
  }
  return validateDto(name, payload, options.scope);
}

/** Explicit user actions only; caller retains idempotency key or revision on failure. */
export async function writeJson<K extends DtoName>(name: K, method: 'POST' | 'PUT', path: string, body: unknown, instanceId: string, fetcher: typeof fetch = fetch): Promise<Dto<K>> {
  const response = await fetcher(apiPath(path), { method, credentials: 'same-origin', redirect: 'error', headers: { 'Content-Type': 'application/json', Accept: 'application/json', 'X-TokenScope-Instance-Id': instanceId }, body: JSON.stringify(body) });
  const payload: unknown = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(await response.arrayBuffer()));
  if (!response.ok) { const error = validateDto('Error', payload); throw new ApiError(response.status, error.error.code, error.error.message); }
  return validateDto(name, payload);
}

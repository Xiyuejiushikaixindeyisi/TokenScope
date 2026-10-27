import type { Dto } from '../api/types';
export interface ViewState {
  catalog: Dto<'CatalogResponse'> | null;
  selection: { appid: string; model_id: string } | null;
  snapshot: Dto<'ViewSnapshot'> | null;
  pending: Dto<'ViewSnapshot'> | null;
  pinned: boolean;
  loading: boolean;
  connection: 'connecting' | 'connected' | 'disconnected';
  error: string | null;
  cacheWarning: string | null;
}
export class ViewStore {
  private state: ViewState = { catalog: null, selection: null, snapshot: null, pending: null, pinned: false, loading: false, connection: 'connecting', error: null, cacheWarning: null };
  private readonly listeners = new Set<() => void>();
  getSnapshot = () => this.state;
  subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  update(patch: Partial<ViewState>) { this.state = { ...this.state, ...patch }; for (const listener of this.listeners) listener(); }
}

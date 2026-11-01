export interface AnalysisRoute {
    binding: string;
    direction: 'low_hit' | 'token_content';
    task: string;
    item: string;
    mode: 'latest' | 'history';
}
export function readRoute(): AnalysisRoute {
    const q = new URLSearchParams(location.hash.split('?')[1]);
    return { binding: q.get('binding') ?? '', direction: q.get('direction') === 'token_content' ? 'token_content' : 'low_hit', task: q.get('task') ?? '', item: q.get('item') ?? '', mode: q.get('mode') === 'history' ? 'history' : 'latest' };
}
export function routeUrl(r: AnalysisRoute) { const q = new URLSearchParams({ binding: r.binding, direction: r.direction, mode: r.mode }); if (r.task)
    q.set('task', r.task); if (r.item)
    q.set('item', r.item); return `#/analysis?${q}`; }
export function navigate(r: AnalysisRoute, replace = false) { if (replace) {
    history.replaceState(history.state, '', routeUrl(r));
    window.dispatchEvent(new HashChangeEvent('hashchange'));
}
else {
    history.pushState(history.state, '', routeUrl(r));
    window.dispatchEvent(new HashChangeEvent('hashchange'));
} }

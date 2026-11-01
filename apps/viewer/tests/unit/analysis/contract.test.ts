import { describe, it, expect } from 'vitest';
import { validate, canonical, AnalysisClient } from '../../../src/api/analysis/client';
import low from '../../../../../docs/tasks/prefix-analysis/FRONTEND_READONLY_EXAMPLES.json';
import token from '../../../../../docs/tasks/length-analysis/FRONTEND_READONLY_EXAMPLES.json';
describe('analysis contract', () => {
  it('validates received scopes, fragments and discovery without converting integers', () => {
    for (const x of token.examples) { validate('AnalysisScope', x.scope); for (const r of x.fragment_list_response.items) validate('AnalysisFragment', r.data); }
    validate('catalog', low.ready_chain.responses['/diagnostics/discovery/catalog'].body);
    expect(canonical({b:'9007199254740993',a:null})).toBe(canonical({a:null,b:'9007199254740993'}));
    expect(() => validate('AnalysisScope', {})).toThrow();
  });
  it('rejects inconsistent capability identities', async () => {
    const fetcher = (async (path: string) => Response.json(path.includes('discovery') ? {version:'diagnostics-discovery-1',service_instance_id:'b'} : {contract_version:'analysis-common-1.0',http_version:'diagnostics-http-1',service_instance_id:'a'})) as typeof fetch;
    await expect(AnalysisClient.connect(undefined, fetcher)).rejects.toThrow('实例');
  });
});

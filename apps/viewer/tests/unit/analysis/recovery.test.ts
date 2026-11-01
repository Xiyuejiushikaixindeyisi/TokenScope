import { describe,it,expect,vi } from 'vitest';
import { SSEDecoder } from '../../../src/state/analysis-discovery';
import { saveMetadata,readMetadata,ReportCache,CACHE_KEY } from '../../../src/storage/analysis-cache';
import low from '../../../../../docs/tasks/prefix-analysis/FRONTEND_READONLY_EXAMPLES.json';
import type { LoadedReport } from '../../../src/features/analysis/model';
describe('analysis recovery and bounded cache',()=>{
 it('storage getter denial does not escape metadata persistence',()=>{
  const c=low.ready_chain.responses['/diagnostics/discovery/catalog'].body;
  const denied=vi.spyOn(window,'localStorage','get').mockImplementation(()=>{throw new DOMException('blocked','SecurityError');});
  try {expect(()=>saveMetadata(c.service_instance_id,{snapshot:c.snapshot,cursor:c.event_cursor,items:c.items,defaults:c.defaults})).not.toThrow();expect(readMetadata()).toEqual([]);} finally {denied.mockRestore();}
 });
 it('assembles split SSE frames, ignores heartbeat and retains exact cursor',()=>{const p=new SSEDecoder();expect(p.push(': heartbeat\r\n\r\n')).toEqual([]);expect(p.push('event: terminal\r')).toEqual([]);expect(p.push('\nid: huge:9007199254740993\r\ndata: {"a":')).toEqual([]);expect(p.push('1}\r\n\r\n')).toEqual([{event:'terminal',id:'huge:9007199254740993',data:'{"a":1}'}]);});
 it('persists only projected metadata and expires it without touching source reports',()=>{localStorage.clear();const c=low.ready_chain.responses['/diagnostics/discovery/catalog'].body;saveMetadata(c.service_instance_id,{snapshot:c.snapshot,cursor:c.event_cursor,items:c.items,defaults:c.defaults},localStorage,100);const raw=localStorage.getItem(CACHE_KEY)!;expect(raw).not.toContain('profile_json');expect(raw).not.toContain('runtime_options');expect(raw).not.toContain('raw_body');expect(readMetadata(localStorage,101)).toHaveLength(1);expect(readMetadata(localStorage,8*86400000)).toHaveLength(0);});
 it('storage denial does not fail report reading and memory cache is LRU bounded',()=>{const c=low.ready_chain.responses['/diagnostics/discovery/catalog'].body;expect(()=>saveMetadata(c.service_instance_id,{snapshot:c.snapshot,cursor:c.event_cursor,items:c.items,defaults:c.defaults},{getItem(){throw Error('disabled');},setItem(){throw Error('quota');}} as unknown as Storage)).not.toThrow();const cache=new ReportCache(1,1000);const r={cards:[]} as unknown as LoadedReport;cache.put('a',r);cache.put('b',r);expect(cache.get('a')).toBeUndefined();expect(cache.get('b')).toBe(r);});
});

import { readFileSync } from 'node:fs';
import type { Obj } from '../../../src/api/analysis/client';
import { AnalysisClient, obj, str } from '../../../src/api/analysis/client';
import schemas from '../../../src/api/analysis/generated/analysis-recommendations-1.json';
export interface TaskSample { task_id: string; report_sha256: string; report: Obj; responses: Record<string, Obj>; examples: Record<string, Obj> }
interface Dataset { name: string; tasks: TaskSample[] }
export const samples = (JSON.parse(readFileSync('../../docs/tasks/prefix-analysis/FRONTEND_REWORK_IMPLEMENTATION_EXAMPLES_ARL3.json', 'utf8')) as { datasets: Dataset[] }).datasets;
export const allTasks = samples.flatMap(x => x.tasks);
export function entry(t: TaskSample): Obj { return { task_id: t.task_id, scope_id: t.report.scope_id, scope: t.report.scope, report_digest: t.report_sha256 }; }
export function client(t: TaskSample, override?: (path: string, response: Obj) => Obj) {
    const calls: string[] = [];
    const fetcher = (async (input: string | URL | Request, init?: RequestInit) => {
        if (init?.method !== 'GET') throw Error('GET_ONLY');
        const url = new URL(String(input), 'http://fixture'); const path = decodeURIComponent(url.pathname); calls.push(path);
        let response: Obj;
        if (path.endsWith('/recommendations/capabilities')) response = { version: 'analysis-recommendations-1', service_instance_id: 'fixture', read_only: true, token_rule_ids: ['T2', 'T3', 'T4'], schemas: schemas.models };
        else if (path.endsWith('/report')) response = t.report;
        else if (t.examples[path]) response = t.examples[path]!;
        else {
            const key = path.split('/').at(-1)!;
            if (t.responses[key]) {
                response = structuredClone(t.responses[key]!);
                if (key === 'recommendations') response.items = (response.items as Obj[]).filter(x => obj(x.data).direction === url.searchParams.get('direction'));
            } else {
                const row = (t.responses.recommendations!.items as Obj[]).find(x => x.id === key);
                if (!row) return Response.json({ error: { code: 'RECOMMENDATION_NOT_FOUND', message: 'Unknown result' } }, { status: 404 });
                response = obj(row.data);
            }
        }
        return Response.json(override ? override(path, response) : response);
    }) as typeof fetch;
    return { api: new AnalysisClient('fixture', fetcher), calls };
}
export const low = samples[0]!.tasks.find(x => obj(x.report.scope).appid === 'a')!;
export const token = samples.find(x => x.name === 'test_real_same_task_recommenda0')!.tasks.find(x => x.report.status === 'ready' && (x.responses.recommendations!.items as Obj[]).length > 0)!;
export const taskScope = (t: TaskSample) => str(t.report.scope_id);

import { canonical, str } from '../api/analysis/client';
import type { AnalysisClient, Obj } from '../api/analysis/client';

/** Both first reads and appended pages must address the same frozen report. */
export function analysisReportKey(api: AnalysisClient, entry: Obj, direction: string): string {
    return canonical([api.instance, 'analysis-common-1.0', 'diagnostics-http-1', 'analysis-recommendations-1', api.executionVersion, api.executionVersion ? 'diagnostics-discovery-2' : 'diagnostics-discovery-1', str(entry.task_id), str(entry.scope_id), str(entry.report_digest), direction]);
}

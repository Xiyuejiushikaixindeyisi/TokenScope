import { arr, obj, str } from '../../api/analysis/client';
import type { LoadedReport } from './model';

const reasons: Record<string, string> = {
    NO_CONFIGURED_RECIPES: '本报告未配置自动修改方案，未进行修改后的收益评估；已完成的检查和差异仍可查看。',
    TOKEN_FRAGMENT_INCOMPLETE: '部分请求的内容检查未完整完成，暂不能据此给出完整修改收益。',
    FRAGMENT_RETENTION_TRUNCATED: '部分内容证据因保存上限未保留，修改收益评估受限；不等于这些请求未检查。',
    FINDING_RETENTION_TRUNCATED: '发现的差异超过证据保存上限，当前只展示已保存的部分；不等于扫描已停止。',
    CANDIDATE_LOOKUP_TRUNCATED: '可比较请求的查找达到上限，尚未覆盖所有候选比较。',
    COMPARISON_COUNT_BUDGET_EXHAUSTED: '请求比较达到次数上限，部分比较未完成。',
    ENCODING_BUDGET_EXHAUSTED: '编码计算达到上限，相关分析或收益评估未完成。',
    RECIPE_BASIS_MISSING: '缺少该修改适用的业务依据，暂不能提供修改后的收益。',
    REFERENCE_MAPPING_MISSING: '缺少可用的内容引用映射，暂不能验证这项修改。',
    NO_APPLICABLE_TARGETS: '当前范围没有适用的分析目标。',
};
export function executionReason(code: string): string {
    return reasons[code] ?? (code.includes('BUDGET') || code.includes('LIMIT') ? `相关检查达到处理限制（${code}），结果可能不完整。` : `报告限制：${code}。`);
}
export function reportReasons(data: LoadedReport): string[] {
    const stages = arr(data.execution?.stages ?? []).map(obj).filter(x => x.direction === data.direction);
    const parts = [...stages];
    // Recommendation summary covers Token proposal/evaluation, independent of low-hit checks.
    if (data.direction === 'token_content') parts.push(data.summary, ...['proposal_coverage', 'evaluation_coverage'].flatMap(k => data.summary[k] ? [obj(data.summary[k])] : []));
    return [...new Set(parts.flatMap(x => [...arr(x.reason_codes ?? []).map(str), ...(typeof x.reason === 'string' ? [x.reason] : [])]))];
}
function number(value: unknown) { return value == null ? '未提供' : BigInt(str(value)).toLocaleString('en-US'); }
function complete(value: unknown) { return value === true ? '完整' : value === false ? '未完整' : '未提供'; }
function ruleCounts(value: unknown): string {
    return value == null ? '未提供' : Object.entries(obj(value)).map(([rule, count]) => `${rule}：${number(count)}`).join('；') || '无记录';
}
export function ExecutionStatus({ data }: { data: LoadedReport }) {
    const execution = data.execution;
    if (!execution) return null;
    if (execution.availability === 'not_computed') return <p className="notice">这份历史报告未记录新版执行状态；仍按原报告读取已发布结果，不能据此判断检查完整性。</p>;
    const stages = arr(execution.stages).map(obj).filter(s => s.direction === data.direction);
    const codes = reportReasons(data);
    return <>{codes.length > 0 && <div className="notice">{codes.map(code => <p key={code}>{executionReason(code)}</p>)}</div>}
        <details className="report-detail"><summary>本次检查范围与限制</summary><div className="a-pad">
            <p>本任务分析方向：{arr(execution.selected_directions).map(d => d === 'low_hit' ? '低命中率' : 'Token异常').join('、')}。</p>
            {stages.map((s, i) => <div key={i}>
                <p>已检查请求：{number(s.checked_requests)} / {number(s.eligible_requests)}；扫描：{complete(s.scan_complete)}；比较：{complete(s.comparison_complete)}；证据保存：{complete(s.retention_complete)}。</p>
                {data.direction === 'low_hit' ? <><p>各规则发现条数：{ruleCounts(s.detected_by_rule)}。</p><p>各规则保留条数：{ruleCounts(s.retained_by_rule)}。条数不是影响请求数量。</p></> : <>
                    <p>内容检查完整性：{complete(s.fragments_complete)}；已保留请求：{number(s.retained_requests)}。</p>
                    {s.rule_status_counts != null && Object.entries(obj(s.rule_status_counts)).map(([rule, counts]) => <p key={rule}>{rule}：{Object.entries(obj(counts)).map(([status, count]) => `${({ completed: '完成', not_applicable: '不适用', partial: '部分完成', failed: '失败', not_checked: '未检查' } as Record<string, string>)[status] ?? status} ${number(count)}`).join('；')}</p>)}
                </>}
            </div>)}
            {data.ruleCoverage?.map((row, i) => <p key={i}>{arr(row.supported_rules ?? []).map(str).join(' / ')}：已访问候选比较 {number(row.candidate_comparisons)}；适用对数 {row.applicable_pairs == null ? '未单独统计' : number(row.applicable_pairs)}。</p>)}
            <p>各规则可能重复涉及同一请求，不能相加为影响范围；卡片数量仅统计已保存证据。未提供的值不等于零。</p>
        </div></details></>;
}

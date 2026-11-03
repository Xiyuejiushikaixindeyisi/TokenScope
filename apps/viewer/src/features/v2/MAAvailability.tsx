import { ApiError } from '../../api/client';
import { segment, type V2Client } from '../../api/v2/client';
import type { Snapshot } from '../../api/v2/generated/ma';
import type { Availability, AvailabilityResponse, Reasons } from '../../api/v2/generated/ma/AvailabilityResponse';
export type Explanation = { state: 'loading' | 'legacy' | 'error'; message?: string } | { state: 'ready'; value: AvailabilityResponse['availability'] };
export const availabilityStates = { available: '可用', partial: '部分样本（仅已知子集，不外推全量）', unavailable: '不可用', empty: '空范围（无请求）' };
const reasons: Record<Reasons[number], string> = {
    empty_now: '当前小时无请求', empty_bin: '此桶无请求', no_valid_prompt: '无有效生产输入',
    source_cached_missing: '本实例源 cached_tokens 缺失', invalid_cached: '本实例 cached_tokens 无效', invalid_prompt: '本实例 prompt_tokens 无效',
    no_real_samples: '无有效真实观测', no_paired_samples: '无配对样本', no_ideal_samples: '无有效理想回放样本',
    warmup_order_conflict: '预热顺序冲突，理想回放不可用', no_valid_prewarm: '无有效预热，按冷启动对照',
    zero_input_denominator: '输入总量为0，命中率分母为0', partial_sample_coverage: '仅部分请求具有有效观测',
};
export function MetricAvailability({ value }: { value?: Availability | undefined }) {
    if (!value) return null;
    return <small className="cell-sub" data-availability={value.state}>{availabilityStates[value.state]} · 样本 {value.sample_count}/{value.population_count}
        {value.reasons.map(reason => <span className="cell-sub" key={reason}>{reasons[reason]}</span>)}
        {value.denominator !== null && <span className="cell-sub">分母 {value.denominator} {value.denominator_unit === 'seconds' ? '秒' : '输入Token'}</span>}
    </small>;
}
export function ExplanationStatus({ explanation, retry }: { explanation?: Explanation | undefined; retry(): void }) {
    if (!explanation || explanation.state === 'loading') return <small className="cell-sub" role="status">正在读取指标说明…</small>;
    if (explanation.state === 'legacy') return <small className="cell-sub">历史结果未记录细化原因；原快照值保持，不自动重算。</small>;
    if (explanation.state === 'error') return <small className="cell-sub" role="alert">指标说明读取失败：{explanation.message}；原快照值保持。<button onClick={retry}>重试指标说明</button></small>;
    return null;
}
export function assertAvailabilityScope(snapshot: Snapshot, response: AvailabilityResponse) {
    if (snapshot.service_instance_id !== response.service_instance_id || snapshot.ma_run_id !== response.ma_run_id || snapshot.instance.instance_uuid !== response.availability.instance_uuid || snapshot.instance.model_standard_name !== response.availability.model_standard_name || Object.entries(snapshot.binding).some(([k, value]) => response.binding[k as keyof typeof response.binding] !== value) || Object.entries(snapshot.instance.coverage).some(([k, value]) => response.availability.coverage[k as keyof typeof response.availability.coverage] !== value)) throw Error('指标说明与快照范围不一致');
}
export async function readMAAvailability(api: V2Client, snapshot: Snapshot, signal: AbortSignal): Promise<Explanation> {
    try {
        const response = await api.request('ma', 'AvailabilityResponse', `/runs/${segment(snapshot.ma_run_id)}/instances/${segment(snapshot.instance.instance_uuid)}/availability`, { signal });
        assertAvailabilityScope(snapshot, response);
        return { state: 'ready', value: response.availability };
    } catch (error) {
        if (signal.aborted || api.signal.aborted) throw error;
        if (error instanceof ApiError && error.status === 409 && error.code === 'AVAILABILITY_NOT_RECORDED') return { state: 'legacy' };
        return { state: 'error', message: error instanceof Error ? error.message : '读取失败' };
    }
}

import examples from '../../../../docs/tasks/monitoring/v2-ma/hv2-availability/examples.json';
import original from '../../../../docs/contracts/ma-monitoring-v2/frontend.examples.json';
import { validateV2 } from '../../src/api/v2/client';
export const availabilityCases = examples.cases;
export function maCase(name: string) {
    const item = availabilityCases.find(v => v.name === name)!;
    const response = validateV2('ma', 'AvailabilityResponse', structuredClone(item.response));
    const base = validateV2('ma', 'Snapshot', original.examples.find(v => v.type === 'Snapshot')!.payload);
    // Strict presentation projection: excerpt has no distributions; retain original histogram DTOs.
    const snapshot = validateV2('ma', 'Snapshot', { ...base, service_instance_id: response.service_instance_id, ma_run_id: response.ma_run_id, binding: structuredClone(response.binding), instance: { ...base.instance, ...item.snapshot_excerpt } });
    return { response, snapshot };
}

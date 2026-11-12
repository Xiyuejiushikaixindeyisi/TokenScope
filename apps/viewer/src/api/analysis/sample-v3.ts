import Ajv from 'ajv';
import { sha256 } from '@noble/hashes/sha2.js';
import { bytesToHex } from '@noble/hashes/utils.js';
import schemas from './generated/diagnostics-report-3.json';
import sampling from './generated/diagnostics-sampling-3.json';
import { apiPath } from '../client';
import { arr, obj, str, type Obj } from './client';

const ajv = new Ajv({ strict: false, allErrors: true });
for (const [keyword, compare] of Object.entries({
  'x-integer-minimum': (v: bigint, bound: bigint) => v >= bound,
  'x-integer-maximum': (v: bigint, bound: bigint) => v <= bound,
  'x-integer-exclusiveMinimum': (v: bigint, bound: bigint) => v > bound,
})) ajv.addKeyword({ keyword, type: 'string', validate: (bound: string, value: string) => /^-?\d+$/.test(value) && compare(BigInt(value), BigInt(bound)) });
const reportValidator = ajv.compile(schemas.SampleReport3);
const executionValidator = ajv.compile(schemas.Execution3);
const receiptValidator = ajv.compile(sampling.receipt);
const evidenceValidator = ajv.compile(schemas.EvidenceBundle3);
export const integer = (value: unknown): bigint => {
  if (typeof value !== 'string' || !/^-?(0|[1-9][0-9]*)$/.test(value)) throw Error('INVALID_INTEGER');
  return BigInt(value);
};
function stable(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stable).join(',')}]`;
  if (value && typeof value === 'object') {
    const v = obj(value);
    return `{${Object.keys(v).sort().map(k => `${JSON.stringify(k)}:${stable(v[k])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}
export function verifySampleCapabilities(value: Obj): void {
  const offered = obj(value.schemas);
  if (stable(offered.report) !== stable(schemas.SampleReport3) || stable(offered.execution) !== stable(schemas.Execution3) || stable(offered.receipt) !== stable(sampling.receipt)) throw Error('V3_CONTRACT_MISMATCH');
}
export function validateSampleReport(value: unknown, task?: string): Obj {
  if (!reportValidator(value)) throw Error('INVALID_SAMPLE_REPORT');
  const report = obj(value), sample = obj(report.sample), decision = obj(sample.decision);
  if (task && report.task_id !== task) throw Error('REPORT_TASK_MISMATCH');
  const windows = arr(decision.windows).map(obj), seen = new Set<string>();
  for (const window of windows) {
    const members = arr(window.members).map(obj);
    const digest = bytesToHex(sha256(new TextEncoder().encode(members.map(m => stable(m.key) + '\n').join(''))));
    if (digest !== window.keys_digest) throw Error('WINDOW_DIGEST');
    let p = 0n, bytes = 0n;
    for (const member of members) {
      const key = stable(member.key);
      if (seen.has(key)) throw Error('SAMPLE_OVERLAP');
      seen.add(key); p += integer(member.prompt_tokens); bytes += integer(member.raw_bytes);
    }
    if (p !== integer(window.prompt_tokens) || bytes !== integer(window.raw_bytes)) throw Error('SAMPLE_TOTAL_MISMATCH');
  }
  const identity = { ...sample }; delete identity.verification_bytes;
  if ('sample:' + bytesToHex(sha256(new TextEncoder().encode(stable(identity)))) !== report.sample_id) throw Error('SAMPLE_IDENTITY');
  if (BigInt(seen.size) > integer(obj(decision.limits).max_requests)) throw Error('SAMPLE_LIMIT');
  if (integer(decision.parent_count) !== integer(decision.admitted_count) + integer(decision.excluded_count)) throw Error('SOURCE_TOTAL_MISMATCH');
  const evidence = new Map<string, Obj>();
  const discoveryKeys = new Set(arr(windows.find(w => w.role === 'discovery')?.members).map(m => stable(obj(m).key)));
  for (const record of arr(obj(report.discovery).evidence_requests ?? []).map(obj)) {
    const key = stable(record.request_key);
    if (!discoveryKeys.has(key) || evidence.has(key)) throw Error('EVIDENCE_SCOPE');
    if (bytesToHex(sha256(new TextEncoder().encode(str(record.raw_body)))) !== record.raw_sha256) throw Error('EVIDENCE_DIGEST');
    evidence.set(key, record);
  }
  for (const group of arr(obj(report.discovery).cause_groups).map(obj)) {
    if (!group.comparison) continue; // Older V3 results remain readable with an explicit missing-evidence label.
    const pair = obj(group.comparison);
    for (const side of ['left', 'right']) {
      const record = evidence.get(stable(pair[side]));
      if (report.evidence_mode === 'sealed_examples') {
        if (!discoveryKeys.has(stable(pair[side]))) throw Error('PAIR_EVIDENCE_IDENTITY');
      } else if (!record || record.raw_sha256 !== pair[side + '_raw_sha256']) throw Error('PAIR_EVIDENCE_IDENTITY');
    }
  }
  for (const recommendation of arr(report.recommendations).map(obj)) {
    const finding = obj(recommendation.finding), recipe = obj(finding.recipe);
    const discovery = windows.find(w => w.role === 'discovery');
    const keys = new Set(arr(discovery?.members).map(m => stable(obj(m).key)));
    const comparison = obj(finding.comparison);
    if (!keys.has(stable(comparison.left)) || !keys.has(stable(comparison.right))) throw Error('FINDING_OUTSIDE_DISCOVERY');
    if ('finding:' + bytesToHex(sha256(new TextEncoder().encode(stable([finding.rule_version, comparison, recipe])))) !== finding.finding_id) throw Error('FINDING_IDENTITY');
    const nativeRecipe = { ...recipe };
    if (finding.rule_version === 'clock-3.1') nativeRecipe.block_indices = arr(recipe.block_indices).map(x => { const n = integer(x); if (n < 0n || n > 100000n) throw Error('BLOCK_INDEX'); return Number(n); });
    else if (recipe.slot_index !== null) { const n = integer(recipe.slot_index); if (n < 0n || n > 100000n) throw Error('SLOT_INDEX'); nativeRecipe.slot_index = Number(n); }
    const digest = bytesToHex(sha256(new TextEncoder().encode(stable(nativeRecipe))));
    if (digest !== recommendation.transformation_digest) throw Error('RECIPE_DIGEST_MISMATCH');
    const roles = new Set<string>();
    for (const evaluation of arr(recommendation.windows).map(obj)) {
      const role = str(evaluation.role);
      if (roles.has(role)) throw Error('DUPLICATE_WINDOW');
      roles.add(role);
      if (evaluation.transformation_digest !== digest) throw Error('REVIEW_RECIPE_CHANGED');
      if (evaluation.complete !== true) {
        if (evaluation.after !== null || evaluation.before !== null || evaluation.improvement_pp !== null) throw Error('INCOMPLETE_TOTALS');
        continue;
      }
      const window = windows.find(w => w.role === role);
      if (!window || integer(evaluation.n) !== BigInt(arr(window.members).length)) throw Error('WINDOW_SCOPE_MISMATCH');
      const b = obj(evaluation.before), a = obj(evaluation.after);
      for (const metrics of [b, a]) {
        if (['p', 'h', 'c'].some(k => integer(metrics[k]) < 0n)) throw Error('NEGATIVE_METRIC');
        if (integer(metrics.p) !== integer(metrics.h) + integer(metrics.c)) throw Error('METRIC_CONSERVATION');
      }
      if (['n', 'matched', 'modified'].some(k => integer(evaluation[k]) < 0n)) throw Error('NEGATIVE_COUNT');
      if (integer(evaluation.modified) > integer(evaluation.matched) || integer(evaluation.matched) > integer(evaluation.n)) throw Error('TARGET_COUNTS');
      const bp = integer(b.p), ap = integer(a.p);
      if (!bp || !ap) {
        if (evaluation.improvement_pp !== null || evaluation.status !== 'unavailable') throw Error('ZERO_DENOMINATOR');
      } else {
        const pp = obj(evaluation.improvement_pp), n = integer(pp.numerator), d = integer(pp.denominator);
        if (d <= 0n || n * bp * ap !== 100n * (integer(a.h) * bp - integer(b.h) * ap) * d) throw Error('GAIN_MISMATCH');
        if (evaluation.status !== (n > 0n ? 'positive' : n < 0n ? 'negative' : 'zero')) throw Error('GAIN_STATUS');
      }
    }
  }
  return report;
}
export function ratio(n: unknown, d: unknown): string {
  const numerator = integer(n), denominator = integer(d);
  if (denominator <= 0n) return '不可计算';
  const scaled = numerator * 100n / denominator;
  const absolute = scaled < 0n ? -scaled : scaled;
  return `${numerator < 0n ? '-' : ''}${absolute / 100n}.${String(absolute % 100n).padStart(2, '0')}`;
}
export class SampleClient3 {
  constructor(readonly instance: string, readonly fetcher: typeof fetch = (...args) => fetch(...args)) {}
  async request(path: string, body?: unknown, signal?: AbortSignal, query: Record<string, string> = {}): Promise<Obj> {
    const response = await this.fetcher(apiPath(path, query), { method: body === undefined ? 'GET' : 'POST', credentials: 'same-origin', redirect: 'error',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'x-tokenscope-service-instance': this.instance, 'x-tokenscope-instance-id': this.instance },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }), ...(signal ? { signal } : {}) });
    const value: unknown = await response.json();
    if (!response.ok) throw Error(str(obj(obj(value).error).code));
    return obj(value);
  }
  async execution(path: string, body?: unknown): Promise<Obj> {
    const value = await this.request(path, body);
    if (!executionValidator(value)) throw Error('INVALID_V3_EXECUTION');
    return value;
  }
  async receipt(path: string, body?: unknown): Promise<Obj> {
    const value = await this.request(path, body);
    if (!receiptValidator(value)) throw Error('INVALID_V3_PREPARATION');
    return value;
  }
  async evidence(task: string, sample: string, owner: string, signal?: AbortSignal): Promise<Obj[]> {
    const value = await this.request(`/diagnostics/v3/tasks/${encodeURIComponent(task)}/evidence/${encodeURIComponent(owner)}`, undefined, signal);
    if (!evidenceValidator(value) || value.task_id !== task || value.sample_id !== sample || value.owner_id !== owner) throw Error('EVIDENCE_IDENTITY');
    const examples = arr(value.examples).map(obj);
    if (examples.length > 3 || examples.some(e => e.task_id !== task || e.owner_id !== owner)) throw Error('EVIDENCE_OWNER');
    return examples;
  }
  async report(task: string, signal?: AbortSignal): Promise<Obj> {
    return validateSampleReport(await this.request(`/diagnostics/v3/tasks/${encodeURIComponent(task)}/report`, undefined, signal), task);
  }
}

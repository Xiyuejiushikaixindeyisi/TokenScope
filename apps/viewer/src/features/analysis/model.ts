import { arr, canonical, obj, str, taskPath } from '../../api/analysis/client';
import type { Item, Obj, AnalysisClient } from '../../api/analysis/client';
import { resultExamples, resultPage, summary, verifyItem } from '../../api/analysis/recommendations';
import type { Direction, ResultKind } from '../../api/analysis/recommendations';
import { ApiError } from '../../api/client';
export type { Direction } from '../../api/analysis/recommendations';
export interface Card {
    id: string; kind: ResultKind; rule: string; title: string; tag: string; description: string; advice: string;
    conditions: string[]; synthetic: boolean; data: Obj; evaluation: Obj | null; metrics: Obj | null;
    affected: string | null; total: string; limitation: string;
    // Display-only detector overview. The selected owners remain unmodified backend groups.
    differenceGroups?: Obj[];
}
export interface LoadedReport {
    entry: Obj; report: Obj; summary: Obj; cards: Card[]; direction: Direction;
    execution?: Obj | null;
    ruleCoverage?: Obj[];
    offsets: Record<ResultKind, string | null>; hasMore: boolean;
}
export const checks = {
    low_hit: [['L1 · 前部动态内容', '查找前部频繁变化的日期、编号等内容，分析是否打断相同前缀的复用。'], ['L2 · 工具排列', '查找定义相同、排列顺序不一致的工具列表。'], ['L3 · 工具定义', '比较工具定义与集合变化，识别可优化的具体内容。'], ['L4 · 消息内容差异', '对比请求的消息内容；缺少会话关联时不判断历史被改写。'], ['L5 · JSON 写法差异', '对比内容相同、空格等写法不同的工具结果。']],
    token_content: [['T2 · 工具返回内容', '检查字段和条目，按业务所需内容提出保留方案。'], ['T3 · 重复内容', '查找同一请求内的重复内容，识别可引用复用或省略的副本。'], ['T4 · 历史工具结果', '检查较早结果的重复携带，按保留约定给出具体方案。']],
};
const descriptions: Record<string, string> = {
    L1: '前部频繁变化的内容，会提前打断相同前缀的复用。', L2: '相同工具的排列顺序不一致，可能影响公共前缀复用。', L3: '工具定义或集合存在变化，可按适用条件调整。',
    L4: '可比请求的消息内容不同；当前证据不认定这些请求属于同一次会话。', L5: '工具结果的 JSON 结构一致，但空格或写法不同。',
    T2: '工具返回内容可按业务所需范围调整，减少不必继续携带的字段或条目。', T3: '同一请求包含重复内容，可在引用可用或获准省略时调整副本。', T4: '较早的工具结果仍在继续携带，可按保留约定调整。',
};
export function reasonText(value: Obj): string {
    const codes = arr(value.reason_codes ?? []).map(str);
    if (codes.includes('RECIPE_BASIS_MISSING')) return '尚未配置这项修改适用的业务依据，暂未评估修改后的变化。';
    if (codes.some(x => /BUDGET|LIMIT/.test(x))) return '本次分析达到处理上限，这项方案尚未完成评估。';
    if (codes.some(x => /REFERENCE|PROTOCOL/.test(x))) return '尚未提供可用的内容引用协议，暂未评估。';
    if (codes.some(x => /GUARD|MISMATCH|CHANGED/.test(x))) return '内容与方案要求不一致，本次没有可用的修改后结果。';
    if (value.status === 'interrupted') return '评估中断，暂未产生完整结果。';
    if (value.status === 'failed') return '评估未成功，暂未产生修改后结果。';
    return '这项方案尚未完成评估，暂不能提供修改后的变化。';
}
export function cardFromRow(row: Item, kind: ResultKind, entry: Obj, direction: Direction): Card | null {
    verifyItem(kind, row, entry, direction);
    const r = row.data;
    if (kind === 'difference_group') {
        const rule = str(r.rule_id);
        return { id: row.id, kind, rule, tag: checks.low_hit.find(x => x[0]!.startsWith(rule))![0]!, title: rule === 'L4' ? '相同位置的消息出现内容差异' : '相同工具结果，JSON 的写法不一致', description: descriptions[rule]!, advice: '', conditions: [], synthetic: false, data: r, evaluation: null, metrics: null, affected: String(arr(r.member_requests).length), total: str(obj(entry.scope).request_count), limitation: r.members_complete === true ? '' : '仅统计已发现涉及的请求，不表示已穷尽全部差异。' };
    }
    const qualification = r.display_qualification;
    if (direction === 'low_hit' && qualification !== 'low_hit_optimization') return null;
    if (direction === 'token_content' && !['token_evaluated', 'token_advice'].includes(str(qualification))) return null;
    const recipe = obj(r.recipe), rule = str(recipe.primary_rule), impact = obj(r.impact), e = r.evaluation ? obj(r.evaluation) : null, metrics = r.metrics ? obj(r.metrics) : null;
    if (!checks[direction].some(x => x[0]!.startsWith(rule))) throw Error('UNSUPPORTED_ACTIVE_RULE');
    if (direction === 'low_hit') {
        const g = metrics?.gain_percentage_points ? obj(metrics.gain_percentage_points) : null;
        if (!e || !g || e.status !== 'available' || !['full', 'direct_full'].includes(str(e.stage)) || obj(e.coverage).complete !== true || impact.evaluation_complete !== true || BigInt(str(g.numerator)) <= BigInt(str(g.denominator))) throw Error('INVALID_LOW_HIT_QUALIFICATION');
    }
    if (qualification === 'token_evaluated' && (!e || e.status !== 'available' || impact.evaluation_complete !== true || !metrics)) throw Error('INVALID_TOKEN_QUALIFICATION');
    const basis = recipe.basis ? obj(recipe.basis) : null;
    const conditions = [...arr(recipe.conditions), ...arr(recipe.limitations), ...(basis ? [...arr(basis.assumptions), ...arr(basis.limitations)] : [])].map(str);
    return { id: row.id, kind, rule, title: str(recipe.title), tag: checks[direction].find(x => x[0]!.startsWith(rule))![0]!, description: descriptions[rule]!, advice: str(recipe.change_summary), conditions: [...new Set(conditions)], synthetic: basis !== null && obj(basis.authority).source_kind === 'synthetic_fixture', data: r, evaluation: e, metrics, affected: impact.modified_requests === null ? null : str(impact.modified_requests), total: str(impact.total_requests), limitation: metrics ? '' : reasonText(r) };
}
async function readPages(api: AnalysisClient, old: LoadedReport, signal?: AbortSignal) {
    const kinds: ResultKind[] = ['recommendation'];
    const results = await Promise.all(kinds.map(async kind => { const offset = old.offsets[kind]; return offset === null ? null : { kind, page: await resultPage(api, old.entry, kind, old.direction, offset, signal) }; }));
    const cards = [...old.cards], offsets = { ...old.offsets };
    for (const result of results) if (result) {
        if (result.page.availability !== old.summary.availability) throw Error('SUMMARY_PAGE_MISMATCH');
        offsets[result.kind] = result.page.next;
        for (const row of result.page.items) {
            const card = cardFromRow(row, result.kind, old.entry, old.direction);
            if (!card) continue;
            if (cards.some(x => x.id === card.id)) throw Error('DUPLICATE_RESULT');
            cards.push(card);
        }
    }
    return { ...old, cards, offsets, hasMore: Object.values(offsets).some(x => x !== null) };
}
const differenceId = (rule: string) => `difference-detector:${rule}`;
async function loadDifferenceCards(api: AnalysisClient, entry: Obj, s: Obj, signal?: AbortSignal): Promise<Card[]> {
    const groups = new Map<string, { first: Item; members: Set<string>; owners: Obj[]; complete: boolean }>();
    const ids = new Set<string>();
    let offset: string | null = '0';
    while (offset !== null) {
        const page = await resultPage(api, entry, 'difference_group', 'low_hit', offset, signal, 100);
        if (page.availability !== s.availability) throw Error('SUMMARY_PAGE_MISMATCH');
        for (const row of page.items) {
            if (ids.has(row.id)) throw Error('DUPLICATE_RESULT');
            ids.add(row.id);
            const rule = str(row.data.rule_id);
            const group = groups.get(rule) ?? { first: row, members: new Set<string>(), owners: [], complete: true };
            for (const member of arr(row.data.member_requests)) group.members.add(canonical(member));
            group.complete = group.complete && row.data.members_complete === true;
            if (group.owners.length < 3 && arr(row.data.example_refs).length) group.owners.push(row.data);
            groups.set(rule, group);
        }
        offset = page.next;
    }
    if (BigInt(ids.size) !== BigInt(str(s.difference_group_count))) throw Error('DIFFERENCE_COUNT_MISMATCH');
    return ['L4', 'L5'].flatMap(rule => {
        const group = groups.get(rule);
        if (!group) return [];
        if (BigInt(group.members.size) > BigInt(str(obj(entry.scope).request_count))) throw Error('DIFFERENCE_MEMBERS_MISMATCH');
        const card = cardFromRow(group.first, 'difference_group', entry, 'low_hit')!;
        return [{ ...card, id: differenceId(rule), affected: String(group.members.size), differenceGroups: group.owners,
            limitation: group.complete ? '' : '本项检查尚未完整完成，数量仅包含已发现涉及的请求。' }];
    });
}
export async function loadCardExamples(api: AnalysisClient, report: LoadedReport, card: Card, signal?: AbortSignal): Promise<Obj[]> {
    if (!card.differenceGroups) return arr(card.data.example_refs).length ? resultExamples(api, report.entry, card.kind, card.data, signal) : [];
    const rows = await Promise.all(card.differenceGroups.map(owner => resultExamples(api, report.entry, 'difference_group', owner, signal)));
    const selected: Obj[] = [], seen = new Set<string>();
    // Take one example from each selected group first. Swapping a pair does not create a new example.
    for (let index = 0; index < 3; index++) for (const group of rows) {
        const example = group[index];
        if (!example) continue;
        const key = canonical([example.before, example.comparison].filter(Boolean).map(x => canonical(obj(x).source)).sort());
        if (seen.has(key)) continue;
        seen.add(key); selected.push(example);
        if (selected.length === 3) return selected;
    }
    return selected;
}
export async function loadReport(api: AnalysisClient, entry: Obj, direction: Direction, signal?: AbortSignal): Promise<LoadedReport> {
    const [report, s, execution] = await Promise.all([api.report(entry, signal), summary(api, entry, signal), api.execution(entry, signal)]);
    const ruleCoverage = execution?.availability === 'computed' && direction === 'low_hit' ? (await api.all(str(entry.task_id), 'rule_coverage', signal)).map(x => x.data) : [];
    for (const row of ruleCoverage) {
        if (!arr(row.supported_rules).every(rule => ['L1', 'L2', 'L3', 'L4', 'L5'].includes(str(rule))) || row.applicable_pairs !== null || row.applicability_status !== 'not_separately_classified_by_detector' || !/^(0|[1-9]\d*)$/.test(str(row.candidate_comparisons))) throw Error('INVALID_RULE_COVERAGE');
    }
    const data: LoadedReport = { entry, report, summary: s, execution, ruleCoverage, direction, cards: [], offsets: { recommendation: '0', difference_group: null }, hasMore: false };
    if (s.availability === 'not_computed') return { ...data, cards: direction === 'low_hit' ? await loadDifferenceCards(api, entry, s, signal) : [], offsets: { recommendation: null, difference_group: null } };
    const [loaded, differences] = await Promise.all([readPages(api, data, signal), direction === 'low_hit' ? loadDifferenceCards(api, entry, s, signal) : Promise.resolve([])]);
    return { ...loaded, cards: [...loaded.cards, ...differences] };
}
export function moreReport(api: AnalysisClient, old: LoadedReport, signal?: AbortSignal) { return readPages(api, old, signal); }
export async function getCard(api: AnalysisClient, report: LoadedReport, id: string, signal?: AbortSignal): Promise<Card> {
    if (report.direction === 'low_hit' && /^difference-detector:L[45]$/.test(id)) {
        const cards = await loadDifferenceCards(api, report.entry, report.summary, signal);
        const card = cards.find(x => x.id === id);
        if (!card) throw Error('RESULT_NOT_FOUND');
        return card;
    }
    try {
        const r = await api.get(`${taskPath(str(report.entry.task_id))}/recommendations/${encodeURIComponent(id)}`, {}, signal);
        const card = cardFromRow({ id, data: r }, 'recommendation', report.entry, report.direction);
        if (!card) throw Error('RESULT_NOT_DISPLAYABLE');
        return card;
    } catch (e) { if (!(e instanceof ApiError && e.status === 404 && report.direction === 'low_hit')) throw e; }
    // Opaque difference IDs are resolved in the directory, never inferred from their spelling.
    let offset: string | null = '0';
    while (offset !== null) {
        const page = await resultPage(api, report.entry, 'difference_group', report.direction, offset, signal);
        const found = page.items.find(x => x.id === id);
        if (found) {
            const cards = report.cards.some(x => x.differenceGroups) ? report.cards : await loadDifferenceCards(api, report.entry, report.summary, signal);
            const card = cards.find(x => x.id === differenceId(str(found.data.rule_id)));
            if (!card) throw Error('RESULT_NOT_FOUND');
            return card;
        }
        offset = page.next;
    }
    throw Error('RESULT_NOT_FOUND');
}

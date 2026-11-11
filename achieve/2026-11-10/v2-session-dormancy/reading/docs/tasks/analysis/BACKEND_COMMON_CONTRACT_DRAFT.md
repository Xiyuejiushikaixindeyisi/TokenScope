> V2历史材料，仅供追溯，不是当前启动/修复/打包指令。[原始字节](../../../../originals/docs/tasks/analysis/BACKEND_COMMON_CONTRACT_DRAFT.md) · [当前会话登记](../../../../../../../memory/SESSIONS.md)。下文仅迁移导航链接，历史决定和结果未更新。

# 两类分析后端公共接入设计草案

版本analysis-common-draft-2，2026-10-31。产品v0.4及用户本轮修订为依据；A/B/C/D方向已确认，正式Schema尚未冻结/实现。维护身份与分工见[交接](../../../../../../../docs/tasks/analysis/BACKEND_SPLIT_HANDOFF.md)。不改监控S0、用户监控2.0.0或MA契约。新增语义见第9节及[修订细则](../../../../../../../docs/tasks/prefix-analysis/DESIGN_REVISION_20261031.md)，覆盖本文早期不一致描述。

## 1. 公共服务边界

拟新增src/tokenscope/analysis_common包，负责范围解析、原始请求读取、统一编码桥接、修改副本、离线评估、任务与结果存储。低命中实现放prefix_analysis；Token规则由Token线在本线设计决定目录并登记。不将monitoring已有analysis-runs更名或复用为业务诊断任务。

业务探测器只消费不可变RequestView和公共能力，返回Observation、FindingCandidate、ModificationCandidate；不写公共数据库，不调用源监控replay修改原结果，不自行加载另一套Tokenizer。两线需要的补充字段以本线接口需求文档对照本草案记录，后续明确签收后固定版本。

## 2. 输入对象

| 对象 | 字段与语义 |
| --- | --- |
| SourceSelection | source_kind=user_v2/base；对应user_run_id或base_run_id二选一；appid必需；window可选[start_ns,end_ns)，不提供则该appid原run完整有效范围；user_v2可带expected_index_revision |
| SourceIdentity | 实际base_run_id、user_run_id/common_name（可空）、model_id、源manifest摘要、runtime的asset/encoder/profile、settings、algorithm_version；模型配置只由源结果读取 |
| RequestKey | base_run_id + source_record_index；hash_id仅显示/溯源，不能去重主键 |
| RequestView | RequestKey、appid、time_ns、raw_json/raw_sha256、解析结构、原J/P/H/C/O、TokenSlice引用、light_evidence/effective_options；大原文/IDs通过lazy读取，非全量常驻内存 |
| AnalysisScope | 固定请求键集合摘要、按time_ns/index的顺序、数量、窗口与基线模式；同appid不同源run不隐式拼接 |
| EncodingContext | 经校验的原资产/settings/profile与公共EncodingBatchService；每请求原effective_options保留，修改不得改变这些选项 |

user_v2读取ready/empty收据与索引身份，解析base_run_id，核对服务/模型/manifest；base模式用于已发布V1结果，common_name未知不猜测。MA来源拒绝进入用户appid分析。source/run路径仅通过已知control记录解析，禁止客户端传任意路径。

源requests.sqlite3只读，联接request_records与encoded_requests，WHERE appid=?并按窗口过滤；读到的是原运行最终有效记录，不重新纳入原先拒绝的行。源manifest完整性校验可能读取整个封存文件，但不意味着对其他appid做业务分析/回放。原source行/原文/Token切片摘要记录到范围清单；读取失败不能静默跳过后继续称全范围。

## 3. 能力接口（逻辑签名，非已实现API）

| 能力 | 输入→输出 | 限制 |
| --- | --- | --- |
| resolve_scope | SourceSelection→SourceIdentity+AnalysisScope | 校验源发布/绑定、同appid范围；不重建监控索引 |
| iter_requests / read_ids | scope/key→RequestView/IDs | 只读分页/游标；切片校验；请求必须属于scope |
| inspect_input | key→结构、渲染视图/offset证据或unavailable | 只在显式分析任务内执行；详细编码ID校验；原字段映射可unknown |
| compare_inputs | 当前/前序key→原字段差异、LCP、独立原H | 对照不是缓存唯一来源；不宣称同session |
| encode_variants | 一批准确原结构修改→EncodedRequest或逐项失败 | 复用EncodingBatchService；不删IDs、不绕过控制Token |
| save_observations | 某探测器输出→不可变发现/证据引用 | 按实际请求覆盖去重；公开来源与现场证据分开 |
| create_plan | 明确候选及参数→不可变ModificationPlan | 包含准确目标、原值guard及协议检查；不执行评估 |
| evaluate_plan | scope+plan→BaselineCheck+前后逐请求/汇总结果 | 同窗口独立账本，复用make_strategy；组合另算 |

探测器运行输入额外含规则版本、明确预算、已核验共享事实、可选业务policy。返回status/reason、checked_keys、observations及候选；未完成与未检出不同。Token规则不依赖prefix_analysis类，可独立运行；L1/L2等低命中修改与Token内容修改遵守同一Plan结构。

## 4. 修改契约

Plan字段：id/version、source_scope_digest、finding_refs、action_class、target RequestKeys、ordered operations、guard摘要、参数及业务依据、组合组成、预期非目标不变量。

首期操作：去除明确字符串范围、替换指定值、工具数组固定排列、字段/条目投影、已有协议的引用替换、明确消息插入/移动。原结构路径使用JSON Pointer；字符串范围使用解码Unicode codepoint半开区间，单列原始JSON字节与渲染/Token坐标。多个操作按原值guard及次序应用，冲突返回错误，不隐式覆盖。

修改时保留对象插入顺序及非目标数组顺序。未修改请求复用原始raw_json；修改请求使用记录版本的确定性序列化，但不能sort_keys整个请求而顺带影响模板。J变化包含重新序列化的字节影响，清单单列；对解析结构做非目标子树一致性核对。

已知cch清理/同集合固定排序不重复要求业务确认。L1/L3普通动态时间/路径可生成准确删除假设并离线评估，不以业务无损确认作为实验前置；记录action_class及被删除内容，由业务决定上线。Token内容裁剪仍需明确保留/替换参数。是否业务无损与副本可编码分开；缺少明确变换时不伪造方案。

## 5. 离线评估

冻结scope与plan → 核验原settings/runtime及资产 → 按源编码身份重编码基线并核对J/P/IDs → 单项或组合生成副本并校验 → 原/新独立空PrefixLedger → 按同一scope顺序调用make_strategy(...).process(appid,ids) → 保存逐条P/H/C和汇总。

original_run_window模式核对原H/C；selected_window_recomputed模式只采用本窗口新H/C，不拿源完整run H/C作收益分母。资产与encoder身份必须匹配；旧算法版本不相容时阻断相应评估，不能仅因为当前代码能跑就覆盖历史口径。reuse监控make_strategy而不是调用会写源encoded_requests的replay(store,...)。

修改目标任何一条失败则方案blocked，无after/收益发布；非目标保持原样且参与整个窗口回放。允许分析报告partial，但成功评估必须完成所声明scope。无缓存模式仍可评P/C；P=0时R不可用。O只作源背景，不进入after。组合单独实际计算，不相加单项。

初版不做缓存快照恢复、跨run预热或增量重放；失败重试从明确范围重新执行，复用相同源身份而非部分账本。

## 6. 任务、存储和只读发布

提案目录：state_root/anomaly_analysis/control.sqlite3；jobs/<job_id>/attempt-<n>.partial；reports/<report_id>/与evaluations/<evaluation_id>/不可变结果。不得写源runs目录或复用原monitoring.control中的analysis_runs表。

control管理幂等submission_key+规范化意图、scope/plan、状态和发布引用；结果SQLite存逐请求事实/观察/变更引用，JSON摘要及manifest存身份/覆盖。大原文优先引用原seal，只保存必要副本/证据；manifest保护派生产物。模型正文不写普通错误日志。

状态：queued→running→ready/partial/empty/failed/interrupted；evaluate用独立任务，ready可零/负改善。worker持已有state_root/worker.lock，注册Dispatcher，不另起争抢编码资源的线程池。成功封存先完成文件/摘要与原子rename，再control事务发布；崩溃后只接受验证完整的已封存产物，否则interrupted。GET无恢复/补算。

恢复采用显式retry生成新attempt，旧证据/状态保留；同幂等键且相同意图返回原任务，不暗中重试。同键不同意图409。现有ModelEncoder固定进程RAYON预算，分析复用服务统一CPU预算；不同源profile的cpu_budget与进程配置冲突应给具体错误，不能每任务任意改环境。

## 7. HTTP边界提案

新前缀建议/diagnostics，与旧/analysis-runs和/monitoring/user-v2/evaluations分开。仅是待技术评审提案，尚无端点。

| 方法/路径 | 语义 |
| --- | --- |
| POST /diagnostics/runs | source selection、directions、规则/预算→202任务收据；不修改源监控 |
| GET /diagnostics/runs/{id} | 状态、覆盖、报告引用，不继续分析 |
| GET /diagnostics/reports/{id} | 两方向结果摘要、实际规则版本、基线身份 |
| GET /diagnostics/reports/{id}/findings | direction及分页；确定性排序、报告版本绑定 |
| GET /diagnostics/reports/{id}/evidence/{evidence_id} | 已保存片段与引用，限定属于本报告 |
| POST /diagnostics/plans | 基于报告候选的准确参数→不可变计划；拒绝任意源码/文件操作 |
| POST /diagnostics/evaluations | 计划id或明确组合计划→202评估任务 |
| GET /diagnostics/evaluations/{id} | 评估状态/结果、同窗口指标与限制 |
| POST /diagnostics/runs/{id}/retry、/evaluations/{id}/retry | 显式新attempt，源身份变化拒绝复用 |

沿用X-TokenScope-Instance-Id实例防错与no-store；它不是鉴权。整数采用现有十进制字符串wire约定，ratio与百分点单列；不把异常输入正文回显到错误。404未知/不属于scope，409身份/幂等/基线冲突，422不支持操作，503必要源/资产不可用；具体错误枚举随正式Schema固定。

## 8. 与Token线需要核对的项目

RequestView是否足以消费tool参数/返回与历史位置；T1结构度量的单位与方法；T2/T4保留policy表达；T3引用替换guard；同位置证据/修改去重键；修改失败语义；公共Plan操作是否覆盖本期四规则。由Token线记录本线需求后对照本草案收敛，不等待或要求其完成低命中逻辑。

未完成项：正式Schema/OpenAPI、worker执行时间/内存预算实测、源码实现与测试、两线契约签收。本文不宣称这些已经完成。

## 9. draft-2已纳入的公共语义

### 9.1 人工原因与阶段编排

POST runs显式携带reason_codes/reason_note、enable_low_hit、enable_token_content、evaluation_policy=screen_then_full。含low_hit时两个开关均true且先低命中（含两阶段评估）后Token；仅request_length/qps时false/true。冲突拒绝，不从监控阈值自动触发。全量监控是现场先行流程，不由本任务重启。32k/70%不是本服务默认告警阈值，QPS入口不代表已实现Loop诊断。

用户启动一次诊断可驱动已具体化L1–L3候选的pilot→full，不必逐次批准纯离线实验；没有准确参数的候选仍为待参数。POST plans/evaluations保留供显式参数方案及重新实验。方向级失败保留事实后可继续下一方向；共享源失配/中断则阻断后续。状态附direction_status及stage_status，避免把Token未开始显示为无问题。

### 9.2 六项类型细化及Token协议接纳

主会话已读取并接纳[TA-I0.2](../../../../../../../docs/tasks/length-analysis/INTERFACE_REQUIREMENTS.md)和[TA-C0.2](../length-analysis/COMMON_INTERFACE_ALIGNMENT.md)以下技术选择；本行是公共维护方接纳记录，不是已联调或代签Token线接受本轮新编排。

1. RequestView补raw_body_complete及capture_truncation=known_truncated/known_complete/unknown；前者表示存储正文完整读取，后者表示采集事实，不能相互推导。原H/C可空，齐全同口径才校验P=H+C。
2. participation含included/ignored/unknown、evidence_method与模板/选项身份；精确Token spans独立可空。一次对照无变化只记录本次无可观察影响，不单凭此标ignored。
3. 接纳location_id/unit_id/observation_id三层身份及TA-C0.2第4节材料；保存parent/overlap关系、多位置证据和同报告幂等冲突检查。T2/T4共用单元，rule_id不进入位置/内容单元身份。固定元数据编码样例仍待正式Schema。
4. TargetLocation分别保存source_pointer、embedded(format/parser_version/pointer)、text_range、原值及外层字符串guard。Token处理器严格解析一次内层，生成PreparedMutation受保护外层替换和内层操作manifest，公共层不复制内层解析器。同外层多个操作一次编译；数组删除按原位置编译最终数组，普通消息删除须符合已批约束。跨方向父子覆盖/移动冲突不自动重定位。静态注册token_content的describe/validate_selection/analyze_request/prepare_mutation调用面及版本化handlers；公共层保存纯fragment，不让插件持DB或注册独立worker。
5. EvaluationResult区分全评估scope和modified_subset的N/J/P/H/C/R；保存baseline_origin、stage、scope_digest、before/after、delta、manifest与覆盖。not_run没有零收益，blocked/failed没有after。原O仅作背景。
6. RunControl共享固定预算及停止信号，在请求边界和可控遍历/比较批次检查；不承诺中断第三方解析。分析中止保留实际覆盖，未完成评估scope不发布after；不因此新增取消HTTP API。

### 9.3 两阶段门槛与展示

低命中方案分别保存pilot/full scope、选择算法版本、计划和共同transformation_digest；小范围取连续记录序列，前后同空起点，成功后原语义变换应用目标appid全窗口。规则/参数变化需重新pilot。

R=ΣH/ΣP，delta_R_pp=100×(after.R−before.R)。未舍入结果严格>1pp且实验完整才pilot_high_confidence；该置信度只指小范围缓存改善。full阶段完整且同门槛才display_eligible=true。相等不通过，P=0不可判定。失败无after，零/负结果在后台保留。全窗口和修改子集分列，组合独立评估。门槛不用于Token报告；L4/L5完整JSON对比作为差异证据不受门槛限制。

需要记录gate_threshold_pp=1、gate_operator=gt、gate_passed、display_reason及confidence_basis。前端GET仅读已存结果，完整请求对比必须提供两条完整原文的身份/摘要及受报告范围约束的读取引用；端点名称在正式Schema阶段确定。不以preview冒充完整JSON。

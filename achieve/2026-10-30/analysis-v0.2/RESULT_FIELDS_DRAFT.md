# 首期分析结果与证据字段草案

版本：v0.2讨论稿，2026-10-30。配套[首期流程](PHASE1_PLAN.md)，供产品与后续后端/前端设计对齐，不是已冻结JSON Schema或已实现API。

字段名用于消除歧义。下表“整数”为逻辑类型，后续接口沿用项目精确整数传输约定；不在本稿另定序列化协议。缺值用null及原因，不用0代替；0是有效观测。所有数组可分页或引用已保存证据，UI无需一次加载完整原文/IDs。

## 1. 报告 Report

| 字段 | 类型 | 必需性与含义 |
| --- | --- | --- |
| `report_id`, `report_version` | 标识、版本 | 必需；独立于监控run。新分析/评估保留版本关系，不覆盖原结果 |
| `source_run_id`, `source_digest` | 标识、摘要 | 必需；绑定不可变源运行/来源身份 |
| `scope` | 对象 | 必需；appid、服务绑定/来源、编码model_id、记录/时间选择、原运行时间语义；缺服务绑定显式未知 |
| `measurement` | 对象 | 必需；encoder/asset/template/profile身份、有效选项、simulation_semantics、块/MTP/CP、cache开关与签名；不只保存模型展示名 |
| `analysis_identity` | 对象 | 必需；分析规则版本、探测器次序/版本、候选选择与预算；用于解释两次结果不同 |
| `created_at`, `published_at` | 时间 | 必需创建时间；未发布时后者为空；与数据时间分开，展示北京时间 |
| `status` | 枚举 | 拟采用queued/running/ready/partial/failed/empty；partial有可读结果及缺口，empty仅指无可分析输入 |
| `quality` | 对象 | 必需；原运行文件读入/有效/跳过、可归属范围、原因引用；不把文件级未知跳过摊到appid |
| `baseline_metrics` | 指标对象 | 必需；所选统计范围的N与J/P/H/C/O、R；说明H/C继承原回放历史；未支持值附原因 |
| `coverage` | 对象 | 必需；选定、已检查、深查、具备比较条件的当前请求数；缺失输入与未完成原因。区分对照引用条数 |
| `detector_runs` | 探测记录列表 | 必需；每个计划探测器均有状态，不把不适用/失败藏在空发现中 |
| `findings` / `finding_refs` | 发现列表/引用 | 必需，可为空；每个方向的未检出与输入不足由探测记录解释 |
| `evaluation_refs` | 评估引用列表 | 必需，可为空；没有评估时说明未建立方案/受阻等原因 |
| `limitations`, `retained_process_requirements` | 限制与保留项 | 必需；当前证据上限、Loop等缺口，能关联到受影响方向 |
| `previous_report_ref`, `trigger_signal_refs` | 引用 | 可选；上一报告或触发信号，仅说明来源，不代表自动消费已实现 |

指标对象使用完整语义：`request_count`、`json_tokens`、`prompt_tokens`、`ideal_cached_input_tokens`、`ideal_compute_input_tokens`、`completion_tokens`、`ideal_hit_rate`。可附P/C分位数及原监控引用，不把J/P/C已有分布误称为全部五类均有分布。

## 2. 探测记录 DetectorRun

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `detector_id`, `version`, `sequence` | 标识、版本、整数 | 哪个探测器，第几个执行；次序不代表原因优先级 |
| `input_baseline_ref` | 引用 | 读取哪个原始基线；串行探测器共用，不引用前一个的修改副本 |
| `status` | 枚举 | completed/not_applicable/insufficient_input/failed/not_run；completed可有零发现 |
| `candidate_count`, `checked_count`, `comparison_current_count` | 整数 | 候选、实际检查及有可比前序的当前请求数；无候选为0，未知不填0 |
| `selection` | 对象 | 全量/Top-N/抽样规则、参数、预算及确定性样本身份 |
| `finding_refs`, `reason`, `error_ref` | 引用、原因 | 关联发现；不适用/不足/失败必须有解释；错误不回显敏感正文 |

## 3. 发现 Finding

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `finding_id`, `detector_ref` | 标识、引用 | 固定报告内的问题与产生依据 |
| `directions`, `category` | 分类列表、类别 | low_hit/token_content，可同时适用；类别如dynamic_field/tool_order/large_tool_result |
| `title`, `observation`, `business_location` | 文本 | 事实标题、观察解释、中文位置；不由字段名直接推断根因 |
| `fact_status` | 枚举 | confirmed/candidate/insufficient_input；只对应卡片陈述的事实，不代替收益可信度 |
| `cause_hypothesis`, `cause_limits` | 文本/列表 | 候选原因、替代解释及尚未核实环节 |
| `observed_request_refs`, `observed_request_count` | 引用集合及整数 | 已核实呈现该输入现象的唯一记录；不是全部生产受影响数或工具执行数 |
| `comparison_current_count`, `comparison_scope` | 整数、说明 | 有更早比较对象的当前请求数及候选范围；对照引用可能包含额外更早请求，数量不直接相加 |
| `checked_scope_count`, `coverage_note` | 整数、说明 | 观察分母；抽样时写样本，不外推全量 |
| `metrics_ref`, `evidence_refs` | 引用 | 原监控上下文与支持证据；指标低值本身不作为原因证明 |
| `recommendation` | 对象 | 改什么、为什么、示意、条件、业务复核项与验证办法 |
| `modification_refs`, `evaluation_refs` | 引用列表 | 单项候选与各自结果；没有方案/评估可为空并解释原因 |
| `related_finding_refs`, `overlap_note` | 引用、说明 | 跨方向或相同请求的相关发现，不重复累加收益 |

`recommendation`至少包含`action`、`target`、`preconditions`、`before_example`、`after_example`、`business_review`、`validation_steps`。修改例子标原证据片段/假设示意，不能用示意文本回算原始指标。

## 4. 证据 Evidence

### 4.1 通用定位

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `evidence_id`, `kind` | 标识、枚举 | raw_field/raw_comparison/prompt_prefix/content_size/duplicate_span/cache_rule等 |
| `request_refs` | 引用列表 | 每项为source_run_id与source_record_index；hash_id只作辅助展示，appid和模型核验归属 |
| `source_identity` | 对象 | 原JSON/IDs/编码身份摘要；原始内容不回写，字段变化可追溯 |
| `locator` | 对象 | JSON Pointer、角色、工具名称等业务定位；不存在或不可靠时为空并解释 |
| `representation` | 枚举 | raw_json / decoded_field / rendered_prompt / prompt_ids；不混合不同空间的坐标 |
| `span` | 区间对象或空 | start、end、unit，统一零起始左闭右开；unit明确utf8_bytes、unicode_codepoints或token_indices；记录所属representation |
| `mapping_status`, `mapping_method` | 枚举、说明 | exact/partial/unknown及验证方法；只有证据支持该映射时才为exact |
| `snippet` | 对象 | 显示文本、是否裁切/脱敏、原范围引用；脱敏展示坐标不冒充原文坐标 |
| `measures` | 测量对象 | 字符/字节/Token等分别命名，来源和计算口径明确 |
| `claim_supported`, `limitations` | 文本/列表 | 该证据支持的具体事实与上限，例如只证明文本不同 |

原JSON字节、解码后字符串位置、模板后字节和Token位置是四类坐标，不直接互换。比如Pointer能定位`messages/3/content`，不意味着已找到它在模板后出现的位置。offset、字段Token贡献或块位置未知时为空，前端隐藏对应高亮。

### 4.2 前缀对照附加字段

`comparison`包含：

- `current_request_ref`, `reference_request_ref`及`basis`：reliable_sequence或structural_peer；前者需可靠关联证据。
- `temporal_relation`与`cache_history_eligible`：更早/同刻排序/更晚；只有前序可用于历史解释。后者表示对照资格，不表示证明为缓存来源。
- `candidate_scope`, `candidate_checked_count`：查找范围，是否全量；不能据有限候选声称全局最优。
- `raw_differences`：两个字段/值/顺序及各自定位。
- `prompt_comparison_status`：verified/unavailable/mismatch；verified需同编码身份及IDs依据。
- `longest_common_prefix_tokens`、`first_difference`：不同Token的索引等于LCP；一方为另一方完整前缀时是end_of_sequence，不虚构不同Token。
- `matched_blocks_before_mtp`、`baseline_hit_tokens`与`rule_note`：可读时引用原监控事件，分别解释块边界与退块；不将LCP当作H。
- `cache_origin_status`：首期固定为not_tracked，除非后续另有真实来源证据；对照样例不得称实际命中来源。

### 4.3 内容证据附加字段

`content`包含：消息角色/数量、工具身份、`characters`、`utf8_bytes`、重复片段的两处引用、重复范围与匹配方法。`prompt_token_contribution`仅在可靠归属时填写，并附方法及未归属项；独立字段tokenization、删除后ΔP都不能冒充精确原始贡献。父子容器和重复命中的重叠区间去重规则需记录。

## 5. 修改方案 Modification

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `modification_id`, `version`, `finding_refs` | 标识、版本、引用 | 一个可独立评估的具体假设 |
| `operation`, `selection_rule`, `parameters` | 操作、规则、参数 | move/remove/replace/stable_tool_order/trim等；写明匹配路径、值及保留范围，不只给自然语言建议 |
| `selected_request_refs`, `selection_digest` | 集合、摘要 | 实际选中目标；跨请求规则可展开追溯，不仅保存易变glob |
| `preconditions`, `applicability` | 条件、状态 | 工具身份、字段结构、业务依赖；可机械校验与业务待核实分别记录 |
| `business_validity` | 枚举 | requires_business_review / externally_verified；静态可编码不能设为已通过业务验证 |
| `change_manifest` | 变更清单引用 | 每记录原/修改JSON与IDs摘要、变更位置、前后片段；包含非目标序列化变化说明 |
| `selected_count`, `applied_count`, `not_applicable_count`, `failed_count` | 整数 | 实际操作覆盖；目标失败不能静默跳过后发布全方案收益 |
| `evaluation_refs`, `combination_of` | 引用列表 | 每项评估；组合方案明确引用组成项，收益必须独立重放 |

原始与修改内容保存在现场独立产物中，展示仅取所需片段。任何哈希/脱敏身份的对外回传都应服从现场规则；此字段草案不要求上传真实正文或Token IDs。

## 6. 离线评估 Evaluation

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `evaluation_id`, `modification_ref` | 标识、引用 | 对应哪个不可变方案 |
| `status`, `reason` | 枚举、说明 | not_run/queued/running/available/blocked/failed；预算不足、资产不符、校验失败分别说明 |
| `mode`, `baseline_verification` | 枚举、对象 | 首期mode为offline_input；保存基线IDs/P/H/C一致性检查及差异，不一致时收益不可用 |
| `replay_context` | 对象 | 全历史记录集合/摘要、原排序、appid隔离、空起点和配置身份；不只写“相同配置” |
| `metric_scope` | 对象 | kind为replay_scope/modified_requests/selected_time_slice，另存实际记录集合及数量；全范围与子集不混合 |
| `before`, `after` | 指标对象 | N、J/P/H/C、R；相同记录集合；after不含预测O |
| `delta` | 对象 | J/P/C减少量、H变化及R百分点变化；约定正负方向，允许负收益 |
| `modified_count`, `evaluated_count`, `coverage_note` | 整数、说明 | 实际作用与完整回放/统计覆盖；比较对象/分母明确，不混作任务进度 |
| `business_review`, `limitations` | 状态与说明 | 业务效果尚未验证、未来输出/步骤未预测、物理缓存/费用/性能未评估 |
| `artifact_refs`, `created_at`, `completed_at` | 引用、时间 | 原/修改摘要、保存结果与复核依据；页面读取这些结果 |

`delta`方向：`json_tokens_reduced=J前−J后`，`prompt_tokens_reduced=P前−P后`，`compute_input_tokens_reduced=C前−C后`，`cached_input_tokens_change=H后−H前`，`hit_rate_change_pp=100×(R后−R前)`。R零分母不可用，差也为空并附原因。R变化用百分点，不能展示成相对提升百分比。

`before`中的原运行全范围基线与重放校验结果保留对应引用；对统计子集须从同一完整重放中提取。输入裁剪的ΔP只是反事实变化，不命名为字段精确贡献。没有组合评估不生成总收益；阻断/失败不输出after指标，不能留下看似成功的节省数值。

## 7. 覆盖与状态的组合规则

- 探测成功但零发现：展示“已检查，未检出此类现象”，带检查数量。
- 发现事实成立但评估受阻：卡片仍显示事实和建议，评估栏显示具体阻断原因。
- 一个方向无可靠输入：该方向为部分可分析/输入不足，其他方向照常发布。
- 只有字节证据：保留内容卡片，Token贡献为空；只有原字段差异：保留观察，模板后影响待核实。
- 修改后P/H/C无改善或变差：评估仍可为available，明确结果；状态不等于“优化成功”。

尚待详细设计落实：字段分页/上限、存储引用、错误协议和API形式。当前仅有文档，没有新增数据表、端点或消费者。

# 首期结果与证据字段草案

> 2026-10-31最新用户修订已生效：手动指定appid及异常原因；低命中先执行L类两阶段评估再Token，长度/QPS仅Token；L1/L3允许动态字段删除候选实验；小范围及全范围提升严格>1个百分点；L4/L5完整请求对比、Token报告独立。以[当前修订](../prefix-analysis/DESIGN_REVISION_20261031.md)和[公共draft-2](BACKEND_COMMON_CONTRACT_DRAFT.md)覆盖下文不一致的v0.4历史条款。未编码。

> 当前分工：主会话继续低命中后端，Token异常后端已获准fork并启动；见[分线交接](BACKEND_SPLIT_HANDOFF.md)。下文“本轮未编码”为产品形成阶段事实；本次仅交接整理，尚未修改源码。逻辑字段尚非冻结API。

v0.4产品基线，2026-10-31已获用户审批。配套[总览](PRODUCT_PROPOSAL.md)、[流程](PHASE1_PLAN.md)及两份探测器规则。下列是逻辑字段，不冻结API/JSON Schema，不新增端点或数据表。缺值用null及原因，不以0代替未知。

## 1. 报告

| 字段 | 含义 |
| --- | --- |
| report_id/version、source_run_ref/digest | 报告与不可变来源，修改评估产生独立引用 |
| scope | appid、服务绑定或原模型身份、窗口、请求键集合/摘要、排序语义；不混其他appid |
| input_identity | 模型/Tokenizer/Template/配置与资产摘要，由后台读取，非业务修改项 |
| status、created_at、published_at | queued/running/ready/partial/failed/empty及时间，区分数据时间 |
| baseline_metrics、baseline_origin | 原运行或子窗口重算的N/J/P/H/C/R；源O单列，不混作修改后预测 |
| coverage_by_direction | 两方向分别记录selected/checked/eligible/comparable/matched/unfinished数量及原因 |
| detector_runs | L1–L5、T1–T4执行记录；内部配置/模板参与检查不是业务探测器 |
| findings、evaluation_refs | 分别可按low_hit/token_content读取，两个页签共享证据和方案 |
| limitations | 可读输入缺口、范围/采样、未执行项；Loop保留依赖可链接，不冒充已检查 |

coverage以请求键去重，规则之间可重叠；不能把每个探测器matched相加作为总影响请求。低命中无历史/无合格对照/候选歧义/未检查分别记录。

## 2. 探测记录与规则来源

| 字段 | 含义 |
| --- | --- |
| detector_id/version、direction | L1–L5或T1–T4；编号不是执行优先级 |
| status/reason | completed/not_applicable/insufficient_input/not_run/failed；completed可零发现 |
| input_baseline_ref、selection | 共用原始输入、全量/筛选/样本规则、预算及实际检查集合 |
| source_refs、evidence_kind | 公开依据URL/研究引用；官方实践、缺陷个案与本项目产品判据区分 |
| rule_parameters、policy_ref | 具体比较规则；若涉及预算/保留策略，必须记录值、单位、业务来源和版本 |
| checks、finding_refs | 判定条件逐项通过/不满足/未知及对应发现 |
| execution_sequence | 实际运行次序仅用于复核，不决定业务原因顺序 |

阈值无业务来源时为空；没有阈值仍可返回内容负担。公开来源不能作为“当前appid已命中规则”的证据。

## 3. 发现与业务判定

| 字段 | 含义 |
| --- | --- |
| finding_id、detector_refs、directions | 同一问题可由多规则支持、跨页签引用；不重复构造收益 |
| title、business_location、observed_fact | 业务标题、具体内容位置及观察事实 |
| fact_status | confirmed/candidate/insufficient_input，限定于陈述事实 |
| anomaly_condition、condition_status | 明确判据及met/not_met/unknown；如“字段动态进入前缀”或“超出业务列白名单” |
| conclusion_type | construction_issue/optimization_opportunity/policy_exceeded/needs_evidence |
| action_class | known_metadata_cleanup/stabilization/content_change/reference_replacement/advice_only |
| observed_request_refs/count、checked_scope_count | 当前请求去重集合和分母；对照锚点另计，非执行次数 |
| observations、aggregation_key | 每个当前请求/对照的事实、规则、位置；按位置/机制/工具版本归组 |
| evidence_refs、conflicting_evidence_refs | 代表证据与反例/其他解释，不只展示一个样例代替全组验证 |
| recommendation | 具体改什么、保留什么、依据与不能推断什么 |
| modification_refs、evaluation_refs | 可执行副本及实际评估；没有则附原因，不写预计节省 |
| related_findings、shared_evidence_refs | 同字段多规则/T2-T4交叉的去重与关联 |
| display_state | 首屏或折叠，仅影响展示，不影响探测/评估资格 |

不设置人工0.9等置信度。输入构造问题、优化机会与业务超限分别展示；业务预算不明时不能使用超限标签。

## 4. 证据

通用：evidence_id、source_request_ref、JSON Pointer、协议角色/工具身份、脱敏片段及原内容摘要、具体支持的主张、限制、source_ref。

低命中附加：

- current/reference请求与前序资格，basis为可靠关联或结构对照；可靠关联必须有来源。
- 原字段差异、结构相等性、IDs相等性分别保存；不能用J/P相同替代内容比较。
- 模板参与状态、映射方法及exact/partial/unknown；映射多义时保留候选位置，不画确定连线。
- LCP、first_difference或end_of_sequence；原H/C另列，不把LCP或差异位置当命中Token。
- reference_status为ok/no_history/no_clean_reference/ambiguous/not_inspected/error；没有对照不等于不可优化。
- 缓存实际来源默认未追踪，不能将比较请求标“真实命中来源”。

Token内容附加：

- 内容类型、字符/UTF-8字节/条目或行数、计量基准；tools结构展示大小附序列化方法。
- 模板参与状态；prompt_token_spans/contribution只有可靠映射才填写，附归属方法和未归属范围。
- duplicate_locations、match_method、重复载荷字节与区间去重；不等于可节约Token。
- policy_ref、observed_value、limit_value/unit；相同单位才能判断超限，未知为空。

原JSON字节、解码字符串位置、模板后字节、Token位置分开，不互相冒充。父子容器/重叠片段的内容度量取不重复范围。

## 5. 修改方案

| 字段 | 含义 |
| --- | --- |
| modification_id/version、finding_refs | 独立方案及来源，多个卡片可共用 |
| operation、paths、source_guards、parameters | 原结构字段remove/replace/move/order/trim等；准确原值条件、保留规则及目标位置 |
| action_class、business_basis | 已知元数据无损/稳定化/内容变化/引用替换；记录业务场景或契约，不只写“能编码” |
| selected_requests、selection_digest | 确切目标集合，可包含原先对照锚点；与观察影响数分开 |
| applied/not_applicable/failed_count | 应用覆盖；目标失败阻断该方案，合法不适用保留原样 |
| change_manifest | 每条请求前后字段片段、原/新原文与IDs摘要、非目标表示变化 |
| combination_of/order、conflict_checks | 组合组成、路径与操作顺序；冲突未解决不评估 |
| evaluation_refs、limitations | 保存结果引用；仅建议时明确缺少的具体副本条件 |

已知cch清理及同集合工具稳定排序无需反复请求业务等价确认。内容裁剪或需新工具协议的建议不得因此自动视为无损。

## 6. 评估

| 字段 | 含义 |
| --- | --- |
| evaluation_id、modification_ref、kind | single/combined，关联明确方案 |
| status/reason | not_run/queued/running/available/blocked/failed；available可为零或负改善 |
| mode | offline_input，不执行agent，不推断未来输出 |
| replay_context | 目标appid、服务、窗口、请求集合摘要、排序、initial_state=empty、资产/规则身份 |
| baseline_origin | original_run_window或selected_window_recomputed；不能混用H/C |
| baseline_verification | IDs/P核验；原运行窗口同时核对原H/C，子窗口与新建同范围基线比较 |
| metric_scope | replay_scope为默认；modified_requests为可选子集，二者不相加 |
| before/after | 同请求集合N/J/P/H/C/R；after无预测O |
| delta | P/C/J为前−后，H为后−前，R为后−前百分点；允许负值 |
| coverage、artifact_refs | 修改数、评估数、摘要/结果/变更引用，不能只写成功 |
| business_limits | 内容改变、任务效果未验证及真实运行未评估等与方案相关的限制 |

原监控指标可作背景，但子窗口收益只基于本窗口重算。评估失败/受阻不输出after或节省数值；不完整评估不发布全窗口收益。单项和不生成组合收益，组合必须有实际评估记录。

## 7. 展示状态约定

未检出、不适用、输入不足、未完成、失败分开；“未检出”只覆盖实际检查范围。字段事实已确认但评估受阻，卡片仍保留。主界面两个页签各自显示结果状态；Top-K只是折叠，不影响规则是否执行。

字段分页、存储与接口传输留给后续详细设计，仍沿用项目精确计数约定。本稿没有新增后端能力。

# Token只读前端接入回执 FE-R-T1

> 2026-10-31最新批准范围：[TA-S1](SCOPE_REVISION_T234.md)移除Token T1，保留T2–T4编号；工具定义归低命中现有一致性/漂移职责，不增长度精简。当前新设计/计划/推荐/视觉验收仅T2–T4；旧源码及TA000–006历史仍含T1，不冒称已删除。当前实施计划见[BATCH_PLAN_ARTA](BATCH_PLAN_ARTA.md)，三卡样例见[AR-T3](FRONTEND_REWORK_EXAMPLES_ART3.json)。本轮仅文档同步，暂不编码打包部署。

> 2026-10-31最新决定（AR-02/AR-T2）：已核实前端会话用户原始指令，Token后台自动建议与量化收益前移到本轮，覆盖之前留V3/暂停安排；自进化Agent及实际Agent修改不前移。[AR-T2补充设计回执](FRONTEND_REWORK_RECEIPT_ART2.md)提供归并/计数/字段/局部证据、4类视觉样例及ARTA000–004批次。当前回执与草案已形成，公共契约/业务依据尚待落定，新后端未编码；不改正式前端，不打包部署。

> 2026-10-31最新用户决定：后台自动修改建议与预期收益方向保留，推迟到V3与自进化Agent一起实现；当前停止该方向进一步设计和开发。TA-AE0.1仅作未来讨论输入，不是已审批设计或实施计划，不作为当前前端接入/验收的新增阻碍；现有Token只读能力边界保持。重启以用户后续明确安排为准，不自动创建或启动自进化Agent会话。

> 后续用户纠偏：后台必须负责自动修改建议与预期收益，不能以本回执的现有缺口替代产品目标。参见[TA-AE0.1补充方案](AUTOMATIC_RECOMMENDATION_EVALUATION.md)。下文描述现有实现；前端只读原则保持，后端补充尚未编码。

2026-10-31。提供方：Token异常后端 `01a18fcd-0464-7cf1-b435-4f394bd33e66`，本轮环境 THREAD_ID/SESSION_ID 一致核实；接收方：异常分析前端 `01a19111-344a-75c1-84e0-14db8be08f4f`。当前仅文档、构造样例、静态身份核对，未改业务源码、启动服务/诊断任务、重跑业务测试、打包部署或Git收口。

已接收 [DEVELOPMENT_READINESS](../viewer/analysis/DEVELOPMENT_READINESS.md) 与 [INTERACTION_DRAFT I-0.5](../viewer/analysis/INTERACTION_DRAFT.md) 最新范围：UI-03只读问题/证据、建议及后端已有收益；无参数/授权/评估表单，无自动POST，通知后GET、打开/重连对齐目录，不轮询，partial保留旧默认。此决定覆盖本线旧 [FRONTEND_HANDOFF](FRONTEND_HANDOFF.md) 第2/3/6节中的前端提交操作，以及旧“无目录/时间”的能力描述；旧POST接口仍存在，但不属于本期前端。

**结论：Token只读内容映射已明确，可以据此制定前端开发方案。无需用户先提供policy、业务授权或修改参数才能展示事实与建议。初始Token分析没有自动量化修改收益；任意历史评估也没有从发现直接反查的完整目录。不能承诺每张卡片有预期提升。** 若产品要求所有卡片自动附带量化收益，属于需要另行决定的后台工作流与公共关联能力，不是补一个前端字段，也不是本次编码授权。

## 一、字段映射与只读能力

### 1. 共用GET与精确关联

统一前缀 `/diagnostics`。主capabilities与独立discovery capabilities确认同一实例；其余GET带 `x-tokenscope-service-instance`。目录/通知按公共 [NOTIFICATION_HANDOFF](../prefix-analysis/NOTIFICATION_HANDOFF.md)，不再将discovery-1当缺失。

| GET | 响应字段/用途 |
| --- | --- |
| `/tasks/{task}/report` | `scope/scope_id/runtime_options/stages/reason_codes`；实际policy输入在 `runtime_options.token_selection.policies_json`（JSON文本），规则选择与budget同处；不是业务默认阈值 |
| `/tasks/{task}/items/fragment?offset=0&limit=100` | `items[i].id` 是fragment ID；`items[i].data` 是下面的F，`offset`；无total/has_more。Token不走低命中finding列表 |
| `/tasks/{task}/items/fragment_index/{fragment}` | `location_ids/unit_ids/observation_ids`，分别与F的三个数组同序；这些ID由服务返回，前端不重算hash |
| `/tasks/{task}/requests/{fragment}` | `request_key/raw_body/raw_sha256/raw_body_complete/capture_truncation/scope_id`，完整单请求；64KiB preview不可替代 |
| `/tasks/{evalTask}/items/evaluation`、`/items/plan`、`/items/authorization` | 只有已知评估任务且已有成员时可读；列表的`items[].data`为对象，单项`/{key}`直接返回对象 |
| `/tasks/{evalTask}/evaluations/{evaluation_id}/rows` | available且有行manifest时的逐请求证据；`items[].source_record_index/evidence`，不属于发现到子任务的搜索接口 |

F公共字段：`request_key/raw_sha256/plugin_id/plugin_version/locations/units/observations/finding_candidates/modification_candidates/rule_results/coverage/reason_codes`。F本身**没有scope_id**，由所属report.scope_id及requests响应关联，不能从其他报告借scope。

Finding路径为 `F.finding_candidates[].{finding_id,rule_ids,observation_ids,title,category,advice}`。没有独立业务 `description/example/expected_gain` 字段。前端可按rule/predicate提供经设计确认的固定中文解释，但须与后端原生title/advice区分，不把固定文案称为后端结论。例子来自实际证据原文/路径；下文构造例子仅供验收。

观察路径为 `F.observations[].{rule_id,rule_version,unit_ids,predicate,condition,method,policy_digest,details_json}`；D表示解析该观察的details_json后对象。`details_json`内部数字是业务JSON数字，不套外层元数据十进制字符串转换。`content_inventory/met`只是观察到内容，不是异常成立。`rule_results[].condition=unknown`与观察事实met可同时成立。

关联：Finding.observation_ids → index.observation_ids对应位置 → Observation.unit_ids → index.unit_ids → Unit.location_id → index.location_ids → Location。没有Finding时从Observation开始。Unit的`measurement_unit/measured_value`、`participation`与`parent_unit_id/container_unit_id/overlap_relation`独立解释；数值不是Token贡献。

### 2. T1–T4逐项映射

| 规则 | 原生事实/分类与量度 | 建议、业务文案与原文例子 | 无业务配置时 |
| --- | --- | --- | --- |
| T1 工具定义 | `predicate=content_inventory`的D：`measures/tool_name/tool_identity/identity_status/participation/capture_truncation/token_contribution/components`；components含unit_id/measures/source_pointer。`identical_descriptions`另有occurrences/deletion_safe。显式limit观察D有actual/limit/unit/operator；满足时Finding.category=policy_exceeded | 固定标题可用“工具定义内容”；原生机会Finding.title为“内容修改待业务确认”，advice说明不能判无用；候选handler=replace_tool_description、missing_parameters说明仍需替换文本/依据。实际description与parameters从Location读取，不造“未使用工具”结论 | 有库存/重复描述事实；符合内容结构时有optimization_opportunity与待确认候选。无policy不判超限，不证明模型Token贡献或安全删工具，无收益 |
| T2 工具返回 | 同一content_inventory字段（无components）；limit同上；field_allowlist的D=`extra_fields[{row,fields}],field_level`；身份/单位不足为unknown并给reason | 固定标题可用“工具返回内容”；原生机会或policy_exceeded。候选handler=select_result_lines/project_result_fields/select_result_items；按missing_parameters只说明可选保留思路，不呈现表单或自动裁剪；原文可展示实际第1行多出debug | 无policy仍有完整内容事实，符合类型时有待确认候选；65536字节只是64KiB，不是65536Token，也不证明超限或无用 |
| T3 重复载荷 | `predicate=exact_payload_repetition`，D=`occurrences/comparison/repeated_utf8_bytes/occurrence_measures/scope/aggregation/saved_tokens/deletion_safe/execution_count`；后3项为null。comparison为exact_text_bytes或typed_structure_number_lexemes，后者重复字节可null | 当前规则**没有Finding/默认修改候选**。固定标题“同一请求载荷重复”，固定建议“确认业务用途后考虑引用复用或减少额外复制”，必须标为待业务确认。一个请求中tool结果、arguments内/document、普通消息三处“中文”，12重复字节不等于12Token | 无授权也显示Observation及证据；不默认生成删除方案/授权，不推断Loop、调用次数或执行失败，无收益 |
| T4 历史工具结果 | `content_inventory`的D另含later_message_count；显式`retain_last`观察D=`keep_last/retention_unit/scope_count/index/reason`，condition=met时为policy_exceeded；matched scope和容器/文本块由策略决定 | 固定标题“历史工具结果内容”；有策略时原生Finding及apply_retention_replacements候选，仍缺replacement_json/business_basis_ref；原文按结果容器/parts定位。无策略可固定说明“核对历史结果保留必要性”，不能说已经过期 | 无keep_last只有库存和后续消息数，没有T4保留候选；keep_last=0是显式策略而非缺省。仅有policy仍不自动替换或评估，无收益 |

依据为当前 [rules.py](../../../src/tokenscope/token_content/rules.py) 的 `run_inventory_rule`、[candidates.py](../../../src/tokenscope/token_content/candidates.py) 的 `pending_candidates`、[duplicates.py](../../../src/tokenscope/token_content/duplicates.py) 的 `run_duplicates`；不是由UI原型反推实现。实际七类handler与必填语义见 [IMPLEMENTED_API](IMPLEMENTED_API.md)。既有advice里“提供参数后评估”是后端能力说明，前端可以只读显示或配固定释义，不应因此恢复已撤回表单。

### 3. 定位与去重

Location=`source_pointer + embedded(format/parser_version/pointer)`；embedded=null表示外层，embedded.pointer=""表示字符串中的JSON根，二者不可混同。先定位外层，再解析该字符串一层；无raw offset时展示路径和上下文，禁止用全文首次substring伪造准确高亮。保留原文数字字面量（如9007199254740993），不通过JS JSON.stringify重写证据；按文本安全渲染。

T2/T4复用相同unit，展示两种规则解释不代表两份内容。T1父定义和description/parameters子项、T4容器与parts、T3父子重叠均按引用关系展示，不能相加成“总浪费”。RequestKey=(base_run_id,source_record_index)只在当前报告scope内统计请求并集，不按hash_id去重；跨报告不能合并后声称全范围统计。分页未读全不提供全appid排行/统计；不在前端重新探测重复。

### 4. 量化收益及可选配置边界

初始Token阶段调用插件后仅保存fragment/index；不会prepare_mutation或evaluate_plan。即使提供policy并产生策略违反或候选，也**不自动有Plan、after或收益**。同一分析任务可能含低命中评估，它们不能转贴为Token发现收益。历史消费测试 `test_real_saved_candidates_explicit_zero_negative_and_missing_parameters` 明确断言初始Token-only任务evaluation列表为空。

已有显式Token/combined评估可读取 `EvaluationResult.before/after/modified_before/modified_after` 与派生 `gain_percentage_points/compute_tokens_delta/gate_passed/display_eligible`。P/H/C在同scope比较，P=H+C；Token/combined的gate=null、display_eligible=false不隐藏结果。P10000→8000、H8000→5000、C2000→3000，应展示输入减少2000、计算增加1000、理想命中率下降17.5pp；不笼统显示“优化成功”。零收益保留；blocked/failed/not_run/interrupted无after，不补0。prepare受阻可只有report.reason_codes与stages=[]，没有evaluation。

若未来希望后台自动形成收益，需要另行确定策略来源/版本及作用范围、具体保留或替换参数、业务依据、T3引用协议/真实地址或删除授权、提交者及触发/预算，再由后端评估可实现方案；不把这些默认为本期新增配置。当前只读方案**没有用户必须先填写的policy/授权/参数**。缺收益显示“未提供量化评估”，缺策略显示“未提供业务策略”，不是让用户完成报告的交互。

### 5. 发现到既有评估：真实链路与缺口

**不存在发现→全部既有评估的反向索引，也没有按parent_task_id查询评估子任务列表。** discovery catalog只列已发布analysis，排除评估子任务。初次打开拿到诊断目录，并不意味着能发现全部历史Token收益；不能扫本机文件、猜task ID或把事件游标从零回放当未约定的历史评估目录。

若已有可信evalTask ID（调用方交接、已接收终态事件等），可GET discovery/tasks/{evalTask}/terminal读取parent_task_id、plan_refs、scope；再读该任务report/items/evaluation → evaluation.plan_id → items/plan/{plan_id}。普通Token Plan.finding_refs可对应父fragment里的finding_id，operations[].target.location给RequestKey/raw_sha及路径；据此读取父任务fragment/index/全文。它不是candidate_id反向索引，不能保证从某张卡片知道所有子任务。

T3的Plan.finding_refs可能为空，因为原观察没有Finding。已存authorization成员的 `input.observation_id/selected_unit_id/handler_id/handler_version/parameters_json/business_basis_ref` 和 `candidate.locations` 可回溯父fragment的Observation/index；input不额外提供fragment_id，需用候选Location.request_key.source_record_index与父task关联并复核rawsha。准备失败且无plan时不能假定可用以上Plan链。组合使用terminal.plan_refs（task_id/plan_id）及report.combination_refs回到各来源Plan，不强造单父任务。

因此，只读前端可以设计“有可信关联的既存收益才展示，否则未提供”；若验收要求自动发现**任意历史**评估收益，该项是公共发现/关联缺口，须在开发计划冻结前由产品/公共维护方确定范围。本线不静默扩展接口、不代替公共方承诺完成。

## 二、当前版本与文件身份

本轮 [FRONTEND_READONLY_IDENTITY.json](FRONTEND_READONLY_IDENTITY.json) 是静态工作树快照，不是release或远端部署身份。列出28个Token私有源码/测试/资源文件摘要、TA006逐项对比和三个公共manifest核对。

| 身份 | 当前值/验证边界 |
| --- | --- |
| plugin/rules | token-content-1；T1/T2/T3/T4均@1 |
| parser/measurement/policy | json-exact-1 / content-measures-1 / token-policy-1；policy_schema_version来自plugin.describe，具体业务policy有policy_id/revision/source及digest |
| handler/authorization | 七个handler均@1，名称见IMPLEMENTED_API；token-authorization-1 |
| 公共消费 | analysis-common-1.0、diagnostics-http-1、diagnostics-runtime-1、diagnostics-report-1；新增独立diagnostics-discovery-1无需新增插件方法 |
| 当前静态核对 | common manifest 5项、HTTP 3项、discovery 5项全部匹配；不等于运行时capabilities或消费者回归通过 |
| TA006历史差异 | 原43项中40项相同；公共evaluation.py、service.py、storage.py共3项变化，旧摘要保留。本线Token私有源码/测试与旧清单内对应项未变；不能把43项称全部仍一致 |
| 资源 | env/encoding-assets.lock.json摘要与RESOURCE_PROFILE.md列入快照；TA006 BENCHMARK/MACHINE为历史合成测量，不外推新版本SLA |

历史证据：[TA006 RESULT](batches/TA006/RESULT.md) 112项（103 unit+9 integration）及真实三模型固定资产/合成请求消费；不是生产trace或本轮重测。新discovery的199联合/7专用/300兼容是公共提供方记录，见其FE-N1；本线仅静态检查新增机制和旧GET契约保持，不代签公共新版本运行时通过。本轮未运行pytest、编码器、API服务或回放。

## 三、可消费关联样例与验证

[FRONTEND_READONLY_EXAMPLES.json](FRONTEND_READONLY_EXAMPLES.json) 提供4份**手工构造且经当前模型校验**的完整序列化fragment + 同序fragment_index + 完整raw_body响应；示例封套不是新API，task/scope/model身份全为fixture，非真实发布任务，不能用于在线执行。只选择对应规则与代表性证据，未宣称等于插件对原文的全量提取结果。前端消费服务返回ID，本轮样例制作使用公共模型的ID属性生成位置/单元/观察关联，不要求前端实现hash。

| JSON位置 | 覆盖与消费方式 |
| --- | --- |
| examples[0] / t2-64k-no-policy | 65536个ASCII字节完整原文，participation unknown，无policy；有待确认机会/候选，无评估。原文字面整数9007199254740993保留 |
| examples[1] / t3-three-positions-no-authorization | 一份原文三处“中文”；外层arguments字符串、内层根空pointer及/document均有位置/父子引用；重复字节12，Finding/candidate为空，无授权 |
| examples[2] / t4-missing-keep-last | 两个结果容器库存，NO_APPLICABLE_POLICY，无保留候选 |
| examples[3] / t4-explicit-zero | 明确构造policy keep_last=0，两个容器均满足策略条件，仍缺替换内容/业务依据；不把0作为未填 |
| evaluations[0..2] | 完整Plan与Evaluation序列化对象，分别零收益、P降C升、blocked无after；parent_task_id连接examples[0]，plan.finding_refs关联其Finding |
| prepare_blocked | 明确标注report字段片段：partial/stages=[]/BUSINESS_BASIS_REQUIRED，无evaluation；不是完整report响应 |

收益数值是**独立展示情境**，不是附件64KiB原文的实测编码结果。Plan guard特意为不可执行fixture摘要，不冒充已实际应用的修改；没有伪造rows文件或能访问的服务URL。完整report/runtime_options/discovery响应形状继续引用 [HTTP契约](../../contracts/diagnostics-http-1/README.md)、[discovery样例](../../contracts/diagnostics-discovery-1/examples.json)；本文件不重造一套报告/目录契约。

本轮实际验证：4个fragment经AnalysisFragment构造及from_wire往返、引用完整性检查；3个EvaluationResult模型构造与evaluation_view序列化；原文摘要、index数组对应、Plan/父task关联及数字方向另做文档检查。未执行探测器或实际分析任务。具体测试依据而非本轮执行：

- tests/unit/token_content/test_rules.py：test_no_policy_is_facts_not_anomaly_and_shared_units、test_retention_counts_containers_not_text_parts（含K=0）、test_field_allowlist_requires_exact_level_and_reports_rows。
- tests/unit/token_content/test_duplicates_plugin.py：test_three_payloads_count_once_and_no_execution_claim、test_structural_key_order_numeric_types_and_overlap。
- tests/integration/token_content/test_task_service.py：test_real_saved_candidates_explicit_zero_negative_and_missing_parameters、test_low_hit_precedes_token_original_scope_and_queries_are_readonly。
- tests/integration/token_content/test_authorization_http.py：test_full_body_authorization_and_combination_real_http；test_real_handlers.py：test_all_handlers_real_encoding_and_token_replay。历史真实服务/编码使用合成fixture，不是现场业务数据。

## 四、返回用户监控的范围身份

Token没有独立目录、binding或监控路由。继承公共report.scope：`appid/window/request_count/request_keys_digest/baseline_origin` 与 `source.base_run_id/user_run_id/common_name/model_id/manifest_sha256/asset_identity/encoder_identity/profile_json/settings_json/algorithm_version`。fragment.request_key定位底层base记录；不能仅用base_run_id忽略user_v2来源/时间窗/配置。源与模型身份在同一scope固定，Token评估没有另选模型配置。

返回监控用公共discovery binding/source身份及前端既有监控路由映射，公共方另行确认。common_name=null时不能推断物理模型服务；历史源不可用时说明限制，不跳到另一个服务。返回“当前监控”是导航，不证明当前监控与历史报告同窗口/资产/请求范围或Agent已完成修改，不作前后因果对比。

Token特有边界只有：fragment没有自带scope_id、同一RequestKey可出现在不同窗口/任务、T2/T4共享unit与父子重叠。用所属report/requests响应绑定即可，无新增Token专用监控协议缺口；跨scope合并、同单位重复计量、将不同编码身份收益相加均禁止。

## 接收结论与后续分界

| 项目 | 结论 | 对开发方案的影响 |
| --- | --- | --- |
| T1–T4只读事实/建议/证据映射 | 已明确 | 可据本回执制定组件与验收，不需用户补policy/授权/参数 |
| 初始Token量化收益 | 已明确：当前不自动产生 | 方案必须允许“未提供量化评估”，不能把零值当缺值或承诺每卡必有收益 |
| 所有历史评估反向发现 | 存在缺口 | 若要求自动展示任意旧收益，需要用户/公共方决定补关联范围；只展示可信既有引用时不阻碍基础只读方案 |
| 后台自动收益工作流 | 需要用户决定（仅在提升要求时） | 现只读范围无需新增后台配置；不能因文案“预期收益”擅自默认授权/新增调度 |
| Token身份与冻结接口 | 已明确，13项manifest静态匹配，TA006有3项公共变更 | 当前方案可绑定本快照及公共方最新回执；新公共运行时兼容仍须后续联合验证 |
| 构造关联样例 | 已提供并静态校验 | 足够编写接入/边界验收方案，不代表真实浏览器/HTTP/现场通过 |
| 监控范围身份 | Token侧已明确；公共binding/监控路由由公共回执确认 | 不另建协议；null服务与源不可用需前端回退方案 |
| 实际capabilities/SSE/目录/证据与既存收益联调 | 后续联合验证 | 本轮不启动服务，不填写未执行结果，不阻碍先写开发方案 |

本回执不是前端正式开发、服务部署、打包或Git收口批准，也不代签前端接收。参数错配继续独立研究。

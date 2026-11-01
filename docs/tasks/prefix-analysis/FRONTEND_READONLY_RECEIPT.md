# FE-R-L1 只读前端接入回传

2026-10-31。实际 CODEX_THREAD_ID / CODEX_SESSION_ID 均为 `01a18be2-7112-7aa2-919b-5137d1f1b1ad`，与 SESSIONS 低命中/公共方登记一致。已读前端 DEVELOPMENT_READINESS、INTERACTION_DRAFT I-0.5；以用户已认可 UI-03 只读范围为准。本轮仅核对、制作静态文档样例与摘要；未改业务源码、未运行分析服务/真实任务、未打包部署或Git收口，不修改前端或Token私有文件，不发送跨会话消息。

## ① 字段映射与只读能力

所有以下GET（capabilities除外）带 `x-tokenscope-service-instance`。基本路径记为 `B=/diagnostics/tasks/{task_id}`。目录和SSE沿用已实现[discovery-1交接](NOTIFICATION_HANDOFF.md)，不是新增缺口。列表 `B/items/{kind}` 返回 `{items:[{id,data}],offset}`，单项 `B/items/{kind}/{id}` 直接返回data。分页无total/has_more，满页继续；原文/Plan不是轻量持久缓存候选。

### L1–L5逐项映射

下表 F 表示 `GET B/items/finding` 的 `items[i].data`；完整请求 C 表示 `GET B/comparisons/{F.finding_id}`。这些规则没有后端独立 `title`、`description`、`examples`、`affected_request_count` 字段。前端可根据固定rule_id显示以下**解释性文案**，但不能冒充源字段或扩展诊断断言。建议优先直接用F.advice；F.source_pointer是主要位置，不能替代comparison的前后差异指针。

| 规则 | 可固定解释的标题/描述 | 已有建议/例子/证据原字段 | 已量化收益关联与可空条件 |
| --- | --- | --- | --- |
| L1 | 动态前缀内容；说明“可比请求中已定位动态片段变化”，不能写任意动态字段都无用 | F.advice；F.recipe_json（已识别时间/路径/known billing cch删除假设）；F.comparison、C.left_raw_body/right_raw_body；F.evidence_status=source_change_and_input_difference | 经同finding_ids的experiment→evaluation/plan追溯；有recipe仍可能预算未执行、pilot不足/不过门槛，不能承诺都有收益。已知cch信息保持标签以Plan.action_class为依据，其它按假设修改表达 |
| L2 | 工具顺序不稳定；完整定义集合相同且仅顺序变化 | F.advice固定排列建议；F.recipe_json.kind=sort_tools；C两条完整JSON，difference_pointers通常含/tools；evidence_status=source_order_and_input_difference | 自动pilot/full可产出已有收益；Plan.action_class=stabilization，不能据此把所有工具定义变化当无损排序 |
| L3 | 工具定义/集合变化；有动态片段时明确“工具内容中的动态片段” | F.advice；F.recipe_json可空，动态片段可删除副本评估；集合增删仅事实；C全文及前后difference_pointers（数组位置不同可有两个指针） | 只有可编译recipe才自动评估。recipe=null无量化收益是合法能力边界，不以最多出现定义替换其它版本，不称合法版本变化为错误 |
| L4 | 消息内容差异（关联待确认）；不能写同会话历史污染/Loop已证实 | F.advice；recipe_json=null；evidence_status=needs_association；C全文及comparison.association_ref通常null；正常后缀追加已排除 | 当前无自动收益；独立事实区展示，无>1pp门槛，不要求用户补参数或在前端发评估 |
| L5 | 工具结果JSON表示差异；不能推断可删业务内容 | F.advice；recipe_json=null；evidence_status=source_change_and_input_difference；C全文，保留内嵌字符串、数值词法/数组顺序 | 当前无自动收益；独立证据区展示，无>1pp门槛，不把字符差异自行换算Token节省 |

F共同字段还有rule_version、finding_id、comparison.left/right（base_run_id/source_record_index）、left_raw_sha256/right_raw_sha256、difference_pointers、association_ref、lcp_tokens。lcp_tokens允许null且不是引擎缓存命中边界。C.raw_body_complete仅表示保存全文完整，不证明上游未截断；该端点没有capture_truncation，不补造。JSON必须能查看左右完整请求，片段高亮只能作为导航；保留原始字符串，避免JS重新序列化损失大整数/空白证据。

### 结果关联、门槛和数量

1. `GET /diagnostics/discovery/catalog` 的defaults按binding_id+direction给task_id，items内相同task给scope_id、scope、report_digest、完成时间。`GET B/report`取得该task的scope、stages、runtime_options等。目录sequence决定发布顺序，不能用读取时间重排默认。
2. F.finding_id → `GET B/items/experiment` 中data.finding_ids。一个recipe可归并多个观察，只保留代表性finding参与实验；**不能仅按rule_id把一次收益贴到该规则所有finding**。没有关联实验只说明没有该项已存实验，不等于收益为0。
3. experiment.pilot/full是核心EvaluationResult；独立 `GET B/items/evaluation` /optimization 的data还包含四个派生字段。用evaluation_id匹配；不要假设嵌套pilot/full也有gain_percentage_points等派生字段。experiment未执行分支可能只有status/not_run、reason、finding_ids，完整对象可能有reason_codes、pilot_scope、confidence_basis。
4. evaluation.plan_id → `GET B/items/plan/{plan_id}` → plan.finding_refs → F → `GET B/comparisons/{finding_id}`。Plan.operations记录变换、目标RequestKey/原文摘要/value_guard、replacement_json等。`recipe_json`是后端变换描述，不是业务标题，也不是客户端可执行脚本。
5. 初始analysis的L1/L2/可变换L3按预算自动探测→连续pilot→完整full；完整pilot精确ΔR>1pp才自动full。完整full/direct_full的display_eligible=true才有优化卡片；恰1pp为false。pilot未full不能展示全范围预期收益；其范围只属于experiment.pilot_scope。高置信度依据是confidence_basis=pilot_gain_gt_1pp，不能当成功概率。
6. 既存显式direct_full可只读展示，但必须注明其报告 `pilot_bypassed_by_explicit_request=true`；不冒充两阶段完成。当前前端无POST，因此**不补参数、不授权、不创建评估**。L4/L5与差异事实不套门槛；现有Token/combined评估零/负收益不隐藏，其语义由Token回传确认。
7. 显式评估子任务不在诊断主目录中；初始report没有完整子任务列表。已知子task或SSE事件可通过 `/diagnostics/discovery/tasks/{id}/terminal` 读parent_task_id/plan_refs，再回父任务找finding/fragment。子report不保证重复保存父证据，plan.finding_refs也不自带父task。**若只读页面不知道子task，不能宣称能发现所有历史显式评估**；本期以初始报告已存自动收益为主，无需新增接口或前端操作。

指标：before/after及modified_before/modified_after为 `{n,j,p,h,c}`，全部十进制字符串；n请求数、j序列化JSON Token、p模型输入Token、h理想命中Token、c计算Token，p=h+c。R=h/p，p=0不可判定。gain_percentage_points是绝对百分点精确分子/分母；compute_tokens_delta=after.c-before.c，正数是增加。modified_*只代表实际改动请求子集，不能重命名为“全部受影响请求”；未修改的后继请求也可能收益变化。

**影响请求数缺口**：finding没有全scope去重影响数量；plan.operations数量是操作数，不是请求数。可显示scope.request_count（分析范围）、evaluation.coverage（评估覆盖）、modified_*.n（实际修改请求数）并分别标注。没有量化评估时仅显示例证两端RequestKey，不能说“只有2条受影响”。不得把L2通道和dynamic通道rule_coverage简单相加当五规则总覆盖。

结论：**已明确**字段及只读资格；**存在缺口**：专属title/description/全范围影响数、所有候选必有收益、未知子task自动发现均未提供。固定解释文案/未知值展示已符合UI-03原则，不阻碍开发方案；若未来要强制全覆盖量化或跨浏览器全部评估历史发现，那才需要另行需求决定，本轮不扩展。

## ② 当前版本与文件身份

当前[完整本线读取摘要](FRONTEND_READONLY_IDENTITY.json)记录64个文件，包括公共/低命中源码、诊断HTTP/discovery/app/CLI/Dispatcher装配、本线测试、三个契约JSON、pyproject/uv.lock、env来源与编码资产锁、RESOURCE_PROFILE及本轮样例。Token私有源码/测试/资源不在本清单，不代签其身份。

- 本轮读取HEAD：`5d824b506d9e055bcf397c3846dafc450fcf02e5`；这是Git检查点，不代表清单文件全已入提交。JSON逐文件SHA是**当前工作树**身份，tracked_in_index仅表示Git索引中有路径，不代表clean或已经发布。本轮无Git提交、合并、push。
- analysis-common-1.0、diagnostics-http-1、diagnostics-discovery-1三个原manifest逐项匹配。旧local-2摘要中当前发生变化的原有文件仅analysis_common/storage.py（FE-N1持久终态日志安装）；新增discovery模块等不在旧清单，不能用旧local-2全量摘要证明新实现。
- L1–L5仍prefix-detectors-1、finding.rule_version=1；RuntimeOptions仍diagnostics-runtime-1。没有因为前端只读新增或修改规则。
- app.py注册diagnostics与diagnostic_discovery路由；CLI/Dispatcher使用共享worker；service.process_next锁实际state_root/worker.lock，锁是运行态文件，没有固定内容SHA。source/encoding仍按封存模型/profile/settings/资产身份复用；env编码锁的SHA不是本轮实际资产加载验证。
- SSE64连接/20秒心跳/10秒发送超时、显式资源预算及已知校准限制见[通知交接](NOTIFICATION_HANDOFF.md)与[资源记录](RESOURCE_PROFILE.md)。本轮不设新预算、不新增用户输入项。

适用测试身份：历史[自审](SELF_REVIEW_20261031.md)对应local-2；历史[FE-N1结果](batches/FE-N1/RESULT.md)对应通知增补，联合199、专用7、监控300通过（集合重叠）。它们是本地构造数据/真实Tokenizer、HTTP/ASGI等分项证据，不是生产业务效果或前端验收。**本轮只做静态模型/关联/摘要核对，不运行这些业务回归，不调用分析服务或真实任务**；当前测试文件身份在新清单中供后续重跑。

结论：**已明确**当前源码、冻结契约、装配、依赖锁及历史测试适用范围；**无需用户新增输入**。服务现场版本、资产可用性、前端连接与代理行为属于后续联合验证。

## ③ 可消费关联静态样例

[FRONTEND_READONLY_EXAMPLES.json](FRONTEND_READONLY_EXAMPLES.json) 为**纯构造响应**，不是HTTP抓取、任务运行或真实模型结果。没有启动数据库/服务/Tokenizer/离线回放；只用现有不可变模型和纯值/序列化辅助函数生成字段。指标与时间为说明性数值。资产/encoder/algorithm身份显式写synthetic；source manifest摘要仅哈希文件中明确保留的synthetic marker文本，不声称存在模型资产。raw_sha256确实根据所附原始UTF-8文本计算；report_digest只对应说明性fixture manifest，不是服务器封存验收摘要。前端不可拿样例run/task/asset向实际API请求。

| JSON入口 | 内容/消费方法 |
| --- | --- |
| ready_chain.responses | 按真实GET路径索引 `{status,body}`；含目录→report→finding/experiment/evaluation/optimization/plan→comparison全文完整链。ready_chain.walk列读取顺序；单项data与列表包装区别保留 |
| ready_chain中的pilot/full | pilot n=2、全scope n=4；相同transformation_digest，pilot +10pp、full +20pp，n/p/h/c守恒；仅full进入optimization。构造总量不表示附带短JSON实际Token数 |
| exact_1pp_pilot | 独立替代场景：恰1pp，pilot_below_gate、full=null、optimization空、仅pilot Plan；只可复用公共finding/comparison，不与ready场景的full结果混合 |
| L4_L5 | 两个独立场景；finding + comparison_response，左右均完整JSON而非block，原文摘要真实对应这份合成文本；recipe=null、优化空 |
| catalog_variants | 首次partial、empty、legacy分别defaults=[]；empty scope.n=0（字段request_count）；legacy时间三个字段均null；用于“请选择历史报告”，不判断正常 |
| direction_isolation | 同binding的完整两方向报告随后Token-only ready；低命中默认仍旧task，Token默认新task。仅目录语义样例，不附第二报告正文；跨模型隔离由既有test_discovery.py覆盖 |
| read_error | 409 REPORT_DIGEST_MISMATCH；原已显示报告/时间保持，不能渲染为空建议 |

已有[discovery完整样例](../../contracts/diagnostics-discovery-1/examples.json)继续用于事件/terminal/空目录；不替代本轮低命中关联链。低命中full/direct_full差异的真实运行测试入口：test_experiments.py、test_diagnostic_tasks.py、test_diagnostic_http.py、test_dynamic_replay.py；本轮不重跑、不把这些生成器说成静态现场响应。

本轮核验应包含：新JSON解析；finding/plan/evaluation/目录/TaskReceipt按当前wire模型验证；plan→finding、evaluation→plan、experiment→evaluation与scope一致；比较摘要匹配原文；strict>1pp/恰1pp资格；历史目录无默认与方向隔离；清单文件SHA/原manifest一致。验证结果收口在本文末，不替代真实联调。

结论：**已明确**完整构造消费链及边界样例；不再只有测试生成器。**后续联合验证**才补真实服务响应、浏览器/代理SSE与样例到实际展示一致性；不要求用户重复批准已有展示门槛。

## ④ 返回用户监控的范围身份

后端确认身份，不制定前端hash路由。必须区分“查看原报告来源监控”和“查看业务修改后的当前监控”。后者只导航到已确认的同服务范围，不声称跨run/配置/窗口已直接可比。

| 来源/目的 | 可用身份和现有只读入口 | 限制与前端行为 |
| --- | --- | --- |
| base原报告来源 | scope.source.base_run_id + scope.appid；GET `/analysis-runs/{run_id}/view-snapshot?appid=...`、`/requests?appid=...`及完整原文明细；源run/model通过`/analysis-runs/{run_id}`核对 | base没有common_name；不能拿base_run_id冒充user_run_id、自动POST绑定或猜服务名。诊断可能是子window，S0快照是run×appid范围，不支持用诊断window参数直接复现相同聚合 |
| user_v2原报告来源 | scope.source.user_run_id → GET `/monitoring/user-v2/runs/{user_run_id}`；核对receipt.base_run_id/common_name/model_id；rankings/modes用同user_run_id；基础图/请求明细仍用base_run_id | 排行appid_contains是子串筛选，不是精确appid，前端须从返回项核对完全相同appid。后续页固定index_revision，不能拼不同revision |
| 源快照/配置 | scope.source.manifest_sha256、asset_identity、encoder_identity、profile_json、settings_json、algorithm_version，scope.window/request_count/request_keys_digest | 保存的是原base封存身份；SourceSelection.expected_index_revision在提交校验，但**AnalysisScope.SourceIdentity没有持久返回该user index revision字段**。回监控读到的现revision不能标为原报告revision；没有索引revision精确历史重建保证 |
| base当前监控 | GET `/monitoring/catalog?appid=...&model_id=...` 或 `/monitoring/runs`读取当前已发布候选，按监控自己的catalog_revision及身份契约选择 | 只确定appid+model，缺common_name无法证明物理/逻辑服务一致；应回监控选择页/提示身份不足，不无声跳某一服务。不能把旧run固定链接称当前监控 |
| user_v2同服务当前监控 | binding的appid/model_id/common_name可作导航条件；以监控前端已知且核对过的user_run receipt匹配当前run；用该run自己的index_revision/配置展示 | 当前用户V2没有服务器用户运行目录/latest按common_name查询接口；公共diagnostics目录也不是用户监控最新run目录。仅凭旧user_run_id不能自动发现该服务最新监控；若前端无已验证关联则返回服务选择入口，不自动bind/recompute |

common_name是已声明的逻辑服务名，不是物理Endpoint/UUID；discovery.binding_id忽略run/window/配置，用于报告目录分组，不能作为配置一致性证明。source_kind由user_run_id是否存在区分base/user_v2，不等于另一个服务实例。

header区分：diagnostics使用x-tokenscope-service-instance；user_v2使用X-TokenScope-Instance-Id（必需）；S0按已有监控契约读取/绑定实例，不把诊断header当监控header。先确认同服务实例再使用缓存的run ID，实例切换不能跨实例转移。

源库/原文已清理或校验失败时，原报告封存结果仍可能读到但原文/监控回跳返回404/409/503；保留报告原身份并提示来源不可用，不能用新run代替旧证据。业务修改后读取当前监控时同时显示新数据范围/模型模式，与旧建议比较仅为人工判断，不证明同样负载、相同资产、线上质量或效果归因。

结论：**已明确**可用只读路径和两类返回语义；**存在缺口**：旧user索引revision未回传、base缺服务名、缺按服务名发现最新user run接口。这些不阻碍按已确认的轻量返回方案进入监控选择/已验证范围；若要求自动精确跳到未知服务当前run，才需后续接口或业务绑定信息，本轮不临时编码。

## 收口与用户决定

本轮[静态验证记录](FRONTEND_READONLY_VALIDATION.json)：24个wire模型对象、6个完整原文摘要、64个当前文件摘要及当时8个正文链接通过；目录→报告→finding/experiment/evaluation/plan→comparison关联和精确1pp门槛核对通过。三个原manifest无差异；本轮没有执行历史业务测试或启动任务。链接计数为验证时正文快照，不作为功能测试数量。

四项中字段语义、当前身份、构造关联样例、监控范围边界均已明确；未提供的字段与发现能力已逐项标出。开发方案前不再缺本线材料。真实HTTP/浏览器、代理长连接、缓存失效、历史源不可用及UI-03截图为后续联调/验收，未代填通过。

**无需新增业务输入，剩余为工程计划/后续联调。** 本轮不要求重复审批只读原则、通知目录、partial/empty、严格>1pp或无参数评估UI；正式前端编码是否启动及工程计划按其会话的用户授权推进。

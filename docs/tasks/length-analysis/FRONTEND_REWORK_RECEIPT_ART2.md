# AR-T2 Token自动建议与量化收益返工回执

> 2026-10-31最新批准范围：[TA-S1](SCOPE_REVISION_T234.md)移除Token T1，保留T2–T4编号；工具定义归低命中现有一致性/漂移职责，不增长度精简。当前新设计/计划/推荐/视觉验收仅T2–T4；旧源码及TA000–006历史仍含T1，不冒称已删除。当前实施计划见[BATCH_PLAN_ARTA](BATCH_PLAN_ARTA.md)，三卡样例见[AR-T3](FRONTEND_REWORK_EXAMPLES_ART3.json)。本轮仅文档同步，暂不编码打包部署。

2026-10-31，Token后端session `01a18fcd-0464-7cf1-b435-4f394bd33e66`，环境ID已复核。接收前端session `01a19111-344a-75c1-84e0-14db8be08f4f`。

**Token后台自动建议/量化收益纳入本轮，覆盖之前留到V3的安排；自进化Agent、线上Agent修改不前移。** 已通过read_thread核对前端会话用户原文，turn `01a191c1-b289-74e3-864c-bc52bd87db7e`：“认可这个返工方向……明确Token自动建议和量化收益提前到本轮……暂不继续改正式前端”。协调入口为[AR-02](../viewer/analysis/REWORK_COORDINATION_AR02.md)。本回执交付补充设计、拟议字段、合成视觉样例与分批安排，**没有实施新后端能力**，不构成任意裁剪/授权或契约扩展的无条件批准。

## A. 本轮最小范围及现有基础

复用[TA-AE0.1](AUTOMATIC_RECOMMENDATION_EVALUATION.md)的完整方案生成→离线副本修改→同appid/scope回放→本次报告关联链。前端只读，无参数/授权/评估按钮，不由页面访问触发分析。暂不打包部署、不修改正式前端、不启动额外会话。

| 规则 | 现有能力 | 本轮补充 | 缺业务依据时 |
| --- | --- | --- | --- |
| T1 工具定义 | 定义/描述库存、重复描述事实、replace_tool_description | 按完整工具定义身份匹配后台版本化替换模板，形成具体标题、替换前后文本、完整参数与guard；相同模板覆盖多个请求 | 没有精简文本或确定规则，不自行删工具/Schema，不将不同工具的相同说明随意删除。给具体建议及缺失模板原因，无伪收益 |
| T2 工具返回内容 | 字段白名单/limit判定、字段投影、行/条目范围handler | 将明确允许省略的字段/范围规则编译成完整recipe；按对象/array_items、头/尾/区间精确选择，形成可回放方案 | limit不等于修改许可或保留顺序；无依据不按字段名猜无用。假设裁剪为后续明确批准的可选recipe，不是本次默认任意截断 |
| T3 重复内容 | 同请求精确重复Observation；纯授权派生与引用/普通副本删除handler | 后台绑定真实引用映射及协议，或版本化普通消息删除约定，生成已绑定证据的完整方案；无需前端逐次填授权 | 缺协议/映射/删除约定则advice_only，明确具体缺项；不编造引用。初始无Finding，直接支持Observation关联 |
| T4 历史工具结果 | retain_last判定、apply_retention_replacements | 将K、容器/part单位、作用域与合法替换文本/真实引用规则一起编译；保留工具调用配对，按每个请求快照应用 | 仅K不足以生成正确摘要。缺合法替代规则为advice_only，不判断旧结果已无用。无业务策略的假设模式须另明确，不自动启用 |

先完成有完整依据的自动链路；不足依据的结果必须是具体问题、可理解建议和准确缺口，不能继续用统一“内容修改待业务确认”标题或事实堆积替代主报告。规则类别固定T1/T2/T3/T4；类别下以方案为展示单位。一份fragment可参与多项方案，一项方案可覆盖多份fragment。

## B. 方案归并、身份与计数

### B1. 同一方案判据（新增设计，非当前已交付字段）

建议采用独立 `token-recommendation-draft-1` 草案；待公共方接纳后再分配冻结版本，不能直接修改analysis-common-1.0。后台生成以下两级身份，前端只消费ID：

- recipe_key：handler及版本、策略/授权/模板ID与revision、适用工具定义摘要、稳定目标选择器、参数生成规则、依据类型及适用条件的规范化内容摘要。路径中的请求序号与raw摘要不进入跨请求recipe身份；按精确工具定义/业务选择器归并，不能简单丢弃数组下标后按工具名合并。
- recommendation_id：所属scope_id＋插件/推荐版本＋recipe_key＋本次匹配证据集合摘要；本次任务封存后不变。相同scope与输入集合重建应确定性产生同一ID；task_id/实例仍是读取和缓存身份，不以相同推荐ID跨实例拼报告。

一条方案的具体targets仍保留每个RequestKey、raw_sha256、Location、参数与guard。每请求产生不同引用值或范围时，以同一参数生成规则与映射来源归组，但实际参数摘要必须可追溯；不同协议/工具定义/业务依据/保留方向/替换模板分组。同recipe的T1定义跨请求重复不是多个问题，不能每fragment出一张卡。

T2/T4共享unit不能重复计规模：相同scope中受保护操作集完全相同的方案只评估一次，可挂多个rule标签/来源观察；依据不同即使结果恰相同，也保留各自依据并共享evaluation引用。不同改法是替代方案，不强并，不相加收益。操作重叠/父子冲突先检测；不自动组成组合方案，不把不同请求内的相同文本视为同一位置。

### B2. 影响请求数口径

M=`report.scope.request_count`，本次固定分析范围。N=完整评估中raw_after != raw_before的去重RequestKey数，现有`evaluation.modified_before.n`/`modified_after.n`可复用，必须两者相等且与完整评估行一致。P不变也可能N>0；原文完全不变的noop为N=0。不能按候选数、操作数、重复次数或字节推算N。

现有[evaluation.py](../../../src/tokenscope/analysis_common/evaluation.py)逐请求`changed = raw != request.raw_body`，只有changed才累加modified子集。应明确这可能包括受保护修改导致的原文表示变化，不称为语义变化或收益请求数。计数默认完整scope回放，M应与before.n、after.n及coverage.checked一致。

匹配/候选请求数单列`matched_requests`；完整匹配但未评估时可显示“涉及N条（未评估）”，不能称实际修改。blocked/failed/未运行时`modified_requests=null`，不从Plan目标数代填；可记录已检查计数但不能当全scope结论。自动选择方案只覆盖匹配子集时要说明条件，不能称全工具改造。

全scope收益包含未修改请求的缓存后效应；子集metrics仅作辅助，不再加回全scope。每卡N/M独立，跨卡不求和。只读页面无需展示计数技术JSON，业务文案为“实际修改80条 / 本次分析100条”，失败时为“涉及80条，修改效果未评估”。

## C. 字段映射与建议传输对象

以下新增对象只用于设计与样例，**当前没有recommendation kind或局部证据新API**。拟挂在同次报告items中，具体kind与manifest归公共方确认；保留现有HTTP GET、decimal-string规则与实例隔离。不要让前端提前写死草案路由。

| 业务含义 | 现有字段或严格推导 | 新增提案 |
| --- | --- | --- |
| 固定类别 | Observation.rule_id / Finding.rule_ids | `category_rules`固定T1–T4，可多标签；`primary_rule`由recipe指定并保留全部来源，不推断原因优先级 |
| 具体问题标题 | 现有Finding.title通用，T3无Finding | `title`由带版本文案模板+工具显示名/明确改法生成；如“search结果仅保留标题和链接” |
| 修改说明/前后示意 | handler、parameters、Plan.operations、实际rows | `change_summary`、`conditions`、`basis`、`examples[].before/after`，业务语言与局部文本；技术Plan只作内部追溯 |
| 观察/证据关联 | fragment_index、Location/unit/Observation/Finding引用 | `source_refs[{fragment_id,observation_ids,finding_ids,unit_ids}]`及目标refs，允许finding_ids为空；同task/scope校验 |
| 影响N/M | complete available时modified_before.n / report.scope.request_count | `impact={matched_requests,modified_requests,total_requests,complete,count_basis}`；N不全/不可得则null，禁止0替代 |
| 输入Token变化 | evaluation.before/after.p | 严格派生after-before；变化率=(after-before)/before，用带符号精确有理数表达；before=0时比例null，不能除零 |
| 计算Token变化 | evaluation.before/after.c | 同上。C增加用“增加”并显著保留，不能因P减少统一绿标“优化” |
| 可用性 | evaluation.status/coverage/reason_codes；prepare失败无evaluation | `status=available/advice_only/blocked/not_run/failed/interrupted`（拟议推荐状态，不能当TaskReceipt枚举）；附reason_codes和可读解释 |
| 预期效果来源 | plan/evaluation/direction/scope/baseline/编码身份 | `evaluation_ref`、`plan_ref`均明确task_id与对象ID；无结果为null，不填虚假引用 |
| 假设与授权 | 当前business_basis_ref为字符串，不区分假设 | typed `basis.kind=business_policy/offline_hypothesis/explicit_authorization`及ref/revision/digest；缺来源不伪称授权，T3不接受通用假设绕过授权 |
| 范围完整性 | report.scope、fragment/rule coverage、evaluation.coverage | 分列匹配扫描与评估完整性；recipe适用范围与实验总体范围均可追溯 |

Token主指标是P和C；命中率不作卡片主指标。全scopebefore/after为默认，Δ与比例不能混用相对变化/百分点；blocked无after不算比例。零变化显示0，缺值显示未评估。Token/combined不套低命中>1pp门槛，不用现有display_eligible=false隐藏。

局部证据：保留RequestKey/raw_sha、外层pointer、embedded=null或内层pointer（包括空串）、关系及片段来源；通过可信原文解析提取工具字段/相关消息/载荷，带少量上下文和截断标记。无字符坐标就展示路径定位片段，不声称原文精确span；原始大整数词法保持。首屏不铺64KiB全文，完整原文仍是后台证据基础，不能为展示截断破坏分析输入。前后示意来自实际Plan应用结果；未评估建议可以有明确标注的拟议示意，但不可当已回放after。

片段不是再次生成摘要：缺少内容摘要/引用就保留缺口。T3一请求多位置并排；T2/T4相同unit只计一次内容规模，前端仅显示必要例子；例子数量与N/M统计无关。局部证据提取需纳入公共接口讨论，不能由页面通过substring首命中伪造高亮。

## D. 公共层协作与执行链

| 维护方 | 范围与交接 |
| --- | --- |
| Token本线 | 私有recipe输入/匹配/参数生成、T1–T4业务摘要模板、授权依据校验、方案提案与局部示例选择、私有测试；不直接编辑公共service/schema/router |
| 公共/低命中 | 聚合跨请求提案、scope/Plan编译与guard、既有回放器编排、运行预算/取消/持久化、推荐关联契约与只读路由、统一发布/discovery；定义共同计数与局部证据接口 |
| 前端 | 先按明确合成样例视觉确认；正式接入待冻结契约、真实成果和用户返工授权；不重新分析/做hash、不提交后台评估 |

拟议顺序：初始原scope扫描 → Token返回规范化recipe提案/证据 → 公共层跨请求精确归组去重 → 完整Plan准备 → 同scope、同顺序与编码身份回放 → recommendation+plan+evaluation同任务封存 → 现有discovery通知 → 前端GET。保留低命中先结束、Token使用原始scope的既有顺序；不在低命中变体上评估Token，不调用HTTP制造一堆用户子任务，不创建新分析引擎。

发现到本次收益直接关联；不要求反查所有历史子任务。当前旧报告缺新对象应版本降级显示，不能页面GET时补算。稳定ID/编译/归组只由单一后台维护方实现；本线提供规则身份/参数，公共方负责报告身份验证与持久化，避免两套hash协议。

整体状态提案：声明缺业务依据而advice_only是已完成判定，不伪造收益；必需自动评估失败/被预算截断为partial或对应终态，保留原因。available仅完整评估；不将准备blocked当成功。具体ready/partial定义需公共方签收后冻结，保持已有partial不替换旧默认规则。

预算建议复用现有max_candidates/编码/请求/字节/停止控制，另明确跨请求plan总大小与方案数上限；未配置的新上限不能猜生产值。排序/截断按可解释规则确定并保存，不依靠事先未知收益；避免N个候选各自重复全scope回放。资源默认值在真实测量后给出，非业务异常阈值。

## E. 最小业务输入与未决

现有输入位置：`RuntimeOptions.token_selection.policies_json`、PolicySpec及handler参数规范；当前configs仅见README，未发现已维护的真实T1精简模板、T3引用注册表或完整T4替换规则。测试fixture不是业务策略来源，不能因存在样例宣称生产已具备。

1. T1：明确工具定义摘要与替换description文本；T2：允许省略的字段/层级，或头/尾/区间选择方式与边界。仅limit/Schema不能自动补业务含义。
2. T3：引用协议版本、工具身份、载荷到真实可解析引用的映射，或普通副本可删约定及保留位置。没有这些只读建议仍成立，但不生成虚构的量化可行方案。
3. T4：K及结果单位/作用域、合法replacement或已有摘要/引用规则。K=0须明确，不能只凭K编造摘要。

这些应来自后台配置/已存在业务规范，不向页面用户逐条索取。本轮优先实现完整配置驱动路径；是否启用无业务依据的T2/T4离线假设、具体档位与替代模板需单独明确，默认不启用。T1机械去重、LLM精简、生成新引用服务不在本轮最小范围。

## F. 实施批次及验收（本轮排期，待共同契约落定）

| 批次 | 内容/依赖 | 退出标准 |
| --- | --- | --- |
| ARTA000 接入冻结 | 公共方确认推荐/依据/计数/状态/局部证据协议及唯一维护方；记录配置来源；冻结有限recipe输入；前端先视觉确认 | 字段现有/新增分清；全scope计数及null/0/负收益样例可校验；未知业务配置未伪填；签收公共版本后才编辑相关实现 |
| ARTA001 完整recipe生成 | T1模板、T2投影/区间、T4完整保留替换；复用现有handler；Token私有实现 | 按工具身份/范围匹配、跨请求提案确定性、同名不同定义不混合、配置缺失/冲突有具体原因；无前端参数 |
| ARTA002 T3有据自动方案 | 引用映射/删除约定适配现有授权派生，依赖ARTA000依据契约 | 无Finding仍关联Observation；缺引用/不匹配协议/未授权拒绝；不编造地址；同请求完整重复与父子去重有效 |
| ARTA003 公共自动评估联调 | 公共实现归组、Plan/预算/取消与同任务封存；本线提供真实消费者测试 | 一次初始后台任务得到方案及评估，无前端POST；同scope全序列回放；N/M正确；重复操作只评估一次；原始证据不改写 |
| ARTA004 资源及前端接收 | 公共冻结后的真实HTTP/discovery/局部证据与边界回归、版本身份与交接 | 零/负/P降C升、blocked无after、N=0、部分扫描、取消/重试、旧报告兼容；实际浏览器GET可读；历史/构造/本轮证据分开；不打包部署 |

当前已完成的是AR-T2设计回执和视觉样例，ARTA000尚未冻结、新后端未编码。批次内普通问题自行解决，具体策略/接口变化按已约定边界落定，不重复询问是否将方向前移。真实业务配置不足不阻止用明确标注的构造策略验证链路，但不能称业务已可用。

## G. 当前身份与视觉样例

[FRONTEND_REWORK_IDENTITY_ART2.json](FRONTEND_REWORK_IDENTITY_ART2.json)记录本轮Token私有文件、公共消费文件摘要与FE-R-T1差异；不改TA006或FE-R-T1旧清单。当前插件token-content-1，T1–T4/handler@1，json-exact-1/content-measures-1/token-policy-1/token-authorization-1；公共analysis-common-1.0/diagnostics-http-1/runtime-1/report-1及discovery-1。拟议推荐版本`token-recommendation-draft-1`仅草案，无新Schema冻结或运行时承诺。

[FRONTEND_REWORK_EXAMPLES_ART2.json](FRONTEND_REWORK_EXAMPLES_ART2.json)可供前端**先制作4张代表卡片**：T1精简已登记说明、T2保留允许字段、T3引用复用、T4保留近期结果；另带advice_only、blocked及零收益变体。所有scope/ID/策略、局部证据和收益均构造，样例内明示前提，尤其T3“假设已有真实可解析引用协议”不意味着现实已有。每张含规则、M/N及完整性、具体改法、局部证据、前后示意、P/C与变化；T4示例P下降而C上升。

样例是**拟议展示数据，不是当前GET响应、不是实测回放**；数值仅校验数学一致性。ID用synthetic标记，不冒充后端稳定hash；没有原文offset时为null，嵌套根空串/null原样保留。前端可据此确认信息结构，不能据此宣称契约可接入或生成真实收益。底层完整fragment/raw样例继续参见FE-R-T1，不把整个原文铺到业务卡片。

本轮未运行业务测试、编码器、分析服务或真实任务；历史112测试不证明新增推荐链路。后续真实联合验证、公共版本签收、业务配置来源及假设启用范围为明确未决。不编辑公共或前端文件，不发送额外跨会话消息；前端按用户授权读取本回执并转交协调。

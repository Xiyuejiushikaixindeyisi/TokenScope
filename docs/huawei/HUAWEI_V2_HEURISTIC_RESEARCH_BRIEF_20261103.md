# 华为V2补证据、数据量级与启发式研究任务书（方案依据）

2026-11-03后续：用户已要求完整可转发prompt，见[最终调查prompt](../../prompts/delivery/HUAWEI_V2_READONLY_INVESTIGATION_20261103.md)。执行顺序以该prompt为准：身份/资源→量级/预算→三项页面排查→有界tools/messages研究；本文保留原方案依据，不作为另一份并行指令。本机只完成文稿，尚未向华为发送或执行。

2026-11-03。由镜像打包与审查会话拟定，当前只形成方案；尚未向华为agent发送、未启动调研或修复。用户后续决定转交启动时，可直接提供本文。本文是本次只读调查范围，不沿用旧部署prompt中的修复、重建或全量执行授权。

依据：[本机核对与修复方案](HUAWEI_V2_REVIEW_AND_RESEARCH_PLAN_20261103.md)、[现场报告原件](HUAWEI_V2_ACCEPTANCE_REPORT.md)。第二次验收不通过；本任务用于查根因和确定研究/预算，不宣称已修复。

## 给华为agent的任务

请基于现有交付版本、原始真实CSV和已经产生的结果，完成以下调查，只回传一份自包含Markdown：`HUAWEI_V2_HEURISTIC_RESEARCH_REPORT.md`。关键命令、研究脚本/查询的关键源码、原始值与API/DOM证据直接嵌入正文；不能写“见附件”“见items”“日志另发”。不覆写上一份验收报告。

### A. 范围与证据保全

1. 当前只读调查，不修改产品源码、前端HTML/展示、冻结契约、原CSV、已发布结果、recipe或模型配置；不提交诊断/评估/重算任务、不构建或部署镜像、不改变限额并全量重跑。发现问题应提供复现和修复建议，明确“建议、未实施”。只有用户另外明确授权修复后才实施并记录diff/复测，不能将本任务书当修复授权。
2. 读取已有服务与state。服务未运行、身份不一致或无法读到证据时如实记录，不顺带启动新部署/新任务。保留当前失败状态和原包、state、日志；以后新版本端到端验收必须先核实停旧TokenScope服务、进程和容器、端口释放，再用独立新state和新浏览器冷启动，不能换端口让旧版并行。只读调查浏览器可使用独立临时profile，不清除用户浏览器记录。
3. 固定版本：交付名`tokenscope-v2-approved-20261102`，报告源码`b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af`，镜像`sha256:a38d0ab2cfe26154c96adb5e876538893005e5cb100fc5c53640823c391683a8`。实查运行镜像ID、容器资源/挂载、HTTP前端资源SHA、API能力/服务ID、配置和模型资产摘要，差异先列出，不能强套旧身份。
4. 只用真实数据：`/home/aarc/zhangxiyue/10.20_Trace_extract/10.20_Trace/`的3个CSV供用户监控和异常研究；`10.20_MA/`的18个CSV供MA调查。两类字段不同，不能互换，也不能造数据填缺失。
5. 原报告state为`/home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-approved-20261102-20261102T0955`，原service ID为`abf57577-2dcc-4ddb-9758-bbbd548ddfdf`，均仅作查找线索。SQL用只读连接/一致性事务，不实例化可能建表或迁移的产品Store。只读DB前查明WAL与连接状态，不能仅复制主DB文件而漏WAL。
6. 调研生成物仅放现场TokenScope项目内独立`artifacts/research/`子目录；允许在本任务实际获启动后编写独立统计脚本，但不得改产品/测试源码，脚本关键逻辑须嵌回报告。使用流式读取、有界采样，不一次载入26GB正文或给每行完整展开树常驻内存。失败/预算触顶保留已知覆盖并停止该子项，不自动升级成大作业。
7. 用户远程看页面仍为SSH转发：`ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44`，然后访问`http://localhost:18002`。该URL需配合真实现场服务身份核对。

### B. 先补三项页面问题的端到端读取证据

这些都是本次用户明确反馈，不能再仅用API返回200或任务completed作“通过”。

#### B1. 同一用户的多模型结果不可见

- V1用户能从同一入口查看该用户使用的所有模型。V1发布commit `92236ee993974e740d085e22e49b6b93c9487430`的`apps/viewer/src/app.tsx:70`按同appid生成模型按钮，`state/catalog.ts`分页读取全服务`/monitoring/catalog`。
- V2 `#/users?run=...`绑定一个user_run；模型区域为静态common_name/model_id，最近记录来自本浏览器。调查不以手填其他run ID或分发三个URL作通过标准。
- 选原报告中跨模型存在的同一APPID，读服务端完整目录及三个用户运行回执，列`appid/model_id/common_name/user_run_id/base_run_id/index_revision/state/时间窗`映射。以最新数据查实，不只拿S0目录存在证明V2索引可用。
- 独立浏览器进入普通`#/users`与原Qwen链接，逐项记录模型是否可发现/可切换、APPID范围、网络请求和所见文字；刷新/从搜索与排行返回也记录。地址中固定run应只表达当前选择，不应遮蔽同APPID其他模型。
- 回报“数据是否存在”“V2运行映射是否完整”“页面是否列出”“是否只能手填ID”四层证据。方案恢复同一入口内模型切换和已有搜索/TTFT功能，不新增入口，不跨模型混算一个命中率，不把APPID擅自改成跨租户userhash聚合。

#### B2. 后台已结束但异常页面无结果

- 列指定10个任务的完整task_id（不能截断）、appid/model/service/source/index/scope/window/方向、终态、report_published/digest、各阶段完成度、预算reason_codes、recommendation availability/counts。`partial`是任务终态但不是全规则完整，report摘要也不内嵌全部items。
- 先通过`/diagnostics/capabilities`、`/diagnostics/discovery/capabilities`、`/diagnostics/recommendations/capabilities`取得实际身份/Schema。诊断读取使用`X-TokenScope-Service-Instance`，不要误用监控的`X-TokenScope-Instance-Id`。
- 只读检查以下链路，按实际Schema补参数、分页/快照和身份头：

```text
GET /diagnostics/discovery/catalog
GET /diagnostics/tasks/{task_id}
GET /diagnostics/tasks/{task_id}/report
GET /diagnostics/tasks/{task_id}/recommendation-summary
GET /diagnostics/tasks/{task_id}/recommendations
GET /diagnostics/tasks/{task_id}/difference-groups
GET /diagnostics/tasks/{task_id}/difference-groups/{group_id}/examples
GET /diagnostics/tasks/{task_id}/items/{kind}
```

- 前端实际读取report+recommendation-summary，再读recommendations/difference-groups；不能把没有report.items直接定为根因。记录响应头、状态、身份/计数/关键内容和浏览器错误，分页读全，不能只检查第一页。
- 对同一任务分别打开裸`#/analysis`、页面手动选择历史、显式`#/analysis?direction=low_hit&mode=history&task=<完整task_id>`（如有binding参数必须与task一致），再切Token方向。记录是否无默认ready、是否没有发report请求、是否收到结果但校验/渲染失败、是否扩展未发布。缓存、SSE终态与刷新结果分别核实，不提交重算来掩盖读取问题。
- 当前默认只选择ready；10任务均partial可能导致裸入口无默认。即使不能作为最新完整默认，已有partial结果也应能被用户发现、明确其限制并查看；不能把partial改成ready，不能用原始finding替代批准卡片。L4/L5各聚合一张卡最多3例；L1–L3优化卡仍要求完整评估严格>1pp，不降低门槛制造结果。
- 原始事实、无适用规则、没有业务recipe、证据不足、技术未完成与真正零异常分开。Token fragment数等于请求数不代表T2/T3/T4全完成。给出每层实际状态，禁止只写“后台完成，前端问题”。

#### B3. MA四指标缺失

用户范围：DeepSeek-V4-Flash全部UUID、GLM-V5.2部分UUID；缺理想命中率、真实命中率、整小时重算Token/s、实际重算Token。对9规格全部已发布UUID做矩阵，所有受影响UUID都列明，正常GLM和Qwen作对照；无数据与未调查要分开。

只读查`/monitoring/ma/catalog`（分页带catalog_revision）、`/monitoring/ma/runs/{id}`、`/monitoring/ma/runs/{id}/instances/{uuid}`、`/monitoring/ma/runs/{id}/quality`，用实际`X-TokenScope-Instance-Id`。保留run/revision/配置及pre/now文件身份。

矩阵至少含：

```text
model/spec | pre/now文件SHA | ma_run_id/revision | UUID | pre/now记录数
A可归属 | P生产输入有效 | R真实有效 | E编码/理想有效 | Q配对
pre_assigned/pre_encoded | ideal_status | 逐字段quality原因及互斥行数
ideal.hit_rate | real.hit_rate | paired_ideal.hit_rate | paired_real.hit_rate
real.sample_count | real.totals.input_tokens/cached_tokens/uncached_tokens
hour.request_count/real_count/uncached_tokens/uncached_tokens_per_second
12桶合计 | 页面四项文字 | 独立指标详情文字 | 缺失根因/证据/尚缺信息
```

原报告DeepSeek-32K run `1bb5a14b-6356-44fc-80f4-08c15fc1255c`、UUID `0a5bf216-53d9-40ad-967f-49365bcd1c20`：A740/P730/R0/E345/Q0，独立ideal=0.3597190553279913、ideal_status=available。主表使用paired_ideal/paired_real，详情使用独立ideal/real。因此配对理想空不等于独立理想不存在；请展开详情并记录真实响应/DOM，不能只复述报告。

对缺数UUID流式审计原CSV：prompt_tokens/cached_tokens/completion_tokens各自的空/字面NULL/非整数字符串/负数/超界/cached>prompt及合法零的计数与最小真实原值；确认model_standard_name、UUID、时间窗和列绑定。不预设出现了这些格式，只报告观测。源记录索引是CSV逻辑记录编号，含换行字段时不能用wc -l当记录数。

核对已有只读MA records/issues/projections：R只依赖A及合法prompt/cached，不依赖request_input能否编码，也不依赖completion合法。非法JSON可能减少E/Q，不能单独解释R=0。按`field×code×role×UUID`统计并保留每类最小源记录映射；一行多错误需单独列联合组合，不能把issue总数当坏行总数。

检查null和0：无R时真实指标不可用；prompt>0且cached=0时真实命中率应为0且重算量有效；全部prompt=0时命中率分母为0，但有效重算量可为0。有请求但无R的桶为null，真空桶为0，部分R仅覆盖该有效集合并注明覆盖。预热冲突只影响理想，不应损坏实际统计；不要用模拟值补实测或把独立值填进配对列。对每个缺数UUID归因到原数据/解析/回放/聚合/API/前端中的有证据层，未确定则写未知。

### C. 数据量级与预算调查先于深度探测

已知量级仅供复核：Trace3文件26,881,586,080字节，354,638记录，150,698有效、203,940跳过（57.51%）；指定10模型×appid共111,541有效请求，两大Qwen54,602与52,098，小8个合计4,841。CSV字节不是某appid的raw_body字节。不能用这些旧计数替代本次实际扫描。

先全量流式做低成本清点，再决定小样本结构检查的预算，最后才提出正式全量诊断预算。本任务没有新的全量诊断授权。

1. **文件层**：3 Trace+18 MA逐个给完整SHA256、字节、表头、CSV逻辑行数、时间窗、模型/规格/APPID/UUID分布；行数与原报告对照。Trace与MA单列表。跳过原因给互斥主因与可重叠次因、按模型×appid分布，确认`.5`只是某种原因还是确实覆盖全部拒绝。对无法解码/归属行保留未知桶，计数守恒，不静默扔掉。
2. **范围层**：Trace全部appid只做清点/粗粒度分布；深度启发式仅下列已指定10个model×appid。列原CSV候选数、严格有效数、已有monitoring/index数、实际task选择数及差异；原文UTF-8总字节、单条P50/P90/P95/P99/max，已有J/P/C统计与适用模型，读取来源/分母。分位数注明精确或近似算法、样本数/误差；max是否全扫单独说明。
3. **结构层**：消息数/角色/文本或多模态形态、tools/functions定义与Schema节点、tool_calls/arguments/result、内嵌JSON解码层数和深度、提取units、重复候选/规范化字节、模板/结构族大小。已有探测器适配失败、不适用、未检查分开。先取可复现分层样本（模型/appid/长度/深度/消息和工具形态），包含长尾及真实负例，记录种子、来源行和排除原因。重结构提取不盲扫全部超长请求。
4. **规则/工作量层**：每L1–L5/T2–T4已检查请求、候选/比较、有效适用数、发现数、独立请求数、保留证据数、预算截断位置/原因。低命中前序K候选某通道上界为Σ_gΣ_i min(i−1,K)，不同通道分别算；指纹族不等于会话，检查32上限与1MiB单pair的截断。Token比较预算是单请求候选规范化字节累积，不同于低命中两正文之和。
5. **扩展层**：实际Proposal/RecommendationBudget及快照配置；proposal数、prepared operations、plan单份/总字节、评估数、证据字节等，不能只核主任务source/encoding预算。空recipe仍可能重复提取，须量测而非假设无成本。
6. **性能/存储层**：先读既有日志可确认的阶段时间；缺计时标未知，不能靠mtime拼精确profile。获本任务启动后，可在独立研究进程做少量已冻结真实请求的只读解析/提取/候选微测，先登记最大样本、墙钟时间、CPU/内存/输出上限，触顶即停；不提交产品任务、不运行外部模型调用、不更改缓存/源state。记录读取、解析、提取、对照、序列化/写研究结果分别耗时、峰值RSS、CPU、I/O；Token静态处理encoding_calls=0不代表没有CPU成本。不同请求族测量不得只按N线性外推。
7. **资源层**：复查容器8CPU/32GiB、tmpfs512MiB及当前磁盘/inode余量、现有state/SQLite/fragment/token shard/报告大小和增长；主机40CPU不意味着可独占。未来新state/旧state同时保留的磁盘需求应计入，预留量有依据且不自动扩容。

调查范围（模型名称以实际source model_id与alias同时记录）：

| 模型 | APPID | 原报告N | 后续原用户范围 |
| --- | --- | ---: | --- |
| DeepSeek | S00000000000000000000000000000773 | 1047 | 两方向 |
| DeepSeek | S010320 | 1038 | 两方向 |
| DeepSeek | com.huawei.ipd.tianzhou.ai | 864 | 两方向 |
| DeepSeek | com.huawei.mbs.ilegal.ioc | 661 | 两方向 |
| DeepSeek | com.huawei.newalliance | 104 | 两方向 |
| Qwen | app_000000030502 | 905 | 两方向 |
| Qwen | com.huawei.aidp_dg06 | 171 | 两方向 |
| Qwen | com.huawei.meca.admin.digital | 51 | 两方向 |
| Qwen | S00000000000000000000000000000773 | 54602 | 仅low_hit |
| Qwen | S00000000000000000000000000001679 | 52098 | 仅low_hit |

本表不是重新启动任务指令。两大Qwen可以读取旧任务已有Token结果以说明之前多执行的成本，但不能新增T2–T4扫描或评估；通用消息/工具结构清点用于量级与low_hit研究须与Token诊断分开。现接口强制Token，未来若仍不支持low_hit-only，应说明并等待能力修复，不能再次扩大用户选择。

必须输出逐model×appid的预算表，每行至少：`实际量/测量方法 → 当前冻结上限 → 已知覆盖/超限概率或确定超限 → 具体停止点 → 建议预算/候选策略/分批方式 → 时间/内存/磁盘区间和假设 → 未知/需要决定项`。max_findings=100已令十个任务partial且可能仅检查少数请求，不能以“100条结果”宣称足够。建议区分扫描完整度与证据保留；不要把全部限额乘10，也不要因为调大上限就保证完成。

若建议抽样/分段，明确覆盖清单、采样偏差、可恢复边界和跨段候选缺口；正式收益必须保留原顺序统一回放或证明缓存状态延续等价，不能把独立窗口收益相加。全量上界无法估计时明确暂不建议运行并列最小补测。

### D. 启发式研究：从真实tools/messages证据选择探测器

“Qwen/DeepSeek不是典型agentic infra”是待验证的工作负载判断，不按模型名称直接分类。按appid×模板族记录单轮/多消息、显式调用协议、普通消息内工具样式文本/检索内容、真实可用关联ID；没有会话关联证据就不能宣称历史被改写、重试或agent loop。

当前L1仅特定动态模式和system/developer字符串；L3动态范围偏工具description；L4是消息差异事实，needs_association时不是动态字段诊断；T3要求重复组至少有tool_result，T1已退出。以下仅作研究候选，不能自动增加规则或恢复T1：

- 工具定义/Schema负担与同工具变体：区分合法版本/权限变化，不因未看到调用就删除工具。
- 消息模板混杂、稳定前缀与变量位置：先分真实业务族再比较，不把不同业务输入判异常。
- 普通message内非重叠重复文档/内容：区别正常引用、few-shot和每次请求携带历史，说明现T3遗漏。
- 普通消息内结构化上下文/检索片段负担：文本大不是可删除证据，也不是已证实tool返回。
- 更广运行元数据/动态ID模式：业务必需ID为负例，不能泛化为正则删除或将L4改名L1。
- JSON/转义/重复序列化表示开销：现L5范围之外另证明适用性，不默认重序列化等价。

每个候选提供：真实最小正例与相似合法负例、来源文件SHA/记录号/任务范围、现探测器结果与遗漏原因、可观察量与分母、抽样/人工复核方法、误报风险、扫描/存储成本、后续所需业务语义和收益验证。不用最先保留的100条finding作为唯一研究样本；探索样本与留出验证样本分离。没有标注就不编准确率、没有全扫就不编全量覆盖率。

原始内容只嵌能解释问题的最小必要片段，保留消息role/结构/类型和脱敏说明，敏感值用稳定代号；不要上传完整CSV或凭据。脱敏文本不能冒充精确Tokenizer/LCP/收益测量输入。不得将真实数据发送外部模型服务；报告聚焦本地结构与已有结果。

此阶段不修改业务内容、recipe、不执行删减/改写方案或重新编码收益实验。哪些候选进入设计、哪些需新证据，由用户审阅本报告后决定。

### E. 唯一回传Markdown格式与退出标准

建议正文依序包含：

1. 实际日期、操作者session ID（未知就写未知）、授权范围/未做事项、源/镜像/API/资源身份。
2. 三项页面问题逐条结论：复现入口、步骤、请求响应和DOM文字、源码依据、根因已证实/假设/未知、修复建议、必要复测；不得写“API正常所以页面通过”。
3. 21文件全SHA/字节/表头与计数；Trace有效性审计；MA全部UUID四指标矩阵及最小真实原值证据。
4. 10范围量级、所有相关预算和资源表，既有任务每规则覆盖与截断、性能剖析，建议值/区间及前提。
5. 工作负载分类与探测器候选正反例、现规则覆盖/遗漏、成本与验证建议。
6. 按模块归口的修复优先级、用户待决定项、未决/不可证明事项，以及后续最小复测标准。
7. 直接嵌入支持关键结论的可执行命令、统计脚本关键源码/SQL、输入片段/精确响应/日志及退出码；每段指明实际执行还是建议。前后源码/配置摘要证明只读范围，说明是否发生任何意外修改及恢复情况，不能隐瞒。

本次没有修复则明确“未修改，尚无修复后结果”；不要填写虚假的修复diff或通过结论。后续获授权修复时需在相应回传文档中补容器内原bug复现、改法/完整关键diff、重建方式、前后同输入结果与风险，但本任务不提前执行。

输出只这一份md，关键证据不能只给现场绝对路径或SHA而缺内容。所有现存原件继续现场保留；报告可列其索引用于追溯，但不依赖附件才能判读。将已证明事实、推测、建议与用户验收分别标注，由用户决定下一步。

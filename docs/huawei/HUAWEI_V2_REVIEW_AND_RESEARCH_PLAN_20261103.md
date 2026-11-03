# 华为V2回传核对、修复与启发式研究方案

2026-11-03。角色：镜像打包与审查／完整服务总负责；实际session ID为`01a1800e-80b4-7400-a78b-a84f5b6e888d`，本轮环境THREAD/SESSION ID一致核实。

本轮只读报告、相关源码/契约并提出方案、更新记忆。没有修改产品/测试/构建代码、冻结契约或原报告，没有启动服务/复测/现场任务、发送会话消息、提交/push或打包。本方案不构成后续实现授权。

## 1. 当前结论和证据身份

用户2026-11-03明确：第二次验收也不通过；怀疑Qwen、DeepSeek工作负载不属于典型agentic infra，问题可能更集中在tools/messages，要求启发式研究；追加要求先调研待分析数据量级，防止预算不足。第一阶段用户监控和第二阶段异常分析均不能标为验收通过。用户进一步明确MA缺四项指标：DeepSeek-V4-Flash全部UUID、GLM-V5.2部分UUID；这是待闭环问题，不能再以API/任务完成或“未指出问题”记MA通过。TTFT真实参数仍缺失。

本轮最新用户反馈另确认两项端到端问题：V1同一入口能查看某用户使用的所有模型，V2一个URL似乎只显示某个模型；异常页完全没有结果，而后台显示分析完成。前者按多模型访问能力回归处理，不以发送三个URL或要求手填run ID作修复；后者按任务状态→发布→发现→读取→展示逐层核实，不把“后台结束”当页面闭环。本文的“用户”沿现有产品租户APPID范围核对，不擅改为跨appid的userhash聚合。

原件：[HUAWEI_V2_ACCEPTANCE_REPORT.md](HUAWEI_V2_ACCEPTANCE_REPORT.md)，50,443 bytes，SHA256 `93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e`，原位保留、未改写。本文对原件的勘误和推断不回填原报告。

报告声明现场固定源码`b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af`、镜像`sha256:a38d0ab2cfe26154c96adb5e876538893005e5cb100fc5c53640823c391683a8`，四个HTTP资源摘要与[已交付版本](../tasks/delivery/V2_APPROVED_DELIVERY_20261102.md)一致。本机当前HEAD为`7cbe28621f4e46083bf47f9aa14b011b3cb250c4`，其后续为文档收口。这里核对的是回传材料和本机源码，未登录华为复现，不能把材料陈述冒称独立现场实测。

## 2. 报告需要纠正的判断

| 报告说法/现象 | 本轮核对 | 对方案的影响 |
| --- | --- | --- |
| 用户页只显示Qwen，V1同一用户可切所有模型，V2似乎一URL一模型 | V1发布源码有全服务目录及同appid模型按钮；V2用户页只打开指定run、模型标签不可切换，最近记录是本地最多50条。报告服务端3模型77个appid×model目录仍存在 | 确认多模型访问能力回归；不是已证明的数据被删，也不只是缓存容量问题；修复目标是同一入口内发现/切换，非分发多个URL |
| report.items为空导致前端无卡片，应直接接/items/finding | 源码loadReport同时读report、recommendation-summary；再读recommendations和difference-groups。report本身是阶段摘要，不负责内嵌全部结果 | 此根因不成立，不能照抄为前端修复指令；先补真实请求链和明确历史task的复现 |
| 97条L4证明动态字段异常 | L4示例明确evidence_status=needs_association、association_ref=null；仅证明所比请求消息内容不同 | 不能等同L1、历史被错误改写、浪费或可恢复缓存收益；97是finding数，不是97个独立请求 |
| L1/L2/L5为0，意味着没有问题 | 示例dynamic覆盖只有checked_requests=3、comparisons=4，FINDING_BUDGET_EXHAUSTED；100条上限已满 | 只能说已保存发现中没有相应项。各规则需单独覆盖/适用性，不把未检查当零 |
| 10/10完成 | 10个任务均partial；Token fragment个数等于请求数也不证明每个fragment内T2/T3/T4完成 | 分开记终态、请求遍历、规则完成、建议评估、用户验收 |
| 两大appid“只low_hit”但实际执行Token是契约所致 | DiagnosticSelection强制enable_token_content=true；service._analyze无条件进Token；符合现有实现但不符合用户后续选择 | 这是产品能力/范围控制缺口；现场遇不支持应说明并停止该部分，不能把硬限制当作扩大执行授权 |
| 耗时按请求数线性，Qwen因block_size大所以快 | 51条约1540s与5万条约30–40min已否定单一请求数外推；Token静态提取/度量不调用编码器，encoding_calls=0不是总CPU工作为0 | 需阶段/单请求剖析；“长深/大块导致”均尚缺实证，10–12小时旧估计不能继续用 |
| MA completed，real=0因无实测观测 | 用户明确DeepSeek全UUID、GLM部分UUID四指标缺失；CSV含真实Token列，报告没有逐字段/逐UUID证据。主表配对理想与详情独立理想不是同一集合 | 新增HV2-08/P0；不能将缺数统归前端或缺原始观测，也不能用独立理想偷换配对理想 |
| 跳过行都由前导点数字引起且与产品无关 | `.5`示例可解释一类拒绝，报告未给完整错误分布；拒绝率很高 | 保持严格解析，先查数据来源/导出格式与拒绝原因，再讨论有依据的派生修正；不可忽略代表性 |

另有证据缺口：MA18文件只列摘要前16位且未逐文件列字节；MA real=0不能仅凭一个实例证明所有文件无观测（表头含prompt_tokens/cached_tokens）；缺完整10个task_id、recommendation-summary/difference-groups实际响应和浏览器网络/错误；Token规则结果仍写“见items”，不满足单文档可独立复核。报告内curl/SSH部分被转换为Markdown链接，不能原样当命令执行。补证据仍只回传一份自包含Markdown，不要求额外附件。

## 3. 源码依据与最可能的故障链

### 3.1 用户运行发现

[UserMonitor.tsx](../../apps/viewer/src/features/v2/UserMonitor.tsx)的open/follow及初始化使用指定run或本机记录；[v2-records.ts](../../apps/viewer/src/storage/v2-records.ts)的remember保留本浏览器最近50条。[api/user.py](../../src/tokenscope/api/user.py)提供提交/绑定、单个运行回执和排行等接口，但没有已发布用户运行全目录GET。[用户Store](../../src/tokenscope/user_monitoring/storage.py)已有runs、base_id、model_id、common_name、state、revision可供受控只读投影。

对V1发布commit `92236ee993974e740d085e22e49b6b93c9487430`只读核对，`apps/viewer/src/app.tsx:70`确有`catalog.items.filter(i => i.appid === state.selection?.appid)`生成模型切换按钮；[catalog.ts](../../apps/viewer/src/state/catalog.ts)分页取`/monitoring/catalog`的全服务appid×model目录。V2交付commit中该V1组件仍保留，但正式用户入口走UserMonitor，其模型区域为common_name/model_id静态文本，仅APPID能在当前run内选择。因此这是访问能力回归，有源码证据，不是要求用户接受的新设计。V1并非将所有模型Token合并为一个指标，需恢复的是同一用户入口内的完整模型可见性与逐模型切换。

建议用户后端与监控前端共同补服务端已发布用户运行/模型映射目录，在批准的模型服务/运行选择区域消费。用户选定APPID后，应列出该APPID的所有已发布模型/服务及对应历史运行；切换时保持APPID、显示对应数据窗，URL可记录当前选择供分享，但不得将链接里的run变成全目录过滤条件。保留新加入的搜索/排行、TTFT及源身份，不能简单退回V1页面丢失V2功能。localStorage仅作最近记录/偏好；不新建第五入口，不要求用户复制run ID找回模型，不拿S0 base_run_id冒充user_run_id，也不通过POST binding/重算来做目录GET。增加契约时明确身份、稳定分页/目录快照、状态、模型/common_name、user/base/index revision映射及旧客户端兼容。

### 3.2 全partial情况下“无默认报告”是优先核查项

[discovery.py](../../src/tokenscope/analysis_common/discovery.py)的default_eligible与defaults仅选择ready；[AnalysisApp.tsx](../../apps/viewer/src/features/analysis/AnalysisApp.tsx)以route.task或defaultTask定位target，没有target就不loadReport，显示“当前没有默认完整报告，请选择历史报告”。报告10个任务全部partial，因此新浏览器直接进入#/analysis可能落在此分支。这是有源码依据的高优先级假设，尚不能代替现场URL/目录/网络复现。

先对同一完整task_id分别验证裸入口、显式历史链接及手动选择历史报告。记录catalog defaults、summary availability/counts、difference-groups、两方向recommendations、examples及错误。

- 若显式历史可显示L4：修复历史/partial入口说明和可发现性，保持partial不替换ready默认的既定语义。
- 若summary有分组但页面失败：按具体Schema/身份/计数/网络错误修前端消费，不绕过校验。
- 若finding有L4而扩展分组缺失：查recommendations快照/扩展阶段异常及publication结果，归公共后端；不要用原始finding直接填业务卡片。
- L1–L3优化卡仍需完整评估严格>1pp；L4/L5事实卡不依赖该收益门槛。[model.ts](../../apps/viewer/src/features/analysis/model.ts)、[recommendations.ts](../../apps/viewer/src/api/analysis/recommendations.ts)、[recommendation_publication.py](../../src/tokenscope/analysis_common/recommendation_publication.py)已实现该区分。不得降低门槛制造L1卡。
- 默认空recipe会没有Token优化建议；原始fragment事实、无规则适用、未配置依据、技术未完成必须区分。是否在现有区域增加只读事实摘要由对应前后端提出最小展示调整，不恢复T1或重设计界面。

### 3.3 当前探测范围与预算导致的盲区

[dynamic.py](../../src/tokenscope/prefix_analysis/dynamic.py)仅识别日期时间、路径和特定billing-header；L1只扫描system/developer的字符串，L3动态方案只针对工具description。不能覆盖任意ID、消息角色/协议形式或模板变化。

[detection.py](../../src/tokenscope/prefix_analysis/detection.py)按编码身份/effective_options/前两个消息角色召回最多candidate_limit条前序请求；该指纹不能证明同一业务模板或会话。逐对列出L1/L3，再列L4/L5，每条差异调用共享control.finding；100条可能被几对消息差异耗尽并停止后续扫描。[CandidateIndex](../../src/tokenscope/prefix_analysis/candidates.py)候选超上限本身也会标partial：单纯增加max_findings不一定产生ready，更不能靠去掉partial标志解决。

[CurrentTokenContentPlugin](../../src/tokenscope/token_content/current_plugin.py)仅T2–T4；[extraction.py](../../src/tokenscope/token_content/extraction.py)解析明确tool/function、工具调用arguments、user/assistant等内容，system/developer没有同样的普通message_payload提取；工具定义子树也计入max_units，即使当前不启用T1。[duplicates.py](../../src/tokenscope/token_content/duplicates.py)的T3要求重复组至少含一个tool_result，不覆盖所有普通消息重复。用户所说tools/messages问题，应先核对这些适配/召回缺口，而非假定现有规则已完整覆盖。

性能方面，[auto_proposals.py](../../src/tokenscope/token_content/auto_proposals.py)在遍历bundle.recipes前再次extract，即使空recipe也会发生提取；[recommendation_engine.py](../../src/tokenscope/analysis_common/recommendation_engine.py)逐fragment读取/验证，发现不完整fragment可终止建议扫描。这是应测量的重复工作/停止点，不是已经证实的现场耗时占比。

### 3.4 MA四指标缺失：先分清字段、集合和展示

用户报告的受影响范围：DeepSeek-V4-Flash全部UUID、GLM-V5.2部分UUID，缺理想命中率、真实命中率、整小时重算Token/s、实际重算Token。尚未取得完整规格×UUID清单和对应页面/API；Qwen没有被用户报告异常，仍需作为对照核对，不能宣称它已全部通过。

[ingest.py](../../src/tokenscope/monitoring/ma/ingest.py)和[statistics.py](../../src/tokenscope/monitoring/ma/statistics.py)明确：

- A为可归属记录；P为生产prompt合法；R要求prompt及cached均合法且cached≤prompt；E为成功本地编码/理想回放；Q=R∩E。completion_tokens缺失或request_input非法JSON不会单独剔除已满足条件的R。不能把大批INVALID_JSON直接解释成real=0。
- Token解析只接受非负十进制整数字符串，区分MISSING_TOKEN_VALUE、INVALID_TOKEN_INTEGER、TOKEN_OVERFLOW、CACHE_EXCEEDS_INPUT。若CSV中是空串、`NULL`、`123.0`、负数或超界，行为不同；目前未取得这些真实原值，不推断其存在。先核数据生产语义，不能笼统float→int、补0或放宽校验。
- [MAMonitor.tsx](../../apps/viewer/src/features/v2/MAMonitor.tsx)主表使用`paired_ideal.hit_rate`、`paired_real.hit_rate`；[MACharts.tsx](../../apps/viewer/src/features/v2/MACharts.tsx)“独立指标、覆盖与运行条件”详情使用`ideal.hit_rate`、`real.hit_rate`。无R→无Q→两配对率为null；并不等于E上的独立理想不存在。
- 实际重算量在R上求Σ(prompt−cached)，整小时速率除3600。有A但R=0时速率为null，主表重算量显示“—”；有效cached=0应该是有效数据，prompt>0时真实命中率0，绝不能因0是假值就隐藏。全部prompt=0时分母为0的命中率仍应null，但有效重算量/压力可为0。
- [replay.py](../../src/tokenscope/monitoring/ma/replay.py)的预热顺序冲突会使理想回放不可用，但不应影响R上的真实统计。无有效预热不等同无编码或无任何冷启动理想结果；需结合ideal_status和E/Q实际值解释。

报告给出的DeepSeek-32K运行`1bb5a14b-6356-44fc-80f4-08c15fc1255c`、UUID `0a5bf216-53d9-40ad-967f-49365bcd1c20`：A=740、P=730、R=0、E=345、Q=0，独立ideal.hit_rate=0.3597190553279913（约35.97%），ideal_status=available。按此源码，主表配对率与实际两项均可为空，独立理想详情应有值。这是一个可解释的实例链，不足以解释全部DeepSeek/部分GLM，更不能证明原始cached都缺失。原报告仅列少量质量示例，需取得完整field×code×UUID分布。

要求华为对9规格全部已发布UUID补矩阵：文件全SHA/字节、run/revision、UUID、A/P/R/E/Q、pre编码数、ideal_status、四个命中率（独立/配对各两）、实际重算总量/整小时速率、12桶有效数、页面对应文字。对DeepSeek全UUID和GLM缺数UUID列完整矩阵，选GLM正常UUID及Qwen作对照。

按证据决定最小修复：原CSV缺观测则补采/修生产导出；合法原值被错解析则修有依据的适配并加真实样本回归；存储正确而聚合错则修后端；API有值而DOM无值则修前端；仅Q缺失而E有效则在批准既有详情/提示内讲清独立结果与配对不可用原因。不能以理想值补真实值、以独立值填配对列、以null填0或用本地模拟生产prompt冒充实测。未明确根因的UUID保持未决。

## 4. 拟修复工作及复测标准（尚未实施）

| 编号/优先级 | 归口与拟动作 | 退出标准 |
| --- | --- | --- |
| HV2-01 / P0 | 用户后端＋监控前端：服务端运行发现与批准模型选择区域打通 | 全新浏览器打开同一个用户监控入口，即可看到所选APPID的全部可用模型并切换（覆盖真实三模型数据及仅单模型APPID）；不需手输ID/另换URL；模型×appid/索引身份准确；刷新、失败、分页、历史、导出不串范围；GET无计算 |
| HV2-02 / P0 | 异常前端＋公共后端：先补完整真实任务读取链，再修partial历史入口/实际读取或发布故障 | 全partial无ready、ready+新partial、显式历史task三场景可解释；L4/L5各一张卡且最多3例；收益门槛/原身份校验保持 |
| HV2-03 / P0 | 公共后端：显式执行方向能力，兼容历史任务与旧请求 | 新版本选low_hit-only时无Token遍历/提取/建议阶段；token-only不跑L；双方向保持；回执/capabilities/目录/幂等/重试均按真实方向；不支持则提交前明示 |
| HV2-04 / P0 | 公共＋低命中后端：区分扫描、候选召回、证据保留和评估预算，避免L4耗尽全部检测机会 | 高L4密度及尾部真实异常场景中各规则覆盖可知；计数去重，抽样/截断不伪装全量；无法穷尽就保留partial及原因，GET仍只读 |
| HV2-05 / P1 | Token后端＋公共后端：基于剖析消除空recipe重复提取、重复解析/序列化/读源等已证实热点，再考虑有界并发/增量 | 同真实范围、同资源及规则比较前后分阶段时间/峰值RSS/I/O；结果身份、完整度、取消、恢复、负收益不变；未测不承诺倍率 |
| HV2-06 / P0调研前置 | 用户监控归口＋现场agent：拒绝数据审计、全量级统计、预算建议；数据生产侧补证据 | 所有行计数守恒，拒绝原因/模型appid偏差可查；不静默修原CSV、不用合成数据补覆盖；任何派生修正另获授权并保留映射 |
| HV2-07 / 参数待提供 | 用户监控：真实TTFT情景参数及来源 | T/W/K/τ齐备后按真实P90验证；不默填W=0、不把硬件型号当校准 |
| HV2-08 / P0 | MA后端＋监控前端：逐规格/UUID追踪四项缺数，补原始字段→A/P/R/E/Q→API→DOM证据后按层修复 | DeepSeek全部、GLM部分受影响UUID逐项有根因/结果；正常UUID对照不回退；独立/配对不混用，0/null/缺观测可分，实际总量与12桶/3600秒守恒，JSON坏行不误伤独立真实统计；用户现场复验 |
| HV2-R / 研究 | 低命中/公共与Token维护方消费现场启发式材料，再提规则改动 | 有正反例、未覆盖量级、成本和误报依据；新增探测器/恢复历史规则先形成设计供用户决定 |

HV2-03涉及当前强制路由设计，需版本化能力/Schema/实现一起评审，不只删一个validator；旧task、老报告不得重解释。本轮不擅改冻结契约，也不继续执行用户未选的方向。UIR-03仍留V3，本方案不借机启动全局路由重构。

## 5. 华为真实数据量级调研：深度分析前必须完成

报告可计算的基线（来自报告、尚未独立现场复算）：

| 模型 | CSV记录 | 有效 | 跳过 | 跳过比例 |
| --- | ---: | ---: | ---: | ---: |
| DeepSeek | 36,222 | 19,186 | 17,036 | 47.03% |
| GLM | 26,505 | 12,446 | 14,059 | 53.04% |
| Qwen | 291,911 | 119,066 | 172,845 | 59.21% |
| 合计 | 354,638 | 150,698 | 203,940 | 57.51% |

3个CSV共26,881,586,080字节（文件大小，不是单appid解码正文预算）。指定10个模型×appid的报告请求数合计111,541，其中两大Qwen为54,602和52,098，小8个合计4,841。大文件、长单请求、深结构、多对照、高证据输出是不同资源维度；不能只按请求数分“大/小”。

MA18CSV另做规格×pre/now×UUID量级表和HV2-08四指标矩阵，不能沿用Trace字段/拒绝口径，也不混入两类异常的Trace输入。

华为需对每个模型×appid输出：原CSV/有效监控/实际诊断三层计数、原文总UTF-8字节及单条P50/P90/P95/P99/max、已有J/P/C分位数、root/内嵌JSON深度、消息角色/数量/内容形态、工具定义/Schema节点/调用/返回、提取units分位数、重复/结构族数量、预计候选对/比较字节、各规则扫描/发现/保留/截断比例、既有state/SQLite/fragment/证据文件体积与数量、各阶段耗时/峰值RSS/CPU/I/O。标清完整扫描、抽样估计及未知，不以CSV行数推断JSON深度/提取单位。

| 预算层 | 当前现场值/代码口径 | 必须核对的实际量 |
| --- | --- | --- |
| 任务输入 | max_source_requests=100000、max_source_bytes=5GiB；_preflight硬拒绝，不是抽样 | 目标冻结范围N及解码raw_body UTF-8总字节，含必要重扫I/O |
| 单请求 | max_request_bytes=1MiB、max_depth=32、max_units=256 | 最大正文、外层/内嵌深度、全部被提取节点（含tool definition子树）的units；P99不能替代max保证全覆盖 |
| 低命中对照 | candidate_limit=32（当前Schema上限128）；max_comparison_bytes=1MiB按两条正文之和检查 | 每个结构族的前序候选量、截断比例和pair字节；两条均<1MiB仍可能合计超限 |
| Token比较 | 同名max_comparison_bytes在T3为单请求候选规范化内容的累计字节 | 不是低命中单pair口径；父子/内嵌展开会使其不同于原文大小 |
| 发现与实验 | max_findings=100全任务累计；max_experiments=20、max_combinations=10、pilot_limit=4 | 差异密度、规则竞争、方案数、实际pilot/full范围；展示最多3例不等于仅分析3条 |
| 编码/方案 | 任务与插件的max_encoding_calls分层；任务max_plan_bytes默认16MiB | 原结果IDs读取、静态提取与重新编码耗时分开；plan实际字节/操作数 |
| 建议扩展 | 独立RecommendationBudget：默认proposals256、recommendations32、prepared_operations10000、proposal1MiB、plan16MiB、total_plan64MiB、token_evaluations8、每组证据24KiB | 读取现场冻结snapshot实际值，不把这些默认当已核实配置；5万请求逐请求proposal/操作可先触顶，与max_source_requests无关 |
| 宿主/容器 | 报告8CPU/32GiB、tmpfs512MiB、/home余271GiB | 重测配额、RSS、I/O、输出增长、磁盘/inode；不可因主机40CPU自动提高共享预算 |

预算回执每行需“实际量级→当前上限→已覆盖比例→瓶颈/停止点→建议值或分批/抽样方式→时间/内存/磁盘区间→保留余量及依据”。固定范围已知N/字节可精确算；未知长尾用分层样本测成本，给区间，不能保证绝不耗尽。不能简单将全部上限乘10，也不能把调大预算写成修复。

按某候选通道的结构族大小n_g和前序上限K，比较次数上界可估为Σ_g Σ_{i=1..n_g} min(i−1,K)，再分别计L2与dynamic通道；真实提前停止、不同指纹和重复读源另记。把粗指纹当“同会话”无效。若正式任务必须分段，需定义覆盖清单与恢复游标；抽样不能报告全量，独立窗口的缓存收益也不能直接相加，正式收益仍需原顺序/原范围统一回放或证明等价的缓存状态延续。

## 6. 启发式研究方向：先认识数据，再选择探测器

认可先研究真实tools/messages的方向，但“Qwen/DeepSeek不是典型Agent场景”仍是工作负载假设，不能按模型品牌定场景。按appid×模型×实际模板族观察单轮/多消息、显式tool协议、普通消息内结构化上下文、工具调用结果关联和既有session证据；没有关联则只描述快照，不能推断agent loop、重试或历史被改写。

以下为研究候选，不是新L/T编号或已批准功能：

| 候选 | 现场需要的证据 | 防误报/与既有实现关系 |
| --- | --- | --- |
| 工具定义/Schema负担与变体 | 同工具身份的定义/描述/Schema差异、出现频率、模板参与、稳定前缀差异 | 先扩展L3事实；工具不同可能是合法版本/权限变化。T1已退出，不能自动恢复，更不能因没看到调用删工具 |
| 消息模板族混杂/稳定前缀差异 | 同appid内system/developer/user结构族、固定文本与业务变量的位置、跨族/族内对照及已有IDs | 请求业务不同是负例；先分族再比较，位置差异不直接等于浪费 |
| 非工具消息重复内容/文档重复携带 | 同请求中确切非重叠重复片段、位置、容器关系、上下文 | 现T3要求tool_result；通用message重复须新设计，不把正常引用、few-shot或跨请求历史重发当异常 |
| 消息内结构化上下文/检索片段负担 | user/assistant内JSON/数组/表格/转义文本的结构、大小、重复及来源证明 | 不把普通文本伪装成真实tool返回；内容大不等于可删除，需要业务保留依据 |
| 更广动态字段/运行元数据 | 真实ID/时间/版本等变化片段、相邻稳定内容、影响IDs的位置、是否业务必需 | 现L1模式窄，可研究扩展；不靠通用正则批量删除ID，不把L4自动改名L1 |
| JSON表示/序列化膨胀 | 解码结构与数字词法、转义层数、空白和真实模板输入差异 | L5当前限tool消息；其他位置需单独证明适用性，不假定重序列化语义和缓存收益无损 |

每个候选必须给最小真实正例、近似但合法的负例、适用/未适用/未检查分母、对现L1–L5/T2–T4的重叠/遗漏、误报/漏报的人工复核记录、统计与扫描成本。只有实际做过标注/全量检查才报准确率/覆盖率；发现数据集与保留验证样本分开，避免只用最初100条findings评价探测器。

优化机会事实与“允许修改/语义安全/可量化收益”分开。研究阶段默认不删内容、不改业务recipe、不伪造verified、不重算整套用户监控。后续离线副本实验需要确切方案和用户同意，统一模型/编码/缓存实现计算P/H/C，保留零/负收益及P降C升，不拿字段字节或LCP替代可节约Token。

## 7. 建议推进顺序与交接

1. 本轮完成报告核对/方案/记忆，保留原报告及交付身份；当前没有代码修复或研究执行。
2. 下一轮先由华为补读取链和量级/预算/拒绝原因，按[只读调研任务书草案](HUAWEI_V2_HEURISTIC_RESEARCH_BRIEF_20261103.md)形成一个自包含回传文档。先补三项页面问题的只读读取链（多模型/异常空白/MA缺数）并做已有结果与流式统计，再做有预算的真实样本启发式/性能剖析，不能直接再次全量跑两方向。
3. 据证据确定HV2-01/02/08最小闭环修复，公共维护方设计HV2-03方向与HV2-04预算/覆盖口径；Token维护方按实际profile处理HV2-05。各session职责不变，本轮未唤醒或下发任务。
4. 真实场景研究候选先由用户选择，再实现所选探测器；不把调研当自动恢复T1、hybrid或自进化Agent授权。
5. 获实施安排后，本机用经授权的最小脱敏真实回归样本验证，再由审查方从停旧服务/新空state/新浏览器独立复审。新镜像/包仍等用户打包授权；现场两次用户验收分别记录，若用户明确改变顺序按最新决定执行。

本次后续授权分析10个appid是用户在第一阶段不通过后明确追加的指令，不应被误判为agent自行跳过第一阶段；但其中“只low_hit”的进一步缩小范围必须遵守。新的研究阶段也不能扩大到未选appid的深度诊断。

本轮保全/来源检查在`artifacts/reviews/huawei-v2-report-review-20261103/`。文档入口与本线记忆更新，但旧交付包、原始证据、其他session修改不动；没有把该方案标为已修复或已验收。

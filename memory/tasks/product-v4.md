# V4产品设计与汇报记忆

2026-11-13本人接收：用户启动V4产品设计与汇报。实际session ID `01a1d3e3-0c34-7320-bf6f-14438c120aed`，从本人Windows环境`CODEX_SESSION_ID`与`CODEX_THREAD_ID`核实且一致；不继承V3或镜像会话身份。此前“待启动/ID未知”为镜像线准备登记，现由本人更新。

入口：[V4](../../docs/tasks/v4/ENTRY.md)；启动：[产品prompt](../../docs/tasks/v4/START_PRODUCT.md)。用户已通过V3验收；两个V3角色休眠。V4核心汇报与模型演进，Token新规则留候选。本线负责产品定位、汇报稿/演示、必要最小差异DEMO和需求验收，不写产品代码/代开发测试。前端变化先获用户“前端展示审批通过”。仅启动需求方案，无现场/编码/打包/push授权。

## 11月15日最新：两研究fork与主会话审核分工

用户明确授权主会话fork两次、准备三份启动prompt、登记身份与任务、更新记忆并做一次Git提交。主会话继续汇报方案，负责审核两线最终文档、判断融入V4汇报并正式提交；不再独自包办两条研究线。本人SESSION/THREAD与应用“整理TokenScope V4汇报方案”均核实为`01a1d3e3-0c34-7320-bf6f-14438c120aed`。

已用fork_thread从本主会话同目录fork两次，并用read_thread核对标题／ID／cwd与idle状态：

| 角色／应用实际标题 | 实际ID | 启动与任务 |
| --- | --- | --- |
| 副本1“TokenScope V4现网流量研究” | `01a1de7c-8ea4-7cb2-b8e6-114aeba29a60` | [启动prompt](../../docs/tasks/product-v4/sessions/START_TRAFFIC_20261115.md) · [ENTRY](../../docs/tasks/product-v4/traffic/ENTRY.md)：研究现网现状／证据，用户长低→短低→长高长尾三阶段协作、节点与有证据效果，最终独立HTML |
| 副本2“TokenScope V4 MaaS架构与试点” | `01a1de7c-a6fd-7043-baa7-987f03d5af3c` | [启动prompt](../../docs/tasks/product-v4/sessions/START_MAAS_20261115.md) · [ENTRY](../../docs/tasks/product-v4/maas/ENTRY.md)：先两DeepSeek appid简单试点设计，获得初步结果后形成场景分类MaaS网关待同事粗评材料 |

[主启动prompt](../../docs/tasks/product-v4/sessions/START_MAIN_20261115.md)及[三线协作／文件所有权](../../docs/tasks/product-v4/SESSION_COLLABORATION_20261115.md)齐备。两fork没有自动发送启动消息或执行新研究turn；其最新interrupted turn是继承父历史，不代表任务失败或已自核。用户进入各fork后按对应prompt开始；不得重复父会话创建／Git任务。子ID是工具确认，待本人环境复核，不能写成副本已签收。

副本1维护traffic目录、流量研究正文与个人记忆；副本2维护maas目录、三架构／P2核对正文及个人记忆。主会话统一共享入口／CURRENT／SESSIONS、reviews及Git。默认共享HANDOFF与用户转交协作，无自动跨chat消息、额外fork／子agent／自动化；业务语义、节点、实验范围由用户决定，现场由用户转交prompt。主会话审核记录包含版本摘要、来源／限制、修改项及是否纳入汇报，不代签用户验收。

最新授权允许副本1制作新研究HTML，主会话继续整理汇报方案；不修改旧V3 HTML/PPT或产品页面。副本2先设计缓存集中／服务表现简单试点，不叠加多个长度物理池；prompt-3在用户讨论设计后制定，执行另按范围授权；未来架构粗评依赖初步结果，Tokenization／编码复用继续pending。资料优先级保持，两条研究正文高、原件／专题为重点支撑、P2为次高先行试点。

本次Git由主会话做一次本地文档检查点，纳入本线正式研究／图件、三prompt／分工／入口／记忆及证据身份清单；原始现场回传、MA画像、运行数据和包体保留本机，不push。提交前精确核对索引与文件范围，不全局reset/clean；实际提交SHA与检查记录留`artifacts/reviews/v4-fork-20261115/`，以Git提交结果为准。三线尚无新HTML、试点结果或架构粗评成品，不写已完成。

## 11月15日前轮：用户确认资料层级，长期入口已固化

本人实际SESSION/THREAD再次从环境核实为`01a1d3e3-0c34-7320-bf6f-14438c120aed`。用户已认可两份研究为高优先级，并修订前轮候选排序：**现网流量研究与三架构研究为长期核心正文，原始证据及指定专题是重点支撑，P2仅为次高优先级先行试点。** 本轮已据此固化，不再待同一项评审；下节“候选／待评审”是此前时点，不覆盖本决定。

固定导航：[产品ENTRY](../../docs/tasks/product-v4/ENTRY.md) → [资料层级／路由／内容分工](../../docs/tasks/product-v4/V4_REVIEW_PACKAGE_20261115.md) → 对应研究正文 → 直接链接的原证据与专题。清单沿用原文件名，标题及状态已更新为用户确认。阅读一般先理解自身业务，再看架构机制，按需追溯来源；具体试点另查P2，不把P2夹在两份长期正文之间作为必经入口。

| 层级与固定文档 | 包含内容与使用时机 |
| --- | --- |
| 高：[现网流量研究](../../docs/tasks/product-v4/PRODUCTION_TRAFFIC_STUDY_20261114.md) | 企业多业务入场、调用类型／服务需求、典型请求与复用、四象限占比、appid治理候选、全部短低输出索引；用于理解自身业务和优化依据 |
| 高：[三架构研究](../../docs/tasks/product-v4/INFERX_DEEPSEEK_MOONCAKE_ARCHITECTURE_COMPARISON_20261114.md) | InferX／DeepSeek／Mooncake三图，场景识别、选模、缓存亲和／负载、无共享KV热点及GB/GF/独立MA适用条件；§9保存分桶／Tokenization既有判断，供未来恢复讨论 |
| 次高：[P2核对与试点输入](../../docs/tasks/product-v4/HUAWEI_P2_REVIEW_AND_PILOT_INPUTS_20261115.md)及[P2原报告](../../docs/huawei/HUAWEI_V4_P2_MAAS_TRAFFIC_AND_FEASIBILITY.md) | 两DeepSeek appid的流量／负担、分母与配置身份核对、容量推断限制和设计输入；作为未来MaaS架构演进先锋队，不代表全部业务或整体架构 |

重点原始证据／基准直接路径：[四象限HTML](../../docs/tasks/product-v3/promotion/quadrant-detail/dist/index.html)（发现入口、对象与分布）、[MaaS现有架构](../../docs/architecture/MAAS_REFERENCE.md)（GB/GF/motor/MA与字段口径）、[P1阶段1](../../docs/huawei/HUAWEI_V4_P1_STAGE1_MIXED_SCENARIOS.md)（三个短低对象混合调用）、[阶段2](../../docs/huawei/HUAWEI_V4_P1_STAGE2_LONG_TAIL.md)（三个长高对象长尾）、[阶段3](../../docs/huawei/HUAWEI_V4_P1_STAGE3_OUTPUT_HISTOGRAMS.md)（22 appid／23组输出直方图）。这些是高优先级资料体系的重要组成，正文摘要不替代原件，资料层级认可不改变既有统计限制或等于能力验收。

重点专题直接路径：[主流MaaS调研](../../docs/tasks/product-v4/MAAS_ROUTING_RESEARCH_20261114.md)（广泛厂商分流实践）、[DeepSeek专项](../../docs/tasks/product-v4/DEEPSEEK_ROUTING_AND_SHARED_KV_20261114.md)（长度调度与共享KV）、[扩展企业架构研究](../../docs/tasks/product-v4/ENTERPRISE_MAAS_ARCHITECTURE_RESEARCH_20261114.md)（企业多场景／选模／亲和负载比较及前轮勘误）。它们是重点支撑，不仅是普通历史备查；仍区分公开技术资料与现场原始证据，旧阶段表述不驱动当前任务。

**[MA流量画像HTML](../../docs/huawei/MA_TRAFFIC_PROFILE.html)：高优先级证据，已接收。** 用户原同意先登记“路径待补”并要求提供位置；本轮随后检测到文件已到约定位置`/home/zhangxiyue/TokenScope/docs/huawei/MA_TRAFFIC_PROFILE.html`，已补两份正文及入口的实际链接。文件388,189字节，SHA256 `c182844ce71cda20eaebf44ec36bf49cee7d54dc82d3acb089b6600c38bd0167`；标题“MA 流量画像 · UUID 聚类与证据核验”，页面注明生成2026-11-10，Qwen-V3.6-27B 32K/64K/128K、2026-10-20 08:00–09:00 UTC，pre小时仅预热。仅核文件身份／页面声明范围，未研究聚类或复算CSV，不与DeepSeek试点／四象限分母合并。

MA画像引用的`../../engineering/MA_FLOW_FOR_SUPER_P90_READONLY_20261110.md`、`ANALYSIS.md`、`instance-features.csv`、`audit-data.json`在当前相对位置均缺失，详[接收记录](../../artifacts/reviews/v4-doc-review-20261115/ma-profile-receipt.json)。HTML内嵌原文SHA是其声明，不等于本机已取得原回传；不改原HTML、不用P2／原型替代、不标完整证据链已核验。

资料优先级与执行顺序分开：下一项仍先设计简单试点，验证缓存集中与服务表现，不叠加多个长度物理池；未来MaaS形态与Tokenization讨论继续pending，先观测自身性能变化位置，不先冻结长度池。用户不优先编码复用，粗估仅为以后软调度候选。本轮只固化文档和记忆，未开始试点设计、生成prompt-3、改HTML/PPT或产品、执行现场／服务、构建、提交／push。

文档本地核对沿用[检查记录](../../artifacts/reviews/v4-doc-review-20261115/document-check.json)，保护原报告、四象限HTML、MAAS_REFERENCE、原prompt、图件及新接收MA画像；MA文件身份另存接收记录。原数值仍在研究正文维护，记忆保留路由、内容分工、用户决定与pending。

## 11月15日前轮：资料整理与评审，简单试点优先

本人从Windows环境再次核实CODEX_SESSION_ID与CODEX_THREAD_ID均为`01a1d3e3-0c34-7320-bf6f-14438c120aed`。用户最新要求本轮先整理文档与记忆、梳理高优先级资料供评审；评审通过后再将路由／包含内容固化为未来V4与MaaS设计入口。**候选清单待评审，不能记作已批准的长期路由。**

已确认的顺序与判断：下一项优先简单试点实验设计，先验证缓存集中与服务表现，暂不叠加多个长度物理池；未来MaaS形态与Tokenization成本讨论均pending。未来先建立长度观测桶，观察计算耗时、KV占用、批次干扰或SLO变化位置，以自身真实业务证据优化，不先冻结8K／32K／64K／128K物理池。用户对GB代码／通信了解不足，当前不优先复用编码结果；这是可行性与优先级判断，不是技术不可能结论。“粗估用于软调度”保留为以后候选，也不本轮展开。

本轮产出[高优先级文档评审清单](../../docs/tasks/product-v4/V4_REVIEW_PACKAGE_20261115.md)，提出先业务证据、再试点输入、后架构参照，列每文用途／包含内容／评审点／证据边界及备查分工。新增[P2核对与试点设计输入](../../docs/tasks/product-v4/HUAWEI_P2_REVIEW_AND_PILOT_INPUTS_20261115.md)，将前轮仅在记忆的P2初审移到可引用正文；保留原报告值与分母，纠正容量、配置及实际命中推断，未知项不自动变新增现场任务。

既有[三架构研究](../../docs/tasks/product-v4/INFERX_DEEPSEEK_MOONCAKE_ARCHITECTURE_COMPARISON_20261114.md)更新过期阶段，§9保存DeepSeek分档／共享KV、InferX映射与选模、GDA边界及Tokenization前轮讨论和最新暂缓决定。[流量研究](../../docs/tasks/product-v4/PRODUCTION_TRAFFIC_STUDY_20261114.md)仅同步P2已回传及下一阶段，原统计口径／内容保持。较早广泛调研及r1/r2仅备查，不移动原路径或据旧“下一轮”恢复任务。

待用户评审的是文档优先级、内容分工与能否作为下一轮试点设计的共同资料；已确认的简单试点优先／未来讨论暂缓不重复请示。通过后按用户修订固化确认的路径、内容摘要、适用问题、证据索引与pending事项；记忆保导航和决定，数字与勘误由研究正文维护。当前仅记录整理完成与待评审状态，不提前冻结该导航。

本轮没有开始试点设计／执行或生成prompt-3，不修改V3 HTML/PPT、四份原prompt、现场回传、MAAS_REFERENCE或三张架构图，不写产品代码／代开发测试，不启动服务、委派会话、构建、提交或push。本地核对通过：12份文档／259处本地链接、表格及可见算术一致，21份受保护原件／图件摘要不变；流量研究23组附录及关键比例复核仍通过，git diff --check无错误。记录见[2026-11-15检查](../../artifacts/reviews/v4-doc-review-20261115/document-check.json)，仅文档核对，不是产品测试或生产复验。

## 11月14日探索prompt准备（历史阶段）

当时安排：先收集证据、整理资料；不修改V3华为风HTML/PPT，暂不思考汇报组织。用户预计未来主要改第四页，列方案、预期、协作对象及验收节点；待用户启动修改时再全面整理和讨论。当时不生成prompt-3、不执行现场工作。

当时交付：[本人ENTRY的四份独立Markdown](../../docs/tasks/product-v4/ENTRY.md)。prompt-1阶段1固定三个短低对象，查混合业务/规模；阶段2固定三长高长尾对象，分必要长任务/混合/工具候选；阶段3扩大到四象限全部短低appid，查输出长度及场景。MaaS prompt-2只查两DeepSeek appid独立/合计req/s，与32K/64K/128K规格及各UUID比较，结合现网0731实际配置/已有容量证据作初步判断；部署、数据整理、重放与采集prompt-3等回传后讨论。

第三阶段直接解析HTML `data-quadrant=sl`，固定SHA `8d76928147dd8a4f274fd0e160a916a493e7878d4ba14c7c339683877ba2a354`：22唯一appid、23组、124913条历史有效请求，DeepSeek/GLM/Qwen各7/2/14组。末3344 appid跨GLM/Qwen，在一份Markdown内分模型章节；共22份报告（最新用户要求覆盖旧单Markdown通则）。[提取清单](../../artifacts/reviews/v4-prompts-20261114/short-low-targets.json)。输出直方图用同源全集completion_tokens，不能用正文抽样代替；保留0/缺失/无效与短输出精确频数、双峰证据，不据输出长度单独判任务类型。

已生成四文件于`docs/tasks/product-v4/prompts/`，均可独立转发；本机未发送或执行。旧合并prompt已标替代，r1/r2是历史讨论与事实备查，不继续按其四页重排或旧阶段编号推进。模型演进原职责/验收要求保留。

本轮本地核验已完成：第三份prompt的23行对象/模型/人数与HTML提取逐项一致；22个appid交付数量、7/2/14模型组数、124913条总数正确；148个文档链接和5份原报告/既有HTML摘要通过，`git diff --check`通过。[核验记录](../../artifacts/reviews/v4-prompts-20261114/document-check.json)。本轮仅文档与提取/验证材料，未提交/push、未执行华为探索，prompt-3未生成。

## 11月14日前轮：长度分桶 模型路由与Tokenization讨论

用户在两份材料完成后启动五项讨论：DeepSeek高命中为何仍按上下文分桶；InferX是否不分桶及GDA关系；模型能力选模与规格／名字映射的区别；试点及未来MaaS是否分桶、8K/32K/64K/128K是否合适；精确Tokenization的成本。仅原理、证据与候选原则，不编写实施方案、冻结阈值或执行prompt-3。本人实际SESSION/THREAD再次核实一致。

重新核对[DeepInfer Q&A](https://github.com/deepseek-ai/DeepInfer/blob/main/doc/inference_deployment_qa.md)：P按总上下文<16K／16–64K／64–256K／≥256K分档、按计算配额动态调引擎，单步有依赖q/c的成本模型；D分别均衡并发与KV长度。没有核到全局95%命中率统计，不把用户观察升为厂商全量事实。高命中仍可能有新Token计算、历史注意力、缓存传输及生成工作；官方又明确其V4.1 Decode不受KV容量约束，不能把分桶只归因显存容量。

[InferX配置](https://help.aliyun.com/zh/pai/inferx-config-center)未证明完全不做长短分桶，公开有least-token等负载策略；“模型路由”按model字段映射服务，[智能选模](https://help.aliyun.com/zh/pai/inferx-smart-model-selection)则用外部分难度L1/L2/L3，默认model=auto，档位内候选按优先序与可用性选择。不能把InferX绑定某一种GDA结构。若用户GDA指Gated DeltaNet一类，线性层当前状态固定不等于混合模型全部缓存恒定；[Qwen3.5官方模型卡](https://huggingface.co/Qwen/Qwen3.5-35B-A3B)是3线性层加1Attention的例证，不外推本项目未知模型配置。

候选判断尚待讨论：长度感知／观测桶不等于独立MA硬分池；试点优先隔离需验证的变量，在容量与完整上下文允许时比较同一兼容缓存域，不预先叠加多档物理切分。8K/32K/64K/128K可作观测基线但不作最佳阈值；应看实际新输入量、KV负担、输出、时延干扰及缓存域变化。复核H-9/H-31原1K直方图，选定N=595/1159，均含超过131072 Token的请求；不能把128K服务标签当硬限。历史统计与P2原Trace3534行不是同一分母。

Tokenization讨论：文本最终进入模型仍需准确编码；优先区分GB重复分词和引擎必要编码。粗长度只用于软调度，靠近硬限必须按真实Template／Tokenizer核验并保留输出空间；计费／安全准入／KV匹配不能盲用字符数。复用计数／编码需固定模型、模板与模式；增量BPE不可直接相加。CPU成本须实测，不编造ms或核数。[DeepSeek Recipe](https://github.com/deepseek-ai/deepseek-recipe)提供统一协议渲染／编码参考，[vLLM输入处理](https://docs.vllm.ai/en/stable/configuration/optimization/#input-processing)说明可独立优化CPU输入路径。

### 本轮发现并初审MaaS prompt-2回传

新读[HUAWEI_V4_P2_MAAS_TRAFFIC_AND_FEASIBILITY](../../docs/huawei/HUAWEI_V4_P2_MAAS_TRAFFIC_AND_FEASIBILITY.md)，原件保持。以下为文本初审，未重跑或远端核验，不据摘要给单MA容量通过：

- 3534 Trace行与1754有效请求被解释成统一model后去重，但缺逐请求连接／排除依据；后者表头在用户监控与MA监控之间混用。统计时间为GF或MA字段，不能等同GB真实到达；窗口也不同。
- 摘要把目标60秒峰值1.2 req/s称远低于规格平均1.10/0.82 req/s，数值及比较方式不成立；1秒峰值5不能与80个并发容量示例比较。B=16是历史说明示例，不是已核实0731容量。
- 32K实例表A/B逐行加总为161/497，但128K实例表B为250（含空UUID79）；§4.3有效PT/CT子集另有缺失，不能混作同一完整覆盖。§2.9部分avg req/s与N/3600不符；需保留分母再使用。
- 128K标签被称128000硬上限，但表内PT max=132700、32K标签PT max=90025；不能凭标签推出引擎上限。GB原始JSON与模型模板后计量也不同。
- `/models`返回的cache_mode=full_block_approximation等是TokenScope模型／仿真配置，不是生产模型启动参数。2×V100是分析主机信息，不能作生产MA硬件或容量证据；历史3P3D说明不能当现场完整部署证明。10P5D原是用户候选示例，不是现网矛盾。
- P2列的A/B理想命中92.72%/90.93%不能冒充真实cached_tokens命中，后者缺失；TTFT/TPOT、并发／队列、成功率与可引用压测证据仍缺。可讨论试点目标，不能据此宣布“一个MA吃得下”。

本轮仅更新入口与本人记忆／阶段登记，不改两份研究原文、现场原件、四prompt、产品／锁文件或HTML/PPT，无服务、编码测试、部署、构建、push或跨会话操作。

## 11月14日前轮：按用户认可主线形成现网流量研究

用户已明确认可“调用类型及服务需求”为主线、四象限为发现入口、appid为证据索引；新增要求是先让领导理解企业MaaS多业务，解释agentic及搜索问答／提取等调用的请求构成、复用原因、典型行为，再按四象限给占比、已调研appid及治理方向。已交[现网流量与服务需求研究](../../docs/tasks/product-v4/PRODUCTION_TRAFFIC_STUDY_20261114.md)。这次认可允许成文，不等于方案实施或产品页面批准。

本轮本人实际ID再次从Windows SESSION/THREAD核实一致。直接解析固定四象限HTML并与77组原统计逐组核对：长低3,296／2.19%，短低124,913／82.89%，长高21,213／14.08%，短高1,276／0.85%，分母150,698；仅2026-10-20约两小时窗口。长低补入五个C04业务对象及onlinetools反例，六clock独立收益／修改数／stopped分层保留。短低突出三大流量输出形态及调用分型需求，附全部22 appid／23组索引；长高区分历史连续性、混合调用和工具载荷候选。

分类约定区分交互组织与调用目的：agentic不是长输入的同义词，搜索问答／分类／提取／总结可以是独立调用或工作流步骤；深度多轮等典型行为不是本批实测用户画像。统计事实／抽样解释／待验证假设逐处标明，原件不改。两份研究材料均已就位，用户仍明确暂不做路由或资源池方案；不推进prompt-3、页面、产品编码、现场任务或构建／push。

本地依据与原件摘要见[证据清单](../../artifacts/reviews/v4-production-traffic-20261114/evidence.json)；[文档核对](../../artifacts/reviews/v4-production-traffic-20261114/document-check.json)已通过：全部23组附录与原输出汇总／HTML逐项一致，四象限及关键比例复算一致，本地链接有效，13份原报告／HTML／prompt摘要不变，git diff --check通过。本轮只维护研究文档、入口／记忆及本地文档核对材料，不创建会话或派子agent、不发送跨会话消息；文档检查不是产品测试或现场复验。

## 11月14日前轮：现网流量研究先讨论

用户最新明确本轮仅讨论“三份回传＋四象限HTML”能形成的结论与文档组织，讨论结束后才能写文档。已复核四象限统计范围、三回传及前轮勘误；讨论中的结论和章节建议尚未获用户确定，不生成研究文档或草稿，不把方案建议记作用户决定。场景路由／差异化资源池仍在两份研究文档就位之后，prompt-3继续待讨论。本轮仅更新阶段登记，原报告和HTML保持。

## 11月14日前轮：三架构／三图文档

用户明确认可“保留场景大标签，同时识别重要工作流步骤；让场景表达服务需求，让缓存位置和实时工作量参与实际承载决策”，并指定重点收敛为InferX、DeepSeek、Mooncake／Kimi。本轮已完成[调研与对比文档](../../docs/tasks/product-v4/INFERX_DEEPSEEK_MOONCAKE_ARCHITECTURE_COMPARISON_20261114.md)，3张1800×1510 PNG及对应SVG，展开服务/选模/缓存/负载与无共享KV热点，逐层对照GB、GF、motor和独立MA，逐项附官方来源和版本边界。

新增证据：InferX可选绑定FlashKV，不能只描述为独立缓存路由；默认model=auto触发选模，分类缓存不是KV缓存。DeepSeek跨DP去亲和以共享KV可访问为前提，场景标签如何产生及跨模型选模未披露。Mooncake论文Conductor是全局调度角色，当前开源Conductor主要索引/查询，由上层router最终选择；KV目录、真实数据传输和负载决策分开。已用PDF技能核对FAST2025 Fig.2与Algorithm1；§4.2文字比较方向有歧义，不摘成固定实现不等式。知乎原链接403未作为已读来源。

**用户确定顺序：本轮架构研究→下一轮三份华为回传＋四象限HTML形成《现网流量研究文档》→两份齐备后再讨论场景路由，乃至差异化模型资源池。** 本轮未做第二份，不把前轮初步比例判断当流量研究已完成；不提前给实现方案/参数/MA数量/XPYD/模型替换或prompt-3。MaaS prompt-2回传仍未核得。

本轮只写研究文档、原创图及本地核验材料，精确更新本人入口和共享索引/记忆；原报告、四prompt、V3页面、产品/锁文件与其他session身份保持。无服务/现场操作、产品测试、安装依赖、子agent、跨会话消息、构建、commit或push。[本地核验](../../artifacts/reviews/v4-three-architectures-20261114/document-check.json)：161个本地链接有效，12份原报告/prompt/HTML摘要不变，3张PNG逐图检查并修正连线，SVG解析通过，git diff --check通过；不代表产品或现场复验。

## 11月14日前轮：三份用户侧回传与企业MaaS架构比较

用户明确要研究供应商整体架构，涵盖场景/模型路由、长短分流对KV的影响、无共享KV时怎样均衡；已转回prompt-1阶段1/2/3三份Markdown。本轮重新核实本人ID一致，读回传并完成[企业共享MaaS架构研究](../../docs/tasks/product-v4/ENTERPRISE_MAAS_ARCHITECTURE_RESEARCH_20261114.md)。公开证据扩展InferX、Foundry、Bedrock、Anyscale、Fireworks、Together，并复核腾讯、NVIDIA、DeepSeek、Mooncake；公开功能/部署平台/作者生产架构分开表达，不假定某供应商全部流量相同。

研究判断：场景决定服务策略，但粒度可能是工作流步骤；选模型和选副本分开；agentic/chat不等于长短，也不自动等于两个物理MA池。无跨MA共享时优先参考带过载退出的缓存亲和；GB必须兼顾跨MA负载，GF只能处理选中MA内部。DeepSeek/Together共享KV能使计算分档/冷热分离不必丢掉缓存可访问性，现网不能直接套用其前提。只是产品研究，不冻结算法、比例、阈值或模型替换。

用户关注的alpha_voc、末773、末1679共115375/124913=92.36%短低请求；panshi/esalespdb仅65条，不列优先。员工助手样本支持多模板/步骤，不把抽样占比当全量，不把长尾与模板因果当已逐请求验证。会议纪要120样本以单模板为主；合同审查以同业务多模板为主。长高三对象仍保留必要上下文与治理候选，不冒称工具循环。

回传引用边界：H是理想量，三报告无TTFT/TPOT实测比较；末773按原箱≥1024为1161/54602=2.13%，不沿摘要1.8%；datalinkpro的58307为11个tool总字符，最大单条20963，67464为整请求Token。完整勘误在研究末节，华为原件不改写。阶段3合并文档23组直方图各自加总守恒、总124913；不据此宣称每appid共22独立回传已全部验收。

MaaS prompt-2报告本轮尚未核得，prompt-3不生成；不修改既有四prompt/HTML/PPT/产品/锁文件，不远端执行、测试产品、启动服务、派agent、跨会话发信、构建、commit或push。更新自身入口/状态及必要共享索引，其他角色身份不变。[本地文档核验](../../artifacts/reviews/v4-enterprise-maas-20261114/document-check.json)：118个本地链接有效，12份保护原件摘要不变，23组直方图守恒、22唯一appid/124913条，git diff --check通过。仅文档核验，不是现场复验或产品测试。

## 11月14日等待现场期间：公开分流调研（前序记录）

用户告知华为正在执行探索，报告未回传；此前“本机未发送/执行”仍属实，但不再表示现场未启动。用户要求调研火山、DeepSeek、Mooncake、腾讯、Qwen、NVIDIA的分流做法及原因，判断场景分流方向。已完成[研究记录](../../docs/tasks/product-v4/MAAS_ROUTING_RESEARCH_20261114.md)，含官方文档、作者论文、llm-d能力和AIBrix历史讨论；实际session环境复核一致。

产品判断（非用户实施决定）：支持场景服务策略与缓存域亲和，但agentic/chat不能等同长短，混合appid需细分证据，GB仍要跨MA容量/排队保护；减少MA或10P5D另待技术证据。DeepSeek V4.1公开材料显示共享缓存与长度分档可并存，不套作华为0731或新模型Tokenizer适配结论。llm-d公开具备缓存路由，不把现网主要均衡概括成框架能力不足。最终看满足质量/SLO的成功任务/卡分钟，缺任务标识时只报请求指标。

四份现场prompt保持原件，未生成prompt-3、改HTML/PPT、产品代码/锁文件、启动服务、派子agent、发送跨会话消息、提交或push；报告后再讨论实验。本轮只检查文档和保护原件，不冒称产品测试或现场复验。

## 11月14日DeepSeek专项：仅机制与条件

用户进一步要求展开DeepSeek长度调度及共享KV，映射GB、GF和独立MA；明确先不做实现方案。已完成[专项记录](../../docs/tasks/product-v4/DEEPSEEK_ROUTING_AND_SHARED_KV_20261114.md)，依据官方V4.1 Q&A、3FS、旧V4报告和DualPath，版本分别表达；知乎原链接本轮403，未冒称已读。

核心判断：计算落点与缓存域需分开，同MA池化是已有基础，跨MA共享路径按用户描述不具备；网络性能、统一身份与引擎读取能力仍属未证实条件。“换档可保留复用机会”不等于全命中或零成本。只解释可借鉴原则，不冻结路由算法、XPYD和阈值，不生成prompt-3或改原prompt/页面。

本轮git状态发现`docs/huawei/HUAWEI_V4_P1_STAGE1_MIXED_SCENARIOS.md`与`HUAWEI_V4_P1_STAGE2_LONG_TAIL.md`新文件，未审阅或改写；不据文件出现宣称现场全部完成/通过。后续报告核对保持独立，不自动切换本轮研究任务。

## 11月13日方向背景与已完成工作（历史）

2026-11-13用户方向：TokenScope本质上提升KV cache hit，最终提升一张卡每分钟成功完成任务的数量/价值，不仅看吞吐与单请求时延。V3最大价值是四象限场景分类及真实数据上的可行改法。领导汇报要把大方向、节点和预期成果；用户回复没有既定日期。方向保留，当前汇报组织暂停。

11-13讨论的优化路线曾按三阶段：1长低prompt改造/session_clock；2短低大流量，查混合业务（DeepSeek meeting.brain，Qwen员工助手末773/末1679）；3长高长尾，查Token工具异常候选及混合（DeepSeek天舟、Qwen datalinkpro、GLM notify_message）。这是背景路线，不是11-14新prompt-1的阶段编号。三个混合业务重点对象在旧窗口合计109610条/150698≈72.7%，不等于可节省比例；旧retain_last=3不作推荐。

Infra方向来自用户debug：上下文分流与过多MA打散缓存；拟按agentic/chat场景分流，GB做KV路由，减少MA个数、扩大实例内XPYD（10P5D仅示例），GF内部均衡并由Infra审查motor边界。试点DeepSeek的com.huawei.ucd.uiplus.wa、com.huawei.cloud.ioc.global。本机MAAS_REFERENCE确认同UUID内共享、跨UUID不默认共享；用户debug的具体差距/llm-d部署、对标DeepSeek大池细节需现场证据，不写成本机独立实测。场景不能只按长度命名；拆标签不自动提升缓存；实际任务/卡/分钟需任务完成、质量及卡分钟口径。

已准备[华为定向探索prompt](../../docs/tasks/product-v4/HUAWEI_V4_SCENARIO_EXPLORATION_PROMPT_20261113.md)：先阶段2三组，复用阶段3三组，补两个Infra对象已有路由/缓存域数据；小样本只读结构与现成计量，不新分词/仿真、不重跑全量、不动V3服务，单Markdown正文嵌证据。尚未发送/执行，不自动增加新探测器或部署工作。模型演进原职责保留，前端变化仍须明确DEMO批准。

r2本机核验完成：8个对象的旧报告P/H/C守恒及阶段2总数/占比、114个文档链接、5份原报告/既有HTML摘要检查通过，`git diff --check`通过；[记录](../../artifacts/reviews/v4-direction-20261113/document-check.json)。这是文档/已有证据检查，不是新分析或现场复现。当前r2及prompt保留未提交，未push。

口径锁定：父集1047监控34.81%与选定73条31.93%分开；六clock按模板签名区分，最高单项43.27%（+11.34个百分点），各自独立不求和。ICSL102条35.95%→90.16%为合成实算。stopped源于L4原因覆盖受限，BUS01已发布7项窗口均complete；例证不代表全部修改覆盖，固定clock影响时间感知。MA缺数保留null；真实覆盖67/77/150698属历史窗口。三新模型资产/模式和TTFT仍待证，不编兼容/性能结论。

定向核对原报告与补证、验收收口及旧宣传/四象限口径；本轮只做文档数字/链接与原件摘要核验，记录在[本地材料](../../artifacts/reviews/v4-product-first-round-20261113/source-check.json)，不冒称产品测试或现场复验。保护产品/锁文件/state/既有HTML及其他session身份；本轮文档保留未提交，未构建/push/启动服务/重跑分析/创建或联络其他会话。

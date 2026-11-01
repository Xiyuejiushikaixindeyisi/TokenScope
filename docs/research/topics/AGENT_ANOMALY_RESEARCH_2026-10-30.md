# Agent 异常分析首轮调研

日期：2026-10-30。维护角色：异常分析后端母会话，session `01a18be2-7112-7aa2-919b-5137d1f1b1ad`。任务入口：[异常分析](../../tasks/analysis/ENTRY.md)。

本轮响应用户六项调研：相似工具、低理想命中原因、agent 编排问题、公开负载与 trace、排队建模、agentic infra。依据为论文、作者文档、开源仓库和当事人的公开 issue；公开报告中的局部复现与普遍结论分别表述。本文是研究依据和产品讨论输入，尚未形成正式设计或接口契约。本轮未下载运行数据集、部署候选工具或验证现场调用链。

## 1. 主要发现与指标边界

已有工具分别覆盖链路观测、执行剖析、失败分类和缓存诊断，能够提供组件和方法参考；本轮未发现一个已经核实、同时覆盖 TokenScope 两类诊断及现有监控计量的完整替代品。这是检索范围内的结论，不是对所有开源项目的穷尽判断。

低命中与 Token 浪费需要联合观察：循环执行可以持续复用长历史，因而缓存命中率很高，但调用次数、输出和总消耗仍不断增加。反过来，新任务首轮或合理引入新资料也会降低命中率，不能只凭比率判断编排错误。

首先区分三类问题：

| 问题 | 能说明什么 | 需要的主要证据 |
| --- | --- | --- |
| 理想命中率低 | 在固定编码、缓存规则、隔离范围和历史窗口内，可复用前缀较少 | 模板后输入、共同前缀及断点、历史候选、配置与预热范围 |
| 实际命中低于可复用水平 | 有内容复用潜力，但真实服务未兑现 | 引擎缓存读写、TTL/淘汰、路由、并发与写入就绪、真实配置 |
| agent 消耗异常 | 单次或整个任务的输入、输出、步骤或重复工作偏离合理行为 | session/turn/tool 关联、失败与重试、任务进展及完成状态 |

TokenScope 当前监控口径来自[公共计量说明](../../contracts/MONITORING_V1.md)：`P` 是模板后输入，`H` 是规则下可复用输入，`C=P−H`；appid 隔离、空缓存起始、无限容量、仅发布完整输入块。有效块长、MTP、CP、模型及模板身份影响结果。这里的“理想”仍受所选规则和可见历史限制。真实 TTL、显存淘汰和跨实例路由不能直接解释这个无限容量仿真的低值。

因此，诊断前还需核对冷启动、窗口前历史缺失、有效样本筛选、隔离粒度、块规则和编码身份。只发布输入块也会影响相邻轮次复用的模拟结果，不能直接按真实引擎复用上一轮输出的能力解释。汇总时同时报告总量比 `ΣH/ΣP` 和分组分布，避免把请求比率的算术平均与 Token 加权比率混用。这些是本项目口径核对项，不是新增算法。

## 2. 相似开源工具与技术文档

| 来源 | 已核实的定位 | 对本项目的借鉴与限制 |
| --- | --- | --- |
| [Langfuse](https://github.com/langfuse/langfuse) | 开源 LLM/agent tracing，包含 session、调用、成本、prompt 管理和评估 | 借鉴请求到任务的关联、版本和证据浏览；未据此确认具备模板后前缀断点或 TokenScope 理想缓存归因 |
| [Phoenix](https://github.com/Arize-ai/phoenix) | 基于 OpenTelemetry/OpenInference 的追踪、评估、数据集与实验 | 借鉴 span、工具与模型调用关系、跨版本比较；trace 可见性本身不等于原因识别 |
| [TraceLab](https://github.com/uw-syfi/TraceLab) | 编码 agent 轨迹收集、脱敏、公开数据与分析流水线 | 最贴近本轮负载研究，可参考 turn/tool/token 字段和分析方式；不是现成异常判定服务 |
| [AgentSight](https://github.com/eunomia-bpf/agentsight) | 结合系统侧观测与 agent 活动关联的研究工具 | 为 SDK 之外的进程、文件、网络活动提供思路；部署权限、平台及加密链路覆盖需另验 |
| [AgentPProf](https://arxiv.org/abs/2609.20301) | 将 agent 轨迹组织成语义操作栈，进行跨运行归属与剖析 | 借鉴按任务/语义操作呈现耗时和资源；语义分段与归属仍需验证，不能直接等同因果证明 |
| [MAST](https://github.com/multi-agent-systems-failure-taxonomy/MAST) | 多 agent 失败分类、标注轨迹与分析资源 | 可作异常词表、语义案例与评估输入，不能当作生产流量分布 |
| [Claude Cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics) | 官方 API 缓存诊断，比较关联请求并返回最早的 model/system/tools/messages 分歧 | 与低命中产品形态最接近的公开参照；属于服务端功能，不是通用开源组件，且有平台和比较可用性限制 |

Cache diagnostics 的一个可借鉴细节是先定位最早分歧，再解释受影响的后缀；一次返回不代表列出了全部差异。其 `diagnostics:null` 可以有多种含义，比较尚未完成也有单独状态，缺少原因不能直接推断为 TTL。TokenScope 可参考这种“位置＋影响＋证据状态”的表达，而正式结果结构仍待产品讨论。[官方响应语义](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics)

采用状态：以上均为候选参考。没有引入外部源码、修改 sources.lock，亦未验证它们与当前监控的兼容性。

## 3. 理想命中率低的 agent 相关原因

### 3.1 与用户 cch 场景直接对应的公开证据

用户解释的场景是：复用 CC 编排时，网关将带有 cch 等动态内容的字段继续传入模型输入，破坏前缀复用。公开 [CC Switch issue #2350](https://github.com/farion1231/cc-switch/issues/2350) 对应得很直接：报告者在 Claude Code 2.1.119、CC Switch 3.14.1 的 `openai_responses` 转换中，发现 `instructions` 前部的 `x-anthropic-billing-header` 含变化的 cch，而模型和工具等条件保持一致；移除该输入行后，其局部样例缓存读取比例明显恢复。

这支持“动态元数据进入输入前部可以破坏后续复用”的具体案例。公开材料将该字段称为 billing/attribution；本文不把“鉴权”认定为已核实的官方职责，也不推断所有版本、官方直连或所有代理都会出现同样行为。后续验证应比较网关转换前后和最终模板后输入，确认实际变化位置与功能影响；不能仅按字段名就认定可删除。

另有 [Claude Code issue #40652](https://github.com/anthropics/claude-code/issues/40652) 报告历史工具输出中的 cch 在下一轮发生变化，可作为“历史被重写”的线索。该报告关于内部替换机制的解释尚不足以作为已证实根因；issue 关闭状态也不等同已修复。

### 3.2 原因、症状与证据

| 候选原因 | 典型表现 | 诊断需要核对的证据 |
| --- | --- | --- |
| 前部动态字段 | 时间戳、request ID、动态账单标记、临时路径等进入 system/instructions 或早期消息 | 相同任务连续输入的最早 Token 分歧；字段实际位置和生成来源 |
| 工具定义或顺序漂移 | 工具列表增删、Schema/描述更新、异步发现导致排序不稳定 | tools 的规范化差异、原始顺序、工具注册/版本记录及模板后位置 |
| 历史非追加式改写 | 每轮重写旧消息、旧工具输出、摘要、角色或包装标记 | 对同一历史条目的跨轮对比；区分内容真的改变与序列化变化 |
| 动态内容放在稳定内容前 | RAG 结果、用户状态或实时环境说明排在可共享说明/工具之前 | 最早断点之后有多少相同内容；移动位置的反事实比较需保证语义等价 |
| 序列化或模板身份变化 | JSON 键顺序、空白、转义、工具模板、特殊 Token 或模式改变 | 最终输入 IDs、模板/Tokenizer 摘要、模式身份，而非仅看 JSON 语义相同 |
| 上下文压缩或截断 | 旧历史被摘要替代、滑动窗口前移、主动清理工具结果 | compaction/截断事件及边界；这种变化可能是合理的上下文管理 |
| 负载组成与隔离范围 | 新会话多、首轮多、工具/租户差异大、公共前缀短、合法新增长 | session/turn、输入增长、分组及冷启动窗口；不应预设统一目标百分比 |

[Manus 的一手工程总结](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) 强调稳定前缀、追加式历史和确定性序列化，并指出动态修改前部工具定义会影响缓存复用。它采用工具集合稳定、动作可用性另行约束的方案；这是一种具体选择，工具规模、权限和模型能力不同仍需权衡。

工具漂移还有具体公开案例：[Claude Code issue #49038](https://github.com/anthropics/claude-code/issues/49038) 报告 Agent SDK 0.2.101/捆绑 CC 2.1.101 中，工具描述里的子 agent 名称顺序跨请求改变。报告者给出输入差异并用本地确定性排序恢复命中。这是特定版本的报告，不能推广为所有 SDK 固有行为。

[Claude 缓存文档](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) 说明工具、system、messages 的缓存层级，以及不同配置变化对缓存的影响。它可支持上述机制解释，但服务商的最小长度、TTL 和断点规则不应直接移植为 TokenScope 当前完整块模拟规则。

### 3.3 产品讨论上的含义

低命中分析宜先回答：哪组请求本来有复用关系、最早在哪里分歧、变化属于哪个输入来源、影响了多少可复用后缀。然后再给出稳定排序、调整动态内容位置、保持历史一致等条件化建议。

“去掉差异后模拟 H 上升”只能证明所选输入变换在固定规则下的复用潜力；它不自动证明生产可安全改写、真实命中达到同值，或端到端延迟/成本按同样比例下降。收益需明确是模拟输入 Token、实际计费还是现场性能。

## 4. Agent 编排异常与 Token 消耗

[MAST 论文 v3](https://arxiv.org/html/2503.13657v3) 分析 7 个多 agent 系统、超过 1,600 条标注轨迹，将 14 类失败归入系统设计、agent 间失配、验证与终止三组。这提供了比“循环”更完整的分类起点；样本来自其评测任务，分类频率不能当作所有生产 agent 的发生率。

以下表格综合论文、工具设计文档和公开问题，最后一列是本项目后续取证需求，尚非探测器承诺。

| 问题 | 可能造成的消耗/行为 | 所需证据与误判边界 |
| --- | --- | --- |
| 工具定义漂移或工具行为变更 | 缓存断点、引用已移除工具、参数不兼容 | 区分输入表示漂移与工具实际语义/版本变化；需要工具身份与版本 |
| 工具选择、参数或权限错误 | 调用失败后重复尝试，修复无效 | tool 名称、参数、状态码、错误类型和后续动作；单次失败可正常恢复 |
| 无退避/无预算的重试 | 服务故障放大为重试风暴，重复输入与输出 | retry 关联、幂等键、重试次数和退避时间；区分 SDK 自动重试与模型新决策 |
| 重复行动且没有进展 | 相同检索、相同文件读取、同样错误被反复执行 | 规范化参数、结果摘要、状态变化与任务进度；重复工具名本身证据不足 |
| 停止条件或图路由不一致 | 工具回流后持续执行，模型一直返回 tool_calls | 路由、stop reason、步数/预算、最终任务状态；达到步数上限也可能是任务合理复杂 |
| 多 agent 协同失配 | 相互转交、角色职责冲突、同一工作重复做 | handoff、角色、父子任务、消息与共享状态；仅凭并发或多个 agent 无法判断浪费 |
| 上下文膨胀与重复注入 | 全量工具返回、重复历史、嵌套 JSON、多份上下文反复回灌 | 按来源统计每轮新增和累计 Token；长上下文本身未必异常 |
| 压缩/记忆管理失效 | 关键限制丢失后重复探索，历史重置后重新工作 | 压缩前后映射、保留约束、后续错误及任务状态 |
| 验证与终止失败 | 未完成就结束，或已经完成仍反复验证/修改 | 验证目标、结果与完成标准；“运行很久”不足以判为死循环 |
| 并行、取消和超时处理问题 | 分支失败后其他分支继续，任务已取消仍有调用或副作用 | 分支依赖、取消传播、工具完成事件和孤立任务；需执行层数据 |

一个直接的 Loop 报告是 [LangGraph issue #3097](https://github.com/langchain-ai/langgraph/issues/3097)：模型反复调用搜索而不结束。[维护者解释](https://github.com/langchain-ai/langgraph/issues/3097#issuecomment-2602686208) 该 ReAct 流程在模型不再返回 tool_calls 时终止；若底层持续产生调用，流程也会继续。这说明需要同时检查模型输出与编排终止策略，不能把所有循环归为框架 bug。

[Anthropic 工具工程文档](https://www.anthropic.com/research/writing-tools-for-agents) 讨论工具命名、说明、返回内容与评估；[上下文工程文档](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) 讨论压缩、结构化笔记和分工。它们可帮助提出可执行建议，但“摘要更短”“工具更少”都需结合准确性和任务完成率评价。

研究层面建议把重复执行分成合法迭代/轮询、可恢复重试、疑似无进展循环、已证实错误循环四种证据状态。尤其不能把 TraceLab 中的 autonomous loops 翻译成“死循环”：前者也包含正常的多步自主工作。

## 5. 大模型与 agent 负载研究、数据集和使用方式

### 5.1 公开材料对照

| 材料 | 已公开内容 | 适合的问题 | 主要限制 |
| --- | --- | --- | --- |
| [TraceLab，论文 v2](https://arxiv.org/abs/2606.30560v2)／[数据 release v0.0.1](https://github.com/uw-syfi/TraceLab/releases/tag/v0.0.1) | 日常编码 agent 的 session/turn、LLM 步骤与工具记录；该 release 含 357,161 条 LLM、432,510 条工具记录、43 位使用者 | 多轮增长、前缀读写、工具间隔/失败、任务调用数、工具耗时分布 | 发布数据移除工具输入正文，仅保留字符数等；不能直接定位 cch 或判定参数语义重复；首页与 release 的统计不可混用 |
| [KVCache Cache in the Wild，ATC 2025](https://www.usenix.org/conference/atc25/presentation/wang-jiahao)／[Qwen-Bailian trace](https://github.com/alibaba-edu/qwen-bailian-usagetraces-anon) | 采样集群匿名轨迹：以秒为单位的相对时间、输入输出长度、会话/父请求、轮次与前缀块哈希；当前 README 含 To-C、To-B、Thinking、Coder 场景 | 请求间/轮间复用、容量与淘汰、复用距离、场景混合 | 哈希为模板后真实输入的块标识，块长 16；无原文，不能做语义归因；当前发布场景不必然等于原论文全部实验切片 |
| [Mooncake FAST25 release](https://github.com/kvcache-ai/Mooncake/blob/main/FAST25-release/README.md) | conversation 12,031 请求、toolagent 23,608 请求、synthetic 3,993 请求；前两份为小时级真实采样，另有合成负载 | agent/对话的前缀复用、缓存策略、调度和合成压力流量 | 时间戳为毫秒，块长 512；toolagent 名称不表示提供完整工具语义/任务链，合成负载不能当真实流量 |
| [Azure LLM 2023](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2023.md)／[2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md) | 时间戳、ContextTokens、GeneratedTokens；分别关联 Splitwise 与 DynamoLLM 工作 | 到达率、输入输出长度、prefill/decode 负载、排队与容量模拟 | 三列长度轨迹不能重建前缀、工具链或循环原因 |
| [BurstGPT](https://github.com/HPMLL/BurstGPT) | 长时间真实服务轨迹，包含时间、模型、请求/响应 Token、耗时和部分会话标识等 | 突发性、日周期、长尾、失败和负载生成 | elapsed time 为请求提交到完成的耗时，不能直接当 TTFT 或纯 GPU 服务时间；无完整 prompt/tool 语义 |
| [MAST 论文/数据入口](https://arxiv.org/html/2503.13657v3) | 多 agent 执行轨迹、失败标签与分类 | 失败案例、标签定义、语义诊断评估 | 评测/标注集不是自然生产到达流，也不能直接校准排队参数 |

[TraceLab 论文](https://arxiv.org/abs/2606.30560v2) 观察到长自主执行链、长上下文与短输出、工具耗时重尾、较高但不完美的前缀命中。它很适合作为本项目“普通 agent 负载是什么样”的起点；使用者和编码场景的选择偏差仍需保留。其 `newly_append_tokens` 包含未缓存输入与缓存创建部分，不能直接解释成语义上首次出现的内容。

[KVCache Cache in the Wild](https://arxiv.org/html/2506.02634v1) 表明真实复用存在偏斜，跨请求共享与多轮复用都值得研究。这对缓存模拟很重要，但论文针对特定服务商和负载，不提供通用“理想命中率应为多少”的阈值。

还有两类 agent 系统研究值得读：[Agentic AI Workload Characteristics v2](https://arxiv.org/abs/2605.26297v2) 比较基准、模型与缓存等配置；[AgentSysBench](https://arxiv.org/abs/2608.15127v1) 研究多种应用中的非 LLM 工作、工具与控制层成本。它们说明 agent 负载不能只按输入输出长度描述；本文未据此确认可直接下载的原始生产 trace，亦不把其基准统计当作普遍分布。

### 5.2 常见使用方式与容易出错的地方

1. **做负载画像**：用 TraceLab 看每个任务的调用数、轮间增量、工具等待和缓存读写；用 Azure/BurstGPT 看外部到达、长度、突发与日周期。先固定发布版本和样本筛选，再算分布。
2. **做缓存研究**：用 Qwen/Bailian 或 Mooncake 的前缀哈希做复用和缓存事件模拟。匹配必须保持前缀及前驱关系，不能把共享块当无序集合；不同数据集的块长和时间单位不能混用。
3. **做服务压力回放**：可以从长度/哈希构造保留所需属性的合成输入。Qwen 仓库提供作者维护的 [trace-replayer](https://github.com/blitz-serving/trace-replayer) 入口；其保真性和目标引擎兼容性需另做实验。模板后哈希不能重新套 Chat Template，更不能据此还原原文。
4. **做 agent 行为归因**：采用语义轨迹或脱敏现场样例，保留工具参数/结果摘要、失败、状态变化和任务完成信息。匿名哈希或只有长度的数据不足以验证 cch、工具选择错误或死循环。

回放还需区分开放到达流与按完成事件推进的 agent 交互：前者按时间表注入，后者要保留工具、LLM、分支之间的因果依赖。服务速度变化后机械保留全部原始内部请求时间，可能得到不可能的执行顺序。以上为方法建议，本轮尚未回放。

### 5.3 本轮固定的数据来源身份

| 来源 | 本轮核对的身份 | 用途 |
| --- | --- | --- |
| TraceLab README | commit `5c6550b0d08beff983e9159fe2575e7a2334c8c1`，路径 `README.md` | 核对字段、脱敏范围与 release；数据规模按 v0.0.1 |
| Qwen/Bailian README | commit `5f7439c51ec248a0c585f7d90a41a6f57773b912`，路径 `README.md` | 核对 16-token 哈希、模板后输入及场景 |
| Mooncake README | commit `522b716ee7ba459008b59fd6fa3c6937fcde93c9`，路径 `FAST25-release/README.md` | 核对三份 trace、规模、毫秒及 512-token 块 |

固定链接：[TraceLab README](https://github.com/uw-syfi/TraceLab/blob/5c6550b0d08beff983e9159fe2575e7a2334c8c1/README.md)、[Qwen README](https://github.com/alibaba-edu/qwen-bailian-usagetraces-anon/blob/5f7439c51ec248a0c585f7d90a41a6f57773b912/README.md)、[Mooncake README](https://github.com/kvcache-ai/Mooncake/blob/522b716ee7ba459008b59fd6fa3c6937fcde93c9/FAST25-release/README.md)。

TraceLab v0.0.1 release API 公布的资产摘要：DuckDB 99,889,152 bytes，SHA-256 `97715265367cc72376475f5d444c8e1900b88cab1482aa7b9a742894d9f15619`；JSONL.gz 53,601,226 bytes，SHA-256 `9d265eae69a31cae203848bea936f018148eed7ca8bf56050c5abe96da0b4e6b`。这是远端元数据核对，不是本地下载后验算。实际采用时仍需校验文件与数据使用条款。

## 6. Agent 负载的排队建模

### 6.1 M/G/1 有直接相关研究，但应明确对象

[A Queueing Theoretic Perspective on Low-Latency LLM Inference with Variable Token Length，v2](https://arxiv.org/html/2407.05347v2) 使用排队模型讨论可变输出长度、截断和批处理。其中 FCFS M/G/1 基线的平均排队等待为：

`E[Wq] = λ E[S²] / (2(1−ρ))`，其中 `ρ=λE[S]<1`。

它假设泊松到达、独立同分布的服务时间、有限二阶矩和单服务台等条件。对本项目的价值是解释：在相同平均工作量下，服务时间波动和长请求也会显著放大等待。这个公式不是 P90 TTFT 计算式；请求完成耗时若含排队、工具或用户等待，也不能直接代入 GPU 服务时间 `S`。

对 agent 可先使用一个计数关系作为工作量检查：稳态下 `λ_LLM = λ_task × E[K]`，`K` 为每个外部任务产生的 LLM 调用次数。它说明重试/循环会放大内部流量，但不意味着这些内部请求仍是独立泊松到达。估计时还需处理窗口边界、未完成任务和长期不终止任务。

### 6.2 更贴近 agent 的模型

[Throughput-Optimal Scheduling Algorithms for LLM Inference and AI Agents，v3](https://arxiv.org/html/2504.07347v3) 直接研究多类别批处理网络、DAG 和 fork-join agent 拓扑，建立调度稳定性/吞吐分析；循环路由和批量限制会增加复杂性。其吞吐最优结论有模型假设，不能直接解释为所有实现中的尾延迟最优，或对当前某引擎版本的性能判决。

| 场景 | 合适的起点 | 额外需要描述的内容 |
| --- | --- | --- |
| 单模型、串行服务的简化基线 | M/G/1 或更一般到达过程的队列 | 到达拟合、服务时间与重尾、稳定区间 |
| 多实例与不同长度/优先级 | 多类、多服务台队列 | 路由、类别、实例性能和缓存状态 |
| LLM→工具→LLM | 带反馈与外部等待的排队网络 | 工具耗时/失败、返回概率、重试、会话状态 |
| 并行子任务汇合 | DAG/fork-join 网络 | 分支数、依赖、慢分支和同步；等待不等于各分支耗时之和 |
| 连续批处理、KV 容量及动态策略 | 校准后的离散事件/迭代级模拟 | prefill/decode、batch token budget、缓存就绪、抢占与资源竞争 |

建议先以数据估计外部到达、任务调用数、每轮新增输入/输出、工具等待、并行与回流，再选择模型；不要先把所有 agent 负载强行拟合为一个 M/G/1。对 TokenScope，这一方向适合解释负载放大与资源压力，尚不是已批准的首期诊断模块。

## 7. Agentic infra 的设计思路

| 思路与来源 | 可以借鉴的设计 | 与异常分析的联系 |
| --- | --- | --- |
| 会话日志、执行循环与环境分离：[Managed Agents](https://www.anthropic.com/research/managed-agents) | 持久事件日志支持恢复；harness 负责模型/工具循环；sandbox 承载执行，凭据有独立边界 | 会话事实与发送给模型的上下文投影分开，便于重放、对比压缩及追踪历史改写 |
| 可恢复执行与幂等：[LangGraph Functional API](https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/functional-api.mdx) | checkpoint 恢复已完成任务，未完成操作可能重跑；外部副作用仍需幂等 | 将模型重试、框架重放和工具重复副作用分开归因，避免把“有 checkpoint”当任意操作只执行一次 |
| 面向整个程序调度：[Parrot，OSDI 2024](https://www.usenix.org/conference/osdi24/presentation/lin-chaofan) | 暴露请求依赖和语义变量，按端到端应用而非孤立调用优化 | trace 应保留父子依赖与汇合点，性能建议应考虑关键路径 |
| 任务进度与服务公平性：[Autellix](https://arxiv.org/abs/2502.13965v1) | 利用程序已有服务量等信息调度多次 LLM 调用 | 单次请求快不代表整个任务快；比较应保留任务完成率和端到端时延 |
| 缓存局部性与负载均衡：[Preble](https://arxiv.org/abs/2407.00023) | 多实例路由同时考虑缓存复用和服务负载 | 最高命中率不是唯一目标；为了命中挤到忙实例可能延长等待 |
| 前缀共享与结构化运行时：[SGLang](https://arxiv.org/abs/2312.07104) | 结构化程序与运行时协作，RadixAttention 管理前缀共享 | 缓存证据要保留真实前缀和分支，不能只对 JSON 做无序相似比较 |
| 通用观测语义：[OTel GenAI agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md) | agent/workflow/model/tool 的层次关联，结合版本、耗时及状态 | 可参考身份和关联方式；规范仍标记 Development，采用时需锁版本 |

结合这些来源，本项目后续产品讨论可优先围绕四个问题展开：

1. 如何从稳定会话身份关联输入、工具、重试和终止，并把日志事实与模型上下文区别开来。
2. 如何用固定编码和前缀证据解释缓存损失，同时保留内容变化的合理性与建议前提。
3. 如何按任务呈现累计输入、输出、步骤、工具时间、错误与进展，发现高命中下的浪费。
4. 如何使每项结论都能回到请求对、来源位置和执行事件，并明确缺失信息导致的判断上限。

这些是研究推导的讨论议题，未冻结数据模型。监控统一维护编码、计量与理想缓存计算；分析消费结果或复用同一实现。展示读取已有成果，不在访问页面时触发分析；两条详细设计/开发线仍按用户后续启动。

## 8. 下一阶段需要收敛的证据

首轮研究已覆盖六个方向；下一步产品讨论最有价值的输入是：现场是否有稳定 session/turn/agent/tool 标识，以及可否在现场取得少量连续、脱敏的最终模型输入和工具结果摘要。appid 不应直接替代 agent 或 session 身份。

如果只有当前请求正文和监控结果，可以先讨论输入组成、动态字段和前缀变化；对“工具失败导致重试”“无进展循环”等因果判断，应保留输入不足状态。即使取得调用链，也需要正常长任务、合法轮询和恢复重试作为对照，避免把所有长链标成异常。

本轮完成文献与来源核对，未做数据集分析、性能实验或现场复现。后续需按选定问题记录固定数据、配置、对照、结果和限制，再将研究结论升级为能力事实。

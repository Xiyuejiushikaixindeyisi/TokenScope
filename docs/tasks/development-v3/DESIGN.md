# V3 四P0设计（面向开发 agent，r2，2026-11-11范围修订）

**当前范围决定（2026-11-11）：显式 full 延期（DEFERRED_BY_USER，未实现/未运行，不记PASS），不再是本期V3门禁；自动full仍禁止。候选repair-r1-02为LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING，独立R2已关闭RV3-01/02/03。大源自动缩样和五组session_clock样本参考率优先，真实BUS01–05及现场AC-MEM待华为验收。暂不打包。**

本修订覆盖下文原r1日期和当时计划状态；实现与实测映射见[设计核对](DESIGN_CHECK.md)及[本地收口](LOCAL_ACCEPTANCE_CLOSE_20261111.md)。延期未指定版本，不自动纳入V3.5；Token异常修复仍留V3.5。

日期：2026-11-10。状态：**按[评审决定](../product-v3/V3_REVIEW_DECISION_20261110.md)落实两项修订，完成一致性检查后获准串行实施**。范围依据用户本轮要求、[证据核验](EVIDENCE_REVIEW_20261110.md)和[独立CHECK](CHECK.md)。本文定义目标行为；现有实现事实查CHECK；实际实现与测试结果未来记入每批记录，不能由本文代替。

## D0. 范围、成功条件与评审决定

V3目标：在明确资源上限内，以可复现样本定位低命中原因，生成受业务约束的精确变换，完成同样本对照和冻结改法后的独立复核，发布完整的收益与未完成解释。保留原始数据、四入口、L4/L5主体及Token旧结果。

**用户本轮追加的底线优先**：①总数据量过大必须自动缩小到可完成的小样本分析，不能把mem_limit、整scope超限拒绝或预算不足当成功；②指定五组业务必须在前端显示session_clock固定化方案及V3实算的参考提升率，形成业务沟通证据。五组与逐组门禁见[底线验收](ACCEPTANCE.md)。正常低命中诊断必须由L1自动发现有证据的clock变化并完成改法→评估→前端链路；人工预指定clock/recipe的实验不能替代该门禁。普通日期槽删除不能替代session_clock固定化，旧报告数字不能冒充V3结果。

不做：T1/T2–T4新规则或修复、默认limit/retain_last/recipe安装、assistant/system Token占比新探测器、独立P1模板产品、路由拆appid、hybrid、自进化Agent、GPU答案质量重放、现场部署或镜像打包。候选内部结构分桶属于P0，不做新的模板产品页面。

R1–R5按评审范围执行；新增条件为自动L1闭环及逻辑字段可比性，详见[修订核对](REVIEW_FIXES.md)。镜像/现场授权仍独立：

| 决定 | 建议 | 原因 / 不采用时的影响 |
| --- | --- | --- |
| R1 来源准备 | 明确诊断请求内自动编排元数据准入、受控流式校验与有界快照 | 大源自动缩样，用户无需猜sample_limit；旧manifest校验仍有全文件I/O，流式独立计账，不承诺首次即O(样本)。 |
| R2 新协议 | 新增V3任务/样本/报告协议与路由；V1/V2冻结schema及已发布读接口保持 | pilot/A/B、partial证据不塞进旧full字段；旧写入口不能绕过V3预算/Token休眠。 |
| R3 改法边界 | session_clock固定化是必做标准变换：同一常量替换所选块内部，只修改副本 | 五组必须显示具体改法与实算参考提升率，标明时间感知改变/业务待确认，不自动应用到生产。 |
| R4 执行与门槛 | 默认自动有界profile，可解释且版本化；无固定300假设、无pilot触发full | 用户可收窄不能越界；五组样本参考数值不受旧1pp过滤，零/负收益也如实显示，不为过验收换样本。 |
| R5 发布与休眠 | 停止时保留已封存证据、评估完整性独立；新Token执行统一拒绝，旧结果可读 | 不把取消任务改成成功、不捞取未封存working目录；旧排队/重试不自动恢复Token。 |

两条底线及两项评审修订作为实施门禁；R1–R5和[TESTS](TESTS.md)响应目标按已评审方案执行，重大改变返回评审。自动profile在V3B002按模型固定开销与可用资源校准留证，不抄现场数值；用户不填sample_limit时使用批准的自动策略，不拒绝正常请求。设计变化同步批次和验收映射。

## D1. 数据流与模块边界

推荐新主链：

`explicit diagnostic request → metadata admission / automatic bounded sampling → prepare snapshot → discovery A → freeze session_clock transformation → evaluate A → independent B → sealed report → read-only UI`

`explicit full request`按2026-11-11用户决定延期，本期无此入口。未来另行规划时须为独立任务，绑定冻结变换、明确范围和新预算；以下仅保留其语义，不构成本期实施要求。prepare是用户明确发起诊断后的自动阶段，独立记录意图/预算/耗时/状态；可保留高级prepare API供复用。页面GET、服务启动和旧任务恢复不得触发准备或分析；自动缩样不是自动full。

| 模块 | 现有复用 | 拟增/改位置（未创建源码） |
| --- | --- | --- |
| 来源/样本 | SourceIdentity、RequestKey、编码证据、seal；不重写监控计量 | `analysis_common/source.py`增加适配点；新增`sample_source.py`、`sampling_v3.py`及source preparation模块。 |
| 生命周期/资源 | TaskStore幂等、摘要校验、telemetry、冻结结果读取 | 新增`execution_v3.py`、`runtime_v3.py`、`worker_v3.py`、V3存储/发布适配；`api/app.py`与CLI/dispatcher最小注册。 |
| L1/候选 | 动态槽、工具逻辑名、CandidateIndex、L2工具集合、L4/L5事实 | `prefix_analysis/dynamic.py`、`detection.py`、`candidates.py`、`service.py`、`recommendation_groups.py`；必要新模块分离V3策略。 |
| 实验/投影 | guarded mutation、EncodingContext、monitoring.make_strategy、P/H/C | `prefix_analysis/experiments.py`和新V3实验编排；`analysis_common/evaluation.py`抽取可复用核心、V3投影；不复制tokenizer/缓存算法。 |
| API/UI | 原冻结读接口、目录绑定与四入口/L4L5展示 | 新`api/diagnostics_v3.py`及新契约目录；viewer API适配、model.ts、Reports.tsx、ExecutionStatus.tsx、必要的历史选择逻辑。 |

这里的公共层扩展不改变用户监控/MA指标、默认来源绑定、TTFT或缓存策略。源码文件拆分允许批内合理调整，必须在PLAN和CLOSE记录映射；接口语义、范围和验收门槛变化须返回评审。

## D2. 范围先行与可信样本

### D2.1 选键规则

- 输入固定source kind/run/index revision、appid、模型/编码身份和可选父时间范围。只用`time_ns, source_record_index`稳定排序；hash_id不是session_id。
- V3首版提供两个连续窗口A/B：默认按固定算法从父范围前部/末部选取，依据元数据P/bytes、模型固定开销和可用预算自动确定N/M；调用方可收窄。去重按RequestKey，A/B不得重叠；同时间戳以record_index稳定裁定，不以时间包络代替精确成员。
- 连续性是**在所选appid×来源×父范围的原始顺序内无跳过请求**，不是把元数据筛选后的稀疏集合叫连续。无法取得两个独立窗口，标`review_unavailable`，仍允许A诊断；不拼接、不重抽直到出现收益。
- 本版不实现Token探索的众数/长尾四层产品采样。将来可用通用成员manifest承载结构样本，但非连续集合只能作结构证据，禁止按真实到达序列展示H/C收益。
- 元数据投影仅取键、时间、P、原文摘要/字节长度和Token切片描述，不SELECT *；已有字段提取的SQL成本计入prepare。正文长度可用SQLite字节长度查询或有界BLOB分块读取，必须在Python完整物化之前拒绝超长，不把UTF-8字节与字符数混用。
- 先确定全部键及A/B用途、排除原因，再取正文；B正文在独立快照内封存，仅复核阶段可访问。prepare执行存储复制/摘要，不做B内容归因、模板选择或规则调整。
- 冻结前按预定顺序缩短窗口/选下一个元数据可容纳的连续段，记录尝试/排除，不能按收益选段。冻结后缺失/损坏/超限不能删一条再算连续窗口；需要缩样则自动建立有限次数的新attempt及新样本身份，保留旧原因，不能混算。单条或模型本身无法在支持环境加载须明确说明，不泛化为总数据量大导致mem_limit。

### D2.2 来源校验成本不藏进小样本

旧来源没有独立可信抽样索引。推荐最小实现为**明确诊断请求自动编排受控prepare，产生仅含入选成员的封存快照**：

1. API只校验请求形状、来源引用和自动profile合法性，登记诊断及prepare receipt后返回；不在提交路径hash全源/加载tokenizer。不得因父scope请求数或总体积大直接拒绝，应进入自动缩样。
2. prepare worker核验manifest、目录边界、完整文件摘要；固定小chunk检查取消、累计字节/时间，计入verification_bytes。校验I/O按已知源文件大小及验证次数单独规划，不用小样本raw_bytes额度拒绝大源；不是全量正文分析。超时需明确准备阶段未完成并可重试，不能谎称满足底线。
3. 在只读连接/稳定文件身份下读取已选成员，逐条校验raw SHA、编码身份、P、slice SHA，复制原始完整正文及Token slices到本任务独立工作目录；限制单条/累计bytes、P和磁盘。不重新编码整个来源。
4. 复制前后验证来源一致性；首版允许两次完整seal验证，均受同一prepare预算约束。未建立跨文件一致性或来源变更即丢弃未封存候选并报`SOURCE_CHANGED`，不能把mtime缓存当完整性证明。无并发修改才可封存来源快照。
5. 封存小快照、成员manifest和prepare receipt后，由独立诊断任务消费；诊断迭代校验快照，**不再递归回源验证整份CSV**。重新使用快照要匹配source/成员/编码/profile摘要，不能自动扩充成员。

prepare不是“免成本小样本”；新快照是原版本数据的有界派生证据。源随后变化不改变已封存快照的身份，但不得称“当前最新源”；延期的显式全scope评估未来须另准备并核原身份，本期不执行。失败/取消prepare不发布可用样本。

首版不加全源可信缓存、Merkle格式或改写历史run。大源分析/编码内存由样本上限决定；不能仅返回“预算不足”就算完成底线。若流式完整校验在目标规模仍不能按验收profile完成，V3B001/V3B007保持阻断，评审补充可信索引方案；不删校验换通过，不隐藏第一遍I/O成本。

### D2.3 SampleManifest3（逻辑字段）

`version, sample_id, parent_source_identity, parent_scope_selector, sampling_algorithm/version, requested_windows, windows[{window_id, role, ordered_request_keys, request_count, ordered_keys_digest, contiguous, snapshot_ref, snapshot_sha, raw_bytes, baseline_p}], exclusions[{key, reason, observed_metadata}], source_verification_receipt, budget_snapshot/digest`。

- source身份保留asset、encoder、profile、settings、algorithm、run/index/manifest摘要；request记录有raw SHA、时间、P、Token引用。公开响应不内嵌全部正文。
- raw、Token数组只在有界工作目录；元数据列表也有条数/字节限。
- sample_id摘要包含成员顺序及抽样规则；相同内容不同请求仍各自保留。新结果同时保存父范围、入选分母、可评估分母，禁止将样本N显示为总体N。
- 可用`SampleResolvedSource`适配已有评估核心，但每窗独立scope_id/key digest及`selected_window_recomputed`语义；任何旧函数不得通过原source._rows绕过成员限制。

## D3. 资源、取消、恢复与部分结果

### D3.1 预算计费

自动profile预算正整数、版本化、摘要固定；先扣除模型固定开销/服务安全余量，再用元数据计算可接纳窗口，先reserve后执行，记录limit/consumed/stop_location及缩样理由。用户无需手动试sample_limit；请求正文不能改变执行策略。

| 预算类 | 边界与计数 |
| --- | --- |
| prepare来源 | metadata rows/bytes、verification读字节、读取时间、选定requests、单条/总raw bytes、P、快照磁盘；整源hash与选样正文分账。 |
| 解析/比较 | 单条raw bytes、结构深度/节点数、单对/累计比较字节；总物理比较数及各通道计数；已读body/Token bytes分别统计。 |
| 编码 | 调用数、单次输入字节与原P预估、实际输出Token及累计编码Token工作量；before/after均计入。实际超限的单次调用由子进程时间/内存硬边界保护，不宣称事后Token检查能抢占tokenizer。 |
| 结果 | 唯一原因组、成员/代表证据、plan操作数与字节、评估数、总产物磁盘；超限只保留允许的元数据和明确未完成原因。 |
| 时间/资源 | 整任务及阶段deadline、CPU线程数、worker进程树内存、清理宽限；包括模型加载、比较、编码、结果封存。 |

V2 candidate_limit仍解释为每请求前序候选上限；V3保留1–128作为局部检索保护，新增真正的task total比较预算，与通道份额分开。通道总消耗不得超过task total，不把V2两条lane各自max误记为一个全局总限。

正文通过单条/累计bytes准入后，先作有界JSON词法扫描，检查深度/节点/超长标量等，再构造完整Python对象；扫描正确处理字符串转义，不能用括号计数误伤文本。SQLite page cache、Token slice读取/转换、结构索引/排序及结果编码也有内存/磁盘边界，不能只限tokenizer。上述防线由B002验证，超深结构不允许先json.loads再补检查。

进程隔离：昂贵诊断/prepare计算在受控子进程，API/父监督进程只接收有界状态/对象引用；不经IPC传整份语料。运行平台必须声明可用资源控制能力，Linux优先受控cgroup或明确记录的RLIMIT限制与进程树监测，Windows用等价Job机制时另测。虚拟内存上限不能伪称RSS上限。无法提供承诺的硬限制时fail closed为`RESOURCE_ENFORCEMENT_UNAVAILABLE`，不得照常编码再宣称“有界”。

不建设通用分布式队列；复用单任务调度，避免同时加载多份编码器。禁止任意fork/外部命令；模型本地资产缺失明报，不在验证中临时下载或修改模型锁。

**内存硬门禁**：硬限是最后保护，不是正常大数据缩样机制。支持环境和目标负载下必须自动缩样后完成诊断/参考计算，OOM、mem_limit、内存杀worker均判失败。运行趋势超预估须在危险阈值前协作退出当前计算，有限次缩样重建attempt，保留调整过程；软阈值下正常退出与OOM/硬限杀进程分开记录，不能把保护性杀进程算安全通过。固定模型开销超过环境能力时单列环境不支持，不能用来掩盖总量导致的内存故障。

### D3.2 两个独立维度

- 执行状态：queued → running → completed / stopped / failed / interrupted。停止原因区分用户取消、预算、deadline；重启遗留running变interrupted，不自动续跑。
- 证据状态：none / partial / complete，与各阶段coverage及各窗evaluation状态独立。stopped允许读取已提交部分证据，但不是completed。
- 每个安全检查点写有界、校验可读的journal/checkpoint；只有完整评估窗口的事务才能写P/H/C after。失败窗保留checked/eligible和原因，after为空。
- 正常停止由父监督进程封存已提交检查点；强制结束时只采纳已完整提交且校验通过的检查点。临时文件或半个JSON不是证据；没有可用检查点就report_available=false。
- 取消与最终成功发布需要事务竞争规则：成功提交前看到取消必须落stopped；成功已提交后取消返回已终态，不重写已发布成果。
- retry总是新attempt/task身份，保留上一封存产物；引用同一快照/冻结变换时可复现，预算变化必须进入新意图摘要。旧任务不能自动抢救working目录。

日志和API仅记录必要元数据/原因，不把raw body、长Token数组、环境secret写入异常堆栈。产物路径须在当前项目指定workspace内，拒绝路径穿越。

## D4. 时间识别与受约束变换

1. 继续限定L1为system/developer可消费文本（含content块），L3为按工具逻辑名对齐的description；不扩到任意user/assistant历史。明确记录字段角色、JSON pointer、字符区间、原片段摘要/示例及实际Token LCP；字符位置不转换成猜测Token位置。
2. 日期识别支持ISO、斜杠年/月/日和中文年月日及其时间；做基本日期/时间合法性校验。时区/精度原样保存。无标签时间可以定位，但时间用途未知不能自动给“无损修改”。
3. session_clock先定位结构边界再识别内层时间槽；只支持定义清楚的闭合块，多个块分别定位，嵌套/不完整块输出unsupported/证据不足。外层块与内层时间不能双计、重叠删改；path与timestamp重叠按上下文消歧，实际路径中的日期不当时钟。
4. 自动变化归因要求两个请求的同一逻辑字段除目标动态槽之外的结构/文本一致；不是要求整个messages历史或工具数组都相同。相同固定日期、只有单条支持、完全不同模板不能生成“时钟导致分叉”的证据。已有path不同长度和CCH逻辑保持回归。正常诊断不得要求用户指定clock位置/recipe：自动识别、生成合格请求对与字段变化证据后才产L1 finding，再自动生成固定化改法和样本评估。可保留另行指定反事实入口，但其结果须标manual_counterfactual且不计自动L1通过；无合格对如实给证据不足。对同一可比system/developer逻辑字段，后续历史轮次及user/assistant/tool序列长度不同不得单独阻断比较。自动发现与评估预算分别保底，不能由高频候选耗尽。
5. **必做session_clock固定化**：对经验证的完整`<session_clock>…</session_clock>`内部替换为同一常量`NORMALIZED`，保留外层标签和块外内容，与报告变换形态一致。常量不得含请求ID/当前时间或按请求变化；多块分别定位，额外业务指令/结构歧义不盲改。明确记录时间/时区/说明被固定，动作仍为hypothetical_content_removal。日期槽定位、CCH/path回归保留，但普通日期槽删除不能替代这项交付；移动时间和其他业务改法不自动实现。
6. 业务用途未知时允许用户要求的离线固定化参考评估，但页面始终标“时间感知将改变，需业务确认”，不自动采用到真实请求。已知业务依赖时间时也不得称方案可直接采用；若明确禁止此反事实试验则仅保留证据并标business_constraint，不伪造参考数值。不新增业务策略编辑器。
7. recipe冻结slot_kind、逻辑key、标准shape、槽序号/上下文、变换版本/参数。自动L1发现后冻结允许角色、合法块语法、证据支持的应用条件和同一常量；针对各A中证据支持的字段shape记录适用范围，不要求整条请求/完整历史一致，不观察B后增加规则。指定反事实结果另记来源模式，不可冒充自动发现。通用动态recipe仍遵守自己的shape约束。每窗重新生成具体guarded operations，原文SHA/原值守卫必须匹配。复用PreparedMutation，不做全局正则替换。未改请求保持原raw及Token；改后保留协议合法性/数值词法安全，序列化变化明确记录，不能承诺所有JSON字节均不变。
8. 多槽组合只评估明确兼容的集合，预算内单独运行，不把单项收益相加；首版默认不枚举所有组合，是否提交某组合属于显式任务意图。

## D5. 候选覆盖与原因组

### D5.1 双遍有界发现

只对发现窗A做有界结构提取，缓存标准化特征而非无限保存正文；必要磁盘索引也计入预算。B不参与选择recipe/候选策略。

- **L1 channel**：同encoder/assets/effective options、同一可比system/developer逻辑字段角色与定位语义、该字段规范化形状；不将完整messages角色序列、后续历史长度或前两个历史角色作为L1必需桶键。字段外历史不同仍可比；字段角色不兼容、clock外文本不同、相同固定clock仍须负例保护。仅掩码已识别且上下文允许的槽，不以原始system SHA切桶。这里消除V3设计歧义，不声称V2按完整历史分桶；V2现有粗桶只取前两个消息角色。
- **L2 channel**：保留完整工具集合/定义相同、顺序不同的通道；使用现有tool_set_fingerprint，不按已排序的原数组做不可逆改写。
- **L3 channel**：允许共同逻辑工具名下description/定义不同，以及工具集合增减。用稳定的结构/工具关系作有限候选，不要求工具定义digest完全相同；增加/删除证据不伪装可执行变换。
- **L4/L5 channel**：保留既有消息差异与JSON表示差异比较能力，对未知结构提供预算受限的邻近回退；不因为L1分桶变严而消失。不同上下文不可强并为同一语义原因。

完成特征索引后，按channel→桶→时间段轮询分配比较，避免最前面的高频桶吃掉预算。每个current只取其前序候选；优先最近、最早代表和确定性时间分散代表（重复键去重，按显式K上限截取）。分散代表选择与迭代顺序固定，不能用收益高低挑候选。

总比较预算先分配已启用通道的保底份额，余量轮询借用；份额和候选算法版本记录在profile。本轮不设生产比例。相同物理请求对跨通道复用解析/Token结果，物理比较只计一次，通道访问另计。并非枚举桶内全部两两组合。桶不适用/预算不足/发现未完整分别报告；不对未比较对数虚构完整性。

### D5.2 前移去重与有界保留

按 `规则+变换/显式差异类型+逻辑位置+标准化上下文` 聚合。未知关联保持独立或GROUPING_UNRESOLVED，不按“相同错误文字”硬合并。

每组保存唯一请求数、观察对数、有限代表请求对/原文摘要、覆盖完整性；成员精确集合在受限磁盘索引中，超成员预算就下界+incomplete，不能用估计值填精确数。同一请求跨组可重复，组人数不可相加为总体影响人数。

在昂贵证据序列化和多份plan之前判断是否已有原因组。对原输入Token摘要相同的请求对不制造输入失配；真实LCP只对保留代表按统一Token slice读取计算，缓存受限。分别统计原文差异观察、输入确实变化、保留证据；不沿用旧detected名称混淆新计数。

重用现有recipe去重和L4/L5精确上下文分组；旧报告仍按旧计数解释。测试用同预算比较唯一原因覆盖，不要求线上收益或所有appid均出建议。

## D6. 精确改法、A/B（显式full延期）

- 冻结变换之前只用A发现并选定计划；保存transformation_digest、版本、条件、排除、业务假设、A结果。B执行只能应用同一变换规则并生成B的原值守卫，不允许参考B收益再调参。
- A/B各自有独立before/after空PrefixLedger，按manifest原顺序覆盖相同成员；before验证原编码/P/Token SHA，H/C由当前窗口重算。不存在“拿全量历史H作样本before”。
- 每窗保存N、P/H/C、H/P、ΔP/ΔC/ΔH/Δ(H/P)、匹配/修改请求数、完整性、配置身份和逐请求证据索引；同窗before与after键/顺序必须相同。统一整数/有理数计算，P=0时比率不可用，不填0%。
- B无适用对象→independent_review_no_targets；B预算不足→review_not_completed；B改善不一致→review_inconsistent；无B→review_unavailable。均可展示A已完成数值但不写“独立复核通过”。评估完整和收益正负分开；独立复核只证明该窗口数值，业务等价另记。
- 样本等于整个选定scope时直接评估该scope作为A，不触发现有pilot_scope的“必须更小”限制；若没有不重叠B，明确无独立复核。复用评估核心，不把旧pilot改名为B。
- 已封存的A成功不因B失败而消失；不完整B绝不发布完整after。原样/no-op必须精确复现；matched=0、modified=0和实算Δ=0分开。
- **DEFERRED_BY_USER（2026-11-11）**：以下全scope入口为未来约束，不纳入本期验收。全scope只有显式新请求：引用冻结变换、父范围/source identity、预算与独立prepare产物。范围、成本和结果与样本分开。自动full次数必须为0；不因超过1pp/5pp就排队full。
- 旧full/direct_full的旧优化资格不降低；新样本数值无正收益门槛，卡片标“样本评估/限制/业务未确认”，不占用旧low_hit_optimization定义。P/H/C或样本收益均不表示TTFT、吞吐、实际账单或答案质量。

## D7. 协议、旧结果、页面与Token休眠

### D7.1 新对象与状态语义

新schema建议标`diagnostics-execution-3`及`analysis-sample-results-1`，在新目录生成schema/examples/manifest；本轮未冻结。至少包含：

- PrepareRequest/Receipt、SampleManifest3、DiagnosticRequest3（snapshot refs、只选low_hit、预算、变换意图）、Execution3、WindowEvaluation3、RecipeOutcome3、Report3。
- RecipeOutcome3连接finding/group → frozen transformation → window plans → window evaluations → displayed outcome，保留无适用/业务限制/未评估/预算/取消/失败/无收益/负收益原因，不以NO_COMPLETE_FULL_EVALUATION覆盖所有状态。
- 执行完成、证据封存、评估完整、独立复核、业务确认、优化资格各有独立字段。引用绑定task/source/sample/window/scope/plan摘要，不凭前端推断。
- 示例至少含成功、零收益、负收益、A完整B失败、无B、无适用、取消部分证据、旧报告缺字段。schema不能将unknown/null强转成0。

拟接口：`POST /diagnostics/v3/source-preparations`、`POST /diagnostics/v3/tasks`、`POST /diagnostics/v3/tasks/{id}/cancel`、显式retry，以及相应capabilities/receipt/catalog/report/result只读GET。全scope评估入口已由用户延期，不在本期接口范围。实际命名在V3B001冻结提案快照，语义须按本设计；API重放/冲突/实例身份检查沿用原保障。

V3新结果使用独立目录/存储命名空间，V1/V2 catalog和冻结对象不塞入新状态。V3目录可聚合旧记录引用，附schema version并分派旧读适配；旧ready优先/partial回退规则保持。默认选源/原监控绑定不改；取消partial作为历史可选项，不自动覆盖最近完整报告。

### D7.2 写入口不允许绕过边界

V3运行配置下，旧diagnostics POST（submit、retry、低命中/组合/Token evaluation、Token authorization）统一检查执行策略；旧低命中新执行请求要求显式升级到V3意图，不能调用旧自动pilot/full；Token相关新执行返回明确休眠原因。历史cancel可安全终止本服务拥有的任务，不等于恢复它。

V3 worker只claim新V3队列，旧queued/running记录不自动执行、不破坏历史记录；需要迁移/重试必须显式建新V3低命中任务。legacy测试环境可保留旧执行语义以验证历史代码，但生产V3入口不暴露绕过开关。bootstrap懒加载Token运行组件，旧报告序列化/读取仍可用；不修改Token私有检测逻辑。

### D7.3 页面最小兼容

保留四入口、原L4/L5布局、历史来源绑定与完整请求对照。V3新增信息只进入现有报告范围/状态/建议解释区域：

- 五组目标必须显示标题“session_clock固定化”、精确前后片段、常量、样本参考提升率（百分点）及前后命中率；不能仅有L4卡片或后台实验。明示N/父范围N、A/B用途、原顺序冷启、自动缩样/排除原因；P/H/C并列，负收益不涂绿。
- 所有已尝试recipe的结果可查；无适用/未评估/零收益/负收益分别可见，不仅显示达旧门槛卡片。
- L4/L5仍无需通过收益门槛即可读取；数量按已保留/覆盖解释。
- Token入口保留旧成果，显示本版本新分析休眠；缺旧报告与“无异常”分开。
- V3客户端按对象版本选择校验，不能关闭AJV、BigInt或引用/分母校验来接入样本。
- 页面GET/刷新/翻页/切换方向/打开历史均不得产生POST任务或补算。当前不建设网页提交向导，显式准备/分析通过受控API/CLI进行；不改变批准展示主体。

## D8. 错误、兼容与完成定义

来源/编码/资产变更、缺片段、无效JSON、异常日期、错位路径、越界索引、超大整数、深度/节点爆炸、磁盘满、进程崩溃、重启、重复提交、取消竞态均须有确定错误或受限结果，不输出半份完整收益。

共享实现变动必须回归编码与监控关键路径；旧契约manifest不得改变。测试中使用历史产物隔离副本，不写真实旧state；本地合成数据不替代华为实测。

实现过程按[V3B001–V3B007](BATCH_PLAN.md)串行门禁，每批都有PLAN、ISSUES、TESTS、CLOSE和记忆增量。最终逐D0–D8对比实际代码/测试/页面，不能只给总测试通过数。未闭环必需项不进入下一批；普通批内bug由本线修复，范围/协议/业务语义重大变化退回评审。

V3B007若仅完成本地工程门禁，可标LOCAL_VALIDATED并交待现场验证的候选；五组真实业务证据缺失时不得标总体验收CLOSED，具体见[ACCEPTANCE](ACCEPTANCE.md)。本次两项计划修订核对完成后按条件授权实施，无需重复启动确认；镜像打包始终须单独用户同意。开发最终交付给镜像会话的是源码候选身份、变更清单、验证证据、风险及回退说明，开发/debug仍由本线负责。


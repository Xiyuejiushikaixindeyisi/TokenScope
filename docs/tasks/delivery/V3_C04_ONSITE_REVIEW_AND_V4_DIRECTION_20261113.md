# C04现场报告核对、重复clock展示解释及V4方向

> 后续补证已核对，主要疑点及V3收口判断以[补证核对](V3_C04_SUPPLEMENT_REVIEW_AND_CLOSE_20261113.md)为准；下文保留首次报告审查时状态。

2026-11-13；镜像打包与审查线，只读源码/报告并更新本线文档，不执行现场、不改产品、不派单、不构建或Git提交。本人ID从Windows环境CODEX_THREAD_ID/CODEX_SESSION_ID核实为01a1800e-80b4-7400-a78b-a84f5b6e888d；WSL子进程未继承这两个变量，不据此换用他人ID。

用户认为多个同类clock条目不是bug，要求解释并讨论V4：0汇报优化；1 Qwen3.6→3.8、GLM5.2→5.3、DeepSeekV4→V4.1；2工具结果重复/巨大返回的Token异常研究。本轮是阶段判断和建议，不是已批准的开发方案，不自行改前端或唤醒旧session。

## 证据身份与结论边界

原始回传[HUAWEI_V3_C04_ACCEPTANCE_REPORT.md](../../huawei/HUAWEI_V3_C04_ACCEPTANCE_REPORT.md)，SHA256 `9a9fc02d369409838cdf1597e95ba2085f7bc804007d913aaad86436024c8daf`，原文不改。报告声明产品commit57fe9f64d78f6363ee18a12ff97693e00ae1fe3d及镜像f2162dfc…，与交付身份一致。当前关键源码clock_discovery_v3、session_clock_v3、candidates_v3、clock_worker_v3、evaluation_v3、sampling_v3、runtime_v3、前端features/analysis/sample-model.ts已逐文件与固定commit比对一致。本轮未取得现场原始report.json或直接访问华为，区分“回传声称”“源码事实”“用户页面观察”。

判断：可以进入V4需求/方案阶段；监控与部署有现场正面证据，但不能凭这份摘要把六组异常的完整收益和证据链标为全部通过。需先补清报告关键字段；补证不要求重跑全量监控，也不自动认定产品bug。用户本机已批准的UI仍保持。

报告记录3真实用户run ready（有效150698行）、9对MA completed、ICSL监控ready、重启后目录与六报告保持，旧state关键SHA未变。MA缺数例中real覆盖为0且cached缺失，支持该例数据限制解释；报告对“全部MA”的概括缺少逐UUID完整证据。Qwen全量监控约3.5小时、内存峰值30.3GB/32GB，只能说明该次未OOM，不能说明资源余量充裕。现场前端视觉仍由报告标PENDING，不能代替用户签字。

## 为什么出现六条同名clock

源码处理链：固定来源→按预算选小样本→按字段/模板等分桶→有界候选配对→发现规则→编译模板适用的修改方案→每方案单独样本回放→一方案一卡。

1. [session_clock_v3.py](../../../src/tokenscope/prefix_analysis/session_clock_v3.py:98)只识别system/developer消息中的受支持clock标签文本；不是遍历所有JSON日期就建议删除，也不据标签名推断真实session。
2. [clock_discovery_v3.py](../../../src/tokenscope/prefix_analysis/clock_discovery_v3.py:90)要求同logical_field、遮掉clock内容后field_shape一致、clock合法时间内容变化、编码输入不同。recipe包括logical_field、field_shape、block_indices，constant=NORMALIZED。
3. [去重](../../../src/tokenscope/prefix_analysis/clock_discovery_v3.py:215)按整个recipe摘要去重，而非按L1或标题去重。六条clock按该实现意味着六个不同转换签名，可能是不同消息槽、不同模板或不同clock块组合；不是同一个方案因六对证据简单复制六遍。报告没有嵌六个完整recipe，因此尚不能逐条断言它们具体差在哪个字段。
4. [编译](../../../src/tokenscope/prefix_analysis/clock_discovery_v3.py:347)在样本内匹配该recipe的所有请求，替换合法标签内内容为NORMALIZED，保留外部文字及标签。它是可执行的样本假设方案，但会改变时间感知，不等于业务安全或线上自动应用。
5. [前端](../../../apps/viewer/src/features/analysis/sample-model.ts:10)逐recommendation建卡，但所有clock用同一标题/描述。无法从标题看出模板/字段/覆盖差异，是本次困惑的直接来源。“收益不可相加”已在conditions里，但[Reports.tsx](../../../apps/viewer/src/features/analysis/Reports.tsx:27)把它放在可折叠的适用前提说明，不够突出。

## 收益为什么不能相加

[evaluation_v3.py](../../../src/tokenscope/analysis_common/evaluation_v3.py:90)公式为 `100 × (H_after/P_after − H_before/P_before)`，单位百分点。每个方案从相同窗口的原始baseline出发；每次after是独立的前缀缓存账本，完整回放该窗口全部请求（含未修改请求），不是把前一方案结果再修改后得到的增量。

因此5/11/10是三次“各自只做这一项”的对照，不是顺次累加的步骤。即使适用请求不重叠，跨请求缓存共享、前缀相互影响和编码后分母变化也使简单求和没有保证。合并收益必须明确兼容性与冲突，合并操作后重新编码及回放一次。当前V3没有这一组合评估结论。

例（仅说明算术，非现场值）：原始样本命中率30%；A独立后35%、B独立后41%、C独立后40%，不能据此宣称组合56%。报告未提供用户看到的5/11/10等数值的完整before/after整数，本轮不计算该appid总收益，约30%不能作为汇报结论。全量监控34.81%也不自动等于小样本baseline。

## 报告中需要核正的关键解释

| 报告表述 | 固定源码事实及判断 |
|---|---|
| clock recipe为null，不能自动执行 | ClockFinding3.recipe为必填ClockRecipe3，含version/logical_field/field_shape/block_indices；没有prefix专用kind/pattern字段不等于recipe为null。clock确有独立编译/回放代码。可能为报告取错字段，但未见现场JSON，不能断言具体错误脚本。 |
| admitted=1047等于1047全部纳入样本 | SamplingDecision.admitted_count是元数据准入数量，窗口members才是实际选中。源码明确members受count/raw/token预算限制；必须读取decision.windows的成员数及evaluation.n。不能把父集/准入数当小样本N。 |
| CAUSE_EVIDENCE_TRUNCATED导致window_evaluation提前停止，sealed examples未生成 | 该原因来自collect_clock中每条规则cause_groups达到128的分支，它置discovery.complete=false并跳过新cause组；不直接停止整个采集循环或评估。clock_worker在之后仍为finding封存example并逐方案计算。任务最终stopped可以只是discovery非穷尽，不等于所有window没算完。 |
| findings/report checkpoint complete=true说明发现完整 | checkpoint发布完成不等于discovery.complete=true，也不等于每项window.complete=true。必须分别读取。 |
| 六组evidence_refs=0且有推荐，因正常小样本预算所致 | 固定worker在首次发布report前为每条finding保存sealed example，并填顶层report.evidence_refs；与此解释不相容，需要核验实际顶层字段及最新report身份。不能据摘要断言正常，也不能据摘要直接改代码。 |
| ICSL“跨对话稳定、同对话变化” | 已验收revision3是同对话稳定、跨对话变化；报告说反。 |
| MA全部缺数均数据原因 | 一个DeepSeek例有明确coverage证据；全部UUID的结论还需逐项核对。不是补0或调整算法的理由。 |

报告的源CSV SHA有省略号、源码多数只有路径没有代码、curl命令含Markdown链接语法；不满足完整可复核的单文档证据要求。保留原报告，本核对文档补注，不改写原始证据。

最小补证（单Markdown追加即可，无需重跑）：六组各自完整execution state/reason、profile.version、discovery.complete/reason_codes、parent_count/admitted_count/各window实际members数；recommendations逐项finding_id/transformation_digest/完整recipe（大模板可用外部形状SHA+定位差异和足够原文）及windows的role/n/matched/modified/complete/status/before/after/improvement_pp；顶层evidence_mode/evidence_refs数量和至少一个实际example响应；BUS01列六方案覆盖请求交集或不重叠证据。原文中原始数字/字段必须保留，说明报告取值方式。只有字段缺失/真实评估失败时才安排针对性复测，不重跑监控。

## V4方向建议（待产品方案批准）

### 0 汇报优化优先

保持四入口与既有页面布局。把同类clock作为“时间动态字段问题”汇总，子项区分消息位置、模板/业务描述、覆盖请求、方案编号及样本before→after；不向用户只展示六条相同标题。分组仅改善呈现，不能粗暴去重丢失六种适用范围。提示“单方案独立收益，不能相加”放在可见收益区。总体收益没有组合实算则写未评估，不求和、不用最大单项冒充总体。

让用户先看到“什么问题→影响哪些请求→改哪里→样本收益→语义风险”，再展开探测器规则/证据。clock定值是反事实评估，不是对时间敏感业务的默认上线建议。汇报必须区分合成ICSL、真实样本效果及未测线上业务收益。

### 1 模型演进

用户目标名称Qwen3.8、GLM5.3、DeepSeekV4.1作为待接入规格，不在本轮外推官方资产可用性、与旧模型兼容性或性能。开发前固定实际服务模型ID/别名、tokenizer与chat template revision/SHA、thinking模式和协议、block设置、MA模型制品映射、TTFT参数。不是简单重命名旧目录/标签。

旧模型身份和结果保留可读；新模型独立身份/结果。相同原始请求分别按旧/新真实编码配置回放可用于离线计量差异，但不能伪称新模型线上命中/业务效果。新TTFT chunk_seconds重新提供或标待配置，不能自动沿用1/2.7/2.6秒。先小样本资源/契约/展示验证，后按现场授权扩大数据；Qwen旧版接近32GB上限作为资源验收约束。

### 2 Token工具异常：先重复载荷与过大返回

优先研究同一完整请求内的跨tool消息重复、单个JSON内重复对象/数组/嵌套载荷，以及单次巨大返回；区分跨请求携带历史与同请求重复，也不能由重复文本推断工具重复执行或Agent死循环。

复用现有T3 [duplicates.py](../../../src/tokenscope/token_content/duplicates.py)，其已做类型化规范值精确核对、哈希后内容确认及父子重叠去除；[extraction.py](../../../src/tokenscope/token_content/extraction.py)有嵌套JSON展开。不能先假定必须新造一个探测器；先用真实样本验证当前覆盖缺口。大返回基于任务/工具类别和业务保留字段说明体量与候选风险，不用统一长度阈值推断无用。

既有[Token长尾核对](../product-v3/V35_TOKEN_TAIL_ASSESSMENT_20261110.md)记录天舟的重复tool载荷、Qwen约202071字符的搜索返回等现场线索，属于回传证据，不是本轮独立复测。可优先用于V4需求样本，不照抄“只保留最近3个”等未经业务验证策略。

规则输出分三层：可证明事实（内容/次数/位置/规模）→需业务确认的候选方案（去重、字段裁剪、分页/引用）→同样本完整变更回放的真实Token变化。重复不等于安全可删；巨大不等于无用。Token方向主要看输入P、未命中C等绝对量及业务质量，不能只要求命中率提升；删去大量已命中的冗余Token可能让命中率下降而总计算量仍下降。精确收益用完整修改请求重新编码，不把字符数/局部token估算作为可兑现节省。

资源预算沿用有界样本、逐请求/逐方案释放与实际容器限额，避免把全量JSON常驻内存。工具协议关联、必要信息保留、误报/漏报和业务任务质量必须进入验收。

建议顺序：先核正V3证据及汇报口径→冻结V4展示和模型资产契约→真实工具样本研究/有限开发→独立验收及授权交付。本轮不发送派单，不把方向讨论当作编码或打包授权。

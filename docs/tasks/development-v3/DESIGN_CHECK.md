# V3最终源码与设计对照

**当前范围决定（2026-11-11）：显式 full 延期（DEFERRED_BY_USER，未实现/未运行，不记PASS），不再是本期V3门禁；自动full仍禁止。候选repair-r1-02为LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING，独立R2已关闭RV3-01/02/03。大源自动缩样和五组session_clock样本参考率优先，真实BUS01–05及现场AC-MEM待华为验收。暂不打包。**

本条为最新状态，覆盖下文历史“待裁定/待独立复验”；原日志、原失败与当时勘误保持。B005按修订范围CLOSED；B007本地收口，整体现场门禁未关闭。见[本地收口](LOCAL_ACCEPTANCE_CLOSE_20261111.md)、[华为交接](HUAWEI_ACCEPTANCE_HANDOFF_20261111.md)。

**最新：独立验收R1原NOT_ACCEPTED；三个阻断已本线修复并验证，等待独立复验，先前LOCAL_VALIDATED不代表接受；见[修复记录](REPAIR_R1.md)。**

2026-11-10，LOCAL_VALIDATED。依据DESIGN r1，不修改历史CHECK结论；当前实测以B001–B007 TESTS/CLOSE及最终attempt15为准。身份：HEAD 9a071c87b517490e497aa6cc1e53ec066bb4ede0加未提交源码；精确source/dist/运行身份见 `artifacts/validation/development-v3/V3B007/attempt-15/`。此目录不是交付包。

| 条款 / 测试 | 具体实现 | 实测与限制 |
| --- | --- | --- |
| D0/D1 自动链，T24 | api/diagnostics_v3.py；analysis_common/service_v3.py PreparationService；clock_worker_v3.py；viewer SampleDiagnostics.tsx | 正常监控来源、无预定recipe，浏览器显式启动，自动clock证据→改法→A/B→封存→展示。最终三场景通过。 |
| D2 范围先行，T01–05 | source_preparation.py、sampling_v3.py、sample_source.py open_sample_window | 元数据选择连续前/后窗口后才读取选择正文；源整体seal校验是流式且预算计费，不称O(样本)。快照身份/同键原序/改源拒绝/大单条边界见B001/B002。2200自动1024且零排除，不由用户调limit。 |
| D3 隔离/预算，T06–09/T25 | runtime_v3.py BudgetLedger；supervisor_v3.py；worker_v3.py；execution_v3.py；preparation_store.py | AS/CPU/FSIZE、取消/父死亡/阶段超时/写满/半文件与发布竞态测试；共享worker锁，健康API不在昂贵worker。B002真实20次延迟与取消门禁，B007全回归/大源。RSS是采样，不是硬RSS限；资源不够模型固定开销时允许明确拒绝，非任意输入无限承诺。 |
| D4 clock识别/精确改法，T10–12 | prefix_analysis/timestamps.py valid_timestamps；session_clock_v3.py；clock_discovery_v3.py collect_clock | ISO/斜杠/中文日期、合法日历、文本结构块；system/developer逻辑字段可比，后续history不同不失配；固定clock、嵌套/额外指令等负例。仅块内部NORMALIZED，原值守卫/块外保留；changes_time_awareness明确业务未确认。 |
| D5 候选与原因，T13–15 | candidates_v3.py CandidateSchedule/feature_keys；clock_discovery_v3.py collect_clock | 每current候选K上限独立于全任务comparisons预算；通道/桶/时间轮询，共享物理对缓存；L2/L3保留、L4/L5回退、成员准确去重与partial下界。47请求同预算12比较oracle对旧索引支持改善，不推断普遍最优。当前有界样本成员精确集合驻内存、受请求/结果预算约束，没有另建无界磁盘成员索引。 |
| D6 A/B实算，T16–19 | analysis_common/evaluation_v3.py evaluate_window/WindowEvaluation3；clock_worker_v3.py；diagnostic_store_v3.py | A-only选定recipe，B仅应用冻结变换；两窗各before/after独立生产PrefixLedger与统一EncodingContext；逐行/守恒/有理数。真实B硬退出仍能读已封存A。独立oracle另用字面Token前缀算法核四窗一致。小范围A=全scope、无B明确不可复核。 |
| D6 full边界 | V3注册与diagnostics_policy_v3.py、SampleDiagnostics.tsx | automatic_full=0，旧写入口409，新界面没有全量快捷入口。当前候选未提供显式扩大全scope的新执行入口；不得把“不自动full”说成已交付全量分析产品功能。未找到最新用户明确取消此设计项的依据；保留UNIMPLEMENTED_DESIGN_ITEM等待范围裁定，不当成已获豁免。 |
| D7 新旧协议，T20–23/T26 | contracts_v3.py/report_v3.py/wire_v3.py；sampling/report schema；viewer api/analysis/sample-v3.ts | 新协议独立schema及BigInt验证；身份/守恒/正负/计数/整数边界验证；原wire.py字节恢复，H0冻结通过。typed-map只在新wire扩展。旧生产低命中/Token结果GET相同，旧写和Token新任务关闭。 |
| D7 前端解释 | SampleDiagnostics.tsx；AnalysisApp.tsx；execution.ts | 显示精确修改、请求对、A/B范围/N/P/H/C/参考百分点、适用/修改/零收益/未完成状态；正收益不作为显示门槛。保留原四入口和旧报告区；404旧服务降级、存储不可用、刷新重连不POST。首次独立小样本面板不是新模板分组功能。 |
| D8 统一验证，T27–30 | scripts/validation/v3_*；B007 TESTS/ISSUES | 最终冷启动、独立oracle、重启报告SHA、截图人工核看、退出端口均完成。Python首次873/17，受影响61与全unit653复验；viewer345+browser12；不隐藏历史fixture3skip/旧脚本lint8项。五业务NOT_RUN。 |

## 事实边界与交接

本地三个真实HTTP/浏览器案例中的“真实”指实际运行产品、模型tokenizer与计算，不是华为真实业务数据。DeepSeek合成参考39.83pp/42.40pp及Qwen0pp不可填进BUS01–05。B是独立不重叠时间窗口，不是旧pilot自动full，也不是业务无损证明。路径值长短变化本身不导致text_shape漏检；没有以提升candidate_limit替代全预算治理。

最终候选源码SHA已核未变；候选截图v3-large.png、browser-results.json、independent-check.json、restart-browser.json、restart-02-shutdown.json、resource-summary.json提供证据。历史B002-I04覆盖损失持续披露，不把新校准当旧证据恢复。公共Token读取兼容测试不构成T2–T4开发；P1、hybrid、自进化Agent未恢复。

下一步仅供用户安排候选审查、授权打包及华为现场验收。本线负责后续debug，不向打包会话派发开发任务。没有自动Git合并、镜像构建或现场命令执行。

## 独立验收R1修复对照（候选已完成定向/E2E，全回归收尾）

原上表基于clock重点链的自验不足以证明既有规则完整保留，独立验收已纠正。以下实现覆盖RV3-01/02/03，不能仅引用原纯函数/旧报告测试。

| 阻断/条款 | 修复位置 | 正常新执行证据 |
| --- | --- | --- |
| RV3-01 / D4,D6 | prefix_findings_v3.dynamic_fields/pair_prefix/recipe_target/compile_prefix_plan；candidates_v3.feature_keys | CCH/普通斜杠时间/workspace三组不预置recipe，由新worker自动发现、guarded修改、A实算、页面参考；独立oracle核数。逻辑role/ordinal不因历史位置改变而失配。clock内槽不走普通删除、合法clock块外动态槽仍支持；非法clock结构不绕过约束。 |
| RV3-02 / D5,D6 | 同模块sort_tools；clock_discovery_v3.collect_clock对空/不交集工具集比较；evaluation_v3.evaluate_window联合分派 | 工具排序与description动态路径正常自动建议/评估；增删真实cause/完整对照、无虚构变换。L2摘要不重复；工具描述变换与集合差异明确分开。 |
| RV3-03 / D5,D7 | EvidenceRequest3/CauseGroup3.comparison；SampleDiagnostics.SampleReport完整原文双列 | 按完整raw SHA去重请求记录；只有两个完整原文内容相同时共用原因代表，成员并集，绝不推断session；L5专门负载浏览器可展开两完整请求，原样JSON/摘要一致。每规则128独立组/原文四分之一元数据界限，超限显式partial，不把摘要当全文。 |
| 同源精算/状态 | PrefixFinding3/PrefixRecipe3；WindowEvaluation3共享生产计量；wire_v3分支恢复 | 同样本整数守恒、B复核冻结变换；A-only/A+B14正常worker场景，两个编译分派的budget/cancel/no_target/no_op状态回归。CCH原文变而输入相同明示source_change_input_identical，实算0pp，无因果伪证。 |
| 协议/兼容 | report_v3联合类型；wire_v3 required/const/enum；sample-v3.ts原文/请求对SHA校验 | ClockFinding结构不变、CauseGroup新字段可选，旧结果缺全文明确提示；新report schema摘要773e1ae2f964143374168489da90fda119fd6dbbd1b48d1147eb32e7ef8f8066。旧H0 wire原SHA不变。 |

最终R1运行目录 `artifacts/validation/development-v3/V3B007/repair-r1-02`，302文件source manifest SHA `1fb8c3dc6a03dc49ddeb4c4cbc8b260c4ebc79e1cc60cfe04dcdcc5ee2fad820`，变更清单final-check.json；前端REPAIR-R1/attempt-07/dist。10真HTTP/浏览器、9窗独立oracle、10历史报告重启摘要不变已通过；定向38、viewer352、旧browser12及静态通过。具体全回归与失败保留见[batches/REPAIR_R1/TESTS](batches/REPAIR_R1/TESTS.md)。开发自验不替独立验收，当前不准打包。华为五BUS依然NOT_RUN。

## 2026-11-11独立复验状态同步
独立R2已关闭RV3-01/02/03，本地已实现小样本链通过；不是全部设计通过。显式full D6/T19未实现、未获延期豁免；五BUS及现场大负载仍待验。用户本轮要求解释差异和继续闭环，暂不打包。权威差异说明：docs/tasks/development-v3/FULL_SCOPE_GAP.md；独立结论：docs/tasks/product-v3/acceptance-v3/REVIEW_20261110_R2.md。

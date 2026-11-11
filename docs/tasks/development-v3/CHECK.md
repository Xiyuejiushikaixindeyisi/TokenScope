# V3 四项 P0 独立 check

2026-11-10；角色：全新 V3 代码修复与开发；实际 THREAD/SESSION ID 均为 `01a1c449-6a9b-7a83-912a-5a9ff77c703d`，由本会话环境读取。当前仅接入与只读核查，优先级 P0；实施依赖 Token 长尾报告回传、详细方案讨论及用户后续授权。

## 核查身份与结论边界

- 根目录 `/home/zhangxiyue/TokenScope`；核查时 HEAD 为 `9a071c87b517490e497aa6cc1e53ec066bb4ede0`。只读 `git diff --name-only c1345b6 -- src tests apps` 无输出，相关产品目录与报告所述 HV2 源码基线一致；HEAD 不代表新产品发布。
- 输入为[当前范围](../product-v3/V3_SCOPE_AND_HANDOFF_20261110.md)、[修复简案](../product-v3/V3_LOW_HIT_REPAIR_BRIEF_20261110.md)、[低命中实际回传](../../huawei/TOKENSCOPE_V3_LOW_HIT_EXPLORATION_20261109.md)及[Token 探索要求](../product-v3/HUAWEI_TOKEN_TAIL_EXPLORATION_PROMPT_20261110.md)。实算低命中报告 SHA256 为 `d321426897f785cf0ec2e665b5e21f1f54cd6b9478a174fad412956656882963`，匹配入口。
- 下述“确认”指源码分支及测试断言的静态核对。本轮未运行产品、纯函数实验、测试或现场复验，未读取实际 state；测试文件存在不等于本轮通过。报告收益、资源测量和现场任务关联均未独立复现。
- **四项 P0 方向有依据，但不能将已有能力视为全缺失，也不能把报告的根因和参数建议直接当实施方案。** 必须补查全源校验成本、按比较通道计费的预算、取消后的证据发布，以及实验状态到页面之间的信息丢失。

以下源码路径相对 `src/tokenscope/`，行号对应上述核查基线。省略目录时，`service.py`、`source.py`、runtime、execution、evaluation、contracts、encoding、storage 及 recommendation publication/pipeline 均指 `analysis_common/`；dynamic、detection、experiments、structure、history 及 recommendation groups/projection 均指 `prefix_analysis/`。L2 的 service 文件另明确写为 `prefix_analysis/service.py`。

## P0-1：有界小样本诊断与资源控制

**已确认与需要纠正的判断**

1. 范围过滤已有一部分提前生效。`analysis_common/source.py:131` 的 `SourceResolver.resolve_scope()` 只查询指定 appid/时间窗的请求键并计算摘要；`ResolvedSource._where/_rows()`（39、47 行）在 SQL 中过滤，再读取正文。`service.py:369` 的 `_preflight()` 先检查 scope 请求数，再逐条检查正文/累计字节和深度，位于检测 JSON 解析和评估编码之前。因此“先解析全部正文才限制”不准确；但请求数超限是拒绝整个 scope，不是先选出小样本。
2. **昂贵读取仍早于任务预算。** `DiagnosticService.submit()`（`service.py:78`）在建任务前解析 scope；`source.py:155` 调用 `verify_seal()`。该函数（`monitoring/pipeline.py:64`）遍历 manifest，用 `file_digest()`（41 行）读完每个文件，包括 `input.csv`、`requests.sqlite3` 及所列 Token 分片。worker 初始 `source()`（`service.py:141`）和每次 `iter_requests()`（`source.py:92`）也再次校验。它是分块读文件，不足以证明整份文件驻留内存或 OOM，但小时间窗不能限制这些全源 I/O，校验函数也没有任务取消/时间预算入口。
3. `_preflight()` 的单条字节检查在 SQL 已返回完整 `request_input` 后；不能保护首次大正文分配。`pilot_scope()`（`prefix_analysis/experiments.py:39`）通过 `source._rows()` 的 `SELECT *` 遍历整个所选 scope 才保存键/时间，亦非正文读取前抽样；它只保留元数据列表，并非持有全部正文。
4. 现有预算可复用：`runtime.py:12`、`execution_v2.py:33`、`runtime_control.py:39/73/81/88` 提供请求/累计字节、深度、比较、编码调用、plan、保留数量/字节等限制，V2 有分方向控制和分规则保留。当前低命中任务未见累计 Token、运行时长或进程内存硬预算；编码调用数不能代表 Token 工作量。`checkpoint()` 仅协作式检查取消，单次校验、解析、编码内部不受其抢占。
5. **partial 与取消不是同一发布行为。** 检测比较超限可返回已保留 findings 并发布 partial；preflight 超限在 `service.py:349` 进入 failed，尚无报告。取消会抛出 `ANALYSIS_INTERRUPTED`，`storage.py:146` 的 `complete()` 拒绝被取消任务发布，`result_directory()`（191 行）只读有发布摘要的产物，重启恢复也不抢救未发布结果（104 行）。因此“取消保留可读部分证据”尚不是已有能力；不能靠暴露 working 目录或放宽完整收益校验实现。

**必须补齐**：把入选范围及准入放到昂贵正文读取/解析/编码之前，并明确全源完整性校验的成本与可信身份保障；补齐工作量/时间控制和可取消边界；区分已完成证据、未完成评估、失败与取消的发布语义；小样本结束后不得隐式扩大范围（见 P0-4）。不能直接去掉 seal 校验以换取性能。

**可复用 / 约束 / 最小范围**：复用稳定请求键、时间顺序、scope 摘要、预算异常、telemetry 与封存读取；最小涉及 `source.py`、`runtime_control.py`、`service.py`、必要的校验调用和发布边界。若需扩展样本身份/状态，再评估 `contracts.py`、`execution_v2.py`、`storage.py` 的兼容扩展，不预先改冻结契约。前端只需承接范围、排除原因及完成状态。单条超长如何排除、取消保留哪些成果属于产品取舍，不能静默截断正文。

**本轮可确认 / 待报告**：上述调用先后和缺口可静态确认；资源默认值、分层抽样所需元数据、长尾预算排除的分母以及具体验收负载要结合 Token 报告再定。服务响应、取消延迟、峰值内存须后续获准实测，报告“约 2–3GiB”不构成验收。

## P0-2：L1 时间字段 / session_clock 识别定位

**已确认与需要纠正的判断**

1. `prefix_analysis/dynamic.py:9` 的 timestamp 仅覆盖当前连字符日期模式，不覆盖斜杠/中文日期，未见 session_clock 专用结构识别。`slots_in_text()`（29 行）按起点优先、同起点长片段优先排除重叠；path 可能吸收日期的一部分、时区或标签片段。报告 C.1 的 `2026/10/20 15:00:29` 与 `15:00:58`，时间仍留在非槽文本，`dynamic_recipes()`（52 行）的完整 `text_shape` 相等条件无法满足。此判断由代码推导，非本轮运行结果。
2. **路径值长度不同不必然漏检。** `text_shape()`（42 行）将整个匹配 path 换成槽类型，匹配值长度不进入 shape。若报告 C.3 两条路径以外文本一致、slot 类型及数量一致，`codex_alone` 与 `frozen_evox` 长度不同不阻止 recipe。真实完整请求是否还存在其他差异/重叠/槽外时间，需要完整对照补证；不据该片段新增 workspace 改写规则。
3. 定位能力已有：`comparable_slots()`（84 行）支持 system/developer 的字符串和内容块、按工具名关联 description；`pair_dynamics()`（`detection.py:26`）保存 JSON 指针，`collect_dynamics()`（114 行）存原文摘要、请求对与实算 Token LCP。当前 L1 **不扫描直接的 user/assistant 消息内容**；嵌在 system 中的历史文字可被遍历。报告 D.1 将任意 messages 时间都列为适用范围，超过现有能力。
4. `apply_recipe()`（`dynamic.py:71`）删除指定槽；`compile_dynamic_plan()`（`detection.py:164`）对 shape 匹配的请求编译有原值守卫的副本替换。普通 timestamp/path 明确标为 `hypothetical_content_removal`，只有已知 billing header 走已有信息保留分类。报告固定整个 `<session_clock>` 块为 NORMALIZED，与删除日期槽不是同一个变换，收益不能互相套用。

**必须补齐**：时间格式/结构块定位及重叠规则，保留精确槽、请求对和真实 Token 前缀证据；分别表达字段被识别、输入前缀受到影响、改法可应用、业务允许采用。不能仅放宽正则就宣称 L1 修复完成。

**可复用 / 约束 / 最小范围**：主要在 `dynamic.py`、`detection.py`，联动 recipe 编译、证据投影及必要的文案。复用 JSON 指针、工具逻辑名、摘要/value guard、统一编码及 CCH 既有逻辑。时间用于业务判断、历史日期是必要内容、路径被工具执行使用时，删改/移动仍需业务确认；无标签时间、扩大到 user 消息、嵌套标签与保留时间的改法暂不冻结。

**本轮可确认 / 待报告**：识别缺口及路径长度反例不依赖 Token 报告。五组真实命中覆盖、完整定位与业务合法负例仍需低命中样本和业务证据；Token 长尾报告只补公共大文本/结构边界，不能替代这些低命中验证，更不能证明时间固定化无损。

## P0-3：候选质量与重复差异汇总

**已确认与需要纠正的判断**

1. `RuntimeOptions.candidate_limit`（`runtime.py:15`）范围为 1–128；`CandidateIndex.lookup()`（`prefix_analysis/candidates.py:20`）限制的是**每个请求、指定 channel/fingerprint 返回的最近前序候选数**，不是任务比较总量。`RuntimeV2.max_comparisons`（`execution_v2.py:37`）另行控制比较数；更准确地说，`TaskControl.comparison()`（`runtime_control.py:88`）按 `self.lane` 分别计数，`service.py:628` 使用 l2、dynamics 两条 lane，并非全任务共享一个总计数器。修复简案的“独立比较总预算”也应作此限定。报告 candidate_limit=1000 的归因不成立；需实际 runtime_options 才能确认现场 1000 对应什么配置。
2. `collect_dynamics()`（`detection.py:72`）分桶仅用 encoder identity、有效参数字符串与前两个消息角色；不含规范化内容模板或工具关系。每条请求取最近前序，遍历/解析/比较后才调用 `retain_finding()`（139 行）；预算在时间序列前部耗尽会限制后部覆盖。静态可证明存在这种风险，不能据此断言现场某个时钟对一定被漏掉。
3. **L2/L3 比较通道必须保留。** `collect_l2()`（`prefix_analysis/service.py:67`）按同一完整工具集合的 fingerprint 找排序变化；`structure.py:8/26` 按逻辑工具名保留定义。L3 的 description 动态片段和工具定义/集合变化由 `pair_dynamics()`（26 行）提供。将所有比较都限定为完全相同工具定义会消灭 L3 所需对照；用原始 system SHA 则会把时间变化拆开。
4. 已有汇总，不是从零建设。`service.py:681` 以 recipe_json 去重实验；`recommendation_groups.py:14` 合并 recipe，`:53` 合并精确差异外上下文一致的 L4/L5，未知上下文保留 `GROUPING_UNRESOLVED`。但这些仅消费**已保留** findings，发生在比较和保留之后。V2 分规则配额避免 L4 挤占所有规则（`runtime_control.py:48`），仍可能被同一规则的重复原因占满，且每条 observation 都构造/序列化后才决定保留，后置汇总不节省前段比较成本。
5. `history_differences()`（`history.py:17`）可为一个请求对生成多个消息字段差异；`retain()`（`runtime_control.py:46`）逐 observation 计 detected。报告百万 L4 不是百万独立请求/根因；`checked_requests`、比较对数、detected、retained、不同请求覆盖不能互换。已有 stage 分开 scan/comparison/retention 完整性（`service.py:756`），但适用对数仍为空（667 行）。

**必须补齐**：有限预算下的代表对覆盖、重复原因对保留空间和成本的影响、分阶段分母及预算归属解释。优先改善候选质量和保留策略，不以提高参数、组内全比较替代；同组全比较是二次规模，最近 K 候选也需计入解析、差异展开与 Token 读取成本。

**可复用 / 约束 / 最小范围**：复用 CandidateIndex、编码身份、L2 工具集合身份、L3 逻辑工具名、已有 recipe/差异分组。最小在 `candidates.py`、`detection.py`、必要的 L2 通道、保留控制和 `recommendation_groups.py`；前端只补真实覆盖/遗漏原因，保持 L4/L5 主体。模板相似不证明同一会话，A4 的多业务步骤也不自动构成可修复错误；独立 P1 模板产品不进入范围。

**本轮可确认 / 待报告**：参数、计数及汇总时机可确认。代表对策略、预算分配与样本覆盖验收暂不选定，等待长尾的内容规模/结构证据并保留低命中真实对照。Token 报告不能替代现场任务参数或 A1/A6 关联证据。

## P0-4：改法 → 样本评估 → 建议解释

**已确认与需要纠正的判断**

1. **pilot 会自动进入所选 scope 的 full，full 不是独立 B 窗。** `run_experiment()`（`prefix_analysis/experiments.py:143`）在 pilot available 且过门槛后直接编译/评估原 `source`（183–196 行）。时间窗过滤仍有效，所以不是无条件跑整个源文件的全部请求；但也不是只跑 pilot。现有门槛由 `contracts.py:132` 定义为严格大于 1pp，这是旧行为事实，不是 V3 决定。
2. `pilot_scope()`（`experiments.py:39`）从 finding 的前后锚点取连续时间窗，包含同时间戳请求；锚点间隔过大、时间戳扩张超限或样本等于整个 scope 时返回 None。因而小 scope 可能成为 `sample_insufficient`；提高 pilot_limit 既不保证可用，也不限制之前的发现流程。当前 pilot 从整个 scope 的已发现 finding 选锚，full 又包含 pilot，请勿把此二阶段称为留出复核。
3. 同样本对照基础可复用。`evaluation.py:28` 的 `evaluate_plan()` 验证 plan/scope、原请求和编码身份，before/after 使用各自新 PrefixLedger，按同一顺序覆盖同一请求集合；`encoding.py:15/42` 复用原模型资产/配置并校验原 Token。窗口使用 `selected_window_recomputed`，不直接累加全量旧 H。完整失败不发布 after（`evaluation.py:145`、`contracts.py:482`）。这些不证明独立 B 窗、业务正确性或报告收益已验证。
4. **报告 C.1 的“L4 没精确定位所以 dynamic_remove pilot 零收益”与源码不符。** `pair_dynamics`/历史观察给 L4 的 recipe 为 None；`service.py:681` 只把有 recipe 的 finding 放入实验；`compile_dynamic_plan()`（`detection.py:167`）只接受 L1/L3，L2 另走专用编译。应补 finding ID/rule/recipe → plan operations → evaluation 的关联。也不能仅凭 before H=after H 就判定 Δ(H/P)=0，须同时核 P；即便 pilot 未达门槛，也不能证明更换成时钟改法必有收益。
5. **状态确实在投影/展示中丢失。** `run_experiment()` 已区分 sample_insufficient、no_applicable_targets、pilot_not_run、pilot_blocked、pilot_below_gate、full_not_run 等，`service.py:725` 保存 experiment。`recommendation_publication.py:37` 仅读取 findings/plans/evaluations；`recommendation_projection.py:76` 只选择同 scope 的 full/direct_full，未获得完整 available full 时在 178–189 行统一投影为 not_run / NO_COMPLETE_FULL_EVALUATION，未保留具体 experiment 原因。
6. 前端还存在独立筛选：`apps/viewer/src/features/analysis/model.ts:39` 的 `cardFromRow()` 在 47 行滤掉所有非 low_hit_optimization 卡片，并要求 full/direct_full、完整覆盖及旧门槛（53 行）；`Reports.tsx:36` 以“没有达到展示条件”概括空列表。`ExecutionStatus.tsx:19` 读取 stage 原因，但不读取逐 experiment 原因。因此不能只修改一段提示文案就修复链路。

**必须补齐**：精确变换及适用集合、同样本重算、发现与冻结改法后的独立复核身份、样本与显式 full 的关系，以及无适用对象/实算无收益或低收益/未评估/预算不足的完整发布解释。保留“不完整不发布完整 after”的保障；已完成的样本实验可以作为受限证据展示，不冒充旧 full 优化资格。

**可复用 / 约束 / 最小范围**：复用 `PreparedMutation` 守卫、统一编码/模拟、P/H/C、修改请求数、原子发布与局部证据。最小涉及 `experiments.py`、`service.py`、必要的 `evaluation.py` 与 recommendation publication/projection；前端涉及 `model.ts`、`Reports.tsx`、`ExecutionStatus.tsx` 及 API 校验。`api/analysis/recommendations.ts:43/52` 要求影响分母和 evaluation scope 与目录 scope 一致，不能把 pilot 或独立 B 窗对象直接塞进旧 full 字段；需要明确兼容投影或版本扩展，方案待定。

**本轮可确认 / 待报告**：自动 full、没有独立复核、状态损失可确认。报告 C.1/C.6 的根因关联和 12.68–39.14pp 收益仍未复验；A1–A3 的 B.5 与 C 节 P/H 不同、A2 的 264+45 超过 300、B.6 编码次数算式相互矛盾，E.4 明确未独立验证 B 窗。后续需可复算样本/变换/顺序/整数指标，而不是照搬收益门槛。固定时间、改位置、路径标准化或历史排序均须单列业务限制。

## 已读测试能支持什么

仅检查以下测试源码及断言，**本轮未执行**。后续验证点是缺口说明，不是冻结测试计划或新增测试授权。

| 已有文件（相对项目根目录） | 已有断言 / 本轮仍不能证明 |
| --- | --- |
| `tests/unit/analysis_common/test_runtime_limits.py:39/60/72/83/97` | 字节、次数、取消、深度边界；不覆盖建任务前 seal I/O、首次正文分配、Token/时间/内存硬限。 |
| `tests/integration/analysis/test_source.py:37`；`test_diagnostic_resources.py:24` | 顺序/窗口/编码身份；规模例仅 16/64/128 请求及有限文本，记录资源数值，不能证明大源预选和服务响应。 |
| `tests/integration/analysis/test_execution_v2_integration.py:86/103`；`test_diagnostic_tasks.py:141/149` | 保留截断与比较超限区分；preflight 失败无报告、取消后无 report_ref。后续需另外验证受限证据保留语义。 |
| `tests/unit/prefix_analysis/test_dynamic.py:12/21/30/39`；`tests/integration/analysis/test_dynamic_replay.py:13/56` | ISO 时间、多槽、CCH、路径、工具重排定位与真实副本评估；指定文件未覆盖斜杠/中文/session_clock、不同长度路径与槽冲突的完整组合。 |
| `tests/unit/prefix_analysis/test_recommendation_groups.py:40/54`；`tests/integration/analysis/test_recommendation_member_coverage.py:9` | 30 findings 汇成两组、未知上下文不乱合并，成员覆盖与 full 完整性分开；不证明相同预算下代表对/独立原因覆盖改善。 |
| `tests/integration/analysis/test_experiments.py:12/59` | pilot 3 → full 6、pilot 不作优化资格、pilot 过门槛而 full 未过；不是独立 B 窗测试，还明确断言 pilot 等于全 scope 时不可选。 |
| `tests/integration/analysis/test_evaluation.py:52/72/96`；`test_recommendation_publication.py:8` | no-op、守卫失败、窗口冷启、末条取消/来源变化不发布 after、完整成果投影；未覆盖样本失败原因逐层到页面的完整链路。 |

## Token 休眠、兼容与下一步依赖

- V2 已支持只选低命中：`execution_v2.py:12`、`service.py:418/450` 按方向执行；`test_execution_v2_integration.py:44` 断言不解析 Token plugin/adapter，仍保留低命中成果。可复用这一隔离机制，但它不等于 V3 全局休眠策略已经落地；新提交、重试、旧排队任务的边界需详细方案决定，本轮不改配置/任务。
- `recommendation_pipeline.py:53` 的 NO_CONFIGURED_RECIPES 属于 Token 建议阶段；`test_execution_v2_integration.py:71` 同时断言仍有检测 fragment。零建议不等于零发现，更不等于无异常。本轮未展开 Token 私有规则或 T2–T4 设计。
- 旧报告读取、not_computed、published partial、方向选择和已有 L4/L5 可复用；相关入口为 `storage.py:191`、`service.py:123`、前端 `Reports.tsx:27` / `ExecutionStatus.tsx:34`。维持批准四入口、既有 L4/L5 主体与历史结果；浏览页面不得触发补算。公共改动不能要求旧 state 重写或伪造新增字段。
- 不采纳 A4“分 appid 即可提高命中”的确定建议：`monitoring/simulation.py:59` 在无限前缀账本的 key 中已包含 appid，拆分不会创造新共享前缀；业务路由变化与缓存实际部署效果需另证。A4 的 6 种模板/108 请求也不足以证明不存在族内对照，P1 产品功能仍不启动。
- **无需等 Token 报告的结论**：本文件确认的代码行为、报告归因冲突、已有能力及静态测试缺口。**必须等报告再结合讨论的事项**：公共样本身份/分层元数据、长尾排除与预算分母、资源和生命周期衔接、旧结果兼容影响；进而细化 V3 修改范围、顺序和验收。**报告仍不能替代的事项**：低命中完整现场链路、独立 B 窗收益与业务正确性。
- 当前不冻结 300 条默认值、预算、API、收益门槛或实现排期。仅在本 CHECK、本线记忆和 SESSIONS 自己登记行写入；不改产品/测试/契约/配置/state，不启动服务/分析/压测/构建，不提交 Git，不委派或唤醒其他会话。等待报告和用户进一步详细方案安排；后续获准修复由本线负责，镜像会话仅接收候选与证据作审批和授权打包。

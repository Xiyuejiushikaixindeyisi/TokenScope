# HV2 异常分析前端接入准备（2026-11-03）

状态：只读事实核查及接入/验收方案完成；未实施、未启动服务、未测试新候选，等待公共层及相关后端独立验收、契约冻结和正式前端任务。负责人为异常分析前端，环境 CODEX_THREAD_ID / CODEX_SESSION_ID 均为 `01a19111-344a-75c1-84e0-14db8be08f4f`。总设计师通过本文跟进，本轮不发送跨会话消息。

依据：[本轮任务](../../../../prompts/sessions/hv2-repair-20261103/ANALYSIS_FRONTEND_PREP.md)、[执行板](../../delivery/HV2_REPAIR_EXECUTION_20261103.md)、[总计划](../../delivery/V2_REPAIR_COORDINATION_PLAN_20261103.md)。公共层由低命中后端唯一维护；本线不接管监控/MA、后端或共享壳。UIR-03 留 V3，旧 UIR 已闭环，不重启旧任务或将旧测试计入 HV2。

## 1. 核查身份与展示边界

本次读取 HEAD 为 `7cbe28621f4e46083bf47f9aa14b011b3cb250c4`；原交付源码 `b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af`。共享树存在其他线修改，不能只凭 HEAD 将当前后端称为冻结版本。开工保护记录为 `artifacts/reviews/hv2-repair-20261103/identity-before.json`；本线未清理或覆盖其他修改。

以下 SHA256 用 Get-FileHash 实际核对，原件保持：

| 材料 | SHA256 |
| --- | --- |
| [UI-02](../monitoring-v2/prototypes/tokenscope-v2-demo-ui02.html) | `799786cb3ee52e0931d2482211f82e594ab0f33ad57969232a7ea2ec06d2eaea` |
| [UI-04](prototypes/analysis-ui04/tokenscope-analysis-ui04.html) | `779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f` |
| [现场验收原件](../../../huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md) | `93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e` |
| [现场调查原件](../../../huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md) | `51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83` |
| apps/viewer/src/features/analysis/model.ts | `d9d8d1f8d4eb7e4887c5a7175b2618db52b69a32cb2e16458bdd71ca87b397dd` |
| apps/viewer/src/features/analysis/AnalysisApp.tsx | `4de7ac5ec1e5078f3654bfb14e87318598a1e017e6421116dbf15aaf74cab675` |
| apps/viewer/src/api/analysis/contract-lock.json | `4299dd204010310ecc6fbe87604520d76bfd75724c7768477a2efc1b43e260c8` |

保留用户监控、搜索与排行、异常分析、MA集群监控四入口及批准配色布局；静态 HTML 中的早期内容不能覆盖后续决定。L4/L5 各一张卡，每类详情最多三个代表例子，完整 RequestKey 去重统计请求数；不逐组造卡，不把例子数或组人数之和当影响数。Token 仅 T2–T4，不恢复 T1、逐项评估表单、hybrid 或 Agent。

## 2. 当前实际读取链与问题边界

源码路径下文均相对项目根目录；这是当前源码事实，不是现场 DOM 实测。

| 环节 | 实际实现与边界 |
| --- | --- |
| 发现与通知 | `apps/viewer/src/state/analysis-discovery.ts` 的 DiscoverySession 连接服务、读取目录，再以目录 cursor 接 SSE；terminal 通知对齐目录，reset/断线重连重新发现。心跳不触发 GET；隐藏页停止、回到前台对齐，不轮询任务状态。 |
| 目录分页 | `apps/viewer/src/api/analysis/client.ts:73` 读取 `/diagnostics/discovery/catalog`，固定 snapshot/event_cursor/defaults，校验分页循环和 default 引用。default 必须对应同 binding/direction 且 default_eligible=true。不能只在 UI 强塞 partial 到 defaults 绕过校验。 |
| 选择 | `AnalysisApp.tsx:37–47` 从 catalog.items 建立 APPID/model binding，按 direction 筛 entries；target 来自显式 route.task 或匹配的 defaults。全 partial 且 defaults=[] 时虽有历史 entries，裸入口没有 target。 |
| 报告内容 | `model.ts:119` 的 loadReport 并行读取 report 与 recommendation-summary；再读 recommendations（按方向分页）及 low_hit difference-groups。report.items/finding 不是卡片来源，不能直接用 findings 替换批准的建议卡。 |
| 空建议和差异 | summary=computed 时，recommendations=[] 不妨碍 L4/L5 差异卡。另有兼容边界：summary=not_computed 时 loadReport 提前返回，Reports.tsx:26 也整体返回空态；新契约若允许该状态仍有差异，需要明确两类结果的可读性并调整这两处，不能猜测。 |
| L4/L5 | model.ts 的 loadDifferenceCards 遍历全部差异元数据页，按规则归并、canonical RequestKey 去重，并校验 difference_group_count 和请求上限。loadCardExamples 最多取三个 owner，按双侧来源无向指纹去重，最终最多三例。旧 group 深链可归并到 detector 详情。 |
| 缓存与固定身份 | analysis-cache.ts 的正文 key 含 instance、契约版本、task、scope、digest、direction；持久化仅目录元数据。AnalysisApp 使用 AbortController 防止切换后的旧响应落地，instance 改变清空正文缓存。显式 task 保持历史，新发布不应覆盖阅读位置。 |
| 源与收益 | recommendations.ts 校验 task/scope/direction、source base_run_id、影响数量、评估引用与精确算术；model.ts 对低命中要求完整 full/direct_full 评估及严格 gain>1pp。Token evaluated 与 advice 区分，不能把无量化依据写成收益。SourceLink 保持 FS-01 精确 run 跳转。 |

调查 §5 的 10 个任务均 partial、已发布、defaults=[] 是报告中的 API 证据；“97 个 L4 差异证明动态字段浪费/会话改写”不成立。现场报告没有最终 DOM，不据此声称浏览器验证通过。

`configured_recipe_count=0` 与 `TOKEN_FRAGMENT_INCOMPLETE` 分别记录，不能互相替代：实际 `src/tokenscope/analysis_common/recommendation_engine.py:64–69` 在 `fragment.coverage.complete` 为 false 时停止。零配方、fragment 不完整、规则预算、建议未计算、未选方向是不同状态；并存不证明因果。旧 Token 请求内 RunControl 与低命中任务 findings 预算须由后端分别复现，前端不推断串扰根因。

其他调查勘误保持：V2Records 本已记忆最多50个 run；当前 user API 没有 GET `/monitoring/user-v2/runs` 目录。151320 与150698差额缺逐行映射，不能全部归因窗口/去重。Qwen逐UUID矩阵、完整MA文件SHA、真实疑似正反例及脚本正文未完整嵌入是证据缺口。本线不冒称取得这些现场证据。

## 3. 等待后端冻结的消费需求

下表已有字段名来自当前读取代码；新增语义为待冻结需求，不是新接口定义或已实现承诺。

| 消费需求 | 已有输入与待确认事项 |
| --- | --- |
| partial-only 可发现且可读 | catalog.items/defaults、status、report_published、default_eligible、directions、sequence；后端明确无 ready 时如何提供可读候选及优先顺序、方向可读性。若新增字段/策略或改变 defaults，必须给 schema、能力版本与兼容样例，不前端自行将所有 partial 视为合格。 |
| ready 优先 | 同 binding/direction 有 ready 时仍选 ready；新 partial/failed 不覆盖旧 ready。明确终态、可读、完整、可推荐是不同维度；总体 partial 不应自动抹去某已完成方向，也不自动把它升级为 ready。 |
| 时间和范围 | analysis_completed_at、binding_id/binding.appid/model_id/common_name、scope_id/scope.source/base_run_id、window、task_id、report_digest；明确方向级完成时间若有新增的映射。缺时间不伪造当前时间，不按显示名称合并 Trace/MA。用户监控和异常共 Trace 模型规格；MA独立数据制品。 |
| 无建议原因 | summary.availability、configured_recipe_count、proposal_coverage/reason_codes、report.stages 与建议 evaluation；提供未启用方向、零配方、fragment incomplete、预算耗尽、完整但无合格结果、旧版 not_computed 的独立样例和原因优先/并列表达规则。原因不能只由空数组推断。 |
| 差异独立可读 | difference_group_count、分页 items/next_offset、members_complete、member_requests、example_refs；冻结“建议未生成但差异存在”的 summary/page 合法组合。保留跨页计数校验，不为 partial 绕过 schema。若优化大目录/差异分页成本，后端先保证唯一请求数与代表例子身份，前端不截断元数据后宣称全量。 |
| 收益和局部证据 | display_qualification、recipe、impact、evaluation、metrics、support_refs/example_refs；L1–L3 全量完整且严格>1pp，Token T2–T4 沿用自动建议和量化/未量化区分。低命中展示影响请求数及命中率提升；Token展示影响请求数及Token变化。仅取局部字段和附近上下文，不加载完整64k请求。 |
| 版本/兼容/通知 | 交付源码commit或精确dirty manifest、契约/schema/capabilities SHA、服务身份、目录snapshot/cursor和事件样例、旧版兼容与失败状态。公共层先通过，相关后端通过后冻结；新增契约必须同步 generated schemas/lock 的正式维护窗口，不能静默放松客户端校验。 |

每线回传须有最小可读取样例及对应 GET/预期响应：ready、partial-only、ready+更新partial、无recipe、fragment incomplete、未选方向、空建议有L4/L5、跨页、旧报告和身份不匹配。需标注合成fixture或真实来源，带固定 task/scope/digest/方向及预期原因，不把业务样例生成等同现场收益证明。

## 4. 冻结后验收方案（尚未执行）

| 编号 | 场景与必须保留的断言 |
| --- | --- |
| A01 | 新空浏览器直接 `/#/analysis`，无本地历史、仅已发布可读partial：能发现 APPID/模型并读到批准卡片，明确部分完成及真实时间/限制；不得显示“完全检查”或靠手填旧task才能看到。 |
| A02 | 同范围旧ready与更新partial/failed共存：最新视图选ready；可显式查看partial历史，不能把partial标ready。没有任何可读发布时才显示相应空态。 |
| A03 | 显式 history/task/detail 冷开、刷新、断网重连、同版本重启：task/scope/digest/direction不变，缺失task给出明确恢复入口，不悄悄改读另一任务。 |
| A04 | 超过一页目录和建议/差异组，跨页加入新发布：快照一致或明确重新对齐；防循环、重复和计数错配；读取失败保留已读内容，重试不重复卡片。 |
| A05 | 相同 APPID 多模型、不同 APPID、low_hit/token_content 快速切换及迟到响应：不串 binding/source/task/正文/证据；未启用方向如实表达，不能强制执行Token或显示另一方向结果。 |
| A06 | SSE terminal重复、乱序、reset、连接中断、前后台切换：对齐目录后读取；历史/详情保持固定，latest按冻结选择策略更新；无3秒任务轮询、无GET启动分析。服务instance变化清正文缓存，离线元数据不能冒称已核验正文。 |
| A07 | recommendations=[]、有跨页L4/L5：各一张卡、每类≤3去重代表例子，跨组重复成员只计一次。例如两组各3人但共享2人应显示4条而非6条。members_complete=false提示仅已发现范围；不要求L4/L5有收益门槛，不宣称动态浪费/会话改写。 |
| A08 | 零配方、fragment incomplete、预算限制、未计算、未启用、完整无合格结果分别测试；有差异时不被空建议遮挡。not_computed+有差异的支持方式必须按冻结契约，不自行造非法fixture。 |
| A09 | L1–L3收益恰好1pp/不足1pp/完整性缺失不进入优化卡，严格大于1pp且其余资格完整才进入。Token evaluated/advice/null/0/大整数和影响请求数、Token差额均真实；不恢复T1，不把收益相加。 |
| A10 | 详情局部证据、旧group深链、返回原卡焦点/滚动和分页位置；新发布时不漂移。FS-01 精确 run 来源及监控/排行/MA/设置/旧深链仍在四入口框架。保留导出取消、SHA/字节/行数完整性既有回归，UIR-03不纳入本轮修复。 |
| A11 | 冻结候选用桌面/窄屏与批准HTML、最终L4/L5对照，记录卡片、时间、部分完成提示和局部证据截图/DOM。不得用API成功替代视觉或用户验收。 |

执行顺序：冻结样例与映射审查 → 单元/组件失败复现和修复 → 本线只读接口联调 → 总设计师协调唯一监听环境下冷浏览器完整E2E。E2E前核实停旧TokenScope进程/worker/测试容器，确认退出及端口释放，保留旧包/state/证据，独立新state与新浏览器；不另端口并行旧版，不误停无关项目。资源峰值和真实数据测试窗口由总设计师确认，不能按历史剩余磁盘直接启动。

保留原断言、失败证据和复测记录。最小合成fixture仅证明软件逻辑，现场缺证仍另列；本线不自行签用户验收。监控/MA全功能回归由对应线及总设计师归口。

## 5. 本轮实际操作与交接

实际执行：PowerShell Get-Content/rg 定向读取以上任务、现场相关章节和源码；环境ID核实；Get-FileHash核对表中7项；WSL git rev-parse HEAD与git status --short只读检查。首次rg使用Windows不支持的通配路径，改为真实目录检索；首次定位recommendation_engine.py误在token_content目录，随后核实实际analysis_common路径。没有执行功能测试、浏览器测试、build、服务启动、Git写操作或打包，故本轮无“修复前后通过数”。

精确变更仅本文、`docs/tasks/viewer/analysis/ENTRY.md` 本线入口和 `memory/tasks/viewer-analysis.md` 本线进度。未改CURRENT/SESSIONS/总执行板、产品/测试代码、后端契约或共享壳。原件SHA复核及本地链接/文档diff检查是文档核验，不是功能验收。

下一步由总设计师提供公共层及相关后端独立验收结果、冻结版本/SHA/样例和正式接入任务。尚无接口冻结结论，不提前声明可编码或现场已修复。公共配置/生成schema等共享窗口如确需变更，正式接入时提交精确清单后由总设计师安排；准备完成后停止等待。

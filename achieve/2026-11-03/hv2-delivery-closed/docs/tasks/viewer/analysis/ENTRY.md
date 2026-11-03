# 异常分析前端入口

2026-11-03总设计师阶段同步：五项后端已独立验收冻结，两前端接入及HV2-AF-01/MF-02修复完成；根339项前端、88项最终浏览器通过（原失败与测试修正分别保留）。本线窗口关闭，统一版本与容器交付由V2总设计师继续；华为真实数据仍待验。[实际独立验收](../../delivery/HV2_INDEPENDENT_ACCEPTANCE_20261103.md)。下方旧阶段按历史阅读。

2026-11-03定向测试增量完成：仅适配analysis-boundaries/review-regressions浏览器fixture及新增analysis-v2-fixtures辅助文件，显式v2握手/目录、精确scope绑定和旧not_computed execution，partial-only按新契约验收自动可读及部分状态。typecheck及无浏览器四组Schema校验通过，原断言除已批准partial期望外全部保留；c3产品与原18项本线SHA未变。测试SHA与边界见[交接顶部addendum](HV2_FRONTEND_HANDOFF_20261103.md)，测试窗口已关闭，浏览器由总设计师统一运行，本线未开服务/Git/打包。

2026-11-03 HV2-R3正式接入完成，源码窗口关闭，交总设计师独立复审：[最终交接](HV2_FRONTEND_HANDOFF_20261103.md)。候选viewer-analysis-hv2-r3-20261103-c3，本线18项组合SHA `61a430bf0ffe931fa5e91713e1a5455b0d518fc2e1293620ed1373cbe105735c`。335单元/组件、typecheck/lint/独立dist build通过，240前端输入前后一致；1项无监听TestClient及实际响应消费通过。已修v2 selected_reports/partial发现、执行原因、HV2-AF-01分页缓存与v2元数据隔离、来源封存身份/revision核验。not_computed当前后端仍0差异组，不造结果、不放松一致性。未启动HTTP/browser E2E、提交/push/Docker/打包；冷浏览器与视觉由总设计师独立验收，UIR-03保持V3。

2026-11-03 HV2-R1：异常前端只读接入准备完成，见 [HV2_FRONTEND_PREP](HV2_FRONTEND_PREP_20261103.md)。已核对批准HTML/现场原件SHA、实际目录与报告读取链，列出partial-only发现、ready优先、方向/历史隔离、空建议原因及L4/L5验收方案。未改产品/测试代码、未启动服务或构建，等待公共层及相关后端独立验收、契约冻结和正式接入任务。当前不是重做旧UIR，以下交付记录为历史。

2026-11-02统一交付同步：V2已完成WSL打包、桌面全文件SHA核对，华为真实数据待验；用户认可V2可交付，UIR-03暂不修、留V3，不作V2阻断。本角色职责/休眠状态不变；当前发布与实际结果见[交付记录](../../delivery/V2_APPROVED_DELIVERY_20261102.md)。现场只用真实Trace3/MA18 CSV，先用户监控（搜索/P90 TTFT）和MA，第一次用户验收并指定appid后才两类异常；SSH18002，唯一Markdown嵌关键源码/证据。[当前prompt](../../../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md) · [固定规则](../../../operations/DELIVERY_ACCEPTANCE_RULES.md)。下方旧开发/交接状态按历史阅读，不覆盖本决定。

2026-11-02 UIR-01鼠标单项修复完成自测，候选viewer-uir01-pointer-fix-20261102-c1；[交接](../../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/viewer/monitoring-v2/UIR01_POINTER_FIX_HANDOFF_20261102.md)。仅用SVG实际screen CTM逆变换修正指针，布局/后端不变。226单元组件、85不同浏览器用例、144真实圆点检查通过；c2负向2项按预期失败；118地址重启一致，重启7项通过。原18项/UIR-02/排行/L4L5/T2–T4保持，窗口释放交审查会话独立复审，未提交/push/打包，不代用户认可。实际session 01a19111-344a-75c1-84e0-14db8be08f4f。

2026-11-02 UIR-01/02补充修复已完成自测，候选 viewer-approved-ui-review-fixes-20261102-c2；[补充交接](../../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/viewer/monitoring-v2/APPROVED_UI_REVIEW_FIX_HANDOFF_20261102.md)。恢复降序读数与不改路由的键盘跳转，另修最近运行覆盖排行路由；222单元组件、81不同浏览器用例、118地址重启通过，重启后13项复测通过。原18项/四入口/L4-L5/T2-T4及后端契约保持。前端窗口释放，交镜像打包与审查独立复审，未提交/合并/push/打包，不代签用户视觉认可。实际session仍01a19111-344a-75c1-84e0-14db8be08f4f。

2026-11-02 四入口/UI-02/UI-04 恢复自测交接：[统一交接](../../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/viewer/monitoring-v2/APPROVED_UI_RESTORATION_HANDOFF_20261102.md)。215单元/组件、71不同浏览器用例通过，111地址重启摘要一致；18项有逐项依据。唯一候选4191，未提交/push/打包，待审查方重新冷启动独立复审，不代签用户视觉验收。

2026-11-01维护：完整服务总负责派发的user_v2来源跳转P1已在本线修复，待其独立复审。[交接与独立候选dist](../../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/viewer/analysis/SOURCE_LINK_FIX_20261101.md)；仅SourceLink URL参数一行变更，203单元/组件及3真实浏览器回归通过，未提交/push或更新冻结镜像。

2026-11-01最新：用户已认可RV2 L4/L5展示，本机统一审查/交付已闭环。总负责权柄已交还镜像打包与审查会话，由其组织华为启动、监控V2及异常分析完整验收和归口修复；本session回到异常分析前端维护支持。[职责交接](../../analysis/ONSITE_COORDINATION_HANDOFF_20261101.md) · [冻结交付](../../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/UNIFIED_REVIEW_DELIVERY_EXECUTION_20261101.md)。原[本机统筹](../../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/COORDINATION_RV2.md)为历史，不继续指挥后端。

2026-10-31；session `01a19111-344a-75c1-84e0-14db8be08f4f`，Windows环境CODEX_THREAD_ID与CODEX_SESSION_ID一致复核，独立于创建方及两后端。

当前前端`viewer-analysis-ui04-local-3`：195项单元/组件、18个不同浏览器用例通过；加载当前后端后7项真实联调再次通过。唯一4191入口，4193仅跳转；Token仅T2–T4，页面只读，不代写后端、不打包部署。

当前后端：[低命中/公共arpc-local-4独立复审通过](../../prefix-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md)；[Token私有T2–T4独立复审通过](../../length-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md)。同一RV1封存状态不变，实际源码身份和验证层级见联合报告。

- **[当前统一功能/视觉验收与联合报告 RV2](../../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/JOINT_VALIDATION_RV2_20261101.md)** · [版本清单](../../analysis/VERSION_RV2_20261101.json) · [统一审查交付prompt](../../../../prompts/sessions/ANALYSIS_UNIFIED_REVIEW_DELIVERY_RV2.md)。
- [前轮RV1](ACCEPTANCE_RV1.md) · [前轮独立复审报告](INDEPENDENT_REVIEW_20261101.md)：6项问题关闭记录保持，其191/17为历史计数。旧[UI-04双实例验收](ACCEPTANCE_UI04.md)已被用户拒绝。
- [前轮执行与验证 ARF000–004](FRONTEND_REWORK_EXECUTION_ARF.md) · [两后端协调及接收 AR-03](REWORK_COORDINATION_AR03.md)。其190项单元/组件、8项浏览器场景为旧验证记录，最新结果以上方RV2为准。

- [验收未通过后的修正方案 AR-0.1](REWORK_PLAN_AR01.md)：逐项原因、真实29项来源、前后端分工及自动收益前移。
- [历史验收入口（未通过）](ACCEPTANCE.md) · [AF006验证闭环](batches/AF006.md) · [旧独立复审prompt（已失效，仅历史）](PROMPT_INDEPENDENT_REVIEW.md)。
- [正式前端开发方案 AF-1.0（已批准）](FRONTEND_DEVELOPMENT_PLAN.md)：模块、接口、分批实施、验收；三项均已获批。
- [两线prompt、发送及最终回传记录](BACKEND_RECEIPT_COORDINATION.md)。
- [开发方案前接入事项](DEVELOPMENT_READINESS.md)：已交付能力、仍需确认与后续联调分列。
- [当前视觉基线UI-04（已认可）](prototypes/analysis-ui04/tokenscope-analysis-ui04.html) · [版本清单](prototypes/analysis-ui04/manifest.json) · [转交低命中后端的完整prompt](BACKEND_DEVELOPMENT_PROMPT.md)。
- [通知/目录/时间需求 FE-N1](BACKEND_NOTIFICATION_HANDOFF.md)：通知后拉取、打开/重连对齐目录、不轮询；partial保留旧报告。discovery-1已交付并接入。
- [视觉基线及批准记录](VISUAL_BASELINE.md) · [修订HTML](prototypes/analysis-ui02-r1/tokenscope-analysis-ui02-r1.html) · [交互讨论稿](INTERACTION_DRAFT.md)。
- [已确认展示方案](DESIGN.md) · [新版自包含HTML](prototypes/analysis-ui02/tokenscope-analysis-ui02.html) · [版本摘要](prototypes/analysis-ui02/manifest.json)。
- [三方接收](BACKEND_ALIGNMENT.md)：版本、摘要差异、样例、缺口和责任。
- [逐文件身份核验](RECEIPT_IDENTITY_20261031.json)：历史清单与当前字节比较，不是发布身份或运行时证明。
- [接入方案草案](INTEGRATION_PLAN.md)：需求映射和UI-01调整意见，待讨论。
- [本线记忆](../../../../memory/tasks/viewer-analysis.md)。

职责覆盖低命中/Token展示、交互与错误恢复设计、获批后的分批开发和真实联合测试，以及最终独立复审prompt。不实现诊断/Tokenizer/归因，不接管监控V2、参数错配研究或Loop过程分析。Token后端本来已经启动，本线仅协调能力补充与接收，没有新建后端开发任务。

视觉历史起点：[UI-01](../prototypes/tokenscope-v2-demo-ui01.html)；当前批准规格为UI-04，HTML保持原摘要。早期浏览器受阻已通过Windows Chrome本地浏览器验证补齐，不能沿用“无法查看”旧状态。正式页面已查看桌面/窄屏截图，用户验收结果须由用户确认。

后续顺序：用户正式页面功能/视觉验收→源码收口→另获授权后统一打包部署。本轮前端独立复审已完成，不代签两后端复审。已批交互/开发边界不重复申请；普通问题本线修复，能力缺口继续发给对应后端，范围/接口变化才请求用户确认。

# 异常分析前端入口

2026-11-01最新：本session已由用户指定为[异常分析功能总负责](../../analysis/COORDINATION_RV2.md)，RV2已修复L4/L5各一张卡、每类最多3例；两后端独立复审与当前组合联合验证通过，统一GitHub收口中。用户视觉确认待进行。

2026-10-31；session `01a19111-344a-75c1-84e0-14db8be08f4f`，Windows环境CODEX_THREAD_ID与CODEX_SESSION_ID一致复核，独立于创建方及两后端。

当前前端`viewer-analysis-ui04-local-3`：195项单元/组件、18个不同浏览器用例通过；加载当前后端后7项真实联调再次通过。唯一4191入口，4193仅跳转；Token仅T2–T4，页面只读，不代写后端、不打包部署。

当前后端：[低命中/公共arpc-local-4独立复审通过](../../prefix-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md)；[Token私有T2–T4独立复审通过](../../length-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md)。同一RV1封存状态不变，实际源码身份和验证层级见联合报告。

- **[当前统一功能/视觉验收与联合报告 RV2](../../analysis/JOINT_VALIDATION_RV2_20261101.md)** · [版本清单](../../analysis/VERSION_RV2_20261101.json) · [统一审查交付prompt](../../../../prompts/sessions/ANALYSIS_UNIFIED_REVIEW_DELIVERY_RV2.md)。
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

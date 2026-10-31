# Token监控V2前端设计与开发

## 2026-10-31 当前入口（覆盖下方历史阶段描述）

用户已批准[分批计划](BATCH_PLAN.md)并授权逐批验证后继续。**MV2-F000–F006正式前端本地实现与验证完成，待用户最终评审**：[结果](batches/MV2-F006/RESULT.md)、[测试](batches/MV2-F006/TESTS.md)、[源码/复现](CODEMAP.md)。159项单元/组件、25项浏览器、类型/静态/本地构建通过。消费用户2.0.0、MA1.0.0及S0；保持UI-02配色/布局。每60秒查处理中任务、终态停止、失败保留历史、完成切新结果，历史目录手动刷新。未部署打包；性能校准仍待完成。下方旧“未开发/待评审”是历史记录，不覆盖当前进度。

TTFT接入统一状态：**代码完成，性能校准待完成**。本轮用户已明确：缺少参数不展示具体命中率，不默认等待为0。三模型最小数据与batch/chunk/等待口径见[校准清单](../../monitoring/v2-user/PERFORMANCE_CALIBRATION.md)。UI-02原配色/布局认可与此前原型检查保留；此前自动显示的合成参数/截图不能当当前默认行为或真实校准证据。
更新：2026-10-30。会话 `01a18c49-d9b4-7a33-8c04-e5a72adfcc24`，本会话环境 `CODEX_THREAD_ID` 与 `CODEX_SESSION_ID` 一致核实，用户明确指派。当前阶段为**UI-02已认可，正式交互方案待评审**：[对照与建议](DEMO_REVIEW.md)已获认可，已保留配色/布局生成[独立新HTML](prototypes/tokenscope-v2-demo-ui02.html)，未覆盖UI-01、未开发正式代码。变化及检查见[UI-02评审记录](PROTOTYPE_UI_02.md)。

## 职责与范围

- 承接用户监控增强、搜索排行、P90长度请求所需参考前缀命中率，以及独立MA监控页面；两条后端并行，本前端分别消费其权威结果。
- 用户侧为GB的appid×common_name；MA侧为GF的model_standard_name×instance_uuid，选择规格后全部UUID直接可见，同UUID跨appid/P共享。两种范围、指标与缓存身份不能混用。
- 负责展示/交互、apps/viewer内增量实现、契约消费记录、前端测试和独立视觉验收。沿用UI-01及后续获批HTML的页面骨架、布局、配色与信息密度，不另建应用或数据层。
- 后端维护算法、采集/回放、计量、性能情景及契约；异常分析页面归另一前端会话。hybrid、自进化Agent、自动采集、部署和打包不在本线范围。

## 阅读与接收入口

P0：AGENTS → [CURRENT](../../../../memory/CURRENT.md) → [SESSIONS](../../../../memory/SESSIONS.md) → [docs入口](../../../README.md) → 本页。

| 优先级 | 材料与用途 |
| --- | --- |
| P1角色/流程 | [启动prompt](../../../../prompts/sessions/TOKEN_MONITORING_V2_FRONTEND_START.md)、[统一工作流](../../../architecture/TASK_SESSION_WORKFLOW.md) |
| P1后端 | [用户设计v1.0](../../monitoring/v2-user/DESIGN.md)、[用户契约1.0.0](../../../contracts/user-monitoring-v2/README.md)；[MA设计v1.0](../../monitoring/v2-ma/DESIGN.md)、[MA协议1.0.0](../../../contracts/ma-monitoring-v2/CONTRACT.md) |
| P1视觉 | [UI-01说明](../PROTOTYPE_V2_UI_01.md)、[自包含HTML](../prototypes/tokenscope-v2-demo-ui01.html)、[视觉摘要](../prototypes/ui01-manifest.json)、[原型源码地图](../CODEMAP.md) |
| P1兼容 | [V1交互](../MONITORING_INTERACTION_V1.md)、[验收门槛](../ACCEPTANCE_V1.md)、[冻结S0](../../monitoring/batches/B005.1/S0_CONTRACT.md) |
| 当前记忆 | [本线职责、材料身份及衔接项](../../../../memory/tasks/viewer-monitoring-v2.md)；后端进度分别读[用户线](../../../../memory/tasks/monitoring-v2-user.md)和[MA线](../../../../memory/tasks/monitoring-v2-ma.md) |

用户线已更新U000–U005本地后端闭环；已复核契约1.0.1勘误与已实现API，业务展示口径未变。MA线M000–M005本机后端闭环，已接收真实路由导出的OpenAPI和16项前端样例。最新消费身份见[UI-02 manifest](prototypes/ui02-manifest.json)，用户运行/情景列表、MA规格汇总等衔接问题见[对照记录](DEMO_REVIEW.md)。本线HTML仅消费合成展示投影，不代替真实前后端/现场验收。

## 后续阶段与协作

本轮已完成获授权的新HTML，等待用户视觉评审；随后依次完成交互方案确认、batch开发方案审批，之后逐批实现与验证。已经认可的UI-01起点、DEMO建议和后端开发授权不重复申请，后续前端阶段不据此自动跳过。

当前维护本ENTRY、DEMO对照/UI-02记录、docs下新HTML及manifest、artifacts内独立ui02生成/检查材料、本线记忆和自身共享登记；未占用apps/viewer公共源码。以后涉及app.tsx、全局样式、路由、API/状态/缓存、锁文件时先登记具体范围和唯一维护方。原UI-01源码、旧HTML、S0及V1发布身份保留；不创建或通知其他会话。

最新：用户认可UI-02，明确两线后端已完成并通过评审。本轮形成[正式交互方案](INTERACTION_V2.md)，等待方案反馈；此前等待HTML审批的描述已被本次决定覆盖。未开发正式代码。

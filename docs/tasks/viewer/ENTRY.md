# TokenScope前端设计开发入口

2026-11-02统一交付同步：V2已完成WSL打包、桌面全文件SHA核对，华为真实数据待验；用户认可V2可交付，UIR-03暂不修、留V3，不作V2阻断。本角色职责/休眠状态不变；当前发布与实际结果见[交付记录](../delivery/V2_APPROVED_DELIVERY_20261102.md)。现场只用真实Trace3/MA18 CSV，先用户监控（搜索/P90 TTFT）和MA，第一次用户验收并指定appid后才两类异常；SSH18002，唯一Markdown嵌关键源码/证据。[当前prompt](../../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md) · [固定规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md)。下方旧开发/交接状态按历史阅读，不覆盖本决定。

2026-11-01异常分析当前：[RV2联合验证与功能统筹](../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/COORDINATION_RV2.md)，由已登记异常前端session兼总负责，正式修复和联合验证完成并进入Git收口；旧“接收准备/未编码”为历史。监控V2维护状态仍见其自身入口。

2026-10-31异常分析后端提供方更新：低命中自审已获用户认可；[公共/低命中前端交接](../prefix-analysis/FRONTEND_HANDOFF.md)与[启动prompt](../../../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md)已按实际冻结接口更新，并链接Token交接。异常前端已由用户明确授权创建，实际ID为01a19111-344a-75c1-84e0-14db8be08f4f（create_thread返回）；当前仅接收核对、职责理解、补充上下文与接入方案，不代签接收或批准编码。监控V2当前状态以其自身ENTRY为准。

**当前状态：2026-10-30原V1前端会话保持休眠；监控V2前端已由用户指定并登记。** 新会话本轮仅理解职责、接收两线设计/契约入口及更新记忆，见[监控V2前端ENTRY](monitoring-v2/ENTRY.md)与[本线记忆](../../../memory/tasks/viewer-monitoring-v2.md)。异常分析前端已启动接收准备；后续设计开发按阶段推进。

2026-10-30：Token监控V1前后端已获用户验收，见[现场验收交接](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)。监控V2与异常分析初版展示原型已生成，**用户认可初版设计，后续优化稿仍按阶段审批**，见[UI-01设计说明](PROTOTYPE_V2_UI_01.md)。已完成两个前端会话的交接，未修改正式代码或冻结接口。功能详细设计与开发归对应新session，本session先负责展示原型及衔接，详见[下一阶段上下文](NEXT_PHASE_CONTEXT.md)。既有HTML不等于正式分析能力或已冻结接口。

## 后续前端会话交接

[监控V2前端启动prompt](../../../prompts/sessions/TOKEN_MONITORING_V2_FRONTEND_START.md) · [异常分析前端启动prompt](../../../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md)。新会话角色与实际ID见[SESSIONS](../../../memory/SESSIONS.md)，就绪条件与审批顺序见[统一工作流](../../architecture/TASK_SESSION_WORKFLOW.md)。监控V2前端已登记，分析前端统一对接两个分析器、已启动接收准备，不是新增分析算法会话。

视觉研究先看[自包含HTML](prototypes/tokenscope-v2-demo-ui01.html)（沉淀于docs，直接本地打开，不依赖HTTP），直接理解风格、配色与布局；无需先读.py或全部脚本。正式实现严格沿用最终获批DEMO，功能测试与视觉验收独立。

## 当前阅读顺序

- P0：[当前状态](../../../memory/CURRENT.md)、[分工](../../../memory/SESSIONS.md)。
- P1当前准备：[下一阶段范围与输出位置](NEXT_PHASE_CONTEXT.md)、[V2产品讨论与字段口径](../../../memory/tasks/monitoring.md)。用户监控增强、独立MA集群页面与异常分析展示可并行准备，沿用获批视觉风格。
- P1监控维护：[批准交互设计](MONITORING_INTERACTION_V1.md)、[源码地图](CODEMAP.md)、[验收门槛](ACCEPTANCE_V1.md)、[固定S0](../monitoring/batches/B005.1/S0_CONTRACT.md)。
- P1分析界面：[分析报告展示设计起点](DESIGN.md)、[两类分析HTML demo](../../../artifacts/prototypes/monitoring-v1/tokenscope-monitoring-with-reports-v2.html)、[原型来源与入口](CODEMAP.md)，再读[低命中分析](../prefix-analysis/ENTRY.md)或[Token异常分析](../length-analysis/ENTRY.md)的当前设计/契约。
- P2已完成证据：[F007结果](../../../achieve/2026-10-28/docs/tasks/viewer/batches/F007/RESULT.md)、[视觉验收](../../../achieve/2026-10-28/docs/tasks/viewer/batches/F007/VISUAL_ACCEPTANCE.md)、[联合结果](../monitoring/JOINT_RESULT_V1.md)、[交付结果](../monitoring/batches/B006/RESULT_20261028.md)。
- P3：[闭环批次索引](batches/README.md)、[审批历史](APPROVAL.md)。

职责：apps/viewer、前端设计/测试/记忆；前端只消费已有结果，不在页面访问时运行编码、理想命中计算或诊断。分析session维护算法和结果/证据契约，前端维护展示和交互，不把合成HTML数据当真实后端能力。

后端负责现场服务启动验收/失败排查；打包session负责统一审查及授权后的交付。前端提供可复现构建/资源/锁/测试和回退，修复自身问题。重大目标/接口/验收变化与用户讨论；授权内普通缺陷和测试失败自行修复复测，不降低门槛。当前导出仍按64MiB优化目标、256MiB验收上限及已批准的重复大文件测量要求，不因归档改变。

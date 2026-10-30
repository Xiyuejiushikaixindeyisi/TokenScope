# TokenScope前端设计开发入口

**当前状态：2026-10-30交接完成，本会话按用户要求暂时休眠。** 待相应产品、后端设计与接口契约固定后，由用户使用下方两份prompt启动新的前端session；不自动创建、唤醒或开展后续设计开发。

2026-10-30：Token监控V1前后端已获用户验收，见[现场验收交接](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)。监控V2与异常分析初版展示原型已生成，**用户认可初版设计，后续优化稿仍按阶段审批**，见[UI-01设计说明](PROTOTYPE_V2_UI_01.md)。已完成两个前端会话的交接，未修改正式代码或冻结接口。功能详细设计与开发归对应新session，本session先负责展示原型及衔接，详见[下一阶段上下文](NEXT_PHASE_CONTEXT.md)。既有HTML不等于正式分析能力或已冻结接口。

## 后续前端会话交接

[监控V2前端启动prompt](../../../prompts/sessions/TOKEN_MONITORING_V2_FRONTEND_START.md) · [异常分析前端启动prompt](../../../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md)。新会话角色、就绪条件与审批顺序见[统一工作流](../../architecture/TASK_SESSION_WORKFLOW.md)，实际ID尚未登记。分析前端统一对接两个分析器，不是新增分析算法会话。

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

# 任务与session入口

> 2026-11-12当前决定：用户本机人工验收已通过，授权镜像线独立E2E、Git/版本/记忆整理及打包；正在复验，华为业务收益待现场。本轮暂不编写华为prompt。旧暂停、旧四P0/硬时限及旧prompt不覆盖本决定，当前进度以交付入口和memory/CURRENT.md为准。

2026-11-11：当前只保留三个活跃角色。实际ID、本人权责登记与六条V2休眠状态见[SESSIONS](../../memory/SESSIONS.md)。

| 活跃角色 | 当前工作 | 入口 |
| --- | --- | --- |
| TokenScope V3调研与产品设计 | 证据、产品范围、宣传、独立验收与四象限资料 | [研究](product-v3/ENTRY.md) |
| TokenScope V3代码修复与开发 | 候选本地验收已完成；等待现场证据，承担后续获准修复 | [开发](development-v3/ENTRY.md) · [CHECK](development-v3/CHECK.md) |
| 镜像打包与审查 | 交付与prompt r2已完成；当前获准分类整理工作树 | [交付](delivery/ENTRY.md) |

V3小样本候选已交付，现场等待回传；[当前执行说明](delivery/V3_PROMPT_R2_20261111.md)要求复用监控成果、逐一分析五组，不重跑全量。Token异常修复留V3.5，不恢复T1/hybrid/Agent。四象限明细保持高优先级，四入口/L4L5与旧结果保护不变。

## V2休眠线：只按问题追溯

- [用户监控后端](monitoring/v2-user/ENTRY.md)、[MA监控后端](monitoring/v2-ma/ENTRY.md)、[监控前端](viewer/monitoring-v2/ENTRY.md)。
- [低命中/公共层](prefix-analysis/ENTRY.md)、[Token后端](length-analysis/ENTRY.md)、[异常前端](viewer/analysis/ENTRY.md)。
- [V2异常产品依据](analysis/ENTRY.md)、[HV2阶段收口](delivery/HV2_ACCEPTANCE_CLOSE_20261105.md)、[HV2发布身份](delivery/HV2_DELIVERY_20261103.md)。
- [旧启动/计划归档](../../achieve/2026-11-10/v2-session-dormancy/README.md)。已闭环prompt不重新派发；有效设计/契约、实际测试/验收证据保持原位。

V1前后端及历史总设计继续休眠；hybrid与Agent未启动。跨模块改动由当前活跃开发会话按获准范围统一承担，不因V2历史入口保留就恢复六线。[协作流程](../architecture/TASK_SESSION_WORKFLOW.md)。

# 任务与session入口

2026-11-01当前异常分析：已进入[功能总负责RV2修复、联合验证与版本收口](analysis/COORDINATION_RV2.md)，由原异常前端session统筹；低命中/公共arpc-local-4及Token私有T2–T4独立复审均已有实际通过报告。下表早期“待创建/未编码/T1–T4”仅历史分线记录，实际角色/范围以最新SESSIONS与各线ENTRY为准。

2026-10-30最新分线；[SESSIONS](../../memory/SESSIONS.md)维护实际ID、角色、状态与优先级。每个session先明确任务/角色再工作，未知ID不编造；异常分析已获用户许可完成fork并启动Token线，主会话继续低命中详细设计；其他线以各自最新授权为准。

| 任务 | 当前状态与范围 | 入口 |
| --- | --- | --- |
| 总设计 | 休眠，总体边界/协调 | [总设计](product/ENTRY.md) |
| 监控V1后端 | 休眠，已验收基线与现场交接 | [监控](monitoring/ENTRY.md) |
| 监控V1前端 | 休眠，F007/UI-01与prompt交接 | [前端](viewer/ENTRY.md) |
| 审查打包 | 运行中，统一审查及授权后交付 | [交付](delivery/ENTRY.md) |
| V2监控父会话 | 运行中，版本整理；待fork | [监控产品记忆](../../memory/tasks/monitoring.md) |
| V2用户监控后端 | 待fork/登记，TTFT命中需求评估与搜索排行 | [用户功能](monitoring/v2-user/ENTRY.md) |
| V2同事监控后端 | 待fork/登记，MA独立采集/回放及对照；与用户功能并行 | [MA监控](monitoring/v2-ma/ENTRY.md) |
| 异常分析已批产品/共同交接 | v0.4已审批；主会话转任低命中后端，Token线已fork启动 | [产品](analysis/ENTRY.md) · [分线交接](analysis/BACKEND_SPLIT_HANDOFF.md) |
| 低命中后端设计和开发 | 当前主会话L1–L5详细设计及公共接入草案已形成；未编码 | [本线](prefix-analysis/ENTRY.md) · [prompt](../../prompts/sessions/LOW_HIT_BACKEND_START.md) |
| Token异常后端设计和开发 | T1–T4；实际会话01a18fcd-0464-7cf1-b435-4f394bd33e66已创建启动并登记 | [本线](length-analysis/ENTRY.md) · [prompt](../../prompts/sessions/TOKEN_ANOMALY_BACKEND_FORK_START.md) |
| 监控V2前端 | 已登记；本轮仅职责理解、两线设计/契约入口接收与记忆整理 | [本线ENTRY](viewer/monitoring-v2/ENTRY.md) · [启动prompt](../../prompts/sessions/TOKEN_MONITORING_V2_FRONTEND_START.md) |
| 异常分析功能总负责（兼前端） | 已登记01a19111-344a-75c1-84e0-14db8be08f4f；前端修复、后端协调、联合验证和Git收口 | [当前统筹](analysis/COORDINATION_RV2.md) · [前端](viewer/analysis/ENTRY.md) |
| hybrid | 暂不做 | [监控交接](monitoring/ENTRY.md) |
| 自进化Agent | 两类分析设计和代码完成后按用户启动 | [Agent](evolution-agent/ENTRY.md) |

P0：AGENTS → CURRENT → SESSIONS → docs/README → 自己的ENTRY；P1本线产品/设计/契约及直接依赖，P2按问题读证据/源码，P3才读历史。共享契约与原始证据不随整理改写。完整边界见[工作流](../architecture/TASK_SESSION_WORKFLOW.md)。

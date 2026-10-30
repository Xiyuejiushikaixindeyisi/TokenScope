# 任务与session入口

2026-10-30最新分线；[SESSIONS](../../memory/SESSIONS.md)维护实际ID、角色、状态与优先级。每个session先明确任务/角色再工作，未知ID不编造；本轮仅整理并push，不创建聊天。

| 任务 | 当前状态与范围 | 入口 |
| --- | --- | --- |
| 总设计 | 休眠，总体边界/协调 | [总设计](product/ENTRY.md) |
| 监控V1后端 | 休眠，已验收基线与现场交接 | [监控](monitoring/ENTRY.md) |
| 监控V1前端 | 休眠，F007/UI-01与prompt交接 | [前端](viewer/ENTRY.md) |
| 审查打包 | 运行中，统一审查及授权后交付 | [交付](delivery/ENTRY.md) |
| V2监控父会话 | 运行中，版本整理；待fork | [监控产品记忆](../../memory/tasks/monitoring.md) |
| V2用户监控后端 | 待fork/登记，TTFT命中需求评估与搜索排行 | [用户功能](monitoring/v2-user/ENTRY.md) |
| V2同事监控后端 | 待fork/登记，MA独立采集/回放及对照；与用户功能并行 | [MA监控](monitoring/v2-ma/ENTRY.md) |
| 异常分析后端母会话 | 待创建/登记，先调研及产品设计 | [母会话](analysis/ENTRY.md) |
| 低命中与Token异常后端 | 母会话产品阶段完成后再fork设计/开发 | [低命中](prefix-analysis/ENTRY.md) · [Token异常](length-analysis/ENTRY.md) |
| 监控V2前端 | 待创建/登记，对接两条监控后端 | [启动prompt](../../prompts/sessions/TOKEN_MONITORING_V2_FRONTEND_START.md) |
| 异常分析前端 | 待创建/登记，对接两类分析后端 | [启动prompt](../../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md) |
| hybrid | 暂不做 | [监控交接](monitoring/ENTRY.md) |
| 自进化Agent | 两类分析设计和代码完成后按用户启动 | [Agent](evolution-agent/ENTRY.md) |

P0：AGENTS → CURRENT → SESSIONS → docs/README → 自己的ENTRY；P1本线产品/设计/契约及直接依赖，P2按问题读证据/源码，P3才读历史。共享契约与原始证据不随整理改写。完整边界见[工作流](../architecture/TASK_SESSION_WORKFLOW.md)。

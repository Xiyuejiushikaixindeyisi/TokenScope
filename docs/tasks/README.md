# 任务入口索引

更新日期：2026-10-27。监控与前端会话已登记；实际实施/暂停状态见各任务ENTRY，不将早期规划视作当前状态。监控V1审批、开发和完整服务交付顺序见[统一工作流](../architecture/TASK_SESSION_WORKFLOW.md)。

| 任务 | 负责会话安排 | 启动依赖 | 入口 |
| --- | --- | --- | --- |
| Token 监控 | Session 1维护监控后端并统一最终联合/交付 | 用户启动 Session 1 | [监控入口](monitoring/ENTRY.md) |
| 前端展示 | 已登记前端fork会话，按自身审批与F批计划 | 监控设计完成 | [展示入口](viewer/ENTRY.md) |
| 理想命中率低原因分析 | 新 Session 2 | 监控设计完成 | [前缀诊断入口](prefix-analysis/ENTRY.md) |
| 单条请求长度异常分析 | 新 Session 3 | 监控设计完成 | [长度诊断入口](length-analysis/ENTRY.md) |
| 自进化 Agent | 后续新的 Agent 会话 | 两类分析设计和代码开发均完成 | [Agent 入口](evolution-agent/ENTRY.md) |

会话安排不代表会话已创建；实际状态见 [会话登记](../../memory/SESSIONS.md)。不按主副会话关系推定职责。

## 阅读方式

新 session 读项目 AGENTS、精简 CURRENT 和自己的 ENTRY。然后按该任务当前工作状态阅读 P1；P2/P3 按需追溯，不全量阅读其他任务文档和上游源码。

各任务ENTRY给出当前设计、batch和CODEMAP。监控当前执行入口为B005.1 PLAN（S0固定，S1–S5后端闭环，交接见RESULT）；前端采用同一S0按自身计划推进；其他任务未登记启动不表示已开展工作。

共享输入输出放 docs/contracts，研究放 docs/research，现场原件放 evidence。任务设计引用这些来源，不复制维护第二份。

完整工作方式见 [协作约定](../architecture/TASK_SESSION_WORKFLOW.md)。P3历史启动 Session 1 的文本见 [启动 prompt](../../prompts/sessions/SESSION1_MONITORING_DESIGN.md)。


# TokenScope总设计入口

2026-10-28：现有总设计session休眠，实际ID未知。负责产品形态、一期/后续边界、session分工和跨任务协调；本次文档整理不唤醒会话或授权新功能。

P0：[当前状态](../../../memory/CURRENT.md)、[session登记](../../../memory/SESSIONS.md)。
P1：[一期目标输入](../../requirements/V1_SCOPE.md)、[协作流程](../../architecture/TASK_SESSION_WORKFLOW.md)、[任务索引](../README.md)、[工作区结构](../../architecture/WORKSPACE_LAYOUT.md)。
P2：用户要讨论的具体任务ENTRY和相关约束，不全量重读闭环批次。

产品目标由用户与本session收敛；各任务session拥有其详细设计、实现与验证。统一计量归监控，两类分析复用它，前端展示已有成果。两类分析设计与代码完成后才考虑自进化Agent启动。历史[工作区交接](../../../achieve/2026-10-28/memory/handoffs/2026-10-23-workspace.md)仅供追溯。

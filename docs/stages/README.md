# 阶段记录

当前尚未启动实现阶段。用户明确应先按任务领域分配 session，由各任务 session 与用户讨论目标和设计。当前不划分全项目实施阶段或具体验收条件。

本目录保留初始化时的通用模板，不作为默认开发路线。用户已同意按任务维护入口及开发 batch，实际入口见 [任务索引](../tasks/README.md) 和 [协作约定](../architecture/TASK_SESSION_WORKFLOW.md)，不同时维护两套 batch 计划。

每阶段使用一个稳定编号和名称，包含：

- CONTEXT.md：目标、范围、基线身份、输入材料和阅读优先级。
- PLAN.md：工作项、产出、负责人或 session、依赖和验证条件。
- VALIDATION.md：实际执行的检查、结果、证据路径和未覆盖范围。
- HANDOFF.md：已完成内容、遗留事项、准确入口及下一步。

模板位于 [_template](_template/CONTEXT.md)。模板不代表已启动任务。当前阶段由 [CURRENT](../../memory/CURRENT.md) 指向，历史阶段保持可追溯，不将旧任务状态混入当前阶段。


# Session 分工登记

更新：2026-10-28，依据用户最新明确分工。现有四个 session；角色职责不等于当前正在执行任务。旧登记与逐轮日志已归档到[历史快照](../achieve/2026-10-28/snapshots/memory/SESSIONS.md)。

| Session | 实际 ID | 当前状态与责任 | 入口 |
| --- | --- | --- | --- |
| TokenScope总设计 | 未知（现有文档未记录可核实ID，不沿用其他会话ID） | 休眠；产品形态、整体边界、session分工与跨任务协调；不代替任务详细设计 | [总设计](../docs/tasks/product/ENTRY.md) |
| Token监控后端设计开发 | 01a1682f-956d-7630-afe7-e123ba38dfc0（历史环境登记） | 监控后端、统一编码/计量/理想命中算法与公共契约；负责华为服务启动/26GB真实CSV分析验收、故障调查prompt、报告驱动修复及patch应用/回退说明；现场报告尚未收到 | [监控后端](../docs/tasks/monitoring/ENTRY.md) |
| TokenScope前端设计开发 | 01a17811-4c9a-7513-befc-b35723aec96e（历史环境登记） | F007监控展示已通过用户验收；持续负责整体前端及低命中率/Token异常两类分析的前端设计开发；分析器契约待对应新session明确 | [前端](../docs/tasks/viewer/ENTRY.md) |
| 镜像打包和审查 | 01a1800e-80b4-7400-a78b-a84f5b6e888d（本轮环境CODEX_THREAD_ID/SESSION_ID一致） | 打包前统一审查、获明确授权后的WSL构建与容器验收、镜像/代码/prompt交付及本地备份管理；本轮更新文档与记忆 | [审查与交付](../docs/tasks/delivery/ENTRY.md) |

## 未来 session（尚未登记启动）

- [Token异常分析—调研设计开发](../docs/tasks/length-analysis/ENTRY.md)：当前范围为请求长度/组成归因；更广语义由该session与用户确认，复用统一编码计量。
- [命中率异常分析—调研设计开发](../docs/tasks/prefix-analysis/ENTRY.md)：当前范围为低理想命中原因诊断，复用监控算法，不维护第二套计算口径。
- [自进化Agent](../docs/tasks/evolution-agent/ENTRY.md)：两类分析设计和代码均完成后，再按用户启动；不限于未来仅新增两个session。

监控设计前置已满足；未来session仍需用户实际创建/启动，不能因为文档入口存在就自动开展。两个分析session拥有分析实现及结果/证据契约，前端session拥有其界面，两者共同明确可展示数据。

共享文件修改前读最新状态；按职责维护模块。后端提供现场脱敏报告与修复版本，前端处理界面缺陷，打包会话审查修复和重新交付；总设计只在用户唤醒或需产品/跨任务决策时介入。记录与文件交接不等于已通知其他会话，本轮未创建、唤醒或发送消息。

# 任务与session入口

2026-10-28：四个现有session，未来两个以上；实际ID与状态见[登记](../../memory/SESSIONS.md)。职责来自用户最新指派，不由早期主副/fork关系推断。

| 任务/session | 状态与职责 | 入口 |
| --- | --- | --- |
| TokenScope总设计 | 休眠；产品形态、整体边界、session分工 | [总设计](product/ENTRY.md) |
| Token监控后端设计开发 | 后端与公共计量契约；华为启动验收、失败debug/修复 | [监控](monitoring/ENTRY.md) |
| TokenScope前端设计开发 | 监控展示完成；后续两类分析的前端设计开发 | [前端](viewer/ENTRY.md) |
| 镜像打包和审查 | 统一审查、授权后构建/包体/prompt/本地备份 | [交付](delivery/ENTRY.md) |
| 命中率异常分析 | 新session待启动；当前范围低理想命中原因分析 | [前缀诊断](prefix-analysis/ENTRY.md) |
| Token异常分析 | 新session待启动；当前范围请求长度与组成归因 | [长度诊断](length-analysis/ENTRY.md) |
| 自进化Agent及其他后续任务 | 按依赖与用户启动，不预设已创建 | [Agent](evolution-agent/ENTRY.md) |

P0读AGENTS→CURRENT→自己的ENTRY；P1读当前设计、直接依赖契约、源码和测试；P2按问题追依据；P3才读[achieve](../../achieve/README.md)历史。共享输入输出放docs/contracts，原始证据不移改。完整协作方式见[工作流](../architecture/TASK_SESSION_WORKFLOW.md)。

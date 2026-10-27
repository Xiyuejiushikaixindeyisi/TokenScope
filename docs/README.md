# 文档索引与阅读优先级

新 session 先恢复自己的任务和工作状态，再阅读当前工作需要的文档和代码。第一版目标仍需各任务 session 与用户共同讨论；阅读优先级与采用状态分开，研究建议不会自动成为实施决定。

| 优先级 | 入口 | 何时阅读 |
| --- | --- | --- |
| P0 | [AGENTS](../AGENTS.md)、[当前状态](../memory/CURRENT.md)、[自己的任务入口](tasks/README.md) | 恢复约束和当前工作 |
| P1 | 当前工作所需的目标、设计、直接依赖契约、batch、源码和测试 | 根据调研、设计、编码、评审状态选择具体文件，不整目录阅读 |
| P2 | 被设计或问题引用的研究结论、固定源码、现场证据与决策 | 需要解释依据或定位疑问时，沿引用阅读 |
| P3 | [归档](archive/README.md)、旧设计、旧 batch 和交接 | 按需追溯历史 |

任务入口与代码地图应列文件、章节或符号和用途。编码时以已共同确定的设计及当前 batch 为主；相关实现和测试须读足，遇到依赖问题可扩展阅读，不把默认清单当作禁止调查的边界。详细机制见 [协作约定](architecture/TASK_SESSION_WORKFLOW.md)。

## 当前监控V1：只从这里进入

- 用户审批：[监控ENTRY](tasks/monitoring/ENTRY.md)→**B005.1 PLAN**，附件S0与TESTS；无需逐份审批DESIGN/Schema/过程记录。
- 后端代码：B005.1 S1–S5已闭环，交接和证据见其RESULT；前端代码按其[ENTRY](tasks/viewer/ENTRY.md)和当前F批计划，以S0为共同接口。
- 协作、交接、联合验收、打包与文档权威：[统一工作流](architecture/TASK_SESSION_WORKFLOW.md)的当前V1章节。
- B006仅在前后端就绪后进入；Docker/交付包须联合验收通过后单独同意。当前后端ready_for_joint，未进行Docker/交付打包。

## 其他入口

| 目的 | 文档 |
| --- | --- |
| 理解产品、一期目标输入与已确认约束 | [目标输入](requirements/V1_SCOPE.md) |
| 查看任务分工、阅读范围与 batch 开发方式 | [任务与 session 协作约定](architecture/TASK_SESSION_WORKFLOW.md) |
| 进入负责的任务 | [五个任务入口](tasks/README.md) |
| P3历史：最初启动监控设计的prompt（非当前开发入口） | [Session 1 prompt](../prompts/sessions/SESSION1_MONITORING_DESIGN.md) |
| 确定文件应该放在哪里 | [工作区结构](architecture/WORKSPACE_LAYOUT.md) |
| 查看目录决定 | [工作区决策](decisions/0001-workspace-and-scope.md) |
| 恢复协作与分工 | [协作约定](../memory/COLLABORATION.md)、[session 登记](../memory/SESSIONS.md) |
| 查看尚未启用的阶段模板 | [阶段组织](stages/README.md) |
| 盘点参考项目 | [候选参考清单](research/implementations/CATALOG.md) |
| 面向同事分享 | [分享入口](sharing/README.md) |

## 文档职责

- requirements：当前目标、范围和待明确的业务口径。
- architecture：总体架构、模块边界和目录结构。
- contracts：数据、指标、探测器与模型适配契约，明确采用状态。
- huawei：现场调查、版本核对、差异与验收结论，链接 evidence 原件。
- tasks：各任务的 ENTRY、DESIGN、CODEMAP 和后续开发 batch。
- stages：保留初始化时的通用模板，不与任务 batch 重复维护计划。
- research：参考实现、论文与专题研究，说明依据、适用性及采用状态。
- decisions：采用、否决和调整方案的原因与替代关系。
- operations：已实现功能的运行和维护说明。
- sharing：面向同事的文档及导出快照。
- archive：被替代的资料，标明替代入口。

用户最新决定确定范围；对应版本的代码和验证证据确定能力事实。文档不能把“计划支持”写成“已经验证”，原始材料与核对结论分别保留。


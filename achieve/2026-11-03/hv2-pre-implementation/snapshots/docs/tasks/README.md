# 任务与session入口

2026-11-03后续执行更新：华为调查已收到，用户已要求开始修复与实际任务派发。当前状态、证据勘误、源码窗口和阶段门槛以[本轮执行板](delivery/HV2_REPAIR_EXECUTION_20261103.md)为准；下方“等待回传/尚未派发”保留为前序规划记录。公共层先验收，后端通过冻结后前端，最终完整验收交付。

2026-11-03当前：[V2总设计修复与交付计划](delivery/V2_REPAIR_COORDINATION_PLAN_20261103.md)。本审查交付会话已获用户指定为V2版本总设计师，等待华为调查回传后直接派发六线修复和本线测试；先公共层、对应后端验收及契约冻结，再前端，最后统一E2E和已授权版本/构建/交付。当前仅计划/记忆，未派发/开发/测试/push/打包。已知二次现场验收不通过，不再把旧本机完成当现场通过。

[SESSIONS](../../memory/SESSIONS.md)记录实际ID与接收进度；下面是职责和依赖，不代表各线已开始本轮工作。

| 任务 | 职责与依赖 | 入口 |
| --- | --- | --- |
| V2版本总设计师（原审查打包） | 规划分配、公共层与模块独立验收、E2E、Docker/代码镜像、归档记忆、版本push与华为统筹 | [总计划](delivery/V2_REPAIR_COORDINATION_PLAN_20261103.md) · [工作入口](delivery/ENTRY.md) |
| 异常分析前端 | 异常发现/读取/状态与批准展示；依赖公共层及分析后端通过和契约冻结 | [异常前端](viewer/analysis/ENTRY.md) |
| MA监控后端 | 独立MA模型制品/UUID/pre-now数据、四指标缺数与质量 | [MA后端](monitoring/v2-ma/ENTRY.md) |
| Token异常后端 | Token私有探测/预算/证据；依赖先验收的异常公共层，当前T2–T4，研究不自动恢复T1 | [Token后端](length-analysis/ENTRY.md) |
| 低命中后端与异常公共层 | 公共层唯一设计集成维护方，先验收公共层，再完成低命中私有规则；基于真实调查确定修复 | [低命中/公共](prefix-analysis/ENTRY.md) |
| Token监控V2前端 | 用户、搜索排行、MA和TTFT前端；各自依赖对应已通过的后端及冻结契约 | [监控前端](viewer/monitoring-v2/ENTRY.md) |
| 用户监控V2后端 | 同APPID多模型访问、搜索/排行、同Trace异常衔接、逐模型TTFT默认参数及计算 | [用户后端](monitoring/v2-user/ENTRY.md) |
| 历史全项目总设计 | 保持休眠，不因V2总设计指派自动唤醒 | [历史入口](product/ENTRY.md) |
| 监控V1前后端 | 保持休眠，已验收源码/契约和批准HTML依据 | [后端](monitoring/ENTRY.md) · [前端](viewer/ENTRY.md) |
| hybrid / 自进化Agent | 未启动，不因当前修复自动开展 | [Agent入口](evolution-agent/ENTRY.md) |

用户监控与异常共用Trace模型规格，MA使用独立制品数据；TTFT由用户逐模型提供chunked seconds，K默认8192可选改，日常页面只填等待时间和SLO。详情和未输入参数见总计划，不把新需求当已实现。

P0：AGENTS → CURRENT → SESSIONS → docs/README → 本线ENTRY；P1当前总计划、本线设计/契约及派发任务，P2按问题读源码/证据，P3才追历史。六线ENTRY内旧开发/交付状态保留对应版本事实，恢复时以CURRENT和本次任务派发为准。[工作流](../architecture/TASK_SESSION_WORKFLOW.md) · [交付固定规则](../operations/DELIVERY_ACCEPTANCE_RULES.md)。

历史：[2026-11-02交付](delivery/V2_APPROVED_DELIVERY_20261102.md) · [闭环归档](../../achieve/2026-11-02/v2-approved-delivery/README.md) · [分线交接](analysis/BACKEND_SPLIT_HANDOFF.md)。UIR-03留V3，四入口HTML/L4L5保持；当前调查和未闭环问题不提前归档，原始证据和冻结契约不改。

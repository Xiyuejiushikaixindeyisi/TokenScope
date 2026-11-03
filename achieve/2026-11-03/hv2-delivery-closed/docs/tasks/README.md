# 任务与session入口

2026-11-03最新阶段：异常公共层及四项后端已独立验收冻结，两前端接入完成，HV2-AF-01和HV2-MF-02已闭环；根339项前端、88项最终浏览器、135项鼠标核对及156资源重启一致性通过。源码版本整理/容器交付待继续，当前未发布本轮包体；现场真实数据仍待验。 下方执行日志和前序状态按时间追溯，以本段及当前入口为准。

2026-11-03当前：[执行板](delivery/HV2_REPAIR_EXECUTION_20261103.md) · [独立验收](delivery/HV2_INDEPENDENT_ACCEPTANCE_20261103.md) · [六线总计划](delivery/V2_REPAIR_COORDINATION_PLAN_20261103.md)。华为调查已收到并实际派发任务；公共层及全部相关后端已独立通过并冻结，两个前端正式接入中。后续完整E2E→固定commit/push→WSL构建/容器复验→本地包体/桌面SHA按既有授权执行。目前未完成本轮完整验收或产品发布，不把旧本机通过当现场通过。

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

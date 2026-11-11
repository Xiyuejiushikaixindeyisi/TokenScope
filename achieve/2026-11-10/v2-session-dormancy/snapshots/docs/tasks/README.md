# 任务与session入口

2026-11-10：用户认可V3低命中四P0方向，新开发角色先独立check；待三组Token探索回传后再细化范围/顺序/验收。Token在V3休眠，修复留V3.5；六条旧线不恢复。[当前分工](product-v3/V3_SCOPE_AND_HANDOFF_20261110.md)，V2事实仍查[阶段收口](delivery/HV2_ACCEPTANCE_CLOSE_20261105.md)。

| 任务 | 职责与依赖 | 入口 |
| --- | --- | --- |
| **全新V3代码修复与开发（待启动/ID未知）** | 先check四P0方案；回传后细化，未来承担获准公共层/低命中/必要前端兼容和验证 | [最小入口](development-v3/ENTRY.md) · [启动消息](development-v3/START_PROMPT_20261110.md) |
| 镜像打包与审查（曾统筹V2修复） | V3仅镜像/交付打包与审批，不承担开发/debug/开发调度或开发验收执行 | [工作入口](delivery/ENTRY.md) |
| TokenScope V3调研与产品设计 | 证据、产品范围、交接与探索prompt；四象限高优先级维护，本轮不实施 | [V3入口](product-v3/ENTRY.md) · [Token探索prompt](product-v3/HUAWEI_TOKEN_TAIL_EXPLORATION_PROMPT_20261110.md) |
| 异常分析前端 | 异常发现/读取/状态与批准展示；依赖公共层及分析后端通过和契约冻结 | [异常前端](viewer/analysis/ENTRY.md) |
| MA监控后端 | 独立MA模型制品/UUID/pre-now数据、四指标缺数与质量 | [MA后端](monitoring/v2-ma/ENTRY.md) |
| V2 Token异常后端 | V3休眠，V3.5再据真实长尾证据修复；T2–T4历史实现参考，不恢复T1 | [Token后端](length-analysis/ENTRY.md) |
| V2低命中后端与异常公共层 | 历史维护方休眠；V3范围交全新开发角色，旧契约/代码为按需参考 | [低命中/公共](prefix-analysis/ENTRY.md) |
| Token监控V2前端 | 用户、搜索排行、MA和TTFT前端；各自依赖对应已通过的后端及冻结契约 | [监控前端](viewer/monitoring-v2/ENTRY.md) |
| 用户监控V2后端 | 同APPID多模型访问、搜索/排行、同Trace异常衔接、逐模型TTFT默认参数及计算 | [用户后端](monitoring/v2-user/ENTRY.md) |
| 历史全项目总设计 | 保持休眠，不因V2总设计指派自动唤醒 | [历史入口](product/ENTRY.md) |
| 监控V1前后端 | 保持休眠，已验收源码/契约和批准HTML依据 | [后端](monitoring/ENTRY.md) · [前端](viewer/ENTRY.md) |
| hybrid / 自进化Agent | 未启动，不因当前修复自动开展 | [Agent入口](evolution-agent/ENTRY.md) |

用户监控与异常共用Trace模型规格，MA使用独立制品数据；TTFT由用户逐模型提供chunked seconds，K默认8192可选改，日常页面只填等待时间和SLO。用户参数已登记为Qwen1/GLM2.7/DeepSeek2.6秒，尚未性能校准；实际实现/现场边界见最终交付。

P0：AGENTS → CURRENT → SESSIONS → docs/README → 本线ENTRY；P1最终交付、本线有效交接/契约及新的定向任务，P2按问题读源码/证据，P3才追历史。六线ENTRY内旧开发/交付状态保留对应版本事实，恢复时以CURRENT和本次任务派发为准。[工作流](../architecture/TASK_SESSION_WORKFLOW.md) · [交付固定规则](../operations/DELIVERY_ACCEPTANCE_RULES.md)。

历史：[2026-11-02交付](delivery/V2_APPROVED_DELIVERY_20261102.md) · [闭环归档](../../achieve/2026-11-02/v2-approved-delivery/README.md) · [分线交接](analysis/BACKEND_SPLIT_HANDOFF.md)。UIR-03留V3，四入口HTML/L4L5保持；当前调查和未闭环问题不提前归档，原始证据和冻结契约不改。

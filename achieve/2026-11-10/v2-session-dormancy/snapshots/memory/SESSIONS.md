# Session角色与任务登记

2026-11-10：用户基本认可V3低命中四项P0，指定全新开发角色独立check和后续获准代码开发；角色预登记、实际ID未知，未创建/唤醒会话。镜像打包与审查在V3仅打包与审批。Token异常在V3休眠，三组长尾探索为V3.5取证；回传后再细化V3范围/顺序/验收。[最新范围](../docs/tasks/product-v3/V3_SCOPE_AND_HANDOFF_20261110.md)。

P0：AGENTS→CURRENT→本登记→自己的ENTRY。当前以11-10用户决定为准；V2发布事实仍查[阶段收口](../docs/tasks/delivery/HV2_ACCEPTANCE_CLOSE_20261105.md)。V2六线、历史总设计/V1保持休眠，其他session未提交内容保留。新开发会话只需[精简入口](../docs/tasks/development-v3/ENTRY.md)，不全量恢复历史。

## 已有session

| 角色 | 实际ID与来源 | 状态 | 当前任务与优先级 | 入口 |
| --- | --- | --- | --- | --- |
| TokenScope总设计 | 未知，历史未核实 | 休眠 | 用户唤醒后处理总体边界与协调，不代写任务方案 | [总设计](../docs/tasks/product/ENTRY.md) |
| Token监控后端开发V1 | 01a1682f-956d-7630-afe7-e123ba38dfc0，历史环境登记 | 休眠 | 保留V1能力/现场交接；不自动启动修复或打包 | [监控V1](../docs/tasks/monitoring/ENTRY.md) · [验收](../docs/huawei/MONITORING_V1_ACCEPTANCE_20261030.md) |
| Token监控前端开发V1 | 01a17811-4c9a-7513-befc-b35723aec96e，前端环境已核实 | 休眠 | F007/UI-01和两份新前端prompt交接完成，保留原型开发起点 | [前端交接](../docs/tasks/viewer/ENTRY.md) · [UI-01](../docs/tasks/viewer/PROTOTYPE_V2_UI_01.md) |
| 镜像打包与审查（曾任V2修复总设计师） | 01a1800e-80b4-7400-a78b-a84f5b6e888d，既有环境登记；11-10应用列表核对 | V2及ICSL revision3历史交付保持；未启动V3打包 | **V3只负责镜像/交付打包与审批**；接收新开发会话候选及验证证据，问题退回开发处理；不承担V3编码/debug/开发调度/开发验收执行 | [本线记忆](tasks/delivery.md) · [交付入口](../docs/tasks/delivery/ENTRY.md) |
| TokenScope V3调研与产品设计 | 01a1a5d5-4baf-7a41-b5c6-14bd5f4f67c2，2026-11-10环境THREAD/SESSION一致核实 | 四P0方向获基本认可；本轮交接/登记/Token探索prompt已整理 | 现场证据、产品范围、探索prompt与研究文档；维护高优先级四象限资料；报告回传后参与范围细化，不承担产品开发 | [V3入口](../docs/tasks/product-v3/ENTRY.md) · [本线记忆](tasks/product-v3.md) |
| V2 Token监控后端（原父会话） | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境与应用列表核实 | 历史角色；同一会话已按用户指派转为同事监控后端 | 已完成产品讨论、分线与版本整理；不再以父会话接管两线 | [产品记忆](tasks/monitoring.md) · [检查点](../docs/operations/V2_HANDOFF_20261030.md) |
| V2 同事监控后端设计与开发 | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境核实 | HV2 MA解释资源已独立通过冻结，源码窗口关闭 | 维护MA数据/预热/独立与配对指标和availability；按总负责定向处理后续问题，真实cached缺失不补造；[冻结](../docs/tasks/delivery/HV2_MA_FREEZE_20261103.json) | [MA入口](../docs/tasks/monitoring/v2-ma/ENTRY.md) · [记忆](tasks/monitoring-v2-ma.md) |
| V2 用户监控后端—功能设计与开发 | 01a18bc7-cdb5-7830-a185-ad3aa6257b21，环境核实 | HV2用户2.1.0目录及默认TTFT已独立通过冻结，源码窗口关闭 | 多模型发现、同Trace来源与用户提供τ已实现；前端接入支持和问题归口，未校准；[冻结](../docs/tasks/delivery/HV2_USER_FREEZE_20261103.json) | [本线ENTRY](../docs/tasks/monitoring/v2-user/ENTRY.md) · [设计](../docs/tasks/monitoring/v2-user/DESIGN.md) · [记忆](tasks/monitoring-v2-user.md) |
| 低命中率分析后端设计和开发（原异常分析母会话） | 01a18be2-7112-7aa2-919b-5137d1f1b1ad，2026-10-31环境THREAD/SESSION ID一致复核 | HV2公共第一关及低命中第二关均独立通过冻结，继续休眠 | 保留V2公共层/L1–L5维护历史；V3范围由全新开发会话统一接手，不双写；[公共冻结](../docs/tasks/delivery/HV2_COMMON_FREEZE_20261103.json)／[私有冻结](../docs/tasks/delivery/HV2_LOW_HIT_FREEZE_20261103.json) | [本线ENTRY](../docs/tasks/prefix-analysis/ENTRY.md) · [记忆](tasks/prefix-analysis.md) · [分线交接](../docs/tasks/analysis/BACKEND_SPLIT_HANDOFF.md) |
| Token异常分析后端设计和开发 | 01a18fcd-0464-7cf1-b435-4f394bd33e66，既有环境登记；11-10应用列表核对 | V3休眠；修复开发留V3.5，未唤醒 | 保留T2–T4历史资料/旧成果；新三组长尾探索不是本线编码启动；[冻结](../docs/tasks/delivery/HV2_TOKEN_FREEZE_20261103.json) | [本线入口](../docs/tasks/length-analysis/ENTRY.md) · [记忆](tasks/length-analysis.md) |
| Token监控V2前端设计与开发 | 01a18c49-d9b4-7a33-8c04-e5a72adfcc24，本会话环境CODEX_THREAD_ID与CODEX_SESSION_ID一致核实 | HV2接入/MF02及根源码与容器完整复验通过，窗口关闭 | 保持UI02/四入口；完整多模型发现、固定历史、仅W/SLO日常输入和MA缺数解释；不独立监听/Git/打包 | [修复交接](../achieve/2026-10-31/monitoring-v2-review/docs/tasks/viewer/monitoring-v2/REVIEW_FIX_HANDOFF_20261031.md) · [本线ENTRY](../docs/tasks/viewer/monitoring-v2/ENTRY.md) · [记忆](tasks/viewer-monitoring-v2.md) |


## 其他已登记与未来角色

新V3开发角色为用户本次指定的全新session，只登记职责和启动资料，不用旧会话顶替。下表旧前端/hybrid/Agent记录保留历史身份，不构成新启动。

| 角色 | 实际ID／状态 | 优先任务与范围 | 依赖与入口 |
| --- | --- | --- | --- |
| **全新V3代码修复与开发** | **01a1c449-6a9b-7a83-912a-5a9ff77c703d；2026-11-10本会话环境THREAD/SESSION一致核实；四P0只读check完成；等待Token报告与详细方案安排，未获实施授权** | 已完成[独立CHECK](../docs/tasks/development-v3/CHECK.md)；华为Token探索回传后细化，随后承担获准公共层/低命中/必要前端兼容与验证；不把Token私有开发纳入V3 | [入口/代码地图](../docs/tasks/development-v3/ENTRY.md) · [启动消息](../docs/tasks/development-v3/START_PROMPT_20261110.md) · [记忆](tasks/development-v3.md) |
| 异常分析前端维护（原本机阶段总负责） | 01a19111-344a-75c1-84e0-14db8be08f4f，已核实 | HV2 c3/AF01及根源码与容器完整复验通过，窗口关闭 | v2 partial可读/状态与批准L4L5、固定来源revision；本线实施后根独立复审。异常前端归口维护、现场问题支持及被协调复验；不继续统一指挥后端或华为验收，不作为新总负责与后端中转；原交付/验证身份保持 | [职责交接](../docs/tasks/analysis/ONSITE_COORDINATION_HANDOFF_20261101.md) · [前端入口](../docs/tasks/viewer/analysis/ENTRY.md) |
| hybrid attention仿真 | 无session；暂不做 | 不调研设计或开发，不作为监控两线依赖 | 保留现有近似的能力边界 |
| 自进化Agent | 未知；未启动 | 两类诊断设计与代码均完成后由用户另行启动 | [Agent ENTRY](../docs/tasks/evolution-agent/ENTRY.md) |


## 当前协作边界

V3获准改动涉及的公共层由新开发会话统一维护，并负责相关后端/必要前端兼容与代码验证；旧六线不并发介入。镜像会话只做审批和授权打包，不承担开发验收执行；候选问题由新开发会话修复。研究会话维护证据、范围和交接，本轮按用户明确要求增量更新共享登记/导航；以后修改前仍核最新状态，不覆盖他人dirty。先等Token探索报告再细化V3实施安排，当前不编码/提交/打包。

用户与异常同Trace，MA独立制品；W/SLO与用户τ/K要求保持。旧结果与批准四入口/L4L5保护，四象限HTML为高优先级资料。现场真实数据、两阶段用户验收、SSH18002及唯一Markdown要求按当前具体授权适用；不因旧prompt恢复源码窗口或开启Token分析。

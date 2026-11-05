# Session角色与任务登记

2026-11-05：用户暂时接受V2，产品宣传优先；新回传已核对，未决项和证据局限见[阶段收口](../docs/tasks/delivery/HV2_ACCEPTANCE_CLOSE_20261105.md)。六线开发窗口关闭，未自动启动修复/重构。现有V3 session继续已开展的宣传讨论与研究，输入新增真实业务场景与32GiB容器容量约束；历史总设计/V1休眠。

P0：AGENTS→CURRENT→本登记→自己的ENTRY。当前以11-05用户决定和阶段收口为准；V3研究/宣传由本线维护，镜像打包与审查只管版本生命周期。V2六线待新定向任务，其他session未提交内容保持。

## 已有session

| 角色 | 实际ID与来源 | 状态 | 当前任务与优先级 | 入口 |
| --- | --- | --- | --- | --- |
| TokenScope总设计 | 未知，历史未核实 | 休眠 | 用户唤醒后处理总体边界与协调，不代写任务方案 | [总设计](../docs/tasks/product/ENTRY.md) |
| Token监控后端开发V1 | 01a1682f-956d-7630-afe7-e123ba38dfc0，历史环境登记 | 休眠 | 保留V1能力/现场交接；不自动启动修复或打包 | [监控V1](../docs/tasks/monitoring/ENTRY.md) · [验收](../docs/huawei/MONITORING_V1_ACCEPTANCE_20261030.md) |
| Token监控前端开发V1 | 01a17811-4c9a-7513-befc-b35723aec96e，前端环境已核实 | 休眠 | F007/UI-01和两份新前端prompt交接完成，保留原型开发起点 | [前端交接](../docs/tasks/viewer/ENTRY.md) · [UI-01](../docs/tasks/viewer/PROTOTYPE_V2_UI_01.md) |
| 镜像打包与审查（曾任V2修复总设计师） | 01a1800e-80b4-7400-a78b-a84f5b6e888d，2026-11-05环境CODEX_THREAD_ID/CODEX_SESSION_ID一致再次核实 | V2用户暂时接受；本轮回传核对、归档记忆与文档push | V1/V2/V3版本迭代、版本级debug协调、独立E2E、Git/WSL镜像代码包及现场交付；V3产品设计交新session | [本线记忆](tasks/delivery.md) · [交付入口](../docs/tasks/delivery/ENTRY.md) |
| TokenScope V3调研与产品设计 | 01a1a5d5-4baf-7a41-b5c6-14bd5f4f67c2，2026-11-04 create_thread返回且新会话已报告环境核实 | 首轮研究/宣传讨论已有产出；11-05新证据已接收并完成本轮口径更新，待继续讨论 | 产品宣传优先，研究真实业务场景/定位与功能取舍；新报告高优先级核对，32GiB与场景适配纳入设计，本轮不实施 | [V3入口](../docs/tasks/product-v3/ENTRY.md) · [本线记忆](tasks/product-v3.md) |
| V2 Token监控后端（原父会话） | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境与应用列表核实 | 历史角色；同一会话已按用户指派转为同事监控后端 | 已完成产品讨论、分线与版本整理；不再以父会话接管两线 | [产品记忆](tasks/monitoring.md) · [检查点](../docs/operations/V2_HANDOFF_20261030.md) |
| V2 同事监控后端设计与开发 | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境核实 | HV2 MA解释资源已独立通过冻结，源码窗口关闭 | 维护MA数据/预热/独立与配对指标和availability；按总负责定向处理后续问题，真实cached缺失不补造；[冻结](../docs/tasks/delivery/HV2_MA_FREEZE_20261103.json) | [MA入口](../docs/tasks/monitoring/v2-ma/ENTRY.md) · [记忆](tasks/monitoring-v2-ma.md) |
| V2 用户监控后端—功能设计与开发 | 01a18bc7-cdb5-7830-a185-ad3aa6257b21，环境核实 | HV2用户2.1.0目录及默认TTFT已独立通过冻结，源码窗口关闭 | 多模型发现、同Trace来源与用户提供τ已实现；前端接入支持和问题归口，未校准；[冻结](../docs/tasks/delivery/HV2_USER_FREEZE_20261103.json) | [本线ENTRY](../docs/tasks/monitoring/v2-user/ENTRY.md) · [设计](../docs/tasks/monitoring/v2-user/DESIGN.md) · [记忆](tasks/monitoring-v2-user.md) |
| 低命中率分析后端设计和开发（原异常分析母会话） | 01a18be2-7112-7aa2-919b-5137d1f1b1ad，2026-10-31环境THREAD/SESSION ID一致复核 | HV2公共第一关及低命中第二关均独立通过冻结，源码窗口关闭 | 公共层唯一维护方与L1–L5私有开发；等待定向问题，不恢复历史arpc/RV2提交；[公共冻结](../docs/tasks/delivery/HV2_COMMON_FREEZE_20261103.json)／[私有冻结](../docs/tasks/delivery/HV2_LOW_HIT_FREEZE_20261103.json) | [本线ENTRY](../docs/tasks/prefix-analysis/ENTRY.md) · [记忆](tasks/prefix-analysis.md) · [分线交接](../docs/tasks/analysis/BACKEND_SPLIT_HANDOFF.md) |
| Token异常分析后端设计和开发 | 01a18fcd-0464-7cf1-b435-4f394bd33e66，环境再次核实 | HV2私有优化/预算消费独立通过冻结，源码窗口关闭 | T2–T4私有维护与现场成本方案；无新生产recipe/质量收益承诺；[冻结](../docs/tasks/delivery/HV2_TOKEN_FREEZE_20261103.json) | [前端交接](../docs/tasks/length-analysis/FRONTEND_HANDOFF.md) · [记忆](tasks/length-analysis.md) |
| Token监控V2前端设计与开发 | 01a18c49-d9b4-7a33-8c04-e5a72adfcc24，本会话环境CODEX_THREAD_ID与CODEX_SESSION_ID一致核实 | HV2接入/MF02及根源码与容器完整复验通过，窗口关闭 | 保持UI02/四入口；完整多模型发现、固定历史、仅W/SLO日常输入和MA缺数解释；不独立监听/Git/打包 | [修复交接](../achieve/2026-10-31/monitoring-v2-review/docs/tasks/viewer/monitoring-v2/REVIEW_FIX_HANDOFF_20261031.md) · [本线ENTRY](../docs/tasks/viewer/monitoring-v2/ENTRY.md) · [记忆](tasks/viewer-monitoring-v2.md) |


## 其他已登记与未来角色

用户监控、同事监控后端、低命中主会话（原异常分析母会话）及监控V2前端均已登记。Token异常已获用户允许并完成fork，真实ID已登记；启动prompt已发送，active及子会话环境身份复核已确认。两条监控后端平行推进，不将此前“TTFT排在MA之后”的建议当作强制依赖。

| 角色 | 实际ID／状态 | 优先任务与范围 | 依赖与入口 |
| --- | --- | --- | --- |
| 异常分析前端维护（原本机阶段总负责） | 01a19111-344a-75c1-84e0-14db8be08f4f，已核实 | HV2 c3/AF01及根源码与容器完整复验通过，窗口关闭 | v2 partial可读/状态与批准L4L5、固定来源revision；本线实施后根独立复审。异常前端归口维护、现场问题支持及被协调复验；不继续统一指挥后端或华为验收，不作为新总负责与后端中转；原交付/验证身份保持 | [职责交接](../docs/tasks/analysis/ONSITE_COORDINATION_HANDOFF_20261101.md) · [前端入口](../docs/tasks/viewer/analysis/ENTRY.md) |
| hybrid attention仿真 | 无session；暂不做 | 不调研设计或开发，不作为监控两线依赖 | 保留现有近似的能力边界 |
| 自进化Agent | 未知；未启动 | 两类诊断设计与代码均完成后由用户另行启动 | [Agent ENTRY](../docs/tasks/evolution-agent/ENTRY.md) |


## 当前协作边界

公共层唯一维护方为低命中后端；公共/契约变化先独立验收冻结，再由依赖后端与前端接入。镜像打包与审查负责跨版本迭代、版本级debug、独立E2E、停旧冷启、Git/WSL构建/交付、归档记忆和华为归口。V3新session仅调研与产品设计，独占本线研究文档；共享入口/Git由审查会话维护，不并发改写。用户与异常同Trace，MA独立制品；W/SLO与用户τ/K要求保持。现场真实数据、两阶段用户验收、SSH18002及唯一Markdown要求见当前现场prompt。不得因旧派发prompt/历史压缩摘要重开已闭环源码窗口。

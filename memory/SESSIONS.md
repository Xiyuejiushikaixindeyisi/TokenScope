# Session角色与任务登记

2026-11-02最新：用户认可V2可交付，UIR-03留V3；审查打包负责本轮发布和现场完整验收统筹。业务归口、实际ID、休眠状态保持，不因文档整理唤醒其他session。以下行中的前序完成记录仅是模块状态，不代替新镜像或华为验收。[当前入口](../docs/tasks/delivery/ENTRY.md) · [现场流程](../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md) · [历史登记原文](../achieve/2026-11-02/v2-approved-delivery/snapshots/memory/SESSIONS.md)。

P0：AGENTS→CURRENT→本登记→docs/README→自己的ENTRY；核实实际ID，不沿用其他会话ID。源码公共窗口一次一个维护方，按原分工，未分配不主动接管。前端本轮窗口已释放，发布候选冻结；用户最新决定覆盖旧暂停/旧中转安排。

## 已有session

| 角色 | 实际ID与来源 | 状态 | 当前任务与优先级 | 入口 |
| --- | --- | --- | --- | --- |
| TokenScope总设计 | 未知，历史未核实 | 休眠 | 用户唤醒后处理总体边界与协调，不代写任务方案 | [总设计](../docs/tasks/product/ENTRY.md) |
| Token监控后端开发V1 | 01a1682f-956d-7630-afe7-e123ba38dfc0，历史环境登记 | 休眠 | 保留V1能力/现场交接；不自动启动修复或打包 | [监控V1](../docs/tasks/monitoring/ENTRY.md) · [验收](../docs/huawei/MONITORING_V1_ACCEPTANCE_20261030.md) |
| Token监控前端开发V1 | 01a17811-4c9a-7513-befc-b35723aec96e，前端环境已核实 | 休眠 | F007/UI-01和两份新前端prompt交接完成，保留原型开发起点 | [前端交接](../docs/tasks/viewer/ENTRY.md) · [UI-01](../docs/tasks/viewer/PROTOTYPE_V2_UI_01.md) |
| 镜像打包与审查／完整服务总负责 | 01a1800e-80b4-7400-a78b-a84f5b6e888d，2026-11-02环境再次核实 | V2源码已push；WSL构建/实际容器复验/桌面全SHA交付完成，华为真实数据待验 | P0按真实数据两阶段/指定appid/单Markdown协议接收华为结果和归口问题；UIR-03留V3，保持批准展示/用户计划 | [当前交付](../docs/tasks/delivery/V2_APPROVED_DELIVERY_20261102.md) · [固定规则](../docs/operations/DELIVERY_ACCEPTANCE_RULES.md) |
| V2 Token监控后端（原父会话） | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境与应用列表核实 | 历史角色；同一会话已按用户指派转为同事监控后端 | 已完成产品讨论、分线与版本整理；不再以父会话接管两线 | [产品记忆](tasks/monitoring.md) · [检查点](../docs/operations/V2_HANDOFF_20261030.md) |
| V2 同事监控后端设计与开发 | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境核实 | MA监控维护；按完整服务总负责协调参与现场验证与Bug修复 | 新决定将华为启动/验收总责交镜像打包与审查；本线仍归口MA收集/复现/修复，不承担全功能总责。P90 TTFT/校准归用户监控线 | [MA入口](../docs/tasks/monitoring/v2-ma/ENTRY.md) · [记忆](tasks/monitoring-v2-ma.md) |
| V2 用户监控后端—功能设计与开发 | 01a18bc7-cdb5-7830-a185-ad3aa6257b21，环境核实 | U006–U008 closed且源码已push；代码完成，性能校准待完成；前端接入支持 | 2026-10-31最小TTFT模型已实现，契约2.0.0；W覆盖全部非计算、不单列O，证据选填，旧历史兼容。380全量＋最终126测试、类型/静态/契约审计通过；前端交接完成但未改前端，现场/真实校准待完成 | [本线ENTRY](../docs/tasks/monitoring/v2-user/ENTRY.md) · [设计](../docs/tasks/monitoring/v2-user/DESIGN.md) · [记忆](tasks/monitoring-v2-user.md) |
| 低命中率分析后端设计和开发（原异常分析母会话） | 01a18be2-7112-7aa2-919b-5137d1f1b1ad，2026-10-31环境THREAD/SESSION ID一致复核 | arpc-local-4独立复审通过；2026-11-01 RV2-L聚合接入验证闭环，L4/L5各唯一6请求、215只读路由通过；精确提交清单交总负责统一收口，本线不commit/push、不打包部署 | L1–L5后端设计开发；兼任公共分析结果/范围/证据/离线评估封装的单一设计集成维护方，复用监控算法；Token fork已获准创建 | [本线ENTRY](../docs/tasks/prefix-analysis/ENTRY.md) · [记忆](tasks/prefix-analysis.md) · [分线交接](../docs/tasks/analysis/BACKEND_SPLIT_HANDOFF.md) |
| Token异常分析后端设计和开发 | 01a18fcd-0464-7cf1-b435-4f394bd33e66，环境再次核实 | T2–T4+arpc-local-4独立复审通过（明确限制），164本线+12独立边界+14只读GET，无阻断或业务修改；RV2-T精确清单交总负责统一收口，本线不commit/push、不打包部署 | 唯一维护src/tokenscope/token_content、tests/unit/token_content、tests/integration/token_content及本线文档；不改公共源码；参数错配独立，不打包部署 | [前端交接](../docs/tasks/length-analysis/FRONTEND_HANDOFF.md) · [记忆](tasks/length-analysis.md) |
| Token监控V2前端设计与开发 | 01a18c49-d9b4-7a33-8c04-e5a72adfcc24，本会话环境CODEX_THREAD_ID与CODEX_SESSION_ID一致核实 | RV2-01/02/03修复已独立复审通过并推送main；维护支持 | 保持UI-02；用户2.0.0/MA1.0.0及S0；已补身份/导出/排行与冷state回归，最终复审及Git收口已由审查方完成；TTFT性能校准待完成，未构建镜像/部署打包 | [修复交接](../achieve/2026-10-31/monitoring-v2-review/docs/tasks/viewer/monitoring-v2/REVIEW_FIX_HANDOFF_20261031.md) · [本线ENTRY](../docs/tasks/viewer/monitoring-v2/ENTRY.md) · [记忆](tasks/viewer-monitoring-v2.md) |


## 待创建或登记session

用户监控、同事监控后端、低命中主会话（原异常分析母会话）及监控V2前端均已登记。Token异常已获用户允许并完成fork，真实ID已登记；启动prompt已发送，active及子会话环境身份复核已确认。两条监控后端平行推进，不将此前“TTFT排在MA之后”的建议当作强制依赖。

| 角色 | 实际ID／状态 | 优先任务与范围 | 依赖与入口 |
| --- | --- | --- | --- |
| 异常分析前端维护（原本机阶段总负责） | 01a19111-344a-75c1-84e0-14db8be08f4f，已核实 | 本机RV2交付闭环；按用户决定已交还完整服务总负责职责 | 异常前端归口维护、现场问题支持及被协调复验；不继续统一指挥后端或华为验收，不作为新总负责与后端中转；原交付/验证身份保持 | [职责交接](../docs/tasks/analysis/ONSITE_COORDINATION_HANDOFF_20261101.md) · [前端入口](../docs/tasks/viewer/analysis/ENTRY.md) |
| hybrid attention仿真 | 无session；暂不做 | 不调研设计或开发，不作为监控两线依赖 | 保留现有近似的能力边界 |
| 自进化Agent | 未知；未启动 | 两类诊断设计与代码均完成后由用户另行启动 | [Agent ENTRY](../docs/tasks/evolution-agent/ENTRY.md) |

## 当前协作边界

各维护方处理本模块设计/代码及归口问题；审查打包负责完整服务复审、授权发布、华为统筹。现在各ENTRY已同步本轮真实数据/两次验收/单文档协议，不代表已向会话下发新编码任务。只按用户实际指定appid开展异常，不自动启动hybrid/自进化Agent。

## 2026-11-03用户后端历史版本交接复核

仅补充用户后端角色（01a18bc7-cdb5-7830-a185-ad3aa6257b21）：U006–U008已closed且源码a4053db与回执ac06998已进入GitHub main；前端历史接入入口为[TTFT交接](../docs/tasks/monitoring/v2-user/TTFT_FRONTEND_HANDOFF.md)，[本次复核](../docs/tasks/monitoring/v2-user/GIT_HANDOFF_U008_20261031.md)。真实性能校准仍待完成。当前HV2-R1-USER属于后续独立修复，仍按执行板推进，不纳入此次历史版本提交，不改变其他session状态。

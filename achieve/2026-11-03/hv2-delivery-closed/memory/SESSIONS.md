# Session角色与任务登记

2026-11-03最新阶段：异常公共层及四项后端已独立验收冻结，两前端接入完成，HV2-AF-01和HV2-MF-02已闭环；根339项前端、88项最终浏览器、135项鼠标核对及156资源重启一致性通过。源码版本整理/容器交付待继续，当前未发布本轮包体；现场真实数据仍待验。 下方执行日志和前序状态按时间追溯，以本段及当前入口为准。

2026-11-03最新：用户指定原审查交付会话为**V2版本总设计师**，授权华为调查回传后直接向六个既有开发session派发修复/测试prompt，依公共层→后端验收→契约冻结→前端→统一E2E→版本/构建/交付顺序推进。[总计划与六线任务分工](../docs/tasks/delivery/V2_REPAIR_COORDINATION_PLAN_20261103.md)。华为调查已回传，六线任务已实际发送成功，接收进度/交接/独立验收见[执行板](../docs/tasks/delivery/HV2_REPAIR_EXECUTION_20261103.md)；不以待发送冒充已接收。二次现场验收不通过，UIR-03仍留V3。[历史登记原文](../achieve/2026-11-02/v2-approved-delivery/snapshots/memory/SESSIONS.md)。

P0：AGENTS→CURRENT→本登记→docs/README→自己的ENTRY；核实实际ID，不沿用其他会话ID。源码公共窗口一次一个维护方，按原分工，未分配不主动接管。前序交付窗口已闭环；本轮全部五项后端关卡已独立验收冻结、源码窗口关闭。监控前端接入已交接并通过75项独立定点测试，窗口关闭待根E2E；异常前端c3独立复审通过，HV2-AF-01闭环；两前端浏览器维护增量已交接并关闭。用户最新决定覆盖旧暂停/旧中转安排。

## 已有session

| 角色 | 实际ID与来源 | 状态 | 当前任务与优先级 | 入口 |
| --- | --- | --- | --- | --- |
| TokenScope总设计 | 未知，历史未核实 | 休眠 | 用户唤醒后处理总体边界与协调，不代写任务方案 | [总设计](../docs/tasks/product/ENTRY.md) |
| Token监控后端开发V1 | 01a1682f-956d-7630-afe7-e123ba38dfc0，历史环境登记 | 休眠 | 保留V1能力/现场交接；不自动启动修复或打包 | [监控V1](../docs/tasks/monitoring/ENTRY.md) · [验收](../docs/huawei/MONITORING_V1_ACCEPTANCE_20261030.md) |
| Token监控前端开发V1 | 01a17811-4c9a-7513-befc-b35723aec96e，前端环境已核实 | 休眠 | F007/UI-01和两份新前端prompt交接完成，保留原型开发起点 | [前端交接](../docs/tasks/viewer/ENTRY.md) · [UI-01](../docs/tasks/viewer/PROTOTYPE_V2_UI_01.md) |
| V2版本总设计师（原镜像打包与审查／完整服务总负责） | 01a1800e-80b4-7400-a78b-a84f5b6e888d，2026-11-03环境CODEX_THREAD_ID/CODEX_SESSION_ID一致再次核实 | 后端五关及两前端产品冻结；根第一阶段E2E通过，完整回归/发布进行中 | 六线统筹、独立验收、停旧冷启动E2E、固定commit/push及WSL构建/桌面交付；按执行板推进，不代签现场 | [总计划](../docs/tasks/delivery/V2_REPAIR_COORDINATION_PLAN_20261103.md) · [本线记忆](tasks/delivery.md) · [交付入口](../docs/tasks/delivery/ENTRY.md) |
| V2 Token监控后端（原父会话） | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境与应用列表核实 | 历史角色；同一会话已按用户指派转为同事监控后端 | 已完成产品讨论、分线与版本整理；不再以父会话接管两线 | [产品记忆](tasks/monitoring.md) · [检查点](../docs/operations/V2_HANDOFF_20261030.md) |
| V2 同事监控后端设计与开发 | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境核实 | HV2 MA解释资源已独立通过冻结，源码窗口关闭 | 维护MA数据/预热/独立与配对指标和availability；按总负责定向处理后续问题，真实cached缺失不补造；[冻结](../docs/tasks/delivery/HV2_MA_FREEZE_20261103.json) | [MA入口](../docs/tasks/monitoring/v2-ma/ENTRY.md) · [记忆](tasks/monitoring-v2-ma.md) |
| V2 用户监控后端—功能设计与开发 | 01a18bc7-cdb5-7830-a185-ad3aa6257b21，环境核实 | HV2用户2.1.0目录及默认TTFT已独立通过冻结，源码窗口关闭 | 多模型发现、同Trace来源与用户提供τ已实现；前端接入支持和问题归口，未校准；[冻结](../docs/tasks/delivery/HV2_USER_FREEZE_20261103.json) | [本线ENTRY](../docs/tasks/monitoring/v2-user/ENTRY.md) · [设计](../docs/tasks/monitoring/v2-user/DESIGN.md) · [记忆](tasks/monitoring-v2-user.md) |
| 低命中率分析后端设计和开发（原异常分析母会话） | 01a18be2-7112-7aa2-919b-5137d1f1b1ad，2026-10-31环境THREAD/SESSION ID一致复核 | HV2公共第一关及低命中第二关均独立通过冻结，源码窗口关闭 | 公共层唯一维护方与L1–L5私有开发；等待定向问题，不恢复历史arpc/RV2提交；[公共冻结](../docs/tasks/delivery/HV2_COMMON_FREEZE_20261103.json)／[私有冻结](../docs/tasks/delivery/HV2_LOW_HIT_FREEZE_20261103.json) | [本线ENTRY](../docs/tasks/prefix-analysis/ENTRY.md) · [记忆](tasks/prefix-analysis.md) · [分线交接](../docs/tasks/analysis/BACKEND_SPLIT_HANDOFF.md) |
| Token异常分析后端设计和开发 | 01a18fcd-0464-7cf1-b435-4f394bd33e66，环境再次核实 | HV2私有优化/预算消费独立通过冻结，源码窗口关闭 | T2–T4私有维护与现场成本方案；无新生产recipe/质量收益承诺；[冻结](../docs/tasks/delivery/HV2_TOKEN_FREEZE_20261103.json) | [前端交接](../docs/tasks/length-analysis/FRONTEND_HANDOFF.md) · [记忆](tasks/length-analysis.md) |
| Token监控V2前端设计与开发 | 01a18c49-d9b4-7a33-8c04-e5a72adfcc24，本会话环境CODEX_THREAD_ID与CODEX_SESSION_ID一致核实 | HV2完整接入交接完成，75项独立定点测试通过，窗口关闭待根完整E2E | 保持UI02/四入口；完整多模型发现、固定历史、仅W/SLO日常输入和MA缺数解释；不独立监听/Git/打包 | [修复交接](../achieve/2026-10-31/monitoring-v2-review/docs/tasks/viewer/monitoring-v2/REVIEW_FIX_HANDOFF_20261031.md) · [本线ENTRY](../docs/tasks/viewer/monitoring-v2/ENTRY.md) · [记忆](tasks/viewer-monitoring-v2.md) |


## 待创建或登记session

用户监控、同事监控后端、低命中主会话（原异常分析母会话）及监控V2前端均已登记。Token异常已获用户允许并完成fork，真实ID已登记；启动prompt已发送，active及子会话环境身份复核已确认。两条监控后端平行推进，不将此前“TTFT排在MA之后”的建议当作强制依赖。

| 角色 | 实际ID／状态 | 优先任务与范围 | 依赖与入口 |
| --- | --- | --- | --- |
| 异常分析前端维护（原本机阶段总负责） | 01a19111-344a-75c1-84e0-14db8be08f4f，已核实 | HV2 c3接入与独立335项/第一阶段浏览器通过，源码和测试窗口已关闭 | v2 partial可读/状态与批准L4L5、固定来源revision；本线实施后根独立复审。异常前端归口维护、现场问题支持及被协调复验；不继续统一指挥后端或华为验收，不作为新总负责与后端中转；原交付/验证身份保持 | [职责交接](../docs/tasks/analysis/ONSITE_COORDINATION_HANDOFF_20261101.md) · [前端入口](../docs/tasks/viewer/analysis/ENTRY.md) |
| hybrid attention仿真 | 无session；暂不做 | 不调研设计或开发，不作为监控两线依赖 | 保留现有近似的能力边界 |
| 自进化Agent | 未知；未启动 | 两类诊断设计与代码均完成后由用户另行启动 | [Agent ENTRY](../docs/tasks/evolution-agent/ENTRY.md) |

## 当前协作边界

各维护方处理本模块设计/代码及本线测试；V2总设计师直接协调六线、先验收异常公共层和对应后端、固化契约后交前端，最后独立完整验收与授权交付。用户监控与异常同Trace模型规格，MA独立数据及模型制品；逐模型TTFT默认τ由用户提供，K默认8192，前端日常只填W/SLO，具体分工见总计划。其他角色ID及既有历史进度保持；六线本轮prompt已实发，全部后端已验收冻结、两前端正式接入实施，实际进度见执行板，不唤醒历史总设计/V1。现场只按用户指定appid/模型/方向，不自动启动hybrid/自进化Agent。

## 2026-11-03用户后端历史版本交接复核

仅补充用户后端角色（01a18bc7-cdb5-7830-a185-ad3aa6257b21）：U006–U008已closed且源码a4053db与回执ac06998已进入GitHub main；前端历史接入入口为[TTFT交接](../docs/tasks/monitoring/v2-user/TTFT_FRONTEND_HANDOFF.md)，[本次复核](../docs/tasks/monitoring/v2-user/GIT_HANDOFF_U008_20261031.md)。真实性能校准仍待完成。当前HV2-R1-USER属于后续独立修复，仍按执行板推进，不纳入此次历史版本提交，不改变其他session状态。

2026-11-03勘误：上节用户后端U008历史复核来自该session上下文恢复误读，非本轮新增用户指令；对应d55df94只含3份文档，不含HV2源码。总设计师已恢复HV2-R1-USER任务，不以旧交接代替本轮验收，具体见执行板。

## HV2当前阶段确认（2026-11-03，总设计师核对）
公共层、用户2.1.0、MA解释资源、Token与低命中私有五项均已独立通过并冻结；后端源码窗口关闭。监控前端交接完成、75项独立定点测试通过、源码窗口关闭。异常前端c3已交接并通过独立335项与第一阶段真实浏览器，HV2-AF-01闭环。第一阶段已正常停启核验156资源/业务行一致，正在新的独立state完成旧功能/最终视觉回归，本轮产品源码未发布或打包。实际证据与后续阶段以执行板为准，各分线不自行Git/push、监听或打包。

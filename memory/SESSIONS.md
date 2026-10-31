# Session 角色与任务登记

2026-10-31：审查session实际环境ID `01a1800e-80b4-7400-a78b-a84f5b6e888d` 已再次核实。本轮监控V2评审/修复/Git链已闭环并归档；[当前状态](../docs/tasks/delivery/MONITORING_V2_STATUS.md)。当前P1为入口和记忆整理，等待异常分析前后端验收后统一交付，暂不打包。其他session角色与工作保留。

更新：2026-10-30，依据用户最新分工及“先整理并push，暂不创建聊天”的明确回复。本文是角色/状态权威入口，覆盖旧四会话分工和旧串行V2推进顺序。状态按用户安排记录，不把应用idle等瞬时状态当作角色休眠。

## 每个session首先做什么

P0：AGENTS → CURRENT → 本登记 → docs/README → 本角色ENTRY。首次回复明确角色、任务与排除范围、当前阶段、优先级、依赖和下一步；取得实际ID再登记，未知写未知，不复用父会话ID。角色未明确不进入设计/编码。P1读自己的产品输入/当前设计/契约及直接依赖；P2按问题读证据、源码与研究；P3才追历史。fork继承上下文，不继承父会话全部职责或实施授权。

## 已有session

| 角色 | 实际ID与来源 | 状态 | 当前任务与优先级 | 入口 |
| --- | --- | --- | --- | --- |
| TokenScope总设计 | 未知，历史未核实 | 休眠 | 用户唤醒后处理总体边界与协调，不代写任务方案 | [总设计](../docs/tasks/product/ENTRY.md) |
| Token监控后端开发V1 | 01a1682f-956d-7630-afe7-e123ba38dfc0，历史环境登记 | 休眠 | 保留V1能力/现场交接；不自动启动修复或打包 | [监控V1](../docs/tasks/monitoring/ENTRY.md) · [验收](../docs/huawei/MONITORING_V1_ACCEPTANCE_20261030.md) |
| Token监控前端开发V1 | 01a17811-4c9a-7513-befc-b35723aec96e，前端环境已核实 | 休眠 | F007/UI-01和两份新前端prompt交接完成，保留原型开发起点 | [前端交接](../docs/tasks/viewer/ENTRY.md) · [UI-01](../docs/tasks/viewer/PROTOTYPE_V2_UI_01.md) |
| Token监控V2前端设计与开发 | 01a18c49-d9b4-7a33-8c04-e5a72adfcc24，本会话环境CODEX_THREAD_ID与CODEX_SESSION_ID一致核实 | RV2-01/02/03修复已独立复审通过并推送main；维护支持 | 保持UI-02；用户2.0.0/MA1.0.0及S0；已补身份/导出/排行与冷state回归，最终复审及Git收口已由审查方完成；TTFT性能校准待完成，未构建镜像/部署打包 | [修复交接](../achieve/2026-10-31/monitoring-v2-review/docs/tasks/viewer/monitoring-v2/REVIEW_FIX_HANDOFF_20261031.md) · [本线ENTRY](../docs/tasks/viewer/monitoring-v2/ENTRY.md) · [记忆](tasks/viewer-monitoring-v2.md) |
| 镜像打包和审查 | 01a1800e-80b4-7400-a78b-a84f5b6e888d，本轮实际环境核实 | 监控V2复审/Git收口完成；归档整理，等待统一交付 | 三项问题已关闭；main已推送；暂不打包，待异常分析前后端验收；其他会话工作保留 | [当前状态](../docs/tasks/delivery/MONITORING_V2_STATUS.md) · [本线入口](../docs/tasks/delivery/ENTRY.md) |
| V2 Token监控后端（原父会话） | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境与应用列表核实 | 历史角色；同一会话已按用户指派转为同事监控后端 | 已完成产品讨论、分线与版本整理；不再以父会话接管两线 | [产品记忆](tasks/monitoring.md) · [检查点](../docs/operations/V2_HANDOFF_20261030.md) |
| V2 同事监控后端设计与开发（本会话） | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境核实 | M000–M005 closed；版本同步与前端交接，后续维护 | ma-backend-local-1；源码已在获授权的后端集成提交中，本轮仅追加MA交接；未部署打包 | [交接](../docs/tasks/monitoring/v2-ma/FRONTEND_HANDOFF.md) · [Git身份](../docs/tasks/monitoring/v2-ma/GIT_CHECKPOINT.md) · [记忆](tasks/monitoring-v2-ma.md) |
| V2 用户监控后端—功能设计与开发 | 01a18bc7-cdb5-7830-a185-ad3aa6257b21，环境核实 | U006–U008 closed且源码已push；代码完成，性能校准待完成；前端接入支持 | 2026-10-31最小TTFT模型已实现，契约2.0.0；W覆盖全部非计算、不单列O，证据选填，旧历史兼容。380全量＋最终126测试、类型/静态/契约审计通过；前端交接完成但未改前端，现场/真实校准待完成 | [本线ENTRY](../docs/tasks/monitoring/v2-user/ENTRY.md) · [设计](../docs/tasks/monitoring/v2-user/DESIGN.md) · [记忆](tasks/monitoring-v2-user.md) |

## 待创建或登记session

用户与MA后端均已登记；其余角色保持各自提交时点状态。本轮不创建聊天、不发跨会话消息。两条监控后端平行推进，不将此前“TTFT排在MA之后”的建议当作强制依赖。

| 角色 | 实际ID／状态 | 优先任务与范围 | 依赖与入口 |
| --- | --- | --- | --- |
| 异常分析后端设计 | 未知；待创建/登记 | 先统一调研、产品设计，明确两类分析边界及证据需求；不属于监控功能增加 | [分析母会话ENTRY](../docs/tasks/analysis/ENTRY.md)；产品阶段完成后按用户启动fork下面两线 |
| 低命中率分析后端 | 未知；后续fork，未启动 | 母会话调研/产品设计完成后承接本线详细设计与开发 | [低命中ENTRY](../docs/tasks/prefix-analysis/ENTRY.md)；复用监控统一计量 |
| Token异常分析后端 | 未知；后续fork，未启动 | 母会话调研/产品设计完成后承接本线详细设计与开发 | [Token异常ENTRY](../docs/tasks/length-analysis/ENTRY.md)；复用统一编码计量 |
| 异常分析前端设计与开发 | 未知；待创建/登记 | 两类业务建议/证据报告；先职责/后端就绪核对 | [异常前端prompt](../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md)；后续对接两条分析后端，不使用监控前端prompt代替 |
| hybrid attention仿真 | 无session；暂不做 | 不调研设计或开发，不作为监控两线依赖 | 保留现有近似的能力边界 |
| 自进化Agent | 未知；未启动 | 两类诊断设计与代码均完成后由用户另行启动 | [Agent ENTRY](../docs/tasks/evolution-agent/ENTRY.md) |

## 共享职责与交接

- 两监控后端共用统一Tokenizer/Template、计量和理想命中基础，各自维护本线场景/结果语义，不复制公共算法。每项公共模块或契约改动先在本登记/任务ENTRY注明唯一维护会话、影响范围和接入版本；未分配的公共改动不同时编辑。V1休眠会话不自动成为活动维护方。
- 两前端分别负责监控/异常界面；共享路由、样式、状态/API、锁文件同样按一次改动一个维护方。UI-01是初版认可起点，不是正式后端能力或新契约。
- 详细设计、开发与验证由新session和用户推进；职责安排不等于全部方案/接口/batch已审批。V1兼容/数据质量作为相关依赖保留，不在本轮另启修复。
- 文档交接不等于已通知。共享文件修改前读最新状态，每轮维护实际进度；见[工作流](../docs/architecture/TASK_SESSION_WORKFLOW.md)。旧登记见[归档](../achieve/2026-10-28/snapshots/memory/SESSIONS.md)。

后端交接更新（2026-10-30）：用户U000–U005、MA M000–M005均closed；本次收录用户线及已闭环MA接入依赖。共享app/CLI编辑窗口已释放，用户索引经Dispatcher.register接入共同worker.lock。用户会话转入前端接入支持/后端维护；[前端交接入口](../docs/tasks/monitoring/v2-user/FRONTEND_HANDOFF.md)。前端接收/真实校准/现场仍待验证，不部署打包；其他会话未完成工作不纳入本次提交。

用户后端源码交接9a037466f7211126261ec2026f54b9c19c2e2151已push origin main并核实远端SHA；当前为前端接入支持/后端维护。[交接入口](../docs/tasks/monitoring/v2-user/FRONTEND_HANDOFF.md)。其他会话未完成材料留在工作区，未部署打包。

用户监控U006–U008本轮获授权提交/push；当前前端接入支持/后端维护，性能校准待完成；[Git检查点](../docs/tasks/monitoring/v2-user/GIT_HANDOFF_U008_20261031.md)。只暂存本线共享段落，其他会话未完成材料保留本地，未部署打包。

2026-10-31推送确认：U006–U008源码提交a4053db5789fa9460b1fae4097a8835b2554357c已push origin main，git ls-remote核实远端同一SHA；本地身份u008-local-1/契约2.0.0。仅本线44文件及共享记忆本线段落入提交，其他session未完成材料保留工作区。当前前端接入支持/后端维护；代码完成，性能校准待完成。未修改前端、部署或打包。

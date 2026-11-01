# Session 角色与任务登记

ARPC005公共app/bootstrap装配窗口已释放：ARPC006验证完成，当前arpc-local-1交接支持；不修改正式前端、不打包部署。

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
| 镜像打包和审查 | 01a1800e-80b4-7400-a78b-a84f5b6e888d，2026-11-01环境再次核实 | 用户明确授权后已接收并启动RV2统一审查；两后端独立复审保持 | P0：固定组合/前端聚合/完整服务审查，问题回总负责协调，独立复验通过后正式镜像/代码包/执行prompt交付；发布工具归口维护，Git由总负责收口；无桌面写入或远端部署 | [当前执行](../docs/tasks/analysis/UNIFIED_REVIEW_DELIVERY_EXECUTION_20261101.md) |
| V2 Token监控后端（原父会话） | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境与应用列表核实 | 历史角色；同一会话已按用户指派转为同事监控后端 | 已完成产品讨论、分线与版本整理；不再以父会话接管两线 | [产品记忆](tasks/monitoring.md) · [检查点](../docs/operations/V2_HANDOFF_20261030.md) |
| V2 同事监控后端设计与开发（本会话） | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be，环境核实 | MA监控已闭环；现场启动/功能验证与Bug维护 | 2026-10-31用户限定：负责华为机服务启动、功能验证及发现的MA Bug修复；P90 TTFT/校准由用户监控线讨论，不继续扩展本线设计 | [MA入口](../docs/tasks/monitoring/v2-ma/ENTRY.md) · [记忆](tasks/monitoring-v2-ma.md) |
| V2 用户监控后端—功能设计与开发 | 01a18bc7-cdb5-7830-a185-ad3aa6257b21，环境核实 | U006–U008 closed且源码已push；代码完成，性能校准待完成；前端接入支持 | 2026-10-31最小TTFT模型已实现，契约2.0.0；W覆盖全部非计算、不单列O，证据选填，旧历史兼容。380全量＋最终126测试、类型/静态/契约审计通过；前端交接完成但未改前端，现场/真实校准待完成 | [本线ENTRY](../docs/tasks/monitoring/v2-user/ENTRY.md) · [设计](../docs/tasks/monitoring/v2-user/DESIGN.md) · [记忆](tasks/monitoring-v2-user.md) |
| 低命中率分析后端设计和开发（原异常分析母会话） | 01a18be2-7112-7aa2-919b-5137d1f1b1ad，2026-10-31环境THREAD/SESSION ID一致复核 | arpc-local-4独立复审通过；2026-11-01 RV2-L聚合接入验证闭环，L4/L5各唯一6请求、215只读路由通过；精确提交清单交总负责统一收口，本线不commit/push、不打包部署 | L1–L5后端设计开发；兼任公共分析结果/范围/证据/离线评估封装的单一设计集成维护方，复用监控算法；Token fork已获准创建 | [本线ENTRY](../docs/tasks/prefix-analysis/ENTRY.md) · [记忆](tasks/prefix-analysis.md) · [分线交接](../docs/tasks/analysis/BACKEND_SPLIT_HANDOFF.md) |
| Token异常分析后端设计和开发 | 01a18fcd-0464-7cf1-b435-4f394bd33e66，环境再次核实 | T2–T4+arpc-local-4独立复审通过（明确限制），164本线+12独立边界+14只读GET，无阻断或业务修改；RV2-T精确清单交总负责统一收口，本线不commit/push、不打包部署 | 唯一维护src/tokenscope/token_content、tests/unit/token_content、tests/integration/token_content及本线文档；不改公共源码；参数错配独立，不打包部署 | [前端交接](../docs/tasks/length-analysis/FRONTEND_HANDOFF.md) · [记忆](tasks/length-analysis.md) |
| Token监控V2前端设计与开发 | 01a18c49-d9b4-7a33-8c04-e5a72adfcc24，本会话环境CODEX_THREAD_ID与CODEX_SESSION_ID一致核实 | RV2-01/02/03修复已独立复审通过并推送main；维护支持 | 保持UI-02；用户2.0.0/MA1.0.0及S0；已补身份/导出/排行与冷state回归，最终复审及Git收口已由审查方完成；TTFT性能校准待完成，未构建镜像/部署打包 | [修复交接](../achieve/2026-10-31/monitoring-v2-review/docs/tasks/viewer/monitoring-v2/REVIEW_FIX_HANDOFF_20261031.md) · [本线ENTRY](../docs/tasks/viewer/monitoring-v2/ENTRY.md) · [记忆](tasks/viewer-monitoring-v2.md) |


## 待创建或登记session

用户监控、同事监控后端、低命中主会话（原异常分析母会话）及监控V2前端均已登记。Token异常已获用户允许并完成fork，真实ID已登记；启动prompt已发送，active及子会话环境身份复核已确认。两条监控后端平行推进，不将此前“TTFT排在MA之后”的建议当作强制依赖。

| 角色 | 实际ID／状态 | 优先任务与范围 | 依赖与入口 |
| --- | --- | --- | --- |
| 异常分析功能总负责（兼前端设计与开发） | 01a19111-344a-75c1-84e0-14db8be08f4f，已核实 | 用户已认可L4/L5展示并授权统一审查→修复复验→打包交付；prompt已实际发送并获接收，当前跟进审查 | P0：前端及两后端归口修复协调、Git统一收口、最终交付文件/版本/SHA256核验；打包由审查会话执行，无远端部署 | [执行与授权](../docs/tasks/analysis/UNIFIED_REVIEW_DELIVERY_EXECUTION_20261101.md) · [联合报告](../docs/tasks/analysis/JOINT_VALIDATION_RV2_20261101.md) |
| hybrid attention仿真 | 无session；暂不做 | 不调研设计或开发，不作为监控两线依赖 | 保留现有近似的能力边界 |
| 自进化Agent | 未知；未启动 | 两类诊断设计与代码均完成后由用户另行启动 | [Agent ENTRY](../docs/tasks/evolution-agent/ENTRY.md) |

## 共享职责与交接

- 两监控后端共用统一Tokenizer/Template、计量和理想命中基础，各自维护本线场景/结果语义，不复制公共算法。每项公共模块或契约改动先在本登记/任务ENTRY注明唯一维护会话、影响范围和接入版本；未分配的公共改动不同时编辑。V1休眠会话不自动成为活动维护方。
- MA最终设计的[公共职责表](../docs/tasks/monitoring/v2-ma/BATCH_PLAN.md)区分用户线时间/别名/模式/开放排行箱与MA专属编排/接口/worker接入；旧distribution/V1链键不变。M000锁定接入版本，M004改app/CLI前登记具体diff，尚未发生源码占用或对方签收。
- 异常分析v0.4已获用户审批；原母会话转任低命中后端，继续维护共同产品/交接及公共分析封装的设计集成，Token异常已获准fork并承接本线。具体唯一维护范围见[分线交接](../docs/tasks/analysis/BACKEND_SPLIT_HANDOFF.md)。当前两线本地后端实现/验证完成，公共Schema/HTTP版本已交付；实际状态见两线批次记录，不接管监控算法或前端。
- 两前端分别负责监控/异常界面；共享路由、样式、状态/API、锁文件同样按一次改动一个维护方。UI-01是初版认可起点，不是正式后端能力或新契约。
- 监控V2前端本轮维护本线docs/tasks/viewer/monitoring-v2中的UI-02 HTML/manifest/评审记录、artifacts/prototypes/monitoring-v2/ui02及对应验证材料、ENTRY/记忆和自身共享登记。未占用apps/viewer公共源码、未改原UI-01或后端契约；此授权仅为展示原型，不代签后端/现场或跳过正式交互与开发方案阶段。
- 详细设计、开发与验证由新session和用户推进；职责安排不等于全部方案/接口/batch已审批。V1兼容/数据质量作为相关依赖保留，不在本轮另启修复。
- 文档交接不等于已通知。共享文件修改前读最新状态，每轮维护实际进度；见[工作流](../docs/architecture/TASK_SESSION_WORKFLOW.md)。旧登记见[归档](../achieve/2026-10-28/snapshots/memory/SESSIONS.md)。

MA本会话最新状态：M000–M005本机后端闭环，共享app/CLI编辑窗口已释放；用户线后续装配前重读最新代码，使用Dispatcher.register接入其持同worker.lock的索引处理器。真实三线联合待对方实现，不声称已通知或已签收。

用户线当前U001修改窗口：src/tokenscope/ingestion/csv_reader.py、src/tokenscope/domain.py及本线测试/契约；公共API/worker/CLI由MA窗口维护，不在本批覆盖；statistics/simulation保持不变。已登记不等于跨会话已通知。

U001追加公共修改：monitoring/storage.py的update_settings，在既有CAS事务内验证新别名跨模型冲突；不改schema/worker。旧配置读取不变。

MA M004已完成的共享修改：api/app.py仅增加MA路由/worker dispatcher；cli.py仅增加ma-*命令和work-once统一轮转；新增monitoring/dispatcher.py。不覆盖用户线csv_reader/domain/storage；不修改旧S0。当前用户索引适配未出现，注册接口预留，真实联合单列pending。

用户线U003共享编辑窗口：已复核MA释放状态，本线接入api/app.py和cli.py的独立user-v2路由及Dispatcher.register(user)；保留MA/V1逻辑。U002已closed，继续U003–U005，无部署打包。

用户线U005已closed：共享app/CLI窗口释放；保持MA/V1处理器，通过Dispatcher.register(user)接入。当前契约1.0.1，实际API与289回归/15增量/真实MA联合证据见本线U005 RESULT。早期U001/U003窗口文字为历史记录；不得据此重复占用。未部署打包，前端/真实校准/现场仍pending。

用户后端本轮整理提交/push及前端交接；[本线交接入口](../docs/tasks/monitoring/v2-user/FRONTEND_HANDOFF.md)。共享文件只暂存后端有关内容，其他会话未完成进度保留工作区；没有发送跨会话消息或代签前端接收。

用户后端源码交接9a037466f7211126261ec2026f54b9c19c2e2151已push origin main并核实远端SHA；当前为前端接入支持/后端维护。[交接入口](../docs/tasks/monitoring/v2-user/FRONTEND_HANDOFF.md)。其他会话未完成材料留在工作区，未部署打包。

2026-10-30本会话按用户最新要求维护TTFT校准最小清单、跨线状态与交接文档；补后端缺参回归，修正UI-02原型空等待转0及默认假设展示（含本地原型生成源/摘要），不接管正式前端开发、不改后端公式/API契约、不改V1配置。

2026-10-31用户授权本线TTFT增量U006–U008：唯一维护user_monitoring/contracts.py、estimator.py、api/user.py及本线契约/测试；不占用公共app/CLI或前端。按批验证闭环后继续，性能校准仍pending。

2026-10-31用户线U006–U008已closed，上述本线编辑窗口释放；契约2.0.0接入与兼容依据TTFT_FRONTEND_HANDOFF.md。未修改前端、部署打包或跨会话通知。

用户监控U006–U008本轮获授权提交/push；当前前端接入支持/后端维护，性能校准待完成；[Git检查点](../docs/tasks/monitoring/v2-user/GIT_HANDOFF_U008_20261031.md)。只暂存本线共享段落，其他会话未完成材料保留本地，未部署打包。

2026-10-31推送确认：U006–U008源码提交a4053db5789fa9460b1fae4097a8835b2554357c已push origin main，git ls-remote核实远端同一SHA；本地身份u008-local-1/契约2.0.0。仅本线44文件及共享记忆本线段落入提交，其他session未完成材料保留工作区。当前前端接入支持/后端维护；代码完成，性能校准待完成。未修改前端、部署或打包。

2026-10-31低命中会话LH008共享窗口：重读最新app.py/cli.py和登记，增加diagnostics服务装配、独立路由、Dispatcher.register；不改监控V1/user/MA算法或已有路由。其他共享编辑窗口已释放，异常API由本线唯一维护。

2026-10-31低命中LH008：共享app/CLI只增加diagnostics装配，监控兼容300项通过，窗口已释放。公共与本线源码继续LH009检查/交接，不修改监控算法或Token私有模块。

2026-10-31异常分析前端共享窗口：本线维护apps/viewer/src/app.tsx路由分派、features/v2/V2App.tsx导航入口、vite.config.ts增加diagnostics开发代理；独立分析模块/测试，不改监控业务与后端。用户授权AF000–AF006逐批闭环，普通修复自主，范围/接口变化再确认。

2026-10-31异常分析前端AF006：本线共享app.tsx/V2App.tsx/vite.config.ts编辑窗口释放；后端与监控业务逻辑未改。当前等待用户功能/视觉验收，复审prompt已准备，未打包部署。

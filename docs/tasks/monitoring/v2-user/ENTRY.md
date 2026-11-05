# V2 用户监控后端功能入口

2026-11-05：用户暂时接受V2，产品宣传优先；[现场核对与保留问题](../../delivery/HV2_ACCEPTANCE_CLOSE_20261105.md)为当前版本状态。本线HV2源码窗口关闭，不自动修复/重构/复测。V3先真实业务场景、定位与功能取舍及32GiB资源约束讨论；后续有新定向任务再恢复。以下保留对应版本维护资料，旧“待验/未打包”等不覆盖本段。

P0：AGENTS→CURRENT→SESSIONS→本入口；当前维护优先读取[HV2用户后端交接](HV2_USER_BACKEND_HANDOFF_20261103.md)及[用户2.1.0契约](../../../contracts/user-monitoring-v2/2.1.0/README.md)。默认τ为用户提供1/2.7/2.6秒，K8192，真实性能校准待完成。

本线职责及ID保持，后续现场问题由镜像打包与审查会话按新任务定向协调；不自行重跑旧派发prompt或改变批准展示。旧阶段/候选回执已[完整归档](../../../../achieve/2026-11-03/hv2-delivery-closed/docs/tasks/monitoring/v2-user/ENTRY.md)。以下为版本化维护材料，历史批次状态不覆盖本段。
## 优先阅读

P0：AGENTS → CURRENT → SESSIONS → docs/README → 本入口。
P1：[TTFT增量验收](batches/U008/RESULT.md) → [TTFT前端交接](TTFT_FRONTEND_HANDOFF.md) → [既有最终报告](batches/U005/RESULT.md) → [已实现API](IMPLEMENTED_API.md) → [分层验收](batches/U005/VALIDATION_SUMMARY.md) → [设计符合性](batches/U005/DESIGN_CONFORMANCE.md) → [版本](VERSIONS.md)。
需要修改时再读[当前设计v1.1（最小产品方案获认可，后端适配已实现）](DESIGN.md)、[批次计划](BATCH_PLAN.md)、[交叉检查](CROSSCHECK_MA_20261030.md)及相关batch四文档。设计目标与实际验证分别以设计/最终报告为准，不用旧“未实现”描述覆盖现状。
P2：按问题读[V1实际API](../../../contracts/MONITORING_IMPLEMENTED_API.md)、[S0](../batches/B005.1/S0_CONTRACT.md)、[现场验收](../../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)、[MaaS](../../../architecture/MAAS_REFERENCE.md)、[MA设计](../v2-ma/DESIGN.md)及[UI-01](../../viewer/PROTOTYPE_V2_UI_01.md)。

## 范围与接入

- GB appid×common_name独立、每CSV空缓存；原JSON先tokenization得到J，P套模板，C=P−H；排行基于C众数箱内均值，最低并列箱为排序代表。
- V1 UTC日期/模型别名/DeepSeek现场模式兼容已修复；旧default不静默覆盖。生产缺省、GF资产/GLM CP限制保留。
- TTFT为P90长度固定chunk情景参考；等待参数化，无队列模型、总体命中达标保证或实测准确性承诺。
- 用户router/控制库/索引独立；HTTP worker及CLI work-once通过Dispatcher.register接入，与MA/V1共用同state_root/worker.lock。共享app/CLI编辑窗口已释放，接入方先读最新文件。
- 不负责MA编排、异常分析、前端、hybrid、自动采集或生产路由切换。内网开放仍由审查打包会话另行授权。

[契约2.0.0](../../../contracts/user-monitoring-v2/2.0.0/README.md) · [本线记忆](../../../../memory/tasks/monitoring-v2-user.md) · [角色登记](../../../../memory/SESSIONS.md)

## 源码/前端交接
本轮用户授权提交并push。前端首先阅读[用户后端交接](FRONTEND_HANDOFF.md)，提交边界见[Git交接检查点](GIT_HANDOFF_20261030.md)。本会话转为前端接入支持/后端维护，未部署打包。

## U006–U008提交交接（2026-10-31）
本轮用户授权提交/push，范围与实际Git身份见[U008 Git检查点](GIT_HANDOFF_U008_20261031.md)。优先采用[TTFT前端交接](TTFT_FRONTEND_HANDOFF.md)及契约2.0.0；前端接入支持/后端维护，性能校准待完成，不部署打包。

## 2026-11-03最新：HV2用户后端已独立验收并冻结

总设计师已确认用户监控发现与自动TTFT 2.1.0独立验收通过，权威[冻结清单](../../delivery/HV2_USER_FREEZE_20261103.json)，identity为4d9e2e5d6c7031ff0aaa266114b92dbcb8684b9a80d722d2cfae9de8ad1d7dc0。上方“候选/待独立验收”保留为此前状态，当前以本节及冻结清单为准。监控前端正式接入已派发，后端源码窗口关闭；本线等待总设计师归口后续问题，不自行修改、复测、提交/push或监听。

冻结仅覆盖清单列出的源码/测试、2.1.0与旧2.0.0契约及相关锁/S0身份，不代表前端验收或现场性能校准通过。现场622条数差、真实性能准确性及大历史目录规模仍未决。前端按[本轮交接](HV2_USER_BACKEND_HANDOFF_20261103.md)接入；不恢复旧U008工作。

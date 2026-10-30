# V2 用户监控后端功能入口

2026-10-30：用户已认可最终设计并授权连续开发。**U000–U005 closed，本地用户后端统一验收完成**；289全量回归及最终增量15项恢复测试通过，真实MA联合通过。未部署、打包或修改V1运行配置；前端、真实TTFT校准及现场仍pending。

## 优先阅读

P0：AGENTS → CURRENT → SESSIONS → docs/README → 本入口。
P1：[最终报告](batches/U005/RESULT.md) → [已实现API](IMPLEMENTED_API.md) → [分层验收](batches/U005/VALIDATION_SUMMARY.md) → [设计符合性](batches/U005/DESIGN_CONFORMANCE.md) → [版本](VERSIONS.md)。
需要修改时再读[获批设计v1.0](DESIGN.md)、[批次计划](BATCH_PLAN.md)、[交叉检查](CROSSCHECK_MA_20261030.md)及相关batch四文档。设计目标与实际验证分别以设计/最终报告为准，不用旧“未实现”描述覆盖现状。
P2：按问题读[V1实际API](../../../contracts/MONITORING_IMPLEMENTED_API.md)、[S0](../batches/B005.1/S0_CONTRACT.md)、[现场验收](../../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)、[MaaS](../../../architecture/MAAS_REFERENCE.md)、[MA设计](../v2-ma/DESIGN.md)及[UI-01](../../viewer/PROTOTYPE_V2_UI_01.md)。

## 范围与接入

- GB appid×common_name独立、每CSV空缓存；原JSON先tokenization得到J，P套模板，C=P−H；排行基于C众数箱内均值，最低并列箱为排序代表。
- V1 UTC日期/模型别名/DeepSeek现场模式兼容已修复；旧default不静默覆盖。生产缺省、GF资产/GLM CP限制保留。
- TTFT为P90长度固定chunk情景参考；等待参数化，无队列模型、总体命中达标保证或实测准确性承诺。
- 用户router/控制库/索引独立；HTTP worker及CLI work-once通过Dispatcher.register接入，与MA/V1共用同state_root/worker.lock。共享app/CLI编辑窗口已释放，接入方先读最新文件。
- 不负责MA编排、异常分析、前端、hybrid、自动采集或生产路由切换。内网开放仍由审查打包会话另行授权。

[契约1.0.1](../../../contracts/user-monitoring-v2/README.md) · [本线记忆](../../../../memory/tasks/monitoring-v2-user.md) · [角色登记](../../../../memory/SESSIONS.md)

## 源码/前端交接
本轮用户授权提交并push。前端首先阅读[用户后端交接](FRONTEND_HANDOFF.md)，提交边界见[Git交接检查点](GIT_HANDOFF_20261030.md)。本会话转为前端接入支持/后端维护，未部署打包。

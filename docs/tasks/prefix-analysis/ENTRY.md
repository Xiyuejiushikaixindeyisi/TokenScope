# 低命中率后端与公共层入口

2026-11-03：HV2修复已完成公共层→依赖后端独立验收及冻结→前端→源码与容器独立验收→WSL打包和桌面全SHA交付。源码 `c1345b6fd7d413a94420642ca1b4099b9ec104b4` 已push main；版本 `tokenscope-v2-hv2-20261103`。现场真实数据及用户两阶段验收待执行，六线开发窗口关闭。 [完整结果与现场prompt](../delivery/HV2_DELIVERY_20261103.md)。

P0：AGENTS→CURRENT→SESSIONS→本入口；当前维护优先读取[公共交接](HV2_COMMON_HANDOFF_20261103.md)与[低命中交接](HV2_LOW_HIT_BACKEND_HANDOFF_20261103.md)。公共层唯一维护方；保持F保留/方向预算/扫描覆盖分离，不恢复旧arpc任务。

本线职责及ID保持，后续现场问题由总设计师定向分配；不自行重跑旧派发prompt或改变批准展示。旧阶段/候选回执已[完整归档](../../../achieve/2026-11-03/hv2-delivery-closed/docs/tasks/prefix-analysis/ENTRY.md)。以下为版本化维护材料，历史批次状态不覆盖本段。

## 有效维护依据

实际session：01a18be2-7112-7aa2-919b-5137d1f1b1ad。负责L1–L5及analysis_common、diagnostics HTTP/任务/存储/Dispatcher，公共层唯一维护方；Token私有由其session维护。当前方向和预算以HV2冻结及实际实现为准，不套用历史隐式双方向启动流程。

- [公共HV2交接](HV2_COMMON_HANDOFF_20261103.md)、[低命中HV2交接](HV2_LOW_HIT_BACKEND_HANDOFF_20261103.md)、[公共冻结](../delivery/HV2_COMMON_FREEZE_20261103.json)、[低命中第二关冻结](../delivery/HV2_LOW_HIT_FREEZE_20261103.json)。第二关仅覆盖已授权两项prefix适配，第一关原证据保留。
- [已实现API](IMPLEMENTED_API.md)、[CODEMAP](CODEMAP.md)、[测试索引](TESTS.md)、[资源profile](RESOURCE_PROFILE.md)、[前端交接](FRONTEND_HANDOFF.md)。旧版本字段按相应冻结读取，不替代本轮v2契约。
- [公共历史Schema](../../contracts/analysis-common-1.0/README.md)、[HTTP历史Schema](../../contracts/diagnostics-http-1/README.md)、[后端交接](../analysis/BACKEND_IMPLEMENTATION_HANDOFF.md)。保持旧报告只读兼容。

现场只处理用户指定appid/模型/方向与冻结范围，业务GET不计算；L4/L5保持批准展示，不把差异相关性写成根因。完整评估/收益门槛保持，缺证据和partial如实说明。tools/messages新探测器先真实规模预算与正反例，不擅增recipe/T1/hybrid/Agent。源码窗口已关闭，现场问题由总设计师定向恢复。

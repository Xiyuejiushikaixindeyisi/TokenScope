# 低命中率后端与公共层入口

2026-11-10当前：V3低命中四P0由**[全新V3代码修复与开发角色](../development-v3/ENTRY.md)**先独立check、后续获准实施；本历史会话继续休眠。V3范围内公共层、低命中和必要前端兼容由新开发角色统一负责，不同时由旧公共层维护方修改。镜像会话仅审批/打包。待Token探索回传后再细化V3范围/顺序/验收。[当前范围](../product-v3/V3_SCOPE_AND_HANDOFF_20261110.md)。

以下“公共层唯一维护方”、恢复顺序和协调关系均为V2历史记录，仅供核对已交付源码与契约，不覆盖上述新分工。

## V2历史维护入口

2026-11-05：用户暂时接受V2，产品宣传优先；[现场核对与保留问题](../delivery/HV2_ACCEPTANCE_CLOSE_20261105.md)为当前版本状态。本线HV2源码窗口关闭，不自动修复/重构/复测。V3先真实业务场景、定位与功能取舍及32GiB资源约束讨论；后续有新定向任务再恢复。以下保留对应版本维护资料，旧“待验/未打包”等不覆盖本段。

P0：AGENTS→CURRENT→SESSIONS→本入口；当前维护优先读取[公共交接](HV2_COMMON_HANDOFF_20261103.md)与[低命中交接](HV2_LOW_HIT_BACKEND_HANDOFF_20261103.md)。公共层唯一维护方；保持F保留/方向预算/扫描覆盖分离，不恢复旧arpc任务。

本线职责及ID保持，后续现场问题由镜像打包与审查会话按新任务定向协调；不自行重跑旧派发prompt或改变批准展示。旧阶段/候选回执已[完整归档](../../../achieve/2026-11-03/hv2-delivery-closed/docs/tasks/prefix-analysis/ENTRY.md)。以下为版本化维护材料，历史批次状态不覆盖本段。

## 有效维护依据

实际session：01a18be2-7112-7aa2-919b-5137d1f1b1ad。负责L1–L5及analysis_common、diagnostics HTTP/任务/存储/Dispatcher，公共层唯一维护方；Token私有由其session维护。当前方向和预算以HV2冻结及实际实现为准，不套用历史隐式双方向启动流程。

- [公共HV2交接](HV2_COMMON_HANDOFF_20261103.md)、[低命中HV2交接](HV2_LOW_HIT_BACKEND_HANDOFF_20261103.md)、[公共冻结](../delivery/HV2_COMMON_FREEZE_20261103.json)、[低命中第二关冻结](../delivery/HV2_LOW_HIT_FREEZE_20261103.json)。第二关仅覆盖已授权两项prefix适配，第一关原证据保留。
- [已实现API](IMPLEMENTED_API.md)、[CODEMAP](CODEMAP.md)、[测试索引](TESTS.md)、[资源profile](RESOURCE_PROFILE.md)、[前端交接](FRONTEND_HANDOFF.md)。旧版本字段按相应冻结读取，不替代本轮v2契约。
- [公共历史Schema](../../contracts/analysis-common-1.0/README.md)、[HTTP历史Schema](../../contracts/diagnostics-http-1/README.md)、[后端交接](../analysis/BACKEND_IMPLEMENTATION_HANDOFF.md)。保持旧报告只读兼容。

现场只处理用户指定appid/模型/方向与冻结范围，业务GET不计算；L4/L5保持批准展示，不把差异相关性写成根因。完整评估/收益门槛保持，缺证据和partial如实说明。tools/messages新探测器先真实规模预算与正反例，不擅增recipe/T1/hybrid/Agent。源码窗口已关闭，现场问题由总设计师定向恢复。

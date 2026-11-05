# Token异常分析后端入口


2026-11-03：HV2修复已完成公共层→依赖后端独立验收及冻结→前端→源码与容器独立验收→WSL打包和桌面全SHA交付。源码 `c1345b6fd7d413a94420642ca1b4099b9ec104b4` 已push main；版本 `tokenscope-v2-hv2-20261103`。现场真实数据及用户两阶段验收待执行，六线开发窗口关闭。 [完整结果与现场prompt](../delivery/HV2_DELIVERY_20261103.md)。

P0：AGENTS→CURRENT→SESSIONS→本入口；当前维护优先读取[Token HV2交接](HV2_TOKEN_BACKEND_HANDOFF_20261103.md)。T2–T4和预算消费保持；生产recipe与tools/messages新探测器需要现场证据，不因本机通过自动启用。

本线职责及ID保持，后续现场问题由总设计师定向分配；不自行重跑旧派发prompt或改变批准展示。旧阶段/候选回执已[完整归档](../../../achieve/2026-11-03/hv2-delivery-closed/docs/tasks/length-analysis/ENTRY.md)。以下为版本化维护材料，历史批次状态不覆盖本段。

## 有效维护依据

实际session：01a18fcd-0464-7cf1-b435-4f394bd33e66。负责T2工具大返回注入、T3载荷重复搬运、T4历史工具结果负担，私有规则/受保护修改/目标范围离线评估；复用公共层与统一编码，不改L1–L5、不另建回放/结果存储。T1仅旧报告兼容，未恢复开发。

- [HV2实际交接](HV2_TOKEN_BACKEND_HANDOFF_20261103.md)、[本轮冻结](../delivery/HV2_TOKEN_FREEZE_20261103.json)、[前端接收](FRONTEND_HANDOFF.md)、[代码地图](CODEMAP.md)。
- [规则说明](../analysis/TOKEN_CONTENT_DETECTORS.md)、[公共分线边界](../analysis/BACKEND_SPLIT_HANDOFF.md)、[本线设计](DESIGN.md)、[验证方案](TESTS.md)。历史计划/候选状态只证明对应版本，当前以HV2交接/冻结源码为准。
- [SESSIONS](../../../memory/SESSIONS.md)、[本线记忆](../../../memory/tasks/length-analysis.md)、[公共层入口](../prefix-analysis/ENTRY.md)。

本轮序列化复用已通过171项及510种旧实现等价比较，未改变DSL/插件/预算/收益门槛。不能把字节当Token贡献；正常append-only不判浪费，缺关联不推断Loop/会话。真实生产recipe、容量预算、tools/messages正反例与收益仍需现场研究。源码窗口关闭，后续只按定向问题恢复；不重跑旧fork/启动prompt。

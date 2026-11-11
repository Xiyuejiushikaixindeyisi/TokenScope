# Token异常分析后端入口

2026-11-10当前：**Token异常在V3休眠，修复开发留V3.5**。旧成果保留可读，具体禁用/兼容方式待新开发会话复核后细化，本轮不改产品或唤醒本线。华为仅按[三组长尾探索prompt](../product-v3/HUAWEI_TOKEN_TAIL_EXPLORATION_PROMPT_20261110.md)对天舟/数据链/通知业务取证，回传后再细化V3公共能力衔接与V3.5私有方向。长尾不等于浪费，零建议不等于零发现。

V3获准公共修改由[全新开发角色](../development-v3/ENTRY.md)统一负责；镜像会话仅审批/打包。以下是V2维护历史，不作为本轮编码、运行旧分析器或重新派发任务的指令。[当前范围](../product-v3/V3_SCOPE_AND_HANDOFF_20261110.md)。

## V2历史维护入口


2026-11-05：用户暂时接受V2，产品宣传优先；[现场核对与保留问题](../delivery/HV2_ACCEPTANCE_CLOSE_20261105.md)为当前版本状态。本线HV2源码窗口关闭，不自动修复/重构/复测。V3先真实业务场景、定位与功能取舍及32GiB资源约束讨论；后续有新定向任务再恢复。以下保留对应版本维护资料，旧“待验/未打包”等不覆盖本段。

P0：AGENTS→CURRENT→SESSIONS→本入口；当前维护优先读取[Token HV2交接](HV2_TOKEN_BACKEND_HANDOFF_20261103.md)。T2–T4和预算消费保持；生产recipe与tools/messages新探测器需要现场证据，不因本机通过自动启用。

本线职责及ID保持，后续现场问题由镜像打包与审查会话按新任务定向协调；不自行重跑旧派发prompt或改变批准展示。旧阶段/候选回执已[完整归档](../../../achieve/2026-11-03/hv2-delivery-closed/docs/tasks/length-analysis/ENTRY.md)。以下为版本化维护材料，历史批次状态不覆盖本段。

## 有效维护依据

实际session：01a18fcd-0464-7cf1-b435-4f394bd33e66。负责T2工具大返回注入、T3载荷重复搬运、T4历史工具结果负担，私有规则/受保护修改/目标范围离线评估；复用公共层与统一编码，不改L1–L5、不另建回放/结果存储。T1仅旧报告兼容，未恢复开发。

- [HV2实际交接](HV2_TOKEN_BACKEND_HANDOFF_20261103.md)、[本轮冻结](../delivery/HV2_TOKEN_FREEZE_20261103.json)、[前端接收](FRONTEND_HANDOFF.md)、[代码地图](CODEMAP.md)。
- [规则说明](../analysis/TOKEN_CONTENT_DETECTORS.md)、[公共分线边界](../analysis/BACKEND_SPLIT_HANDOFF.md)、[本线设计](DESIGN.md)、[验证方案](TESTS.md)。历史计划/候选状态只证明对应版本，当前以HV2交接/冻结源码为准。
- [SESSIONS](../../../memory/SESSIONS.md)、[本线记忆](../../../memory/tasks/length-analysis.md)、[公共层入口](../prefix-analysis/ENTRY.md)。

本轮序列化复用已通过171项及510种旧实现等价比较，未改变DSL/插件/预算/收益门槛。不能把字节当Token贡献；正常append-only不判浪费，缺关联不推断Loop/会话。真实生产recipe、容量预算、tools/messages正反例与收益仍需现场研究。源码窗口关闭，后续只按定向问题恢复；不重跑旧fork/启动prompt。

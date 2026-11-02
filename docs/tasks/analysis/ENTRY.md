# 异常分析已批产品与分线交接入口

2026-11-02统一交付同步：V2已完成WSL打包、桌面全文件SHA核对，华为真实数据待验；用户认可V2可交付，UIR-03暂不修、留V3，不作V2阻断。本角色职责/休眠状态不变；当前发布与实际结果见[交付记录](../delivery/V2_APPROVED_DELIVERY_20261102.md)。现场只用真实Trace3/MA18 CSV，先用户监控（搜索/P90 TTFT）和MA，第一次用户验收并指定appid后才两类异常；SSH18002，唯一Markdown嵌关键源码/证据。[当前prompt](../../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md) · [固定规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md)。下方旧开发/交接状态按历史阅读，不覆盖本决定。

2026-11-01当前入口：[功能统筹RV2](../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/COORDINATION_RV2.md) · [联合验证报告](../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/JOINT_VALIDATION_RV2_20261101.md)。两后端已实际实现并完成独立复审，前端已修复L4/L5各一张卡、每类≤3例；Token仅T2–T4，前端只读，无参数/评估表单。用户指定异常前端session兼总负责，统一版本归档与GitHub收口，再给出审查打包prompt。下方v0.4产品/分线过程为历史依据，“待启动/未编码/T1–T4”等不代表当前状态。

2026-10-31：用户已审批产品v0.4。原母会话01a18be2-7112-7aa2-919b-5137d1f1b1ad继续负责[低命中率后端](../prefix-analysis/ENTRY.md)；[Token异常后端](../length-analysis/ENTRY.md)由已创建会话01a18fcd-0464-7cf1-b435-4f394bd33e66负责。用户已允许fork，启动prompt已发送且身份复核完成，当前进入两线后端详细设计。[分线交接与prompt](BACKEND_SPLIT_HANDOFF.md)为当前状态依据。

## 当前产品入口

已按用户纠偏重整并获批为v0.4产品基线，覆盖旧v0.3及其增量表述：

| 阅读顺序 | 文档 |
| --- | --- |
| 1 | [产品总览](PRODUCT_PROPOSAL.md)：两个独立页签、现有输入、范围和业务目标 |
| 2 | [低命中探测器](LOW_HIT_DETECTORS.md)：L1–L5逐项依据、数据能力、判据、建议、评估 |
| 3 | [Token内容探测器](TOKEN_CONTENT_DETECTORS.md)：T1–T4逐项依据、判据及内容负担/异常边界 |
| 4 | [流程与评估](PHASE1_PLAN.md)：仅目标appid窗口、原运行/子窗口基线、具体副本和组合评估 |
| 5 | [业务展示样例](DISPLAY_EXAMPLES.md)：九类规则卡片、零收益/负收益及输入不足 |
| 6 | [结果字段草案](RESULT_FIELDS_DRAFT.md)：事实、判据、来源、操作及评估分离，未冻结API |

[纠偏与证据核对](EVIDENCE_AND_SCOPE_REVISION_20261031.md)和[首轮研究](../../research/topics/AGENT_ANOMALY_RESEARCH_2026-10-30.md)保留来源追溯。PrefixLens只作参考，[原报告核对](../../research/implementations/PREFIXLENS_HUAWEI_REVIEW_2026-10-30.md)不决定业务清单或缓存算法。[旧v0.3](../../../achieve/2026-10-31/analysis-v0.3/README.md)已保存快照。

## 本轮固定的边界

- 只分析/回放目标appid、同服务/编码身份、明确窗口；不要求其他appid或整个生命周期历史。
- context_check/format_visibility下沉内部校验；用户不修改模型配置。没有固定业务探测优先级。
- 已知误注入cch元数据清理按业务信息无损处理，同集合定义不变的工具排序按稳定化修复处理。
- 低命中用输入差异证据，Token内容用具体来源负担/重复/业务策略；无阈值时不发明超限或无用结论。
- Loop/失败重试/子agent等仍只保留原数据需求，不做过程检测、不新增采集系统。
- 编码、Tokenizer/Template、理想命中计量由监控维护并复用；页面只读保存结果，不在GET时触发分析。

## 角色接口与依赖

监控提供请求/原文、J/P/H/C/O、IDs/证据及配置身份；分析提出缺口并消费统一能力，不复制算法。已有analysis-runs是监控接口，不代表诊断已实现，signals的pending_consumer同理。

用户已明确两线设计开发职责：主会话继续[低命中](../prefix-analysis/ENTRY.md)，[Token异常](../length-analysis/ENTRY.md)已获准fork并启动；低命中技术设计/CODEMAP已形成草案，Token线自行维护本线进度。[异常前端](../../../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md)未启动；本次只整理文档，不修改HTML、源码或冻结契约。

当前请求快照不保证session/turn/trace，字段Pointer不保证精确Token归属，源O不提供完整响应内容。这些是各规则降级的依据，不因规划而假定已有能力。

## 恢复与交接

P0：AGENTS → CURRENT → SESSIONS → docs/README → 本入口。P1阅读上述v0.4方案，P2按需核对[监控现场交接](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)、[实际API](../../contracts/MONITORING_IMPLEMENTED_API.md)、[S0](../monitoring/batches/B005.1/S0_CONTRACT.md)，不全量读取历史。

本轮文档链接/一致性及展示算术可检查，不能称业务探测器测试或实际回放。后续按本线详细设计和工作流推进开发；本次已完成授权fork并继续详细设计，未编码。详细历史与职责见[本线记忆](../../../memory/tasks/analysis.md)。

后端技术入口：[低命中详细设计](../prefix-analysis/DESIGN.md) · [公共接入草案](BACKEND_COMMON_CONTRACT_DRAFT.md) · [低命中验证设计](../prefix-analysis/TESTS.md)。这些是待评审技术文档，不是已实现或冻结接口。

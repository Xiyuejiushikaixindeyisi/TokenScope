# 自进化 Agent 任务入口

2026-11-02统一交付同步：用户认可V2可交付，UIR-03暂不修、留V3，不作V2阻断。本角色职责/休眠状态不变；当前发布与实际结果见[交付记录](../delivery/V2_APPROVED_DELIVERY_20261102.md)。现场只用真实Trace3/MA18 CSV，先用户监控（搜索/P90 TTFT）和MA，第一次用户验收并指定appid后才两类异常；SSH18002，唯一Markdown嵌关键源码/证据。[当前prompt](../../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md) · [固定规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md)。下方旧开发/交接状态按历史阅读，不覆盖本决定。

状态：依赖未满足。按用户安排，理想命中率低原因分析与单条请求长度异常分析均完成设计和代码开发后，才开始本任务的调研、设计与开发。

## 当前目标输入与责任

问题报警与归因不足警报同时成立时唤醒 Agent，并通知运维。Agent 使用对应 appid × 模型版本的原始数据和已有分析结果调查原因，产出候选探测器，通知运维验收。

候选规则与正式探测器分开保存。参考 SupervisorAgent 的具体方式由本任务后续研究；当前不开展预先调研、代码实现或外部通知。

## 阅读范围

- P0：项目 AGENTS、memory/CURRENT、本入口。
- P1：两类诊断最终交接中的当前设计、实际代码入口、结果/证据约定和验证结论；监控的报警与输入约定；本任务 [DESIGN](DESIGN.md)、[CODEMAP](CODEMAP.md)。
- P2：SupervisorAgent 等直接相关参考，以及解释具体问题所需原始证据。
- P3：监控与前端的无关实现、已被替代的诊断方案按需。

## 协作与维护范围

先消费已有诊断能力和共享探测器边界，再与用户共同设计调查、候选生成、验证和验收流程。代码维护范围为后续 src/tokenscope/agent、prompts/agent 及实际需要的接入；原始调查产物保存 artifacts/agent_runs。

本入口仅预留任务身份与阅读范围，不表示已创建 Agent 会话或已满足启动依赖。


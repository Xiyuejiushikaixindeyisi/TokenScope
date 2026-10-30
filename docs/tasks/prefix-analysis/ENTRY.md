# 理想命中率低原因分析任务入口

状态：2026-10-30用户最新分工：先由[异常分析后端母会话](../analysis/ENTRY.md)完成调研/产品设计，之后再按用户启动fork本线详细设计/开发。本线尚未创建/登记，不按旧安排直接启动。

## 当前目标输入与责任

研究 PrefixLens 华为完整版本的低命中诊断能力、现有实现与重构方式，分析动态内容、system prompt、前缀断点等原因，输出可解释证据与典型请求。

理想命中率计算归监控维护。本任务直接消费监控的结果或必要中间信息；需要计算能力时复用同一实现。不得形成独立的第二套理想命中口径，也不重复维护 Tokenizer/Template 编码链路。

## 阅读范围

- P0：项目 AGENTS、memory/CURRENT、本入口。
- P1首读：[监控现场验收及分析交接](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)、[监控代码地图](../monitoring/CODEMAP.md)、[实际API](../../contracts/MONITORING_IMPLEMENTED_API.md)、[固定S0](../monitoring/batches/B005.1/S0_CONTRACT.md)。现场结果为有效子集；质量范围与配置身份必须随诊断保留。
- P1：监控交接中的计算语义、结果/中间信息约定和样例；本任务 [DESIGN](DESIGN.md)、[CODEMAP](CODEMAP.md)；[公共契约索引](../../contracts/README.md)；[目标输入](../../requirements/V1_SCOPE.md) 中理想命中率异常部分。
- P2：PrefixLens 与本任务相关的诊断源码、华为版本核对结论和案例，复用监控任务已获得的版本证据。具体来源状态见 [upstream](../../../upstream/README.md)。
- P3：其他任务的算法实现、历史方案和无关研究按需。

## 协作与维护范围

监控设计完成即可开展本任务调研与设计；在结果未实现时明确使用契约样例，实际联调另有证据。

本任务维护诊断逻辑、结果/证据契约和本任务文档。与长度诊断协商共用的分析输出和探测器边界，不提前实现自进化 Agent。设计与代码完成状态记录在本入口，作为后续 Agent 会话的输入之一。

需要监控提供更多信息时，提出具体用例、来源与成本，交给监控维护方共同调整契约，不私自复制计算管线。


## 前端协作

2026-10-30用户最新分工：后续界面由新的[异常分析前端session](../../../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md)承接；原[前端session](../viewer/ENTRY.md)提供[HTML视觉入口](../viewer/prototypes/tokenscope-v2-demo-ui01.html)。对应后端设计基本固定、接口冻结后按工作流推进。本session负责分析实现与结果/证据契约，与前端确认真实可提供字段；HTML仅为展示参考，不代表契约冻结或算法已实现。

# 单条请求长度异常分析任务入口

状态：2026-10-30用户最新分工：先由[异常分析后端母会话](../analysis/ENTRY.md)完成调研/产品设计，之后再按用户启动fork本线详细设计/开发。本线尚未创建/登记，不按旧安排直接启动。

## 当前目标输入与责任

模板后长度分布明显变化时，分析模板控制文本、完整工具 Schema、历史消息、工具返回和重复序列化的组成与贡献。

复用监控任务的编码和计量基础，并协商所需来源映射和结果信息。具体归因方法由本任务设计，不独立维护另一套 Chat Template/Tokenizer。session、turn、Loop 和 subagent 使用方式分析继续暂缓。

## 阅读范围

- P0：项目 AGENTS、memory/CURRENT、本入口。
- P1首读：[监控现场验收及分析交接](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)、[监控代码地图](../monitoring/CODEMAP.md)、[实际API](../../contracts/MONITORING_IMPLEMENTED_API.md)、[固定S0](../monitoring/batches/B005.1/S0_CONTRACT.md)。现场结果为有效子集；质量范围与配置身份必须随诊断保留。
- P1：监控交接中的输入、编码、长度信息及可得来源映射；本任务 [DESIGN](DESIGN.md)、[CODEMAP](CODEMAP.md)；[公共契约索引](../../contracts/README.md)；[目标输入](../../requirements/V1_SCOPE.md) 中单条请求长度异常部分。
- P2：与模板、字段边界、上下文组成有关的固定源码和研究证据；按实际问题选取，不扫描全部模型实现。
- P3：前缀诊断内部实现及历史研究按需。两个诊断任务默认通过公共结果和探测器约定协作。

## 协作与维护范围

监控设计完成即可开始调研与设计，样例验证和实际联调分别记录。维护本任务归因实现、结果/证据契约及文档，具体源码位置在 CODEMAP 登记。

与前缀诊断协商共用分析输出和探测器边界；本任务设计和代码完成后，将可接手材料交给后续 Agent 会话。缺少必要输入时向监控任务提出扩展需求，不能通过独立编码生成不一致的计量。


## 前端协作

2026-10-30用户最新分工：后续界面由新的[异常分析前端session](../../../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md)承接；原[前端session](../viewer/ENTRY.md)提供[HTML视觉入口](../viewer/prototypes/tokenscope-v2-demo-ui01.html)。对应后端设计基本固定、接口冻结后按工作流推进。本session负责分析实现与结果/证据契约，与前端确认真实可提供字段；HTML仅为展示参考，不代表契约冻结或算法已实现。

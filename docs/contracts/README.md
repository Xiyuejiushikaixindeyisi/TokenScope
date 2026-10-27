# 公共契约索引

监控 v1.0 已于2026-10-27获批；B001–B005本机实现/合成验收完成，实际接口见 [实现说明](MONITORING_IMPLEMENTED_API.md)和[OpenAPI](schemas/monitoring-current.openapi.json)。[实际执行的合成样例](examples/monitoring-v1-executed-synthetic.json)来自真实三模型编码，不是生产数据；B001接口快照保留追溯。V1完整服务仍未完成；[B005.1展示服务契约](MONITORING_VIEW_V1_DRAFT.md)已完成S0 1.0.0固定，新增服务尚未实现，前端实际联合验收是发布前硬门槛；B006历史准备归档/pending。

当前已批准：[Token 监控首版契约 v1.0](MONITORING_V1.md)及[首版示意样例](examples/monitoring-v1-illustrative.json)。2026-10-26 收敛为参数化离散事件、hybrid 仅留接口、UTC/重复行和独立阈值表等首版范围；新增默认 5K、≥200K 尾桶、众数与图外分位数；样例不是实测或正式 Schema。v1.0-rc2、v1.0-rc1 及 v0.1/v0.2 文档与样例保留追溯，不作为首版开发入口。新增首版运行/交付约定，指标语义相对 rc2 不变；[完整版本关系](../tasks/monitoring/VERSIONS.md)。维护任务为 Token 监控，消费者见下表。

## 设计归属

| 约定类别 | 首要维护任务 | 消费任务 |
| --- | --- | --- |
| 数据导入、模型身份、统一编码与计量、理想命中计算及结果 | Token 监控 | 两类分析、展示、后续 Agent |
| 前缀原因分析结果及证据 | 理想命中率低原因分析 | 展示、监控触发与结果关联、后续 Agent |
| 长度异常分析结果及证据 | 单条请求长度异常分析 | 展示、监控触发与结果关联、后续 Agent |
| 展示读取已有成果的交互方式 | 展示与对应结果生产任务共同讨论 | 展示 |
| 探测器及归因不足相关共用约定 | 两类分析任务先协商共同部分，后续 Agent 消费和完善 | 两类分析、后续 Agent |

这些是交接内容的类别，不是已经确定的字段或接口格式。各任务设计时说明来源、缺失值含义、版本、消费者及兼容方式。理想命中率只有监控维护的一套计算口径；诊断可以直接消费其信息，也可以调用同一实现。

Session 1 完成设计时，按实际形成的约定在这里登记文档与样例链接，并在设计交接中记录版本。消费者只读自身依赖部分。不得仅因创建索引就把所有类别变成首期必须实现的完整平台接口。


## 前端前置：S0 1.0.0固定

[交接/边界](../tasks/monitoring/batches/B005.1/S0_CONTRACT.md) / [完整字段](MONITORING_VIEW_V1_FIELDS.md) / [Schema](schemas/monitoring-view-v1.schema.json) / [设计OpenAPI](schemas/monitoring-view-v1.design.openapi.json) / [完整成功错误样例](examples/monitoring-view-s0/README.md) / [摘要](../tasks/monitoring/batches/B005.1/S0_MANIFEST.json)。原DRAFT文件名保留历史，内容按固定版本消费；设计接口不代表当前运行能力。

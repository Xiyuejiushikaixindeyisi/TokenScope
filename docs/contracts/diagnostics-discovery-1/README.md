# diagnostics-discovery-1

FE-N1 的独立兼容增补。analysis-common-1.0 和 diagnostics-http-1 的模型及冻结摘要不变；原客户端仍可使用旧接口。新前端使用本协议发现成果与监听终态，不轮询任务状态。独立发现入口 GET `/diagnostics/discovery/capabilities`；旧 `/diagnostics/capabilities` 不被静默改写。

`wire.json` 给出 Catalog、Terminal、terminal SSE data、reset SSE data、Error 的JSON Schema。来自 discovery_contracts.py，导出命令 `.venv/bin/python scripts/export_diagnostic_discovery_schema.py`。`manifest.json` 记录实际本地源码与Schema身份，不是部署证明。请求均为GET，路径/查询参数见[前端增补交接](../../tasks/prefix-analysis/NOTIFICATION_HANDOFF.md)。错误仍为 `{error:{code,message}}`。

数字计数/sequence及嵌套scope整数均十进制字符串；时间是UTC RFC3339毫秒字符串或null；游标是不透明字符串，不能转整数或跨实例复用。新协议不修改既有报告原文、TaskReceipt、EvaluationResult或Token候选。

[examples.json](examples.json) 为完整合成响应样例（空目录、完整/部分诊断、评估及terminal事件），实际任务ID/时间仅是构造器运行时生成的示例，不代表现场分析。

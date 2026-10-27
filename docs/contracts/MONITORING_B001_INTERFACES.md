# B001 实施接口（0.1.0.dev1）

依据已批准 [MONITORING_V1](MONITORING_V1.md)，本文件补充实际序列化，不改变指标/仿真语义。[OpenAPI](schemas/monitoring-b001.openapi.json)从代码导出。

- GET /models；GET/PUT /models/{model_id}/settings。PUT 为 `{"expected_revision":1,"changes":{"block_size":256}}`，revision 不符 409。显式 null 为非法设置，省略表示不变。返回 settings/capability。增强 hybrid 可保存为选项，但能力明确 not_supported，不能降级执行。
- POST /analysis-runs 输入 `{"file_ref":"glm.csv","model_id":"GLM-5.2"}`；完整流水线完成前固定返回 503 PIPELINE_NOT_READY（非法输入/不支持模式仍先返回明确错误），不入队伪任务。内部队列/冻结原语已实现并测试。
- GET /analysis-runs/{run_id} 返回既有状态，不触发分析。run_id 未知 404。
- GET /healthz=200 表示存活；GET /readyz=503 说明编码/流水线尚未就绪；GET /version 给实际开发版本和无 release/asset 身份，不能当交付验收。
- CLI 与 HTTP 共 MonitoringService。validate-input 仅校验 CSV，token_metrics=null，输出独立 validation_id 和质量/SHA；不是 completed 分析。
- UTC 时间接受 ISO 日期时间、可选 1–9 位小数；无后缀按 UTC，带 offset 归一 UTC；不猜数字时间戳单位。SQLite 纳秒表示范围之外为无效行。重复 ID 每行保留，后续有效重复计 warning；坏行跳过，错误 CSV 引号/编码等不可恢复异常使整个输入失败。
- 词法严格的 JSON、纯文本消息/工具校验；重复对象键、非有限浮点、孤立 surrogate 无效。输出仅错误码/字段定位，不回显原文。API 错误统一 `{"error":{"code":"...","message":"..."}}`。
- 目前结果/直方图/阈值/signals 路由尚未实现；人工设计样例不是接口运行结果。随后 B003/B004 扩展 schema，并和前端消费者核对，不自行改动前端设计。

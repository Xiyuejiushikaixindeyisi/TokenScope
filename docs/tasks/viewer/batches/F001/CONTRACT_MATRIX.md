# F001 契约对照

输入S0 1.0.0 / view_schema=1；身份见apps/viewer/src/api/contract-lock.json。运行后端身份不由本前端宣告。

| 固定输入/要求 | 消费入口 | 验证 |
| --- | --- | --- |
| S0_MANIFEST全部文件SHA | scripts/generate-contract.mjs | generate先验证再生成，不改上游 |
| JSON Schema 67定义 | src/api/generated/types.ts与schema.json | 所有75份S0 JSON样例 |
| 16路径18操作，完整参数 | docs/contracts/schemas/monitoring-view-v1.design.openapi.json（只读固定） | F001根路径/URL编码；具体操作按F002–F005实现 |
| DTO结构、nullable、枚举与Error | api/validate.ts、client.ts | 未知schema、未知字段、错误/整数类型、bin_width/limit |
| cursor原串+格式+同实例 | validate.ts | 正常/大序号/负数/前导零/换行/跨实例 |
| scope隔离 | domain/identity.ts、validateDto expected | 实例/appid拒绝、键无歧义 |
| 无损Token与时间 | domain/integer.ts、time.ts | 2^53与64位、负delta、null、纳秒、北京时间 |
| R1六态回执/失败/404 | S0全部样例，client错误测试 | 类型确认；实际恢复状态机F004 |
| R2结束与字节摘要 | normal/empty NDJSON+原CSV夹具索引 | NDJSON摘要/行数/类型；CSV完整流式解析与保存F005 |

运行时校验器遵循原Schema；行为契约补充语义不改变DTO。实例请求头使用X-TokenScope-Instance-Id。未实现功能不标为完成。

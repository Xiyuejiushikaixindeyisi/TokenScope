# MA后端已实现接口 1.0.0

2026-10-30；本机后端已验收，未部署/打包。独立契约：[CONTRACT](../../../contracts/ma-monitoring-v2/CONTRACT.md)、[Schema](../../../contracts/ma-monitoring-v2/schema.json)、[实际路由OpenAPI](../../../contracts/ma-monitoring-v2/design.openapi.json)。旧S0及V1结果协议不变。

| 方法/路径 | 用途 |
| --- | --- |
| POST /monitoring/ma/runs | 绑定pre/now文件、规格、编码模型、连续UTC窗口与submission_key，返回202 |
| GET /monitoring/ma/runs/{ma_run_id} | 回执、状态、error_code及安全定位error_detail |
| GET /monitoring/ma/submissions/{submission_key} | 响应丢失后恢复回执 |
| GET /monitoring/ma/catalog | 规格筛选、offset/limit/revision一致分页；仅已完成运行 |
| GET /monitoring/ma/runs/{ma_run_id}/instances/{instance_uuid} | 预生成的同集合对照、独立指标、12桶、两图、质量、运行条件 |
| GET /monitoring/ma/runs/{ma_run_id}/quality | role/源序号/字段/原因分页，不发送正文 |

CLI沿用全局input-root/state-root/asset-root/cpu-budget参数，新增ma-submit --json、ma-run、ma-snapshot、ma-catalog；work-once同时调度V1和MA。HTTP后台也使用同一Dispatcher；用户索引处理器可注册，尚未进行真实三线联合验证。

用户需先将两CSV放到受控input-root，再提交相对file_ref，不提供上传或自动采集。source_timezone固定UTC；两个窗口均一小时，左闭右开。原SQL BETWEEN的右端重复行必须在导出时处理，工具不静默迁移记录或修改JSON。

查询只读已发布结果。未完成409，未知run/instance404，提交键异体409，分页revision过期409；服务身份沿用X-TokenScope-Instance-Id。样本计数/Token/目录revision为十进制字符串；速率浮点，缺失/null与零不同。直方图三箱宽全部预计算，200K为开放尾桶。

首版不提供MA SSE、原文导出、最优路由推荐或自动告警。正式前端应遵循已有DEMO并消费本协议；前端联调和现场性能单独验收，不把本机合成结果当生产容量保证。

[完整前端合成样例](../../../contracts/ma-monitoring-v2/frontend.examples.json)：16项，含五类实例快照/质量/目录/回执/错误，已通过当前严格DTO验证。

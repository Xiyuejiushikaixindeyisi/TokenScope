# S0 实际检查记录

2026-10-27；工具环境、UTC执行时间、每个检查与结果见[contract-check.json](../../../../../../artifacts/validation/monitoring/B005.1/S0/contract-check.json)。仅协议和夹具验证，不是API、应用E2E、浏览器或部署测试。

| 实际命令 | 退出码/结果 |
| --- | --- |
| python3 scripts/contracts/build_monitoring_view_v1.py（最初） | 1，SSE字典语法错误；见ISSUES S0-01 |
| 系统Python导入Draft202012Validator（探测） | 1，旧jsonschema不支持；见S0-02 |
| .venv/bin/ruff check scripts/contracts（最初） | 1，E501/E731，后加时间字段触发I001/UP017也修正；见S0-05 |
| python3 scripts/contracts/build_monitoring_view_v1.py（修正后） | 0；67定义、75 JSON完整用例、16路径18操作 |
| 项目专用uv工具环境运行validate_monitoring_view_v1.py | 0；94项全部通过 |
| .venv/bin/ruff check scripts/contracts；ruff format --check scripts/contracts | 0；工具静态/格式检查通过 |

可重跑命令见[样例README](../../../../../contracts/examples/monitoring-view-s0/README.md)。关键检查：75完整样例；Schema元模式/内部引用/OpenAPI参数默认值；五个快照各1029桶、P=H+C、率及质量守恒；11个非法字段/类型/边界反例；SSE原字节帧；正常/空NDJSON及CSV、4个损坏导出变体；NDJSON单记录恰好1048576与1048577字节。

正常CSV实际4条请求、7个LF（包含引用字段内换行），防止物理行数充当请求数。NDJSON request行SHA见fixture清单，按原字节+LF计算；没有执行真实浏览器大流或文件sink验证。文档链接、归档与源基线检查另见[review-check](../../../../../../artifacts/reviews/monitoring-b005-1-v0.2/review-check.json)。

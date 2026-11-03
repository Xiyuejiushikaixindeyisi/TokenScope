# HV2-R1-USER实际测试

运行环境：WSL Ubuntu-22.04，项目.venv Python，独立pytest tmp state。全程无监听服务；TestClient/ASGI仅进程内。下面命令均以项目根目录为cwd。

## 命令与结果

1. 初始新增目录/默认集成18 passed；追加真实GLM过滤审计后19 passed。
2. 候选导出与封存损坏测试：2项首轮1失败/1通过；失败是JSON数组用Python tuple严格验证，改用model_validate_json后契约单项通过。没有放宽生产校验。
3. `.venv/bin/pytest -q tests/unit/monitoring tests/integration/monitoring --ignore=tests/integration/monitoring/test_events.py --junitxml=artifacts/validation/user-monitoring/HV2-R1-USER/regression.xml`：270 passed、1 failed，141.77秒。唯一失败为旧测试固定接口数9；现在新增5个接口为14。修正断言并新增旧9操作requestBody/responses与冻结2.0.0逐项一致检查，没有删除验证。
4. `.venv/bin/pytest -q tests/integration/monitoring/test_user_robustness.py tests/integration/monitoring/test_user_discovery_defaults.py tests/integration/monitoring/test_user_trace_filter_audit.py --junitxml=artifacts/validation/user-monitoring/HV2-R1-USER/final-targeted.xml`：27 passed，17.49秒。
5. `.venv/bin/pytest -q tests/unit/ingestion tests/unit/encoding tests/integration/encoding --junitxml=artifacts/validation/user-monitoring/HV2-R1-USER/ingestion-encoding.xml`：62 passed，46.09秒。
6. `.venv/bin/mypy src/tokenscope/user_monitoring src/tokenscope/api/user.py`：12 source files通过。
7. `.venv/bin/ruff check src/tokenscope/user_monitoring src/tokenscope/api/user.py tests/integration/monitoring/test_user_discovery_defaults.py tests/integration/monitoring/test_user_trace_filter_audit.py tests/integration/monitoring/test_user_robustness.py`：通过。
8. 最终完整不监听回归见RESULT及final-regression.xml。XML留于artifacts，本文件保留结果，不将日志当生产数据或包体入Git。

依赖有既存Starlette/httpx弃用warning，未为此修改依赖。初次diff检查本线记忆混合CRLF出现trailing whitespace，统一该本线文件LF后再核对；不处理其他session文件格式。

## 覆盖

- 3模型共appid、单模型、多个历史、ready/empty/未发布隔离、首屏冷state、分页大于一页、指纹失效/固定历史、重启、实例错误、GET全state内容/mtime不变。
- 3模型默认τ、显式K覆盖/恢复/τ不缩放、配置CAS及幂等/并发8请求同结果、null停用重启不被种子覆盖、跨模型422、错误index revision、默认历史不存在。
- W=0、T=W le/lt、T<W、小数7.7−5=2.7等号、缺W/T的missing/null/blank、P90=0/空运行、旧2.0.0结果原样读取。
- 14操作OpenAPI/Schema生成与比较，8个合成正反例，SHA复核；源summary篡改409且不修复/写入。
- 严格JSON错误/重复hash短hash/缺model/晚时刻，3个有效保留、5个明确拒绝；与公共SourceResolver同Trace结果一致，CSV不改。
- 既有监控/S0范围和CSV/编码回归；不涉及其他会话修改的业务验收。

## 排除
tests/integration/monitoring/test_events.py启动uvicorn/socket，按任务约束未运行。真实监听/浏览器完整E2E、华为现场和真实TTFT校准留总设计师统一验收；不能用合成fixture冒称完成。

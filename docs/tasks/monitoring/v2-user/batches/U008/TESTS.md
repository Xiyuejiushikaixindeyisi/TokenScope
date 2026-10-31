# U008 TESTS

2026-10-31。
- 全量：.venv/bin/pytest -q --junitxml=artifacts/validation/user-monitoring/U008/pytest.xml：380 passed，284.59s。
- 最终增量：test_user_minimal_contract / test_user_minimal_estimator / test_user_minimal_ttft / test_user_estimator / test_user_ranking：126 passed，12.69s。覆盖全量启动后补充的254位派生chunk边界及新限制文案；仅随后换行格式化不改字符串。
- mypy src/tokenscope：50源文件通过。
- ruff check src tests scripts/validation/check_user_contract.py：初次发现一行101字符，拆为相邻字符串后通过；static-after-format-fix.log保留最终结果，不删除失败日志。
- 契约：31正反例、17 schemas、9操作通过；连续生成摘要一致；6份三模型新旧ASGI响应验证；实际OpenAPI双类型及2.0.0操作标记核对。
- 边界/兼容：le/lt等号、尾chunk、无预算/0%/100%、缺参/明确W=0、可选范围、未知tag/混入O、冻结1.0.1原payload读回、幂等竞争、重启及无索引仍读历史。
- 共享审计：相对U006基线，既有src/tests/apps/docs/contracts范围仅3个用户后端源文件变化；原测试未提交改动、旧1.0.1冻结文件、前端及V1/MA源文件保持。新增测试与2.0.0契约另计。
- 唯一测试警告：现有Starlette/httpx弃用提示；未改变依赖。

详细命令/输出在artifacts/validation/user-monitoring/U008/{checks.json,final_checks.json,pytest.log,pytest.xml,final_targeted.log,static-after-format-fix.log,audit.json}。checks/final_checks中的ruff失败已由最终日志闭环，不把失败记录删除或伪装为首次通过。
本轮真实模型编码、ASGI HTTP和本地持久重启；不是浏览器、远端服务或生产性能校准。

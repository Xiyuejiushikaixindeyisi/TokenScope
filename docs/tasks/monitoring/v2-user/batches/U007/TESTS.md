# U007 TESTS

pytest -q tests/unit/monitoring/test_user_minimal_estimator.py tests/integration/monitoring/test_user_minimal_ttft.py tests/unit/monitoring/test_user_ranking.py tests/unit/monitoring/test_user_estimator.py：83 passed，14.31s。
新增preupgrade冻结1.0.1快照直接入库回放：1 passed，0.39s。
mypy src/tokenscope：50源文件通过；ruff src和本次测试/生成器通过。
三模型真实编码CSV→索引→ASGI HTTP情景/估算→重新创建app→历史读取通过；样例artifacts/validation/user-monitoring/U007/{model}.json。ASGI TestClient非远端生产或真实网络部署。

# U006 TESTS

2026-10-31：.venv/bin/pytest -q tests/unit/monitoring/test_user_minimal_contract.py tests/unit/monitoring/test_user_estimator.py：79 passed，2.60s。旧缺参测试原有改动保留。
.venv/bin/python scripts/validation/check_user_contract.py：31样例、17 schemas、9操作通过，输出独立2.0.0目录。
ruff check契约/生成器/新增测试通过；mypy contracts.py通过。Starlette/httpx弃用警告不影响本批结果。

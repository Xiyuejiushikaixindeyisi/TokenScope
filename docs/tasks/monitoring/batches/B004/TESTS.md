# B004 测试记录

`.venv/bin/python scripts/validation/check_batch.py B004`：131 passed，pytest/ruff/format/mypy退出码均0；报告 `artifacts/validation/monitoring/B004/20261027T032958Z-report.json`。真实三模型资产固定，但请求为合成。三模型每个都覆盖完整流水线、时间稳定排序、H/C守恒、分页/查询不修改产物、按需IDs复核；另有无效/未决/无有效行、规则版本/幂等、无缓存和封存后故障恢复。

首轮schema无法加载，原因和修复见ISSUES；修复后130项通过，补极端整数查询防溢出测试与耗时scope后131项通过。保留所有日志。

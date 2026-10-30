# U005 测试记录

环境：项目WSL .venv，CPU预算8，批256/16MiB；三模型本地真实Tokenizer/Template，非mock编码；全部输入为项目内合成CSV。机器/文件摘要见VALIDATION_MANIFEST.json。

| 验证 | 命令/证据 | 结果 |
| --- | --- | --- |
| 全量回归 | .venv/bin/python -m pytest -q --junitxml=artifacts/validation/user-monitoring/U005/full-final.xml | 289 passed，222.81s，0 failed/skip；1条第三方Starlette弃用提示 |
| 最终恢复修复定点 | pytest tests/integration/monitoring/test_user_robustness.py tests/integration/monitoring/test_user_runs.py | 15 passed，24.42s；recovery-final.xml，包含基础回执预留绑定竞争 |
| 健壮性与排行 | robustness.xml | 27 passed；大数/大字段、源/控制/索引缺失、权限、模式、GET只读等 |
| 真HTTP+CLI | scripts/validation/run_user_monitoring_e2e.py | http-5e7619f2/report.json：3模型全过程、MA真联合、重启读取、带待处理任务跨进程锁、进程os._exit在rename/发布前中断后恢复均通过 |
| 精确公式 | test_user_estimator.py；U004/estimator-performance.json | 1000独立Decimal穷举边界算例；≤2s预算通过 |
| 资源 | scripts/validation/user_resource_probe.py；resources/projection.json、query.json | 100k事实/10k组，1.396s；RSS增量9048064B≤256MiB；索引22855680B≤3×6934528B+32MiB；20次查询最慢0.255s≤2s |
| 静态/类型 | ruff check本线源码测试脚本；mypy src/tokenscope | 通过，50源文件类型通过 |
| 契约 | check_user_contract.py、validate_ma_contract.py | 用户26例/15 schema/9操作；MA2正例/4反例均通过；旧S0真实响应/Schema回归在全量测试内 |
| 差异与链接 | Git diff --check；本线Markdown/Schema/证据清单 | 见VALIDATION_MANIFEST.json |

第一次完整回归283 passed（246.64s）保存在full-initial.xml；增加6个健壮性用例后完整289通过。最后的“基础任务预留绑定”增量修复由15项恢复/三模型测试复测，不将旧快照的全量结果冒称覆盖随后改动。

资源样本为合成数据，连接冷/重复读取均每次新建SQLite连接；未驱逐操作系统页缓存，不报告物理冷盘性能。固定预算未事后放宽。没有华为现场吞吐或校准准确性测试。

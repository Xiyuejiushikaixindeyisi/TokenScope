# U002 实测

2026-10-30，WSL本地.venv，CPU8。pytest test_user_statistics/test_user_projection/test_user_runs：22 passed，16.01s；XML artifacts/validation/user-monitoring/U002/tests.xml。

覆盖三模型真实facts、appid隔离/duplicate、并发幂等、基础提交后中断、rename前存储拒绝、发布前中断恢复、源摘要损坏、全无效empty/缺facts、索引损坏、worker锁、历史绑定、混服务拒绝、跨64位精确累加及开放箱边界。原seal不变，重建摘要一致。

资源：scripts/validation/user_resource_probe.py，100000 facts/10000 appid，1.202s；RSS增量9175040 B≤256MiB；索引22855680 B≤3×6934528+32MiB。固定预算未修改。报告artifacts/validation/user-monitoring/resources/projection.json。mypy6源文件、ruff通过。合成资源不代表现场流量性能。

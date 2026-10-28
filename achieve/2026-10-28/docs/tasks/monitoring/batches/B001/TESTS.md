# B001 实际测试记录

日期：2026-10-27。本机 WSL Ubuntu-22.04；Python 3.11.16。身份见 [源码清单](../../../../../../../artifacts/validation/monitoring/B001/source-manifest.json)、[运行报告](../../../../../../../artifacts/validation/monitoring/B001/20261027T021711Z-report.json)，依赖精确锁定于 uv.lock。测试全部为人工合成输入，不含用户生产 CSV。

## 命令与结果

复现：项目根目录执行 `.venv/bin/python scripts/validation/check_b001.py`。该脚本依次运行 pytest、ruff check、ruff format --check、mypy，并启动/关闭真实 uvicorn 进程，验证 health/models/ready，再导出 OpenAPI。

| 检查 | 退出码 | 证据 |
| --- | --- | --- |
| pytest | `0` | [日志](../../../../../../../artifacts/validation/monitoring/B001/20261027T021711Z-pytest.log) |
| ruff | `0` | [日志](../../../../../../../artifacts/validation/monitoring/B001/20261027T021711Z-ruff.log) |
| format | `0` | [日志](../../../../../../../artifacts/validation/monitoring/B001/20261027T021711Z-format.log) |
| mypy | `0` | [日志](../../../../../../../artifacts/validation/monitoring/B001/20261027T021711Z-mypy.log) |
| real_process_http | `0` | [日志](../../../../../../../artifacts/validation/monitoring/B001/20261027T021711Z-http.log) |

最终 **66 passed，1 条上游 TestClient 弃用 warning**；mypy 检查 12 个源文件；格式检查 19 个文件。独立 HTTP 验证三个默认块长、健康 200 和未就绪 503，进程已结束。

覆盖：UTF-8/BOM、多行/引号/长字段/批预算；原 JSON 完整保留；纯文本工具往返；非法 JSON/非有限数/字段/时间/模型冲突；UTC 纳秒、offset 与稳定排序；重复 ID 保留并计数；坏行/坏文件/SQLite 故障区分；路径穿越/符号链接替换/FIFO/目标不可覆盖；配置 CAS 并发、运行开始冻结/历史不变/单运行竞争；hybrid 不支持明确失败；CLI/API 共服务、错误不回显正文、未实现分析不产生伪指标。

首轮：`pytest -q` 65 passed；`ruff check src tests` exit 1（33 项）；`mypy` exit 0。原日志：[pytest](../../../../../../../artifacts/validation/monitoring/B001/pytest-initial.log)、[ruff](../../../../../../../artifacts/validation/monitoring/B001/ruff-initial.log)、[mypy](../../../../../../../artifacts/validation/monitoring/B001/mypy-initial.log)。修复及新增回归见 ISSUES。期间格式工具的修复迭代输出属编辑检查，最终上述 gate 已统一重跑。

不覆盖：真实 tokenizer IDs、DES/统计/阈值、前端联调、三模型真实 CSV、性能与华为机运行。这些归后续 batch，不据本报告宣称通过。

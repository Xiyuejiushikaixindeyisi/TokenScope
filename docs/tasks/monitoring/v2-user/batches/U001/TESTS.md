# U001 测试记录
2026-10-30，WSL项目.venv，实际执行。
- 首次检查：domain重复逗号导致SyntaxError，未得到业务通过；见I01。
- 修复后pytest tests/unit/monitoring/test_v2_compat.py tests/unit/monitoring/test_storage.py -q：28 passed，0.67s。
- ruff check：新增契约、csv_reader/domain/storage及受影响测试通过。
- mypy src/tokenscope：35文件通过。
- 全量pytest tests/unit tests/integration -q正在执行，未出最终结果前不closed。
- 网络/Compose/现场访问：未执行；参数交接见ACCESS_HANDOFF.md。

最终：编码旧模式夹具复测19 passed(49.18s)，新增现场模式等价1 passed(2.13s)。
全量初轮175passed/4failed/4error为profile身份夹具问题；第二轮161passed/32failed/12error为新增测试CPU预算污染，均保留记录。
最终pytest全量205 passed，1 warning，158.98s，退出0。机器报告artifacts/validation/user-monitoring/U000/u001-final.xml。lint和diff检查通过；不将通过测试数量等同现场性能。

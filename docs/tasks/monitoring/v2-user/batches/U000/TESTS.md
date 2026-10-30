# U000 测试记录
日期2026-10-30。本轮真实WSL .venv执行。
- U000-T04：.venv/bin/python -m pytest tests/unit tests/integration -q：169 passed，155.33s，退出0；1条Starlette httpx弃用提示。执行会话44173。
- 初步契约：.venv/bin/python scripts/validation/check_user_contract.py：18样例、15 schema、9操作通过；仅当前已有覆盖，不代表U000-T01/T02全部通过。
- .venv/bin/python -m mypy src/tokenscope/user_monitoring：2文件通过。
- ruff初次发现3条行长，format已修复，最终lint尚待复测。
- U000-T03：已读取process_next/flock、facts和submit共享服务入口；具体持久恢复规则见契约README。未装配服务，无业务运行能力声明。

最终复测：26例、15 schemas、9操作通过；mypy 2文件通过；ruff check --fix仅修import顺序后0剩余，ruff format --check 3文件通过。U000-T01/T02结构和样例通过；T03恢复/共享职责按README固定，运行态验证属于后批。

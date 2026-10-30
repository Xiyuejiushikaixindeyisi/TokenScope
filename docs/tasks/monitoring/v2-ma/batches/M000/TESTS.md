# M000 测试要求与记录

状态：**completed（最终记录见文末）**，下表为计划，非测试结果。见[PLAN](PLAN.md)。

| 用例 | 检查内容 | 结果 |
| --- | --- | --- |
| M000-T01 | 协议所有操作/错误/跨字段约束、成功/空集/仅pre/部分可用/冲突样例校验和负例拒绝。 | 未执行 |
| M000-T02 | 双1h窗口、12桶、精确整数、空值/覆盖、service与集群UUID区分。 | 未执行 |
| M000-T03 | 旧S0摘要不变，公共函数签名/用户修复接入能力和未接入清单完整。 | 未执行 |

代码批运行当前模块与受影响pytest、ruff check、ruff format --check、mypy；M005完整执行，M000验证契约及验证器正负例。新增测试按PLAN实现后才可运行，不引用不存在脚本冒充实际命令。

每次实际记录：attempt、候选commit/文件SHA、Python3.11/依赖、夹具SHA和独立预期、完整命令/退出码、pass/fail/skip、日志/结果及SHA、关联问题和修复后复测。证据路径：artifacts/validation/monitoring/v2-ma/M000/<attempt>/。

| attempt | 源码/输入/环境身份 | 实际命令/退出码 | 结果/证据 | 问题/复测 |
| --- | --- | --- | --- | --- |
| 未执行 | 未取得 | 未运行 | 无业务证据 | 无已验证修复 |


## attempt 01：契约原语子集
环境WSL Ubuntu-22.04，项目.venv Python3.11.16。pytest -q tests/unit/ma：3 passed；ruff check src/tokenscope/monitoring/ma tests/unit/ma：通过；mypy src/tokenscope/monitoring/ma：2 source files通过。ruff format已格式化新增文件。仅覆盖连续1h与同文件拒绝、A/P/R/E/Q交集边界、超过JS安全整数的守恒和零分母；M000-T01/T02/T03整体仍未完成，不能closed。

## 2026-10-30 M000闭环记录
M000 closed：独立contracts.py、CONTRACT.md、schema/design.openapi/examples/manifest及验证器已生成。Python3.11.16；pytest tests/unit/ma：10 passed；协议验证器2正例4负例；ruff check/format与mypy通过。BASELINE.json记录公共源码、用户契约、依赖及旧S0摘要，旧S0未修改。窗口/交集/守恒/12桶/仅pre/时序不可用约束验证通过。设计OpenAPI仅操作/响应骨架，请求及查询完整语义在CONTRACT明确，M004必须以真实路由导出补全；不声称运行接口已存在。公共解析用户线维护，MA不覆盖；真实用户索引联合后续核验。允许进入M001。

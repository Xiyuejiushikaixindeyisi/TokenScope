# M002 测试要求与记录

状态：**completed（最终记录见文末）**，下表为计划，非测试结果。见[PLAN](PLAN.md)。

| 用例 | 检查内容 | 结果 |
| --- | --- | --- |
| M002-T01 | 同UUID跨appid命中、跨UUID不命中、V1仍隔离、原appid不变。 | 未执行 |
| M002-T02 | pre只预热、now后续复用、重跑冷启动、空pre/坏pre/仅pre/同刻和时间交叉。 | 未执行 |
| M002-T03 | 128/1536/32、MTP、短请求/完整重复、禁缓存、hybrid拒绝，独立参考逐请求差分。 | 未执行 |
| M002-T04 | 三模型真实资产、显式/默认模式、缺资产/未决模式，合法批大小变化结果一致。 | 未执行 |

代码批运行当前模块与受影响pytest、ruff check、ruff format --check、mypy；M005完整执行，M000验证契约及验证器正负例。新增测试按PLAN实现后才可运行，不引用不存在脚本冒充实际命令。

每次实际记录：attempt、候选commit/文件SHA、Python3.11/依赖、夹具SHA和独立预期、完整命令/退出码、pass/fail/skip、日志/结果及SHA、关联问题和修复后复测。证据路径：artifacts/validation/monitoring/v2-ma/M002/<attempt>/。

| attempt | 源码/输入/环境身份 | 实际命令/退出码 | 结果/证据 | 问题/复测 |
| --- | --- | --- | --- | --- |
| 未执行 | 未取得 | 未运行 | 无业务证据 | 无已验证修复 |


## 实际闭环 2026-10-30
M002 closed：ma/replay.py复用公共批编码/分片/完整块账本；三模型真实资产验证跨租户共享、UUID隔离、预热、时序冲突保留真实。pytest本线及内核/分片/模型回归67 passed in64.67s，证据artifacts/validation/monitoring/v2-ma/M002/attempt-02/regression.txt；ruff/mypy通过。M002-I01预算冲突已修复并完整复测，attempt-01失败日志保留。公共DD/MM解析已出现，仍由用户线维护，MA消费。允许进入M003。

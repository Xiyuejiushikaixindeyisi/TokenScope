# M001 测试要求与记录

状态：**completed（最终记录见文末）**，下表为计划，非测试结果。见[PLAN](PLAN.md)。

| 用例 | 检查内容 | 结果 |
| --- | --- | --- |
| M001-T01 | 两源序号碰撞、重复hash、BOM/多行/引号、原文SHA保真。 | 未执行 |
| M001-T02 | 端点、跨日/亚秒/offset/UTC默认、非法日期、DD/MM能力标识、窗外/规格冲突。 | 未执行 |
| M001-T03 | 坏JSON真实可用、缺cached可编码、completion不污染输入、基础不可归属/负数/越界。 | 未执行 |
| M001-T04 | 路径/符号链接越界、缺表头/破损CSV、复制时变化、权限/磁盘错误。 | 未执行 |

代码批运行当前模块与受影响pytest、ruff check、ruff format --check、mypy；M005完整执行，M000验证契约及验证器正负例。新增测试按PLAN实现后才可运行，不引用不存在脚本冒充实际命令。

每次实际记录：attempt、候选commit/文件SHA、Python3.11/依赖、夹具SHA和独立预期、完整命令/退出码、pass/fail/skip、日志/结果及SHA、关联问题和修复后复测。证据路径：artifacts/validation/monitoring/v2-ma/M001/<attempt>/。

| attempt | 源码/输入/环境身份 | 实际命令/退出码 | 结果/证据 | 问题/复测 |
| --- | --- | --- | --- | --- |
| 未执行 | 未取得 | 未运行 | 无业务证据 | 无已验证修复 |


## 实际闭环（2026-10-30）
M001 closed。实现ma/ingest.py、storage.py，独立事实/质量/控制库；原文保留、窗口半开/规格拒绝、Token精确整数、字段独立有效性、幂等绑定及发布单向状态。pytest局部及公共输入回归66 passed（0.55s）；ruff、mypy通过。证据artifacts/validation/monitoring/v2-ma/M001/attempt-01/pytest.txt。发现E501长SQL字符串，拆为相邻常量并复测通过；未修改公共解析/用户代码。InputRoot快照复用既有受控实现，服务装配和故障注入在M004/M005验证。允许进入M002。

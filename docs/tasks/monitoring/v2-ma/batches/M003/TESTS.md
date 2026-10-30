# M003 测试要求与记录

状态：**completed（最终记录见文末）**，下表为计划，非测试结果。见[PLAN](PLAN.md)。

| 用例 | 检查内容 | 结果 |
| --- | --- | --- |
| M003-T01 | 比率加权90%非50%、P_db/P_local不一致、Q筛选不改变缓存历史。 | 未执行 |
| M003-T02 | 12桶/小时守恒、边界/零桶/缺失/部分有效、处理时间跨窗、超64位累计。 | 未执行 |
| M003-T03 | 两图不同N、零/箱边界/200K以上、最近秩/并列众数、零未命中；旧箱与已接入用户开放箱不干扰。 | 未执行 |
| M003-T04 | 空文件/全坏/仅pre、真实可用理想不可用、输入不一致和覆盖状态符合协议。 | 未执行 |

代码批运行当前模块与受影响pytest、ruff check、ruff format --check、mypy；M005完整执行，M000验证契约及验证器正负例。新增测试按PLAN实现后才可运行，不引用不存在脚本冒充实际命令。

每次实际记录：attempt、候选commit/文件SHA、Python3.11/依赖、夹具SHA和独立预期、完整命令/退出码、pass/fail/skip、日志/结果及SHA、关联问题和修复后复测。证据路径：artifacts/validation/monitoring/v2-ma/M003/<attempt>/。

| attempt | 源码/输入/环境身份 | 实际命令/退出码 | 结果/证据 | 问题/复测 |
| --- | --- | --- | --- | --- |
| 未执行 | 未取得 | 未运行 | 无业务证据 | 无已验证修复 |


## 实际闭环 2026-10-30
M003 closed：ma/statistics.py完成精确独立/配对聚合、质量覆盖、12桶/小时、两图三箱宽与预生成投影。16项聚合/契约/公共分布测试通过；ruff/format/mypy通过。证据artifacts/validation/monitoring/v2-ma/M003/attempt-01/regression.txt。问题：mypy不能确认list展开参数数量，改显式下标；一次测试路径误写已改为实际test_statistics_rules.py并通过。允许进入M004。

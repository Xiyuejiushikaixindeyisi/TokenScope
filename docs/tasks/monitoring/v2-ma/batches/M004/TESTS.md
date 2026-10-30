# M004 测试要求与记录

状态：**completed（最终记录见文末）**，下表为计划，非测试结果。见[PLAN](PLAN.md)。

| 用例 | 检查内容 | 结果 |
| --- | --- | --- |
| M004-T01 | 真实HTTP/CLI一致、三ID区分、同键查回/异体冲突/文件移走恢复。 | 未执行 |
| M004-T02 | 封存前后退出、提交失败、坏seal、目录并发、只发布一次、原seal不改。 | 未执行 |
| M004-T03 | 真实API worker+CLI/双进程的V1-MA互斥、两队列能推进、恢复不误杀活动任务；用户索引/回填适配器注册不嵌套，同额度轮转；用户真实未就绪时分开记录夹具验证与真实联合pending。 | 未执行 |
| M004-T04 | GET零编码/回放/写入、旧S0/旧结果/配置回归，错误不回显正文，分页revision一致。 | 未执行 |

代码批运行当前模块与受影响pytest、ruff check、ruff format --check、mypy；M005完整执行，M000验证契约及验证器正负例。新增测试按PLAN实现后才可运行，不引用不存在脚本冒充实际命令。

每次实际记录：attempt、候选commit/文件SHA、Python3.11/依赖、夹具SHA和独立预期、完整命令/退出码、pass/fail/skip、日志/结果及SHA、关联问题和修复后复测。证据路径：artifacts/validation/monitoring/v2-ma/M004/<attempt>/。

| attempt | 源码/输入/环境身份 | 实际命令/退出码 | 结果/证据 | 问题/复测 |
| --- | --- | --- | --- | --- |
| 未执行 | 未取得 | 未运行 | 无业务证据 | 无已验证修复 |


## 实际闭环 2026-10-30
M004 closed。新增MA服务/HTTP/CLI、封存恢复与共享轮转，实际修改app.py/cli.py局部已登记。真实多进程锁和双队列推进、CLI数值往返2项通过；本线+V1监控回归76 passed in121.28s，证据artifacts/validation/monitoring/v2-ma/M004/attempt-01/pytest.txt；追加故障/存储/恢复13 passed in25.14s。ruff/mypy通过。修复：SQL长行；CLI跨进程轮转位置持久化；封存子目录fsync；claim后再次检查hybrid；error_detail保留安全role/行号定位。真实路由OpenAPI已导出并验证，旧S0未改。用户索引处理器仍未实现，注册接口可用但真实三线联合pending。允许进入M005。

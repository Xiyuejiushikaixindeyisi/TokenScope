# M005 测试要求与记录

状态：**completed（最终记录见文末）**，下表为计划，非测试结果。见[PLAN](PLAN.md)。

| 用例 | 检查内容 | 结果 |
| --- | --- | --- |
| M005-T01 | 固定候选E01–09全路径通过，真实三模型编码/服务/恢复/互斥。 | 未执行 |
| M005-T02 | 完整工程检查无未解释的新skip/xfail，关键依赖未就绪不写通过。 | 未执行 |
| M005-T03 | 规模/大单条/多UUID/重复运行资源可复核，批处理和磁盘账本不改变结果。 | 未执行 |
| M005-T04 | 设计符合性、问题闭环、实际入口/协议样例、旧S0摘要与回归、外部pending清晰。 | 未执行 |

代码批运行当前模块与受影响pytest、ruff check、ruff format --check、mypy；M005完整执行，M000验证契约及验证器正负例。新增测试按PLAN实现后才可运行，不引用不存在脚本冒充实际命令。

每次实际记录：attempt、候选commit/文件SHA、Python3.11/依赖、夹具SHA和独立预期、完整命令/退出码、pass/fail/skip、日志/结果及SHA、关联问题和修复后复测。证据路径：artifacts/validation/monitoring/v2-ma/M005/<attempt>/。

| attempt | 源码/输入/环境身份 | 实际命令/退出码 | 结果/证据 | 问题/复测 |
| --- | --- | --- | --- | --- |
| 未执行 | 未取得 | 未运行 | 无业务证据 | 无已验证修复 |


## 最终执行记录 2026-10-30
M005 closed。本机后端最终pytest235 passed/1既有弃用warning/190.03s；ruff check、format111文件、mypy44源码及协议校验通过。真实HTTP/CLI、进程退出恢复/并发、资源及MA01–14/X01–12设计矩阵已完成。详见RESULT、DESIGN_CHECK、IMPLEMENTATION_MANIFEST；原始证据artifacts/validation/monitoring/v2-ma/M005/final-02与resource-attempt02。未部署/打包；前端、现场、用户索引三线联合单列pending。

最终交接补充：已读取前端接收记忆中的样例缺口，用真实MA管线生成并严格校验16个合成前端样例（含5类Snapshot、完整Receipt、质量、目录、错误），位于docs/contracts/ma-monitoring-v2/frontend.examples.json；生成器scripts/contracts/generate_ma_examples.py。部分回执状态显式为合成状态，均非现场或前端验收证据。未发跨会话消息，前端按入口自行接收。业务源码未改变，235项全量证据仍对应同一候选。

# M003 开发方案：生产画像与同集合对照

状态：**closed（2026-10-30）；下列为原计划，实际执行见文末及RESULT**。依据[设计](../../DESIGN.md)、[总执行方案](../../BATCH_PLAN.md)、[统一验收](../../ACCEPTANCE.md)。进入条件：M002 closed，以及本批所需输入版本和维护范围已登记。

## 范围与文件

统计/预计算投影，不实现路由或报警。

拟monitoring/ma/{statistics,projection}.py；tests/unit/monitoring/ma/test_statistics.py及tests/integration/monitoring/ma/test_projection.py；复用旧distribution。 新增路径均为拟建，开批时核对实际文件/符号并记录accepted_common_baseline；不能把文档路径当作已实现能力。

## 开发步骤

1. 定义并计算A/P/R/E/Q和pre质量，Q只筛聚合、不删除模拟历史。
2. 计算生产/理想各自分母和实际U；长度不一致、覆盖、无预热/冲突及空值明示。
3. request_time固定12个300s桶及3600s均值，保留零桶、分清全缺失和部分有效；精确大整数累计。
4. 生成两张独立分布的三种箱宽、200K尾桶、精确分位与众数，预生成快照供GET读取。

## 验证与出口

[TESTS](TESTS.md)全部必需项满足才可闭环。独立预期值、全部守恒及协议校验通过；无假收益/最佳算法/容量结论。 修复后相关复测、[ISSUES](ISSUES.md)闭环、[RESULT](RESULT.md)及增量记忆写完后才能进入下一批。

## 依赖与回退

用户理想C与MA实际U为不同对象；不得借用用户排行均值代替生产分布。

回退只撤回已记录的本批改动及可选接入，保留数据/失败证据，不改原CSV、旧seal、V1运行配置，不全局reset或删除共享目录。开批补齐实际源码/依赖/协议/资产SHA、环境、精确文件/符号、测试命令和回退核验；实施未发生时不得预填通过。


M003启动：新增ma/statistics.py，Python精确累加、SQLite排序、公共distribution，序列和投影持久化；无页面计算。

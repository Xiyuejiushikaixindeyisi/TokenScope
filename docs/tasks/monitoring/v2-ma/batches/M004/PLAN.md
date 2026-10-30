# M004 开发方案：发布恢复与服务接入

状态：**closed（2026-10-30）；下列为原计划，实际执行见文末及RESULT**。依据[设计](../../DESIGN.md)、[总执行方案](../../BATCH_PLAN.md)、[统一验收](../../ACCEPTANCE.md)。进入条件：M003 closed，以及本批所需输入版本和维护范围已登记。

## 范围与文件

MA服务/恢复/共用执行闸门。

拟monitoring/ma/{pipeline,service,query}.py、api/ma.py；api/app.py/cli.py等装配点先登记具体diff；拟integration/monitoring/ma/test_service.py、test_recovery.py、test_worker_lock.py。 新增路径均为拟建，开批时核对实际文件/符号并记录accepted_common_baseline；不能把文档路径当作已实现能力。

## 开发步骤

1. 受理/回执按协议，先查已有键再查文件；同键异体冲突，claim冻结配置。
2. partial→seal→MA库单事务发布；验证seal后恢复，同run一次发布，上次成功目录稳定。
3. HTTP和CLI共用服务层，目录绑定revision，快照/质量只读，旧S0不注入新字段。
4. MA与旧处理器使用同state_root/worker.lock，覆盖恢复/claim/执行/发布；dispatcher注册V1、MA、用户索引/回填适配器并非嵌套轮转，保留旧维护和停止行为。用户提供索引适配器，本线装配；源任务持锁时不能再进入索引锁。未接入用户代码的真实联合保持pending。

## 验证与出口

[TESTS](TESTS.md)全部必需项满足才可闭环。真实服务/进程/存储故障门槛通过，旧接口无破坏；mock锁或内存DB不替代证据。 修复后相关复测、[ISSUES](ISSUES.md)闭环、[RESULT](RESULT.md)及增量记忆写完后才能进入下一批。

## 依赖与回退

装配文件可能由用户线并发修改，开批重读；MA发布无跨库事务，公共设置只快照。

回退只撤回已记录的本批改动及可选接入，保留数据/失败证据，不改原CSV、旧seal、V1运行配置，不全局reset或删除共享目录。开批补齐实际源码/依赖/协议/资产SHA、环境、精确文件/符号、测试命令和回退核验；实施未发生时不得预填通过。


M004启动：M003 closed。确切文件ma/pipeline.py、ma/service.py、api/ma.py、monitoring/dispatcher.py；共享app/cli局部接入已登记。

# M002 开发方案：统一编码及UUID共享回放

状态：**closed（2026-10-30）；下列为原计划，实际执行见文末及RESULT**。依据[设计](../../DESIGN.md)、[总执行方案](../../BATCH_PLAN.md)、[统一验收](../../ACCEPTANCE.md)。进入条件：M001 closed，以及本批所需输入版本和维护范围已登记。

## 范围与文件

编码、范围适配和pre/now回放。

拟monitoring/ma/{encoding,replay}.py；tests/unit/monitoring/ma/test_replay_scope.py及tests/integration/monitoring/ma/test_encoding_replay.py；只读消费共用batch/models/shards/simulation。 新增路径均为拟建，开批时核对实际文件/符号并记录accepted_common_baseline；不能把文档路径当作已实现能力。

## 开发步骤

1. claim时冻结公共配置和资产，显式模式优先，配置/资产异常不能当坏JSON跳过。
2. 流式批编码并留生产P和本地P两列、Token分片/错误/源引用；不覆盖原appid。
3. 使用规格×UUID范围适配键调用现有完整块策略，按处理时间稳定排序；pre暖场后now继续查询/发布。
4. 检查双阶段时间冲突、无预热/仅pre/空now；pre不计now统计，新任务无持久缓存继承。

## 验证与出口

[TESTS](TESTS.md)全部必需项满足才可闭环。共享隔离、暖场/角色和匹配差分全部通过，公共旧用例回归；不能仅用stub完成编码验收。 修复后相关复测、[ISSUES](ISSUES.md)闭环、[RESULT](RESULT.md)及增量记忆写完后才能进入下一批。

## 依赖与回退

process参数名appid不能成为伪造租户的理由；公共接口变化先登记责任且兼容旧键。

回退只撤回已记录的本批改动及可选接入，保留数据/失败证据，不改原CSV、旧seal、V1运行配置，不全局reset或删除共享目录。开批补齐实际源码/依赖/协议/资产SHA、环境、精确文件/符号、测试命令和回退核验；实施未发生时不得预填通过。


M002启动：M001 closed。新增ma/replay.py，复用EncodingBatchService/TokenShardWriter/make_strategy；按uuid/role/handle_ns/源序号流式重放，顺序冲突保留生产事实。

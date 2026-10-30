# M001 开发方案：双文件输入与独立质量

状态：**closed（2026-10-30）；下列为原计划，实际执行见文末及RESULT**。依据[设计](../../DESIGN.md)、[总执行方案](../../BATCH_PLAN.md)、[统一验收](../../ACCEPTANCE.md)。进入条件：M000 closed，以及本批所需输入版本和维护范围已登记。

## 范围与文件

MA输入/存储基础，不实现缓存匹配。

拟src/tokenscope/monitoring/ma/{models,ingestion,storage}.py；tests/unit/monitoring/ma/test_ingestion.py和tests/integration/monitoring/ma/test_ingestion_store.py；复用paths及公共时间/JSON校验。 新增路径均为拟建，开批时核对实际文件/符号并记录accepted_common_baseline；不能把文档路径当作已实现能力。

## 开发步骤

1. 实现绑定与MA控制记录，角色/规格显式，不从文件名猜测；源记录键含role与CSV记录序号。
2. 校验file_ref边界，双文件流式快照/SHA及变化检测；保留原JSON字节与定位。
3. UTC/半开窗与规格校验；混规格、窗外有效行拒绝文件对，行级无效按字段分类；严格整数不舍入。
4. 分别持久化生产观测与可编码输入，保存原appid/hash，输出有界迭代和质量守恒。

## 验证与出口

[TESTS](TESTS.md)全部必需项满足才可闭环。输入保真、字段分类和守恒及所有边界通过，错误可定位；不以改写原文或静默删行换通过。 修复后相关复测、[ISSUES](ISSUES.md)闭环、[RESULT](RESULT.md)及增量记忆写完后才能进入下一批。

## 依赖与回退

只验证所提供文件及UTC约定；不声称源数据全量/实际记录层已验证。

回退只撤回已记录的本批改动及可选接入，保留数据/失败证据，不改原CSV、旧seal、V1运行配置，不全局reset或删除共享目录。开批补齐实际源码/依赖/协议/资产SHA、环境、精确文件/符号、测试命令和回退核验；实施未发生时不得预填通过。


实际启动：M000已closed。新增ma/ingest.py及独立SQLite事实表，复用InputRoot/parse_utc/validate_request，不修改用户线公共模块。角色+源序号为唯一定位，原文保留；按字段独立质量，文件级错误终止。

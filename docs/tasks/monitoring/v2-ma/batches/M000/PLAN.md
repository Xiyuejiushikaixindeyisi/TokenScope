# M000 开发方案：依赖基线与MA契约

状态：**closed（2026-10-30）；下列为原计划，实际执行见文末及RESULT**。依据[设计](../../DESIGN.md)、[总执行方案](../../BATCH_PLAN.md)、[统一验收](../../ACCEPTANCE.md)。进入条件：用户明确启动实施；核对最终设计及共享职责，以及本批所需输入版本和维护范围已登记。

## 范围与文件

契约和基线，不实现业务回放。

拟contracts/下CONTRACT、字段字典、Schema、设计OpenAPI、合成样例、manifest；拟scripts/contracts/validate_ma_contract.py，不覆盖旧S0。 新增路径均为拟建，开批时核对实际文件/符号并记录accepted_common_baseline；不能把文档路径当作已实现能力。

## 开发步骤

1. 锁定源码/依赖/资产/用户设计与公共接口SHA，登记accepted_common_baseline及维护方。与用户v1.0核对时间解析错误字段/策略和用户索引process_next注册接口；未实现时以契约和夹具验证，不冒充真实联合。
2. 固定提交/回执、三个UUID身份、目录revision、A/P/R/E/Q、12桶、空值/整数、错误/恢复语义；消除影响编码的待定项。
3. 生成合成正负样例及协议验证器，冻结摘要和版本规则；设计OpenAPI明确未实现。

## 验证与出口

[TESTS](TESTS.md)全部必需项满足才可闭环。协议/样例/负例全部通过，公共责任和基线可追溯；无阻塞实现的未定语义。 修复后相关复测、[ISSUES](ISSUES.md)闭环、[RESULT](RESULT.md)及增量记忆写完后才能进入下一批。

## 依赖与回退

用户线可能继续修订时间/模式/排行；先锁定已接入能力，不假定对方整线完成。

回退只撤回已记录的本批改动及可选接入，保留数据/失败证据，不改原CSV、旧seal、V1运行配置，不全局reset或删除共享目录。开批补齐实际源码/依赖/协议/资产SHA、环境、精确文件/符号、测试命令和回退核验；实施未发生时不得预填通过。


## 实际启动记录
状态更新为in_progress。用户已批准设计及全部顺序开发；本批新增src/tokenscope/monitoring/ma/contracts.py与tests/unit/ma/test_contracts.py。共享用户契约、csv_reader、simulation、pipeline仅核对不修改。先验证连续窗口、集合交集上下界及精确Token守恒，再补完整协议。

# U008 设计符合性

| 要求 | 实现 | 验证 |
| --- | --- | --- |
| 最小参数、O移除、显式W | BatchScenario / EvaluationRequest；新模型extra forbid | minimal_contract必填/非法/证据选填；HTTP缺参不入库 |
| W总非计算，K为整批进度近似 | estimator.calculate新分支T−W及limitations | boundaries / fraction_oracle / 6份新旧响应 |
| ≤/<与0/100/无预算、正P90 | 精确Fraction、既有状态机 | 边界表、640组有理数枚举、无正P90 |
| 可选覆盖范围、不假造无限范围 | 成对可空bounds；缺省unverified提示 | optional_range、单边范围拒绝 |
| 新旧显式区分、旧JSON形状不变 | ScenarioPayload与SCENARIO_ADAPTER | 旧Scenario往返、旧HTTP计算、冻结旧Evaluation直接入库回放 |
| 不可变revision/幂等/GET无写入 | 保留EstimatorService事务/快照 | 冲突、并发、重启、索引删除仍复读、文件mtime/DB摘要不变 |
| 三模型/用户范围不变 | 复用现有编码、索引及服务匹配 | 三模型CSV→索引→ASGI API；全量V1/MA/用户回归 |
| 极端输入稳健 | 输入128字符、派生n256字符 | 254位n通过，非法/非有限拒绝 |
| 前端交接，不修改前端 | TTFT_FRONTEND_HANDOFF及契约2.0.0 | 文件摘要审计、相对链接检查 |

不声称生产P90目标可保证、完整公式已校准、总体命中率可直接判达标。前端浏览器联合验收未执行。

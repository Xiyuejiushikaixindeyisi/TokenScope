# 每批记录模板

执行批次时将以下四节分别保存为batches/Uxxx/PLAN.md、ISSUES.md、TESTS.md、RESULT.md。未开始不得写通过。规划依据为[BATCH_PLAN](BATCH_PLAN.md)，实现依据为[DESIGN](DESIGN.md)。

## PLAN.md

- 批次/日期/负责人/状态：
- 设计版本与需求ID：
- 前批RESULT及通过证据：
- 起始HEAD、已有未提交文件、资产/契约身份：
- 修改文件与类/函数、共享拥有方和接入版本：
- 逐步实施内容、禁止改变的不变量：
- 用例ID、独立期望值与测试层级：
- 预先固定的资源/性能预算（环境、数据hash、CPU/RSS/磁盘/耗时/查询门槛）：
- 回退/失败恢复方案：
- 外部依赖与不允许宣称的完成范围：

## ISSUES.md

| ID | 发现步骤/输入 | 影响/严重度 | 根因 | 处理/版本 | 关联测试/证据 | 状态/未决 |
| --- | --- | --- | --- | --- | --- | --- |

状态使用open/resolved/deferred；deferred注明依据及影响，阻断正确性/兼容/恢复的缺陷不得defer后closed。每次修复及复测追加记录，不能只删除失败。

## TESTS.md

| 用例ID | 环境/数据与资产摘要 | 命令 | 期望值及来源 | 实际结果/退出码 | 日志/摘要 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |

通过/失败/未执行分别统计；记录时间、运行器、代码身份、重试与最终结论，人工核查同样留依据。本地fixtures、mock、真实编码、真实HTTP、前端和现场不能混写。

已核实项目pytest、ruff、mypy配置位于pyproject.toml；开发环境就绪后运行受影响pytest用例，以及python -m ruff check、python -m ruff format --check、python -m mypy（范围在PLAN中明确）。最终pytest覆盖tests/unit与tests/integration。已有scripts/validation/check_batch.py、run_monitoring_e2e.py、run_monitoring_view_e2e.py可复用；先读参数和实际资产需求再写确切命令，不猜命令行参数。业务新增测试放tests对应目录，不将文档检查当业务测试。

## RESULT.md

- 状态：planned/active/verifying/closed/blocked/needs_revision
- 实际完成与未完成：
- 源码身份/契约/数据/证据摘要：
- 门槛逐项结果：
- 问题关闭情况与阻断/外部pending：
- 设计对照（需求→实现→测试→证据→偏差）：
- 回退/恢复验证：
- 可供下一批/MA/前端消费的版本：
- memory增量记录位置及下一步：

closed需有实际证据，不是文件数量达标；“后端本地完成”不得改写为“联合/现场完成”。部署打包始终另行授权。

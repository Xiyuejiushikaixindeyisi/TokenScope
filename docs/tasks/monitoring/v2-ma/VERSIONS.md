# MA监控设计版本与恢复入口

2026-10-30。当前唯一活动设计：[DESIGN v1.0](DESIGN.md)。它是文档最终稿，未实施；不改变monitoring-v1-20261028、dev6/F007、S0 1.0.0、control3/view1或应用版本。

| 版本 | 状态与位置 | 变化 |
| --- | --- | --- |
| MA v0.1 | [按字节归档](../../../../achieve/2026-10-30/monitoring-v2-ma-design-v0.1/MA_DESIGN.md)，仅追溯 | 最初完整审批稿；未编码 |
| 用户v0.1核对输入 | [只读快照](../../../../achieve/2026-10-30/monitoring-v2-ma-design-v0.1/USER_DESIGN_REVIEW_INPUT.md)；活动入口仍由用户线维护 | 本线不改原文；输入SHA固定本轮交叉核对范围 |
| 用户v1.0追加核对 | [最终稿输入快照](../../../../achieve/2026-10-30/monitoring-v2-ma-design-v0.1/USER_DESIGN_V1_REVIEW_INPUT.md) | 用户线并行完成v1.0后重新核查；补齐用户索引/回填同一执行额度及公共解析字段定位 |
| MA v1.0 | [最终设计](DESIGN.md)＋[交叉核对](CROSS_CHECK.md)＋[batch计划](BATCH_PLAN.md)＋[统一验收](ACCEPTANCE.md) | 区分P_db/P_local和实际U/理想C、开放排行箱与旧展示箱；统一UTC/模式来源；补充共用worker.lock、单库恢复/发布、六批四文档与最终符合性检查 |

v0.1 MA SHA256：`e1865de93326954a8caf7ed1d3c6165dbeb632441b229b9da6e323da1fb126fb`。

用户v0.1输入SHA256：`bc036529fa013a43339d3cb57b7eb70b1cca5aceaee339717aa3ae237c549c08`。

用户v1.0追加核对输入SHA256：`f991245dbe48a2568c721ba67256d91b3bdbf86b997bdf79c373386f1c70b110`。后续用户文件如再次修订，以此快照明确本次阅读范围，实施前重核差异。

本轮文档身份、归档摘要与检查范围见[DESIGN_MANIFEST](DESIGN_MANIFEST.json)；该清单是文档版本证据，不是release manifest，也不是实现通过报告。工作树包含其他会话修改，版本整理只维护本线和共享状态中的本线部分；本轮未执行Git提交/push，不改分支/tag，不混合提交用户线或分析线工作。

## Agent恢复顺序

AGENTS→CURRENT→SESSIONS→[ENTRY](ENTRY.md)→当前设计→CROSS_CHECK→BATCH_PLAN→ACCEPTANCE→当前batch的PLAN/ISSUES/TESTS/RESULT。运行前确认实际用户启动授权；本次结束M000–M005都是planned，契约尚未冻结，无代码/业务测试证据。

历史讨论记忆已保留在[整理前快照](../../../../achieve/2026-10-30/monitoring-v2-ma-design-v0.1/MA_MEMORY_BEFORE_V1.md)，活动[本线记忆](../../../../memory/tasks/monitoring-v2-ma.md)只保留当前事实、依赖和增量进度。历史文件内部相对链接保留原字节；阅读当前导航使用本页。

后续设计修订须记版本、原因、影响需求/batch/契约、确认来源及需重测项；代码版本、MA协议版本和设计版本分开记录。未满足上一批门槛不能仅通过改设计文档把失败改名为通过。

## 本机实现检查点（2026-10-30）
设计1.0已获用户批准并实施；MA协议1.0.0独立于旧S0，M000–M005本机后端闭环。[最终实现/验证清单](batches/M005/IMPLEMENTATION_MANIFEST.json)及[报告](batches/M005/RESULT.md)为当前身份；原DESIGN_MANIFEST仅保留设计阶段检查记录，不作为最新工作树摘要。未改变发布tag/包体身份，未Git提交push，未部署打包。

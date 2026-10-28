# Token 监控版本与权威入口

更新：2026-10-27。批准计量设计v1.0原摘要不变；代码0.1.0.dev6/schema3/view1（backend_ready_for_joint）。B001–B005原后端本机门槛通过，**V1前后端完整服务未完成**；B005.1设计v0.2与B006评审修订完成；S0契约1.0.0固定，S1–S5后端闭环；B006历史准备已归档/pending。

## 当前一致版本集

| 内容 | 权威入口 | 状态 |
| --- | --- | --- |
| 设计 v1.0 | [DESIGN](DESIGN.md) | 已批准；原稿摘要见 APPROVAL |
| 评审阅读版 | [HTML](../../../achieve/2026-10-28/docs/tasks/monitoring/TOKEN_MONITORING_V1_APPROVAL.html) / [Markdown](../../../achieve/2026-10-28/docs/tasks/monitoring/TOKEN_MONITORING_V1_APPROVAL.md) | 从 DESIGN 生成，包含组件、类、时序和活动四图 |
| 公共契约 v1.0 | [MONITORING_V1](../../contracts/MONITORING_V1.md) | 与 rc2 的指标/仿真/分布语义一致；补充运行和交付接口 |
| 示意样例 v1.0 | [JSON](../../contracts/examples/monitoring-v1-illustrative.json) | 人工数据，包含三模型、分箱边界、并列众数和空集；非业务实测 |
| 环境证据 | [原报告](../../huawei/TOKEN_SCOPE_V100_ENVIRONMENT_REPORT.md) / [核对](../../huawei/MONITORING_V100_DESIGN_REVIEW_2026-10-26.md) / [profile](../../../env/profiles/huawei-v100-2026-10-26.json) | 原报告未改写；兼容性和性能未验证 |
| 执行与进展 | [batch 索引](batches/README.md) / [监控记忆](../../../memory/tasks/monitoring.md) | B001–B005后端closed；B005.1 S0已固定，S1–S5后端闭环；B006归档/pending；生产DeepSeek缺省pending |
| 恢复上下文 | [当前交接](../../../achieve/2026-10-28/memory/handoffs/2026-10-27-monitoring-development.md) / [CODEMAP](CODEMAP.md) | 下一轮按当前 batch 扩展阅读 |
| 本次版本摘要与检查 | [manifest](../../../artifacts/reviews/monitoring-v1/design-v1.0-manifest.json) / [检查结果](../../../artifacts/reviews/monitoring-v1/context-validation.json) | 文档/图形/链接/样例检查，不代表代码或部署测试 |

## 历史与替代关系

| 版本 | 关键内容/变化 | 追溯入口 |
| --- | --- | --- |
| v1.0 | 纳入 V100 现场事实；CPU 交付与资源初值；逐批五文档/门槛/增量记忆；六批计划、设计对照和现场首次验收 | 当前 DESIGN |
| v1.0-rc2 | 默认 5K、众数高亮、≥200K 尾桶和图外分位数；环境探测 prompt | [历史设计](../../archive/monitoring/DESIGN_v1.0-rc2.md)、[历史契约](../../contracts/MONITORING_V1_RC2.md)、[历史样例](../../contracts/examples/monitoring-v1-rc2-illustrative.json) |
| v1.0-rc1 | 三模型普通链式 DES；默认 128/1536/32；hybrid 只留接口 | [历史设计](../../archive/monitoring/DESIGN_v1.0-rc1.md)、[历史契约](../../contracts/MONITORING_V1_RC1.md) |
| v0.2.2 及更早 | 增强 hybrid 研究和此前候选，不是当前必做范围 | [历史设计](../../archive/monitoring/DESIGN_v0.2.2.md)；按 CODEMAP 查研究，不全量阅读 |

归档设计仅为迁移目录修正必要相对链接，业务正文保留其当时状态。审批阅读版是生成副本，正文更改只维护 DESIGN 后重新生成，不能各改一份。

## 原型与其他会话

[冻结 HTML 起点](../../../artifacts/prototypes/monitoring-v1/tokenscope-monitoring-baseline-v1.html)仍保留其 v1.0-rc2 身份及[原清单](../../../artifacts/prototypes/monitoring-v1/baseline-manifest.json)，不为升级设计号而重写已交给前端的产物。当前图表语义仍兼容；前端 fork 独立维护后续原型与展示设计，本轮没有修改它们。共享契约的实际 schema 在 B001 固化时登记兼容性；业务语义/不兼容接口改变须先讨论。

审批时记录被批准的设计与契约摘要，不修改为“代码已完成”。后续每批记录实际源码/测试身份；发布包用独立 release_id 关联代码、依赖、资产、镜像和现场报告。任何后续修订都追加版本说明和受影响范围，不能覆盖历史证据或悄悄改变批准口径。

## 实现版本增量

- dev1/B001：66项门槛，schema1；dev2/B002闭环96项；B003闭环117项。
- dev4/B004：schema2增量配置/快照/结果/outbox，131项；完整HTTP/CLI后端。
- dev5/B005：8CPU进程约束、145项最终回归、源码摘要绑定的实际进程E2E；[最终报告](../../../artifacts/validation/monitoring/B005/20261027T035327Z/report.json)。
- [实现API](../../contracts/MONITORING_IMPLEMENTED_API.md)、[当前schema](../../contracts/schemas/monitoring-current.openapi.json)、[执行合成样例](../../contracts/examples/monitoring-v1-executed-synthetic.json)供前端/分析消费。B001/B004 schema快照保留历史。
- B006原仅后端准备已[归档](../../archive/monitoring/B006-backend-preparation-2026-10-27/README.md)，原路径只保留追溯；pending。前后端完整服务验收和新的打包批准是恢复前置。

## B005.1规划及S0契约版本

[设计v0.2](batches/B005.1/DESIGN.md)、[共享接口草案](../../contracts/MONITORING_VIEW_V1_DRAFT.md)、[输入摘要](batches/B005.1/INPUT_MANIFEST.json)。拟dev6/schema3/view1仅为计划，不修改运行版本/当前OpenAPI；完整服务还需前端资源版本和J01–J06真实联合证据。

S0：[固定交接](batches/B005.1/S0_CONTRACT.md)、[Schema/样例清单](batches/B005.1/S0_MANIFEST.json)、[闭环](batches/B005.1/S0/RESULT.md)。本轮评审响应与修订摘要见[响应v0.2](../../../achieve/2026-10-28/docs/tasks/monitoring/batches/B005.1/REVIEW_RESPONSE_v0.2.md)。旧v0.1文档[14文件原字节归档](../../archive/monitoring/B005.1-v0.1-2026-10-27/README.md)；旧B00619文件不变。前端可消费固定契约，实际服务和最终联合另验。


2026-10-27 joint-v1-20261027：dev6/f006联合修正版（按joint-v1/source-manifest.json身份），不覆盖S0和原版本证据；统一本机验收完成，未打包，详见JOINT_RESULT_V1.md。

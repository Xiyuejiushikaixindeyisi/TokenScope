# B005.1 代码编写与实施方案

2026-10-27，**待评审；本轮仅形成方案与归档，未开始编码**。依据 [CONTEXT](CONTEXT.md)、[DESIGN v0.1](DESIGN.md)、[共享接口草案](../../../../contracts/MONITORING_VIEW_V1_DRAFT.md)。恢复代码实施后按以下小步验证推进，不跳过失败进入下一步。

## 开发顺序与门槛

| 步骤 | 行为和代码范围 | 进入下一步的门槛 |
| --- | --- | --- |
| S0 契约固定 | 确认latest、SSE游标/终态、视图生成、整数规则；增加view_models.py和JSON样例；版本拟dev6/schema3/view1，当前版本不提前变更 | BE01–BE10逐项映射、字段和错误明确，用户/前端可核对 |
| S1 元数据/迁移/目录 | view_projection.py、publications.py、storage/pipeline；数值时间范围、scope质量、sidecar、历史回填、完整组目录和运行目录 | 空库/旧库可恢复迁移；旧结果不变；latest/分页一致；失败不暴露半成品 |
| S2 发布与SSE | complete/fail/claim失败同事务事件，events.py/API；重放/reset/心跳/慢连接 | 崩溃各切点、无报警通知、空结果、断线恢复和幂等发布通过 |
| S3 轻量快照 | views.py和DTO；三宽度已有值、冻结参数/规则、固定信号摘要、ETag及scope身份 | 与原结果逐值一致；GET计算哨兵通过；旧包不随设置/消费变化 |
| S4 操作链路 | 单查询多列请求、详情/原文/轻证据、view-signals、设置/规则无损整数适配、submission_key及查回、NDJSON/CSV导出 | 不同排名/重复hash/分页/并发提交/丢回执重试/导出完整性全部通过 |
| S5 本机综合验收 | 新HTTP/SSE E2E、性能/故障、旧145项回归、OpenAPI/实测样例、设计对照和回退演练 | TESTS所有后端必测门槛通过，ISSUES无阻断，RESULT记录实际结果 |
| J1 前后端联合验收 | 已登记前端会话的实际页面 + 同一候选后端/契约/数据 | 用实际浏览器证明全链路；假服务/后端HTTP不替代；未完成则V1未完成 |

S0–S5是同一个 B005.1 内部步骤，不假造六个已经闭环的新 batch。J1 是完整服务的独立发布门槛，可在 B005.1 后端关闭后联合执行；未取得实际前端版本和测试证据时写 pending。用户只要求本轮方案，不因写出实施顺序自动开始执行。

## 修改清单

新增拟定：
- src/tokenscope/monitoring/{view_models,view_projection,publications,events,views}.py。
- tests/unit/monitoring/test_{view_projection,publications,view_wire}.py。
- tests/integration/monitoring/test_{view_api,publication_recovery,submission_idempotency,view_migration,view_export}.py。
- scripts/validation/run_monitoring_view_e2e.py；artifacts/validation/monitoring/B005.1/ 下实际报告/快照/性能。

增量修改：
- storage.py：schema迁移、同事务发布/失败/入队幂等；pipeline.py：展示预处理、时间边界修复与封存恢复；service.py/API/CLI：只读接口和显式迁移/运行支持；domain.py：submission_key可选字段。
- scripts/validation/check_batch.py 当前 choices 不接受 B005.1，实施时补上，并把新增验证代码纳入源码清单；保留旧批证据。
- 实施后生成新的 OpenAPI，更新 MONITORING_IMPLEMENTED_API、操作说明和 CODEMAP；草案与实测例分开存。旧批OpenAPI/批准DESIGN不覆盖。
- B006原脚本/门槛测试目前保留原路径用于历史回归；本批不把其仅后端白名单升级为有效交付方案。B006重启时才重做完整服务交付计划。

不修改 apps/viewer、viewer设计/HTML、上游代码、生产部署参数默认值或已封存结果。若联调发现消费方需求变化，更新共享契约并记录影响，不擅自代做前端。

## 代码质量、测试与问题记录

沿用 pytest、ruff check/format、mypy 和独立真实进程 HTTP 验证。关键事务用故障注入/进程中断，SSE必须用实际网络流连接验证，不能仅靠TestClient一次性读取。新的行为测试不复制实现；统计和命中沿用B005独立参考，新增测试只比对投影不改变值。

每个失败按ISSUES登记复现、根因、修正、重测证据；TESTS记录代码/资产/配置/环境/种子/命令/退出码。通过后 RESULT 逐项映射BE与验收ID并更新监控增量记忆、入口、CODEMAP、版本。禁止用文档检查替代业务测试。

## 回退及交付边界

S1前形成B005源码清单和schema2库一致性备份；S5实际演练回退并记录新增状态保留方式，详见DESIGN第8节。B006所有已有准备已归档、pending；只有后端增补与实际前端联合验收通过，再提交完整服务的版本、范围、测试证据询问打包意见。用户明确同意后才构建镜像/代码交付包；不以Docker循环修代码。


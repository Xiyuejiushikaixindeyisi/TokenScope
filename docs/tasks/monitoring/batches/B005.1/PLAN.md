# B005.1 代码编写与实施方案

2026-10-27，v0.2：**用户已批准实施。S0保持冻结，S1–S5后端门槛闭环；backend_ready_for_joint，未打包**。依据 [CONTEXT](CONTEXT.md)、[DESIGN v0.2](DESIGN.md)、[共享接口草案](../../../../contracts/MONITORING_VIEW_V1_DRAFT.md)。恢复代码实施后按以下小步验证推进，不跳过失败进入下一步。

## 2026-10-27 当前有效授权（覆盖下方历史状态）

用户明确批准B005.1 PLAN、S0契约和TESTS，后端从S1开始逐步验证并闭环；完成本批约定工作即停止。双方完成后由后端统一真实端到端验收，前端未就绪则如实pending。Docker、镜像及交付包未获授权，不进入B006构建/打包。当前S1–S5 closed / backend_ready_for_joint；S0固定清单已核对，基线源码副本见artifacts/validation/monitoring/B005.1/baseline。

## 主审批与代码启动入口

本文件是B005.1唯一主审批/后端实施计划，附件为[S0固定契约](S0_CONTRACT.md)和[TESTS](TESTS.md)。DESIGN供技术核对，CONTEXT/ISSUES/RESULT/manifest供执行追溯，不逐份申请审批。

授权记录：2026-10-27用户已批准本PLAN、S0和TESTS，从S1实施并逐步验证闭环；Docker和交付包仍未授权。门槛满足后自主推进，不逐步重复申请。

开始S1前：核对S0_MANIFEST→登记采用版本→读S1对应DESIGN/TESTS及CODEMAP源码→确定本步修改和回退点。每步更新父batch问题/测试/结果与记忆，门槛未满足不得推进；不重做S0或重写批准计量设计。前端仍由原会话维护。

前后端交接、文档权威与问题处理统一见[协作方案](../../../../architecture/TASK_SESSION_WORKFLOW.md)。S5后交付实际API/启动方式/合成数据/版本/测试/遗留项，标backend_ready_for_joint；前端F006提供对应构建/锁/资源/测试与回退。Session 1统一运行本批TESTS的J门槛；B006 P1只引用此结果，不另执行一套重复标准。

## 开发顺序与门槛

| 步骤 | 行为和代码范围 | 进入下一步的门槛 |
| --- | --- | --- |
| S0 契约固定 | 固定R1回执/连接对齐、实例防护和R2完整字节协议/样例，再确认latest、视图生成、整数规则；输出完整Schema/设计OpenAPI/字段字典/成功错误样例，view_models.py实现放S1；版本拟dev6/schema3/view1，当前版本不提前变更 | [S0固定交接](S0_CONTRACT.md)及校验/摘要完成，前端可锁版本；此门槛已通过 |
| S1 元数据/迁移/目录 | 按固定Schema实现view_models.py；view_projection.py、publications.py、storage/pipeline；数值时间范围、scope质量、sidecar、历史回填、完整组目录和运行目录 | 空库/旧库可恢复迁移；旧结果不变；latest/分页一致；失败不暴露半成品 |
| S2 发布与SSE | complete/fail/claim失败同事务事件，events.py/API；重放/reset/心跳/慢连接 | 崩溃各切点、无报警/空结果、终态早于cursor及reset恢复的持久状态一致、幂等发布通过 |
| S3 轻量快照 | views.py和DTO；三宽度已有值、冻结参数/规则、固定信号摘要、ETag及scope身份 | 与原结果逐值一致；GET计算哨兵通过；旧包不随设置/消费变化 |
| S4 操作链路 | 单查询多列请求、详情/原文/轻证据、view-signals、设置/规则无损整数适配、submission_key及查回、NDJSON/CSV导出 | 不同排名/重复hash/分页/并发提交/R1丢回执恢复/R2原字节摘要与结构/计数全部通过 |
| S5 本机综合验收 | 新HTTP/SSE E2E、性能/故障、旧145项回归、OpenAPI/实测样例、设计对照和回退演练 | TESTS所有后端必测门槛通过，ISSUES无阻断，RESULT记录实际结果 |
| J1 前后端联合验收（Session 1统一执行） | 接收前端F006 ready_for_joint固定构建/证据，实际页面+候选后端/契约/数据 | J01–J06及R1/R2真实浏览器、统一E2E/健壮性/设计核对通过；假服务或各方单独报告不替代 |

S0–S5是同一个 B005.1 内部步骤，不假造六个已经闭环的新 batch。J1 是完整服务的独立发布门槛，可在 B005.1 后端关闭后联合执行；未取得实际前端版本和测试证据时写 pending。S0已实际交付；S1–S5按已批准范围实施。真实前端联合需F006固定交接，不能以本批后端通过替代。

## 修改清单

新增拟定：
- src/tokenscope/monitoring/{view_models,view_projection,publications,events,views}.py。
- tests/unit/monitoring/test_{view_projection,publications,view_wire}.py。
- tests/integration/monitoring/test_{view_api,publication_recovery,submission_idempotency,view_migration,view_export}.py。
- scripts/validation/run_monitoring_view_e2e.py；artifacts/validation/monitoring/B005.1/ 下实际报告/快照/性能。

增量修改：
- storage.py：schema迁移、同事务发布/失败/入队幂等；pipeline.py：展示预处理、时间边界修复与封存恢复；service.py/API/CLI：只读接口和显式迁移/运行支持；src/tokenscope/domain.py：submission_key可选字段。
- scripts/validation/check_batch.py 当前 choices 不接受 B005.1，实施时补上，并把新增验证代码纳入源码清单；保留旧批证据。
- 实施后生成新的 OpenAPI，更新 MONITORING_IMPLEMENTED_API、操作说明和 CODEMAP；草案与实测例分开存。旧批OpenAPI/批准DESIGN不覆盖。
- B006原脚本/门槛测试目前保留原路径用于历史回归；本批不把其仅后端白名单升级为有效交付方案。B006的完整服务统一交付计划本轮同步修订，实际执行仍pending。

不修改 apps/viewer、viewer设计/HTML、上游代码、生产部署参数默认值或已封存结果。若联调发现消费方需求变化，更新共享契约并记录影响，不擅自代做前端。

## 代码质量、测试与问题记录

沿用 pytest、ruff check/format、mypy 和独立真实进程 HTTP 验证。关键事务用故障注入/进程中断，SSE必须用实际网络流连接验证，不能仅靠TestClient一次性读取。新的行为测试不复制实现；统计和命中沿用B005独立参考，新增测试只比对投影不改变值。

每个失败按ISSUES登记复现、根因、修正、重测证据；TESTS记录代码/资产/配置/环境/种子/命令/退出码。通过后 RESULT 逐项映射BE与验收ID并更新监控增量记忆、入口、CODEMAP、版本。禁止用文档检查替代业务测试。

## 回退及交付边界

S1前形成B005源码清单和schema2库一致性备份；S5实际演练回退并记录新增状态保留方式，详见DESIGN第8节。B006所有已有准备已归档、pending；只有后端增补与实际前端联合验收通过，再提交完整服务的版本、范围、测试证据询问打包意见。用户明确同意后才构建镜像/代码交付包；不以Docker循环修代码。


## R1/R2实现与交接细化

S0输出v0.2协议及完整回执/导出fixture，明确UTF8/LF与CSV头/计数、instance防护和terminal规则；所有完整DTO/OpenAPI已在S0 1.0.0固定，前端可锁定契约，但其实际接收/恢复状态由自身登记。S2/S4在既有状态查询上补持久回执联结、实例校验、同事务终态事件，无周期查询任务。前端ReceiptStore/4并发对齐/终态合并由前端F004维护。

后端拟新增或扩展test_submission_recovery、test_export_protocol与真实流验证入口；R2以可独立复核样例比较原字节摘要/CSV记录数，覆盖空输出/Unicode/引号换行/重复hash。实际浏览器故障代理和≥256MiB压力夹具只在授权实施/联合阶段准备并执行，不能为简化测试更改生产统计。

J1由Session 1统一执行，前端提供F006交接和修复支持；联合报告路径拟artifacts/validation/monitoring/joint-v1/<candidate>/，含双方源码/资源/锁/契约与数据摘要、浏览器/环境身份、R1时序网络证据、R2队列/内存/实际文件证据、问题回归和设计对照。之后后端统一负责获批的Docker/镜像归档/代码包。具体见[B006设计](../B006/DESIGN.md)。

## S0独立交付（已完成）

按用户最新要求，S0是前端开发的前置交付，本轮先完成。见[S0固定契约及R1/R2边界](S0_CONTRACT.md)、[五文档闭环](S0/RESULT.md)及[S0_MANIFEST](S0_MANIFEST.json)。包含全部字段/nullable/精确整数、16路径18操作设计OpenAPI、完整成功/错误样例、SSE与导出字节夹具、校验工具与实际记录；Schema和样例验证已通过。

F001可据此做类型/契约假服务，实际接收版本由前端登记，不自动发送消息或恢复其会话。S1开始前必须校验固定摘要，view_models实现接受同样例；S5真实API与固定设计OpenAPI对照，存在不兼容差异先修订契约并协调消费方。S0不是运行代码、API或浏览器验收。

执行完成：2026-10-27，S1–S5后端范围已闭环，证据见RESULT；遵用户要求停止，不自动进入Docker/交付包或启动未就绪的联合验收。

# B005.1 上下文：监控展示服务增补

2026-10-27；Session 1：`01a1682f-956d-7630-afe7-e123ba38dfc0`，本轮从 CODEX_THREAD_ID / CODEX_SESSION_ID 核实。状态：**v0.2按R1/R2修订，S0契约已固定，S1–S5业务实现未开始**。

## 最新范围

用户明确第一版是前端和后端组成的完整服务，当前尚未完成。本轮授权：按用户提供的后端交接评审修订B005.1、共享契约及B006；用户已采用R1终态恢复和R2方案A方向，后端Session 1统一负责最终联合测试及获批后交付。B006 pending。此次不恢复业务编码、Docker 构建或打包。前端仍由已登记会话维护，不替其宣布实施进度。

B001–B005 closed 只表示各批既定后端本机门槛通过；145 项回归和三模型真实 HTTP 合成 E2E 是已有后端证据，不是浏览器接入/完整服务验收。旧“只剩 B006”“可单独交付后端”的当前执行安排由本次决定覆盖。

## 固定输入与阅读边界

| 输入 | 用途 |
| --- | --- |
| [后端增补 BE01–BE10](../../../../../../../docs/tasks/viewer/BACKEND_REQUIREMENTS_V1.md) | 六类增补与操作完整性 |
| [前端最终评审稿 v1.0](../../../../../../../docs/tasks/viewer/MONITORING_INTERACTION_V1.md) | 推送后读取、完整版本切换、缓存及联调责任 |
| [批准设计 v1.0](../../../../../../../docs/tasks/monitoring/DESIGN.md)、[批准契约](../../../../../../../docs/contracts/MONITORING_V1.md) | 计量、DES、分位数、模型配置和安全边界保持 |
| [已实现 API](../../../../../../../docs/contracts/MONITORING_IMPLEMENTED_API.md) | 兼容旧入口，不把提案当已实现 |
| [B005 闭环](../B005/RESULT.md)和[最终 E2E](../../../../../../../artifacts/validation/monitoring/B005/20261027T035327Z/report.json) | 开发基线 0.1.0.dev5 / schema2 |
| [旧输入摘要](../../../../../../../docs/tasks/monitoring/batches/B005.1/INPUT_MANIFEST.json)、[本次评审输入摘要](../../../../../../../docs/tasks/monitoring/batches/B005.1/REVIEW_INPUT_MANIFEST_v0.2.json) | 旧v0.1身份保留；新清单固定交接prompt、前端v1.0/评审/验收及源码 |
| [本批设计](../../../../../../../docs/tasks/monitoring/batches/B005.1/DESIGN.md)、[共享接口草案](../../../../../../../docs/contracts/MONITORING_VIEW_V1_DRAFT.md) | 本批实现前须确认的增量设计 |
| [B006 归档](../../../../../../../docs/archive/monitoring/B006-backend-preparation-2026-10-27/README.md) | 原仅后端准备材料，退出当前交付路径 |

源码只读核对：storage.complete / enqueue / fail、pipeline.execute / recover、statistics.aggregate、service 查询、API 路由、编码落盘。已存在 groups 的全部三宽度直方图、facts 的 J/P/H/C/O、request_records 的原 JSON 和 encoded_requests.evidence_json。缺发布目录/事件日志/提交幂等/组合展示接口；现有 signals 无筛选分页。pipeline 文件时间范围使用 min/max(time_utc)，必须改按 time_ns 取边界。

保持公开固定资产、生产 DeepSeek 缺省 pending、GLM CP 映射未决等原边界。生产 CSV 不进入本机；每模型 5 appid 的固定种子泊松合成数据继续用于本机验证。单文件 <7200 秒预算覆盖新增展示预处理。不要读取整套 upstream 或改动 viewer 的设计/HTML/源码。

## 完成层级

B005 后端基线 → B005.1 后端增补验收 → 前端实际接入及完整服务联合验收 → 用户明确批准打包 → B006 重定交付范围并执行。B005.1 可先关闭后端子批，但联合验收未通过时，项目 V1 仍未完成、B006 仍 pending。


## 本次直接依赖

[交接prompt](../../../../../prompts/sessions/MONITORING_BACKEND_FRONTEND_V1_HANDOFF.md)、[前端R1/R2评审](../../../viewer/reviews/B005_1_REVIEW_2026-10-27.md)、[F001–F006](../../../../../../../docs/tasks/viewer/batches/README.md)、[V01–V15](../../../../../../../docs/tasks/viewer/ACCEPTANCE_V1.md)。前端最终方案及具体浏览器边界后续已获批，F001因完整契约依赖暂停；本轮不改viewer文件或其状态。修订映射和前端可接入条件见[响应](REVIEW_RESPONSE_v0.2.md)。

本轮后续观测：[前端审批记录](../../../../../../../docs/tasks/viewer/APPROVAL.md)确认v1.0已获批准，SHA与设计文件相符；[F001-I01](../../../viewer/batches/F001/ISSUES.md)因缺完整schema/样例暂停。交接prompt中的“待前端审批”是较早状态，本次以前述记录为准，未改写前端文件或状态。

## 本轮最新指令：先完成S0

用户要求后端设计/开发先完成S0契约固定，因为前端依赖。已交付[S0 1.0.0](../../../../../../../docs/tasks/monitoring/batches/B005.1/S0_CONTRACT.md)字段/完整成功错误样例/R1R2边界及实际契约校验；S1–S5业务实现未启动。历史F001依赖发现记录保留，前端是否恢复由其会话/用户处理。

## 已批准实施的上下文更新
2026-10-27用户批准PLAN/S0/TESTS，由后端S1顺序实施至S5闭环即停止，前端按固定S0独立开发。双方ready后后端统一真实联合；Docker/交付另行用户批准。当前dev6/schema3/view1候选，具体门槛与未决项以RESULT/ISSUES最新记录为准，不沿用本文早期“未开始实施”的阶段状态。

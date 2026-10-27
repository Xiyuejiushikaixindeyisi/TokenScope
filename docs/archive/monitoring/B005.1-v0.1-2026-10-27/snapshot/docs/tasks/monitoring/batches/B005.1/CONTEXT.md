# B005.1 上下文：监控展示服务增补

2026-10-27；Session 1：`01a1682f-956d-7630-afe7-e123ba38dfc0`，本轮从 CODEX_THREAD_ID / CODEX_SESSION_ID 核实。状态：**方案待评审，尚未编码**。

## 最新范围

用户明确第一版是前端和后端组成的完整服务，当前尚未完成。本轮授权：读取前端两份提案，生成 B005.1 设计、代码编写和验收方案；归档 B006 已有产出，B006 pending。此次不恢复业务编码、Docker 构建或打包。前端仍由已登记会话维护，不替其宣布实施进度。

B001–B005 closed 只表示各批既定后端本机门槛通过；145 项回归和三模型真实 HTTP 合成 E2E 是已有后端证据，不是浏览器接入/完整服务验收。旧“只剩 B006”“可单独交付后端”的当前执行安排由本次决定覆盖。

## 固定输入与阅读边界

| 输入 | 用途 |
| --- | --- |
| [后端增补 BE01–BE10](../../../viewer/BACKEND_REQUIREMENTS_V1.md) | 六类增补与操作完整性 |
| [前端交互 v0.1](../../../viewer/MONITORING_INTERACTION_V1.md) | 推送后读取、完整版本切换、缓存及联调责任 |
| [批准设计 v1.0](../../DESIGN.md)、[批准契约](../../../../contracts/MONITORING_V1.md) | 计量、DES、分位数、模型配置和安全边界保持 |
| [已实现 API](../../../../contracts/MONITORING_IMPLEMENTED_API.md) | 兼容旧入口，不把提案当已实现 |
| [B005 闭环](../B005/RESULT.md)和[最终 E2E](../../../../../artifacts/validation/monitoring/B005/20261027T035327Z/report.json) | 开发基线 0.1.0.dev5 / schema2 |
| [输入摘要](INPUT_MANIFEST.json) | 两份提案、固定设计、所读源码及原测试证据身份 |
| [本批设计](DESIGN.md)、[共享接口草案](../../../../contracts/MONITORING_VIEW_V1_DRAFT.md) | 本批实现前须确认的增量设计 |
| [B006 归档](../../../../archive/monitoring/B006-backend-preparation-2026-10-27/README.md) | 原仅后端准备材料，退出当前交付路径 |

源码只读核对：storage.complete / enqueue / fail、pipeline.execute / recover、statistics.aggregate、service 查询、API 路由、编码落盘。已存在 groups 的全部三宽度直方图、facts 的 J/P/H/C/O、request_records 的原 JSON 和 encoded_requests.evidence_json。缺发布目录/事件日志/提交幂等/组合展示接口；现有 signals 无筛选分页。pipeline 文件时间范围使用 min/max(time_utc)，必须改按 time_ns 取边界。

保持公开固定资产、生产 DeepSeek 缺省 pending、GLM CP 映射未决等原边界。生产 CSV 不进入本机；每模型 5 appid 的固定种子泊松合成数据继续用于本机验证。单文件 <7200 秒预算覆盖新增展示预处理。不要读取整套 upstream 或改动 viewer 的设计/HTML/源码。

## 完成层级

B005 后端基线 → B005.1 后端增补验收 → 前端实际接入及完整服务联合验收 → 用户明确批准打包 → B006 重定交付范围并执行。B005.1 可先关闭后端子批，但联合验收未通过时，项目 V1 仍未完成、B006 仍 pending。


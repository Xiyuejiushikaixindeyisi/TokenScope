# 用户监控后端版本与上下文

2026-10-30。获批设计v1.0；本地开发身份u005-local-1；用户契约1.0.1，独立control schema1/index算法user-index-1。U000–U005全部closed，[最终报告](batches/U005/RESULT.md)为能力入口。

| 版本 | 状态 | 入口 |
| --- | --- | --- |
| v0.1 | 历史初稿归档 | [原文](../../../../achieve/2026-10-30/docs/tasks/monitoring/v2-user/DESIGN_v0.1.md) |
| 设计v1.0 | 用户认可，按batch实现 | [DESIGN](DESIGN.md) · [BATCH_PLAN](BATCH_PLAN.md) |
| 用户契约1.0.0 | U000初始契约/基线，执行记录保留 | [U000 RESULT](batches/U000/RESULT.md) |
| 用户契约1.0.1 | U005输入防护/计数正则勘误及错误/分页语义对齐；字段/公式/分组不变 | [契约](../../../contracts/user-monitoring-v2/README.md) |
| u005-local-1 | 本地后端实现及统一验证通过，MA真联合通过 | [实际API](IMPLEMENTED_API.md) · [源码证据清单](batches/U005/VALIDATION_MANIFEST.json) |

## 能力与验证边界

289全量测试通过，最终恢复竞争修复由15项定点回归补证；三模型真实编码/HTTP/CLI、重启、进程中断恢复、共享锁和MA隔离、资源预算通过。真实校准/前端/现场尚未验收。UI-01、V1/S0与原监控发布身份保持，不新增发布tag。

恢复阅读：AGENTS→CURRENT→SESSIONS→ENTRY→U005 RESULT/IMPLEMENTED_API；修改前再看DESIGN/对应batch。每个后续session先登记角色和当前阶段；无需重复启动已闭环开发，不能把维护入口当部署授权。

## 工作树身份

源码基线HEAD见VALIDATION_MANIFEST.json；本次新增源码用逐文件SHA256标识。共享工作树还包含MA/分析/前端其他会话改动；未擅自提交或push这些改动，也未将包体、CSV或模型资产纳入Git。共享app/CLI依赖当前MA实现，后续统一源码提交应一并核对依赖，不能单独截取装配文件造成缺模块。

V1发布monitoring-v1-20261028、包内源码92236ee993974e740d085e22e49b6b93c9487430保持；不是本地新功能HEAD。旧DOCUMENT_CHECK.json仅记录设计阶段文档检查；当前源码/验证身份见U005清单。

## 存储与回退

用户库独立，不修改旧control3/view1、S0 1.0.0。重建派生索引可调用UserRunService.rebuild，由worker执行；无facts需新分析。停止用户扩展可回退服务入口，保留用户控制库/情景/估算，不能删原封存。未来schema迁移先备份，不自动降级未知schema。

## 2026-10-30源码交接授权
用户本轮已明确授权提交及push；此前“未提交”描述是U005完成时点。当前交接提交由git log -- docs/tasks/monitoring/v2-user/GIT_HANDOFF_20261030.md定位；范围及已闭环MA依赖见[GIT_HANDOFF](GIT_HANDOFF_20261030.md)，前端入口见[FRONTEND_HANDOFF](FRONTEND_HANDOFF.md)。旧验收清单不回写为新commit身份。

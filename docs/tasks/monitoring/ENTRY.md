# Token监控：开发与交接入口

2026-10-27：**用户授权的真实前后端联合E2E与review已完成并暂停。** 最新入口：[联合报告](JOINT_RESULT_V1.md)。候选joint-v1-20261027为dev6/f006联合修正版，以SHA清单为准；166项后端、143项前端回归，3模型×5appid全量泊松30,168有效请求及浏览器/恢复/导出压力通过。S0/schema不变，B006打包pending，Docker/交付包未授权。

## 当前阅读顺序

| 优先级/用途 | 入口 |
| --- | --- |
| P0 恢复 | AGENTS→[CURRENT](../../../memory/CURRENT.md)→本页 |
| P1 后端结果/接入 | [B005.1 RESULT](batches/B005.1/RESULT.md)、[实际API](../../contracts/MONITORING_IMPLEMENTED_API.md)、[监控交接](../../../memory/handoffs/2026-10-27-monitoring-development.md) |
| P1 已批准基线 | [PLAN](batches/B005.1/PLAN.md)，必要附件[S0](batches/B005.1/S0_CONTRACT.md)、[TESTS](batches/B005.1/TESTS.md)；无需重新逐份审批 |
| P1 前端与联合 | [联合报告](JOINT_RESULT_V1.md)及其候选/测试清单为当前结果；前端自身批次入口保留历史 |
| P1 后续交付 | 联合通过后按[B006 PLAN](batches/B006/PLAN.md)提供具体候选并征得用户同意，再构建/容器验证/现场验收 |
| P2 实现依据 | [CODEMAP](CODEMAP.md)、B005.1 DESIGN/ISSUES/TESTS和[源码/证据总清单](../../../artifacts/validation/monitoring/B005.1/backend-acceptance.json) |
| P3 追溯 | [VERSIONS](VERSIONS.md)、旧批/研究/审批HTML与归档，不替代当前入口 |

协作、权威顺序及门槛：[统一工作流](../../architecture/TASK_SESSION_WORKFLOW.md)。后端通过≠联合通过≠容器通过≠现场通过。不代替前端会话修改进度、发消息、fork或委派。

## 保留边界

GLM/Qwen/V4普通链式DES，block=128/1536/32；Qwen/V4标近似，增强hybrid只占位。统一编码、计量和直方图由后端维护，GET只读已存成果。生产DeepSeek缺省思考、GLM CP映射、GF资产等价和V100现场性能仍未决。本机只有每模型5appid泊松合成数据，不索取绝密CSV。

[任务记忆](../../../memory/tasks/monitoring.md) · [实际会话](../../../memory/SESSIONS.md)


本机人工验收环境已按README构建并持续运行：http://127.0.0.1:8000；三模型×5appid合成结果已生成，等待用户人工确认。详情见README的本机人工验收环境。由用户另行决定是否进入Docker和交付包。

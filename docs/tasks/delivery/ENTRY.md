# 镜像打包和审查入口

当前：[监控V2审查通过与Git收口状态](MONITORING_V2_STATUS.md)。本轮闭环评审、修复交接和本地验收记录已[归档](../../../achieve/2026-10-31/monitoring-v2-review/README.md)，原始证据不移动。

**暂不打包；等待异常分析前后端完成验收后再按用户安排统一交付。** 本session负责统一审查、获授权后的Docker构建、镜像/代码包及执行prompt、版本配置摘要和本地backup管理；业务缺陷回对应前后端，不暗改契约或代用户验收。

## 当前阅读顺序

- [CURRENT](../../../memory/CURRENT.md)、[SESSIONS](../../../memory/SESSIONS.md)、[本线记忆](../../../memory/tasks/delivery.md)。
- [统一流程](../../architecture/TASK_SESSION_WORKFLOW.md)、[Git约定](../../operations/GIT_WORKFLOW.md)；无PR，backup仅本地，包体不上GitHub，含产物分支不合main。
- 后续候选按[异常分析入口](../analysis/ENTRY.md)、[监控前端入口](../viewer/monitoring-v2/ENTRY.md)及各后端入口核对范围与验收证据。

## 已发布V1与交付工具

monitoring-v1-20261028发布身份不变；[现场接收](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)、[B006结果](../monitoring/batches/B006/RESULT_20261028.md)、[审查](../monitoring/batches/B006/PREPACKAGE_REVIEW_20261028.md)、[B006计划](../monitoring/batches/B006/PLAN.md)。

[构建运行入口](../../../deploy/monitoring/README.md)、[发布脚本](../../../scripts/release/README.md)、[V1现场prompt](../../../prompts/delivery/HUAWEI_MONITORING_FULL_SERVICE.md)保留为工具和历史版本依据，不是V2部署指令。

已有交付目录：`C:\Users\ALIENWARE\Desktop\TokenScope-monitoring-v1-20261028`。WSL原产物指针、代码包/镜像/manifest及桌面prompt保持冻结，本轮未重新打包。现场启动验收和失败debug沿[监控维护入口](../monitoring/ENTRY.md)及当前MA分工。

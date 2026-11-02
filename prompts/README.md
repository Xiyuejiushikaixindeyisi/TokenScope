# Prompt入口

2026-11-01当前异常分析：[RV2统一审查与交付打包prompt](sessions/ANALYSIS_UNIFIED_REVIEW_DELIVERY_RV2.md)，由功能总负责准备供用户转交，尚未自动发送/启动新打包任务。两后端实际独立复审已通过，见[联合报告](../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/JOINT_VALIDATION_RV2_20261101.md)；下方“Token仅准备/未启动”是旧阶段。

2026-11-01 Token后端独立复审：[完整prompt](sessions/TOKEN_CONTENT_BACKEND_INDEPENDENT_REVIEW.md) · [候选与交接](../docs/tasks/length-analysis/INDEPENDENT_REVIEW_HANDOFF.md)。仅准备，未发送/启动；对齐当前T2–T4自动建议、公共AR-L5和前端UI-04，不打包部署。

异常分析前端接入：[启动prompt](sessions/ANOMALY_ANALYSIS_FRONTEND_START.md)已按2026-10-31实际后端交付更新；配套[公共/低命中前端交接](../docs/tasks/prefix-analysis/FRONTEND_HANDOFF.md)，其中对齐Token后端入口。供用户交给新会话，不自动创建或发送。

当前现场执行：[完整服务华为prompt](delivery/HUAWEI_MONITORING_FULL_SERVICE.md)，部署时使用随包冻结副本并核对manifest；维护仓库文本不覆盖已交付版本。

分析参考调研：[华为PrefixLens串行探测器与业务展示prompt](sessions/HUAWEI_PREFIXLENS_SERIAL_DETECTOR_RESEARCH.md)保留追溯；已接收用户回传报告，[来源与核对](../docs/research/implementations/PREFIXLENS_HUAWEI_REVIEW_2026-10-30.md)。仅参考，不替代部署prompt或本项目计量。

已完成的session启动、前后端交接、F007审查prompt已移至[achieve](../achieve/README.md)，不再作为新会话当前指令。新会话从[任务ENTRY](../docs/tasks/README.md)读取职责。agent目录仅用于产品自进化Agent，角色规划不自动启动工作。

2026-10-31异常分析产品已批，后端分线当前prompt：

- [低命中率后端主会话恢复](sessions/LOW_HIT_BACKEND_START.md)。
- [Token异常后端fork启动](sessions/TOKEN_ANOMALY_BACKEND_FORK_START.md)，仅用户明确允许且fork成功后发送执行。

[分线交接与许可状态](../docs/tasks/analysis/BACKEND_SPLIT_HANDOFF.md)。用户已明确允许并完成fork，Token线启动prompt已发送且实际身份已登记；不使用旧母会话prompt重新进行已完成的产品审批。

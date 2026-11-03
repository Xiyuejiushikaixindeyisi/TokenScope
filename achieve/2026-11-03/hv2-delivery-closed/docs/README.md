# 文档入口

2026-11-03最新阶段：异常公共层及四项后端已独立验收冻结，两前端接入完成，HV2-AF-01和HV2-MF-02已闭环；根339项前端、88项最终浏览器、135项鼠标核对及156资源重启一致性通过。源码版本整理/容器交付待继续，当前未发布本轮包体；现场真实数据仍待验。 下方执行日志和前序状态按时间追溯，以本段及当前入口为准。

2026-11-03当前：[HV2修复执行板](tasks/delivery/HV2_REPAIR_EXECUTION_20261103.md) · [独立验收](tasks/delivery/HV2_INDEPENDENT_ACCEPTANCE_20261103.md) · [六线总计划](tasks/delivery/V2_REPAIR_COORDINATION_PLAN_20261103.md)。华为新调查已收到，六线任务已实际派发。异常公共层、用户2.1.0和MA解释资源均已独立验收冻结；Token与低命中私有后端也已独立通过；两前端产品已冻结；根335项前端检查、第一阶段10项真实浏览器及156资源重启一致性通过，正在全新state执行旧功能/最终视觉回归。完整验收后按既有授权统一版本push、WSL构建与桌面交付；目前未发布本轮产品源码或包体。

[二次验收原件](huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md) · [调查原件](huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md) · [核对方案](huawei/HUAWEI_V2_REVIEW_AND_RESEARCH_PLAN_20261103.md)。原件只读，勘误和证据缺口见执行板。

2026-11-02已交付版本参考：[V2批准交付](tasks/delivery/V2_APPROVED_DELIVERY_20261102.md) · [华为真实数据两阶段执行prompt](../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md) · [固定规则](operations/DELIVERY_ACCEPTANCE_RULES.md) · [闭环归档](../achieve/2026-11-02/v2-approved-delivery/README.md)。UIR-03由用户留V3，不是V2阻断；旧记录只作历史。

完整服务总负责已按2026-11-01用户决定交回镜像打包与审查会话，负责华为启动/完整验收及归口修复协调；[职责交接](tasks/analysis/ONSITE_COORDINATION_HANDOFF_20261101.md)。现场范围包括Token监控V2（用户监控、MA、搜索等）和两类异常。异常前端转为维护支持；原[RV2本机统筹](../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/COORDINATION_RV2.md)与[AF归档](../achieve/2026-11-01/analysis-rv2/README.md)保留历史依据。

本机历史监控V2评审与修复已闭环并归档（不代表本次现场通过）：[当前状态](tasks/delivery/MONITORING_V2_STATUS.md)。2026-11-01用户认可异常分析L4/L5展示，已授权[统一审查、修复复验后完整服务打包交付](../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/UNIFIED_REVIEW_DELIVERY_EXECUTION_20261101.md)。

2026-10-30整理：当前入口与已闭环记录分开；新分线角色、状态及阅读优先级见[任务索引](tasks/README.md)与[实际登记](../memory/SESSIONS.md)。

| 优先级 | 阅读入口 |
| --- | --- |
| P0恢复 | [AGENTS](../AGENTS.md) → [CURRENT](../memory/CURRENT.md) → [SESSIONS](../memory/SESSIONS.md) → [自己的任务ENTRY](tasks/README.md) |
| P1当前工作 | 当前设计/有效契约/具体批次、相关源码和测试；不全量读历史 |
| P2依据 | 被当前问题引用的研究、来源锁、现场证据及验证报告 |
| P3追溯 | [achieve归档](../achieve/README.md)、[旧archive索引](archive/README.md) |

监控dev6/F007已完成本机审查、容器和桌面交付：[交付结果](tasks/monitoring/batches/B006/RESULT_20261028.md)。后端负责华为启动验收与失败修复，打包session负责交付管理；2026-10-30用户确认前后端V1通过，见[现场验收与分析交接](huawei/MONITORING_V1_ACCEPTANCE_20261030.md)；异常分析产品v0.4已审批，主会话承接低命中后端，Token异常线已获用户许可fork并启动，见[分线交接](tasks/analysis/BACKEND_SPLIT_HANDOFF.md)。

- [总设计](tasks/product/ENTRY.md)：产品形态、边界、分工，当前休眠。
- [监控V1](tasks/monitoring/ENTRY.md)：休眠，已交付源码/契约基线；V2两线并行：[用户功能](tasks/monitoring/v2-user/ENTRY.md)、[MA监控](tasks/monitoring/v2-ma/ENTRY.md)。
- [前端交接](tasks/viewer/ENTRY.md)：V1会话休眠，UI-01及两个前端prompt；[异常分析已批产品](tasks/analysis/ENTRY.md)与两线后端交接入口。
- [本轮版本检查点](operations/V2_HANDOFF_20261030.md)：仅文档/DEMO交接，V1发布身份不变。
- [V2总设计与交付](tasks/delivery/ENTRY.md)：六线任务规划分配、独立审查/E2E、构建/包体、文档记忆、版本push与现场prompt；不唤醒休眠的历史全项目总设计。
- [工作流](architecture/TASK_SESSION_WORKFLOW.md)、[目录约定](architecture/WORKSPACE_LAYOUT.md)、[一期目标](requirements/V1_SCOPE.md)、[Git流程](operations/GIT_WORKFLOW.md)。

requirements管目标，architecture管边界，contracts管接口，tasks管当前任务与仍有效设计，huawei管现场结论，research管依据，operations管运行，sharing管分享。achieve保存本次关闭批次/旧prompt/历史记忆；docs/archive的旧冻结快照继续原位保留。原始证据不改写，历史测试只证明对应版本，不等于当前授权或现场通过。

# 文档入口

2026-10-30整理：当前入口与已闭环记录分开；新分线角色、状态及阅读优先级见[任务索引](tasks/README.md)与[实际登记](../memory/SESSIONS.md)。

| 优先级 | 阅读入口 |
| --- | --- |
| P0恢复 | [AGENTS](../AGENTS.md) → [CURRENT](../memory/CURRENT.md) → [SESSIONS](../memory/SESSIONS.md) → [自己的任务ENTRY](tasks/README.md) |
| P1当前工作 | 当前设计/有效契约/具体批次、相关源码和测试；不全量读历史 |
| P2依据 | 被当前问题引用的研究、来源锁、现场证据及验证报告 |
| P3追溯 | [achieve归档](../achieve/README.md)、[旧archive索引](archive/README.md) |

监控dev6/F007已完成本机审查、容器和桌面交付：[交付结果](tasks/monitoring/batches/B006/RESULT_20261028.md)。后端负责华为启动验收与失败修复，打包session负责交付管理；2026-10-30用户确认前后端V1通过，见[现场验收与分析交接](huawei/MONITORING_V1_ACCEPTANCE_20261030.md)；异常分析现改为先母会话调研/产品设计，再fork两线。

- [总设计](tasks/product/ENTRY.md)：产品形态、边界、分工，当前休眠。
- [监控V1](tasks/monitoring/ENTRY.md)：休眠，已交付源码/契约基线；V2两线并行：[用户功能](tasks/monitoring/v2-user/ENTRY.md)、[MA监控](tasks/monitoring/v2-ma/ENTRY.md)。
- [前端交接](tasks/viewer/ENTRY.md)：V1会话休眠，UI-01及两个前端prompt；[异常分析母会话](tasks/analysis/ENTRY.md)先调研/产品设计。
- [本轮版本检查点](operations/V2_HANDOFF_20261030.md)：仅文档/DEMO交接，V1发布身份不变。
- [审查打包](tasks/delivery/ENTRY.md)：审查、构建、包体、版本和执行prompt。
- [工作流](architecture/TASK_SESSION_WORKFLOW.md)、[目录约定](architecture/WORKSPACE_LAYOUT.md)、[一期目标](requirements/V1_SCOPE.md)、[Git流程](operations/GIT_WORKFLOW.md)。

requirements管目标，architecture管边界，contracts管接口，tasks管当前任务与仍有效设计，huawei管现场结论，research管依据，operations管运行，sharing管分享。achieve保存本次关闭批次/旧prompt/历史记忆；docs/archive的旧冻结快照继续原位保留。原始证据不改写，历史测试只证明对应版本，不等于当前授权或现场通过。

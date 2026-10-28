# 文档入口

2026-10-28整理：当前入口与已闭环记录分开；四个现有session见[任务索引](tasks/README.md)与[实际登记](../memory/SESSIONS.md)。

| 优先级 | 阅读入口 |
| --- | --- |
| P0恢复 | [AGENTS](../AGENTS.md) → [CURRENT](../memory/CURRENT.md) → [自己的任务ENTRY](tasks/README.md) |
| P1当前工作 | 当前设计/有效契约/具体批次、相关源码和测试；不全量读历史 |
| P2依据 | 被当前问题引用的研究、来源锁、现场证据及验证报告 |
| P3追溯 | [achieve归档](../achieve/README.md)、[旧archive索引](archive/README.md) |

监控dev6/F007已完成本机审查、容器和桌面交付：[交付结果](tasks/monitoring/batches/B006/RESULT_20261028.md)。后端负责华为启动验收与失败修复，打包session负责交付管理；现场验收仍未完成。

- [总设计](tasks/product/ENTRY.md)：产品形态、边界、分工，当前休眠。
- [监控后端](tasks/monitoring/ENTRY.md)：源码/契约及现场验收。
- [前端](tasks/viewer/ENTRY.md)：监控维护及未来两类分析界面/HTML参考。
- [审查打包](tasks/delivery/ENTRY.md)：审查、构建、包体、版本和执行prompt。
- [工作流](architecture/TASK_SESSION_WORKFLOW.md)、[目录约定](architecture/WORKSPACE_LAYOUT.md)、[一期目标](requirements/V1_SCOPE.md)、[Git流程](operations/GIT_WORKFLOW.md)。

requirements管目标，architecture管边界，contracts管接口，tasks管当前任务与仍有效设计，huawei管现场结论，research管依据，operations管运行，sharing管分享。achieve保存本次关闭批次/旧prompt/历史记忆；docs/archive的旧冻结快照继续原位保留。原始证据不改写，历史测试只证明对应版本，不等于当前授权或现场通过。

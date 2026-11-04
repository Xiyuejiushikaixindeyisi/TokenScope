# 文档入口

2026-11-04：新增[V3调研与产品设计](tasks/product-v3/ENTRY.md)，用户七项观察已形成[研究任务书](tasks/product-v3/RESEARCH_BRIEF_20261104.md)。不等华为报告即启动，报告后补高优先级证据；本轮不实施产品代码。镜像打包与审查负责跨版本迭代/独立验收/debug/交付，身份见[SESSIONS](../memory/SESSIONS.md)。

2026-11-03：HV2修复已完成公共层→依赖后端独立验收及冻结→前端→源码与容器独立验收→WSL打包和桌面全SHA交付。源码 `c1345b6fd7d413a94420642ca1b4099b9ec104b4` 已push main；版本 `tokenscope-v2-hv2-20261103`。现场真实数据及用户两阶段验收待执行，六线开发窗口关闭。 [交付结果](tasks/delivery/HV2_DELIVERY_20261103.md) · [现场执行prompt](../prompts/delivery/HUAWEI_V2_HV2_REAL_DATA_20261103.md)。本机通过不代签华为现场。

恢复顺序： [AGENTS](../AGENTS.md) → [CURRENT](../memory/CURRENT.md) → [SESSIONS](../memory/SESSIONS.md) → [自己的任务入口](tasks/README.md)。按问题读取有效契约/源码/实际证据，不全量重跑历史任务。

- [镜像打包与审查](tasks/delivery/ENTRY.md)：跨版本迭代、独立验收、版本级debug、版本/构建/包体、归档与现场问题归口。
- [V3调研与产品设计](tasks/product-v3/ENTRY.md)：场景/优化空间、SLO建议、行为分组与路由、真实压测、数据质量；[华为补充取证](../prompts/delivery/HUAWEI_V3_EVIDENCE_APPENDIX_20261104.md)并入唯一报告。
- [用户监控后端](tasks/monitoring/v2-user/ENTRY.md)、[MA后端](tasks/monitoring/v2-ma/ENTRY.md)、[监控前端](tasks/viewer/monitoring-v2/ENTRY.md)。
- [异常公共层/低命中后端](tasks/prefix-analysis/ENTRY.md)、[Token后端](tasks/length-analysis/ENTRY.md)、[异常前端](tasks/viewer/analysis/ENTRY.md)。
- [华为报告与环境](huawei/README.md)：原验收与调查只读；当前版本下一轮现场待验。
- [工作流](architecture/TASK_SESSION_WORKFLOW.md)、[交付规则](operations/DELIVERY_ACCEPTANCE_RULES.md)、[Git约定](operations/GIT_WORKFLOW.md)、[长期教训](../memory/DELIVERY_LESSONS.md)。
- 历史全项目[总设计](tasks/product/ENTRY.md)、[V1后端](tasks/monitoring/ENTRY.md)、[V1前端](tasks/viewer/ENTRY.md)保持休眠。
- [归档总索引](../achieve/README.md)、[本轮闭环记录](../achieve/2026-11-03/hv2-delivery-closed/README.md)、[旧归档](archive/README.md)。原始证据、冻结契约、批准HTML和发布包不改写。

requirements管目标，architecture管边界，contracts管接口，tasks管有效设计与维护，huawei管现场结论，research管依据，operations管运行。旧入口快照已归档，不能把历史“待接入/未打包”当当前指令。

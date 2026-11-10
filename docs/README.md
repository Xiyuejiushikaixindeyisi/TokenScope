# 文档入口

2026-11-10：V3聚焦低命中四项P0，**全新开发角色先独立check，待Token探索回传后细化实施**；Token修复留V3.5。当前范围以[最新分工与交接](tasks/product-v3/V3_SCOPE_AND_HANDOFF_20261110.md)为准。V2发布事实仍查[阶段收口](tasks/delivery/HV2_ACCEPTANCE_CLOSE_20261105.md)和[交付身份](tasks/delivery/HV2_DELIVERY_20261103.md)。

恢复顺序：[AGENTS](../AGENTS.md) → [CURRENT](../memory/CURRENT.md) → [SESSIONS](../memory/SESSIONS.md) → [本线任务入口](tasks/README.md)。按问题读实际证据、源码与契约，不全量恢复历史任务。

- [全新V3代码修复与开发](tasks/development-v3/ENTRY.md)：角色预登记/实际ID未知；含最小文档、源码、测试清单和[启动消息](tasks/development-v3/START_PROMPT_20261110.md)。未来统一承担获准开发和验证，当前只读check。
- [镜像打包与审查](tasks/delivery/ENTRY.md)：V3仅打包与审批，不承担开发/debug/开发调度或开发验收执行。
- [V3研究与产品宣传](tasks/product-v3/ENTRY.md)：证据核对、方案与交接；[三组Token长尾探索prompt](tasks/product-v3/HUAWEI_TOKEN_TAIL_EXPLORATION_PROMPT_20261110.md)。[四象限明细HTML](tasks/product-v3/promotion/quadrant-detail/dist/index.html)是高优先级负载资料。
- [用户后端](tasks/monitoring/v2-user/ENTRY.md)、[MA后端](tasks/monitoring/v2-ma/ENTRY.md)、[监控前端](tasks/viewer/monitoring-v2/ENTRY.md)。
- [V2异常公共/低命中](tasks/prefix-analysis/ENTRY.md)、[Token后端](tasks/length-analysis/ENTRY.md)、[异常前端](tasks/viewer/analysis/ENTRY.md)：历史实现参考，六线休眠；V3公共层统一交新开发角色，Token规则本版不开发。
- [华为证据索引](huawei/README.md)：新原件、日期固定副本、历史原件与核对记录分开。
- [协作流程](architecture/TASK_SESSION_WORKFLOW.md)、[交付规则](operations/DELIVERY_ACCEPTANCE_RULES.md)、[Git约定](operations/GIT_WORKFLOW.md)、[长期教训](../memory/DELIVERY_LESSONS.md)。
- [历史总设计](tasks/product/ENTRY.md)、[V1后端](tasks/monitoring/ENTRY.md)、[V1前端](tasks/viewer/ENTRY.md)休眠。
- [归档总索引](../achieve/README.md)、[本轮归档](../achieve/2026-11-05/hv2-acceptance-close/README.md)。原始证据、冻结契约、批准HTML与发布包不改写。

requirements管目标，architecture管边界，contracts管接口，tasks管有效设计与维护，huawei管现场回传，research管研究依据，operations管运行。当前用户决定、对应版本证据与设计目标分开表达。

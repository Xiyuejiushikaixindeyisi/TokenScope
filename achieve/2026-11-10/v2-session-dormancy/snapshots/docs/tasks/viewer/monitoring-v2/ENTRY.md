# Token监控V2前端维护入口

2026-11-05：用户暂时接受V2，产品宣传优先；[现场核对与保留问题](../../delivery/HV2_ACCEPTANCE_CLOSE_20261105.md)为当前版本状态。本线HV2源码窗口关闭，不自动修复/重构/复测。V3先真实业务场景、定位与功能取舍及32GiB资源约束讨论；后续有新定向任务再恢复。以下保留对应版本维护资料，旧“待验/未打包”等不覆盖本段。

P0：AGENTS→CURRENT→SESSIONS→本入口；当前维护优先读取[监控前端最终交接](HV2_MONITOR_FRONTEND_HANDOFF_20261103.md)及[MA接入](HV2_MA_FRONTEND_HANDOFF_20261103.md)。HV2-MF-02已独立复验；四入口/UI02及L4/L5保持，UIR-03留V3。

本线职责及ID保持，后续现场问题由镜像打包与审查会话按新任务定向协调；不自行重跑旧派发prompt或改变批准展示。旧阶段/候选回执已[完整归档](../../../../achieve/2026-11-03/hv2-delivery-closed/docs/tasks/viewer/monitoring-v2/ENTRY.md)。以下为版本化维护材料，历史批次状态不覆盖本段。
## 职责与范围

- 承接用户监控增强、搜索排行、P90长度请求所需参考前缀命中率，以及独立MA监控页面；两条后端并行，本前端分别消费其权威结果。
- 用户侧为GB的appid×common_name；MA侧为GF的model_standard_name×instance_uuid，选择规格后全部UUID直接可见，同UUID跨appid/P共享。两种范围、指标与缓存身份不能混用。
- 负责展示/交互、apps/viewer内增量实现、契约消费记录、前端测试和独立视觉验收。沿用UI-01及后续获批HTML的页面骨架、布局、配色与信息密度，不另建应用或数据层。
- 后端维护算法、采集/回放、计量、性能情景及契约；异常分析页面归另一前端会话。hybrid、自进化Agent、自动采集、部署和打包不在本线范围。

## 有效维护依据

- [正式交互方案](INTERACTION_V2.md)、[源码与复现地图](CODEMAP.md)、[实施计划](BATCH_PLAN.md)、[F006结果](batches/MV2-F006/RESULT.md)和[测试](batches/MV2-F006/TESTS.md)。批次结果是历史验证，修复后的最终身份以独立复审记录为准。
- [用户监控入口](../../monitoring/v2-user/ENTRY.md)、[用户2.1.0契约](../../../contracts/user-monitoring-v2/2.1.0/README.md)、[MA入口](../../monitoring/v2-ma/ENTRY.md)、[MA协议](../../../contracts/ma-monitoring-v2/CONTRACT.md)、[冻结S0](../../monitoring/batches/B005.1/S0_CONTRACT.md)。当前候选消费用户2.1.0（保留旧9操作兼容）、MA1.0.0及新增availability、S0；具体变化以HV2总交接为准。
- [UI-02](prototypes/tokenscope-v2-demo-ui02.html)、[视觉记录](PROTOTYPE_UI_02.md)、[校准清单](../../monitoring/v2-user/PERFORMANCE_CALIBRATION.md)。原型不代替正式代码/现场验证。
- [本线记忆](../../../../memory/tasks/viewer-monitoring-v2.md)、[会话登记](../../../../memory/SESSIONS.md)、[协作流程](../../../architecture/TASK_SESSION_WORKFLOW.md)。前端维护职责不因文档归档改变；异常分析前端由其独立入口承接。

历史本地验收地址/PID仅存档；需要重启时按项目[README](../../../../README.md)和源码地图核实当前版本，不假定旧服务仍有效。

# Token监控V2前端维护入口

2026-11-02 UIR-01鼠标单项修复完成自测，候选viewer-uir01-pointer-fix-20261102-c1；[交接](UIR01_POINTER_FIX_HANDOFF_20261102.md)。仅用SVG实际screen CTM逆变换修正指针，布局/后端不变。226单元组件、85不同浏览器用例、144真实圆点检查通过；c2负向2项按预期失败；118地址重启一致，重启7项通过。原18项/UIR-02/排行/L4L5/T2–T4保持，窗口释放交审查会话独立复审，未提交/push/打包，不代用户认可。实际session 01a19111-344a-75c1-84e0-14db8be08f4f。

2026-11-02 UIR-01/02补充修复已完成自测，候选 viewer-approved-ui-review-fixes-20261102-c2；[补充交接](APPROVED_UI_REVIEW_FIX_HANDOFF_20261102.md)。恢复降序读数与不改路由的键盘跳转，另修最近运行覆盖排行路由；222单元组件、81不同浏览器用例、118地址重启通过，重启后13项复测通过。原18项/四入口/L4-L5/T2-T4及后端契约保持。前端窗口释放，交镜像打包与审查独立复审，未提交/合并/push/打包，不代签用户视觉认可。实际session仍01a19111-344a-75c1-84e0-14db8be08f4f。

2026-11-02 已批准 UI 恢复自测交接：[统一交接](APPROVED_UI_RESTORATION_HANDOFF_20261102.md)。215单元/组件、71不同浏览器用例通过，111地址重启摘要一致；18项有逐项依据。唯一候选4191，未提交/push/打包，待审查方重新冷启动独立复审，不代签用户视觉验收。

更新：2026-10-31。正式用户/MA页面已获用户验收，RV2-01/02/03修复已通过独立源码及Docker复审，源码与文档检查点已推送main。见[当前审查状态](../../delivery/MONITORING_V2_STATUS.md)。本轮旧评审/修复交接已[归档](../../../../achieve/2026-10-31/monitoring-v2-review/README.md)，不是待执行任务。

暂不交付打包，等待异常分析前后端完成验收后统一交付。监控TTFT为“代码完成，性能校准待完成”；不将合成参数或截图当真实校准证据。

## 职责与范围

- 承接用户监控增强、搜索排行、P90长度请求所需参考前缀命中率，以及独立MA监控页面；两条后端并行，本前端分别消费其权威结果。
- 用户侧为GB的appid×common_name；MA侧为GF的model_standard_name×instance_uuid，选择规格后全部UUID直接可见，同UUID跨appid/P共享。两种范围、指标与缓存身份不能混用。
- 负责展示/交互、apps/viewer内增量实现、契约消费记录、前端测试和独立视觉验收。沿用UI-01及后续获批HTML的页面骨架、布局、配色与信息密度，不另建应用或数据层。
- 后端维护算法、采集/回放、计量、性能情景及契约；异常分析页面归另一前端会话。hybrid、自进化Agent、自动采集、部署和打包不在本线范围。

## 有效维护依据

- [正式交互方案](INTERACTION_V2.md)、[源码与复现地图](CODEMAP.md)、[实施计划](BATCH_PLAN.md)、[F006结果](batches/MV2-F006/RESULT.md)和[测试](batches/MV2-F006/TESTS.md)。批次结果是历史验证，修复后的最终身份以独立复审记录为准。
- [用户监控入口](../../monitoring/v2-user/ENTRY.md)、[用户契约](../../../contracts/user-monitoring-v2/README.md)、[MA入口](../../monitoring/v2-ma/ENTRY.md)、[MA协议](../../../contracts/ma-monitoring-v2/CONTRACT.md)、[冻结S0](../../monitoring/batches/B005.1/S0_CONTRACT.md)。当前消费用户2.0.0/MA1.0.0及S0。
- [UI-02](prototypes/tokenscope-v2-demo-ui02.html)、[视觉记录](PROTOTYPE_UI_02.md)、[校准清单](../../monitoring/v2-user/PERFORMANCE_CALIBRATION.md)。原型不代替正式代码/现场验证。
- [本线记忆](../../../../memory/tasks/viewer-monitoring-v2.md)、[会话登记](../../../../memory/SESSIONS.md)、[协作流程](../../../architecture/TASK_SESSION_WORKFLOW.md)。前端维护职责不因文档归档改变；异常分析前端由其独立入口承接。

历史本地验收地址/PID仅存档；需要重启时按项目[README](../../../../README.md)和源码地图核实当前版本，不假定旧服务仍有效。

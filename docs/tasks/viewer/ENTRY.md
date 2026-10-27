# 前端展示任务入口

2026-10-27：**F001–F006 closed，前端0.1.0-f006 / ready_for_joint，完整前端提交用户审批；可进入后端主持的最终端到端验收。** 不是release_ready，Docker与交付包未授权。

当前入口：[F006结果](batches/F006/RESULT.md) → [测试记录](batches/F006/TESTS.md) → [后端联合交接](handoffs/FRONTEND_READY_FOR_JOINT.md)。[批准设计](MONITORING_INTERACTION_V1.md)、[审批记录](APPROVAL.md)、[验收矩阵](ACCEPTANCE_V1.md)、[源码地图](CODEMAP.md)、[批次索引](batches/README.md)。实际源码apps/viewer；原型HTML仅保留视觉追溯，不是正式服务。

P0：AGENTS、memory/CURRENT、本入口。P1：本次修改涉及的批次与设计章节、固定后端S0及相关源码/测试；不全量读历史研究。

职责：本fork维护前端代码/设计/测试/记忆；只消费监控后端契约，不实现计量或诊断算法。最终真实J01–J06/R1/R2、Docker/镜像/代码交付由后端Session 1统一负责，打包须用户另行同意。两类分析交互延后，已批准报告HTML只是参考。

执行约定：按MONITORING_INTERACTION_V1.md逐batch实现→验证/测试→达到门槛→闭环记录和增量记忆；agent自行决定下一batch，完整前端后交用户审批。只有无法解决、改变总方案、增加未约定组件或类、涉及后端契约变更的重大问题才暂停讨论；普通缺陷和测试失败自主修复，不反复停止、不擅改契约。

用户批准内存修订：64MiB优化、256MiB导出增量验收上限；两规模重复测量，正确性和应用缓冲限制不变，见设计9.4与F005记录。

[前端记忆](../../../memory/tasks/viewer.md) · [实际会话登记](../../../memory/SESSIONS.md) · [构建入口](../../../apps/viewer/README.md)

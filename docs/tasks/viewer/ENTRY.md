# 前端展示任务入口

2026-10-28：**F007（0.1.0-f007）用户人工验收通过，batch closed。后端或新session的打包前统一审查待执行。** Docker与交付包未授权。

当前入口：[F007最终修改方案](batches/F007/PLAN.md) → [测试](batches/F007/TESTS.md) → [独立视觉验收](batches/F007/VISUAL_ACCEPTANCE.md) → [闭环/后端审查入口](batches/F007/RESULT.md)。审批HTML是本批唯一视觉基准，不再仅作为配色参考。功能交互继续遵循[批准设计](MONITORING_INTERACTION_V1.md)和S0。[批次索引](batches/README.md) · [审批记录](APPROVAL.md) · [源码地图](CODEMAP.md)。历史F001–F006及[联合结果](../monitoring/JOINT_RESULT_V1.md)保留。

纯展示修复由前端回归和用户人工视觉验收，不主动重复完整联合review；后端在Docker构建/镜像打包前统一阅读代码、闭环、设计文档验收。两项独立记录，打包仍需单独同意。

P0：AGENTS、memory/CURRENT、本入口。P1：本次修改涉及的批次与设计章节、固定后端S0及相关源码/测试；不全量读历史研究。

职责：本fork维护前端代码/设计/测试/记忆；只消费监控后端契约，不实现计量或诊断算法。最终真实J01–J06/R1/R2、Docker/镜像/代码交付由后端Session 1统一负责，打包须用户另行同意。两类分析交互延后，已批准报告HTML只是参考。

执行约定：按MONITORING_INTERACTION_V1.md逐batch实现→验证/测试→达到门槛→闭环记录和增量记忆；agent自行决定下一batch，完整前端后交用户审批。只有无法解决、改变总方案、增加未约定组件或类、涉及后端契约变更的重大问题才暂停讨论；普通缺陷和测试失败自主修复，不反复停止、不擅改契约。

用户批准内存修订：64MiB优化、256MiB导出增量验收上限；两规模重复测量，正确性和应用缓冲限制不变，见设计9.4与F005记录。

[前端记忆](../../../memory/tasks/viewer.md) · [实际会话登记](../../../memory/SESSIONS.md) · [构建入口](../../../apps/viewer/README.md)

人工验收HTTP：http://127.0.0.1:8000/#/overview （刷新读取当前构建）。后续审查/打包可由用户另建session执行，交接prompt见prompts/sessions/SESSION_FRONTEND_REVIEW_AND_PACKAGING.md；本会话未创建。

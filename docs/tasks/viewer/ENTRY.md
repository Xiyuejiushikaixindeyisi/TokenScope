# TokenScope前端设计开发入口

2026-10-28：Token监控F007（0.1.0-f007）已获用户人工验收，打包前审查和本机容器交付也已完成。当前维护监控前端；后续继续负责低命中率分析、Token异常分析的前端设计与开发。两个分析器的结果/证据契约需与对应新session共同确认，已有HTML demo不等于正式分析实现。

## 当前阅读顺序

- P0：[当前状态](../../../memory/CURRENT.md)、[分工](../../../memory/SESSIONS.md)。
- P1监控维护：[批准交互设计](MONITORING_INTERACTION_V1.md)、[源码地图](CODEMAP.md)、[验收门槛](ACCEPTANCE_V1.md)、[固定S0](../monitoring/batches/B005.1/S0_CONTRACT.md)。
- P1分析界面：[分析报告展示设计起点](DESIGN.md)、[两类分析HTML demo](../../../artifacts/prototypes/monitoring-v1/tokenscope-monitoring-with-reports-v2.html)、[原型来源与入口](CODEMAP.md)，再读[低命中分析](../prefix-analysis/ENTRY.md)或[Token异常分析](../length-analysis/ENTRY.md)的当前设计/契约。
- P2已完成证据：[F007结果](../../../achieve/2026-10-28/docs/tasks/viewer/batches/F007/RESULT.md)、[视觉验收](../../../achieve/2026-10-28/docs/tasks/viewer/batches/F007/VISUAL_ACCEPTANCE.md)、[联合结果](../monitoring/JOINT_RESULT_V1.md)、[交付结果](../monitoring/batches/B006/RESULT_20261028.md)。
- P3：[闭环批次索引](batches/README.md)、[审批历史](APPROVAL.md)。

职责：apps/viewer、前端设计/测试/记忆；前端只消费已有结果，不在页面访问时运行编码、理想命中计算或诊断。分析session维护算法和结果/证据契约，前端维护展示和交互，不把合成HTML数据当真实后端能力。

后端负责现场服务启动验收/失败排查；打包session负责统一审查及授权后的交付。前端提供可复现构建/资源/锁/测试和回退，修复自身问题。重大目标/接口/验收变化与用户讨论；授权内普通缺陷和测试失败自行修复复测，不降低门槛。当前导出仍按64MiB优化目标、256MiB验收上限及已批准的重复大文件测量要求，不因归档改变。

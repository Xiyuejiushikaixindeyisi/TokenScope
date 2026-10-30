# Token监控后端设计开发入口

2026-10-28：后端dev6/schema3/view1、前后端联合已完成，F007与统一交付已完成本机验收。**本session负责华为实验机服务能否拉起的验收，以及运行/大文件分析故障的debug、修复和复测。现场回传尚未收到，不能宣布现场通过。**

## 当前阅读顺序

| 用途 | 入口 |
| --- | --- |
| P0恢复 | [CURRENT](../../../memory/CURRENT.md)、[SESSIONS](../../../memory/SESSIONS.md) |
| P1现场启动验收 | [本轮交付结果](batches/B006/RESULT_20261028.md)、[完整服务执行prompt](../../../prompts/delivery/HUAWEI_MONITORING_FULL_SERVICE.md)、[部署说明](../../../deploy/monitoring/README.md)、[V100事实核对](../../huawei/README.md) |
| P1定位修复 | [CODEMAP](CODEMAP.md)、[实际API](../../contracts/MONITORING_IMPLEMENTED_API.md)、[当前计量设计](DESIGN.md)、[B005.1技术设计](batches/B005.1/DESIGN.md)、[固定S0](batches/B005.1/S0_CONTRACT.md)、[验证门槛](batches/B005.1/TESTS.md) |
| P2本机结果 | [联合报告](JOINT_RESULT_V1.md)、[B005.1闭环](../../../achieve/2026-10-28/docs/tasks/monitoring/batches/B005.1/RESULT.md)、[B006](batches/B006/PLAN.md) |
| P3历史 | [已关闭批次](batches/README.md)、[achieve](../../../achieve/README.md) |

收到现场脱敏报告后先核对release_id/source_commit/image_id、摘要、实际内核/架构/Docker/Compose/端口/权限/挂载和日志；区分包损坏、环境/启动、后端业务和前端问题。按影响范围本地复现并修复后端，保留失败与复测证据；前端问题转其维护范围，镜像/Compose/重新交付与[打包session](../delivery/ENTRY.md)对接。本轮分工不等于已连接现场机器或已执行远程操作。

现场预检和启动成功只是一层；合成功能、持久化恢复、浏览器能力及真实CSV性能分别留证，缺项写未执行，不关闭B006 P5。现场原件按[华为文档规则](../../huawei/README.md)保存，不能回传真实请求正文/CSV。

维护监控后端、统一编码/计量/理想命中计算与公共契约。GET只读成果，诊断复用同一实现。DeepSeek缺省思考、GLM CP映射、GF资产等价和V100真实数据性能仍未决。修复后由打包session统一审查，新的构建/包体须有效明确授权；不用日常Docker重建代替开发测试。

## 2026-10-28 真实大文件现场阶段

用户确认前端修复、端到端验证和Docker打包完成；下一步华为Agent分析三份真实CSV（Qwen约19.8GB、DeepSeek约4.5GB、GLM约1.7GB）。[大文件首跑及单文档故障回传prompt](../../../prompts/sessions/HUAWEI_MONITORING_LARGE_CSV_DEBUG.md)补充已交付prompt，未改发布包。SQL按request_time筛选2026-10-20 07:00–09:00；UTC前提下对应北京时间15:00–17:00，回放字段model_handle_start_time与筛选字段不同。每文件两小时及资源能力待现场验证。

本session收到嵌入源码/复现/脱敏证据的单份md后，负责修复、回归、patch及应用/回退说明；稳定后交打包session重新交付，仍遵循授权流程。本轮未改业务代码、未重包、未进行现场操作。

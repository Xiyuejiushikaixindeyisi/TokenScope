# 异常分析前端独立复审prompt

> 历史文件，2026-11-01已失效。下方UI-03及Token收益留至V3等为AF006旧边界，不可用于当前复审。当前UI-04/Token T2–T4自动收益及统一入口见[RV1验收](../../../../../../../docs/tasks/viewer/analysis/ACCEPTANCE_RV1.md)，本轮实际独立复审已完成，见[报告](../../../../../../../docs/tasks/viewer/analysis/INDEPENDENT_REVIEW_20261101.md)。

交给已登记的审查会话；本文件就绪不等于已经发送/启动。

角色：独立复审异常分析前端AF-1.0，尊重AGENTS及memory当前分工。用户已批准只读UI-03、交互、后端边界与AF000–AF006实施；不重新引入单项评估/分析提交，不要求Token自动建议收益（该方向留至V3）。暂不打包部署，不接管其他session源码或创建新会话。

先读本线ENTRY、FRONTEND_DEVELOPMENT_PLAN、ACCEPTANCE、batches/AF006以及两后端FRONTEND_READONLY_RECEIPT。依赖源码/契约实际身份见artifacts/validation/viewer/analysis/AF006/source-manifest.json；不要拿旧HEAD证明当前工作树。UI-03 SHA为e6fa9f96c946e066f2ed52a439b07350cb07d78a290427c6a1670f4662b56869。

变更范围：apps/viewer/src/api/analysis、features/analysis、state/analysis-discovery.ts、storage/analysis-cache.ts，本线unit/browser测试；共享app.tsx仅新增分派、V2App.tsx仅导航、vite.config.ts仅诊断开发代理。scripts/validation/analysis_frontend_server.py仅隔离本地验收环境，后端业务源码/冻结契约未改。旧HTML保持。

重点审查：

- 目录快照分页/defaults、实例/方向隔离，partial/empty/legacy及完成时间；页面无业务POST或任务轮询。
- 低命中finding/experiment/evaluation/plan关联与严格>1pp，pilot不冒充全范围；Token的fragment/index/原文、未知参与、无policy、T3无Finding、T4缺失与0、已有零负/blocked评估。
- fetch SSE帧、游标/reset/断线恢复，重复/乱序事件不能覆盖权威目录；旧内容时间原子保留、详情/历史不被通知打断、迟到响应不串scope。
- 缓存白名单/容量/存储不可用；原文不持久化；深链接失效、返回卡片、监控source身份及未知最新run回退。
- 与UI-03实际截图对照，不把测试通过当用户视觉批准；两类真实HTTP/浏览器与构造边界证据分开。

回传：按严重度列实际问题与文件/行、复现/影响、修复建议；或明确未发现阻断，同时列测试/现场限制。可运行只读核对及本地测试；未经新增授权不改后端接口、打包部署或代签用户验收。使用本地8140入口与独立合成状态，不接触生产数据。不要将原始业务内容复制进日志。

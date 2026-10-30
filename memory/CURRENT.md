# 当前状态

更新：2026-10-30。用户确认Token监控V1（前端+后端）验收通过，进入维护及两类分析启动阶段。[现场验收与交接](../docs/huawei/MONITORING_V1_ACCEPTANCE_20261030.md)为当前事实入口。

- dev6/F007、S0 1.0.0、schema3/view1；monitoring-v1-20261028发布身份保持不变。三模型现场任务完成，每文件约22–55分钟；有效150,698/读入354,638条，77范围。
- 现场采用时间格式转换、模型别名和DeepSeek thinking_disabled配置；不等于源码修复或生产模式等价。数据质量、时间口径、GF资产/GLM CP等边界见验收交接，不将有效子集称为全量画像。
- 异常分析先由一个后端母会话调研/产品设计，完成后再按用户启动fork低命中与Token异常两线；异常分析不属监控功能增加。统一编码计量仍由监控提供，自进化Agent依赖不变。
- 监控V2改为两条并行后端线：[用户功能](../docs/tasks/monitoring/v2-user/ENTRY.md)负责P90 TTFT目标→最低理想命中率评估及搜索排行；[MA监控](../docs/tasks/monitoring/v2-ma/ENTRY.md)负责GF规格×UUID的独立采集、回放、真实对照。hybrid暂不做；初版UI-01已认可。两线当前待fork/登记，不在本父会话一次性设计全部功能。
- V1前后端、总设计休眠；审查打包运行中。本V2父会话本轮仅版本/角色整理、提交与push；用户明确暂不创建聊天。完整角色、P0/P1入口及状态见[SESSIONS](SESSIONS.md)。
- 原前端会话已完成交接，按用户要求暂时休眠；后续待产品、后端设计与接口契约固定后，由用户使用两份prompt启动新前端会话。用户认可[UI-01初版展示](../docs/tasks/viewer/PROTOTYPE_V2_UI_01.md)，[HTML已沉淀到docs](../docs/tasks/viewer/prototypes/tokenscope-v2-demo-ui01.html)作为风格/配色/布局入口（原HTTP预览已撤下）；已准备[监控V2前端](../prompts/sessions/TOKEN_MONITORING_V2_FRONTEND_START.md)与[异常分析前端](../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md)启动prompt，尚未创建会话。对应后端设计/契约固定后，按[工作流](../docs/architecture/TASK_SESSION_WORKFLOW.md)逐阶段审批；实现必须严格遵循最终获批DEMO视觉。正式代码与S0未改。

- 用户侧GB按appid×common_name；MA侧GF按规格×UUID，同UUID跨appid/P共享。暂定空缓存；MA每30min或1h采集、保留前份并回放前份＋当前份为候选，统计窗口仍待讨论，不能保证理想≥真实。统一内网访问目标保留，见[MaaS参考](../docs/architecture/MAAS_REFERENCE.md)和[产品记忆](tasks/monitoring.md)。
- 本轮为文档/DEMO交接检查点，V1发布身份不变；[版本整理记录](../docs/operations/V2_HANDOFF_20261030.md)。

[SESSIONS](SESSIONS.md) · [监控](../docs/tasks/monitoring/ENTRY.md) · [命中率低分析](../docs/tasks/prefix-analysis/ENTRY.md) · [Token异常分析](../docs/tasks/length-analysis/ENTRY.md) · [交付](../docs/tasks/delivery/ENTRY.md) · [协作流程](../docs/architecture/TASK_SESSION_WORKFLOW.md)

旧状态快照：[2026-10-30](../achieve/2026-10-30/snapshots/memory/CURRENT.md)。原始证据、冻结契约、已发布交付文件保持身份，生产CSV不离现场。

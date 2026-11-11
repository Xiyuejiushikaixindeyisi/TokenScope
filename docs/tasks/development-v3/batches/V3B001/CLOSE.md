# V3B001 CLOSE

状态：**CLOSED — 来源/样本/契约组件范围**，2026-11-10。生产执行未启用，T01真实worker链路及AC-MEM仍待B002/B007。

## 完成与证据

- [x] 已依据[条件授权](../../../product-v3/V3_REVIEW_DECISION_20261110.md)完成r1两项计划修订，核对后启动。
- [x] 元数据流式选A/B，精确成员/顺序/digest，单条先准入再取正文；blobopen避免巨型TEXT预先物化。
- [x] 受控seal回调、前后完整性/用户revision、原子封存快照、A/B访问隔离；不改变原source/旧结果。
- [x] 独立prepare登记/幂等/实例身份，新diagnostics-sampling-3 schema/examples/manifest；自动模式不接受预指定clock/recipe。
- [x] T01–T05组件门禁，46项测试及ruff/mypy通过；问题记录均闭环。
- [x] 本线记忆增量与下一批输入记录，既有dirty/旧契约保留，未提交Git。

| 设计 | 实现 | 验证 |
| --- | --- | --- |
| D2元数据/连续成员 | sampling_v3.select_windows；source_preparation.metadata_rows/blob_text | T01–T03 |
| D2来源/快照/隔离 | prepare_snapshot、PreparationIO、SampleResolvedSource/open_sample_window | T01/T03/T04 |
| D7版本与自动意图 | contracts_v3、PreparationStore、api/diagnostics_v3、export_sampling_schema | T05及HTTP登记/幂等 |
| 旧公共层最小适配 | SourceResolver可注入IO；verify_seal可不解析signals；UserRunService.index可注入digest；wire typed mapping；ObservedSource类型同步 | 既有source/contract/freeze回归 |

候选为v3b001-local-1，基于HEAD 9a071c87b517490e497aa6cc1e53ec066bb4ede0及未提交工作树；[精确文件摘要](../../../../../artifacts/validation/development-v3/V3B001/attempt-05/candidate.json)、[测试记录](TESTS.md)、[问题记录](ISSUES.md)。不得把该HEAD单独称为已包含本批的Git提交。

## 边界与交接

B002接收SamplingLimits、SampleManifest3、prepare_snapshot/PreparationIO、SampleResolvedSource、prepare登记store/router。B002须实现默认自动profile、进程硬资源、取消/partial/恢复和生产编排；本批callback支持不等于硬资源已落实。source全文件hash仍有I/O成本，生产规模/内存/P95未验；AC-MEM、自动L1及BUS01–05尚未关闭。

V3父范围统计包含request_records中所选appid/时间的记录；未有编码结果的记录显式排除并断开连续段，不能跨过它拼接缓存收益。监控本身的历史有效编码分母不改；prepare另核该子集键与旧ResolvedSource一致。

回退：只撤回本批有归属的新V3注册/模块和公共可选参数适配，保留封存产物与对应只读能力、旧源/旧结果；不回退他人dirty、不恢复Token/自动full、不删state。当前未挂生产V3路由，无运行服务需回退。下一步按授权进入V3B002。

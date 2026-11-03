# HV2-R2-TOKEN：公共验收后私有性能与适用性验证

当前任务继续HV2，不恢复arpc/RV1/旧提交。异常公共层第一关已由总设计师独立验收，读取 docs/tasks/delivery/HV2_COMMON_FREEZE_20261103.json（组合9ac3e7fd5c5fea9556f957871bb03a0791e79e9404b207462a1cf8e184d7cb8e）、docs/tasks/prefix-analysis/HV2_COMMON_HANDOFF_20261103.md、docs/contracts/diagnostics-execution-2/README.md及执行板。根独立41+最后3项边界（有重复）通过，维护方331+23专项通过；旧27文件一致。公共API/Schema和旧wire/契约冻结，未声称现场规模/页面完成。
用户后端亦已冻结2.1.0：HV2_USER_BACKEND_HANDOFF_20261103.md与HV2_USER_FREEZE_20261103.json，Trace来源为source_kind=user_v2/user_run_id/appid/expected_index_revision/window=null；base_run只核对，不同时提交；MA另数据。
保持用户批准四入口和L4/L5，T1/hybrid/Agent不恢复。两大Qwen仅low_hit，不为采样额外启Token。无真实最小正反例/业务策略不得凭模型品牌、字节数或重复直接新造生产recipe、删除/收益/会话因果。新调查原件SHA保持；预算先按结构和实际成本实测，不全局提额掩盖。
源码只改本线分配窗口；不改analysis_common/HTTP/用户/MA/前端/CLI/锁/共享记忆。确需公共修改在交接列具体缺口，先由我审查安排，不能并发改已冻结契约。只本地小样本合成unit/TestClient/profile，不监听服务或Docker/打包/部署，不commit/push，不发跨会话消息/创建agent。所有测试/profile结果保留原证据，失败原因/修复/复测分开。当前真实工作树有其他session修改，勿reset/clean。

你PREP已完成，现正式开放src/tokenscope/token_content、tests/unit/token_content、tests/integration/token_content和本线文档/记忆。先读HV2_TOKEN_PREP_20261103.md并核对当前源码，按它第六节执行有界结构基线profile，然后只修实测确认的热点/正确性缺口。
必须完成：
1. 独立复验消费冻结公共选择、空recipe快路径、fragment内部不完整/保留不足/插件错误/缺业务依据不同状态；不要再使用全局findings导致Token片段不完整的错误归因。失败哨兵验证low_hit-only零Token analyze/propose/prepare/encode调用（复用公共入口，不修改它）。
2. 合成小样本覆盖纯messages、tools长Schema、多个tool_result、嵌入JSON宽/深、相同与近似重复及合法few-shot/必要引用对照，明确不是现场复现。分别调bytes/units/depth/comparison/candidates边界；记录各规则完成、适用、partial/失败原因和预算，不用checked全量替代。
3. 先profile初始analyze、proposal、prepare、序列化/写入相关成本：wall/process CPU、峰值内存、parse/dumps/hash/extract调用次数/字节、units/comparison/candidate/encoding_calls、fragment大小。固定输入/预算/来源版本，短样本重复对照并区分profile开销。只对有证据热点优化，优先同次add共用规范序列化结果等不变语义办法；需要改变预算计费的Inventory复用先明确提案并由我审定，不能偷偷改stop点。没有可信性能收益的优化不硬加。
4. 逐项证明有效结果、unit/location/fragment身份、原始数值词法、精度、空值、预算/取消/授权/防篡改均不退化。不得删工具定义库存、跨请求无界缓存、跳过Schema/精确比较或抬预算换通过。保持T2–T4与缺策略advice，不造生产可删除结论。
5. 给出现场量级适配的预算估算方法与应采样的真实结构分层，说明本机结果可/不可外推的部分；真实参数依据缺口写明，不只给一串耗时。
最终交接 docs/tasks/length-analysis/HV2_TOKEN_BACKEND_HANDOFF_20261103.md，含源码SHA/精确清单、基线与优化后profile证据、实际回归、修复记录、契约无变化或明确申请、未决项；更新自己ENTRY/记忆。完成后由我独立验收再通知异常前端，不代签现场。

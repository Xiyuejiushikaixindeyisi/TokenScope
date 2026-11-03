# HV2-R2-LOWHIT：公共验收后的规则覆盖与成本闭环

当前任务继续HV2，不恢复arpc/RV1/旧提交。异常公共层第一关已由总设计师独立验收，读取 docs/tasks/delivery/HV2_COMMON_FREEZE_20261103.json（组合9ac3e7fd5c5fea9556f957871bb03a0791e79e9404b207462a1cf8e184d7cb8e）、docs/tasks/prefix-analysis/HV2_COMMON_HANDOFF_20261103.md、docs/contracts/diagnostics-execution-2/README.md及执行板。根独立41+最后3项边界（有重复）通过，维护方331+23专项通过；旧27文件一致。公共API/Schema和旧wire/契约冻结，未声称现场规模/页面完成。
用户后端亦已冻结2.1.0：HV2_USER_BACKEND_HANDOFF_20261103.md与HV2_USER_FREEZE_20261103.json，Trace来源为source_kind=user_v2/user_run_id/appid/expected_index_revision/window=null；base_run只核对，不同时提交；MA另数据。
保持用户批准四入口和L4/L5，T1/hybrid/Agent不恢复。两大Qwen仅low_hit，不为采样额外启Token。无真实最小正反例/业务策略不得凭模型品牌、字节数或重复直接新造生产recipe、删除/收益/会话因果。新调查原件SHA保持；预算先按结构和实际成本实测，不全局提额掩盖。
源码只改本线分配窗口；不改analysis_common/HTTP/用户/MA/前端/CLI/锁/共享记忆。确需公共修改在交接列具体缺口，先由我审查安排，不能并发改已冻结契约。只本地小样本合成unit/TestClient/profile，不监听服务或Docker/打包/部署，不commit/push，不发跨会话消息/创建agent。所有测试/profile结果保留原证据，失败原因/修复/复测分开。当前真实工作树有其他session修改，勿reset/clean。

你刚完成公共第一关，现在唯一新增窗口src/tokenscope/prefix_analysis及其测试/本线文档记忆（公共已关闭）。本阶段以规则覆盖/预算/性能证据为主，若没有测得需修问题可不强行改源码。
1. 以当前v2公共Runtime实际调用验证L1–L5：密集L4不挤占其他规则保留，所有方向/比较/保留上限有诚实原因，扫描完成、候选截断、比较完成、保留不足分别可核对。原规则/收益>1pp门槛/需业务关联限制保持；L4只是差异，L5只是表示差异，不换文案制造动态字段根因。
2. 按tools/messages结构做有界合成profile：纯messages对照、长tools Schema、工具排列/集合变化、嵌入JSON表示、合法历史差异。测请求数×候选上限对实际比较数/读取字节/编码/CPU/wall/RSS的影响，固定seed和预算，区分source验证、候选查找/匹配、序列化、token读取/编码、pilot/full成本。不能用encoding_calls=0宣称成本0。
3. 仅基于测得热点实施本线不改变证据/规则/身份/精确性/授权的局部优化，若需要改候选语义或缓存影响检测集合先交具体方案由我审定。不得删断言、全局提额、隐式抽样或伪造全量覆盖。新增tools/messages探测器当前只有现场候选统计，真实正反例/业务依据不足；可以给研究建议及最小证据要求，不直接生成人工未经认可的新删除/收益策略。
4. 输出可供华为agent使用的预算预估/小批真实结构抽样方法：max_source/bytes、两个通道comparison上界、每规则保留及byte、编码/实验上界分别注明，依据实际计量判断下一步而非一次长跑OOM。两大Qwen仍仅low_hit。
5. 本线回归与公共调用兼容测试，记录是否发生实际源码改动；如果改了prefix service/detection这两个第一关已记录文件，保持原冻结证据，单列新SHA供我第二次验收，不能回写第一关manifest。
交接 docs/tasks/prefix-analysis/HV2_LOW_HIT_BACKEND_HANDOFF_20261103.md，实际命令/输入/profile/修复/复测/SHA/限制，更新本线入口/记忆；完成后待我独立验收，再通知异常前端。

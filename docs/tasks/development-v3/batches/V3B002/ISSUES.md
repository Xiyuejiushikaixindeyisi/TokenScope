# V3B002 ISSUES — 实际问题与处置

2026-11-10；[PLAN](PLAN.md)、[TESTS](TESTS.md)、[CLOSE](CLOSE.md)。本批代码阻断已关闭；I04历史证据损失未恢复，持续披露。

| ID | 类型/状态 | 问题、处理与证据 |
| --- | --- | --- |
| I01 | PLATFORM / VERIFIED_SUPPORTED_LOCAL | cgroup不可写，采用明确标注RLIMIT_AS/FSIZE/CPU、RSS另测；固定worker禁止派生进程，PDEATHSIG/进程组监督。真实硬限制/父死亡/三模型和取消测试通过；不声称RSS硬限或所有硬件已支持。 |
| I02 | DESIGN_RISK / CLOSED | 取消与发布事务竞态、crash/half-write与恢复：PreparationStore唯一终态，CheckpointJournal只保留已提交且SHA正确前缀，重启interrupted不自动跑working。attempt-03/04/06真实进程与事务测试。 |
| I03 | CODE_BUG / CLOSED | 首轮GLM/Qwen固定开销拒绝。线程收窄后27通过，但不能排除环境变化；attempt-05在首轮原AS上限复验，Qwen仍失败，根因还包括16MiB任意最小余量门槛。保持128MiB安全储备、16/256扩张系数和同一AS上限，允许1MiB正余量生成更小完整窗口；attempt-06两模型在原失败上限成功。未提高内存上限、未更换成功断言。 |
| I04 | TEST_ISOLATION / CODE_FIXED；HISTORICAL_EVIDENCE_LOSS未恢复 | attempt-03的旧test_local_scale_record固定写artifacts/validation/prefix-analysis/lh009/scale-16.json、scale-64.json、scale-128.json，覆盖三份历史校准JSON。执行前漏查副作用是本线失误。改为pytest tmp_path/legacy-resource-measurements，attempt-04原16条校准用例通过且结果落独立目录。项目artifacts/achieve按文件名查找未找到原内容副本（部分Docker目录无读取权限）；三文件不被Git跟踪，不能恢复或伪造旧值。新生成内容另存attempt-06/legacy-overwrite-incident供追责，**不是旧版备份**。原始华为报告/业务state未被该测试改写；丢失的是历史测试日志。代码隔离修复闭环，历史损失仍在，不把它抹成CLOSED或隐瞒。 |
| I05 | CODE_QUALITY / CLOSED | 首轮行长/导入/类型注解缺陷已修，不改lint/mypy规则。最终ruff通过、mypy132源码通过。 |
| I06 | CODE_REVIEW / CLOSED | 监督软RSS若写通用cancel文件会把可协作缩窗误记用户取消。软压力由ledger触发缩窗；监督给释放宽限，RSS回落则继续，明确用户取消仍优先；阻塞不释放才强制停止且判失败。cooperative_memory_release及取消/超时/硬限负例通过。 |

I04不影响本候选重新生成的测试证据或产品源码门禁，但损失不能由agent“接受豁免”后消失；后续交付必须保留披露，不能再引用这三路径称2026-10-31原始校准。镜像会话不承担这些开发问题修复。

剩余产品依赖不是本批已通过结论：B003正常L1自动发现、B004候选覆盖、B005完整窗A/B指标/状态、B006前端、B007真实业务底线。Token私有开发仍休眠。

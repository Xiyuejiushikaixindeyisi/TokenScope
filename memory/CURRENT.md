# 当前状态

2026-11-05：用户决定 **V2暂时认为通过，先完成TokenScope产品宣传**。当前发布仍为tokenscope-v2-hv2-20261103（源码c1345b6）；收到的华为报告、核对、证据局限及留V3问题见[阶段收口](../docs/tasks/delivery/HV2_ACCEPTANCE_CLOSE_20261105.md)。暂时接受不等于全功能/全规模/全部性能问题验证通过；不自动恢复开发、重测或打包。

[V3 session](../docs/tasks/product-v3/ENTRY.md)继续用户已开展的宣传讨论与研究设计，先明确定位/服务对象/功能取舍，以公司真实appid任务、分布、结构和业务确认匹配异常分析；外部报告是参考，不替代现场。细化/重构待讨论决定。本次[新证据交接](../docs/tasks/product-v3/HV2_EVIDENCE_HANDOFF_20261105.md)已接收并由V3本线更新证据/宣传口径，既有草稿不混入本轮提交。

保留问题：搜索排行模型入口留V3；已列出的异常成果主要L4、Token无业务recipe时零建议不等于无异常；MA源缺失/预热冲突仍有边界。报告容器32GiB、峰值30.19GiB，伴随超时/任务Not Found；主机375GiB，未见OOM-kill完整证据。大数据容量/API健康/任务持久化与恢复是V3重要设计约束，不能仅靠扩内存或加探测器解决。

镜像打包与审查负责跨版本迭代、版本级debug、独立E2E、Git及授权交付；六线开发窗口关闭、历史总设计/V1休眠。[SESSIONS](SESSIONS.md) · [交付身份/全部SHA](../docs/tasks/delivery/HV2_DELIVERY_20261103.md)。本轮仅文档归档、记忆和版本push，不改源码/批准四入口与L4/L5/冻结契约/包体；UIR-03仍留V3。

[原字节归档](../achieve/2026-11-05/hv2-acceptance-close/README.md)保留旧报告和新接收快照。旧调查路径的预存重复副本不顺带提交，历史取证从归档读取。现场报告称旧state/镜像已由用户清理，现场回退须先确认介质与匹配state；不得再承诺现场旧环境原位可直接回退。[长期教训](DELIVERY_LESSONS.md)。

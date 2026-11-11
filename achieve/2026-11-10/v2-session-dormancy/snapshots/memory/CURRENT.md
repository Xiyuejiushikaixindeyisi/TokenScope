# 当前状态

2026-11-10：**V3先聚焦低命中四项P0**：有界小样本/资源控制、L1时间字段、候选质量/重复差异、改法到样本验证及建议解释。详见[当前范围与交接](../docs/tasks/product-v3/V3_SCOPE_AND_HANDOFF_20261110.md)。[全新V3开发角色](../docs/tasks/development-v3/ENTRY.md)已预登记，ID未知/待启动；首轮只读check。镜像打包与审查在V3只负责打包和审批，不承担开发/debug/开发调度或开发验收执行。

**Token异常在V3休眠，修复留V3.5**；旧成果保留可读，四入口/L4L5保持。已准备[三组长尾探索prompt](../docs/tasks/product-v3/HUAWEI_TOKEN_TAIL_EXPLORATION_PROMPT_20261110.md)，等待华为单份报告后再细化V3范围/顺序/验收。当前只整理文档与角色，不实施、不启动新分析或会话。[四象限明细HTML](../docs/tasks/product-v3/promotion/quadrant-detail/dist/index.html)为高优先级资料。[SESSIONS](SESSIONS.md)。

## 既有V2状态与文件交付记录（不覆盖上述V3分工）

2026-11-05：用户决定 **V2暂时认为通过，先完成TokenScope产品宣传**。当前发布仍为tokenscope-v2-hv2-20261103（源码c1345b6）；收到的华为报告、核对、证据局限及留V3问题见[阶段收口](../docs/tasks/delivery/HV2_ACCEPTANCE_CLOSE_20261105.md)。暂时接受不等于全功能/全规模/全部性能问题验证通过；不自动恢复开发、重测或打包。

[V3 session](../docs/tasks/product-v3/ENTRY.md)继续用户已开展的宣传讨论与研究设计，先明确定位/服务对象/功能取舍，以公司真实appid任务、分布、结构和业务确认匹配异常分析；外部报告是参考，不替代现场。细化/重构待讨论决定。本次[新证据交接](../docs/tasks/product-v3/HV2_EVIDENCE_HANDOFF_20261105.md)已接收并由V3本线更新证据/宣传口径，既有草稿不混入本轮提交。

保留问题：搜索排行模型入口留V3；已列出的异常成果主要L4、Token无业务recipe时零建议不等于无异常；MA源缺失/预热冲突仍有边界。报告容器32GiB、峰值30.19GiB，伴随超时/任务Not Found；主机375GiB，未见OOM-kill完整证据。大数据容量/API健康/任务持久化与恢复是V3重要设计约束，不能仅靠扩内存或加探测器解决。

镜像打包与审查负责跨版本迭代、版本级debug、独立E2E、Git及授权交付；六线开发窗口关闭、历史总设计/V1休眠。[SESSIONS](SESSIONS.md) · [交付身份/全部SHA](../docs/tasks/delivery/HV2_DELIVERY_20261103.md)。本轮仅文档归档、记忆和版本push，不改源码/批准四入口与L4/L5/冻结契约/包体；UIR-03仍留V3。

[原字节归档](../achieve/2026-11-05/hv2-acceptance-close/README.md)保留旧报告和新接收快照。旧调查路径的预存重复副本不顺带提交，历史取证从归档读取。现场报告称旧state/镜像已由用户清理，现场回退须先确认介质与匹配state；不得再承诺现场旧环境原位可直接回退。[长期教训](DELIVERY_LESSONS.md)。

2026-11-05追加：用户已授权产品宣传合成演示数据+prompt文件包，由交付会话完成[revision2压缩包/桌面校验](../docs/tasks/delivery/ICSL_DEMO_R2_PACKAGE_20261105.md)。仅追加演示交付，不升级产品或停现有服务，不改变上述真实业务验收结论。

最新修订：ICSL revision2（80条/50K）已被用户否决，[候选包撤回](../docs/tasks/delivery/ICSL_DEMO_R2_PACKAGE_20261105.md)，此前启动消息失效；WSL错误包和打包/解压副本已按用户要求清理，桌面撤回旧包及原始证据保留。等待V3新版验收交接后再核对打包、复制桌面、给SHA与新启动消息；保护现场真实数据和分析结果。

最新：V3已完成102条新版验收并交接，本线[revision3核对/打包/桌面SHA](../docs/tasks/delivery/ICSL_R3_PACKAGE_20261105.md)完成。仅ICSL场景构造样本文件交付，非V3产品部署；现场必须核查appid隔离、保留真实数据/成果。旧桌面包继续撤回，WSL旧错误包已清理。

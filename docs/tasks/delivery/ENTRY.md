# 版本迭代、镜像打包与审查入口

2026-11-04用户调整职责：本会话负责V1/V2/V3版本之间的迭代、版本级debug修复协调、独立端到端验收、Git/归档记忆、镜像与代码交付；V3调研/产品设计已交[专职新session](../product-v3/ENTRY.md)，无须等待现场回传。当前仅文档/职责交接和研究启动，没有重新打包或修改已发布包。新增[华为V3补证prompt](../../../prompts/delivery/HUAWEI_V3_EVIDENCE_APPENDIX_20261104.md)并入原唯一报告，不改V2验收顺序。

2026-11-03：HV2修复已完成公共层→依赖后端独立验收及冻结→前端→源码与容器独立验收→WSL打包和桌面全SHA交付。源码 `c1345b6fd7d413a94420642ca1b4099b9ec104b4` 已push main；版本 `tokenscope-v2-hv2-20261103`。现场真实数据及用户两阶段验收待执行，六线开发窗口关闭。 [完整交付结果](HV2_DELIVERY_20261103.md)是当前发布、全部SHA、独立验证、回退和未决项的唯一汇总入口。

当前等待华为对新包执行真实数据验收；下一轮问题按实际报告定向交六线维护方，公共层/契约变化仍先后端审查冻结再前端。历史全项目总设计与V1不自动唤醒。

P0：[CURRENT](../../../memory/CURRENT.md) → [SESSIONS](../../../memory/SESSIONS.md) → [交付规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md) → [长期教训](../../../memory/DELIVERY_LESSONS.md)。P1：[固定版本](VERSION_HV2_20261103.json)、[当前现场prompt](../../../prompts/delivery/HUAWEI_V2_HV2_REAL_DATA_20261103.md)、[部署说明](../../../deploy/monitoring/README.md)、[Git规则](../../operations/GIT_WORKFLOW.md)。

独立验收冻结：[异常公共层](HV2_COMMON_FREEZE_20261103.json)、[用户](HV2_USER_FREEZE_20261103.json)、[MA](HV2_MA_FREEZE_20261103.json)、[Token](HV2_TOKEN_FREEZE_20261103.json)、[低命中](HV2_LOW_HIT_FREEZE_20261103.json)。原执行/评审/任务计划及派发prompt已[归档](../../../achieve/2026-11-03/hv2-delivery-closed/README.md)，保留真实失败与修复证据。

[华为验收原件](../../huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md)、[调查原件](../../huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md)不改写。保持四入口和L4/L5，UIR-03留V3。每个新候选先核实停旧、空state/新浏览器；现场真实Trace3/MA18、先量级预算、两阶段人工验收、SSH18002、唯一Markdown嵌源码与证据。

新包原目录与Windows桌面全15文件SHA一致，旧包/state/证据保留；包体/backup不上GitHub。回退读[2026-11-02旧交付身份](V2_APPROVED_DELIVERY_20261102.md)，旧镜像只配旧state。

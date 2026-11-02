# 镜像打包与审查／完整服务交付入口

2026-11-02当前：[V2批准交付](V2_APPROVED_DELIVERY_20261102.md)已完成WSL构建/容器复验/桌面全SHA交付，华为真实数据待验；用户认可V2可交付，UIR-03留V3，不阻断、不扩展修复。已授权Git整理/push、WSL构建与代码/镜像包、本地backup管理及Windows桌面验收；文件/镜像身份、全部SHA、实际测试与回退按该记录读取。

P0：[CURRENT](../../../memory/CURRENT.md) → [SESSIONS](../../../memory/SESSIONS.md) → [交付规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md)与[长期教训](../../../memory/DELIVERY_LESSONS.md)。P1：[本版现场prompt](../../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md)、[部署工具](../../../deploy/monitoring/README.md)、[Git约定](../../operations/GIT_WORKFLOW.md)、[V100历史环境报告](../../huawei/TOKEN_SCOPE_V100_ENVIRONMENT_REPORT.md)。现场需实测，不直接继承历史可用性。

前置审查：UIR-01/02闭环、四入口和L4/L5保持；[复审及修复原文链](../../../achieve/2026-11-02/v2-approved-delivery/README.md)。源码/锁/契约/模型/实际资源固定后构建，不读共享dirty或旧dist。每个新候选先核实停旧服务/进程，独立空state/新浏览器。其他session业务修改归原维护方；不擅自改变用户计划或展示。

交付：WSL artifacts/releases/tokenscope-v2-approved-20261102，新目录保留旧包；完整复制Windows桌面，所有SHA逐项一致。包体/镜像不上GitHub，backup仅本地不合main；源码和非敏感交付记录精确push main，无PR。华为先用户监控/搜索/TTFT后MA，第一次用户验收后才指定appid两类分析，唯一Markdown回传。

历史：[本次归档](../../../achieve/2026-11-02/v2-approved-delivery/README.md) · [监控V2前序状态](MONITORING_V2_STATUS.md) · [V1现场验收](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md) · [B006工具计划](../monitoring/batches/B006/PLAN.md)。原始证据、冻结契约和旧发布包保持身份；旧合成/额外附件/旧服务并行策略不再适用。

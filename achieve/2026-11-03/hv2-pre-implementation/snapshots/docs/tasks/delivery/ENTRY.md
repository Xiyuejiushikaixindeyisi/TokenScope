# V2版本总设计、审查与完整服务交付入口

2026-11-03后续执行更新：华为调查已收到，用户已要求开始修复与实际任务派发。当前状态、证据勘误、源码窗口和阶段门槛以[本轮执行板](HV2_REPAIR_EXECUTION_20261103.md)为准；下方“等待回传/尚未派发”保留为前序规划记录。公共层先验收，后端通过冻结后前端，最终完整验收交付。

2026-11-03最新：用户指定本会话为**V2版本总设计师**，负责六线规划分配、审查/E2E、Docker/代码镜像包、文档记忆和版本/push。[本轮统筹计划](V2_REPAIR_COORDINATION_PLAN_20261103.md)是当前范围/顺序/条件授权入口：等华为调查回传后，公共层先验收、后端完成并冻结契约、前端接入，完整E2E通过后连续发布交付。当前仅登记计划和记忆，未派发或改代码、复测、提交/push/构建。[已有验收原件](../../huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md) · [核对方案](../../huawei/HUAWEI_V2_REVIEW_AND_RESEARCH_PLAN_20261103.md) · [只读调查prompt](../../../prompts/delivery/HUAWEI_V2_READONLY_INVESTIGATION_20261103.md)（保持只读，新报告尚未收到）。

2026-11-02的[V2批准交付](V2_APPROVED_DELIVERY_20261102.md)已完成WSL构建/容器复验/桌面SHA核对，身份/全部SHA/回退继续读该历史记录；不能代替华为通过或本轮新发布授权。UIR-03仍留V3，原包和证据保持。

P0：[CURRENT](../../../memory/CURRENT.md) → [SESSIONS](../../../memory/SESSIONS.md) → [交付规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md)与[长期教训](../../../memory/DELIVERY_LESSONS.md)。P1：先读本轮方案和原报告；历史发布参考[本版现场prompt](../../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md)、[部署工具](../../../deploy/monitoring/README.md)、[Git约定](../../operations/GIT_WORKFLOW.md)、[V100历史环境报告](../../huawei/TOKEN_SCOPE_V100_ENVIRONMENT_REPORT.md)。现场需实测，不直接继承历史可用性。

前置审查：UIR-01/02闭环、四入口和L4/L5保持；[复审及修复原文链](../../../achieve/2026-11-02/v2-approved-delivery/README.md)。源码/锁/契约/模型/实际资源固定后构建，不读共享dirty或旧dist。每个新候选先核实停旧服务/进程，独立空state/新浏览器。其他session业务修改归原维护方；不擅自改变用户计划或展示。

已交付历史：WSL artifacts/releases/tokenscope-v2-approved-20261102，新目录保留旧包；完整复制Windows桌面，所有SHA逐项一致。包体/镜像不上GitHub，backup仅本地不合main；源码和非敏感交付记录精确push main，无PR。华为先用户监控/搜索/TTFT后MA，第一次用户验收后才指定appid两类分析，唯一Markdown回传。

历史：[本次归档](../../../achieve/2026-11-02/v2-approved-delivery/README.md) · [监控V2前序状态](MONITORING_V2_STATUS.md) · [V1现场验收](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md) · [B006工具计划](../monitoring/batches/B006/PLAN.md)。原始证据、冻结契约和旧发布包保持身份；旧合成/额外附件/旧服务并行策略不再适用。

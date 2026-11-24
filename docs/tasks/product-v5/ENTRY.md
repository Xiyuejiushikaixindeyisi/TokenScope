# TokenScope V5 产品设计入口

2026-11-24用户授权准备产品方向、文档/记忆整理和新session启动prompt。当前仅需求讨论与设计准备，未授权产品开发、前端改版、打包或现场验证。实际V5 session ID未知，待用户启动后本人登记；本轮未创建或发送会话。

## 当前范围

[用户方向与待决口径](USER_DIRECTION_20261124.md)是本轮需求依据；[可直接转发启动prompt](START_PRODUCT_20261124.md)；[本人记忆](../../../memory/tasks/product-v5.md)；[session登记](../../../memory/SESSIONS.md)。

V5六项方向：非法JSON容错；平均输入长度＋理想命中率；跨全部已完成模型服务的搜索排行；平均输入长度排序；长输入低命中的分析触发；面向同事的推理优化建议。Token异常分析长期休眠。用户会另行收集推理优化技术材料，当前不代填一套确定技术方案。

V4.1继续由[原session](../v4/simulator-v41/ENTRY.md)完成本机E2E，**不需要镜像/代码交付包，不需要华为验证**；V5讨论不成为其新增前置条件。原batch、契约、源码、资产、验证和服务归原session维护，本线只读必要交接，不停候选、不重跑、不加验收关卡。

## 定向阅读

V4.1活动入口/batch和V4研究HANDOFF属于共享工作树的本机资料，本次不随V5提交；下列这些链接仅在相应工作区已有文件时有效。新clone缺少时向责任线取得交接，不以缺文件判定该线未开展工作，也不代为补造或提交。

1. AGENTS→CURRENT→SESSIONS→docs/README，再读本入口与USER_DIRECTION。
2. V4.1[入口](../v4/simulator-v41/ENTRY.md)与[执行记录](../v4/simulator-v41/V41_BATCH_EXECUTION.md)：仅了解模型/计量基线，实际闭环以该线最新证据为准。
3. 既有四象限：[展示材料](../product-v3/promotion/quadrant-detail/dist/index.html)；[流量研究交接](../product-v4/traffic/HANDOFF.md)、[MaaS研究交接](../product-v4/maas/HANDOFF.md)按问题追溯，研究假设不等于运行产品能力，旧试点不自动重启。
4. [V4资料索引](../product-v4/V4_REVIEW_PACKAGE_20261115.md)；[V3已批准展示参考](../development-v3/prototypes/repair-demo-r1/index.html)。保持四入口/L4L5，V5只讨论必要局部变化。
5. 如需核实现状，只读定位Ranking.tsx/UserMonitor.tsx/AppShell.tsx、user_monitoring/ranking.py/contracts.py、monitoring/statistics.py/rules.py及编码入口；不全量审读源码，不在页面访问时触发计算。

## 首轮交付

先与用户讨论产品定位、六项需求和最小范围；给出“用户已明确方向 / 需讨论口径 / 需验证事实”。JSON、指标/排行/阈值可先讨论；同事工作台可先梳理问题到证据的结构，具体技术内容等待用户材料。先方案，若要调整页面须再提供DEMO并获得明确展示批准；本轮不制作或实施新页面。

旧启动材料归档见[整理记录](../../operations/V5_DOCUMENTATION_HANDOFF_20261124.md)。归档不是恢复任何旧现场任务。

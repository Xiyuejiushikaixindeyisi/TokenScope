# Session角色与任务登记

2026-11-13用户已确认V3验收通过，要求两条V3会话休眠并准备V4入口/任务/prompt。休眠是项目职责登记，不等于删除/应用归档，不自动发消息或唤醒；新角色待启动不代表实际会话已创建。

## 当前与待启动角色

| 角色 | 实际ID与核验 | 状态与任务 | 入口/记忆 |
| --- | --- | --- | --- |
| V5产品设计（待用户启动） | 未知；未创建/发送会话，待本人环境核实 | 六项产品方向讨论与方案；不接管或阻塞V4.1，不编码/现场/打包/提交 | [入口](../docs/tasks/product-v5/ENTRY.md) · [启动prompt](../docs/tasks/product-v5/START_PRODUCT_20261124.md) · [记忆](tasks/product-v5.md) |
| 镜像打包与审查 | 01a1800e-80b4-7400-a78b-a84f5b6e888d；本人Windows THREAD/SESSION及应用列表核实 | 持续版本职责；11-24按用户要求整理V5方向/文档/启动prompt与记忆；后续按授权仅提交并推送本轮V5文档，不编码/启停/打包/华为验证，其他session未提交工作保留。本人Windows THREAD/SESSION本轮再次核实；V4.1由原session本机验收，不加本线关卡 | [交付](../docs/tasks/delivery/ENTRY.md) · [记忆](tasks/delivery.md) |
| V4主会话：汇报统筹、审核与提交（应用“整理TokenScope V4汇报方案”） | 01a1d3e3-0c34-7320-bf6f-14438c120aed；本人Windows SESSION/THREAD及应用列表11-15核实 | 用户授权fork两次，已创建两副本／准备三prompt；主线整理V4汇报，审核两线最终材料并判断纳入，维护共享入口和正式提交。本轮一次本地Git，未授权push；不代开发或现场执行 | [主prompt](../docs/tasks/product-v4/sessions/START_MAIN_20261115.md) · [分工](../docs/tasks/product-v4/SESSION_COLLABORATION_20261115.md) · [记忆](tasks/product-v4.md) |
| V4副本1：现网流量研究（应用“TokenScope V4现网流量研究”） | 01a1de7c-8ea4-7cb2-b8e6-114aeba29a60；11-15 fork/read工具确认，同目录、idle；待本人环境复核 | 独立HTML：现网现状／证据，用户三阶段协同优化、节点与有依据的效果；维护本线及流量研究。待用户在fork中首次接收启动prompt，不重复父会话fork／Git任务；成品交主会话审核提交 | [启动](../docs/tasks/product-v4/sessions/START_TRAFFIC_20261115.md) · [ENTRY](../docs/tasks/product-v4/traffic/ENTRY.md) · [记忆](tasks/product-v4-traffic.md) |
| V4副本2：MaaS架构与试点（应用“TokenScope V4 MaaS架构与试点”） | 01a1de7c-a6fd-7043-baa7-987f03d5af3c；11-15 fork/read工具确认，同目录、idle；待本人环境复核 | 两DeepSeek appid简单试点设计；有初步结果后形成场景分类MaaS网关架构待同事粗评。待用户首次启动；无现场／产品实施授权，Tokenization继续pending；成品交主会话审核提交 | [启动](../docs/tasks/product-v4/sessions/START_MAAS_20261115.md) · [ENTRY](../docs/tasks/product-v4/maas/ENTRY.md) · [记忆](tasks/product-v4-maas.md) |
| V4模型演进与开发（拟定角色） | 未知，待用户启动后本人登记 | 待启动；首轮只读资产复用核查/技术方案，获准后实现测试，不提前改页面 | [启动](../docs/tasks/v4/START_DEVELOPMENT.md) · [复用表](../docs/tasks/v4/MODEL_REUSE_MATRIX.md) · [记忆](tasks/development-v4.md) |
| 华为现场agent | 未知，现场本人登记 | 现场身份与本地角色分开；prompt-1三阶段及MaaS prompt-2回传均已在项目内，后者初审存在口径待核；本机未发送或远端执行 | [本轮探索入口](../docs/tasks/product-v4/ENTRY.md) · [独立模型资产盘点](../docs/tasks/v4/START_HUAWEI_READONLY.md) |

新角色首次读AGENTS→CURRENT→本页→docs/README→自己的ENTRY，从自己的环境核实ID，未知如实写未知，不沿用父会话/V3会话ID。11-15主会话按用户明确授权创建上面两个同目录fork；工具ID登记与副本本人环境自核分开。未发送跨会话消息，未唤醒旧线；两副本默认通过共享HANDOFF与用户转交协作，全局登记由主会话维护。

## V3会话（2，用户明确休眠）

| 应用实际chat标题 | 实际ID | 当前状态与历史入口 |
| --- | --- | --- |
| TokenScope V3 调研与产品设计 | 01a1a5d5-4baf-7a41-b5c6-14bd5f4f67c2 | **休眠**；[入口](../docs/tasks/product-v3/ENTRY.md) · [记忆](tasks/product-v3.md) |
| TokenScope V3代码修复与开发 | 01a1c449-6a9b-7a83-912a-5a9ff77c703d | **休眠**；[入口](../docs/tasks/development-v3/ENTRY.md) · [记忆](tasks/development-v3.md) |

2026-11-13应用列表确认上述标题/ID及本项目cwd。首次核查notLoaded，后续两会话分别执行了用户另行要求的V4上下文交接；这是本轮收尾，不是新V4身份或恢复产品开发。项目休眠依据用户指令，不从工具idle/active推断；本线未发送消息/唤醒。既有研究/开发事实保留，不转移实际身份给V4。

## V2与更早角色

| 角色 | 历史实际ID | 状态/入口 |
| --- | --- | --- |
| Token监控前端设计开发 | 01a18c49-d9b4-7a33-8c04-e5a72adfcc24 | 休眠 · [入口](../docs/tasks/viewer/monitoring-v2/ENTRY.md) |
| 异常分析前端设计与开发 | 01a19111-344a-75c1-84e0-14db8be08f4f | 休眠 · [入口](../docs/tasks/viewer/analysis/ENTRY.md) |
| 低命中率异常分析后端 | 01a18be2-7112-7aa2-919b-5137d1f1b1ad | 休眠 · [入口](../docs/tasks/prefix-analysis/ENTRY.md) |
| Token异常分析后端设计和开发 | 01a18fcd-0464-7cf1-b435-4f394bd33e66 | 休眠 · [入口](../docs/tasks/length-analysis/ENTRY.md) |
| V2用户监控后端 | 01a18bc7-cdb5-7830-a185-ad3aa6257b21 | 休眠 · [入口](../docs/tasks/monitoring/v2-user/ENTRY.md) |
| V2 MA监控后端 | 01a18ab2-2600-7ae1-8b0e-979dad9ec3be | 休眠 · [入口](../docs/tasks/monitoring/v2-ma/ENTRY.md) |
| 历史总设计 | 未知 | 休眠 · [入口](../docs/tasks/product/ENTRY.md) |
| V1监控后端 | 01a1682f-956d-7630-afe7-e123ba38dfc0 | 休眠 · [入口](../docs/tasks/monitoring/ENTRY.md) |
| V1监控前端 | 01a17811-4c9a-7513-befc-b35723aec96e | 休眠 · [入口](../docs/tasks/viewer/ENTRY.md) |
| hybrid/自进化Agent | 未启动 | [历史入口](../docs/tasks/evolution-agent/ENTRY.md) |

这些历史ID沿原登记保留，本轮未逐个重新核实或唤醒。Token新开发未纳入本次核心；V4不因名称规划自动恢复六条V2。

## 协作与维护

[本机/华为/用户协作](../docs/tasks/v4/COLLABORATION.md)：产品方案和DEMO先经用户确认，开发独立技术审查、公共身份/后端契约先行、前端随后；镜像只接固定候选作版本/交付。已授权阶段自行推进，不反复申请同一批准；未授权部署/产品改动不得因目录存在自动启动。

共享文件先读最新，按责任精确更新。此次用户授权统一登记休眠，可由整理者在两V3入口/记忆加状态说明，保留原历史；不把整理者写入当成接收方回执。[原字节快照](../achieve/2026-11-13/v3-close-v4-start/README.md)。

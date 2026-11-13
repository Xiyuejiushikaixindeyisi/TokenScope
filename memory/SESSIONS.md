# Session角色与任务登记

2026-11-13用户已确认V3验收通过，要求两条V3会话休眠并准备V4入口/任务/prompt。休眠是项目职责登记，不等于删除/应用归档，不自动发消息或唤醒；新角色待启动不代表实际会话已创建。

## 当前与待启动角色

| 角色 | 实际ID与核验 | 状态与任务 | 入口/记忆 |
| --- | --- | --- | --- |
| 镜像打包与审查 | 01a1800e-80b4-7400-a78b-a84f5b6e888d；本人Windows THREAD/SESSION及应用列表核实 | 持续版本职责；本轮V3用户收口、V4登记、文档/记忆/本地Git提交。不代产品编码，不自动构建/现场/push | [交付](../docs/tasks/delivery/ENTRY.md) · [记忆](tasks/delivery.md) |
| V4产品设计与汇报（拟定角色） | 未知，待用户启动后本人登记 | 待启动；产品定位/汇报、最小DEMO与需求验收，不编码 | [V4](../docs/tasks/v4/ENTRY.md) · [启动](../docs/tasks/v4/START_PRODUCT.md) · [记忆](tasks/product-v4.md) |
| V4模型演进与开发（拟定角色） | 未知，待用户启动后本人登记 | 待启动；首轮只读资产复用核查/技术方案，获准后实现测试，不提前改页面 | [启动](../docs/tasks/v4/START_DEVELOPMENT.md) · [复用表](../docs/tasks/v4/MODEL_REUSE_MATRIX.md) · [记忆](tasks/development-v4.md) |
| 华为现场agent | 未知，现场本人登记 | 现场身份与本地角色分开；只读取证prompt待用户转发，本轮未执行 | [只读启动](../docs/tasks/v4/START_HUAWEI_READONLY.md) |

新角色首次读AGENTS→CURRENT→本页→docs/README→V4入口，从自己的环境核实ID，未知如实写未知，不沿用父会话/V3会话ID。当前没有新增应用chat，不把拟定角色名当已存在chat标题。

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

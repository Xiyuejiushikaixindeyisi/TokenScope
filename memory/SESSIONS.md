# Session角色与任务登记

2026-11-11整理更新：**仅以下三个活跃角色，六条V2开发线休眠。** 活跃表示当前职责，不要求持续运行；休眠不等于删除chat、源码、数据或历史成果。工具的idle/notLoaded与这里的项目职责状态不同。先读AGENTS→CURRENT→本页→docs/README→自己的ENTRY，不全量恢复历史。

## 活跃角色（3）

| 角色／应用中的chat标题 | 实际ID与核验 | 当前阶段与权责 | 入口及本人登记 |
| --- | --- | --- | --- |
| TokenScope V3 调研与产品设计 | `01a1a5d5-4baf-7a41-b5c6-14bd5f4f67c2`，环境THREAD/SESSION已核实 | 证据/产品范围/宣传及高优先级四象限资料；**不修改代码，负责独立验收、问题复验及镜像审查交接prompt**。2026-11-11显式全量延期，repair-r1-02本地验收收口；已交接且镜像线完成发布；本人历史通知/验收记录保留。五组真实业务/现场资源仍待验；本线不执行Git或打包 | [研究入口](../docs/tasks/product-v3/ENTRY.md) · [本人记忆](tasks/product-v3.md) |
| 镜像打包与审查 | `01a1800e-80b4-7400-a78b-a84f5b6e888d`，本人核验登记，2026-11-11本人环境THREAD/SESSION再次核实；本轮不读取应用实时状态 | **镜像/交付审查、版本与打包**：repair-r1-02已交付，源码cabf2c6已push、WSL/桌面校验及prompt r2完成，等待现场；用户新授权本线负责本轮工作树分类审查/整理。不直接现场部署，不承担产品开发/debug/开发调度或开发验收执行 | [交付入口](../docs/tasks/delivery/ENTRY.md) · [本人记忆](tasks/delivery.md) |
| TokenScope V3代码修复与开发；chat标题“核查V3四项P0修复方案” | `01a1c449-6a9b-7a83-912a-5a9ff77c703d`，本人环境核验及应用列表一致 | 2026-11-11用户明确延期显式full；设计r2/T19拆分/验收/记忆已同步。repair-r1-02独立R2关闭RV3-01/02/03，本地LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING；华为五BUS及真实AC-MEM仍NOT_RUN。华为验收交接材料已准备，打包由镜像线完成，本开发线不打包/现场执行；继续承担公共层/低命中/必要前端及回传缺陷修复。本人PowerShell环境THREAD/SESSION再次核验一致，302源码摘要无漂移，详本人入口与记忆 | [开发入口](../docs/tasks/development-v3/ENTRY.md) · [CHECK](../docs/tasks/development-v3/CHECK.md) · [本人记忆](tasks/development-v3.md) |

三方权责已由本人登记；两条外部chat已按用户明确授权通知并完成更新，见[通知回执](../docs/operations/SESSION_SCOPE_REGISTRATION_20261110.md)。此前登记轮各方只改自己的记忆、研究汇总共享导航；2026-11-11用户明确授权镜像线整理当前工作树及共享入口，先快照并保留各方原记录。

2026-11-11研究会话补充：[R2复验及用户范围决定已收口](../docs/tasks/product-v3/acceptance-v3/CLOSE_20261111.md)，不改开发自测或历史失败记录。用户新授权已同步[完整打包prompt](../docs/tasks/product-v3/acceptance-v3/PACKAGING_REVIEW_PROMPT_20261111.md)并发送镜像会话，turn已inProgress；[发送回执](../docs/tasks/product-v3/acceptance-v3/PACKAGING_SEND_RECEIPT_20261111.md)。审查/构建是否完成以交付会话后续实际证据为准。

## V2开发会话（6，均休眠）

| 应用中的chat标题 | 实际ID | 状态及历史入口 |
| --- | --- | --- |
| Token监控前端设计开发 | `01a18c49-d9b4-7a33-8c04-e5a72adfcc24` | **休眠** · [V2监控前端](../docs/tasks/viewer/monitoring-v2/ENTRY.md) |
| 异常分析前端设计与开发 | `01a19111-344a-75c1-84e0-14db8be08f4f` | **休眠** · [V2异常前端](../docs/tasks/viewer/analysis/ENTRY.md) |
| 低命中率异常分析后端 | `01a18be2-7112-7aa2-919b-5137d1f1b1ad` | **休眠** · [V2低命中/公共层](../docs/tasks/prefix-analysis/ENTRY.md) |
| Token异常分析后端设计和开发 | `01a18fcd-0464-7cf1-b435-4f394bd33e66` | **休眠** · [V2 Token后端](../docs/tasks/length-analysis/ENTRY.md) |
| V2 用户监控-后端 | `01a18bc7-cdb5-7830-a185-ad3aa6257b21` | **休眠** · [V2用户后端](../docs/tasks/monitoring/v2-user/ENTRY.md) |
| V2 MA 监控-后端 | `01a18ab2-2600-7ae1-8b0e-979dad9ec3be` | **休眠** · [V2 MA后端](../docs/tasks/monitoring/v2-ma/ENTRY.md)；原V2监控父角色已转为本角色，不重复登记 |

六条ID来自既有登记并于本轮应用列表核对；未唤醒、未发送开发任务。旧“等待总负责定向修复/并行分线/公共层唯一维护方”不自动恢复。未来确需唤醒由用户另行指定；V3范围由新开发会话统一负责，不双写。

## 其他历史与未启动角色

| 角色 | ID／状态 | 入口 |
| --- | --- | --- |
| 历史全项目总设计 | ID未知／休眠 | [历史入口](../docs/tasks/product/ENTRY.md) |
| V1监控后端 | `01a1682f-956d-7630-afe7-e123ba38dfc0`／休眠 | [V1入口](../docs/tasks/monitoring/ENTRY.md) |
| V1监控前端 | `01a17811-4c9a-7513-befc-b35723aec96e`／休眠 | [V1入口](../docs/tasks/viewer/ENTRY.md) |
| hybrid／自进化Agent | 未启动 | 不因本次登记创建或恢复；[Agent历史入口](../docs/tasks/evolution-agent/ENTRY.md) |

## 协作边界

V3四P0按条件授权进入开发，Token私有修复留V3.5，四入口/L4L5与旧成果保留。最新分工：开发会话完成实施/自测并提交确定候选，研究会话独立验收；问题交开发修复后复验，研究会话整理验收结论及打包交接prompt，镜像会话审批和授权打包。研究会话不修改代码，打包会话不代开发或验收；不组织旧六线修复。未完成的现场业务底线独立列明，不以本地结果代签。

共享文件先读最新状态，精确增量更新并保留他人修改。当前为授权工作树整理，具体变更与Git结果见[整理记录](../docs/operations/WORKTREE_RECONCILIATION_20261111.md)；不运行产品服务或变更包体。历史职责及逐版状态保存在[归档前登记](../achieve/2026-11-10/v2-session-dormancy/snapshots/memory/SESSIONS.md)；当前流程见[协作规则](../docs/architecture/TASK_SESSION_WORKFLOW.md)。

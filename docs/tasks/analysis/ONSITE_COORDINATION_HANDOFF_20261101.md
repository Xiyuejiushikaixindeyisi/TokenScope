# 完整服务华为启动与验收总负责交接

2026-11-01（北京时间）。用户最新决定生效，覆盖此前异常分析总负责会话统筹本机交付，以及旧文档将华为启动/验收归MA或其他后端的分工。

## 用户决定与职责转移

> 负责华为机服务启动和验收的 session就是负责镜像打包的 session，你需要把总负责人的权柄交还给“镜像打包与审查 session”，发现问题由“镜像打包与审查 session”协调对应 session 修复。
>
> 本次华为机验收的不止是异常分析，还包括之前打包的Token监控V2（MA监控、搜索功能等），需要重新组织发给华为机的prompt。

镜像打包与审查会话`01a1800e-80b4-7400-a78b-a84f5b6e888d`接回完整服务总负责：组织华为执行prompt、服务启动和功能验收、收集现场证据、派发问题到对应维护会话、协调debug/修复/联合复验、汇总结果及后续版本/Git/交付收口。可以直接联系对应会话，不再通过异常前端中转。普通问题按已授权范围闭环，涉及产品范围或冻结接口变化仍明确影响后与用户确认。

本会话`01a19111-344a-75c1-84e0-14db8be08f4f`完成本次职责登记交接后，回到异常分析前端维护与被协调支持，不继续担任整体总负责，不代写各后端业务。各模块唯一维护方保持；V1休眠会话不自动唤醒。

## 归口联系表

| 范围 | 会话ID |
| --- | --- |
| 完整服务总负责、华为启动/验收、审查打包 | `01a1800e-80b4-7400-a78b-a84f5b6e888d` |
| 用户监控V2后端、搜索排行、TTFT情景/校准 | `01a18bc7-cdb5-7830-a185-ad3aa6257b21` |
| MA监控后端 | `01a18ab2-2600-7ae1-8b0e-979dad9ec3be` |
| 用户监控V2/搜索/MA前端 | `01a18c49-d9b4-7a33-8c04-e5a72adfcc24` |
| 低命中与公共分析结果/目录/通知 | `01a18be2-7112-7aa2-919b-5137d1f1b1ad` |
| Token异常私有后端 | `01a18fcd-0464-7cf1-b435-4f394bd33e66` |
| 异常分析前端 | `01a19111-344a-75c1-84e0-14db8be08f4f` |

## 新华为prompt必须覆盖的已有功能

不是新增产品需求，也不以本清单替代冻结设计。新总负责应从以下入口和已打包源码整理逐功能验收矩阵，每项给出数据/配置前置、操作、预期结果、证据和失败归口。

| 已有范围 | 不能遗漏的验证 | 依据 |
| --- | --- | --- |
| 服务与编码配置 | 包/镜像/配置身份，真实宿主预检，输入只读与state可写，同源前后端，三模型模式/别名/时间转换，任务提交/幂等/恢复 | [交付报告](../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/delivery/RV2_UNIFIED_REVIEW_20261101.md)、[部署说明](../../../deploy/monitoring/README.md) |
| 用户监控V2 | GB的appid×common_name隔离，运行/历史，指标与图表、明细/导出、质量说明，已实现TTFT情景与不可变历史 | [前端交互](../viewer/monitoring-v2/INTERACTION_V2.md)、[用户后端](../monitoring/v2-user/ENTRY.md)、[用户契约](../../contracts/user-monitoring-v2/README.md) |
| 搜索与排行 | APPID大小写敏感字面子串、%/_非通配符，命中/无结果，四项排序与AND上下界，稳定分页与revision冲突，切范围/返回定位，精确整数及NULL | [后端接入](../monitoring/v2-user/FRONTEND_HANDOFF.md)、[搜索实现批次](../viewer/monitoring-v2/batches/MV2-F003/PLAN.md) |
| MA监控 | GF规格×UUID，前后连续时间窗输入，全部UUID/实例展开，理想与实际对照、趋势/分布、质量/缺失/零区别，失败保留旧结果 | [MA设计与验收](../monitoring/v2-ma/ENTRY.md)、[MA契约](../../contracts/ma-monitoring-v2/CONTRACT.md) |
| 两类异常分析 | 同实例/同appid切方向，低命中L1–L3建议与L4/L5各一卡≤3例，Token T2–T4影响/建议/量化变化/局部证据，完成通知后拉取，历史/partial保留旧报告，详情返回，页面不触发分析 | [联合验证](../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/JOINT_VALIDATION_RV2_20261101.md)、[统一审查](../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/delivery/RV2_UNIFIED_REVIEW_20261101.md) |
| 跨功能恢复与结果报告 | 重启/断连/身份切换/错误重试/导出取消；现场证据与版本绑定，问题→归口修复→本地复验→必要新版本→现场复验，失败回退 | [协作流程](../../architecture/TASK_SESSION_WORKFLOW.md)、[最新执行记录](../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/UNIFIED_REVIEW_DELIVERY_EXECUTION_20261101.md) |

本机容器通过、SPA或capabilities返回200不能代替现场业务验收；合成数据与真实数据、功能正确性与TTFT真实性能校准分别记录。缺少现场访问、数据、生产策略或配置时列明具体缺口，不能把未执行项写成通过，也不能因只具备异常样例而省略监控V2。

## 冻结身份与新版prompt

已交付版本`tokenscope-rv2-20261101`，构建源码`45d9285210dc0b9edeb86c599c7b6bcd942f60b5`，镜像ID`sha256:483db762852b38ef54559cff1bb23ef668ea9296a055ce02aac44a809b427ce5`。本机交付收尾文档提交`7799a65c190f45a5ebd6c1132fb43d279bc38ad2`已push。

新总负责在`prompts/delivery`另存新版完整现场prompt，记录版本/路径/SHA256并明确替代旧prompt的现场执行范围。现有发布目录内的包体、旧prompt、manifest及SHA256SUMS保持冻结；仅职责/prompt修订不需要重建镜像。后续确需修复交付时由新总负责组织新版本，不能覆盖旧包身份。

## 实际通知

已通过既有会话工具向镜像打包与审查会话发送用户原话、职责转移、全功能范围、全部维护会话ID、新prompt要求及冻结身份；工具返回目标threadId。目标会话已明确回执接受完整服务总负责，确认覆盖用户监控V2、MA、搜索/筛选/排行/明细/导出/任务恢复及两类异常，并已开始按契约与固定45d9285源码另写新版prompt；冻结包不改。新版路径/摘要以该会话实际回传为准。

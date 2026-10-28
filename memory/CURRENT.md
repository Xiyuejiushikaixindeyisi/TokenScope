# 当前状态

更新：2026-10-28。**用户明确授权后，dev6/F007完整服务已完成WSL构建、容器/断网/恢复/浏览器验证及桌面交付；华为现场与桌面用户人工验收待执行。** 最新权威入口：[B006交付结果](../docs/tasks/monitoring/batches/B006/RESULT_20261028.md)。下方旧联合停点仅作历史，不覆盖本轮授权/实测。

## 从哪里开始

- 最新联合结果：[JOINT_RESULT_V1](../docs/tasks/monitoring/JOINT_RESULT_V1.md)；候选joint-v1-20261027，按SHA识别联合修正版。开发基线仍为B005.1 PLAN/S0/TESTS。
- 前端实施：[前端ENTRY](../docs/tasks/viewer/ENTRY.md)及其F批计划；锁定S0版本，实际接收/暂停恢复由该会话维护。
- 协作、文档权威、交接、联合验收与打包：[统一工作流](../docs/architecture/TASK_SESSION_WORKFLOW.md)。

## 实际进度

| 范围 | 状态 |
| --- | --- |
| 原监控后端 | B001–B005本机门槛通过；dev5/schema2、145项回归及真实HTTP合成E2E；不是完整服务验收 |
| B005.1 | S0契约1.0.0已固定、94项契约检查通过；S1–S5后端闭环，164项回归/真实HTTP合成E2E/压力通过；dev6/schema3/view1；联合修正后166项后端、143项前端回归及真实浏览器/压力通过，详见联合报告 |
| 前端 | 设计已批准；执行、S0接收与暂停原因统一读取[前端ENTRY](../docs/tasks/viewer/ENTRY.md)，不在公共记忆复制易过期状态或代其决定恢复 |
| B006 | P2已授权、P3/P4本机完成；镜像/代码/prompt已到Windows桌面，backup/20261028-monitoring-v1仅本地清单；P5华为现场待验收 |

## 工程与边界

项目本地.venv/uv.lock、固定编码资产；现有Git main，origin为Xiyuejiushikaixindeyisi/TokenScope；交付包见上述B006结果，包体不上传GitHub。生产CSV留现场，本机只用每模型5appid泊松合成数据。DeepSeek缺省思考、GLM CP映射、GF资产等价及V100现场性能仍未决。统一计量归监控，GET不触发分析；两类诊断和Agent按既定依赖，不自动新建会话。

[监控交接](handoffs/2026-10-27-monitoring-development.md) · [监控增量记忆](tasks/monitoring.md) · [实际会话登记](SESSIONS.md) · [一期目标输入](../docs/requirements/V1_SCOPE.md) · [协作记忆](COLLABORATION.md)


联合停点：本机完整服务验证完成；30,168条泊松有效请求、15范围、真实恢复/导出及压力证据已固定。V100现场与容器验收未执行。

Git协作见[Git工作流](../docs/operations/GIT_WORKFLOW.md)；此次整理见[仓库基线](../docs/operations/REPOSITORY_BASELINE_20261027.md)。个人直接合并main，不用PR；backup分支仅本地，两类分析分支待后续启动。

本机人工验收服务已保留在 http://127.0.0.1:8000 （完整前后端），输入data/incoming/manual-20261027，状态artifacts/runtime。三模型共30,168有效请求已分析；等待用户人工验收。启动和复现见README，Docker/打包仍未授权。



前端最新状态（2026-10-28）：用户回复“F007 通过”，0.1.0-f007已人工验收通过并closed，见[F007结果](../docs/tasks/viewer/batches/F007/RESULT.md)。后端或新session仍需打包前统一审查，Docker/镜像/交付包未授权；交接prompt已同步审批状态。

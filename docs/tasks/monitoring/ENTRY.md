# Token监控后端设计开发入口

2026-10-30：用户确认Token监控V1前端+后端验收通过，V1后端会话当前休眠。当前事实、现场workaround与后续分析边界见[验收交接](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)。异常分析先母会话调研/产品设计，再fork两线；最新状态见SESSIONS。

## 当前阅读顺序

| 用途 | 入口 |
| --- | --- |
| P0恢复 | [CURRENT](../../../memory/CURRENT.md)、[SESSIONS](../../../memory/SESSIONS.md) |
| P1现场启动验收 | [本轮交付结果](batches/B006/RESULT_20261028.md)、[完整服务执行prompt](../../../prompts/delivery/HUAWEI_MONITORING_FULL_SERVICE.md)、[部署说明](../../../deploy/monitoring/README.md)、[V100事实核对](../../huawei/README.md) |
| P1定位修复 | [CODEMAP](CODEMAP.md)、[实际API](../../contracts/MONITORING_IMPLEMENTED_API.md)、[当前计量设计](DESIGN.md)、[B005.1技术设计](batches/B005.1/DESIGN.md)、[固定S0](batches/B005.1/S0_CONTRACT.md)、[验证门槛](batches/B005.1/TESTS.md) |
| P2本机结果 | [联合报告](JOINT_RESULT_V1.md)、[B005.1闭环](../../../achieve/2026-10-28/docs/tasks/monitoring/batches/B005.1/RESULT.md)、[B006](batches/B006/PLAN.md) |
| P3历史 | [已关闭批次](batches/README.md)、[achieve](../../../achieve/README.md) |

## 维护与交接

本入口保留V1统一编码、计量、理想命中及契约基线；V1会话休眠，修复需用户启动。V2公共改动按工作流登记单一维护方。GET只读已有成果，两类分析复用同一实现；[分析启动边界](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)优先于旧状态文字。

[现场大文件调查prompt](../../../prompts/sessions/HUAWEI_MONITORING_LARGE_CSV_DEBUG.md)保留作故障回传模板。已收到报告，不能继续沿用“现场尚未收到”的旧状态；历史入口见[快照](../../../achieve/2026-10-30/snapshots/docs/tasks/monitoring/ENTRY.md)。不追改发布结果或重新打包。

## 当前V2分线入口（2026-10-30）

用户功能增加与MA监控分别由两个待fork的后端session调研、设计和开发，可并行；hybrid暂不做。先读[SESSIONS](../../../memory/SESSIONS.md)明确角色，再进入[用户功能](v2-user/ENTRY.md)或[MA监控](v2-ma/ENTRY.md)。[异常分析母会话](../analysis/ENTRY.md)独立于监控。UI-01初版已认可；本轮仅整理并push，不创建会话或展开详细设计。

## 早期V2产品交接（范围与顺序由上述分线更新）

V1已验收，用户提出V2：修复V1问题、P90 TTFT目标下的命中需求评估、appid排行搜索、定时数据库采集、MA集群压力/理想与真实命中对比；hybrid仿真最低优先级延后。MA为GF网关+motor路由+XPYD。详细产品输入、来源及待确认项集中于[监控记忆V2交接](../../../memory/tasks/monitoring.md)，避免另增设计文档。

V2由新session调研/设计/开发；本session仅完成产品讨论和V1交接，本轮未创建新会话或开发。当前建议不是已冻结规格，V1发布和S0保持不变，两个原因分析session分工不变。

[原V2启动prompt](../../../prompts/sessions/TOKEN_MONITORING_V2_START.md)仅保留父会话背景，不能覆盖当前分线。两线后续各自收敛设计/开发方案，本轮未启动详细设计、接口或代码。

[MaaS架构与监控概念参考](../../architecture/MAAS_REFERENCE.md)：用户2026-10-30说明的组件关系、请求生命周期、模型服务/规格、字段与SQL；明确MA集群=实例=一个UUID，当前GF＋motor＋3P3D、实例内Mooncake池化，以及V2按UUID统计理想/真实命中的产品要求。此文是结构参考，不是实施设计。

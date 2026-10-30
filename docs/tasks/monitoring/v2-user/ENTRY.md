# V2 用户监控后端功能入口

2026-10-30：待从V2 Token监控后端会话fork/登记，本轮不创建。实际角色/ID见[SESSIONS](../../../../memory/SESSIONS.md)。负责本线调研、产品收敛、后续设计与开发；首次先明确角色和阶段，不直接实现未获批方案。

## 范围与优先任务

- 给定P90 TTFT目标，评估用户需要达到的最低理想kv cache命中率。先收敛模型/部署/流量、真实性能校准、适用范围与证据不足时的表达，不从总体命中率承诺通用达标百分比。
- 搜索排行：请求长度众数区间、Token量、理想命中率和请求量；UI-01是认可起点，具体统计语义与用户收敛。
- GB数据，appid×common_name独立统计，当前暂定空缓存起步。服务级潜力不冒充生产实例命中。
- 与MA线并行，不等待其整线完成；不负责MA采集回放、异常分析、前端或hybrid。V1兼容/数据质量问题按实际影响提出，不默认启动所有历史修复。

## 阅读优先级

P0：AGENTS → CURRENT → SESSIONS → docs/README → 本入口。首次回复明确角色、范围、阶段、依赖、下一步；实际ID未知则如实登记。

P1：[产品记忆](../../../../memory/tasks/monitoring.md)最新决定、[MaaS参考](../../../architecture/MAAS_REFERENCE.md)、[UI-01](../../viewer/PROTOTYPE_V2_UI_01.md)与[HTML](../../viewer/prototypes/tokenscope-v2-demo-ui01.html)。核实V1时按需读取[DESIGN](../DESIGN.md)、[CODEMAP](../CODEMAP.md)、[S0](../batches/B005.1/S0_CONTRACT.md)、[实际API](../../../contracts/MONITORING_IMPLEMENTED_API.md)。

P2：产品记忆中Dynamo Planner、Vidur、kvcache-blog等已有来源及[现场验收](../../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)，按问题增量查证。P3才读历史，不全量阅读HTML/源码。

## 衔接

统一编码计量不分叉，公共修改先登记单一维护方。本线维护后续结果语义/契约，监控V2前端按固定设计/契约接入。研究与设计放本目录，阶段获批后再创建实际产物；增量记忆未来使用memory/tasks/monitoring-v2-user.md，公共记忆只留交接。不得预先生成全部设计、接口或batch。

# V2 同事侧MA监控后端入口

2026-10-30：待从V2 Token监控后端会话fork/登记，本轮不创建。实际角色/ID见[SESSIONS](../../../../memory/SESSIONS.md)。负责本线调研、产品收敛、后续设计与开发，先明确任务/阶段，不直接实现未获批方案。

## 范围与优先任务

- GF数据，model_standard_name×instance uuid；每个规格下每个实例单独统计理想/真实命中与流量压力。同UUID内跨appid和P共享prefix cache，不跨UUID混算。
- 优先讨论MA与用户监控数据隔离：MA按模型规格采集，再按UUID划分小数据；不用GB服务级数据直接计算GF实例对照。
- 用户暂定两侧空缓存起步；提出MA每30min或1h采集，缓存前一份数据，仿真重放“前一份＋当前份”。这是候选产品方案，具体频率及统计窗口未定，不等于已批准持久热缓存状态方案。
- 两份数据从空缓存重放提供有限历史预热，仍不能保证理想值≥线上真实值：线上可能有更早历史，缓存条件也可能不同。需与用户明确前份仅预热且只统计当前份，还是两份共同统计；后者必须配对同样两份真实数据。首次采集、缺前份/漏采、可比集合及重复读取边界由本线讨论，本入口不定算法。
- 与用户功能线并行，不等待TTFT阈值或排行完成；不负责用户侧TTFT反推、异常诊断、前端或hybrid。

## 阅读优先级

P0：AGENTS → CURRENT → SESSIONS → docs/README → 本入口。首次回复明确角色、范围、阶段、依赖、下一步，登记真实ID或未知。

P1：[MaaS参考](../../../architecture/MAAS_REFERENCE.md)、[产品记忆](../../../../memory/tasks/monitoring.md)最新决定、[UI-01](../../viewer/PROTOTYPE_V2_UI_01.md)与[HTML](../../viewer/prototypes/tokenscope-v2-demo-ui01.html)。页面按规格展示全部UUID，不要求先选单个UUID。核实V1时按问题读[DESIGN](../DESIGN.md)、[CODEMAP](../CODEMAP.md)、[S0](../batches/B005.1/S0_CONTRACT.md)、[实际API](../../../contracts/MONITORING_IMPLEMENTED_API.md)。

P2：[现场验收](../../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)及已有llm-d等来源；P3才读历史，不全量重读上游。

## 衔接

复用统一编码/计量/理想命中基础，负责实例共享场景及MA结果语义，公共修改先登记单一维护方。监控V2前端按固定设计/契约接入。统一内网访问已认可，本轮不实施服务发布。研究/设计放本目录，增量记忆未来使用memory/tasks/monitoring-v2-ma.md，阶段未启动不预建全部产物。

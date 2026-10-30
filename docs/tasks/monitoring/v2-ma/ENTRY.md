# V2 同事侧MA监控后端入口

2026-10-30：用户将原V2 Token监控后端会话指派为本线，已登记实际ID；见[SESSIONS](../../../../memory/SESSIONS.md)。已按最新授权完成两线交叉检查和[MA最终设计v1.0](DESIGN.md)，M000–M005已按授权完成开发及统一验收；[最终报告](batches/M005/RESULT.md)、[已实现API](IMPLEMENTED_API.md)、[代码地图](CODEMAP.md)和[设计对照](batches/M005/DESIGN_CHECK.md)为当前入口。235项测试通过，未部署或打包。

## 版本与前端接收

当前检查点ma-backend-local-1；先读[前端交接](FRONTEND_HANDOFF.md)、[版本记录](VERSIONS.md)和[Git检查点](GIT_CHECKPOINT.md)。MA协议1.0.0；合成样例16项。当前为本机后端完成后的维护/交接阶段，前端/现场/发布按各自流程验收。

## 范围与优先任务

- GF数据，model_standard_name×instance uuid；每个规格下每个实例单独统计理想/真实命中与流量压力。同UUID内跨appid和P共享prefix cache，不跨UUID混算。
- 优先讨论MA与用户监控数据隔离：MA按模型规格采集，再按UUID划分小数据；不用GB服务级数据直接计算GF实例对照。
- 初版由用户手动提供同规格pre和now两份各连续1小时的CSV；从空缓存回放pre预热，统计now的理想和真实命中率，按UUID分开。暂不实现自动采集，也不持久化仿真热缓存状态。
- 用户确认两份CSV增加prompt_tokens和request_time、增加实际未命中输入量；时间变化按5分钟一段并保留整小时平均，输入与实际未命中采用两张独立分布图。时间轴/质量/对照集合等具体工程口径见已获批设计及最终实现/测试记录。
- 预热仍不能保证理想值≥线上真实值：线上可能有更早历史，缓存条件也可能不同。可比集合、字段有效性、两种时间口径和重复读取边界已按设计实现，适用限制保留。流量画像用于识别值得开展GF路由对照实验的场景，不直接推荐最优算法或自动切换。
- 与用户功能线并行，不等待TTFT阈值或排行完成；不负责用户侧TTFT反推、异常诊断、前端或hybrid。

## 阅读优先级

P0：AGENTS → CURRENT → SESSIONS → docs/README → 本入口。首次回复明确角色、范围、阶段、依赖、下一步，登记真实ID或未知。

P1：[最终设计](DESIGN.md)→[交叉核对](CROSS_CHECK.md)→[batch计划](BATCH_PLAN.md)→[统一验收](ACCEPTANCE.md)→当前batch的PLAN/ISSUES/TESTS/RESULT；[本线记忆](../../../../memory/tasks/monitoring-v2-ma.md)、[版本索引](VERSIONS.md)。产品背景按问题读[MaaS参考](../../../architecture/MAAS_REFERENCE.md)、[UI-01](../../viewer/PROTOTYPE_V2_UI_01.md)及[HTML](../../viewer/prototypes/tokenscope-v2-demo-ui01.html)。核实V1按问题读[DESIGN](../DESIGN.md)、[CODEMAP](../CODEMAP.md)、[S0](../batches/B005.1/S0_CONTRACT.md)、[实际API](../../../contracts/MONITORING_IMPLEMENTED_API.md)。

P2：[现场验收](../../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)及已有llm-d等来源；P3才读历史，不全量重读上游。

## 衔接

复用统一编码/计量/理想命中基础，负责实例共享场景及MA结果语义，公共修改先登记单一维护方。监控V2前端按固定设计/契约接入。统一内网访问已认可，本轮不实施服务发布。研究/设计放本目录，增量记忆见[monitoring-v2-ma](../../../../memory/tasks/monitoring-v2-ma.md)。

开发已获授权且本机后端闭环。后续变更仍须当前batch完成实现、验证/测试和门槛，写完问题/测试/闭环及增量记忆再进入下一批；最终按MA01–14/X01–12核对设计符合性和E2E/健壮性。契约、前端、现场和交付状态分别记录，不因文档/模板存在写成已完成。

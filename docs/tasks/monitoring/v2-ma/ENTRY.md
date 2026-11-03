# V2 同事侧MA监控后端入口

2026-11-03 HV2-R1-MA：已完成缺数可解释投影与预热边界审查、本线合成及回归验证；已由V2总设计师独立验收冻结，前端、完整源码与固定镜像验收已通过，WSL打包及桌面全SHA交付完成；[当前发布](../../delivery/HV2_DELIVERY_20261103.md)，新版现场待验。[本轮完整交接](HV2_MA_BACKEND_HANDOFF_20261103.md)。原快照/指标/预热语义保持，旧结果不补写；DS源cached缺失与现场真实边界仍待补证。下方旧闭环仅代表对应版本。

2026-11-02统一交付同步：V2已完成WSL打包、桌面全文件SHA核对，华为真实数据待验；用户认可V2可交付，UIR-03暂不修、留V3，不作V2阻断。本角色职责/休眠状态不变；当前发布与实际结果见[交付记录](../../delivery/V2_APPROVED_DELIVERY_20261102.md)。现场只用真实Trace3/MA18 CSV，先用户监控（搜索/P90 TTFT）和MA，第一次用户验收并指定appid后才两类异常；SSH18002，唯一Markdown嵌关键源码/证据。[当前prompt](../../../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md) · [固定规则](../../../operations/DELIVERY_ACCEPTANCE_RULES.md)。下方旧开发/交接状态按历史阅读，不覆盖本决定。

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

## 2026-11-03 总设计师独立验收冻结（最新状态）

V2总设计师01a1800e-80b4-7400-a78b-a84f5b6e888d已明确通知：MA后端及契约工具独立通过，涵盖66项本线、13项工具，以及额外混合UUID原因隔离、0/null、桶与小时守恒核验。冻结清单：docs/tasks/delivery/HV2_MA_FREEZE_20261103.json；组合身份9b48fb244963ce153b009a9a2d0d9050d084bd6c1bb43eec27ddf49f313fd9fa。此状态覆盖前文候选待冻结的历史描述；冻结内容保持原字节。

本次冻结范围为MA新增availability资源及兼容契约工具，原指标和预热策略保持。源码窗口、工具窗口均已关闭；监控前端当前仅接入MA。本线转为等待问题后的归口维护，不再自行测试、提交/push或监听服务。后端独立验收不代表前端或华为现场验收；DS真实观测缺失、GLM真实冲突边界及现场完整证据仍待补证，不代签通过。

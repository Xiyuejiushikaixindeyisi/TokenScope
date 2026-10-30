# 前端下一阶段上下文：监控V2与异常分析

更新：2026-10-30。用户已启动初步展示设计；[UI-01原型与HTML入口](PROTOTYPE_V2_UI_01.md)已完成并待评审。本文件记录范围与交接，不是详细接口契约或正式代码开发计划。

## 已确认的起点与分工

- Token监控V1前后端已经用户验收通过，事实依据为[现场验收交接](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)。F007批准的页面骨架、层级和护眼风格继续作为视觉起点；不重新设计一套风格，也不覆盖既有验收记录。
- 用户明确监控V2与异常分析可并行推进。对应新session负责各自功能的调研、详细设计与开发；本前端session当前负责初步展示方案、DEMO及接口需求衔接，不代替其确定算法或冻结后端接口。
- V2 session已在[SESSIONS](../../../memory/SESSIONS.md)登记；两个分析session的实际ID仍以该登记为准。本轮未创建、唤醒或通知其他session。
- 统一编码、计量和理想命中实现继续归监控维护；页面消费已有成果。自进化Agent的启动依赖不变。

## 当前展示范围（最新用户输入）

| 方向 | 面向对象与展示目标 | 基础材料 |
| --- | --- | --- |
| 用户版监控增强 | GB层，appid×模型服务common_name视角，增加P90 TTFT目标对应的最低命中需求展示、搜索与排序 | [V1批准交互设计](MONITORING_INTERACTION_V1.md)、[V2产品讨论](../../../memory/tasks/monitoring.md) |
| 同事版监控 | 独立新页面；GF层按模型规格model_standard_name×UUID统计，选中规格后直接展示全部UUID的理想/真实命中和流量，同UUID跨appid共享缓存 | [V2产品讨论及字段口径](../../../memory/tasks/monitoring.md) |
| 异常分析展示 | 延续appid×模型下的低命中率、Token异常两类业务建议；展示具体问题、证据、修改建议与可提供的收益和例子 | [既有报告设计](DESIGN.md)、[业务建议卡片DEMO](../../../artifacts/prototypes/monitoring-v1/tokenscope-monitoring-with-reports-v2.html) |

用户版与同事版页面分开；原型采用同侧栏下独立页面，具体布局待用户评审。并行准备展示不改变V2产品讨论中已认可的功能实施优先级。

旧HTML文件名中的“with-reports-v2”指报告展示第二稿，**不是Token监控V2产品原型**。

## 衔接时必须保留的口径

以下沿用现有记忆和已批准的展示原则，不是本轮新增接口设计：

- P90 TTFT最低命中需求仍是产品目标；仅靠总体命中率无法保证反推出唯一阈值。性能校准、适用模型/规格/负载与结果可信范围由V2 session确定；DEMO中的示例不得写成已验证能力。
- 理想与真实命中对比需标明统计窗口、请求覆盖、分母及缓存初始状态。V1是窗口内冷启动理想回放，不能默认它必然高于线上热缓存命中率，也不能直接用差值归因为路由问题。
- 模型规格是GB按模板前长度分流的标签，UUID标识一个MA实例（GF＋motor＋3P3D），同UUID内跨P/跨appid共享已确认，详见[MAAS_REFERENCE](../../architecture/MAAS_REFERENCE.md)。压力指标、观测粒度和更新频率仍待对应session收敛。不把处理开始时间直接当作GF请求到达时间，不把流量自动等同于硬件利用率。
- V2已记录源字段prompt_tokens/cached_tokens/model_ttft/model_tpot等用户语义，但完整性、单位和范围尚需验证；前端不假定它们已加入V1冻结S0。
- 分析结果由探测器提供。断点位置、来源映射、建议、置信度/覆盖率、收益、例子等实际可展示内容由分析session决定；缺失信息不补造。session/turn/工具调用链不能从现有输入直接认定可得。
- 报告展示最近一次已发布的完整分析，标明分析时间及数据范围；一个月前的结果仍可保留。页面访问不触发分析，不周期轮询报告；业务建议不混入任务状态列表。
- 前端沿用完整结果与缓存原则；MA观测的时效另行讨论，不把V1两小时回放耗时当作V2实时更新能力。真实数据质量/有效子集范围应保留，不能因展示简化而变成全量结论。

## 阅读与输出位置

1. P0：AGENTS → memory/CURRENT → [前端ENTRY](ENTRY.md) → 本文件。
2. P1：V2读[产品讨论记忆](../../../memory/tasks/monitoring.md)；分析读[报告设计](DESIGN.md)和既有DEMO，再按需进入[低命中分析](../prefix-analysis/ENTRY.md)、[Token异常分析](../length-analysis/ENTRY.md)。读取对应session的新设计/契约后再明确正式交互。
3. P2：按具体问题读监控DESIGN、冻结S0、源码地图或现场证据；无需重读全部源码和已闭环批次。

展示文档放docs/tasks/viewer；本轮原型统一放artifacts/prototypes/monitoring-v2/，复用已有报告并整合到同一HTML，不再另建analysis-v1副本。验证产物放artifacts/validation/viewer/v2-ui-01/。保留monitoring-v1中的获批HTML及摘要，不覆盖旧基线。

交给对应session的材料应区分：已确认展示目标、合成样例、所需数据/语义、待后端决定项。DEMO评审不等于接口冻结或正式代码开发授权；后续仍按batch记录开发、问题、测试与闭环。打包归审查打包session，另行按用户授权执行。

## 2026-10-30 最新交接决定（覆盖前述本会话继续开发的默认理解）

用户认可UI-01初版，后续由监控V2前端、异常分析前端两个新session接手；原会话提供原型与交接。相应产品/后端设计基本固定、接口冻结后，按[工作流](../../architecture/TASK_SESSION_WORKFLOW.md)逐阶段讨论审批。启动prompt及HTML视觉入口见[ENTRY](ENTRY.md)。最终获批DEMO的配色和布局必须严格迁移；HTML直接用于视觉研究，不要求先读生成源码。当前反馈不是后续优化稿/交互设计/开发计划自动通过。

2026-10-30用户再次明确：HTML必须沉淀到docs作为风格/配色/布局入口。当前为[UI-01 HTML](prototypes/tokenscope-v2-demo-ui01.html)，原HTTP预览已撤下；此项覆盖前述仅放artifacts的原型产物约定。未来获批HTML也归对应前端任务的docs/prototypes，生成材料可留artifacts。

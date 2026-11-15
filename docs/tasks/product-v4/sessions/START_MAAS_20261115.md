# 副本2启动prompt：MaaS简单试点与后续场景架构粗评

你是用户2026-11-15明确要求fork的副本2，负责MaaS架构研究。你继承背景，不继承主会话身份；不要重复fork、替其他角色登记或执行主会话的Git提交任务。

本次工具登记的副本ID为`01a1de7c-a6fd-7043-baa7-987f03d5af3c`，应用标题“TokenScope V4 MaaS架构与试点”；这不代替你首次启动的环境自核。

## 身份与首读

项目根`/home/zhangxiyue/TokenScope`，Windows为`\\wsl.localhost\Ubuntu-22.04\home\zhangxiyue\TokenScope`。首先从自己的环境获取实际session/thread ID，未知写未知，不能沿用父ID或V3／镜像ID。对照memory/SESSIONS.md中副本2的fork工具ID，把本人核验记入本线ENTRY和memory/tasks/product-v4-maas.md；不一致如实记录，主会话统一维护共享登记。

按顺序读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md、[本线ENTRY](../maas/ENTRY.md)、[三会话协作](../SESSION_COLLABORATION_20261115.md)、[长期资料路由](../V4_REVIEW_PACKAGE_20261115.md)。然后读[三架构研究](../INFERX_DEEPSEEK_MOONCAKE_ARCHITECTURE_COMPARISON_20261114.md)、[P2核对与试点输入](../HUAWEI_P2_REVIEW_AND_PILOT_INPUTS_20261115.md)及其原回传、MaaS现有架构；从现网流量研究理解服务需求。专题调研与原证据按问题追溯，不重复泛化全量调研。

## 两阶段目标与先后

**阶段A：简单试点设计与初步结果。** 固定模型DeepSeek-V4-Flash-0731，两个appid：`com.huawei.ucd.uiplus.wa`、`com.huawei.cloud.ioc.global`。先讨论如何验证缓存集中与服务表现，争取简单、快速、可解释的初步效果，暂不叠加多个长度物理池。P2是次高优先级先行试点资料，不是整个MaaS架构的替代。

形成可与用户讨论的实验设计：问题与假设、可比较的基线和处理条件、请求集合／顺序／窗口／预热口径、模型及缓存兼容身份、输入输出负担与承载未知、成功／无效／失败如何区分、需要的最小数据、执行边界、验收节点及结果呈现。提出备选和取舍，不预定未经核实的引擎实现、拓扑或容量数字。

P2存在集合对账、req/s与并发混比、规格标签当硬上限、TokenScope配置当生产引擎配置等问题；不能据此宣布单MA吃得下。用户理想H/P不等于实际cached_tokens；GF TTFT不含GB排队；req/s不是任务／卡分钟。设计可以在已知材料基础上推进，只补影响本实验的关键证据，不要求全量监控重跑。

与用户讨论设计后，再按已定范围准备prompt-3的数据整理、生产数据重放与结果采集材料，区分每份用途／输入／输出；文件编号在设计时明确，不沿用历史重复编号。**编写执行prompt不等于授权现场部署或重放。** 由用户转交华为执行并回传，现场保留已验收V3服务、真实数据和版本身份。没有回传前不写“已取得初步效果”。

**阶段B：有初步试点结果后，形成待同事粗评的场景分类MaaS架构材料。** 以自身业务、试点与三架构参照为依据，解释场景／关键步骤如何表达服务需求，模型选择、缓存亲和与实时负载如何协同，尤其GB/GF/独立MA无跨域共享KV时的热点取舍。给现状、候选方向、依据、未知、代价与粗评问题，明确“待评审”，不冒称生产实施设计或用户最终批准。

既有用户判断保持：场景决定服务策略，长度／实时负载决定承载；未来先建立长度观测桶，观察计算耗时、KV占用、批次干扰和SLO变化，不预定8K/32K/64K/128K最佳物理池。复用编码结果当前不优先；粗估用于软调度可保留候选，Tokenization成本与实现讨论继续pending，不夹带进简单试点。阶段B依赖阶段A初步结果，不因fork立即全面展开。

## 协作与交付

首轮自核身份并读完关键材料，先给用户试点设计讨论提纲、现有可用证据、最小未知项和需决定事项。可创建`maas/PILOT_DESIGN.md`讨论稿，定稿范围由用户决定；结果归档`maas/PILOT_RESULTS.md`，没有实际回传不建假结果；后续粗评材料为`maas/SCENARIO_GATEWAY_REVIEW_DRAFT.md`及必要图件。载体变化按用户讨论决定，不自动建设新系统。

你拥有`maas/`、三架构研究正文、P2核对正文、`memory/tasks/product-v4-maas.md`；原报告／原HTML保持。现网业务分类由副本1维护，跨线需求在本线HANDOFF.md说明后交主会话协调，不自行改另一线正文。最终HANDOFF包含文件路径／摘要、实验身份、结果／未验证项、证据限制、待粗评问题与可纳入V4汇报的内容。

主会话审核两线产物、统一汇报／入口／CURRENT／SESSIONS并正式Git提交；副本不commit/push，不全局reset/clean。与其他会话默认通过共享文件及用户转交协作，本次fork不自动授权跨会话消息、再建会话／子agent或自动化。用户直接决定实验范围、SLO与协作节点；不改产品／锁文件、代开发测试、启动服务、现场部署、构建或发送同事消息。未来粗评稿由用户决定何时转发同事。

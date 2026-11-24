# TokenScope V4入口

**2026-11-24分流：** [V4.1](simulator-v41/ENTRY.md)由原session完成本机E2E，不需要镜像/代码交付包或华为验证；[V5产品方向](../product-v5/ENTRY.md)独立准备，不阻塞V4.1。11-13旧启动prompt已转历史索引，勿据旧“待启动”文字新建重复开发线；既有汇报/研究按各入口继续。

2026-11-13用户已认可V3验收通过。V4核心仅两项：**汇报**、**模型演进**；优先验证小版本间Tokenizer/Chat Template能否复用。产品角色已由用户启动首轮需求与方案；各角色以本人登记为准，不等于前端改版、产品编码、现场分析或打包已获实施批准。

**2026-11-15最新：用户授权本产品会话fork两次，职责和实际ID已登记。** [三会话分工与启动prompt](../product-v4/SESSION_COLLABORATION_20261115.md)：主会话继续V4汇报方案／成品审核／提交；副本1形成流量与用户协同优化HTML；副本2先简单试点，有初步结果后形成场景分类MaaS架构待同事粗评。两个fork已创建、待用户首次启动；本轮一次本地Git，不push、不现场执行。资料层级保持，Tokenization继续pending，产品／旧HTML审批不因fork改变。

高优先级正文：[现网流量研究](../product-v4/PRODUCTION_TRAFFIC_STUDY_20261114.md)、[三架构研究](../product-v4/INFERX_DEEPSEEK_MOONCAKE_ARCHITECTURE_COMPARISON_20261114.md)，分别由副本1／2维护。完整证据路由见[产品入口](../product-v4/ENTRY.md)；[MA画像](../../huawei/MA_TRAFFIC_PROFILE.html)来源附件仍缺。次高优先级：[P2核对](../product-v4/HUAWEI_P2_REVIEW_AND_PILOT_INPUTS_20261115.md)。本轮只完成三线启动安排，试点与架构方案尚未形成。

## 按角色进入

| 角色 | 状态/身份 | 首读与启动 |
| --- | --- | --- |
| V4主会话：汇报统筹与审核 | 01a1d3e3-0c34-7320-bf6f-14438c120aed；统一方案、审核两线材料、入口／记忆及提交 | [启动](../product-v4/sessions/START_MAIN_20261115.md) · [主ENTRY](../product-v4/ENTRY.md) |
| V4副本1：现网流量研究 | 01a1de7c-8ea4-7cb2-b8e6-114aeba29a60；同目录fork，待本人自核／用户首次启动 | [启动](../product-v4/sessions/START_TRAFFIC_20261115.md) · [ENTRY](../product-v4/traffic/ENTRY.md) |
| V4副本2：MaaS架构与试点 | 01a1de7c-a6fd-7043-baa7-987f03d5af3c；同目录fork，待本人自核／用户首次启动 | [启动](../product-v4/sessions/START_MAAS_20261115.md) · [ENTRY](../product-v4/maas/ENTRY.md) |
| V4模型演进与开发（拟定角色名） | 待启动；实际session ID未知，不继承V3 | [复用核查表](MODEL_REUSE_MATRIX.md) → [协作](COLLABORATION.md) → [开发启动prompt](START_DEVELOPMENT.md) |
| 镜像打包与审查 | 既有01a1800e-80b4-7400-a78b-a84f5b6e888d，持续版本职责 | [交付入口](../delivery/ENTRY.md) |
| 华为现场agent | 实际ID未知；prompt-1及MaaS prompt-2回传均已在项目内，后者口径初审待核；本机未远端执行 | [本轮四份探索prompt与回传](../product-v4/ENTRY.md)；[模型资产盘点](START_HUAWEI_READONLY.md)单独按授权，不自动并入 |

本轮主会话已按用户明确指令创建两个fork；三prompt与身份来源见上述入口。副本进入后核实本人环境ID，未知写未知，不重复父会话创建／Git任务。本轮未发跨会话消息、未唤醒旧线；后续按共享HANDOFF及用户转交协作，不自动新增会话。

等待回传期间的[公开MaaS分流调研](../product-v4/MAAS_ROUTING_RESEARCH_20261114.md)及[DeepSeek共享KV专项](../product-v4/DEEPSEEK_ROUTING_AND_SHARED_KV_20261114.md)已完成，现为高优先级资料体系中的重点专题支撑：区分场景策略、跨MA缓存亲和与实例内部调度；不冻结两类硬分池、取消全部长度调度或10P5D。当前阶段按页首决定，不从旧“下一轮”表述恢复未来架构讨论。

用户进一步要求整体企业MaaS架构调研，已完成[供应商比较＋三份回传的业务判断](../product-v4/ENTERPRISE_MAAS_ARCHITECTURE_RESEARCH_20261114.md)。重点是任务/步骤服务策略、可选模型边界、独立缓存与负载取舍；优先三类大流量输出分布。三份报告是研究输入，H不是实际命中，尚无TTFT/TPOT实测比较，不能当生产效果已验收。原件及现场prompt保持不变。

## 继承上下文

- [V3用户验收收口](../delivery/V3_USER_ACCEPTANCE_20261113.md) · [补证核对与数字](../delivery/V3_C04_SUPPLEMENT_REVIEW_AND_CLOSE_20261113.md)。V3已通过，不再保留用户验收待定作为当前阻断；已知有限覆盖/业务风险仍如实表达。
- 发布tokenscope-v3-c04-20261112，源码57fe9f64d78f6363ee18a12ff97693e00ae1fe3d；[发布记录](../delivery/V3_C04_DELIVERY_20261112.md)。Git后续文档commit不改变该产品身份。
- 产品仍为用户监控、搜索与排行、异常分析、MA集群监控四入口，原V2布局/L4/L5及C04获批DEMO为基础；[批准DEMO](../development-v3/prototypes/repair-demo-r1/index.html)。不因“汇报优化”另造产品模块或擅改页面。
- [实际session登记](../../../memory/SESSIONS.md) · [V4产品记忆](../../../memory/tasks/product-v4.md) · [V4开发记忆](../../../memory/tasks/development-v4.md)。两个V3会话及V2/V1维持休眠。
- Token新探测器、组合方案评估、Agent/hybrid/SSD和生产路由改造不自动启动。用户2026-11-13已将三阶段优化路线与Infra场景分流/缓存路由双试点纳入汇报方案及定向取证，详[方向与节点r2](../product-v4/V4_DIRECTION_AND_MILESTONES_20261113.md)，不沿旧范围把这些新议题排除。

优先级：本轮按新prompt阶段收证据；旧r2“优化路线三阶段”不等于本轮prompt-1三阶段编号。阶段3完整对象由四象限HTML固定：22个appid、23组、124,913条；每appid独立Markdown，跨模型分章。MaaS先req/s及现成配置/容量证据，再讨论prompt-3。模型原分工保留，不因本轮材料启动页面或部署。

## 原V3会话提供的上下文补充

用户另行安排两条V3线整理交接，已生成[产品上下文](../product-v4/ENTRY.md)和[开发上下文](../development-v4/DEVELOPMENT_CONTEXT_20261113.md)。这些是经验/需求补充，不是另起两套当前任务；本目录SCOPE_TASKS及用户最新决定为V4范围依据，不继承旧会话ID。

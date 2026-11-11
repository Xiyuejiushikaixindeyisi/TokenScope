# TokenScope V3 调研与产品设计入口

2026-11-11交付进展：用户已授权镜像会话审查通过后版本整理、Git提交/push和镜像打包，准备华为代码包、镜像、使用prompt并保留已有数据/结果。[完整prompt](acceptance-v3/PACKAGING_REVIEW_PROMPT_20261111.md)已发送，镜像chat已active；[发送回执](acceptance-v3/PACKAGING_SEND_RECEIPT_20261111.md)。本线不执行Git或构建，现场验收仍待后续安排。

当前结论（2026-11-11）：用户确认“V3先交付小样本分析，显式全量评估延后”。候选repair-r1-02身份复核不变，**LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING**；[验收收口](acceptance-v3/CLOSE_20261111.md)、[给镜像打包与审查的完整prompt](acceptance-v3/PACKAGING_REVIEW_PROMPT_20261111.md)。10实际页面/9窗独立核算/104后端/34前端兼容/重启读取通过，BUS五组及真实负载AC-MEM仍待现场。本线不修改代码，本轮未Git/构建/部署；跟踪自动化交付prompt后停止，状态见[验收入口](acceptance-v3/ENTRY.md)。以下11-10段落为分工及历史背景，不覆盖本次收口。

最新职责（2026-11-10）：**本session不修改代码。V3开发会话完成开发并交出确定候选/测试证据后，由本session独立验收，记录问题交开发会话修复并复验，再整理给“镜像打包与审查”的交接prompt。** 验收按四P0及两项修订、已有冷启动规则执行；本地工程与待现场业务验收分开记录，不代签未验证项。当前仅登记分工，不提前运行验收或打包。详见[本人记忆](../../../memory/tasks/product-v3.md)及[协作流程](../../architecture/TASK_SESSION_WORKFLOW.md)。

最新任务（2026-11-10）：四P0简评已完成。用户明确授权：开发会话先在计划/验收中修订“自动L1 clock闭环、历史轮次不同不误筛候选”两点，修订完成后即可进入开发。见[评审决定与条件授权](V3_REVIEW_DECISION_20261110.md)。研究会话仅转交结论与维护记忆，不接管开发。[Token回传判断及V3.5投入分析](V35_TOKEN_TAIL_ASSESSMENT_20261110.md)已完成，Token私有修复仍留V3.5。以下归档轮状态为历史时点，不覆盖最新授权。

2026-11-10：用户确认本线、镜像打包与审查、V3代码修复与开发为三个活跃角色，六条V2开发线休眠。本线负责证据/产品方案/宣传/交接，不承担代码开发。低命中四P0方向保持；新开发[独立CHECK](../development-v3/CHECK.md)已完成。Token异常修复留V3.5；回传文件已到目录，待正式核验后细化范围/顺序/验收，当前不实施。

实际会话 `01a1a5d5-4baf-7a41-b5c6-14bd5f4f67c2`；11-10环境THREAD/SESSION一致复核。本轮负责[V2归档](../../../achieve/2026-11-10/v2-session-dormancy/README.md)、共享角色/导航及用户授权的[活跃会话通知](../../operations/SESSION_SCOPE_REGISTRATION_20261110.md)，两线已本人登记回执。镜像会话仅审批/打包；开发ID `01a1c449-6a9b-7a83-912a-5a9ff77c703d`。本轮不提交Git，前序文档提交9a071c8已推送。见[SESSIONS](../../../memory/SESSIONS.md)、[本线记忆](../../../memory/tasks/product-v3.md)。

阅读顺序：AGENTS → CURRENT → SESSIONS → docs/README → 本页 → [当前范围与分工](V3_SCOPE_AND_HANDOFF_20261110.md) → [四P0修复简案](V3_LOW_HIT_REPAIR_BRIEF_20261110.md)。现场依据按需读[低命中实际回传](../../huawei/TOKENSCOPE_V3_LOW_HIT_EXPLORATION_20261109.md)，保留其中收益/采样/预算局限。新开发角色直接使用[精简入口/代码地图](../development-v3/ENTRY.md)及[启动消息](../development-v3/START_PROMPT_20261110.md)，不用全量恢复本线研究历史。

取证入口：[华为三组Token长尾探索prompt](HUAWEI_TOKEN_TAIL_EXPLORATION_PROMPT_20261110.md)及[回传文件](../../huawei/TOKENSCOPE_V35_TOKEN_TAIL_EXPLORATION_20261110.md)。已读全文并核对相关源码/表内算术；局限与不采纳的推断见最新判断，未运行现场复现。区分报告结论、代码复核和用户范围决定。

**高优先级资料：[四象限明细HTML](promotion/quadrant-detail/dist/index.html)**及[说明/口径](promotion/quadrant-detail/README.md)，用于负载画像和探索选点，不能凭长尾直接断言浪费。四页宣传稿与r0研究保留，能力事实仍以对应版本代码和证据为准。

按需历史：[11-05证据交接](HV2_EVIDENCE_HANDOFF_20261105.md)、[初始研究任务书](RESEARCH_BRIEF_20261104.md)、[旧启动prompt](../../../prompts/sessions/TOKENSCOPE_V3_RESEARCH_PRODUCT_START_20261104.md)、[V2交付身份](../delivery/HV2_DELIVERY_20261103.md)。这些不覆盖最新四P0、Token休眠与新开发分工。

[原补充取证prompt](../../../prompts/delivery/HUAWEI_V3_EVIDENCE_APPENDIX_20261104.md)已归档，新报告已收到但部分取证未完成；缺口转入阶段收口，不因旧prompt自动追加现场任务。

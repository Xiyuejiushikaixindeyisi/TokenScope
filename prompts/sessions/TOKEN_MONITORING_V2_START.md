> 2026-10-30状态更新：本prompt是V2父会话历史启动背景。当前改为用户功能增加与MA监控两条并行后端线，hybrid暂不做；新session先按memory/SESSIONS.md确认角色，再分别读docs/tasks/monitoring/v2-user/ENTRY.md或v2-ma/ENTRY.md。下方旧串行优先级不再作为当前依赖。本轮仅整理并push，尚未创建fork。

你负责TokenScope的Token监控V2。项目根目录为/home/zhangxiyue/TokenScope，Windows可经WSL UNC访问。

当前只开展产品讨论与业界调研，与用户共同收敛用途、范围、优先级和数据依赖。不要直接编写详细设计、接口契约、开发batch或代码，不修改V1运行配置，不部署或打包。后续进入设计、开发由用户明确决定。本prompt不是实施批准。

一、先恢复上下文，按需阅读

1. AGENTS.md → memory/CURRENT.md → memory/SESSIONS.md → docs/README.md → docs/tasks/monitoring/ENTRY.md。
2. memory/tasks/monitoring.md：V1维护记忆、V2产品输入、已有调研来源和待确认项。
3. docs/huawei/MONITORING_V1_ACCEPTANCE_20261030.md：V1验收事实、现场workaround、数据覆盖与证据限制；需要核实时再读其链接的原始报告。
4. 仅在核对现有能力时按问题查阅：docs/tasks/monitoring/DESIGN.md、CODEMAP.md、batches/B005.1/S0_CONTRACT.md、docs/contracts/MONITORING_IMPLEMENTED_API.md。它们描述V1，不是V2已批准设计。
5. 协作边界见docs/architecture/TASK_SESSION_WORKFLOW.md；交付身份见docs/tasks/monitoring/batches/B006/RESULT_20261028.md。不要全量阅读历史文档、全部源码或上游仓库。

在memory/SESSIONS.md登记实际会话ID与“V2产品讨论/调研”状态；无法获得ID则写未知。先读最新共享文件，只更新自己的记录，不覆盖其他session进展。

二、V1基线

用户于2026-10-30确认监控V1前端+后端验收通过。发布monitoring-v1-20261028，包内源码92236ee993974e740d085e22e49b6b93c9487430，后端dev6、前端F007、S0 1.0.0、control schema3/view1。这是已交付版本身份，不等于当前工作树HEAD。

V1对手动提供的CSV离线分析：hash_id、appid、model_handle_start_time、completion_tokens、request_input。request_input是GF转换后的OpenAI请求原始JSON文本；纯文本模型，包含工具定义/调用/文本返回。

统一编码与计量、理想命中仿真由监控维护。模板前统计完整原始JSON；模板后统计实际模板编码；输入重算与输出分别统计。每CSV空缓存、无限容量、前一请求可缓存输入立即对后一请求可用；按租户×模型回放。GLM/Qwen/DeepSeek目前共用普通链式近似，默认block分别128/1536/32，不能称为精确hybrid仿真。无效行跳过，重复hash_id仍为独立请求。后端提供权威统计、分位数和直方图，前端展示已有结果。

华为CPU容器8核/32GiB完成三模型约26GB输入，单文件约22–55分钟；354,638条读入、150,698条有效、77个模型×appid范围。此性能只证明当次有效子集与现场配置，不外推全部数据/部署。

三、V1遗留问题

- DD/MM/YYYY时间通过现场预处理转为ISO，兼容问题尚未由源码解决；UTC导出口径仍需确认。
- 生产模型变体通过API注册别名解决，需要产品化配置，不应放宽为任意模型匹配。
- DeepSeek现场选择thinking_disabled，尚不等于生产缺省思考模式已确认，不得静默默认false。
- 有效率约41%–53%；非标准JSON、导出保真和跳过原因需要核实。不能把有效子集当全量流量；不能静默改原始JSON后仍称原文Token计量。
- GF编码资产等价、GLM CP映射及报告内部分计数差异，继续保留为待核对项。验收通过不等于所有workaround已经代码化。

四、用户已认可的产品推进顺序

1. V1兼容与数据质量问题＋appid搜索/排行：按请求长度众数区间、Token量、理想命中率、请求量排序；讨论输入/输出/重算量区分、众数占比、多峰与可比窗口。
2. 自动、定时从数据库采集：支持持续监控；讨论采集窗口、延迟、失败/补采、重复读取与结果完整性。保留CSV离线入口的价值，不先决定具体数据库连接方案。
3. MA集群观测：用户定义MA=GF网关+motor路由+XPYD，不自行推断XPYD拓扑。评估各MA集群理想/真实命中差距，以及到达率、QPS、长度分布、Token速率、排队/并发、TTFT等，用于判断压力和选择适合的proxy路由策略。
4. 经性能校准的TTFT目标评估：给定P90 TTFT，评估指定模型/部署/流量场景下所需最低prefix cache hit及可达性。总体命中率不能唯一反解P90；研究有条件估计、区间和证据不足/不可达的表达，不承诺通用保证值。
5. Hybrid attention prefix cache仿真：最低优先级，延后，优先等Ascend官方实际实现后再研究开发。

推进顺序已认可；具体功能边界、算法、接口和实施计划尚未批准。“支持策略选择”不自动包含生产路由自动切换。

五、产品讨论优先确认

- 数据库类型、可读表/字段、只读采集条件；请求能否关联MA集群、实例与motor策略，是否存在重试/迁移。
- 能否取得GF接收/request_time、逐请求TTFT、实际命中Token、输入Token、队列/并发及缓存层级信息；TTFT从哪里开始、到哪里结束。
- 现有model_handle_start_time不能代替到达时间；现有五列不足以完成全部V2目标。
- 实际与理想命中对比需对齐请求范围、Token分母、窗口、租户隔离与缓存拓扑。V1窗口内空缓存与线上历史热缓存不同，真实命中高于该窗口“上限”不必然是错误；连续窗口缓存口径需要讨论，不能静默改变V1。
- 两小时深度分析与短时压力观测的时效需求分别是什么；首先支持人工策略建议/效果对比，是否自动切换另议。
- 定时采集重试防重不能等同于按hash_id删除合法重复请求；数据不完整时指标与排名如何提示。
- TTFT评估需要哪些真实性能数据，哪些部署配置影响适用范围；没有证据时应明确无法估计。

六、已有调研，可继续核实而非从零重复

memory/tasks/monitoring.md保存官方链接。本机/home/zhangxiyue/kvcache-blog只读参考，已核对版本9659c4a26f4e7eabfb4867c4ea80b50fc30ff913：提供容量—命中率与理想prefill加速评估，尚未找到直接反求P90 TTFT最低命中率的证据。

优先对照：llm-d的集群/路由观测与预测延迟；Dynamo Planner和Vidur的性能校准/工作负载评估；SGLang Model Gateway的缓存与负载权衡；Langfuse/LiteLLM的租户用量、排行和网关指标。区分产品可借鉴之处、论文/工具假设、实际版本支持与Ascend适用性；不要把宣传能力当本项目已具备能力。

七、协作和首轮产出

本session负责监控V2，与“命中率低原因分析”“Token异常分析”两个session分开；诊断复用监控统一实现，不复制第二套计量。现有前端session负责界面，审查打包session负责获授权后的交付。不要自动创建/唤醒其他session或委派子agent。

首轮阅读后先用简洁文字说明：你理解的V2产品目标、V1可复用基础/遗留问题、对已认可优先级的理解、现有数据缺口；再围绕当前最关键问题与用户讨论，并继续必要的官方资料调研。只增量更新产品讨论记忆和必要证据，不输出详细设计或开始修复代码。不要要求上传绝密CSV；需要现场证据时准备单份md回传prompt，关键源码与脱敏证据嵌入正文。镜像/交付包必须另行获得用户同意。

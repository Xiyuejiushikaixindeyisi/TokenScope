# 可直接发送：TokenScope V5产品设计

你负责TokenScope V5产品设计，与用户讨论产品定位、需求优先级、数据口径、交互和验收方案。当前只做研究/讨论及文档记忆，不改产品代码、配置、资产锁或冻结契约，不开始页面制作、打包、现场验证或Git提交/push。

项目根：/home/zhangxiyue/TokenScope；Windows对应\\wsl.localhost\Ubuntu-22.04\home\zhangxiyue\TokenScope。所有新材料放本项目，兄弟项目仅只读参考。

先读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md，再读docs/tasks/product-v5/ENTRY.md和USER_DIRECTION_20261124.md。获取本人实际session ID，登记V5产品设计身份/当前阶段和memory/tasks/product-v5.md；获取不到写未知，不沿用镜像会话或V4.1 ID。只增量维护自己负责的文档，不覆盖其他session记忆。

版本边界：V3已通过用户验收。V4.1是小版本，由原session独立完成本机端到端验证，不需要镜像/代码交付包，不需要华为机验证。V4.1已获授权开发且正在收尾，不要按旧启动prompt把它降回只读，也不要给它增加V5需求或新验收关卡。只读docs/tasks/v4/simulator-v41/ENTRY.md与V41_BATCH_EXECUTION.md了解最新交接，不修改该目录/源码/契约/验证、候选服务和state，不重做其测试。你可立即开始产品讨论，无需等待V4.1完成。

用户提出六项V5方向：
1. 大量非法JSON：用户数据质量不高且难改，TokenScope需要更强的处理能力。讨论哪些错误可确定恢复、哪些有语义歧义，保留原文/来源/diff，批量失败隔离和质量统计，避免静默猜测业务内容；先找代表坏例与实际数据链路，不立即选定修复库或LLM方案。
2. 四象限的两个核心指标是平均输入长度和理想命中率。用户希望讨论用平均输入长度替代主展示中的原始JSON Token。候选定义为同appid×模型服务/同范围内有效prompt_tokens总量÷有效请求数，需讨论修复/失败/重复记录及空值处理；不自动删除旧字段、历史证据或导出兼容。
3. 搜索与排行应独立于用户监控当前选中的模型服务，覆盖所有已完成分析的模型服务，支持全范围排序及独立筛选，不以重新分析数据实现。用户报告了耦合现象，具体前后端原因尚未复现，不预先定责。
4. 用平均输入长度排序替代众数区间排序。明确行身份、统计窗口、结果版本、并列/缺失值与分页；不是删除所有直方图或众数信息。
5. 平均输入长度高于10k且命中率低于50%时，启用低命中率分析。按上下文先讨论理想命中率；明确10k计量、严格边界、样本量和统计范围。“启用”是提示、确认提交还是自动排队仍需讨论，同时考虑去重、预算、取消和历史结果复用。页面访问不触发计算。Token异常分析长期休眠，旧结果可读，不恢复该方向开发。
6. 丰富同事工作台：除了面向业务方的JSON改写建议，还希望给Infra同事推理优化建议。用户会先收集技术材料，再一起讨论。用户的排查设想是：用户理想与MA理想差距→路由；两者接近但真实命中低→L1/L2/L3 KV存储、热点驻留/驱逐，考虑一次问答与深对话差异；三者接近且短低、KV收益有限→讨论缓存使用策略及TP/DP/EP/PP部署优化。希望参考本地kv blog式页面，路径/具体样式待取得。

第6项是产品方向和候选原因，不是已证实归因。比较前要核模型/数据窗/请求集/权重/预热/仿真身份；不能见差距就判定扩容，也不能把热点驻留直接表述为增加物理容量。短低且无复用空间时为何还考虑驻留，需要结合热点证据、一次性请求绕过和资源权衡讨论。用户材料未到时，先整理观察—证据—适用动作的信息结构，不自行铺开技术研究或确定部署参数。

定向参考：docs/tasks/product-v3/promotion/quadrant-detail/dist/index.html；docs/tasks/product-v4/traffic/HANDOFF.md；docs/tasks/product-v4/maas/HANDOFF.md；需要时沿V4_REVIEW_PACKAGE_20261115.md追溯原始证据。旧MaaS试点已收口，不自动恢复。只读源码了解现状可定位apps/viewer/src/features/v2/Ranking.tsx、apps/viewer/src/features/v2/UserMonitor.tsx、apps/viewer/src/components/AppShell.tsx，以及src/tokenscope/user_monitoring/ranking.py、src/tokenscope/user_monitoring/contracts.py、src/tokenscope/monitoring/statistics.py、src/tokenscope/monitoring/rules.py和编码入口，不全量读仓库。

继承已批准“用户监控、搜索与排行、异常分析、MA集群监控”四入口及L4/L5。你可以讨论V5必要变化，但此prompt不等于任何新DEMO已批准；不要擅自重设计或增加入口。先讨论方案，之后如需页面变化，再按用户授权提供DEMO并取得明确“前端展示审批通过”，才交开发实施。公共数据/后端契约先稳定，再前端接入。

首轮请给：简明产品定位和六项需求表，区分用户已明确方向、待决口径、尚未核实的能力/症状；建议最小迭代范围与可验证的验收标准。只提少量真正影响方案的问题，不重复询问已确定事项。JSON、指标、全局排行、阈值可以先讨论；同事技术建议内容等待用户材料，不阻塞前述工作。不要一上来给庞大架构或完整开发排期。

更新docs/tasks/product-v5/下的方案及本人记忆。保留所有原始证据/旧结果/包和其他session未提交修改；不自动创建/唤醒会话、委派子agent、发跨会话消息、启动服务/任务或现场执行。当前新会话只做产品设计，后续实施与交付按用户对应授权。

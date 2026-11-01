# ARTA002 — T3 自动授权提案

2026-10-31，私有实现及目标测试闭环，进入 ARTA003 公共实际消费者联调。

新增 auto_duplicates.py；TokenProposalAdapter 当前声明 T2/T3/T4，generator_identity=token-content-recipes-1，basis_kinds=business_policy/explicit_authorization。

T3 配置版本 token-duplicate-selector-1 / token-duplicate-generator-1。以 appid + 完整载荷 content_sha256 绑定授权范围。引用还须精确工具定义摘要与顶层 argument_pointer；普通重复消息删除须明确 user/assistant 角色。不会修改工具定义。引用值由后台真实映射配置提供，不自行生成；缺 reference_value 返回 REFERENCE_MAPPING_MISSING/advice_only。任何执行须 verified explicit_authorization，scope_selector 完整一致，不接受泛化授权字符串。

采用 exact_payload_repetition Observation，可无 Finding。prepare 从原请求重新分析 T3、重建全部目标/参数，再调用既有 authorize_candidate 和 guarded handler；原文哈希、范围、位置、参数、工具 schema 均受校验。定义变化使旧引用授权不匹配；必需参数/协议字段约束仍由既有 handler 二次校验。

新增 7 项 T3 测试通过；累计 46 项自动适配器单测通过 / 0.18s；17 个私有源码 mypy、ruff 通过。策略及 existing://fixture/1 均明确是构造配置，未声称存在生产对象或实际业务收益。未修改公共源码/前端，未打包部署。

ARTA003 首次真实 GLM-5.2 worker/Tokenizer 联调已通过：同任务 5 个推荐（两份不同依据共享执行、noop、T4、缺依据），M=2，仅 appid=a，noop N=0；完整批次记录待边界补齐。

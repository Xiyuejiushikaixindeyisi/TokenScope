# Token内容分析对公共能力的接口需求

> 当前接入基线为公共draft-2，三项技术选择已被公共维护方接纳。新增原因/方向/阶段字段、完整证据读取、Token无收益门槛及直接全窗口评估语义见[TA-D0.3](DESIGN_ALIGNMENT_DRAFT2.md)。下文draft-1核对表保留为需求来源，原则性接纳不再pending；待固定项限正式Schema、编码样例、注册类型与真实接入。

版本TA-I0.2，2026-10-31，已由本线对照[analysis-common-draft-1](../analysis/BACKEND_COMMON_CONTRACT_DRAFT.md)，三项具体协议已整理为[TA-C0.2](COMMON_INTERFACE_ALIGNMENT.md)，第7节保留公共接纳清单，待双方确认。需求方为Token异常后端01a18fcd-0464-7cf1-b435-4f394bd33e66；公共设计/集成维护方为主会话01a18be2-7112-7aa2-919b-5137d1f1b1ad。本文件没有新增API，不代表对方已签收。

## 1. 责任分界

Token线实现T1–T4纯内容解析、判据、证据和本线变换处理器；公共层提供来源选择、不可变范围、结果归组/存储、显式评估调度、统一编码回放。Token线不直接装配HTTP路由/worker，不直接写源数据库，不维护第二套Tokenizer或缓存账本。

现有`/analysis-runs`是监控任务，user-v2 `/evaluations`是TTFT公式评估，都不能充当已存在的异常分析API。公共外部路由与错误协议由主会话设计。

## 2. 必需能力清单

| 编号 | 能力/逻辑接口 | 最小语义 | 当前源码可复用点 | 缺失时处理 |
| --- | --- | --- | --- | --- |
| I1 | resolve_scope | source/base_run、appid、服务绑定来源、模型/配置、窗口、有效请求集合及摘要；拒绝MA源混入 | UserRunService.receipt、MonitoringService.control/result_db | 来源不确定则阻断，不猜common_name |
| I2 | iterate_snapshots | 原顺序流式提供最终编码成功请求，完整原文/摘要及原计量；严格appid隔离 | requests.sqlite3中request_records JOIN encoded_requests；原顺序time_ns/source_record_index | 某原文不可读/摘要错则记录局部或整体受阻，不能用preview |
| I3 | get_input_evidence | 轻量证据、原IDs摘要、编码/模板身份；可选完整IDs/详细复核引用 | stored_evidence、read_slice、explain_encoding | 保留内容事实，精确Token位置未知 |
| I4 | field_participation | 具体路径在固定模板/选项下included/ignored/unknown、证据依据；可选精确映射 | 当前source_fields仅引用，explain不提供映射 | unknown时不生成模型输入精确占比，源内容事实继续 |
| I5 | publish_fragment | 接收规则状态、content_units、observations、findings、coverage、候选方案，持久化不可变引用 | 公共草案save_observations/报告存储，未实现 | Token线可产生纯结果，不自行建立新结果库 |
| I6 | evaluate_modification | 受保护原结构变换、同appid窗口基线/重放、失败不丢行、负收益保留 | EncodingBatchService、ModelEncoder、make_strategy由公共层封装；不调用写源replay | 只返回未评估及缺口，不调用TTFT公式替代 |
| I7 | cancellation/budget | 固定执行预算、取消信号、按请求边界停止、覆盖及未查原因 | 公共草案含任务/预算，具体取消协议待定 | 不吞预算耗尽、不截断计量后称全量 |

最终接口可采用内部dataclass/Pydantic或其他现有模式；本线不要求上述名称成为公共Python/HTTP名称。

## 3. 请求快照最小字段

RequestView建议含（采用公共草案名称，原本线RequestSnapshot是同一逻辑对象，不再单设公共类型）：

- request_key：base_run_id、source_record_index；hash_id为展示字段，不能替代唯一身份。
- scope_ref：appid、binding_ref/common_name或unbound、model_id、window_ref；源身份不可由请求JSON中model覆盖。
- ordering：time_ns与source_record_index；有真实session信息时另附来源，缺失留空。
- raw_body、raw_body_sha256、raw_body_complete；body_preview不得用于规则计算。
- baseline_metrics：J/P/H/C/O原值及口径，H/C齐全且口径一致时校验P=H+C；修改后O不可预测。
- encoder_identity、asset_identity、profile/effective_options引用、原TokenSlice摘要及证据引用。
- provenance：原记录位置、解析/源质量、采样/截断信息的已知状态；缺失不写false。

不能把已过ingestion但编码失败的行混进成功请求；当前encoded_requests是成功编码集合，存量事实由公共层选择并验证。读取完整源库的能力不代表授权混算其他appid。

## 4. 内容与证据约定

ContentUnit以原JSON Pointer定位；嵌入JSON字符串另有embedded_pointer，不与外层路径混用。字符串字节、结构展示字节、字符、行数、数组项数均有独立unit与representation。

建议公共证据支持：

| 内容 | 本线需要的表示 |
| --- | --- |
| 多位置重复 | 同一request_key下的location列表、内容摘要、比较方法/版本、逐值验证、重叠排除 |
| 工具定义 | tool identity及定义摘要/数量、原位置；同名歧义不合并 |
| 结果归属 | tool_call_id匹配状态resolved/ambiguous/missing；无关联不假定工具名称 |
| 策略判定 | policy_ref、scope、observed_value/unit、expected/operator、met/not_met/unknown |
| 模板参与 | status与evidence_method、模板/选项身份；不要只给“字段存在”布尔值 |
| 精确Token | 可空区间与归属方法；没有精确映射就空，不通过单字段编码或ΔP补值 |

本线返回的重复字节不是节约量；T2/T4同内容用同一evidence key，公共报告去重不能把它们相加。

## 5. 修改协议需求

公共修改对象要能表达“在外层JSON的某个字符串字段内修改已严格解析的内层JSON”，例如arguments字符串中的document字段。仅支持顶层JSON Pointer不足以覆盖T2/T3。

每项方案需要：

1. 固定RequestKey集合、原文/原值摘要、操作版本；应用前验证guards。
2. 原字段与内层路径、原类型、完整参数、保留/截断规则、明确replacement文本或真实引用。
3. 结构性不变量：tool角色/调用ID/定义Schema等不可被本线意外删除；replacement可改变业务信息，须保留action_class。
4. 对未选中或合法不适用记录保持原样；所选目标guard/解析/结构失败则方案受阻，不将其伪装成不适用。
5. 多操作原子方案：T3可能需删除document并加入document_ref；T4可替换多个历史结果。任一步失败不产生部分成功的收益。
6. change_manifest记录前后原文/IDs摘要、具体路径、非目标序列化变化、实际修改/不适用/失败数量。
7. 组合方案检查重复删除/嵌套修改/移动后位置，按显式顺序执行并实际回放。
8. 已批产品的额外普通消息删除仅接受业务指定目标；拒绝删除tool/function消息或携带调用的消息，剩余结构通过原校验。数组索引移位由公共原子计划统一处理，不基于修改后旧索引误删。

本线选择纯函数prepare_mutation处理器，静态注册给公共服务。内嵌JSON先编译为受保护的外层字符串替换，公共层不复制内层解析器；完整顺序、冲突/数组与manifest见TA-C0.2第3节。禁止给本线一个可写源DB连接，避免变换污染封存证据。

## 6. 评估结果与状态

EvaluationResult应提供baseline_origin、replay_context、modification_ref、coverage、before/after N/J/P/H/C/R、差值、manifest/ref和限制。修改子集与整个评估窗口分开。

原运行模式需原IDs/P/H/C校验；子窗口模式保持相同窗口空起点，源H/C只作独立背景。available表示计算完成，不代表优化成功。blocked/failed无after和收益；not_run不能给0。

公共层保存结果，页面只读。字段/数据/接口不支持时报告具体原因，不要求Token线另造缓存模拟器或任务存储。

## 7. 对照analysis-common-draft-1

2026-10-31读取主会话草案，仅在本线记录核对；没有修改公共文件，也不代签其接受以下扩展。

| 范围 | 已覆盖 | 尚需明确的本线需求 |
| --- | --- | --- |
| I1/I2 输入 | SourceSelection/Identity/AnalysisScope、RequestKey/View、iter_requests、完整原文lazy读取与成功集合 | raw_complete及源采集截断未知的表示；不需要第二套快照类型 |
| I3/I4 证据 | read_ids、inspect_input、字段映射可unknown、身份绑定 | 字段参与三态与依据可空字段，单独于精确Token区间；不要求新建映射引擎 |
| I5 结果 | save_observations、覆盖、不可变报告/证据引用 | ContentUnit引用及重叠关系、同请求多位置证据、T2/T4同单元去重键与插件返回Schema |
| I6 计划 | create_plan、guards、结构副本、字段/条目投影、引用替换、组合冲突 | embedded_pointer/解析版本、内层保真序列化与外层guard；消息删除操作和数组移位；本线纯处理器注册方式 |
| I6 评估 | evaluate_plan、完整/子窗口基线、目标失败阻断、零/负结果、原O背景 | 修改子集与全窗口指标单列；具体结果Schema随公共冻结 |
| I7 运行 | 固定预算、partial/失败、显式重试与不可变attempt、共享worker | 取消/停止信号与请求边界退出协议、规则预算覆盖字段；生产默认值待规模校准 |

TA-C0.2第4节已细分location_id/unit_id/observation_id：原位置引用不含rule_id或unit_kind，T2/T4复用单元，策略/规则版本进入观察身份。公共元数据编码需固定，不能靠工具名或显示片段合并事实。公共Plan的JSON Pointer/字符串区间与本线embedded_pointer分别存放；内层改写不是对外层原文进行正则替换。

本线具体选择已经明确：一个token_content插件、describe/validate_selection/analyze_request/prepare_mutation四个逻辑调用面、纯fragment、公共保存、受保护外层替换、三层证据身份；协议状态/取消约定见TA-C0.2第5节。尚待公共维护方将这些选择纳入或明确差异，并给出Schema/注册接入版本。不是再等待本线补充模糊需求。

后续[TA000–TA006计划](BATCH_PLAN.md)区分独立规则与真实公共接入验收；模板参与未知可降级继续，资源默认值经实现校准确定。本轮未发送跨会话消息，未声明对方签收或联调通过。参数错配仅独立研究，不增加公共required capabilities或修改固定effective_options的评估契约。

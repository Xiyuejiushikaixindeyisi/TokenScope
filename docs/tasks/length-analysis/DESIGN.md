# Token异常分析后端详细设计

> 2026-10-31最新批准范围：[TA-S1](SCOPE_REVISION_T234.md)移除Token T1，保留T2–T4编号；工具定义归低命中现有一致性/漂移职责，不增长度精简。当前新设计/计划/推荐/视觉验收仅T2–T4；旧源码及TA000–006历史仍含T1，不冒称已删除。当前实施计划见[BATCH_PLAN_ARTA](BATCH_PLAN_ARTA.md)，三卡样例见[AR-T3](FRONTEND_REWORK_EXAMPLES_ART3.json)。本轮仅文档同步，暂不编码打包部署。

> 当前有效修订为[TA-D0.3：公共draft-2对齐](DESIGN_ALIGNMENT_DRAFT2.md)。用户已确认低命中设计获批；本线已对比并接受draft-2公共语义，流程/展示/评估冲突以修订为准。下文TA-D0.2保留纯内容规则基础；不是重新等待公共方原则性接纳，也不是编码授权。

版本：TA-D0.2，2026-10-31，设计待评审。产品v0.4已批准，本稿落实T1–T4，不重新扩大产品范围。当前会话01a18fcd-0464-7cf1-b435-4f394bd33e66。未编码、未新增API或存储表；公共接口需求见[INTERFACE_REQUIREMENTS](INTERFACE_REQUIREMENTS.md)，三项具体协议见[TA-C0.2](COMMON_INTERFACE_ALIGNMENT.md)，源码核对见[CODEMAP](CODEMAP.md)，分批计划见[BATCH_PLAN](BATCH_PLAN.md)，验证方案见[TESTS](TESTS.md)。参数错配仅为[独立研究](PARAMETER_MISMATCH_RESEARCH.md)，不加入本设计规则。

## 1. 范围与交付边界

当前本线负责工具返回、同请求载荷重复、历史工具结果的内容分析；工具定义仅作身份/协议校验输入，产出可定位事实、条件判定和可机械执行的修改描述。主会话维护公共来源/结果/离线评估封装；监控维护Tokenizer、Chat Template及理想缓存计量。本线不直接维护公共回放、任务存储或HTTP装配。

首期行为为内容事实及规则判断，不推断工具执行次数、Loop、过期性、输出冗长或任务质量。无明确业务预算时输出内容负担和优化机会，绝不补默认异常阈值。示例不是实现或现场验证。

## 2. 已核对的实际能力

2026-10-31读取工作树HEAD ac0699863a4dbe5824862d9d3c1b64a7ecd48d50；关键依赖文件当时无工作树修改，身份与哈希见CODEMAP。

| 能力事实 | 对本线设计的约束 |
| --- | --- |
| validate_request要求messages；工具为tools[].function，参数arguments为JSON字符串；允许旧functions/function_call/function角色 | 第一版解析现有Chat Completions族结构；不自行增加Responses/Anthropic原生协议适配 |
| 内容仅string或text/input_text块；多模态内容当前被拒绝 | 内容分析覆盖现有有效文本请求；不计算图像/音频负担 |
| 原请求完整存入request_records，最终编码成功集合在encoded_requests | 以编码成功集合为分析范围，不能把仅过JSON校验的行算有效模型输入 |
| detail只提供最多64KiB正文预览；body可读取完整原文 | 分析不得使用预览/脱敏片段替代原始内容；展示截断不影响计算 |
| source_fields只有字符串Pointer、字符、字节、摘要 | tools容器大小、子树重复和载荷类型需本线解析；不把字段大小当Token归属 |
| explain复核IDs并给渲染后UTF-8 offsets，但不返回原字段映射，source_attribution_status=unknown | 精确字段Token贡献默认不可用；不能靠全文substring确定归属 |
| ModelEncoder对HF模型传messages/tools，并先解析tool_calls.arguments；DeepSeek使用recipe转换 | legacy字段能通过校验不代表必然进入模型；必须依据具体模板/转换能力说明 |
| user-v2 receipt有base_run_id/common_name；其evaluations是TTFT公式 | 本线可经公共解析器绑定源运行；不能调用TTFT evaluations冒充离线输入回放 |

## 3. 输入边界与模块接口

公共编排器交给本线已固定的AnalysisScope和逐请求RequestView（本线早期名称RequestSnapshot，语义相同，不另建第二套公共类型）；本线不能接受任意文件路径自行打开源库。已对照[analysis-common-draft-1](../analysis/BACKEND_COMMON_CONTRACT_DRAFT.md)，输入/评估边界一致，未决差异见接口需求第7节；公共草案尚非冻结或已实现接口。

AnalysisScope至少含源run/摘要、appid、模型服务绑定及来源、窗口、请求键集合/摘要、顺序、原配置与编码身份、基线模式。RequestKey以base_run_id＋source_record_index为身份；hash_id只作业务显示，不去重身份。不同请求即使hash_id相同仍保留。

RequestView含完整原请求、摘要、源J/P/H/C/O、轻量证据引用和输入IDs摘要；完整原文/IDs按需由公共层提供，本线分析时必须取得原文全文。本线只读。源O只作背景。请求顺序保持原time_ns/source_record_index；本线不按内容排序重放。

拟内部调用形态（逻辑需求，非冻结代码签名）：

- inspect_request(snapshot, policies, capabilities, budget) → content_units、observations、rule_statuses、coverage。
- propose_modification(snapshot_refs, observation_refs, explicit_parameters) → guarded transformation plan或明确不可评估原因。
- 公共层负责存储/归并、实际副本应用与编码回放；本线变换处理器先编译出受保护的公共原子操作，内嵌JSON编译成外层字符串replace_value并保存内层变更清单。token_content作为单个静态插件注册给公共分析服务，不自行注册Dispatcher；逻辑调用与待公共接纳状态见TA-C0.2。

不新增独立监听端口/任务队列。不从页面GET运行解析或模型复核。详细字段需求和待对齐项独立登记，便于公共维护方读取。

## 4. 内容单元与定位

### 4.1 ContentUnit

采用TA-C0.2的位置/单元/观察三层身份：location_id绑定RequestKey、raw_sha256、原/内层位置与解析版本；unit_id补充representation与measurement_version；rule_id仅进入观察身份。unit_kind是tool_definition、tool_description、tool_schema、tool_result、call_argument_payload、message_payload等角色facets，不再作为单元去重键，避免同一tool结果因T2/T4角色不同重复计量。

每个单元保存：

- 原位置：顶层JSON Pointer、message_index/content_part_index、工具身份/调用ID（存在才写）。
- 嵌入内容：若源字段为JSON字符串，例如arguments或tool content，另存embedded_pointer和解析版本；绝不把内部路径伪装成原JSON可直接访问路径。
- 内容：representation、完整值摘要、unicode_codepoint_count/utf8_bytes或display_json_utf8_bytes、条目/行数（适用时），原内容只在现场证据仓保存。
- 来源关系：parent_unit_id、container_unit_id、是否与父载荷重叠，用于禁止加总父子重复。
- 模板参与：included/ignored/unknown及证据方法；精确prompt_token_spans默认空。
- 工具身份解析：resolved/ambiguous/missing。名称相同不自动合并不同定义，call_id重复或无前序匹配不猜测关联。

### 4.2 支持的解析

首期解析现有已验证结构：

1. tools[].function（兼容functions[]），枚举完整定义、description与parameters。两套字段同时出现分别保留原位置；模板实际消费哪一套由公共能力证明。
2. role=tool的content；role=function为legacy观察，能力不明时保留原文字段事实。文本块数组按原序保存各块，不人为插换行导致伪重复。
3. assistant.tool_calls[].function.arguments及legacy function_call.arguments；arguments严格解析JSON，重复key/非有限数值/错误格式返回局部解析不足。
4. user/assistant消息正文仅作为T3可比较目标，不单设通用长prompt探测器；system/developer不扩入新的Token异常方向。
5. tool content为JSON字符串时只解析一层，内部字符串不递归尝试“可能又是JSON”；不通过多层解码改变业务语义。

JSON对象key顺序只在结构比较表示中规范化，字符串值和数组顺序不变。结构相等需逐值比较，类型敏感（true不等于1），数字不经有损float转换；TA-C0.2建议json-exact-1保留数字词法，1与1.0保守不等，方法写入结果。无法保持数值身份时只做字符串完全一致比较；修改无法保持非目标数值则受阻。原请求和原字段从不先规范化再当作源证据。

### 4.3 度量与不重复统计

解码字符串的utf8_bytes是其UTF-8表示长度，characters是Unicode码点数。行数采用原字符串splitlines语义，空字符串0行，末尾换行不额外增加空行；算法版本写入度量。数组条目数仅数组直接元素数量，不把嵌套元素累加。

结构对象采用固定展示序列化（UTF-8、无额外空格、对象key确定序、保留字符串/数组/数值语义），字段名明确为display_json_utf8_bytes，不叫原始字节或Token。原字符串和结构表示字节不得混算一个总量。

T1完整定义与其子description/schema分别列明，但汇总只用不重叠完整定义。T2/T4同一个tool结果引用同一单元；跨探测器不加总。T3只有完全相同字节载荷时才可计算(k−1)×bytes；结构相等而表示不同仅列各位置/各自大小，不给伪精确重复字节。

## 5. 模板参与及精确Token归属

本线需要区分源内容存在、内容是否进入模型、具体Token位置三种证据。

- 公共层提供与模型/模板/选项身份绑定的字段消费能力或已有精确映射时引用它。
- 当前source_fields/explain不提供精确映射，默认unknown；若公共层只确认字段被消费，则included，但Token贡献仍为空。
- 全文里找到相同字符串不证明来自该字段；多处相同、转义/格式转换尤其不可用简单包含匹配强行归属。
- 若公共层支持限定字段的对照渲染，输入变化导致渲染/IDs变化可证明该变换影响模型输入；不能把未变化直接当作“字段永远被忽略”，也不能从ΔP推导原Token贡献。
- 不额外创建一套sentinel编码或模型适配器。该能力不足时内容报告继续，模型输入预算超限结论降级为源内容事实；离线P/C由具体修改评估提供。

## 6. 执行规则（当前T2–T4；T1段仅保留历史）

### 历史T1 工具定义负担（已退出当前范围，不再实施或展示）

输入工具清单，按位置和完整定义保存唯一单元；可选名称用于展示。无tools/functions为not_applicable；空列表为completed且无定义，不伪造失败。

输出每请求工具数量、定义展示大小、description/schema大小、明确完全相同说明的多位置证据。按同单位大小降序排列，同值按位置稳定排序，不以Top-K作为异常判定。

有业务预算时精确匹配适用工具/版本和度量单位。actual > limit才判超限，等于不算；若契约指定其他比较符则必须显式保存。不兼容单位/未知模板参与（且预算针对模型输入）为unknown，不自动折算Token。

修改只允许准确description替换或明确冗余说明删除；保留name/parameters/required及其他定义。未经确认不删工具、不删Schema。没有替换文本则候选待参数；按需发现/延迟加载只作为advice_only。

### T2 大工具返回直接注入

枚举tool_result单元。文本、JSON数组/对象、文本块分别计算适用度量。body是完整快照，但内容本身是否采集前被截断未知，source_truncation=unknown，不能报告原始工具返回总量。

没有业务策略：产生负担事实和可选优化机会，不自动异常。存在精确策略：校验工具匹配、结果路径、单位、限额/列白名单及作用层级；不匹配为not_applicable，结构无法解析为unknown，确定违反才policy_exceeded。

规则示例：每行字段白名单必须明确是array_items，而非顶层对象；逐行保留顺序，异构行/无法验证目标阻断方案，不静默跳过。max_items给出严格非负整数；保留索引范围为左闭右开，不能隐含默认100行。

可评估操作为投影指定字段、指定条目/行范围或明确replacement。保留消息role、tool_call_id及容器；truncation_note只能放契约允许位置，不能为加标记破坏JSON格式。若协议没有允许标记字段，外部变更清单记录截断，不擅自添加业务字段。

### T3 同请求载荷重复搬运

只在一条RequestView内部检查。候选至少涉及一个tool_result，另一位置为另一个tool结果、调用arguments内部完整载荷、user/assistant正文的完整载荷。调用ID、工具名、协议key及JSON结构标点不是载荷。

候选边界按协议和结构确定：tool结果/正文以整个字符串、原文本块或已解析的完整JSON对象/数组为单位；arguments以整个内层对象/数组及其完整字段值为单位，嵌套对象/数组可继续枚举，受深度/单元预算限制；仅非空字符串、非空对象/数组参与，数字/布尔/null不作为文档载荷。字段名不用于猜测业务冗余，重复关系必须保留实际位置供解释。协议层call_id/name等不进入候选，用户载荷内部恰好名为id的字段也不能凭名字擅自删除。

首期确定规则采用完整非空字符串字节相等；结构化载荷可用类型敏感结构相等。按representation+长度+摘要建候选桶，再逐值核实，摘要不单独作相等证据。短的“ok”等相同内容可以保留低量内容事实，但不自动生成异常/可删结论；没有业务长度门槛就不伪设门槛。

对每组选择不重叠的完整载荷位置，父子嵌套的同一范围只计一次；相同大小按稳定位置选择。首期不实现近似文本、语义重复或任意substring搜索；局部片段可由证据显示，但不升级精确重复判定。这是对已批规则中“优先完整载荷”的实现收敛，不新增探测方向。

重复字节反映出现事实，不是可节约Token/C。没有下游引用协议或明确允许删除的额外普通消息，不创建修改方案；“同一请求两个位置”不能表述为重复执行或Loop。

引用替换要求显式的工具协议版本、真实引用值、替换的正确参数形状及可解析性的业务依据；不访问外部工具验证或生成不存在的文件引用。若需删除document并增加document_ref，两操作为同一事务方案，保留其他参数，验证Schema约定；缺任何前提为advice_only。已批产品还允许业务明确指定删除额外复制的普通消息：仅在该消息不承载tool_calls/function_call、不为tool/function角色，且剩余请求通过原协议校验时产生候选；不凭重复事实默认删消息。

### T4 历史工具结果负担

复用T2单元，按原message_index/content_part_index排序，展示结果块数量、每块负担及后续消息数。不会把消息数当turn、工具执行次数或时长；不依赖跨请求关联即可给清单。

保留策略必须明确“结果块”定义：默认本设计的unit是一个tool消息的整个结果容器；多文本块内部不自动当多个工具结果。若策略选择content part则需显式指定单位，不能混用K。按相同工具/策略作用域在快照内选最后K个单元，其余为候选；K必须由业务给定，K=0需要明确提供。

无策略只给清单。策略给出合法replacement/ref时才能生成修改；不能仅凭“旧”清空消息，不能删除调用配对。被保留的单元字节不改，目标替换按原值摘要保护。

离线评估依旧是逐快照确定变换，不模拟未来历史演化、不重新运行Agent。前缀变化可能使P减少而C增加，保持完整前后指标及负收益。

## 7. 策略与修改描述

策略以PolicySpec引用进入分析：policy_id/revision、来源、适用工具/定义版本、source_pointer或单元选择器、measurement_representation、unit、operator/limit或保留规则。没有策略为正常状态，不作为任务失败。模糊工具身份不套用按工具规则。

任何修改均保存RequestKey集合、原文摘要、定位、原值摘要、参数、变换版本和限制。内嵌JSON由本线严格解析并校验内层目标，编译为带整个外层字符串guard的replace_value；公共层在评估时重新验证guards、应用副本、校验和编码。相同外层字符串的多个内层修改一次编译；不同旧值替换不能串行覆盖。记录非目标格式变化并核对结构不变，源JSON不可变。

本线操作候选：replace_tool_description、project_result_fields、select_result_items、select_result_lines、replace_payload_with_reference、remove_authorized_duplicate_message、apply_retention_replacements。名称是需求标识，公共层可映射统一操作模型，不要求增加对应数量的独立外部API。数组删除以源位置和原值定位，在原子计划中统一解析偏移；不会按已移动后的旧索引继续误删。

同一方案目标有任一失败，向公共层返回plan_failed，不发布收益；不能把失败记录留原样而称方案全成功。不适用目标必须在执行前声明并计数，不能用它隐藏guard失败。跨请求匹配相同历史载荷时按明确请求集合逐个应用，不推断session。

## 8. 运行与结果设计

读取公共固定范围 → 逐请求解析一次 → T1–T4共享ContentUnits → 输出Observation与RuleResult → 公共层去重归组/保存 → 显式选择Modification → 公共层评估 → 已存报告读取。

本线不规定T1→T4的业务优先级。T2/T4共享枚举、T3依赖单元解析是数据依赖，不是原因优先级。

拟输出TokenAnalysisFragment：
- rule_results：每规则适用/检查/不完整状态及原因。
- content_units_ref、observations：结构事实、来源、判据及condition_status。
- findings：optimization_opportunity/policy_exceeded/needs_evidence；T1–T4没有仅因内容大而construction_issue的默认分支。
- modification_candidates：明确参数/guards或缺口。
- coverage：请求数、单元数、实际比较数、预算停止位置；来源/预算/显示折叠独立。
- shared_evidence_keys：支持与低命中同字段关联，T2/T4不重复量化。

错误为本线内部原因枚举，外部错误码由公共契约统一映射：SOURCE_BODY_UNAVAILABLE、SOURCE_DIGEST_MISMATCH、UNSUPPORTED_REQUEST_SHAPE、EMBEDDED_JSON_INVALID、TOOL_IDENTITY_AMBIGUOUS、POLICY_NOT_APPLICABLE、POLICY_UNIT_UNSUPPORTED、VISIBILITY_UNKNOWN、ANALYSIS_BUDGET_EXHAUSTED、MODIFICATION_GUARD_FAILED、REFERENCE_CONTRACT_MISSING。错误内容不回显正文。

单元解析失败只影响对应规则；源身份/摘要失配交公共层阻断。预期的局部数据不足不删除其他合法观察，报告partial；意外插件异常为方向failed，不能吞成无发现。没有数据、不适用、没有匹配、未检查、失败分别保存。规则执行状态与判据的met/not_met/unknown独立，见TA-C0.2。

## 9. 性能、内存与确定性

请求顺序流式迭代，一次只解析一条完整请求及其单元；不把整个appid原文同时载入内存。结构遍历一次，T3采用哈希分桶和精确比较，避免全字段两两比较；保留冲突校验与实际比较预算。大单请求仍可能超过预算，显式停止该请求/规则并标partial，不截断后假装完整扫描。

max_request_bytes、max_units、max_comparison_bytes、解析深度等为执行预算，由公共运行配置固定并在报告记录；当前不猜生产默认值，开发校准时用合成边界确定。预算不是异常阈值，不被用来定义“大内容”。输出证据片段单独限长，完整计算不依赖预览。

同一源摘要、规则/解析器/策略版本、参数和预算应产生稳定单位身份、观察顺序及修改清单。重跑不覆盖原报告；存储幂等/取消/恢复由公共编排器负责，本线支持按请求边界检查取消并关闭迭代资源。

## 10. 公共评估接入与完成条件

本线仅提交有guards的原结构变换，不直接写源requests.sqlite3、不调用监控replay改写封存数据。公共评估封装必须：
- 固定appid/服务/窗口与基线来源，原运行模式校验原IDs/P/H/C，子窗口重算前后同空起点。
- 用同一资产/Template/选项编码，将目标失败作为整个方案受阻。
- 统计全评估范围及修改子集，保留N/J/P/H/C/R、零/负结果；不生成修改后O、费用或质量承诺。
- 返回变更manifest和不可变评估引用；组合做冲突检查并实际评估。
- 页面只读已保存结果。

当前公共草案analysis-common-draft-1已覆盖本线主要流程；TA-C0.2进一步明确内嵌JSON编译、证据身份和插件调用面，待公共方接纳为具体Schema/注册版本。逐项对照在INTERFACE_REQUIREMENTS中。本线不改公共草案、不宣称双方已签收；不得声明接入已完成，也不另造公共层绕过等待。

## 11. 设计交付与待决

本轮更新DESIGN、CODEMAP、INTERFACE_REQUIREMENTS及TESTS，新增TA-C0.2、TA000–TA006分批计划和独立参数错配研究；没有运行实现或业务测试。

以下为依赖概览，批次划分与退出标准以[BATCH_PLAN](BATCH_PLAN.md)为当前权威；均为planned，本轮未启动：

1. 固定公共RequestView/Observation/Plan接入版本及本线类型，落实单层内嵌JSON定位与确定性度量；验证P01–P06。
2. 实现T1–T4纯规则、业务策略和来源/参与状态降级；验证T101–T403、V01–V02，使用同请求的明确预期防止扩大到过程判断。
3. 实现本线纯变换处理器，接入公共原值保护/原子应用；验证M01–M08及真实统一编码，不绕过现有校验。
4. 接入公共任务/保存/评估并做E01–E08及只读/取消验证；按合成规模测量确定执行预算默认值，记录实际资源和覆盖。

本线协议选择已具体化，下一步需要公共方确认接纳版本，不再从零讨论三项行为。模板参与可先按unknown降级，不把精确字段映射作为内容事实的启动门槛；资源默认值在实现校准后固定，不能要求纯设计阶段凭空选值。以上不改变已批T1–T4产品范围；不在本轮自动编码或冻结对外接口。

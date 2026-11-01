# AR-C1 公共推荐契约对齐

2026-10-31最终实施入口：docs/tasks/prefix-analysis/FRONTEND_REWORK_IMPLEMENTATION_HANDOFF_ARL3.md；验收：docs/tasks/analysis/batches/ARPC006/RESULT.md。下文为设计/阶段保存记录，旧暂停、未实施或待项不覆盖最新实际交付。

2026-10-31 TA-S1/AR-03范围覆盖：Token新自动方案仅T2–T4，不重编号，不再要求T1精简模板；工具定义仅由低命中现有顺序/一致性/漂移职责负责，不新增长度精简。工具定义仍可作为T2–T4身份/协议校验输入。旧T1报告及冻结契约保留。公共最新直接授权已恢复实施；当前状态以ARPC批次记录为准。详见[范围回执](../prefix-analysis/SCOPE_T234_ACK.md)。

2026-10-31。公共维护方01a18be2-7112-7aa2-919b-5137d1f1b1ad依据用户本轮要求，对齐[AR-L2](../prefix-analysis/FRONTEND_REWORK_RECEIPT_ARL2.md)与[AR-T2](../length-analysis/FRONTEND_REWORK_RECEIPT_ART2.md)。本文为**已确定的工程设计基线**，供实现和消费者签收；不是运行时Schema冻结或新API已上线证明。新源码/Schema在实施批次生成后记录摘要。未改正式前端、旧契约、Token私有文件或部署打包。

## 1. 对齐决定与责任

| 分歧/未定项 | 本轮确定 |
| --- | --- |
| 两套推荐草案 | 对外统一analysis-recommendations-1；token-recommendation-draft-1仅为上游设计输入，不形成第二套前端协议 |
| ID是否含task | recipe_key不含请求序号/原文摘要；recommendation_id含scope/方向/方案生成版本/recipe_key/支持集合摘要/策略快照摘要，**不含task_id**；按ART2实现确定性。读取与缓存必须同时绑定实例+task+scope+推荐版本，不能凭同ID跨任务拼接 |
| 方案与执行去重 | 不同依据的方案不合并为一个推荐；所有方案独立验证依据和guard后，相同执行内容可引用一个canonical Plan/Evaluation；不得把任一未获准方案借别人的评估变成可执行 |
| T3无Finding | support_refs允许token_observation且finding_ids为空；不伪造Finding，不把推荐ID填进Plan.finding_refs |
| 无依据与失败 | 已完成资格判定但缺业务依据为advice_only；适配器缺失/配置错误/预算停止/准备或回放失败为partial或失败终态，不伪ready |
| 新字段放旧items？ | 新独立只读router读取新私有存储kind；不改旧ItemKind枚举或静默刷新diagnostics-http-1 manifest |
| 假设默认 | 保留已批准L1/L3离线删除假设；Token首批仅完整依据驱动。无依据T2/T4裁剪/保留假设默认关闭，T3绝不以通用假设绕过协议/授权 |

公共方唯一维护契约/ID/归组/计数/Plan/回放/资源/封存/通知/局部定位公共设施。Token方维护recipe匹配、每目标完整参数、T2–T4业务文案模板、依据专属有效性验证与handler适配；公共方不改其私有算法或假造策略。前端只消费封存成果，不POST、不现场hash/聚合诊断、不展示Plan或完整原文JSON。

## 2. 版本与只读接口

已实现版本保持analysis-common-1.0、diagnostics-http-1、diagnostics-runtime-1、diagnostics-discovery-1、token-content-1。新报告扩展声明`analysis-recommendations-1`，内部适配器`token-auto-proposals-1`、分组`recommendation-group-1`、局部定位`evidence-locator-1`。这些版本名已确定；**实际Schema、端点尚未实现**。

| 拟实施GET | 语义 |
| --- | --- |
| /diagnostics/recommendations/capabilities | 扩展版本、模型Schema、只读路由、可用适配器及预算profile版本；不返回私密策略正文 |
| /diagnostics/tasks/{task_id}/recommendation-summary | scope、扩展身份、生成/扫描/评估覆盖、预算快照摘要与消耗、group/方案状态计数；旧报告返回availability=not_computed，不自动补算 |
| /diagnostics/tasks/{task_id}/recommendations | 方案摘要列表；query direction=low_hit或token_content可选，offset十进制文本>=0，limit 1–100默认50 |
| /diagnostics/tasks/{task_id}/recommendations/{recommendation_id} | 单项完整推荐元数据及例子引用，技术目标清单不直接内联到业务卡片 |
| /diagnostics/tasks/{task_id}/recommendations/{recommendation_id}/examples | 封存局部证据和建议修改前后，每方案最多3例；无前端参数 |
| /diagnostics/tasks/{task_id}/difference-groups | L4/L5摘要列表，同分页约束，无收益过滤 |
| /diagnostics/tasks/{task_id}/difference-groups/{group_id}/examples | 单项1–3例或明确定位失败原因；没有有效片段时返回空例子及原因，发现组本身仍存在 |

除capabilities外使用既有x-tokenscope-service-instance；列表返回version/task_id/scope_id/availability/items[{id,data}]/offset/next_offset，末页next_offset=null；排序按`display_order`稳定升序再ID，不依赖当下收益排名。不可变task报告不需新增snapshot；目录仍用discovery快照。摘要/列表对旧报告availability=not_computed、items=[]，不能据此写“无问题”；旧报告具体新对象请求404 RECOMMENDATION_NOT_FOUND。未发布409 REPORT_NOT_READY、错误实例409、非法参数422、存储503沿旧语义。未知扩展版本明确不兼容，不从旧fragment猜新对象。

扩展对象存在独立私有kind（recommendation、difference_group、recommendation_example、recommendation_summary），只有新router对外提供。Plan/Evaluation仍用原公共对象和旧GET读取，并纳入同任务封存manifest。discovery只在最终报告和扩展全部提交后通知，保持partial不替换、empty不替换、两方向整体ready的默认选择。

## 3. 推荐对象（字段级实现基线）

元数据整数沿wire十进制字符串；精确有理数为`{numerator,denominator}`，分母>0，缺值null。业务JSON文本不转换。ID/摘要由公共层生成并保存；不得将业务文本JSON重新排序当作语义等价判断。

| 字段 | 类型/不变量 |
| --- | --- |
| version / recommendation_id / task_id / scope_id / direction | direction仅low_hit或token_content；初始自动链不生成combined。已有组合只按原历史接口读取 |
| generator_identity / recipe_key / group_basis_digest | 生成器/文案/handler版本和规范化recipe身份；配置变化不复用旧身份 |
| primary_rule / category_rules | primary_rule由recipe声明且属于category_rules；多标签不是因果排序，T2/T4同操作可有多来源 |
| title / change_summary / conditions / limitations | Token提供受版本控制业务模板+真实工具显示名，公共校验字符串；低命中公共模板生成。不用通用“待确认修改”替代具体问题 |
| basis | 第4节结构；业务依据与“无损”声明分开，不把有政策等同语义无损 |
| support_refs | 非空类型化列表：prefix_finding(task_id,finding_id,rule_id)；token_observation(task_id,fragment_id,observation_ids非空,unit_ids,location_ids,finding_ids可空,request_key,raw_sha256)。引用必须属于当前task/scope且关系有效 |
| matched_set_digest / support_set_digest / members_complete | 有序RequestKey/支持身份摘要；完整成员保存在报告，不要求业务页面加载全量以统计 |
| impact | total_requests=scope.request_count；matched_requests可空，matched_checked_requests、match_complete；modified_requests可空，evaluation_complete；count_basis=raw_body_changed。available时modified_before.n=modified_after.n=modified_requests且<=total_requests；匹配/观察/操作数不冒充修改数 |
| proposal_status / preparation_status / evaluation_status | 见第6节；分层状态保留，不只存一个“成功”布尔值 |
| status / reason_codes / reason_details | 推荐汇总状态，非TaskReceipt枚举；reason_details只保存安全业务解释，不回传异常堆栈/原文 |
| prepared_plan_ref / execution_plan_ref / evaluation_ref | 可空`{task_id,id}`；自己的准备Plan与实际执行的canonical Plan区分。evaluation.plan_id必须等于execution_plan_ref.id，不伪称它执行过prepared_plan_ref；未准备无Plan，未回放无Evaluation |
| evaluation_reused / execution_fingerprint | 复用标志及完整比较指纹；仅在第5节条件满足时为true |
| metrics | 全scope before/after `{n,j,p,h,c}`及modified子集，来源原Evaluation；gain_percentage_points、input_tokens_delta/ratio、compute_tokens_delta/ratio严格派生。delta=after-before，ratio=delta/before，before=0时ratio=null |
| display_qualification | low_hit_optimization、token_evaluated、token_advice、not_eligible；不是Task状态。前端低命中主卡只显示修改数/比例和命中率/百分点；Token主卡显示P/C与变化，不套>1pp |
| example_refs / display_order | <=3例；封存稳定顺序，引用的完整路径/片段只在详情按需读 |

具体身份计算：recipe_key=canonical_metadata版本化recipe内容的SHA256，含handler/version、typed basis身份、精确工具定义/选择器、参数生成规则及适用条件，排除本请求下标/raw值。支持集合规范化排序去重后计算摘要（保留RequestKey及raw_sha）；recommendation_id=scope_id+direction+generator身份+recipe_key+support_set_digest+policy_bundle_digest的稳定摘要。扫描不完整时members_complete=false，支持集合仍如实限定；不与完整报告身份混同。同实例/相同输入和快照重建ID稳定，但不同task的读取/缓存隔离不变。

## 4. Basis、配置与适配器

`Basis={kind,ref,revision,digest,scope_selector,authority,assumptions,limitations}`：kind为business_policy/offline_hypothesis/explicit_authorization；authority记录可验证来源类别、引用及验证状态（verified/missing/invalid），不由字符串自称“已批准”。没有依据时推荐basis=null且reason=RECIPE_BASIS_MISSING，不伪造ref/revision/digest。

- business_policy：明确本场景允许的修改规则。旧PolicySpec limit只表达异常判据，field_allowlist也不能自动推成允许省略的修改授权；必须在独立recipe配置显式`allow_omission`及字段层级/目标工具定义等。
- offline_hypothesis：精确假设方式、值、替代文本、已批准假设profile来源与限制。它不是授权。保留当前L1/L3允许评估的删除假设；Token T2/T4无依据模式默认禁用，未有明确策略不能随意补K、head/tail档位、摘要或占位词。
- explicit_authorization：T3引用协议/真实映射或普通副本删除约定，须校验工具定义、目标/保留角色、完整重复证据及真实引用对应关系；没有Finding不影响校验，但没有授权不能执行。引用值来自注册配置，不生成假地址，不访问工具验证未来效果。

后台配置入口确定为项目内JSON bundle（实施时`configs/analysis/recommendations/*.json`，不新增UI/远程配置平台/依赖）；包含bundle_id/revision、recipes、适用appid/model_id/common_name/source_kind、工具定义摘要、依据ref/revision及精确参数生成规则。秘密/真实引用数据不进入Git；生成报告保存已使用快照和digest，业务接口仅公开必要摘要。配置启用从现有服务配置入口装配，提交时冻结；同submission_key不能因随后文件变化绑定不同快照：先按既有请求意图查已受理任务，返回原快照；新key采新快照。retry必须复用原快照，不偷偷应用新规则。

确定性适配器`token-auto-proposals-1`与原H0插件并存，静态注册，禁止动态模块加载。接口：describe（版本/支持recipe/basis）、validate_bundle（启动/提交校验）、propose(scope_id,request,fragment_id,fragment,bundle_snapshot,capabilities,control)（纯返回完整目标提案或已判定不可行原因）、prepare_proposal(request,proposal,basis_snapshot)（依据复核后复用私有handler，返回受保护MutationPreparation）。明确保留后一个方法：当前H0 prepare只理解business_basis_ref字符串，不能靠把hypothesis字符串伪装成授权兼容。旧显式prepare行为不改。

Token侧输出包含recipe_spec、primary/category_rules、source_refs、request_key/raw_sha、目标Location/匹配条件、该目标完整parameters_json、basis验证结果和可读文案。公共层唯一生成全scope归组ID/计数及报告映射。各目标参数允许不同，但生成规则/映射来源相同才可同recipe。冲突配置（同ID/revision异内容、重叠互斥策略）在校验阶段拒绝，不按文件加载顺序选赢家。

## 5. 编排、等价执行与局部证据

执行顺序：原scope固定→低命中探测/单项pilot/full→Token原文扫描与fragment/index→自动proposal匹配→跨请求归组→逐目标依据/guard准备→完整Plan→原scope同序列direct_full回放→推荐/局部证据/原Plan/Evaluation同任务封存→原终态事务和discovery通知。Token不创建HTTP子任务，不在低命中修改副本上工作，不穷举组合。

去重规则：先分别完成每条方案的basis和prepare验证，再比较同scope、同方向、同编码/profile/settings/算法身份、相同账本初始条件、完整操作集。执行指纹排除operation_id和仅记录来源的business_basis_ref，**保留**handler/version、RequestKey/raw_sha、全部guard、primitive、replacement_json原词法、内嵌处理/invariant/source_operation等其它字段；按规范的目标/操作序稳定排序，重复操作去重需完全同值，重叠不同操作阻断。哈希相同后仍比较规范化字节，不只依赖摘要。不同basis推荐各自保留prepared Plan和依据，引用同一个canonical execution Plan/Evaluation；invalid/missing basis永远不能借有效方案“共享成功”。首个canonical执行失败时其它等价方案同样引用失败结果，不重复尝试直到成功；失败不算available。

扫描和适用集合必须完整才准备全scope可行方案；匹配扫描预算停止时不把已发现子集伪装为全scope计划。单个目标prepare失败整方案blocked，不丢目标；其它独立方案可继续但整体partial。无匹配目标或全目标noop是已完成判定：前者advice_only/NO_MATCHED_TARGETS，无评估；后者可使用已有完整回放得到N=0/零收益，不能仅凭Plan无语义变化伪造结果。

低命中聚合/差异分组、RequestKey去重、L4/L5每组≤3例及不套收益门槛按AR-L2 A–C实施。局部设施统一：source_ref+pointer/embedded+raw_span/decoded_span+offset_unit+locator_version+原文摘要+上下文+omitted标志；单位为Unicode code point半开区间，明确不是UTF-8 byte或JS UTF-16。词法定位器保留数字词法/重复key歧义/转义映射，不substring首命中。解析预算内仍不可定位时保留该发现，examples空并给原因；若必需例子生成因预算/系统错误未完成则报告partial，而非“没有发现”。所有完整原文仍后台保存，不在业务详情铺开。

## 6. 状态、展示与ready/partial

状态层分开：proposal_status=`matched|advice_only|not_applicable|partial|failed`；preparation_status=`not_required|not_run|prepared|blocked|failed`；evaluation_status=`not_required|not_run|available|blocked|failed|interrupted`。available必须对应完整Evaluation，after不完整为null。汇总推荐status沿Token建议统一为available/advice_only/blocked/not_run/failed/interrupted；具体阶段信息不丢。

| 判定 | 方案状态及示例原因 | 任务处理 |
| --- | --- | --- |
| 范围/资格已查完，场景缺完整业务依据或不适用 | advice_only；RECIPE_BASIS_MISSING、REFERENCE_MAPPING_MISSING、NO_MATCHED_TARGETS、HYPOTHESIS_DISABLED | 可ready，明确“未形成可评估方案”而非无异常；不替前端补参数，不编造收益 |
| 明确拒绝非法/不匹配授权 | blocked；BASIS_INVALID / AUTHORIZATION_SCOPE_MISMATCH | partial；无after，无自动放行 |
| 声明启用的自动适配器缺失/版本不支持、bundle缺失或非法 | 阶段failed；AUTO_ADAPTER_UNAVAILABLE / RECIPE_BUNDLE_INVALID | 不能解释为逐场景advice_only；任务partial；提交前可识别的无效配置直接拒绝，不排队 |
| 正常可评估方案完整回放 | available，可能N=0/P不变/C增加 | 可ready；Token不套>1pp，真实零负值完整保留；低命中严格全scope>1pp才优化卡 |
| 匹配/归组/准备/评估/局部证据生成预算或技术失败 | not_run/blocked/failed及具体阶段原因；原结果保留 | partial，不更新旧默认；未完成匹配的matched_requests=null，可保留matched_checked_requests |
| 公共源/封存完整性失败、取消、worker异常重启 | 原failed/interrupted规则 | 不生成假after，不发布半成品；显式retry保存新task与原快照 |
| 源无请求 | empty | 不替换旧默认；有历史报告仍可显式查看 |

全局ready iff全部已启用必需阶段完成资格判定，且所有要求执行的prepare/evaluate完成，无预算/技术/依据invalid阻断。**没有可行方案**可以是完整结果；**缺模块/配置或没有检查完**不能是完整结果。显式有效空bundle可得到“没有已登记方案”及advice_only，但能力声明必须报告configured_recipe_count=0，不称已覆盖业务优化。默认profile启用自动阶段时，bundle路径不存在与合法空bundle不同。

阶段计数固定提供eligible、checked、completed、advice_only、blocked、not_run、failed、complete、reason_codes；unknown eligible为null，不随失败缩分母。error分类由适配器reason code和公共状态映射表驱动，禁止按错误文本猜分类。

具体依据缺项统一`RECIPE_BASIS_MISSING`（真实引用缺失用`REFERENCE_MAPPING_MISSING`），结构化reason_details包含rule_id及missing_requirement枚举：template、retention_rule、reference_or_delete_agreement、replacement_rule。它们是资格检查完成后的业务结果；不另冻结BASIS_T*别名。authority记录source_kind/source_ref/source_digest及验证状态，完整来源快照后台保存。有效依据已校验、内容不在适用场景时proposal_status=not_applicable、汇总status=advice_only；配置非法/越权不得归为not_applicable。此口径与Token [ARTA000第8节](../length-analysis/ARTA000_ALIGNMENT.md)一致。

## 7. 预算与顺序（工程默认已确定，非生产SLA）

冻结服务端`recommendation-budget-1`快照，新增预算独立于旧RuntimeOptions模型。以下为首期保守默认，允许运维在新任务前显式配置；不是业务阈值，不允许任务中自动提额。既有source/request/depth/findings/encoding/Plan限制继续生效，取更严格者；模型API未引入新前端参数。

| 新限制 | 默认 | 计量/停止语义 |
| --- | --- | --- |
| max_proposals | 256 | 全task累计请求级提案；超过前停止，标扫描partial，不评估被截断组 |
| max_recommendations | 32 | 精确归组后方案数；超限保留已登记状态和overflow计数，不挑事后收益好的方案 |
| max_prepared_operations | 10000 | 全task累计已准备操作数，独立于RequestKey数 |
| max_proposal_bytes | 1 MiB | 单proposal完整序列化UTF-8；不截断JSON参数 |
| max_plan_bytes | min(旧RuntimeOptions.max_plan_bytes,16 MiB) | 每个完整Plan，与既有口径一致；等于允许、超过阻断 |
| max_total_plan_bytes | 64 MiB | 全task所有已保存prepared/execution Plan实际序列化总字节；共享同一个Plan只计一次 |
| max_token_evaluations | 8 | 新启动独立Token回放次数，失败启动也计，成功复用不计新一次 |
| max_examples_per_group | 3 | 展示采样上限，不限制扫描/观察数或问题组数 |
| max_excerpt_codepoints / max_context_codepoints | 1024 / 每侧128 | 超长片段显式omitted，不重新摘要；原文不截断 |
| max_example_bytes_per_group | 24 KiB | 局部展示对象；按词法边界有标记裁切，无法安全定位返回原因 |

全任务encoding_calls继续用现有一个计数器，低命中和Token准备/评估不重置；Token实际调用前检查剩余额度。max_experiments沿现有低命中语义，新max_token_evaluations不冒充全局额外编码许可。原Plan编译及Token handler的既有8MiB等硬限制仍保留，新增预算不能放宽它们。资源默认值不保证大appid完成，生产按源规模配置；全scope超预算不缩scope求“合格”。

处理顺序：源按(time_ns,source_record_index)；recipe按primary_rule(T2→T4)、recipe_key、目标RequestKey排序，低命中沿确定规则/recipe顺序；不按预计收益动态挑选。max_proposals先限制扫描产生的提案，全scope匹配完成后才进入准备。所有预算消耗、有效上限和停止位置封存；重试可复现，调整预算需新意图key而非改变原attempt快照。64MiB内存与磁盘不是SLA，Plan总字节只是保存内容预算，不声称限制进程RSS。

## 8. 业务输入与后续验收边界

工程版本、字段、身份、接口、默认预算、顺序、状态和维护职责已落定，不需业务再选择。首批范围定为完整后台配置驱动，Token无依据假设不自动启用；避免以未批准的裁剪策略补齐“人人都有收益”。

真实业务验收仍需提供/指向实际策略资料：T2允许省略字段/层级或明确选择区间；T3真实引用协议/映射或副本删除约定；T4 K/单位/范围及合法replacement规则。不是每条报告用户填表，也不要求一次收齐四类才能开发；构造策略仅用于工程验证。现库未核实这些生产bundle，不能称“业务收益已可用”。

本轮无需重复问L4/L5门槛、Token前移或前端POST。若用户希望**没有上述业务配置仍自动给T2/T4数值收益**，才需额外确定假设档位/保留方向/替代文本；该选择不阻塞目前已确定的配置驱动实施计划。实施与验收见[批次计划](RECOMMENDATION_IMPLEMENTATION_PLAN_AR1.md)。

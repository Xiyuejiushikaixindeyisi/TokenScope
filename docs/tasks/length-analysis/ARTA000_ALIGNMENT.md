# ARTA000 推荐协议、计数与发布状态对齐

> 2026-10-31最新批准范围：[TA-S1](SCOPE_REVISION_T234.md)移除Token T1，保留T2–T4编号；工具定义归低命中现有一致性/漂移职责，不增长度精简。当前新设计/计划/推荐/视觉验收仅T2–T4；旧源码及TA000–006历史仍含T1，不冒称已删除。当前实施计划见[BATCH_PLAN_ARTA](BATCH_PLAN_ARTA.md)，三卡样例见[AR-T3](FRONTEND_REWORK_EXAMPLES_ART3.json)。本轮仅文档同步，暂不编码打包部署。

2026-10-31。用户认可AR-T2实施方向，本轮仅完成文档对齐与最小业务策略清单，暂不编码、打包部署。Token提供方01a18fcd-0464-7cf1-b435-4f394bd33e66；公共提供方01a18be2-7112-7aa2-919b-5137d1f1b1ad。前端只读，无参数/授权/评估表单。下列为提交公共方核对的具体协议；签收记录见末节，不提前代签。

## 1. 对AR-L2提案的接纳与版本统一

接纳[AR-L2](../prefix-analysis/FRONTEND_REWORK_RECEIPT_ARL2.md)独立扩展 `analysis-recommendations-1`、`recommendation-group-1`；替代AR-T2视觉样例的 `token-recommendation-draft-1` 名称。后者保留为旧展示草案，不能产生第二套公共契约。analysis-common-1.0、diagnostics-http-1、discovery-1不静默改写。当前新协议尚未实现；设计对齐不代表Schema/路由已部署。

公共方唯一维护推荐Schema、推荐/差异只读路由、分组稳定ID及结果存储。采用AR-L2提出的独立capabilities、recommendations列表/单项路径；公共R0负责给出确切Schema/分页/兼容声明，Token不扩旧ItemKind。本次Token侧协议冻结对象为下述适配器、支持关系、计数和状态语义；运行时冻结文件交付身份另外记录，不把文档通过称作代码交付。

所有新列表要求有明确终止游标及稳定快照语义；推荐与证据读同一封存任务。旧HTTP offset分页规则不可类推到新路由，最终取公共方定稿。旧报告没有推荐扩展时明确legacy/not_computed，不GET补算。

## 2. Token独立方案适配器（设计名 token-auto-proposals-1）

不改冻结AnalysisPlugin四方法。公共方调用一个静态注册、版本固定的Token方案适配器；方法签名与wire最终由公共R0收口，本线不另外注册worker/router。

输入：原scope身份、单请求RequestView、该请求的已校验AnalysisFragment及fragment_id、当前任务冻结的recipe/依据配置快照、能力描述和预算/取消控制。所有配置只从后台可信配置源注入，不从raw请求文本当作授权。配置与引用映射冻结digest，执行中变更则停止/重新发起，不静默换配置。

输出每个提案：adapter_version、recipe（规则/handler及版本、稳定目标选择语义、参数生成规则与摘要）、support_refs、request_targets（每个准确Location及参数）、basis、applicability、具体title/change_summary与示例选择提示、reason_codes。不得在此执行编码/回放/写库。重复请求输出确定性，同一输入与配置得到相同规范化提案；公共生成推荐ID。

support_refs接纳公共类型化联合：Token使用token_observation，含fragment_id、observation_id、unit_ids/location_ids、RequestKey/raw_sha256；finding_refs可为空。一个提案可支持多条观察，T3没有Finding合法。引用必须属于同一原任务/scope，按fragment_index核对；不把recommendation_id塞进旧Plan.finding_refs。

recipe级字段不含某条请求raw_sha或消息序号，target级必须含这些精确身份。跨请求只有工具定义身份、规则/handler版本、目标语义、参数生成规则、依据及实际适用条件一致才归组。不同引用值可属于同一映射规则，但每个target记录实际参数摘要。相同handler/规则/工具名不构成归并充分条件。

公共group_basis限同task/scope/direction，包含recipe规范化元数据和依据digest。业务JSON参数保持精确值/数值词法，不任意规范化正文。实际目标集合摘要参与封存推荐身份；重复提案去重不丢支持关系。同一组重放一次；相同操作但不同依据可共享评估，不能隐去不同适用条件。T2/T4相同unit或父子重叠不得累加为内容浪费；冲突方案不自动组合。

## 3. typed basis与首批配置

每份basis包含kind、ref、revision、digest、source、适用appid/服务/工具定义/内容范围；配置快照可含多个按规则作用域匹配的basis。kind为business_policy、explicit_authorization或offline_hypothesis。来源可为项目文件或现有业务配置引用；必须可追溯到具体内容，不以任意非空字符串代替业务依据。

- T2：business_policy明确允许投影fields/field_level，或行/条目保留方式、数量/区间；limit仅异常判据，不自动授权删字段。需准确匹配返回结构与工具版本。
- T3：explicit_authorization绑定引用协议、工具定义、载荷摘要到真实引用值的映射，或完整重复普通消息可删除约定（角色/位置选择、保留副本）；派生授权仍复核Observation成员。缺协议不构造引用；offline_hypothesis不允许绕过该要求。
- T4：business_policy包含keep_last、retention_unit、选择范围、replacement生成方式与准确内容/可信来源；K=0须明确。省略标记必须被业务允许且不冒充摘要；引用必须真实。

首批默认只启用完整依据驱动的recipe。offline_hypothesis作为协议可表达类别保留，但实际recipe默认禁用，未批准具体裁剪/保留档位前不生成。未知kind、未知handler/协议版本、配置自相矛盾属于配置/技术错误，不能降级成正常“业务没提供”。当前代码business_basis_ref与prepare要求不被本文放宽；后续实现须由适配器校验typed basis后传递可审计引用，且保留原guard。

配置快照必须区分：方案器是否安装/启用、recipe是否支持、业务依据是否存在。安装的方案器完整检查后明确缺业务依据可正常给no_feasible_plan；方案器缺失或声明启用但配置无法解析不能伪称所有场景缺依据。

## 4. 影响请求N/M与变化值

M为原report.scope.request_count。matched_requests为完整匹配扫描得到的RequestKey并集；若扫描未完成，只给checked/matched_so_far，不包装成完整匹配数。候选位置数/重复次数与请求数分开。

N仅在available且coverage.complete、before.n=after.n=M时取modified_before.n=modified_after.n；要求修改子集存在且计数有效。当前modified统计定义是raw_after != raw_before，非P减少数、非语义变化数。完整noop为N=0；修改原文但P不变时N可大于0。新结果缺modified计数为不完整契约，不以0补齐；旧报告缺值为unknown。

blocked/failed/not_run/interrupted或准备受阻时N=null，即使Plan明确列目标也不能当实际修改；matched可单独显示“涉及N条（未评估）”。每个方案独立N/M，跨卡不相加；多规则共享同一方案只保留一份计数。scope跨窗口/模型资产/配置不混合。

默认显示全scope before/after.p和.c，Δ=after-before，ratio=Δ/before精确分数；before=0时比例null，Δ仍可表示。正值为增加、负值为减少。输入减少而计算增加不得称整体成功；零负收益保留。modified子集可另列，但不加到全scope。静态回放不能证明输出Token、质量、线上性能或Agent执行行为。

## 5. 推荐、评估与任务三层状态

接纳公共proposal_status/preparation_status/evaluation_status分列，不沿用AR-T2样例中单一status作为正式协议。具体枚举拼写以公共定稿为准，以下语义必须保持。

| 情况 | 推荐/评估语义 | 任务与发布语义 |
| --- | --- | --- |
| 完整检测匹配，无对象适用 | not_applicable，匹配数完整，无Plan/评估 | 可ready；说明不适用，不伪称有收益 |
| 方案器已安装且完整检查，缺模板/允许字段/真实引用/保留替换依据 | no_feasible_plan及具体依据原因；无Plan/after | 可ready；明确未形成可评估方案，不显示“没有问题” |
| 完整依据、准备成功、同scope回放完整 | proposal可行、prepared、evaluation available；零负也available | 所有必需工作均完成才ready；发布关联后通知 |
| 已声明需要但适配器/recipe实现缺失，配置坏/版本不支持 | 技术失败/unsupported；不得标依据不足 | partial或任务级failed，按公共源级错误规则；保留旧默认 |
| 匹配/生成预算停止，准备guard/协议失败，任一应执行评估失败或未完成 | coverage不完整或blocked/failed/not_run；原因、旧证据保留，after不可用 | partial；取消为interrupted、共享源损坏依现有failed/停止规则，不为默认展示强行ready |
| 选择范围为空 | 无收益 | 维持empty，不更新默认 |

业务缺依据reason建议独立命名空间：BASIS_T2_RETENTION_RULE_MISSING、BASIS_T3_REFERENCE_OR_DELETE_AGREEMENT_MISSING、BASIS_T4_REPLACEMENT_RULE_MISSING；这些只能由成功完成资格检查的适配器返回。技术原因复用已有guard/budget/source错误，并增加适配器缺失/配置无效类别，由公共方统一注册，不靠前端解析中文判断。

T3协议形状已检查且明确不属于支持业务场景可not_applicable；声明支持却缺实现/解析失败归技术失败。有效依据明确不匹配当前内容可not_applicable；不能把坏配置归不匹配。区分资格检查与已准备执行后失败。

公共封存recommendation→Plan→Evaluation关联后，同一终态事务发布目录再通知。任一必需技术步骤未完成不替换旧默认；已有partial保留旧默认、整体ready更新已含方向规则不变。读取只GET，不触发重算；历史旧报告不追补。

## 6. 最小业务确认清单

不重复询问是否自动收益、是否前移、是否前端参数输入。当前没有真实recipe配置可直接证明T2–T4均具备业务依据；现有policies_json/PolicySpec只提供部分检测配置，测试fixture与视觉样例不能作为业务授权。

需要用户给出的最少信息可按一份后台配置/规范路径统一提供，不必在页面逐条填写：

1. T2允许字段/行条目选择、T4保留K+单位+替代内容：是否有现成工具/业务规范可作为来源；有则提供入口，后台按内容匹配生成方案，无则这些分支先保留明确缺依据状态。仅给K或字节上限不足。
2. T3是否已有真实引用协议与映射，或允许删除特定普通重复消息的约定；有则给协议/配置来源。没有时不制造引用或默认删除，也不阻碍其他规则链路。
3. 无业务配置时是否本轮启用“明确假设”的T2/T4方案：建议首批先关闭。若用户选择启用，必须一次性确定有限保留方式/档位及合法替代模板；不采用样例中的K=2作为默认，不需要前端表单。

上面业务内容未提供不妨碍ARTA000接口设计对齐与后续构造数据测试，但限制对应真实业务场景可产生收益；不能称全部业务收益已就绪。自进化Agent/LLM改写/自动线上修改仍排除。

## 7. 对齐签收与ARTA000退出

退出要求：公共维护方对版本/适配器职责、support_refs与分组、N/M及null、状态/发布、依据缺失分类书面确认；遗留业务参数与运行时未实现身份分列。公共R0的机器Schema/实现由其维护，未交付时不能称公共扩展已可调用。

当前：公共方已提供[ARTA000_PUBLIC_ACK](../prefix-analysis/ARTA000_PUBLIC_ACK.md)，逐项书面签收；Token侧接受第8节公共收口并完成[ARTA000文档退出](ARTA000_RESULT.md)。ARTA001及后续编码本轮不启动。

## 8. 接纳公共AR-C1精确收口

权威版本/字段/路由/预算见[AR-C1工程基线](../analysis/RECOMMENDATION_CONTRACT_ALIGNMENT_AR1.md)，本节覆盖前文提议的不确定项，不另建第二份Schema。

- 适配器名统一token-auto-proposals-1，含describe/validate_bundle/propose/prepare_proposal；typed basis经专属prepare复核，不改旧H0 prepare。
- recommendation_id不含task_id，含scope/方向/generator/recipe/支持集合/策略快照；同输入重建可同ID，读取/缓存必须绑定实例+task+scope+版本。分组执行限当前task，不跨任务借评估。
- basis精确结构采用kind/ref/revision/digest/scope_selector/authority/assumptions/limitations；依据缺失为null。公共reason采用RECIPE_BASIS_MISSING、REFERENCE_MAPPING_MISSING等，Token专属缺项放有类型的reason_details；不另冻结前文建议的BASIS_T*别名。
- support_refs字段采用公共token_observation（observation_ids数组），N/M为impact.modified_requests/total_requests；未完成匹配matched_requests=null，以matched_checked_requests及match_complete表达检查覆盖，不自行添加另一套matched_so_far计数。
- 公共列表采用封存task稳定offset/next_offset分页，末页null；不新增可变快照，discovery目录仍用既有snapshot。推荐同任务封存后只读，旧报告availability=not_computed。
- 缺业务依据且检查完整可advice_only/ready；非法或越权授权BASIS_INVALID/AUTHORIZATION_SCOPE_MISMATCH为blocked/partial，不能当普通不匹配；有效作用域中没有目标才not_applicable。合法空bundle与丢失/损坏bundle区分，前者明确configured_recipe_count=0，后者技术失败。
- 不同依据先独立validate/prepare，再按完整执行内容与编码/账本身份比较并复用canonical Plan/Evaluation；prepared_plan_ref、execution_plan_ref分别保存，evaluation.plan_id必须指向执行Plan，不伪称执行过别的Plan。
- 预算使用公共recommendation-budget-1独立快照、固定处理顺序，实际参数见AR-C1第7节。首次默认是工程有界配置、非生产SLA；现有更严格限额继续生效，不让前端填预算或任务中自动提额。256请求级proposal等限制可能使较大范围partial，必须真实报告覆盖，后续资源验证不能以缩scope掩盖。
- 提交与幂等重用原快照，retry也用原快照；新配置/新预算必须新意图。局部证据统一evidence-locator-1，Unicode code point半开span，无可靠定位不伪造高亮。

以上均为设计语义签收；尚无新运行时Schema/路由/自动链路实现或联合测试，不启动ARTA001。

公共签收补充：来源统一authority.source_kind/source_ref/source_digest，不保留平行basis.source。适配器propose明确包含scope_id、fragment_id、capabilities；具体签名和结构以AR-C1为准。

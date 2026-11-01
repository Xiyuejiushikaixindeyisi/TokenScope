# AR-L2 推荐聚合、局部证据与公共自动评估回执

2026-10-31，公共/低命中会话01a18be2-7112-7aa2-919b-5137d1f1b1ad。依据AR-02最新决定；覆盖旧“L4/L5业务详情铺全文”和“Token自动收益延至V3”的设想。AF006用户验收不通过，旧测试通过不代表产品通过。本轮先交付范围/映射、扩展设计、视觉样例与实施依赖，**未实现下述新推荐协议、自动Token编排或正式前端**。不打包部署、不启动Agent、不跨会话发消息；Token旧入口的V3描述不作为当前授权边界，也不越权修改该线文件。

## A. 推荐与差异聚合

### 已有字段、严格推导、新增提案

| 内容 | 现有事实 | 严格可推导/新增缺口 |
| --- | --- | --- |
| 具体方案 | finding.recipe_json、rule_id/version；experiment.finding_ids；plan.transformation_digest/operations/finding_refs；evaluation.plan_id/scope_id | 同一已保存recipe的多条finding可归并；不能仅按rule_id，不能把L4补挂L1收益 |
| 代表观察 | 当前service使用recipes.setdefault(recipe_json,finding)，仅代表项进入实验 | 完整读取finding后，用**相同recipe_json、规则版本、scope**反向找到代表项的同组观察；不同recipe即使advice相同仍不同方案；新增持久成员清单避免前端重复实现聚合 |
| 推荐对象 | 没有独立recommendation/result grouping API | 新提案recommendation，保存稳定ID、精确group_basis、member/support refs、plan/evaluation refs及完整性；由后端生成，前端不自行hash身份 |
| L4/L5差异对象 | 每条finding携带comparison两端/路径/证据状态 | 两端RequestKey并集可算发现涉及请求数；**没有现成精确上下文分组ID**，拟增加difference_group；前端不得仅按规则吞并所有上下文 |
| 局部文本 | comparison全文、指针；Plan目标指针/替换文本；Token Location可有range/embedded | 指针可用无损定位器提取字段；L1/L3识别器内部有槽位位置但未全部发布，新提案补source span/decoded span及映射版本，避免前端猜offset |

推荐分组提案 `recommendation-group-1`：限同task/scope/方向；规范化**元数据**recipe（不规范化业务JSON）、规则版本、handler版本、basis/策略摘要组成group_basis。L1/L3至少含slot_key、pattern、slot_index、完整shape；L2含完整工具集合set_digest与固定排序变换。不同槽位、静态shape、工具集合、依据或作用范围不合并。相同完整Plan变换若由多规则支持可以一方案多rule refs，但须公共编译验证一致，不能仅凭文案相似。

拟议ID=版本+task_id+scope_id+group_basis的确定性摘要；对同一封存报告稳定，新task/新scope另ID，不承诺跨月相同ID。member/support refs保存具体来源；实际编译适用范围仍由guard及全scope Plan决定，观察成员数不是变换覆盖数。组合只展示已存在且独立回放的完整组合，不在本轮自动组合穷举。

针对6请求/15 L1+15 L4：若15个L1的recipe完全相同，则1个L1方案组；以其代表experiment→full evaluation→plan的相同scope、transform digest和完整资格证明收益。同组其它14个finding是支持证据，不各自生成卡，也不拿无收益差异卡占位。其Plan确实修改6个不同RequestKey才显示6/6。15个L4若精确上下文键相同，形成1个L4差异组，发现涉及并集6，最多3例；与L1可以共享底层原文引用，但不继承其收益/修改建议/因果判断。若L4上下文不同则保留不同组，不能承诺无条件所有L4只一张卡。

L4分组键提案：rule/version、同scope、差异指针集合、对应消息role/type/调用结构、未改变字段的精确上下文指纹；只在指定差异值上放置带类型占位，绝不删除其它动态字段。若已证实是同一L1/L3槽位差异，可引用其精确slot shape作为上下文，不以整条message无条件占位。未知/多义位置不合并，返回grouping_status=unresolved并保留事实，不额外设置收益门槛。

L5分组键提案：rule/version、同scope、对应工具结果位置及可验证工具身份、严格结构值指纹（保留类型、数组顺序、数字词法）、表示差异类别和相邻调用结构。相同结果内容不同缩进可归组；不同结果值/不同工具或上下文不因都属于L5而合并。缺可靠工具名则用明确unknown及已有调用结构，不猜同工具。L4/L5发现即显示；grouping不能作为隐藏已发现事实的理由。

## B. 数量与收益

- RequestKey去重键为 `(base_run_id,source_record_index)`，不是hash_id、正文摘要、消息路径或操作ID。
- 优化主卡：`modified_request_count=evaluation.modified_before.n`（与modified_after.n一致），`analysis_request_count=report.scope.request_count`，比例是两者精确分数。前提为同scope完整full/direct_full、plan适用范围一致；label明确“本方案实际修改请求”。Plan目标并集只是选定目标，含noop时不能替代实际修改数；有需要由回放行的实际changes/原后摘要验证，不直接数operations。
- 主卡只显示实际修改数/比例、before.h/before.p、after.h/after.p与gain_percentage_points，不显示Token变化；公共原P/H/C/J仍保留供审计，不从后端删掉。提升是绝对百分点，不用四舍五入判断。完整full/direct_full严格>1pp且有具体方案才入优化卡；恰1pp、不完整、无方案或无full的L1–L3不出现占位差异卡。pilot收益不贴作全范围收益。
- L4/L5：`observed_request_count`为该组**所有已保存成员**comparison两端并集；`sample_count`为选出的1–3例数，单列。分母仍scope总请求数。检测候选有界/成员分页未读完时标“已发现涉及X/N，发现覆盖不完整/未知”，不称真实总受影响数。发现通道覆盖和evaluation.coverage不同，不用完整回放反证完整检测。
- 分组和跨规则都可能涉及同请求；不能把6(L1)+6(L4)变为12/6。全报告如需唯一请求汇总，必须对已定义统计集合再做RequestKey并集并说明集合，不能加卡片数值。
- 样本排序不影响数量计算；前端只加载3个例子时，数量由后端完整成员统计返回，并携带统计范围/完整性。不把3当检测上限、问题组总数上限或全报告上限。

## C. 局部证据与例子

业务详情仅显示相关字段/message/动态区及必要上下文，**不铺完整请求、Plan、版本/身份JSON**。底层完整原文仍只读保存供校验，指针和摘要可作为内部追溯字段，不要求业务UI展示技术JSON。

已有全文GET加可靠JSON Pointer足以提取中小字段：使用保留原数字词法、重复key判别、转义映射的JSON词法定位器，按pointer解析位置；严禁全文第一次substring定位，也不JSON.parse→stringify改写证据。字段缺失、重复key路径多义、原文摘要不匹配返回明确不可定位，不伪造span。接口全文可被读取不等于页面必须铺全文；64KiB请求只展示局部。

具体动态片段：拟发布`raw_span`（原始UTF-8文本对应的Unicode code point半开范围，非JS UTF-16）、`decoded_span`（字符串解码后的code point范围）、pointer及映射版本；解码范围不能直接当原文offset。涉及内嵌JSON需outer pointer+embedded pointer+外层字符串guard+映射链。未有可靠span时可以显示通过pointer可靠提取的整个**相关字段**并显式截取上下文；巨大字段也必须按可靠range局部展示，位置不足需补后端locator而非前端猜测。

证据对象提案包含source_ref(task、RequestKey、raw_sha256)、pointer、实际slice/text、offset_unit/ranges、context_before/after、omitted_before/after、locator_status。`pair_difference`是请求A/B，`proposed_edit`是同请求修改前/后，分开标注；不能把两个请求的差异伪称系统修改前后。修改后文本只能来自Plan/已有after_raw或已编译准确操作，不由UI自由改写方案。

例子选择：全部成员完成归组/去重后，按源时间+source_record_index确定前后，按两端RequestKey及路径/片段摘要去重；不同变化签名优先覆盖，签名同一时最早请求对优先，稳定打破并列；最多3例、少于3不补。序列排序字段不在旧finding里时，后端从源索引取得并保存；旧报告只读兼容可使用稳定RequestKey排序并标选择方法，不能编造时间。若某例定位失败选下一有效例并保留失败计数；无可定位片段仍保留发现卡，明确证据位置待补，不显示假样本。

## D. Token初始任务自动建议/评估的公共集成提案

**本次必须交付目标**是后台自动形成具体建议与已有离线量化结果，前端零POST/零参数/零授权表单；不推迟V3。但当前H0插件只提供describe/validate/analyze/prepare，service初始Token仅保存fragment/index，未接自动proposal→Plan→Evaluation。以下为补充设计，不冒充已实现。

拟独立扩展 `analysis-recommendations-1`（未冻结），与H0、diagnostics-http-1、discovery-1并存。不直接增加旧ItemKind枚举或改冻结EvaluationResult；拟新增只读 `GET /diagnostics/recommendations/capabilities`、`GET /diagnostics/tasks/{id}/recommendations`、`/recommendations/{recommendation_id}`、`/difference-groups`、`/difference-groups/{group_id}/examples`。能力Schema/分页细节在R0冻结，当前URL**不可调用**。存储可用新私有kind，但必须通过新路由读取，不让旧HTTP Schema悄然变更。

推荐对象最少字段：version/recommendation_id/task_id/scope_id/direction/rule_refs、group_basis及members_complete、`support_refs`、`recipe_ref/basis`、具体修改描述、applicability、plan_refs/evaluation_refs、影响计数/覆盖、局部例子引用、proposal_status/preparation_status/evaluation_status/reason_codes、display_qualification。support_refs是类型化联合：prefix_finding 或 token_observation（fragment_id、observation_id、unit_ids/location_ids、RequestKey/raw摘要），finding_ref可空。**T3只有Observation时直接支持推荐，不制造Finding占位或要求非空finding_refs**；公共Plan如需关联推荐，使用扩展映射而非把recommendation_id塞进语义为finding的字段。

执行顺序提案：冻结原scope与资源/策略快照→现有低命中探测/评估→Token遍历原文、保存fragment/index→Token自动方案器依据版本化配置生成有完整参数的proposal/不可行原因→公共按精确recipe+依据/目标上下文归组→插件prepare在每个目标原文上复核→完整Plan及支持关系保存→复用evaluate_plan对原scope**独立**回放→保存evaluation与推荐关联→完成报告与目录终态事务→SSE通知。不能用低命中修改副本作为Token基线；多个方案独立，不串联污染或自动组合穷举；保存本报告内完整关联，不依赖追补历史子任务。

Token方案器拟用独立版本适配器协议（不修改冻结AnalysisPlugin）：输入已有RequestView/fragment、后台策略/recipe快照、能力和预算；输出提案含support_refs、精确参数、目标选择规则、typed basis（business_policy/offline_hypothesis/explicit_authorization）、适用性/限制/停止原因。Token只负责具体recipe及受保护变换准备，公共唯一负责scope、Plan、编码回放、状态/持久化/通知。聚合后的每个目标都必须有准确参数及guard；不能拿一个请求的replacement通用覆盖其它内容。

预算：公共任务总编码上限保持，新增自动建议数/准备目标数/Plan字节/评估数等预算由版本化服务端策略快照提供，不能临时扩张旧RuntimeOptions Schema或要求前端填。分析一开始冻结预算/策略digest；按确定顺序处理，逐项/阶段检查取消。单次失败不丢目标偷偷缩scope，也不执行其它recipe替代来伪造通过；预算不足保留proposal/Plan/原因与无after，不扩样本或自动提额。

| 情况 | 推荐/评估与任务语义（提案） |
| --- | --- |
| 全部已启用规则/方案资格检查完成，得到可评估方案且全部规定评估完成 | ready；Token/combined零负收益可读，不套低命中>1pp；结果质量/可行性单列，不保证优化 |
| 资格检查完整，确定无适用方案或缺该场景真实依据 | 记录no_feasible_plan/not_applicable及具体原因，数量完整；可ready但明确“未形成可评估方案”，不能显示“未发现异常”或伪收益 |
| 规则/方案器缺失、应运行模块不支持、预算/时间停止、准备失败、评估失败/未完成 | partial（或源级failed/interrupted），已有成果保留，不把未查/失败伪装为无方案完成；旧默认报告不替换 |
| 取消/源变更/协议guard失败 | 沿公共原规则停止或阻断，不发布after；原因可读，ready不能为了默认目录展示而放宽 |

“业务语义缺依据”和“技术未完成”必须由Token返回有版本的reason code区分；若方案器没配而宣称启用自动收益，是模块缺失partial，不是所有场景no_feasible_plan。新能力未启用的旧报告按legacy/not_computed展示，不追补、不重算、不伪装具备新推荐。

Token方需确认/回传：首批T1–T4 recipe参数与typed basis精确结构；T3无Finding的Observation/Unit成员选择；目标匹配/工具版本与参数生成；无策略时假设方案是否已获具体档位授权；错误码中no_feasible_plan与failed/budget的划分；适配器版本和幂等生成规则。缺真实引用/删除依据不能编造协议或把offline_hypothesis冒充业务授权；公共侧不会替Token擅自设裁剪档位或T3权限。

## E. 身份和兼容

当前已实现版本仍analysis-common-1.0、diagnostics-http-1、diagnostics-discovery-1、prefix-detectors-1；[本轮文件身份](FRONTEND_REWORK_IDENTITY_ARL2.json)分开记录读取HEAD和当前工作树SHA，含app装配/公共与本线源码、测试、依赖锁及旧manifest核对。旧local-2/FE-R-L1清单不重写，Token私有身份不代签。

新recommendation/difference_group/grouping/locator协议、初始Token自动评估编排均为本轮**提案待冻结/实施**；当前旧API可只读得到L1–L3代表方案评估及逐对事实，部分聚合可严格推导，但未提供完整持久聚合对象和片段span。前端视觉草图可使用本轮合成提案对象，不得把它标成当前HTTP响应或直接生成正式接口客户端。

## F. 视觉卡片样例

[FRONTEND_REWORK_EXAMPLES_ARL2.json](FRONTEND_REWORK_EXAMPLES_ARL2.json) 为纯合成提案视图，非运行成果，含：6请求/15 L1观察→1完整合格方案；15 L4观察→1差异组（3例）；1个L5表示差异组（1例）。主卡不含Token变化。每例分别注明请求A/B或同请求修改前后、pointer、局部原文、上下文、省略标识及可复算摘要；合成源文本为验证素材，**不进入业务详情**。新字段不是当前冻结API。

示例数仅是展示选择；成员并集独立计数。同规则不同slot/上下文/工具集合仍独立，不合并成“全部动态字段”；L4/L5不附预期收益。样例中的合成收益只用于视觉评审，不能声称已做Tokenizer/回放或保证线上效果。

## G. 分批实施依赖和需决事项

| 批次提案 | 公共方工作/验收 | 依赖 |
| --- | --- | --- |
| R0 对齐/冻结 | 对齐两线proposal/support_refs/basis/reason/预算协议；冻结独立Schema和读接口；检查新旧兼容 | Token AR-T2回传，不重复询问Token是否本轮实施 |
| R1 低命中聚合/数量 | 6请求30观察形状只形成1个合格方案+准确L4组；recipe不同不合；modified n去重；1pp边界；统计与样本分离 | 已确认本回执口径 |
| R2 局部证据/差异分组 | 无损JSON定位、code point/UTF-16区别、重复key/转义/大整数/缺字段；L4/L5发现即展示；每组≤3样本但完整成员并集 | R0；与前端确认视觉样例而非重批业务门槛 |
| R3 Token自动集成 | 同报告proposal→Plan→Evaluation；T3无Finding；独立原scope回放；取消/预算/无依据/无可行方案区分；封存后通知 | Token确定性recipe实现、typed basis和策略来源；公共唯一编排 |
| R4 联合与兼容 | 旧报告只读不追补、partial保留旧默认、Token零负值、只读前端无POST、静态/真实HTTP/浏览器分开验收 | R1–R3及前端视觉评审通过 |

当前足够前端做少量代表性视觉卡片；不能据此称新后端已就绪或AF006已验收。公共版本/路由/预算是工程对齐事项，不要求用户重新决定L4/L5门槛、Token是否前移或是否前端POST。**仅当Token所选无策略裁剪/保留recipe尚无已批准的具体假设值，或T3方案缺真实协议/删除依据，才需其归口提出精确业务决定/资料需求**；不阻塞先做已可表达的视觉卡片。没有这些依据的分支如实标不可评估，不能用泛化权限推测阻断已授权的离线L1–L3建议。

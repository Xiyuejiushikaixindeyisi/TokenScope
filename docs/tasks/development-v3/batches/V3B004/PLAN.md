# V3B004 PLAN — 候选覆盖与重复差异前移汇总

状态：**CLOSED（组件）**。设计r1已按条件授权修订；前置批次关闭后实施，无需重复启动确认。所属条款：D5。总计划：[BATCH_PLAN](../../BATCH_PLAN.md)；设计：[DESIGN](../../DESIGN.md)；底线：[ACCEPTANCE](../../ACCEPTANCE.md)。

## 输入与依赖

V3B003 CLOSED；有唯一clock规范化与B002共享总预算；先固定F03 oracle和V2相同预算基线。

开始前登记：授权消息/日期、实际HEAD与工作树归属、前批CLOSE、设计版本/摘要、环境/模型/配置/契约身份。当前这些实施字段均为待填；不得把文档提交当产品候选。具体预算先记录测试profile，量值不取报告默认300。

## 最小代码范围（拟；本轮未建源码）

- `prefix_analysis/candidates.py`、`structure.py`：有界A特征、索引与确定性前序候选。
- `prefix_analysis/service.py`、`detection.py`、`history.py`：L1/L2/L3/L4/L5通道调度与预算复用。
- `prefix_analysis/recommendation_groups.py`及必要V3聚合模块：前移唯一原因、成员/代表证据边界与新计数；旧投影保留。

不改其他会话dirty、监控业务语义/默认源或历史产物；不开发Token私有规则、P1模板页面/Agent/hybrid。未列接口的跨层变化先说明必要性，不做整包重构。

## 函数级接入点

- 现有定位：`CandidateIndex.lookup/insert`、`collect_dynamics`、`recipe_groups/difference_groups`；新调度替代预算消耗先被宽桶占满的调用顺序。
- 拟增职责边界（名称可批内调整，语义不可静默改变）：`build_discovery_index(A, control)`；`iter_budgeted_pairs(index, policy, shared_budget)`；`retain_cause_group(pair_result, bounded_store)`，分别负责结构/选择/去重，不将B传入。

## 开发步骤

1. 只索引A，缓存有界特征；按encoder/配置、逻辑字段/工具关系建不同通道，不能统一要求全tool定义SHA相同。B不参与模板/候选决定。
2. 实现channel→桶→时间段轮询，分配已启用通道保底/借用份额；K仍是每请求前序上限且≤128，新增task total为全部通道共享。元数据排序与索引成本也计账。
3. 最近/最早/时间分散前序代表确定选取，不枚举所有pair；相同物理pair跨通道复用解析/Token比较并仅计费一次，通道访问另记。为自动clock发现/评估保留预算，不被重复候选挤占；L1桶仅按可比逻辑字段，不按完整历史角色结构。
4. 保留L2相同集合不同顺序，L3共同工具定义/description变化与集合增减，L4/L5受限回退；未知上下文不能为省预算强合并。
5. 在多份plan/大证据构造前用规则+变换/差异+逻辑位置+标准上下文聚合；成员精确去重有界保存，超限只报下界/incomplete，不把观察对数当受影响人数。
6. 对保留代表用实际Token IDs算LCP；分别记录原文差异/输入变化/保留证据。与预先固定oracle比唯一原因覆盖和V2消耗，解释差异，不拿现场收益当候选好坏的唯一标准。

开始实现前补“具体函数与签名/调用方/错误返回”表；批准语义以内的拆文件记录即可，预算放宽、业务改法、协议语义或范围变化回到评审。中途发现问题立即记[ISSUES](ISSUES.md)，不留到最终批猜根因。

## 测试与退出门禁

- 用例：T13、T14、T15，fixture：F01/F03/F04/F07/F09，精确断言见[总TESTS](../../TESTS.md)。
- 本批选择及命令记录见[TESTS](TESTS.md)；所有新测试落点是计划，当前未创建/运行。
- **必须满足**：T13–T15通过；固定同预算fixture覆盖预标稀有clock/L2/L3，确定性/总计数守恒，无隐蔽N²，无旧L4/L5消失或未知上下文误并。大源性能最终在B007复验。
- 必需项NOT_RUN/FAIL/SKIP、阻断未关闭，均不得把[CLOSE](CLOSE.md)改为CLOSED。

## 下一批输入与回退

稳定原因组/recipe输入、覆盖与计数语义、各通道基线对照、残余限制；B005主流程消费封存的A自动finding；指定反事实独立标记不能冒充自动发现。

回退只撤销本批有归属的源码改动/禁用新V3执行注册，保留已封存产物与旧读取；不执行git reset/clean或覆盖他人改动。回退不能自动恢复Token或旧自动full。若已产生新协议结果，保留对应只读适配；运行清理仅针对已核归属的本attempt，禁止删旧state。具体可逆步骤与文件在CLOSE填写。

完成/受阻时同步[本线记忆](../../../../../memory/tasks/development-v3.md)：状态、候选、测试/issue链接、设计变化、下一步；未闭环不能进入下一批（最终批LOCAL_VALIDATED特例按总计划）。

## 本批实际接入（2026-11-10）

沿用本会话连续推进授权、main 9a071c87 与 B003 候选及既有脏工作区，不接管其他改动。入口改为独立 candidates_v3.CandidateSchedule.pairs → collect_clock；旧 CandidateIndex 和旧结果读协议保留。

- feature_keys(RequestView, body)：encoder/options + clock逻辑字段/外部形状；L2工具集合、L3共同工具名；L4/L5仅请求对证据。
- CandidateSchedule(buckets, candidate_limit=16).pairs：channel/bucket/time轮询，单请求跨桶共享K≤128；总比较由同一BudgetLedger控制。当前16为内部候选策略参数，非默认样本数或业务门槛。
- collect_clock：物理pair缓存一次，读取IDs缓存一次，保留clock改法和L2–L5原因组，成员去重；预算停止返回complete=false+原因码，观察人数仅已覆盖下界。没有推断session。
- SampleResolvedSource：只增加成员/文件查找缓存，仍每次核验文件摘要，不缓存可信读取。
- 不采用旧低效group逐pair排序成员：收集set后结尾一次排序，避免重复成员汇总出现二次复杂度。

测试入口 test_candidates_v3，固定47请求oracle、12比较预算及实际旧CandidateIndex同预算参考；旧参考为早期宽桶流式场景，不宣称全面优于V2。最大1000请求×5通道×K3验证候选输出上界。结果与剩余门禁记TESTS/ISSUES。


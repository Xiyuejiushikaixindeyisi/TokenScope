# V3B005 PLAN — 同样本评估、独立复核与可发布解释

**当前范围决定（2026-11-11）：显式 full 延期（DEFERRED_BY_USER，未实现/未运行，不记PASS），不再是本期V3门禁；自动full仍禁止。候选repair-r1-02为LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING，独立R2已关闭RV3-01/02/03。大源自动缩样和五组session_clock样本参考率优先，真实BUS01–05及现场AC-MEM待华为验收。暂不打包。**

本条为最新状态，覆盖下文历史“待裁定/待独立复验”；原日志、原失败与当时勘误保持。B005按修订范围CLOSED；B007本地收口，整体现场门禁未关闭。见[本地收口](../../LOCAL_ACCEPTANCE_CLOSE_20261111.md)、[华为交接](../../HUAWEI_ACCEPTANCE_HANDOFF_20261111.md)。

状态：**CLOSED（组件）**。设计r1已按条件授权修订；前置批次关闭后实施，无需重复启动确认。所属条款：D6/D7。总计划：[BATCH_PLAN](../../BATCH_PLAN.md)；设计：[DESIGN](../../DESIGN.md)；底线：[ACCEPTANCE](../../ACCEPTANCE.md)。

## 输入与依赖

V3B004 CLOSED；A自动L1 findings及变换已冻结，B封存未参与候选；资源与快照全链可用。

开始前登记：授权消息/日期、实际HEAD与工作树归属、前批CLOSE、设计版本/摘要、环境/模型/配置/契约身份。当前这些实施字段均为待填；不得把文档提交当产品候选。具体预算先记录测试profile，量值不取报告默认300。

## 最小代码范围（拟；本轮未建源码）

- `prefix_analysis/experiments.py`与新V3编排：冻结变换、每窗guarded plan。原计划显式full已于2026-11-11由用户延期，不再纳入本批。
- `analysis_common/evaluation.py`、`encoding.py`：抽取可复用统一回放核心，保留旧full语义；不复制monitoring缓存策略。
- 新V3 outcome/publication/storage，必要复用 `recommendation_pipeline.py`、`recommendation_publication.py`核心；新增API读取与schema实例。

不改其他会话dirty、监控业务语义/默认源或历史产物；不开发Token私有规则、P1模板页面/Agent/hybrid。未列接口的跨层变化先说明必要性，不做整包重构。

## 函数级接入点

- 现有定位：`experiments.pilot_scope/run_experiment/compile_combination`旧自动链；`evaluation.evaluate_plan`复用计算；`publish_low_hit`旧full资格保持独立。
- 拟增职责边界（名称可批内调整，语义不可静默改变）：`freeze_transformation(A_result, intent)`；`evaluate_window(snapshot, frozen_recipe, control)`；`publish_outcome(sealed_windows, execution)`；显式full单独入口，无收益触发分支。

## 开发步骤

1. 在读取B内容前封存transformation_digest、A自动finding/请求对/字段关联、适用条件及业务限制。先A评估再以同规则生成B具体守卫，不能看B改规则/样本或挑最优N。
2. 每窗before/after成员和顺序完全相同、独立空PrefixLedger；原输入验证编码/P/SHA，after只来自guarded副本。保持统一encoder/assets/策略，完整窗才能发布after。
3. 实现N、matched/modified、P/H/C与命中率/pp差值的整数/有理数计算和P=0不可用；保留逐请求索引供独立复算。A/B各自展示，不混成一个推广总体值。
4. 完整状态表覆盖no_targets/no_op/not_evaluated/budget/cancel/failure/zero/negative及B不可用/不一致；完整性、收益正负、业务允许、旧优化资格独立。A完整B失败保留A，未完整B无完整after。
5. 新V3样本结果不经过旧full/direct_full >1pp过滤；旧报告/资格不降门槛。冻结发布对象引用核验，部分任务只发布已提交证据。
6. 断开所有pilot自动full连线；显式full新任务/范围/预算/prepare且仍受资源约束，不为了full要求无界加载。整个选定scope=A可评估而不报pilot不足。

开始实现前补“具体函数与签名/调用方/错误返回”表；批准语义以内的拆文件记录即可，预算放宽、业务改法、协议语义或范围变化回到评审。中途发现问题立即记[ISSUES](ISSUES.md)，不留到最终批猜根因。

## 测试与退出门禁

- 用例：T16、T17、T18、T19，fixture：F01/F08/F09/F11，精确断言见[总TESTS](../../TESTS.md)。
- 本批选择及命令记录见[TESTS](TESTS.md)；所有新测试落点是计划，当前未创建/运行。
- **必须满足**：T16–T19通过，独立算术核对/实际Token回放一致；B不泄漏、不调参，A成功保留；自动full调用=0，所有状态经过API后仍保真。
- 必需项NOT_RUN/FAIL/SKIP、阻断未关闭，均不得把[CLOSE](CLOSE.md)改为CLOSED。

## 下一批输入与回退

封存成功/零/负/partial/无B等真实新报告fixture，字段语义、独立计算记录、前端显示所需精确片段/指标与引用；B006不得自行重算或填默认值。

回退只撤销本批有归属的源码改动/禁用新V3执行注册，保留已封存产物与旧读取；不执行git reset/clean或覆盖他人改动。回退不能自动恢复Token或旧自动full。若已产生新协议结果，保留对应只读适配；运行清理仅针对已核归属的本attempt，禁止删旧state。具体可逆步骤与文件在CLOSE填写。

完成/受阻时同步[本线记忆](../../../../../memory/tasks/development-v3.md)：状态、候选、测试/issue链接、设计变化、下一步；未闭环不能进入下一批（最终批LOCAL_VALIDATED特例按总计划）。


## B005实际函数方案（实施前）
2026-11-10，B004 CLOSED后按连续授权进入。新增evaluation_v3.evaluate_window复用EncodingContext与monitoring.make_strategy，分别为A/B创建独立before/after磁盘ledger；不调用旧pilot/full。窗口完整才返回P/H/C与有理数pp，失败仅状态/原因，不返回完整after。逐请求行与guarded plan在新任务目录封存。
新增diagnostic_store_v3保存诊断任务（绑定完成prep、幂等提交、取消、崩溃恢复）；既有PreparationService在同worker.lock下串行领诊断任务，同一受控worker运行，不新增服务进程。新增V3任务/报告API只读封存checkpoint，旧GET/旧资格不变。前端显式提交prepare、完成后提交诊断；没有收益自动full入口。
错误语义：NO_APPLICABLE_TARGETS/NO_MODIFICATION、BUDGET_EXHAUSTED/USER_CANCELLED/FAILED、NO_REVIEW_WINDOW分别保留；A已封存不受B失败覆盖。字段业务影响与数值正负独立，报告明确样本副本/非无损/现场五业务待验。


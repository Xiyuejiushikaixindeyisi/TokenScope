# V3B005 TESTS — 待执行

**当前范围决定（2026-11-11）：显式 full 延期（DEFERRED_BY_USER，未实现/未运行，不记PASS），不再是本期V3门禁；自动full仍禁止。候选repair-r1-02为LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING，独立R2已关闭RV3-01/02/03。大源自动缩样和五组session_clock样本参考率优先，真实BUS01–05及现场AC-MEM待华为验收。暂不打包。**

本条为最新状态，覆盖下文历史“待裁定/待独立复验”；原日志、原失败与当时勘误保持。B005按修订范围CLOSED；B007本地收口，整体现场门禁未关闭。见[本地收口](../../LOCAL_ACCEPTANCE_CLOSE_20261111.md)、[华为交接](../../HUAWEI_ACCEPTANCE_HANDOFF_20261111.md)。

**全部NOT_RUN，无PASS数量、性能值或截图。** 依[总TESTS](../../TESTS.md)的固定断言，不得将本页写成独立降级门槛。关联[PLAN](PLAN.md)、[ISSUES](ISSUES.md)。

评审r1追加必需断言：正常诊断不预指定clock位置/recipe/finding，自动L1证据→改法→评估/展示（按本批职责）必须可追踪；同一可比system/developer字段clock外一致、后续历史长度/角色序列不同为正例，固定clock/不相关模板/字段不兼容为负例。手动反事实成功不替代自动门禁。见[修订核对](../../REVIEW_FIXES.md)。

## 用例映射

| 必需ID | fixture / 输入 | 最终测试node ID | 结果 | 日志/issue |
| --- | --- | --- | --- | --- |
| T16 | F01/F08/F09/F11 | 实施时填写 | NOT_RUN | 尚无 |
| T17 | F01/F08/F09/F11 | 实施时填写 | NOT_RUN | 尚无 |
| T18 | F01/F08/F09/F11 | 实施时填写 | NOT_RUN | 尚无 |
| T19 | F01/F08/F09/F11 | 实施时填写 | NOT_RUN | 尚无 |

新增测试建议（尚不存在；实际路径/函数必须实施后回填）：

- `tests/integration/analysis/test_sample_evaluation_v3.py`
- `tests/integration/analysis/test_outcomes_v3.py`

受影响已有回归：

- `tests/integration/analysis/test_evaluation.py`
- `tests/integration/analysis/test_experiments.py`
- `tests/integration/analysis/test_recommendation_publication.py`
- `tests/integration/analysis/test_diagnostic_combinations.py`

## 环境与命令

源码/dirty、设计/schema/模型/encoder/profile/fixture/sample摘要、Python/依赖/OS硬限制、时间与cwd：**待填**。预算/profile在测试前固定；无资产不自动下载，缺环境记阻断，不能SKIP后报通过。

以下为实施完成后的命令草案，当前未执行；cwd为项目根。新增文件须先落实，实际执行保存确切命令。basetemp每次使用未存在的attempt路径，pytest可能清理指定临时目录，禁止复用已有证据路径。

```bash
.venv/bin/python -m pytest tests/integration/analysis/test_sample_evaluation_v3.py tests/integration/analysis/test_outcomes_v3.py tests/integration/analysis/test_evaluation.py tests/integration/analysis/test_experiments.py tests/integration/analysis/test_recommendation_publication.py tests/integration/analysis/test_diagnostic_combinations.py --basetemp=artifacts/validation/development-v3/V3B005/attempt-01/pytest -q
```

质量检查按受影响Python模块执行ruff/mypy；总全量回归在B007，除新失败/新变化无需每批重复全套。




## 每次执行追加记录

| Attempt | ID/命令/身份 | 预期 | 实际/退出码/pass-fail-skip | 证据 | issue/复测 |
| --- | --- | --- | --- | --- | --- |
| 未开始 | 未执行 | 按固定T-ID | NOT_RUN | 无 | 无 |

保留初次失败与修复后复测，不能覆盖日志。测试记录与CLOSE中的候选应一致；候选发生变化需核受影响集合并复测，不能套用旧通过数。


## 实际执行与结果（2026-11-10）
attempt-01：真实两模型×变化/固定4 passed22.67s；A实算正/零均留存，无B明确unavailable。
attempt-02：加入强制小上限测试profile生成独立A/B，共8 passed41.08s。profile仅测试注入，不是产品用户调参。
attempt-03：新状态/资源/候选+API共30 passed、8 failed80.49s。失败为严格JSON数组/tuple入口错误，详情ISSUES-I03。
attempt-04：API修复后两模型8 passed43.17s，报告GET、幂等、无自动full、篡改回退校验通过。
attempt-05：DeepSeek A/B及B硬退出故障注入+状态单元12 passed5.47s，A完整报告仍可读。
attempt-06：增加窗口完整性/守恒/收益状态校验后11 passed0.10s。
命令核心：pytest tests/integration/analysis/test_clock_replay_v3.py；unit/analysis_common/test_evaluation_v3.py；unit/prefix_analysis/test_candidates_v3.py；integration/analysis/test_execution_v3_resources.py。每次--basetemp分别指向artifacts/validation/development-v3/V3B005/attempt-NN/pytest，日志同目录。attempt03输出预检包含所有选中测试，新篡改负例只改自己的tmp_path新建行文件，未触及历史。
ruff通过、mypy140文件通过；新report schema SHA256 4ce3368c181c52b00753d89793342ae05ccbc097862bb564985532cf1447ba80，export_report_schema_v3.py可复验。HTTP弃用提示属于既有测试库，不影响结果。
T16同窗keys/order、P=H+C、逐行聚合及Fraction独立算术核对；T17 A冻结digest/B独立ledger与硬失败保留A；T18符号/无对象/无改动/取消/失败/预算/零分母/无B保真；T19无旧pilot/full调用，GET与幂等重复无新增任务。当前产品不提供full快捷路径，重新分析仍须显式新prepare且受限，不通过扩大预算伪造full。

## 2026-11-11 T19勘误
原记录只证明无自动full、GET/幂等不新增任务；显式full新范围/预算/prepare身份未实现也未测试，T19为部分验证，不能整体PASS。开发遗漏及两项底线影响见../../FULL_SCOPE_GAP.md。无用户延期决定，不删除原条款，原测试日志保留。

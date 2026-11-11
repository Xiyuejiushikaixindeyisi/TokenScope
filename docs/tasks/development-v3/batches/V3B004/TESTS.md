# V3B004 TESTS — 待执行

**全部NOT_RUN，无PASS数量、性能值或截图。** 依[总TESTS](../../TESTS.md)的固定断言，不得将本页写成独立降级门槛。关联[PLAN](PLAN.md)、[ISSUES](ISSUES.md)。

评审r1追加必需断言：正常诊断不预指定clock位置/recipe/finding，自动L1证据→改法→评估/展示（按本批职责）必须可追踪；同一可比system/developer字段clock外一致、后续历史长度/角色序列不同为正例，固定clock/不相关模板/字段不兼容为负例。手动反事实成功不替代自动门禁。见[修订核对](../../REVIEW_FIXES.md)。

## 用例映射

| 必需ID | fixture / 输入 | 最终测试node ID | 结果 | 日志/issue |
| --- | --- | --- | --- | --- |
| T13 | F01/F03/F04/F07/F09 | 实施时填写 | NOT_RUN | 尚无 |
| T14 | F01/F03/F04/F07/F09 | 实施时填写 | NOT_RUN | 尚无 |
| T15 | F01/F03/F04/F07/F09 | 实施时填写 | NOT_RUN | 尚无 |

新增测试建议（尚不存在；实际路径/函数必须实施后回填）：

- `tests/unit/prefix_analysis/test_candidates_v3.py`
- `tests/integration/analysis/test_candidate_coverage_v3.py`

受影响已有回归：

- `tests/unit/prefix_analysis/test_l2.py`
- `tests/unit/prefix_analysis/test_history.py`
- `tests/unit/prefix_analysis/test_recommendation_groups.py`
- `tests/integration/analysis/test_recommendation_member_coverage.py`
- `tests/integration/analysis/test_l2_replay.py`

## 环境与命令

源码/dirty、设计/schema/模型/encoder/profile/fixture/sample摘要、Python/依赖/OS硬限制、时间与cwd：**待填**。预算/profile在测试前固定；无资产不自动下载，缺环境记阻断，不能SKIP后报通过。

以下为实施完成后的命令草案，当前未执行；cwd为项目根。新增文件须先落实，实际执行保存确切命令。basetemp每次使用未存在的attempt路径，pytest可能清理指定临时目录，禁止复用已有证据路径。

```bash
.venv/bin/python -m pytest tests/unit/prefix_analysis/test_candidates_v3.py tests/integration/analysis/test_candidate_coverage_v3.py tests/unit/prefix_analysis/test_l2.py tests/unit/prefix_analysis/test_history.py tests/unit/prefix_analysis/test_recommendation_groups.py tests/integration/analysis/test_recommendation_member_coverage.py tests/integration/analysis/test_l2_replay.py --basetemp=artifacts/validation/development-v3/V3B004/attempt-01/pytest -q
```

质量检查按受影响Python模块执行ruff/mypy；总全量回归在B007，除新失败/新变化无需每批重复全套。




## 每次执行追加记录

| Attempt | ID/命令/身份 | 预期 | 实际/退出码/pass-fail-skip | 证据 | issue/复测 |
| --- | --- | --- | --- | --- | --- |
| 未开始 | 未执行 | 按固定T-ID | NOT_RUN | 无 | 无 |

保留初次失败与修复后复测，不能覆盖日志。测试记录与CLOSE中的候选应一致；候选发生变化需核受影响集合并复测，不能套用旧通过数。


## 实际验证
2026-11-10，独占attempt-01/02/03，测试写入预检见attempt-02/output-preflight.txt，仅tmp_path/测试inputs；未覆盖历史输出。
attempt-01：新候选单元3 passed 0.16s。
attempt-02：pytest tests/unit/prefix_analysis/test_candidates_v3.py tests/integration/analysis/test_clock_replay_v3.py tests/unit/prefix_analysis/test_session_clock_v3.py tests/integration/analysis/test_dynamic_replay.py tests/integration/analysis/test_recommendation_tool_identity.py --basetemp=artifacts/validation/development-v3/V3B004/attempt-02/pytest -q：27 passed 41.40s。
attempt-03：类型变量分离后候选+clock单元19 passed 0.17s；mypy137源码通过；ruff格式调整后通过。
T13固定oracle12比较包含L1/L2/L3，实际旧CandidateIndex宽桶同预算耗尽于前40条普通记录，限定此fixture的改善结论。T14物理对计费/ID读取去重、稳定顺序、1000×5×K3输出界通过。T15精确成员、未知历史pair独立、L4/L5和B禁读通过；未扫描完整性为false，下界不能外推整体。

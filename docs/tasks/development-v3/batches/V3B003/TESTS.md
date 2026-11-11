# V3B003 TESTS — 待执行

**IN_PROGRESS：attempt-01中test_session_clock_v3.py及test_dynamic.py共20 passed，0.15s；mypy136源码通过。测试前已检查无固定输出路径，basetemp为独立新建artifacts/validation/development-v3/V3B003/attempt-01/pytest。真实worker集成与完整T10–T12仍NOT_RUN，未关闭本批。** 依[总TESTS](../../TESTS.md)的固定断言，不得将本页写成独立降级门槛。关联[PLAN](PLAN.md)、[ISSUES](ISSUES.md)。

评审r1追加必需断言：正常诊断不预指定clock位置/recipe/finding，自动L1证据→改法→评估/展示（按本批职责）必须可追踪；同一可比system/developer字段clock外一致、后续历史长度/角色序列不同为正例，固定clock/不相关模板/字段不兼容为负例。手动反事实成功不替代自动门禁。见[修订核对](../../REVIEW_FIXES.md)。

## 用例映射

| 必需ID | fixture / 输入 | 最终测试node ID | 结果 | 日志/issue |
| --- | --- | --- | --- | --- |
| T10 | F01/F02/F07/F08 | 实施时填写 | NOT_RUN | 尚无 |
| T11 | F01/F02/F07/F08 | 实施时填写 | NOT_RUN | 尚无 |
| T12 | F01/F02/F07/F08 | 实施时填写 | NOT_RUN | 尚无 |

新增测试建议（尚不存在；实际路径/函数必须实施后回填）：

- `tests/unit/prefix_analysis/test_session_clock_v3.py`
- `tests/integration/analysis/test_clock_replay_v3.py`

受影响已有回归：

- `tests/unit/prefix_analysis/test_dynamic.py`
- `tests/unit/analysis_common/test_modifications.py`
- `tests/integration/analysis/test_dynamic_replay.py`
- `tests/integration/analysis/test_recommendation_tool_identity.py`

## 环境与命令

源码/dirty、设计/schema/模型/encoder/profile/fixture/sample摘要、Python/依赖/OS硬限制、时间与cwd：**待填**。预算/profile在测试前固定；无资产不自动下载，缺环境记阻断，不能SKIP后报通过。

以下为实施完成后的命令草案，当前未执行；cwd为项目根。新增文件须先落实，实际执行保存确切命令。basetemp每次使用未存在的attempt路径，pytest可能清理指定临时目录，禁止复用已有证据路径。

```bash
.venv/bin/python -m pytest tests/unit/prefix_analysis/test_session_clock_v3.py tests/integration/analysis/test_clock_replay_v3.py tests/unit/prefix_analysis/test_dynamic.py tests/unit/analysis_common/test_modifications.py tests/integration/analysis/test_dynamic_replay.py tests/integration/analysis/test_recommendation_tool_identity.py --basetemp=artifacts/validation/development-v3/V3B003/attempt-01/pytest -q
```

质量检查按受影响Python模块执行ruff/mypy；总全量回归在B007，除新失败/新变化无需每批重复全套。




## 每次执行追加记录

| Attempt | ID/命令/身份 | 预期 | 实际/退出码/pass-fail-skip | 证据 | issue/复测 |
| --- | --- | --- | --- | --- | --- |
| 未开始 | 未执行 | 按固定T-ID | NOT_RUN | 无 | 无 |

保留初次失败与修复后复测，不能覆盖日志。测试记录与CLOSE中的候选应一致；候选发生变化需核受影响集合并复测，不能套用旧通过数。


实际补充：attempt-02运行test_clock_replay_v3、test_session_clock_v3、test_dynamic、test_modifications、test_dynamic_replay、test_recommendation_tool_identity，33 passed/44.34s；attempt-03只运行新增单元文件16 passed/0.09s，补业务禁止断言。各命令均项目.venv python -m pytest，basetemp为对应新attempt/pytest；stdout/stderr保留同目录。ruff src tests通过，mypy136文件通过。集成用例test_normal_worker_automatically_discovers_and_encodes_clock分别覆盖两模型×变化/固定，共4例；修改与指针守卫复用test_modifications。T10–T12本批组件PASS；完整收益/浏览器不在本次结论内。

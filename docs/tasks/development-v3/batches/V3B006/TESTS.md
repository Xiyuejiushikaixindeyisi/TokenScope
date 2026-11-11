# V3B006 TESTS — 待执行

**全部NOT_RUN，无PASS数量、性能值或截图。** 依[总TESTS](../../TESTS.md)的固定断言，不得将本页写成独立降级门槛。关联[PLAN](PLAN.md)、[ISSUES](ISSUES.md)。

评审r1追加必需断言：正常诊断不预指定clock位置/recipe/finding，自动L1证据→改法→评估/展示（按本批职责）必须可追踪；同一可比system/developer字段clock外一致、后续历史长度/角色序列不同为正例，固定clock/不相关模板/字段不兼容为负例。手动反事实成功不替代自动门禁。见[修订核对](../../REVIEW_FIXES.md)。

## 用例映射

| 必需ID | fixture / 输入 | 最终测试node ID | 结果 | 日志/issue |
| --- | --- | --- | --- | --- |
| T20 | F09/F10/F11/F12 | 实施时填写 | NOT_RUN | 尚无 |
| T21 | F09/F10/F11/F12 | 实施时填写 | NOT_RUN | 尚无 |
| T22 | F09/F10/F11/F12 | 实施时填写 | NOT_RUN | 尚无 |
| T23 | F09/F10/F11/F12 | 实施时填写 | NOT_RUN | 尚无 |

新增测试建议（尚不存在；实际路径/函数必须实施后回填）：

- `apps/viewer/tests/unit/analysis-v3-contract.test.ts`
- `apps/viewer/tests/component/analysis-clock-v3.test.tsx`
- `apps/viewer/tests/browser/analysis-v3.spec.ts`
- `tests/integration/analysis/test_compatibility_v3.py`

受影响已有回归：

- `tests/integration/analysis/test_recommendation_frontend_reports.py`
- `tests/integration/analysis/test_recommendation_http.py`
- `tests/integration/analysis/test_diagnostic_http.py`
- `tests/integration/analysis/test_discovery_http.py`

## 环境与命令

源码/dirty、设计/schema/模型/encoder/profile/fixture/sample摘要、Python/依赖/OS硬限制、时间与cwd：**待填**。预算/profile在测试前固定；无资产不自动下载，缺环境记阻断，不能SKIP后报通过。

以下为实施完成后的命令草案，当前未执行；cwd为项目根。新增文件须先落实，实际执行保存确切命令。basetemp每次使用未存在的attempt路径，pytest可能清理指定临时目录，禁止复用已有证据路径。

```bash
.venv/bin/python -m pytest tests/integration/analysis/test_compatibility_v3.py tests/integration/analysis/test_recommendation_frontend_reports.py tests/integration/analysis/test_recommendation_http.py tests/integration/analysis/test_diagnostic_http.py tests/integration/analysis/test_discovery_http.py --basetemp=artifacts/validation/development-v3/V3B006/attempt-01/pytest -q
```

viewer另在apps/viewer运行 `npm run typecheck`、`npm run lint`、`npm test`、`npm run build`及选定浏览器用例。默认 `npm run test:browser` 是harness；真实E2E使用经核唯一候选URL及TOKENSCOPE_EXTERNAL_PREVIEW/TOKENSCOPE_TEST_BASE_URL，确切命令与新state/browser身份必须记入实际记录。




## 每次执行追加记录

| Attempt | ID/命令/身份 | 预期 | 实际/退出码/pass-fail-skip | 证据 | issue/复测 |
| --- | --- | --- | --- | --- | --- |
| 未开始 | 未执行 | 按固定T-ID | NOT_RUN | 无 | 无 |

保留初次失败与修复后复测，不能覆盖日志。测试记录与CLOSE中的候选应一致；候选发生变化需核受影响集合并复测，不能套用旧通过数。


## 实际验证
attempt01独占目录：真实B005产物转wire fixture，新增组件4 passed1.63s。覆盖正/零/预算未完成、exact pp/recipe/样本身份校验、浏览刷新无POST。fixtures仅合成，无现场数据。
attempt02：完整viewer单元/组件36文件343 passed10.69s；tsc、eslint通过，ruff/mypy140通过，新schema --check通过。构建输出显式独占attempt02/dist，不覆盖既有dist/历史证据。真实浏览器与后端统一端到端在B007执行。
新增API列表只读，分页100；来源目录沿用已有两类GET，并可按appid筛选。不触发分析；点击分析按钮才prepare→diagnose。旧Token/四入口/L4L5回归仍通过。状态原样显示，不受旧full过滤。

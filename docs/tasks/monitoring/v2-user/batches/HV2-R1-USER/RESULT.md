# HV2-R1-USER本线闭环

2026-11-03。R1-U1–U4实现及本线自测完成，候选2.1.0待总设计师独立验收/冻结。当前软件具备多模型目录、可追溯默认参数与自动参考计算；不是前端/现场完成，真实性能校准待完成。

最终不监听监控回归 **271 passed，151.66秒**；CSV/编码 **62 passed，46.09秒**；最终定点 **27 passed，17.49秒**。mypy12源文件、ruff通过。首轮270通过/1失败（旧接口数量断言）保留在TESTS/ISSUES及regression.xml，已修正并最终全回归通过。旧9操作请求体/响应契约逐项比对、旧2.0.0材料不变、合成8正反例/14操作与运行Schema一致。

## 精确交接范围
- 源码4文件：api/user.py新增router操作；user_monitoring/discovery_contracts.py、discovery.py、defaults.py新增。
- 测试3文件：test_user_discovery_defaults.py、test_user_trace_filter_audit.py新增；test_user_robustness.py只修接口数量断言并加强旧契约比对。
- 新契约docs/contracts/user-monitoring-v2/2.1.0目录；本线交接/ENTRY/此batch四文档与SHA清单；本线记忆及历史GIT_HANDOFF追加误读勘误。
- 不包含其他session源码或U004/U005既有文档追加；旧estimator/contracts/service/storage无本轮业务改动。未改共享app/CLI/锁/前端。
- 文档和源码具体SHA、历史冻结核对与XML摘要见VALIDATION_MANIFEST.json。此清单不含自身SHA，避免自引用；它是候选工作树身份，不是发布commit。

## 未决与下一责任方
总设计师独立复验/冻结→前端接入→协调唯一环境真实监听与新浏览器E2E。test_events.py有监听，未运行。622现场差异、TTFT真实准确性及大历史目录规模仍未证实，不以本线闭环掩盖。三模型τ由用户提供且显式未校准；参数W仍必填。

此前上下文恢复误读发生d55df94旧文档提交/push，已追加勘误，不reset/revert；本轮HV2源码/契约未提交。校正后未再提交push、改共享记忆、部署或打包。

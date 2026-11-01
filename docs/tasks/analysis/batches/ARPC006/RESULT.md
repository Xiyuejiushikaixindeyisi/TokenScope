# ARPC006 联合回归与实际交接

2026-10-31，公共维护方session 01a18be2-7112-7aa2-919b-5137d1f1b1ad。ARPC000–006本地实现闭环，身份arpc-local-1。Token私有实现由其本线维护，公共完成实际消费及应用装配，不代签前端验收/生产策略。

## 验证结果

- 公共/低命中/Token单元与集成：**293 passed / 292.14s**；新增推荐组预算及原提案预算停止位置检查 **2 passed / 7.74s**（其中1项新增、1项加强重跑，去重共294项分析测试）。所有实际计量沿已有GLM/DeepSeek/GLM Flash模型资产和监控算法，未用mock替代收益。
- 监控unit/integration：**254 passed / 121.42s**；MA单元：**46 passed / 58.97s**，监控兼容去重共300项。
- 公共、低命中及API共**42源码文件mypy通过**，本线源码/测试/Schema脚本ruff通过。修复projection类型/变量复用和一处测试import排序。
- 当前源码导出与internal/wire/public-views一致，正例4/反例5验证；旧analysis-common-1.0、diagnostics-http-1、diagnostics-discovery-1三manifest共**13文件摘要不变**。
- 首次扩大回归292通过/1失败：旧取消测试替身仅接受位置参数，新service传入automatic_combinations关键字，测试提前TypeError而未实际取消；将替身改为接收kwargs后完整重跑293通过。生产两阶段取消检查点保留，另有adapter期间取消无报告测试。失败日志保留，不掩盖历史。
- 既有Starlette/httpx弃用warning，未改依赖版本。

## 关键边界与修复

| 场景 | 实际覆盖/处理 |
| --- | --- |
| 归组与门槛 | 30条Finding/6请求按recipe去重；不同规则/依据/上下文不误合。低命中full严格>1pp；L4/L5独立；完整修改数N非样例数 |
| 定位与展示 | raw/decoded码点、重复key/重复文本、大整数、转义/emoji、内嵌JSON、64k文本；最多3例，无法定位明确reason |
| 自动链 | 真Token适配器T2/T4及三模型T3引用/删除；无Finding的Observation合法；原appid全scope，原请求不写回 |
| 复用 | 每依据先prepare/guard；不同依据相同规范化操作复用一次Evaluation，prepared/execution Plan分开；不自动拼组合 |
| 收益 | noop N=0；完整零/负收益仍available；P1026→1022而C642→766不能称整体优化；缺依据N/metrics=null |
| 预算 | inclusive/exceed单元；提案扫描partial不缩scope；组数超限保留已完成并计not_run；Plan预算失败不写悬空ref；证据预算失败保留已完成评估但任务partial |
| 失败与发布 | 取消/重启/源损坏/guard/评估失败/封存异常沿原机制；partial不覆盖默认；两方向整体发布；summary给coverage及stop_location |
| 兼容与只读 | 同key/retry配置固定；当前T1禁用、旧T1读取；legacy not_computed；实例/分页/引用隔离；GET禁止propose/prepare/submit/编码仍成功 |

## 复现与资源

在项目根目录使用本地.venv，以下命令是实际执行命令；重跑请换全新basetemp以免清掉前端验收数据：

```bash
.venv/bin/pytest tests/unit/analysis_common tests/unit/prefix_analysis tests/unit/token_content tests/integration/analysis tests/integration/token_content --basetemp=artifacts/validation/arpc-final-20261031-02 -q
.venv/bin/pytest tests/integration/analysis/test_recommendation_engine.py::test_group_budget_keeps_full_scope_and_records_unrun_group tests/integration/analysis/test_recommendation_engine.py::test_budget_partial_and_snapshot_idempotency --basetemp=artifacts/validation/arpc-boundary-20261031-01 -q
.venv/bin/pytest tests/unit/monitoring tests/integration/monitoring --basetemp=artifacts/validation/arpc-monitor-20261031-01 -q
.venv/bin/pytest tests/unit/ma --basetemp=artifacts/validation/arpc-ma-20261031-01 -q
```

日志在artifacts/validation/arpc-logs-20261031：analysis-recheck.txt、boundary-tests.txt、monitor-tests.txt、ma-tests.txt；首次失败为analysis-tests.txt。/usr/bin/time -v记录分析整套wall=4:52.64、峰值RSS=1,667,784 KiB；监控wall=2:02.03、RSS=992,924 KiB。分析与监控有并行时间，因此耗时仅本开发机套件测量；RSS含多个模型缓存，不等于单请求或生产SLA。规模回归包含既有16/64请求档位，不宣称15万请求已校准。

新增预算是确定性工作量限制而非RSS硬限制。低命中检测/实验仍使用原RuntimeOptions；推荐发布阶段核算其已保存Plan。Token新链在prepare/evaluate前分别消耗新预算，不能把事后低命中发布核算描述成阻止此前计算。默认256提案不保证覆盖大appid，应显式扩预算并重新提交，不能缩窗伪装全量。

## 交接与限制

[实际前端交接/启动prompt](../../../prefix-analysis/FRONTEND_REWORK_IMPLEMENTATION_HANDOFF_ARL3.md) · [最终身份](../../../prefix-analysis/FRONTEND_REWORK_IMPLEMENTATION_IDENTITY_ARL3.json) · [实际HTTP样例](../../../prefix-analysis/FRONTEND_REWORK_IMPLEMENTATION_EXAMPLES_ARL3.json)。样例为8组持久状态/11份报告，由create_app(start_worker=False)实际GET读取；含完整scope/模型资产/编码配置/Plan/Evaluation/局部证据。原始状态不入Git。

Token提供方[ARTA004](../../../length-analysis/batches/ARTA004/RESULT.md)记录163项本线验证，公共本次另以当前源码执行联合消费；两方验证不把测试数量相加重复记。配置DSL以[AUTO_ADAPTER_HANDOFF](../../../length-analysis/AUTO_ADAPTER_HANDOFF.md)为准。真实业务保留策略/引用协议尚未配置，构造策略验证工程正确性，不证明内容质量或生产收益。正式前端浏览器验收由前端会话完成。未打包、部署、修改正式前端或执行Git发布。

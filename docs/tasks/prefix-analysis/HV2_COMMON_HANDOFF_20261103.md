# HV2-R1-COMMON 公共层交接

2026-11-03；候选 `hv2-common-local-1`，**实现与本线验证完成：全套331项通过、最终v2专项23项通过；待总设计师独立验收**。实际session：`01a18be2-7112-7aa2-919b-5137d1f1b1ad`（环境THREAD/SESSION一致）。角色：低命中/异常公共层唯一维护方。本阶段仅公共层及必要低命中调用适配；公共层通过前不进入私有第二阶段。

[P0派发](../../../prompts/sessions/hv2-repair-20261103/COMMON.md) · [执行板](../delivery/HV2_REPAIR_EXECUTION_20261103.md) · [候选契约](../../contracts/diagnostics-execution-2/README.md) · [Token准备与依赖](../length-analysis/HV2_TOKEN_PREP_20261103.md)。本文件是维护方交接，不代签总设计师独立验收或前端接收。

## 证据校正与范围

两现场原件SHA已核实：验收93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e；调查51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83。原件保持。L4只是差异观察，无最终DOM现场证据；空recipe与fragment覆盖不足分开。旧Token逐请求已使用独立RunControl，没有消费TaskControl.findings，**不宣称findings预算直接污染Token fragment**。本轮合成测试分别复现低命中保留停止和Token请求内预算不足，不冒称现场数据复现。

原arpc-local-3/RV1复审及arpc-local-4结果属于历史。本轮以HV2派发基线7cbe28621f4e46083bf47f9aa14b011b3cb250c4叠加当前维护源码验证，旧通过结论不覆盖此候选。恢复上下文时曾短暂误读历史任务，仅只读检查，收到总设计师校正后恢复本任务；未回滚、改写历史或提交。

## proposed → implemented

| 要求 | 已实现入口与行为 | 测试/限制 |
| --- | --- | --- |
| 显式方向 | execution_v2.SelectionV2、RequestV2、RuntimeV2；POST /diagnostics/v2/tasks；至少一个方向，原因不强制另一方向。service提交/调度/扩展/重试依选择；禁用Token不读取plugin/adapter/业务recipe | 三种选择、全false拒绝；失败哨兵检查禁用调用；幂等冲突、重启interrupted和retry保持选择。旧v1校验不变 |
| 发现与保留分离 | runtime_control.TaskControl；低命中L1–L5按规则固定保留配额和字节配额，满后继续扫描计数；L2/dynamics比较预算分开，启用方向编码预算独立 | 10000次L4仍保留L1/L5；实际6请求全遍历但保留截断；比较限1仍partial而Token完成6请求。不是RSS上限承诺 |
| partial可发现 | discovery_v2：version=diagnostics-discovery-2，selected_reports选择每binding×direction最近ready；无ready才published partial fallback | snapshot、分页、实例变更、重启、方向分离；empty/failed/legacy/评估排除。旧defaults和default_eligible不变 |
| 状态原因分离 | 空bundle不进入Token提案扫描，eligible=checked=0代表无配置任务；缺basis仍advice；fragment不完整/保留不足/插件异常分别原因 | 空/非空recipe配max_units=1；插件失败不冒称TOKEN_FRAGMENT_INCOMPLETE；只保留不足仍记录真实fragment完整性 |
| 实测计量 | telemetry、source_observation；perf_counter_ns包实际读取/解析/检测/保留/提案评估阶段；新增execution GET与机器Schema | 正整数纳秒、十进制字符串计数；不泄露正文；嵌套耗时不可相加，重复读取数非唯一请求数 |
| 读旧与契约 | v2附加新路由，旧wire/contracts/runtime/discovery/diagnostics源字节及旧冻结文件保持；实际create_app装配 | 旧报告not_computed；GET封禁计算且state所有文件SHA不变；新Schema及实际HTTP样例可反解析 |

低命中私有改动仅 `prefix_analysis/service.py`、`detection.py`：原Finding构造后传rule_id及实际序列化payload字节给retain_finding；候选截断增加显式原因。没有改日期/路径/cch/工具/历史识别规则、修改recipe、pilot/full、>1pp门槛、L4/L5语义。旧TaskControl调用仍用原finding上限语义。

## 新接口与Token交接

候选新目录 `docs/contracts/diagnostics-execution-2`，包含README、wire.json、实际TestClient examples.json与manifest.json（实际SHA已核对）。接口细节、全部新增预算字段、计量语义和partial选择见README。Token私有插件四方法、AnalysisFragment、RunControl、策略DSL均未改；不需要先改Token源码才能消费。每请求原预算仍由Token管理，公共新增是方向控制与保留策略。

Token后续需要核对：低命中禁用Token零调用；空recipe无提案扫描但内容检测可执行；checked_requests不代表各规则完整；rule_status_counts保留插件原状态；fragments_complete=false不能单凭该布尔归因预算，需reason_codes与rule状态；FRAGMENT_RETENTION_TRUNCATED不等于内部片段不完整。未配置推荐不补造收益。公开stage与telemetry不含raw/内部策略。

禁用方向不创建分析stage；selected_directions明确实际启用。无recipe proposal_coverage complete=true/eligible=0/checked=0仅说明无配置提案工作，evaluation_coverage=null；不表示原appid全部已做修改评估。真实candidate/comparison截断、保留截断仍partial；完整pilot/full收益门槛保持。

shared `src/tokenscope/api/app.py` 的import及include两行由**总设计师**修改，本线未写该文件。实际TestClient直接调用create_app，无手工重复include，测试检查唯一提交路由。CLI/锁/前端/Token私有/监控源码均不在本线修改清单；依赖的其他线并发源码不被本交接代签。

## 已执行测试与中间失败

证据根：`artifacts/reviews/hv2-repair-20261103/`。均本地合成fixture、真实Tokenizer与TestClient，无监听服务或E2E，无依赖升级。

- 初轮旧回归144 passed/2 failed：旧冻结断言校验源SHA，新增功能随后移到v2模块，恢复runtime.py/discovery.py/diagnostics.py原字节；未删除断言或回写manifest。原两项冻结复核2 passed。
- `common-full-second.log`：320 passed/6 failed，410.40s。进程已加载修复前源码，六失败均legacy TaskControl缺telemetry；增加类型保护后公共/低命中unit109 passed，见common-unit-fixed.log，不把此结果当最终全套。
- 新HTTP验证先发现冻结wire codec不转换additionalProperties的十进制map，采用新模型DecimalCount字符串约束，未改旧wire；随后新测试的FastAPI扁平路由假设失败，修为递归检查嵌套router，保持唯一性断言。
- `common-v2-check3.log`：9 passed/46.74s。
- `common-v2-check4.log`：20 passed/56.14s，新增两项目录/数值正反例及两项HTTP/故障边界；各组有重跑，不累加唯一总数。
- `common-contract-check.log`：10 passed/0.40s，新增源码Schema与真实HTTP样例一致性测试。
- `common-mypy-final.log`：46源码mypy通过；`common-ruff-final.log`：公共/低命中/API与对应测试ruff通过。新增契约测试格式/导入检查另已通过。
- `common-final-suite.log`：331 passed/436.92s，退出0；覆盖公共、低命中、Token单元/集成。common-final-start/end.json完全一致；命令/退出码/wall437.67s见common-final-run.json。
- 全套之后唯一源码修正：diagnostics_v2.execution.status改为已发布任务receipt.status，处理旧report正文ready而终态empty的边界，不改旧报告。新增真实空appid任务及禁用Token时缺失recipe文件测试；`common-terminal-final.log`最终23 passed/60.03s，含全部v2单元/集成和这两项新例；不与上述331相加。最后46源码mypy及完整本线ruff再次通过，见common-mypy-terminal.log、common-ruff-terminal.log。仅保留已知Starlette/httpx弃用warning，未升级依赖。

## 复验步骤与验收边界

WSL项目根目录，已有.venv；下列basetemp必须全新，已存在就改后缀，不能清理旧证据：

```bash
.venv/bin/pytest tests/unit/analysis_common tests/unit/prefix_analysis tests/integration/analysis tests/unit/token_content tests/integration/token_content --basetemp=artifacts/reviews/hv2-common-independent-NEW -q
.venv/bin/mypy src/tokenscope/analysis_common src/tokenscope/prefix_analysis src/tokenscope/api/diagnostics_v2.py
.venv/bin/ruff check src/tokenscope/analysis_common src/tokenscope/prefix_analysis src/tokenscope/api/diagnostics_v2.py tests/unit/analysis_common tests/unit/prefix_analysis tests/integration/analysis
```

验收重点：新增direction/coverage/retention/fallback四维不可相互冒充；无recipe、无basis、fragment不完整和预算耗尽分别核查；新端点Schema、十进制map、旧报告和只读副作用；保持旧冻结摘要和>1pp/L4/L5。共享路由已装配，但正式前端未接新接口，不声称页面空结果已现场闭环。

明确限制：本轮未做15万请求/32GiB容器容量或现场性能校准；保留payload上限不保证Python峰值RSS，候选索引和单请求解析仍有原独立预算。低命中applicable_pairs仍null并显式not_separately_classified_by_detector，公共不猜私有适用对数。嵌套耗时不可相加；source读计数包含重读。ready优先可能继续显示旧完整结果，消费者应展示selected_reports实际task与状态，不把新partial伪装默认。无生产策略/质量/真实收益/TTFT结论。

完成后等待总设计师公共第一关独立验收；不进入低命中私有第二阶段或前端、不修改共享CURRENT/SESSIONS/执行板、不commit/push、打包或部署。

## 最终身份与实际交付

本线14份源码/测试精确清单及逐文件SHA、3份新契约文件SHA、8份最终测试证据SHA见[manifest](../../contracts/diagnostics-execution-2/manifest.json)。共享app.py另列designer_owned_dependencies，不归本线修改。common-handoff-identity.json保存交接时完整被测依赖身份；相对331全套结束，**仅diagnostics_v2.py与本线v2集成测试**有上述empty投影修正/补例，已由23项专项和类型/静态验证。公共核心、低命中和Token私有源码均无全套后漂移。

新增模块：execution_v2、runtime_control、telemetry、source_observation、discovery_v2、api/diagnostics_v2。修改公共：service、recommendation_runtime、recommendation_pipeline、recommendation_engine。必要低命中适配：prefix_analysis/service、detection。新增测试：unit/analysis_common/test_execution_v2.py、integration/analysis/test_execution_v2_integration.py。文档：本交接、同目录ENTRY、本线memory及新契约目录。未改旧冻结文件、Token私有、正式前端或共享总记忆。

27项受保护旧契约/兼容源码逐一与派发基线一致，见common-frozen-verification.json。真实样例为完整create_app/TestClient响应，经from_wire和导出Schema一致性验证；示例没有真实业务正文或私有配置。前端与Token需等总设计师通过后按本候选明确接收，当前不冒称已签收。

维护方本阶段完成，无已知未修复测试失败；进入等待公共层独立验收。未打包、部署、Git提交/push或监听新服务。测试中的中间失败与历史arpc/RV1证据全部保留。

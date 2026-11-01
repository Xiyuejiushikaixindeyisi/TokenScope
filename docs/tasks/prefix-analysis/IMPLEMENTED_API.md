# 异常分析公共后端与低命中实际接口

FE-N1扩展：独立 `/diagnostics/discovery/capabilities`、`/catalog`、`/events`、`/tasks/{task_id}/terminal`，版本diagnostics-discovery-1；详见[接入交接](NOTIFICATION_HANDOFF.md)。现有路由、TaskReceipt与EvaluationResult不变；新前端不轮询，旧报告历史时间null。

2026-10-31自审补充（low-hit-backend-local-2）：experiment 增加 `pilot_scope`、`reason_codes`、`confidence_basis`，保留完整小范围边界/请求摘要及未执行原因。`pilot_gain_gt_1pp` 仅代表小范围已通过，全范围是否展示仍使用 `display_eligible`。全范围 Plan 超预算保存已完成的 pilot；后续编码预算耗尽的实验记 `not_run`。低命中及 Token 均按完整序列化 Plan 计算字节预算。冻结公共/HTTP 请求契约不变。详见 [完整自审](SELF_REVIEW_20261031.md)。

2026-10-31，本地实现；HTTP diagnostics-http-1，公共analysis-common-1.0，运行选项diagnostics-runtime-1。Token规则与授权适配由Token会话维护。现场、前端、容器与部署未验证。入口和验收状态见ENTRY、batches/LH000–LH009/RESULT.md。

## 手动提交

GET /diagnostics/capabilities返回服务实际instance和请求Schema。下表除capabilities外均需Header `x-tokenscope-service-instance`，错实例409，缺头422。支持base或已发布user_v2来源，指定appid及可选半开时间窗；不接MA请求库。user_v2可锁索引revision。源码MonitoringService/SourceResolver校验源与模型资产身份。

POST /diagnostics/tasks提交`{request,options}`。request是DiagnosticRequest；options是显式RuntimeOptions。只有low_hit原因时enable_low_hit/enable_token_content均true；仅request_length/qps时false/true，矛盾422。reason_note是人工背景，32k/70%不作自动阈值。没有监控outbox/告警/自动采集触发。

Wire示例的source中base_run_id须换成已有封存run；完整options按capabilities Schema显式填写，测试可用tests/integration/analysis/test_diagnostic_tasks.py的options()或[资源配置](RESOURCE_PROFILE.md)，不可把省略项当默认业务策略：

```json
{"source":{"source_kind":"base","base_run_id":"已有run","appid":"目标appid"},"selection":{"reason_codes":["low_hit"],"enable_low_hit":true,"enable_token_content":true},"submission_key":"业务自定幂等键","reason_note":"人工发现理想命中率偏低"}
```

上例仅request部分；source可省略的可空字段由Schema默认补齐。数字输入如candidate_limit必须是`"2"`，不是JSON数字2。返回202 TaskReceipt，task_id及attempt；同键同意图返回原任务，异意图409。source解析/封存核验属于提交验证，不触发监控重采集或诊断探测。

## 路由

| 方法/后缀（统一前缀/diagnostics） | 内容 |
| --- | --- |
| GET /capabilities | 实例/版本及请求Schema |
| POST /tasks | 排队分析 |
| GET /tasks/{task_id} | queued/running/ready/partial/empty/failed/interrupted及当前方向 |
| GET /tasks/{task_id}/report | 冻结scope、两阶段顺序与覆盖、预算、实际编码次数 |
| GET /tasks/{task_id}/items/{kind} | offset>=0、limit 1–100分页，{items:[{id,data}],offset} |
| GET /tasks/{task_id}/items/{kind}/{key} | 单个已存成员；无成员404 |
| GET /tasks/{task_id}/comparisons/{finding_id} | 两份完整原始请求JSON字符串、两端身份/摘要/差异位置 |
| GET /tasks/{task_id}/requests/{fragment_id} | Token成员完整原文，含scope、RequestKey、raw_sha256、complete及capture_truncation |
| GET /tasks/{task_id}/evaluations/{evaluation_id}/rows | 完整评估逐请求实际指标/IDs摘要/具体变换/修改raw；不完整评估409 |
| POST /tasks/{task_id}/cancel | 协作取消；在请求/阶段/编码边界响应 |
| POST /tasks/{task_id}/retry | 新submission_key，新任务和attempt，原报告保留 |
| POST /tasks/{task_id}/low-hit-evaluations | 显式指定1–2个finding_ids，直接全范围；不冒充pilot通过 |
| POST /tasks/{task_id}/token-evaluations | 已存fragment_id/candidate_id、parameters_json、business_basis_ref、submission_key |
| POST /tasks/{task_id}/token-authorizations | 已存T3观察/单元、注册handler/version、完整参数/业务依据，生成并保存授权候选后评估 |
| POST /tasks/{task_id}/combination-evaluations | 2–8个已存{task_id,plan_id}引用；必须同原scope、不能用pilot Plan冒充full |

kind包括finding、fragment、fragment_index、rule_coverage、plan、evaluation、optimization、experiment、authorization。fragment_index按fragment中数组顺序给location_ids/unit_ids/observation_ids，不改冻结fragment模型。分页不会静默限缩正文。GET只读已封存文件及原始证据、核验摘要，不探测/编码/修改/补算。

## L1–L5实际范围

- L1：system/developer内容中的可对比时间/路径片段及已知billing cch整行。字符串静态形状一致、槽位实际变化后生成明确删除副本；已知cch为信息保持，其它为删除假设。不是从字段名字推断任意业务信息无用；业务自行决定采纳。
- L2：同一唯一function工具身份及完整定义集合，只有排列不同；按工具身份稳定排序，不重排messages/tool_calls。重复身份/不支持类型不生成排序方案。
- L3：工具集合/定义真实差异与描述字段动态路径/时间；动态片段可删除评估，保留name/Schema结构。增删集合只给事实，不以最常见版本覆盖其它版本。当前动态识别限已实现语法，不声称覆盖所有随机ID/业务元数据。
- L4：已有消息位置差异与消失，正常后缀追加排除；现有输入没有可靠session，统一needs_association，不认定同会话历史改写。
- L5：工具结果内嵌JSON结构相同但表示不同，保留数组顺序、数值词法及类型；重复key/非有限值等不当作等价，实际IDs相同不报缓存影响。无自动修改收益承诺。

工程上L2先构建候选，动态/历史通道再运行；所有适用规则都查，不首命中停止。索引只召回前序候选；有界召回不是全对比或同session证明，truncated/预算停止如实partial。L4/L5及Token事实独立于优化门槛。

## 评估与展示

自动低命中：连续pilot（同时间点整体纳入，预算无法容纳则sample_insufficient），两侧独立空账本；完整pilot精确ΔR>1pp才编译同transformation_digest的完整F。F只含目标appid选定范围全部有效请求，含未修改后继。只有完整full/direct_full的ΔR>1pp进入optimization；未达标保留evaluation/experiment。显式direct_full标pilot_bypassed_by_explicit_request，不写成小范围高置信度。

evaluation核心是冻结EvaluationResult，加四个明确派生字段：gate_passed、display_eligible、gain_percentage_points的精确分子/分母、compute_tokens_delta。P/H/C/J/N及修改子集均保留；R上升C也可能上升，不能只凭R说成本降低。Token或含Token组合不套门槛。两阶段单项/组合各自回放，绝不相加收益。

Plan含实际受保护变换/原值guard/目标原文摘要/版本/业务依据。单个目标guard、协议、数值词法或组合重叠冲突失败，无after且不丢行。内嵌多目标由Token处理器编译同外层一次替换；不同已存Plan对同外层产生冲突时拒绝，不擅自合并。源请求从不写回。

完整两请求示例读取实际比较端点；低命中单条卡片通过evaluation.plan_id→plan.finding_refs→finding.comparison追溯。Token多位置重复可发生同一请求，展示该完整请求与多个Location，不虚构第二请求。evaluation rows中的after_raw为实际实验副本，原文从来源引用独立读取。

## 生命周期、限制与回退

公共源失败/完整性错误阻断任务；方向局部失败可保留已完成项并继续Token；未提供插件/预算不足显式partial。底层源/请求硬预算失败未启动阶段时任务failed且无报告。空范围empty。worker重启将未完成running改interrupted，显式retry，不把私有半成品提升为报告。文件封存与发布采用fsync/rename/事务；GET发现摘要变化拒绝，不自动修复。

复用同一MonitoringService CPU预算、统一Tokenizer/Template/make_strategy和worker.lock；app与work-once只增加Dispatcher注册，不改监控计量。当前messages兼容协议；原生Responses、Loop/过程推断、线上改写、前端与打包部署均不包含。捕获截断仍可unknown，完整保存不等于上游采集完整。

回退：撤销app/cli中的diagnostics注册和新路由即可禁用新任务入口；保留独立state/diagnostics与监控源，旧监控库无迁移。冻结analysis-common-1.0保持。私有孤儿产物无自动清理，当前没有华为吞吐承诺，资源证据见RESOURCE_PROFILE。

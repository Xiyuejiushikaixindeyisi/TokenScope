# 用户监控后端已实现API

本机开发身份u005-local-1；契约1.0.1，控制schema1/索引算法user-index-1；见[最终验收](batches/U005/RESULT.md)。使用统一服务地址，前缀/monitoring/user-v2，全部请求必须携带当前服务的X-TokenScope-Instance-Id（非MA UUID），不符409；缓存no-store。没有新增第二监听端口或部署。

| 方法/路径（前缀后） | 输入→输出 | 说明 |
| --- | --- | --- |
| POST /runs | Submit→Receipt 202 | GB单CSV绑定common_name/model_id；先保存意图 |
| POST /bindings | Bind→Receipt 202 | 历史基础run显式绑定，不接受MA任务或已被用户提交预留的base |
| GET /runs/{user_run_id} | Receipt | accepted/base_pending/indexing/ready/empty/failed/interrupted |
| GET /runs/{user_run_id}/rankings | Ranking | 四指标、AND上下界、字面appid_contains、width1000/2000/5000 |
| GET /runs/{user_run_id}/modes | Modes | appid必需，全部并列峰按lower分页 |
| POST /scenarios | Scenario→Scenario 201 | (id,revision)不可变；人工假设/实测来源分开 |
| GET /scenarios/{scenario_id}/{revision} | Scenario | 固定版本只读 |
| POST /evaluations | EvaluationRequest→Evaluation 201 | 幂等保存输入/情景/结果，轻量公式不回放 |
| GET /evaluations/{evaluation_id} | Evaluation | 旧快照只读，不受情景新revision影响 |

Schema、设计OpenAPI及合成例见[契约](../../../contracts/user-monitoring-v2/README.md)。实际运行OpenAPI由服务生成；真实合成CSV响应例见runtime.examples.json，不是现场样本。

排序默认request_count desc；四字段为request_count、ideal_hit_rate、total_ideal_compute_tokens、typical_ideal_compute_tokens。同值appid UTF8升序，NULL末尾。计数/总量范围整数，比率/典型值范围允许精确小数；负值、NaN、倒置区间拒绝。offset规范非负整数字符串，limit1–1000；offset>0必须提供index_revision；不一致409。%/_按字面搜索。模式箱为C=P−H，典型值为最低并列众数箱内均值，返回所有峰的分页入口。

GB结果是appid×common_name有效子集服务级理想潜力。file_quality为整文件，不虚构坏行组归属。TTFT主标签应使用“P90长度请求所需参考前缀命中率”，不与总体ΣH/ΣP比较输出达标；返回人工假设/适用限制、无预算/范围外/空组状态，100%参考可行性未知。

维护：UserRunService.rebuild(user_run_id)显式将已知任务重排索引；读取不会修复。work-once和HTTP worker均统一Dispatcher调度，持同state_root/worker.lock。短暂I/O错误保留任务重试并标STORAGE_UNAVAILABLE；永久缺facts为failed/REANALYSIS_REQUIRED，需要新分析。索引/tmp可重建，源封存与用户control/evaluations不可随意删除。

源导航：user_monitoring/{contracts,storage,service,projection,ranking,estimator}.py；api/user.py；api/app.py和cli.py仅装配。旧S0/MA namespace保持分离。无前端或现场验收声明。

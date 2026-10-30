# 用户监控扩展契约 1.0.1

9个操作已实现并本地验证，见[实际API](../../tasks/monitoring/v2-user/IMPLEMENTED_API.md)；schema.json和design.openapi.json为可机读约定，设计OpenAPI仍保留设计身份，实际运行OpenAPI带x-runtime-implemented=true。examples.json为合成算例，runtime.examples.json为本地真HTTP合成CSV响应；均非现场证据。

1.0.1勘误：数值文本最长128字符，普通非空文本最长4096字符；计数/Token总量筛选只接受整数（与原文字口径一致）；错误码、后续分页revision要求和运行身份头对齐。字段集合、公式和统计口径不变。

## 身份与生命周期

前缀/monitoring/user-v2；全部请求匹配X-TokenScope-Instance-Id，缺失/不符409 INSTANCE_MISMATCH。它是服务身份，不是业务MA UUID。user_run_id与base_run_id、MA运行互不替换。

同submission_key同内容返回同一回执，异体409。先在用户control持久accepted意图，再以uv2.<user_run_id>作为合法稳定基础submission_key；重试先查基础回执，不因源CSV移除重复创建任务。显式历史绑定不能抢占已被用户意图预留的基础运行。

accepted→base_pending→indexing→ready；全无效为empty；failed/interrupted带原因。ready必有base_run_id/index_revision。I/O短暂失败保留可重试状态并报告STORAGE_UNAVAILABLE；永久源缺facts为failed/REANALYSIS_REQUIRED。

索引只读原封存facts，源manifest摘要绑定原配置/资产；独立SQLite稀疏箱及metadata经tmp/fsync/rename后控制事务发布。未发布孤儿一律从核验源重建，不信任残存文件名、不接续缓存状态。GET不构建/恢复；索引摘要不符409，缺失503。原seal不修改。

## 精确数值、筛选与分页

计数/Token/offset/total使用非负规范十进制字符串；秒和均值/比率筛选允许规范非负十进制，不接受指数、NaN、Inf；ratio有限数0–1；均值另带精确sum/count。拒绝未声明字段。

四指标request_count、ideal_hit_rate、total_ideal_compute_tokens、typical_ideal_compute_tokens；范围包含端点并AND组合，min≤max，比率≤1。appid_contains区分大小写，%/_按字面。默认request_count desc，同值appid UTF8升序，NULL最后且不满足范围。

固定一个user_run/common_name/index_revision，先全候选筛选排序后分页；offset≤2^63−1、limit1–1000。第一页可不传revision；offset>0必须携带，缺失/不同409 INDEX_REVISION_CONFLICT。无结果total=0/rows=[]/next_offset=null。众数明细按lower升序分页，保留全部并列峰，代表取最低箱。

## 情景与评估

(scenario_id,revision)不可变；同内容可重复登记，不同内容409。实测来源要求摘要/正样本数，不能由这些字段推断系统验证过证据；人工假设明确user_assumption。首版无自动有效期失效，操作者选择确切revision并确认部署/负载/思考模式/计时边界。

T>0、W/O≥0、K/τ>0；τ不提供即拒绝。模型/服务须一致，P90超长度范围out_of_scope，无有效正P90 unavailable，预算不足no_budget；不伪造0。n=0返回100%参考并明确可行性未知。公式详设计第5节，不做总体命中率达标判断。

POST /evaluations持久输入/情景/结果快照；同键幂等、异体409。GET只读，无正文/编码/回放。旧估算不因新情景revision或后来源文件移除而改写。

## 错误及存储

404 RESOURCE_NOT_FOUND；409 INSTANCE_MISMATCH、SUBMISSION_KEY_CONFLICT、RESULT_NOT_READY、INDEX_REVISION_CONFLICT、SCENARIO_CONFLICT、RESULT_SEAL_INVALID；422 INVALID_ARGUMENT、MODEL_MISMATCH、SERVICE_BINDING_CONFLICT；503 STORAGE_UNAVAILABLE、INDEX_NOT_READY。error.code/message不回显正文或任意输入。

user_monitoring/control.sqlite3 schema1实际表runs/scenarios/evaluations；runs含绑定意图/基础引用/发布revision。独立<user_run_id>.sqlite3含groups/bins/metadata。V1 control3和MA库不迁移。未来迁移先备份/校验，未知schema拒绝；保留控制库和源封存，派生索引可显式rebuild。

公共parse_utc(value, *, source_timezone='UTC', field='model_handle_start_time')保持旧位置签名；新用户router位于api/user.py，通过Dispatcher.register注册持worker.lock的UserRunService。内网监听不属于该API契约，也未在本轮开放。

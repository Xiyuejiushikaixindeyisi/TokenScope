# 监控展示服务契约 v0.1（B005.1 草案）

2026-10-27，**proposal / 未实现 / 待评审**。维护：Token监控；消费：前端。按用户新增范围提出确定的候选协议，供实施前核对；不改写已批准的[计量契约](MONITORING_V1.md)。当前运行接口仍见[实现说明](MONITORING_IMPLEMENTED_API.md)。内部组件/事务/迁移见[B005.1 DESIGN](../tasks/monitoring/batches/B005.1/DESIGN.md)。

## 1. 通用规则与兼容

- 新视图协议 view_schema_version="1"，控制库拟schema3，代码拟dev6；三者独立。当前代码仍dev5/schema2，不先更新实际OpenAPI。
- 所有新的展示响应带service_instance_id、view_schema_version；固定结果带run_id/model_id/appid。身份来自持久控制库，正常重启保持；全新状态目录是新身份。复制成独立服务或恢复导致序号回退时须新实例身份，不能复用同名浏览器缓存。
- 表示请求数/Token数/分位值/直方图计数及边界/rank/ref索引/seq/revision/total/offset的整数，**在新展示DTO中始终是十进制字符串**，即使值很小也不切类型；有符号delta允许负号。ratio/share为有限number或null。bin_width为1000/2000/5000的number枚举，limit为1..1000的number；schema号/ID为字符串。0和null不同，尾桶upper=null。
- 冻结settings/rules按schema声明处理整数，包括规则整数阈值；数值附value_kind="integer"或"ratio"以区分。不得只转换大于2^53的值造成类型漂移。整数累计在Python/SQL边界保持精确；前端用十进制字符串/BigInt表示，不先经过Number。
- 旧API默认形状和旧CLI保持兼容，不把其numeric字段悄悄换字符串。新UI统计/信号/详情及设置/规则编辑走本草案的新适配协议；大整数阈值和revision通过十进制字符串无损写入后转换成原业务类型，禁止JS先舍入后提交。
- 新 GET 不做编码/仿真/统计/详细归因/迁移。未发布409 RESULT_NOT_READY；未知run/appid/ref404；未完成迁移503 VIEW_INDEX_NOT_READY。不返回部分200伪装成功。
- 错误沿用 `{"error":{"code":"...","message":"..."}}`，可以增加无敏感值的可选details；不得回显原JSON、绝对路径或完整用户输入。所有结果范围都是数据筛选，不宣称RBAC。
- URL中的appid/hash通过query编码；不得把它们拼为文件路径。时间UTC RFC3339固定9位小数，前端转Asia/Shanghai。原请求中的时间字符串只作追溯，排序按已存time_ns。

## 2. 完整目录与历史运行

`GET /monitoring/catalog?appid=...&model_id=...&offset=0&limit=100&catalog_revision=...`

响应：service_instance_id、view_schema_version、cursor、catalog_revision、items、total、offset、limit、next_offset。首次页可无revision；后续页必须带，revision变化409 CATALOG_REVISION_CHANGED，重读整份分页。

每个item：appid、model_id、active_run_id、publish_seq、published_at、data_range_utc={start,end}、snapshot_url。目录按(appid,model_id)字节序，筛选为精确匹配。catalog_revision是读事务内最大publish_seq（无发布为"0"）；cursor是同一事务内最大event_seq。读取不扫描CSV/结果目录，不以目录存在推断成功。

latest比较键=(组最大有效time_ns, publish_seq)。相同最大时间按后发布排序；不进行跨文件拼窗或合并缓存。缺组不填零；空结果不清除旧组。events表示发布顺序，不能代替数据新旧比较。

`GET /monitoring/runs?model_id=...&appid=...&offset=0&limit=100&catalog_revision=...`

只列已发布完整运行，按publish_seq降序，有run_id、status（completed/no_valid_rows）、published_at、file_data_range_utc、group_count和数据身份；appid筛选通过publication_groups，仅含该组的run。无appid筛选可以发现no_valid_rows。分页同revision规则。单个queued/running/failed/interrupted仍用既有GET /analysis-runs/{id}或提交回执查回，不伪造完整结果。

## 3. SSE发布与恢复

`GET /monitoring/events?after=<cursor>`，响应text/event-stream。cursor语法 `<service_instance_id>:<event_seq>`，序号为非负十进制；客户端当不透明字符串保存。Last-Event-ID非空时优先于after。首次连接不带两者时从当前高水位等待新事件，**完整恢复流程仍须先catalog再after**。

事件kind：
- result_published：一次run完整发布，data含run_id/model_id/publish_seq/published_at/status/view_schema_version/service_instance_id。包含正常无报警和no_valid_rows；不附全量appid/指标。
- run_terminal：failed/interrupted含run_id/model_id/status/error_code/finished_at及event_seq；不产生publish_seq、不改变业务目录。
- reset：客户端必须关闭旧流并重取目录后重连，data含reason（expired/future_cursor/instance_changed/invalid_cursor）和catalog_url；不发新的id，不以reset冒充数据发布。

每个持久事件SSE id即完整cursor；publish_seq=其result_published的event_seq，所以允许间隔。在同一服务实例内严格递增，重复发送允许。数据库事务提交后才可发送；同run恢复不另建publication。客户端按实例+event_seq去重，依catalog选择active_run_id。

初始配置建议：注释heartbeat=20s，retry=3000ms；持久日志最多100000条且最长7天，保留两约束交集；保留水位持久化、不重置自增序列。after=最早保留序号−1仍可连续回放，更早或大于当前高水位reset。维护清理由后台写路径/维护循环做，GET不删除日志。无日志且从未发布时cursor0合法。

每次读取最多128条事件，逐批关闭数据库事务后再等待/发送；单连接发送等待上限10s、全服务默认最多64条SSE连接（可配置），超限连接在开始流前503 SSE_CAPACITY_EXCEEDED。使用持久日志作为队列，不为每个浏览器积累无限内存。慢客户端超时断开，重连回放或reset；不阻塞计算线程。心跳不带id、不触发目录读取；正常UI不轮询指标。

## 4. 轻量展示快照

`GET /analysis-runs/{run_id}/view-snapshot?appid=...`

| 字段 | 约定 |
| --- | --- |
| identity | service_instance_id、view_schema_version、run_id/appid/model_id、publish_seq |
| provenance | 组data_range_utc、file_data_range_utc、published_at、source_label（仅相对展示名）、input_sha256、settings、rules、runtime编码/算法/资产身份、simulation_semantics、metadata_origin |
| metrics | 保持GroupMetrics业务字段名，按第1节输出精确整数，rate/null不变；含threshold_states和measurement_signatures |
| distributions | json_tokens / prompt_tokens / ideal_compute_input_tokens → "1000"/"2000"/"5000" → 完整Histogram；共1029桶 |
| quality | file_quality(scope=file)和group_quality(scope=appid、coverage、duplicate_scope)；不能归属的skipped_rows=null |
| thresholds | 当前结果冻结规则与比较结果（含comparator、threshold、value_kind、observed_value、state）；不读今天的规则替换 |
| signal_summary | 该run/appid固定信号数、event_ids_digest、view-signals_url；不含可变消费status |
| capabilities/links | 原JSON/轻证据/请求页/导出，模板正文为false且不提供伪链接 |

同instance/schema/run/appid内容不可变。写阶段预生成主体，publish字段来自已提交不可变元数据；GET确定性组装，使用UTF8、ensure_ascii=false、sort_keys=true、紧凑分隔、allow_nan=false，无末尾换行；ETag为完整未压缩响应字节SHA256加引号。Cache-Control: private, no-cache，支持If-None-Match→304；新请求日期等易变值不放响应体。原文/详情另用no-store。

不存在组404 GROUP_NOT_FOUND，未发布409；读取产物校验失败返回503 VIEW_ARTIFACT_UNAVAILABLE并保留旧完整快照，不临时补算。不在GET生成/写缓存文件；可有有界进程内只读缓存。

## 5. 多列请求与已有详情

`GET /analysis-runs/{id}/requests?appid=...&metric=prompt_tokens&lower=0&upper=...&sort_by=prompt_tokens&sort_order=desc&hash_id=...&hash_match=exact&offset=0&limit=50`

- appid必填；metric只允许J/P/C的完整字段名；lower/upper约束同既有长度接口，左闭右开，upper缺省无上界。hash_match=exact或prefix，按文字匹配（SQL通配符转义），保留所有重复hash行。
- sort_by允许time_ns/source_record_index及J/P/H/C/O完整字段名，sort_order=asc/desc；同值永远以source_record_index升序打破并列。排序/过滤身份原样回传。
- 返回total、offset、limit、next_offset、items；item包含request_ref={run_id,source_record_index}、hash_id、time_utc和J/P/H/C/O所有列。列表不返回原JSON/evidence/Token IDs。
- 数据来自同一个结果集，offset是筛选排序后的行位置；不得按不同排序分页位置合并。降序曲线可继续复用旧lengths，或从同一请求页读取对应列；不把部分加载标作全量。

`GET /analysis-runs/{id}/requests/{source_record_index}?appid=...`：返回以上行+原JSON预览、utf8_bytes、preview_bytes、truncated、可用证据摘要及正文/轻证据链接。默认预览最多65536字节，按UTF8合法边界截断，不重序列化JSON。未保存模板正文明确capability=false。

`GET .../requests/{index}/body?appid=...`：精确CSV解码后的原JSON字符串，UTF8 text/plain流式，no-store；不生成新的模板正文。`GET .../requests/{index}/evidence?appid=...&offset=0&limit=256`：已有special ranges等数组分页，固定UTF8字节半开区间、total/next_offset、source pointers及partial/unknown标记；禁止调用explain。详情与正文均先验证appid和ref匹配。

## 6. 信号分页与规则编辑

新增 `GET /analysis-runs/{id}/view-signals?appid=...&offset=0&limit=50`：返回当前run关联信号，按event_id排序，total/next_offset有界；item含当前关联run/appid/model、event_id、metric/comparator/value_kind/observed_value/threshold/rule_id/revision、route、当前消费status、发布时间。消费状态变化不影响快照，且membership/排序由run_signals固定。旧/signals行为保留供旧调用方，新前端不使用其无界形式。

为避免前端在规则写入时丢失超JS安全整数，拟新增 `GET/PUT /monitoring/threshold-rules` 视图适配入口：字段与原规则一致，integer阈值和expected_revision用十进制字符串，ratio阈值用number，value_kind由metric决定且严格校验。转换成既有RuleUpdate后共用ControlStore CAS，不新增比较算法/配置表。GET按appid/model过滤，offset/limit有界分页且返回rules_revision；后续页绑定该revision，变更时409 RULES_REVISION_CHANGED。旧/threshold-rules不改变。新增GET/PUT /monitoring/models/{model_id}/settings作为展示整数适配：settings内整数和expected_revision用十进制字符串，转回ModelSettings/SettingsUpdate共用原校验、CAS和存储；不新增设置表。旧/models枚举仍可用于发现模型ID，编辑读取走新适配，不把旧revision先变成JS Number。

## 7. 提交幂等与回执

扩展原 `POST /analysis-runs` 可选字段submission_key（ASCII [A-Za-z0-9._-]，1..128字符；前端生成随机UUID）。不带key保留旧行为，新UI必须带。

同key同规范请求(file_ref、model_id；含未来影响提交语义的字段)返回原run/status，响应仍202；同key异体409 SUBMISSION_KEY_CONFLICT。相同文件用新key是新任务。设置/规则依旧在claim时冻结，不因幂等改变冻结时点。

首次请求校验输入/模型/资产后，key与queued入库同事务；并发第二次以库唯一约束为准。已存在key必须先返回原回执，不能因输入后来移动、设置改变或资产暂不可用而拒绝查回。首次校验失败不消耗key；服务崩溃不能留下没有任务的key。

`GET /analysis-submissions/{submission_key}` 返回对应run_id/status/created_at及run_url；未见key404 SUBMISSION_NOT_FOUND。回执与run同寿命持久保留，首版不自动清理。原始输入文件内容快照仍在worker领取时生成，本轮不把file_ref改为上传协议。

## 8. 明细导出

`GET /analysis-runs/{id}/requests/export?appid=...&format=ndjson|csv&...同列表过滤排序参数`。路由注册须避免把export当source_record_index。默认全量组，带筛选时明确export_scope=filtered；忽略/拒绝offset、limit以免把当前页误称全部。行中只有请求身份、UTC时间和J/P/H/C/O。

NDJSON：首条type=metadata，含instance/schema/run/appid/model/input_sha256/settings摘要、时间范围、过滤排序、预计行数；中间type=request；末条type=summary，含实际行数和所有request行UTF8字节（含各自换行）SHA256。未收到summary或摘要不符视为下载未完成，不能当成功导出。

CSV：每行附run_id/model_id/appid及配置摘要，Content-Disposition只用内部安全文件名，响应头X-Export-Row-Count声明行数；客户端校验记录数以发现提前断流。以csv库正规引号/换行转义；可能触发公式的文本字段加单引号并声明X-CSV-Text-Escaping=apostrophe，精确保真使用NDJSON。计量数不改变；不包含原始正文。流式每次最多256行，断线关闭句柄；不建立控制库长事务。

## 9. 样例、确认点及实现验收

[合成协议示意样例](examples/monitoring-view-v1-draft.json)明确标记proposal/synthetic，不是运行结果；只展示所列响应片段，完整类型/必填验证在S0固定，并在实施后生成实际OpenAPI与真实合成结果，不覆盖旧OpenAPI。

本轮建议用户核对：latest=(组max时间,发布序号)、预生成主体+只读组装、7天/100000事件保留、失败终态推送、旧结果sidecar回填、始终十进制字符串及规则适配。性能数值属于待测目标，见[B005.1 TESTS](../tasks/monitoring/batches/B005.1/TESTS.md)。后端增补通过不代表前端交互或完整服务已经验收。


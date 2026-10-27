# 监控展示服务契约 S0 1.0.0（B005.1）

2026-10-27，**S0契约已固定；新增服务实现未完成**。维护：Token监控；消费：前端。按用户要求先完成S0字段/成功错误样例/R1与R2边界固定；不改写已批准的[计量契约](MONITORING_V1.md)。当前运行接口仍见[实现说明](MONITORING_IMPLEMENTED_API.md)。内部组件/事务/迁移见[B005.1 DESIGN](../tasks/monitoring/batches/B005.1/DESIGN.md)。

## 1. 通用规则与兼容

- 新视图协议 view_schema_version="1"，控制库拟schema3，代码拟dev6；三者独立。当前代码仍dev5/schema2，不先更新实际OpenAPI。
- 所有新的展示响应带service_instance_id、view_schema_version；固定结果带run_id/model_id/appid。身份来自持久控制库，正常重启保持；全新状态目录是新身份。复制成独立服务或恢复导致序号回退时须新实例身份，不能复用同名浏览器缓存。
- 表示请求数/Token数/分位值/直方图计数及边界/rank/ref索引/seq/revision/total/offset的整数，**在新展示DTO中始终是十进制字符串**，即使值很小也不切类型；有符号delta允许负号。ratio/share为有限number或null。bin_width为1000/2000/5000的number枚举，limit为1..1000的number；schema号/ID为字符串。0和null不同，尾桶upper=null。
- 冻结settings/rules按schema声明处理整数，包括规则整数阈值；阈值附value_kind="integer"、"ratio"或"number"以区分：integer为十进制字符串整数；比率指标用ratio+有限number；兼容已有非比率浮点阈值用number+有限number，observed_value仍按指标类型。不得只转换大于2^53的值造成类型漂移。整数累计在Python/SQL边界保持精确；前端用十进制字符串/BigInt表示，不先经过Number。
- 旧API默认形状和旧CLI保持兼容，不把其numeric字段悄悄换字符串。新UI统计/信号/详情及设置/规则编辑走本草案的新适配协议；大整数阈值和revision通过十进制字符串无损写入后转换成原业务类型，禁止JS先舍入后提交。
- 新 GET 不做编码/仿真/统计/详细归因/迁移。未发布409 RESULT_NOT_READY；未知run/appid/ref404；未完成迁移503 VIEW_INDEX_NOT_READY。不返回部分200伪装成功。
- 错误沿用 `{"error":{"code":"...","message":"..."}}`，S0不提供details字段；不得回显原JSON、绝对路径或完整用户输入。所有结果范围都是数据筛选，不宣称RBAC。
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

### 3.1 R1：订阅与提交终态对齐（已采用方向）

catalog只恢复业务结果指针，不能恢复每个提交任务的终态；事件可能早于首次cursor或已超过保留期。因此“catalog + SSE”必须与持久回执的一次性状态对齐组合使用：

1. 前端ReceiptStore按service_instance_id持久保存自身submission_key、已知run_id、最小规范提交字段和local_submitted_at，不保存CSV正文；提交前先登记key。ReceiptStore与结果快照缓存分开，不随LRU或schema缓存清理丢弃未确认提交。
2. 先安装result_published/run_terminal/reset处理器，建立SSE；onopen确认本连接代次可接收事件后，再GET对齐本实例尚未确认终态的回执。每轮最多4并发，按(instance,key,连接代次/触发批次)去重，不按定时器轮询。
3. 触发为首次订阅就绪、重连就绪、reset重新订阅就绪、页面恢复、提交取得回执。页面恢复时若未连通先重建订阅；提交丢回执保留原key，通过回执查询/显式同key重试恢复。
4. 若GET返回queued/running，等待已经就绪的SSE捕获之后终态。若事件先于GET返回，终态不被迟到的queued/running覆盖；不同终态冲突显示协议错误，保留证据并显式重新对齐，不自行选择一个终态。
5. completed/no_valid_rows/failed/interrupted均是终态。持久记录后移出待确认集合。result_published即使对应run并非latest，也必须更新该提交回执。404不等于failed：显示“提交尚未确认”，允许用户同key重试；读取失败保留待确认项和显式重试入口。
6. reset撤销旧连接代次的回调，重读catalog并订阅，再对齐回执；旧实例回执不查新实例。普通服务重启保留实例身份，回执/终态不随事件日志清理。
7. SSE连接就绪不是“历史事件已全部送完”的屏障；GET和事件允许乱序，上述单向状态合并负责收敛。无需增加后台轮询任务或重新分析。

前端负责ReceiptStore/触发/合并，后端负责持久回执、正确状态及同事务事件。真实浏览器验收由后端Session 1统一执行；仅证明事件可回放不能关闭R1。

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
- 数据来自同一个结果集，offset是筛选排序后的行位置；不得按不同排序分页位置合并。新UI降序曲线从同一请求页读取对应列，item.position是筛选排序后1起全局行位置（offset+页内序号），不使用其他列排名拼接；不把部分加载标作全量。旧lengths仅保留兼容，不作为精确整数展示入口。

`GET /analysis-runs/{id}/requests/{source_record_index}?appid=...`：返回RequestDetail，包含request原事实、body_preview={text,total_utf8_bytes,preview_utf8_bytes,truncated}、evidence_summary、capabilities和links（完整定义见S0字典）。默认预览最多65536字节，按UTF8合法边界截断，不重序列化JSON。未保存模板正文明确capability=false。

`GET .../requests/{index}/body?appid=...`：精确CSV解码后的原JSON字符串，UTF8 text/plain流式，no-store；不生成新的模板正文。`GET .../requests/{index}/evidence?appid=...&section=special_ranges&offset=0&limit=256`：section=special_ranges或source_fields（默认前者），对选定数组独立分页，固定UTF8字节半开区间、total/next_offset、source pointers及partial/unknown标记；禁止调用explain。详情与正文均先验证appid和ref匹配。

## 6. 信号分页与规则编辑

新增 `GET /analysis-runs/{id}/view-signals?appid=...&offset=0&limit=50`：返回当前run关联信号，按event_id排序，total/next_offset有界；item含当前关联run/appid/model、event_id、metric/comparator/value_kind/observed_value/threshold/rule_id/revision、route、当前消费status、发布时间。消费状态变化不影响快照，且membership/排序由run_signals固定。旧/signals行为保留供旧调用方，新前端不使用其无界形式。

为避免前端在规则写入时丢失超JS安全整数，拟新增 `GET/PUT /monitoring/threshold-rules` 视图适配入口：字段与原规则一致，integer阈值和expected_revision用十进制字符串，ratio阈值用number，比率指标value_kind=ratio；非比率整数阈值为integer，兼容已有非比率浮点阈值为number；严格校验类型，不改原比较算法。转换成既有RuleUpdate后共用ControlStore CAS，不新增比较算法/配置表。GET按appid/model过滤，offset/limit有界分页且返回rules_revision；后续页绑定该revision，变更时409 RULES_REVISION_CHANGED。旧/threshold-rules不改变。新增GET/PUT /monitoring/models/{model_id}/settings作为展示整数适配：settings内整数和expected_revision用十进制字符串，转回ModelSettings/SettingsUpdate共用原校验、CAS和存储；不新增设置表。旧/models枚举仍可用于发现模型ID，编辑读取走新适配，不把旧revision先变成JS Number。

## 7. 提交幂等与回执

扩展原 `POST /analysis-runs` 可选字段submission_key（ASCII [A-Za-z0-9._-]，1..128字符；前端生成随机UUID）。不带key保留旧行为，新UI必须带。

同key同规范请求(file_ref、model_id；含未来影响提交语义的字段)返回原run/status，响应仍202；同key异体409 SUBMISSION_KEY_CONFLICT。相同文件用新key是新任务。设置/规则依旧在claim时冻结，不因幂等改变冻结时点。

首次请求校验输入/模型/资产后，key与queued入库同事务；并发第二次以库唯一约束为准。已存在key必须先返回原回执，不能因输入后来移动、设置改变或资产暂不可用而拒绝查回。首次校验失败不消耗key；服务崩溃不能留下没有任务的key。

`GET /analysis-submissions/{submission_key}` 返回固定字段：service_instance_id、view_schema_version、submission_key、run_id、model_id、status、created_at、started_at、finished_at、error_code、run_url。未开始/未结束时间及无错误为null；四种终态有finished_at，failed/interrupted有error_code。时间为规范UTC；响应Cache-Control:no-store。查询在同一短读事务内联结receipt与run，不能从入队时缓存的queued回执返回过期状态。未见key404 SUBMISSION_NOT_FOUND，不代表任务执行失败。

回执与run持久保留，首版不自动清理，不受7天/100000条UI日志保留策略影响。failed/interrupted与run_terminal同事务；completed/no_valid_rows、完成索引和result_published同事务。已受理key无条件查回其当前任务状态，不重新检查CSV是否仍存在，不受默认配置/资产变化影响；终态查询不启动新任务。

新前端POST提交、GET回执和显式GET run须发送`X-TokenScope-Instance-Id`为当前确认实例；不匹配返回409 SERVICE_INSTANCE_CHANGED且不入队/返回另一实例的任务。旧调用方不带该可选头时保留兼容行为；相应响应均附该头，新回执DTO同时含实例身份。此防护补齐目录校验后服务更换实例的竞态，不提供权限鉴别。前端发现实例变化停止旧代次/请求，不能仅更新header后重送旧回执。

原始输入文件快照仍在worker领取时生成，不把file_ref变成上传协议。回执/终态完整合成样例见`examples/monitoring-view-v0.2/receipts.json`，无真实请求正文。

## 8. 明细导出：R2方案A（保留完整性验证）

`GET /analysis-runs/{id}/requests/export?appid=...&format=ndjson|csv&...同列表过滤排序参数`。静态export路由先于request index路由。默认组全量；有过滤时export_scope=filtered；传offset/limit返回422 INVALID_EXPORT_QUERY，避免当前页误称全量。固定同一已封存run/appid，读取已有投影，不重算统计/编码，不预先缓存整个导出。只有身份、时间和J/P/H/C/O，不含原始正文或Token IDs。

### 8.1 响应头、字节和资源边界

两格式返回Cache-Control:no-store、X-Export-Schema-Version:1、X-Export-Row-Count（不含metadata/summary/CSV表头的十进制请求记录数）、X-TokenScope-Instance-Id、X-Export-Run-Id和安全Content-Disposition文件名。Content-Type分别application/x-ndjson; charset=utf-8及text/csv; charset=utf-8。预期记录数可由同一不可变投影上的筛选计数取得，不全量序列化后缓存。

首版应用导出不启用内容压缩、不为获取长度缓冲整个响应，流式响应默认省略Content-Length。若已知精确长度而提供该头，它是HTTP消息body表示的字节数；存在Content-Encoding时它不是解压后的字节数。浏览器Response.body通常提供解码后的内容字节，前端上限及下面SHA均针对解码后的UTF8内容，排除HTTP chunk framing。代理不得改写内容/换行；若压缩必须记录Content-Encoding并继续按实际解码字节计数。缺头/不可信长度不能当作小文件证明。

后端游标逐行或有界读取：最多256行且已取行缓冲目标≤1MiB，不能先fetchmany(256)积累256条超大记录后才检查。超大单行单独处理，分块写出，不截断、不对摄入设置1MiB限制；其单行内存上界单列记录。停止消费/断线取消及时关闭查询、reader和任务，不持有控制库长事务。错误发生在headers前返回标准错误；发生在流中中止流，**不能追加看似成功的summary或伪造EOF成功**。

### 8.2 NDJSON完整格式

UTF8无BOM，每个JSON对象一行，以单字节LF（0x0A）结束，最后summary也有LF；无空行，无CRLF行终止。字符串内部CR/LF按JSON转义，不能产生物理记录分隔。对象使用sort_keys=true、紧凑分隔、ensure_ascii=false、allow_nan=false；明确的十进制字符串保留原值。

顺序严格：恰好1个metadata → 0..N个request → 恰好1个summary → EOF。summary后任何额外记录/字节、缺最后LF、非法UTF8、截断或错误类型均失败。

- metadata固定字段：type、export_schema_version、service_instance_id、view_schema_version、run_id、appid、model_id、input_sha256、settings_sha256、data_range_utc={start,end}、filter={metric,lower,upper,hash_id,hash_match}、sort={by,order,tie_breaker}、export_scope、expected_rows。默认filter完整写出，时间范围是组有效范围，不假称筛选后重新聚合；样例人工身份不代表真实运行。
- request固定字段：type、request_ref={run_id,source_record_index}、hash_id、time_utc、json_tokens、prompt_tokens、ideal_cached_input_tokens、ideal_compute_input_tokens、completion_tokens。即使hash重复也逐条输出。
- summary固定字段：type、actual_rows、request_lines_sha256。摘要为**所有request记录原始UTF8字节及各自LF按传输顺序拼接后的SHA256小写hex**；不含metadata、summary、BOM、HTTP framing。空集使用空字节串SHA256，仍发送metadata+summary。

客户端校验metadata身份/过滤/排序、header预计数、metadata.expected_rows、解析请求数、summary.actual_rows全部一致；按收到的原始request行字节增量摘要，禁止parse后重序列化再算。缺summary/错SHA不能显示导出成功。

### 8.3 CSV完整格式

UTF8无BOM，分隔符逗号、双引号引用，内部双引号写成两个双引号；逻辑记录结束符CRLF（包括最后一条）。字段内已有CR/LF保留并正确加引号，不能按物理换行计数。

固定列顺序：
```text
service_instance_id,view_schema_version,run_id,model_id,appid,settings_sha256,source_record_index,hash_id,time_utc,json_tokens,prompt_tokens,ideal_cached_input_tokens,ideal_compute_input_tokens,completion_tokens
```

必须恰好一个该表头，每个数据记录列数一致，EOF处于完整记录结束状态，记录数等于X-Export-Row-Count；空集为仅表头CRLF、计数0。声明X-CSV-Text-Escaping:apostrophe；文本字段首字符为=、+、-、@、TAB、CR、LF时前置单引号，字段引用由CSV规则独立处理；不影响计量列。客户端不得悄悄还原成公式。CSV只验证结构/记录数，**不宣称字节SHA验证**；保真和摘要验证选NDJSON。协议fixture的CSV文件SHA仅用于核对样例文件身份，不升级CSV产品验收承诺。

### 8.4 浏览器处理与兼容（前端v1.0参数已获批，待实测）

前端按能力检测secure context及showSaveFilePicker/createWritable。支持时用户点击先选文件，再fetch流；Worker增量解析/计数/SHA、有界背压写入临时可写流，EOF及完整性通过才close。错误/取消abort并释放资源，不能显示成功；某些环境可能残留空占位，标未完成，不擅自删用户文件。

拟定应用切片64KiB、最多4片在途，记录解析缓冲上限1MiB（序列化UTF8逻辑记录，含记录终止字节）；一页一个活动导出。不支持流式文件写入时，只允许总解码字节≤16MiB且完整校验后Blob下载；累计超限立即取消并提示缩小范围/使用支持浏览器，不退化成未经校验的普通下载。

这些值与前端最终v1.0一致；本轮后续核对viewer/APPROVAL，最终稿及参数已获批，代码/资源实测仍未通过。当前CSV reader对hash_id/appid仅校验非空及无NUL，没有1MiB业务上限；即使导出不含正文，长ID也可能超过UI限额。前端须明确失败，后端不得为配合UI改Token计量/摄入或截断字段。S0已复核正常样例和NDJSON单记录恰好/超过1MiB的合成字节边界；前端F001/F005仍须验证消费能力，不将字节测量当浏览器通过。

### 8.5 实际验收与fixture边界

提供[完整合成导出样例与清单](examples/monitoring-view-v0.2/README.md)，含Unicode、引号/内嵌换行、重复hash、空集，预期NDJSON request字节摘要和CSV解析记录数可独立复核。它们是协议夹具，不是当前服务输出。

真实浏览器联合门槛包含提前断流、缺summary/错SHA、错误行数/非法CSV EOF、UTF8切点、取消、慢sink/磁盘错误、真实文件close/abort、能力不足、小文件备用路径边界和单记录超限。以≥256MiB且每记录≤1MiB的合成流验证队列上界和**浏览器增量内存目标≤64MiB**，独立于后端导出RSS≤64MiB；记录基线/峰值/方法、JS堆与进程RSS不可混称。

真实服务正常导出、受控故障代理/夹具、前端假服务证据分开标记；mock sink不能替代真实文件写入。后端不为演示生成全量内存缓冲，前端不以大文件response.text/blob/arrayBuffer实现校验。完整服务联合验收由Session 1统一执行，失败或降低标准交用户裁决。

## 9. S0固定入口与实现边界

[S0契约交接](../tasks/monitoring/batches/B005.1/S0_CONTRACT.md)、[完整字段字典](MONITORING_VIEW_V1_FIELDS.md)、[JSON Schema](schemas/monitoring-view-v1.schema.json)、[设计OpenAPI](schemas/monitoring-view-v1.design.openapi.json)和[完整成功/错误样例](examples/monitoring-view-s0/README.md)构成contract 1.0.0。旧v0.1片段、v0.2回执/导出fixture保留追溯；v0.2导出原字节纳入S0校验和摘要。

S0已固定全部新DTO、参数/头/错误、R1/R2责任、success/null/大整数/多模型和错误样例，可供前端锁版本并开发假服务。设计OpenAPI不是当前运行接口；B005.1 S1先按固定Schema实现DTO，S1–S5后用真实合成API对照；J01–J06/R1/R2统一真实浏览器验收另行执行。S0通过不等于R1/R2实现或完整服务通过。

## 10. 兼容与交接

新增精确展示字段与旧numeric API分开；旧RunState.snapshot/result为不透明兼容JSON，前端不据此生成展示统计。runtime.profile_json/effective_options_json为已有配置的完整JSON文本，防止未知数字舍入；详见S0字段语义。signal_summary.event_ids_digest按排序event_id各加LF的UTF8计算SHA256；empty为空字节摘要。

后端Session 1维护此固定协议，前端F001记录实际接收的版本/摘要；本轮不替前端解除暂停或更新其状态。任何后续协议变更须版本/摘要/样例同步并核对消费方，不默改已固定字段。最终联合测试、代码包和获批Docker/镜像交付由Session 1统一负责；B006仍pending。评审落实见[响应](../tasks/monitoring/batches/B005.1/REVIEW_RESPONSE_v0.2.md)。

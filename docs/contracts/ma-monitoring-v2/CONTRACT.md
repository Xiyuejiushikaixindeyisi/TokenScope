# MA backend protocol 1.0.0

独立命名空间 `/monitoring/ma`，不修改旧S0。JSON模型以schema.json和contracts.py的跨字段校验为准；M004已将OpenAPI改为由真实路由签名导出，包含请求、查询参数和响应；生成过程不启动服务。

POST /runs接收Submit，返回202 Receipt。GET /runs/{ma_run_id}、GET /submissions/{submission_key}返回Receipt；未知404。提交键相同且规范化绑定相同查回旧任务，异体409 SUBMISSION_CONFLICT；先查回再检查文件。窗口端点按公共解析归一UTC、文件引用按InputRoot.parts规范化，source_timezone固定UTC。配置在claim时冻结。

GET /catalog可选model_standard_name，offset默认0，limit默认100（1–1000），catalog_revision可选；offset>0必须携带revision，不一致409 CATALOG_REVISION_CONFLICT。只展示completed，UUID按字典序，运行按持久入队序倒序。空结果仍列运行和empty_scope_reason。所有offset/revision/count/token为规范十进制字符串。

GET /runs/{ma_run_id}/instances/{instance_uuid}返回固定Snapshot，未知UUID404 INSTANCE_NOT_FOUND，任务未完成409 RESULT_NOT_READY。三种身份service_instance_id/ma_run_id/生产instance_uuid不互用。服务身份检查沿用X-TokenScope-Instance-Id（不匹配409）。快照携带配对与独立指标、窗口绑定、两角色质量、运行配置/编码摘要、12桶及所有预计算箱宽。GET不编码/回放/修改结果。

GET /runs/{ma_run_id}/quality：offset/limit同上，返回按role（pre先）、source_record_index、field、code排序的行问题；无原文，允许同记录多原因。系统级失败仅回执错误，不冒称完整质量报告。

状态queued→running→completed/failed/interrupted。完整封存后一次控制事务发布revision；只有完整封存可恢复发布，未封存running中断，不续跑残余缓存。旧发布不覆盖。

错误HTTP：INVALID_REQUEST/INVALID_PAGINATION/INVALID_BIN_WIDTH 422；INPUT_NOT_FOUND/RUN_NOT_FOUND/SUBMISSION_NOT_FOUND/INSTANCE_NOT_FOUND 404；SUBMISSION_CONFLICT/CATALOG_REVISION_CONFLICT/RESULT_NOT_READY/RESULT_SEAL_INVALID/INPUT_CHANGED/SERVICE_INSTANCE_CHANGED 409；存储503。CSV文件级MISSING_COLUMNS/MALFORMED_CSV/MIXED_SPEC/OUTSIDE_WINDOW使任务failed；具体role/行号记错误证据。行级独立质量错误不终止运行。全局资产/模式错误沿用公共错误码，不能吞成行错误。对外错误不回显正文/敏感路径。

A/P/R/E/Q、P_db与P_local、null/0、12桶、有限预热、两独立分布与设计v1.0一致。直方图结构沿用V1 distribution，整数递归转十进制字符串，布尔/浮点/null不变；禁止无限/NaN。全空指标sum=0而hit_rate=null；有请求但无有效真实字段时pressure uncached=null；空桶uncached=0。真实指标总量只按有效集合计算。

公共接入：parse_utc旧签名可用，用户线负责DD/MM及field参数；MA通过捕获InvalidRow后定位调用字段，不复制解析器。ModelEncoder/EncodingBatchService/TokenShardWriter/make_strategy/distribution只消费。worker处理器签名process_next() -> DTO | None；返回None表示无任务/锁忙，每个入口自行持state_root/worker.lock，dispatcher不得外层嵌套持锁。注册接口由MA M004实现，用户线适配器后续接入，真实联合状态独立登记。

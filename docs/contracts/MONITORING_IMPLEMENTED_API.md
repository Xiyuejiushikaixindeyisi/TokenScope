# Token 监控已实现接口

代码 0.1.0.dev6，控制库 schema 3，view schema 1（B005.1后端闭环；真实联合pending，详见RESULT）。业务语义仍是已批准的 [v1.0](MONITORING_V1.md)；[dev6实际 OpenAPI](schemas/monitoring-dev6.openapi.json)由运行代码生成。本文补齐 B001 时尚未实现的结果接口，不修改批准原稿或前端代码。完整本机 E2E 由 B005 判定，不能将本页视为现场验收。

## B005.1 前端接入

固定契约仍为S0 1.0.0；字段/错误/成功样例以[冻结协议](MONITORING_VIEW_V1_DRAFT.md)、[字段字典](MONITORING_VIEW_V1_FIELDS.md)为准，运行态新增接口已实现。历史dev5 OpenAPI保留，不覆盖S0生成输入。

| 操作 | 实际接口 |
| --- | --- |
| 完整目录、历史运行 | GET `/monitoring/catalog`、`/monitoring/runs`，后续页带同一catalog_revision；冲突409重新读取 |
| 持久终态通知 | GET `/monitoring/events`，after或Last-Event-ID；重放/reset/20秒心跳，容量64、发送超时10秒；终态与发布同事务 |
| 不可变展示快照 | GET `/analysis-runs/{run_id}/view-snapshot?appid=...`，完整9直方图/冻结参数/分位/质量范围/ETag/304 |
| 请求多列与详情 | GET `/analysis-runs/{run_id}/requests`，统一排序分页；`/{source_record_index}`、`/body`、`/evidence`读取已存内容 |
| 导出 | GET `/analysis-runs/{run_id}/requests/export`，format=ndjson/csv；固定run、支持筛选/排序，不接受分页参数 |
| 信号 | GET `/analysis-runs/{run_id}/view-signals`，appid分页，关联当前run而非首次共享outbox的run |
| 精确整数适配 | GET/PUT `/monitoring/models/{model_id}/settings`、`/monitoring/threshold-rules`；计数及版本以十进制字符串传输，旧接口仍用原数值类型 |
| 幂等提交及查回 | POST `/analysis-runs`增加可选submission_key；GET `/analysis-submissions/{submission_key}`联结持久任务当前状态 |

提交/回执/显式run读取支持`X-TokenScope-Instance-Id`防护；同key同输入先查回原run再考虑验证，文件移动不破坏恢复。异体409 SUBMISSION_KEY_CONFLICT；未受理失败不占key。回执不随SSE日志清理；前端按R1连接建立后一次对齐，不使用周期状态轮询。

SSE只对相同游标的空尾部查询共享最多100ms结果以控制20订阅开销；重放/重置不缓存，清理后立即失效。它不缓存统计、不替代持久日志。导出按单条读取、64KiB输出，NDJSON的SHA只覆盖request行原UTF8字节加LF；CSV采用固定14列、CRLF、公式首字符转义。停止读取或断线显式关闭底层生成器/只读连接。单条极大文本仍可能超过1MiB目标，前端按既定R2拒绝超限记录，不截断计量。

schema2→3启动前自动建立SQLite一致性备份（先pending文件、校验/fsync后原子改名）；已有完成结果由worker仅根据既有facts回填sidecar，完成前新视图返回503 VIEW_INDEX_NOT_READY。原seal不改写。停服务回退需先保存完整schema3状态及sidecar，再恢复schema2备份并使用dev5代码；不要让旧代码直接打开schema3。

B005.1本机验证结果和未决项见[RESULT](../../achieve/2026-10-28/docs/tasks/monitoring/batches/B005.1/RESULT.md)。这些接口可供独立前端按S0接入，但真实完整服务联合/容器/V100验收分别记录，不把后端单独通过当成最终服务通过。

## 提交与状态

`POST /analysis-runs`：`{"file_ref":"glm.csv","model_id":"GLM-5.2"}`，202 返回 queued。后台单 worker 自动领取；CLI 的 `work-once` 处理一个任务。设置和阈值在领取时冻结。

`GET /analysis-runs/{run_id}` 返回 status、settings、snapshot、result、error_code。queued 时快照为空；running 可查询冻结配置；只有 completed/no_valid_rows 才有 result。result 含 quality、源摘要、资产身份、CPU/批次预算、各阶段耗时、计量签名、UTC 时间范围。没有有效行时无分组、不虚构零长度请求。

`GET /healthz` 是进程存活；`GET /readyz` 检查存储、固定资产和当前默认配置。DeepSeek default profile 仍 pending 时整体 503，其模型记录 `ENCODING_DEFAULT_UNRESOLVED`，GLM/Qwen 的 readiness 独立可见。DeepSeek 显式请求思考选项仍可提交；遇到未指定模式的有效请求，整个 run 明确 failed，不静默选默认或跳过。

## 模型设置与编码模式

GET/PUT `/models/{model_id}/settings` 保持 revision CAS；参数字段见 OpenAPI。注册的 `encoding_profile` 有 `default`、`thinking_enabled`、`thinking_disabled`。后两项只有用户明确选择后才成为下一次运行默认；请求内显式选项优先。GLM/Qwen default 使用原模板默认，DeepSeek default 不设思考默认。配置不会改写旧结果。

GLM CP 仍使用批准的 scalar 默认 1；现场 PCP1/DCP8 记录是声明信息，未擅自映射。GF hash_block_size 不代替仿真 block_size。

## 已存结果读取

| GET 路径后缀（均在 `/analysis-runs/{run_id}` 下） | 查询与结果 |
| --- | --- |
| `/metrics` | 可选 appid，offset 默认0、limit默认100（1–1000）；返回 groups、total_groups。组内 totals 为 J/P/H/C/O 完整字段名，quantiles 为 J/P/C→p50/p80/p90；附 capability、threshold_states 和每指标 measurement_signatures |
| `/length-histograms` | 必填 appid，bin_width 为1000/2000/5000，默认5000；metrics 内有 json_tokens、prompt_tokens、ideal_compute_input_tokens 三份完整直方图 |
| `/lengths` | 必填 appid；metric 为上述三种长度之一，默认 prompt_tokens；lower默认0、upper可空，左闭右开；offset/limit分页，返回 points/total，每项有全组降序 rank、request_ref、hash_id、UTC时间、length |
| `/signals` | 返回持久化 signals；无消费者始终 pending_consumer，不表示分析器已经执行 |

所有结果 GET 只读且要求 completed 索引已提交；未完成返回409 RESULT_NOT_READY，未知任务404。切换分箱只读取预计算数据。排名在整个 appid 分组内计算，筛选后保留原 rank，同长按 source_record_index；前端显示时将 UTC 转为北京时间。直方图使用5K默认、200K开放尾桶、并列众数全部标记，分位数仅显示图外数值。

## 阈值与信号

GET `/threshold-rules` 可选 model_id；PUT 同路径提交 appid/model_id/rule_id、expected_revision（新建为0）、metric、comparator、threshold、enabled、可选route和measurement_signature。读取当前结果中对应指标的签名用于建立规则；不提供生产默认阈值。

metric 支持 request_count、ideal_hit_rate、totals 下五类Token计数，以及 quantiles 下 J/P/C 的 p50/p80/p90；比较方向 lt/le/gt/ge。未配置不报警；口径变化 needs_review。缓存参数只影响 H/C 签名；相同源、模型、适用签名、appid、规则revision生成同一event_id。重跑GET可关联同一事件，其 result_ref 指首次成功发布该事件的结果，不伪造第二次触发。

## 详细复核和错误

内部 `MonitoringService.explain_encoding(run_id, source_record_index)` 与 CLI `explain` 显式重编码，校验已存 IDs 摘要；不放入页面 GET 路径。字段定位未知处标 partial/unknown，UTF-8 byte 区间不能误作原 JSON 精确贡献值。

API错误统一 `{"error":{"code":"...","message":"..."}}`，不回显输入正文。坏行只在运行质量与行错误表中记录；存储/资产/模式错误失败整个运行。封存后控制事务失败保持running，下一worker验证 manifest 后恢复；未封存的遗留running标interrupted，重试显式提交新run。

历史B004的schema1→2为增量建表；当前schema3迁移及回退见上节。只允许专属服务状态目录，运行产物和原CSV不自动清理。

正式构建镜像将release_id和SOURCE_MANIFEST摘要写入镜像环境，GET /version回显；本机未打包时为null，不冒充已发布版本。独立CLI/service进程8CPU affinity与Rust8/BLAS1策略见本地运行说明。

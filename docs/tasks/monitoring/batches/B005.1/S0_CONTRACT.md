# B005.1 S0 契约固定与前端交接

2026-10-27，contract **1.0.0 / view_schema_version="1"**；状态：**S0契约已固定，可用于前端契约开发；服务实现未完成**。依据用户本轮“应该先完成S0契约固定”执行。B005.1 S1–S5/J1、B006仍未执行；不更改dev5/schema2运行版本。

## 交付入口与权威顺序

1. [共享行为契约](../../../../contracts/MONITORING_VIEW_V1_DRAFT.md)：路径名保留历史DRAFT，S0正文现为固定1.0.0，不代表运行API。
2. [完整字段字典](../../../../contracts/MONITORING_VIEW_V1_FIELDS.md)与[JSON Schema](../../../../contracts/schemas/monitoring-view-v1.schema.json)：必填、nullable、枚举、整数表示、嵌套DTO均完整定义。
3. [设计OpenAPI](../../../../contracts/schemas/monitoring-view-v1.design.openapi.json)：16条路径、18个操作，参数、请求体、成功/错误响应、导出头及SSE类型。x-runtime-implemented=false；不替换[dev5实测OpenAPI](../../../../contracts/schemas/monitoring-current.openapi.json)。
4. [完整样例索引](../../../../contracts/examples/monitoring-view-s0/README.md)：75个JSON用例，以及正文、SSE字节流、两种导出正常/空集；均为人工合成协议样例，不是Token计量或真实服务证据。
5. [固定摘要清单](S0_MANIFEST.json)、[校验报告](../../../../../artifacts/validation/monitoring/B005.1/S0/contract-check.json)、[S0闭环](S0/RESULT.md)。

不一致时视为契约缺陷，先修订版本及样例，不能让消费方猜字段。JSON Schema约束消息形状；本文和共享契约补充跨字段、排序、事务、字节与恢复语义；设计OpenAPI定义接口边界。所有新DTO拒绝未声明字段；Error不含可选details。Legacy结构为现有接口原样兼容，不做新视图消费入口。

## 字段语义补充（配合完整字段字典）

| 范围 | 固定解释 |
| --- | --- |
| 身份 | service_instance_id是持久UUID；run_id是运行UUID；appid/hash_id是原始非空文字，必须URL编码；request_ref=(run_id,source_record_index)唯一，hash_id可重复 |
| 版本/序号 | view_schema_version="1"；revision/offset/total/seq为十进制字符串；publish_seq来自成功发布事件event_seq，可能有间隔；catalog_revision只随结果发布变，cursor也包含失败事件 |
| 完整时间 | time_utc/published_at/created_at等固定9位小数UTC；data_range_utc是组的有效请求时间范围，file_data_range_utc为整文件有效集；空结果范围start=end=null，空结果不建组 |
| 指标 | J=json_tokens、P=prompt_tokens、H=ideal_cached_input_tokens、C=ideal_compute_input_tokens、O=completion_tokens；P=H+C；命中率ΣH/ΣP，P=0时null；json_to_prompt_delta=P−J可负 |
| 分布 | 三类长度×1000/2000/5000三种宽度，0起左闭右开，最后[200000,+∞)；每快照1029桶；mode_bin_indices含全部并列最大桶；mode_share为单个众数桶占比，不将并列桶相加；<8000独立计数 |
| 分位数 | nearest-rank；权威p50/p80/p90由后端提供；前端图外展示，不依直方图插值或自行重算 |
| 质量 | file_quality计数守恒；group_quality只包含可归属appid的有效数、编码拒绝数及组内重复提示；skipped_rows=null表示不能将全文件无效行归属到此组，不能展示为0 |
| 规则数值 | value_kind=integer时threshold为十进制字符串；ideal_hit_rate用ratio+有限number；已有非比率浮点阈值用number+有限number。observed_value按指标类型：比率number，其余精确整数string。保留旧规则比较语义，不强制将已有90.5变成整数 |
| 阈值状态 | threshold_states维持现有启用规则评价；无启用规则为[{status:unconfigured}]。thresholds列冻结规则，disabled/clear/needs_review/metric_unavailable/triggered；后续编辑不改旧快照 |
| 摘要 | signal_summary.event_ids_digest=按event_id字节序排列后，每个ID加LF，拼接UTF8后SHA256；空集为空字节SHA。只摘要固定成员，不包含可变消费状态 |
| 请求页 | position是筛选和排序后1起全局行位置，即offset+页内序号；不是另一指标排名。稳定次序source_record_index升序；多列属于同一请求。新UI排名展示消费此页，避免旧numeric lengths丢精度 |
| 详情预览 | body_preview.text保留原JSON空白，preview_utf8_bytes是实际字节数，默认最多65536且不切断UTF8；total_utf8_bytes是全原文，truncated显式；不能暗示已保存模板正文 |
| 轻证据 | section=special_ranges或source_fields，默认前者；offset/total/next_offset仅针对选定section。区间为模板UTF8字节[start,end)，不是Token索引；source_fields为JSON Pointer字符串叶节点长度/摘要引用，不能相加当Token归因 |
| 不透明配置 | runtime.profile_json与evidence_summary.effective_options_json为完整JSON文本，用于追溯/展示，不让JS parse后Number舍入；不是新增可编辑参数。没有保存的字段不伪造 |
| 设置 | 默认GLM/Qwen/V4 block=128/1536/32、CP=1；更改下次claim生效，历史快照不变；Qwen/V4仍普通链式近似。hybrid可保存预留配置，但capability.not_supported，提交422；DeepSeek缺省思考仍pending，不由样例thinking_disabled代选 |

Schema的nullable不是允许制造空值：completed组存在时request_count>0；分位值仅空集为null；真正no_valid_rows用运行目录表示，查询任何组返回404。半开范围upper若非null必须>lower；页next_offset=offset+返回数，仅尚有余项时存在，否则null；非法页/排序/过滤422。目录与规则后续分页必须绑定revision，过期409并重读。

## R1 边界确认：终态恢复

已采用“持久回执 + 先订阅、后一次状态对齐”。后端提供当前持久Receipt，不保留只有queued的陈旧副本。成功/空集与result_published同事务，failed/interrupted与run_terminal同事务；失败事件不改业务目录。回执不随7天/100000条事件日志清理。

前端先注册事件处理器→SSE onopen→仅对本实例待确认key发GET（最多4并发），触发限首次/重连/reset后/页面恢复/提交回执，不做定时轮询。onopen不保证历史回放已完成，因此终态单向合并；迟到queued/running不能覆盖终态，冲突终态报协议错误。404为未确认，显式同key重试；绝不自动新key重提。跨实例旧回执停止查询，新UI提交/回执/显式run读取发送X-TokenScope-Instance-Id，失配409且不入队。

| 情景 | 固定结果 | 后续真实验证 |
| --- | --- | --- |
| 失败早于首次catalog cursor | 首次onopen后GET恢复failed | R1-01 |
| 事件过期reset | 重读目录重连后GET恢复四种终态 | R1-02 |
| GET running与SSE终态竞态 | 只前进到终态，迟到非终态不回退 | R1-03/04 |
| POST响应丢失/服务重启/CSV移走 | 原key查回原run，不重验已受理输入、不重建任务 | R1-05/06 |
| 新实例/404/冲突终态 | 隔离实例；404未确认；冲突显式协议错误 | R1-07/08 |

前端ReceiptStore和状态机归前端维护；后端事务/持久化/API归Session 1。S0固定协议与人工时序夹具，**不宣称已经跑过上述竞态或关闭R1实现问题**。

## R2 边界确认：方案A

- 支持secure context + showSaveFilePicker/createWritable的浏览器：用户手势选择文件→流式fetch→Worker增量解析/SHA→有界背压写入；结构/数量/摘要/EOF都通过才close并展示验证成功，失败abort/cancel。
- 应用chunk≤64KiB，最大4个在途；序列化单个逻辑记录≤1MiB（含分隔符）。CSV按含引号换行的逻辑记录计，不能按物理行计。此上限属于前端导出能力，不限制CSV摄入或后端计量。
- 无文件流式写入能力时，只允许解码内容累计≤16MiB，验证完成后Blob保存；超过立即中止。Blob只可声称校验通过且下载已发起，不可声称已经确认OS落盘；不能回退成未经校验链接。
- NDJSON：metadata→requests→summary→EOF；无BOM、每记录LF；SHA只覆盖request原始UTF8字节（含LF）；不得parse后重序列化算摘要。summary/EOF/必需头缺失、错计数或错SHA均失败；空集仍metadata+summary。
- CSV：固定14列表头、UTF8无BOM、CRLF记录、正确引号；校验身份、列数、逻辑记录数及完整EOF，对齐X-Export-Row-Count；只保证结构/计数，不声称内容SHA验证。公式防护按共享契约前缀apostrophe处理。
- 真正≥256MiB大流、慢sink/磁盘故障、浏览器增量内存≤64MiB、真实close/abort、后端独立RSS≤64MiB、代理/文件系统兼容仍须R2-01–10/J04/J06实测。S0仅生成1MiB等于/超过边界并独立测字节，不冒充浏览器测试。

完整服务由Session 1统一J01–J06/R1/R2验收；前端F006提交可复现构建/锁/资产/测试/问题/回退并标ready_for_joint。B006仍pending，联合通过后向用户展示具体候选版本与测试证据，获新同意才构建Docker和交付包。

## 前端接入与版本变更

F001现在可锁定S0_MANIFEST及完整样例，按设计OpenAPI做类型/假服务开发；F002–F005仍区分fake与真实API。前端实际接收确认、其暂停/恢复与测试进度由该会话/用户记录，本会话不自动替其恢复、不发送跨会话消息。S1先实现view_models并对固定Schema校验，不能再等S4才决定字段。

S0以1.0.0固定，任何字段/错误/状态/字节语义修改都须更新契约版本、摘要、样例及变更说明；不兼容变更先与消费方确认，必要时升级view_schema。运行实现通过S5后另生成实际OpenAPI与实测合成响应对照本固定版本；不能覆盖历史dev5证据。

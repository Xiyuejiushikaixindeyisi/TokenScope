# Token 监控首版公共契约

版本：v1.0，2026-10-26，**第一版最终设计配套契约，待审批**。维护：Token 监控。消费者：前端、两类分析、后续 Agent。业务范围以 [DESIGN](../tasks/monitoring/DESIGN.md) 为准；旧 v0.2 文档保留追溯，不作为当前开发入口。

## 输入和运行

每文件显式绑定注册模型，不建设跨文件窗口协议。CSV 列为 hash_id、appid、model_handle_start_time、completion_tokens、request_input。UTF-8 CSV 正常解码后完整保留 JSON 字符串。UTC 输入，内部 UTC，展示 Asia/Shanghai。

`request_ref=(run_id,source_record_index)`；序号从首条数据记录的 1 开始，区别于物理行。无效行跳过并记录原因；重复 hash_id 每行独立，只有提示。系统/文件结构不可恢复错误终止运行。数据质量计数满足 `records_read=valid_requests+skipped_rows`（可恢复且读取完成的文件）；duplicate_hash_id_rows 是 valid_requests 的子集。

运行启动时冻结模型设置和阈值快照，更新仅影响之后启动的运行。历史结果不可被新设置重新解释。来源摘要/run_id 仅用于定位、幂等和复算，不要求用户建立采集窗口身份。

## 参数和能力

H=理想命中的输入 Token 数；C=仍需计算的输入 Token 数=P−H；P=模板后输入总数。输出量独立。三个模型默认都计算 H/C，Qwen/V4 采用用户明确选择的普通链式近似，只将增强 hybrid 通道留作接口。

| 模型 | B 默认与单位 | 首版默认策略 |
| --- | --- | --- |
| GLM-5.2 | 128 simulation_input_tokens | full-block-mtp-v1 |
| Qwen3.6-27B | 1536 simulation_input_tokens | 同一 full-block-mtp-v1，chained_approximation |
| DeepSeek-V4-Flash-0731 | 32 simulation_input_tokens | 同一 full-block-mtp-v1，chained_approximation |

MTP 默认 true；本稿提案 CP 默认 1、prefix_cache 默认 true。128/1536/32 直接是简化仿真的输入 Token 块长，不把 V4 的 32 自动换算成其他值，也不称其等价于真实 Ascend 物理 page 单位。hybrid 增强默认关闭，模型结构本身未改变。显式启用尚未实现的增强通道应在启动前拒绝；默认链式路径都可执行。所有模型显式 prefix_cache=false 时可运行 NoCache 对照，H=0/C=P。

模型设置包含 revision、B/单位、MTP、CP、cache_mode、hybrid_enabled、prefix_cache_enabled；保留未来 prefill_policy。配置能力查询返回可执行状态。生产 TP/dtype/镜像 digest 不是必填；实际使用的编码资产/模式和算法版本仍固定以支持复算。

## 请求与聚合记录

| 字段 | 语义 |
| --- | --- |
| json_tokens / J | 对原始 JSON 的普通文本编码长度，不加入模板/BOS/EOS |
| prompt_tokens / P | 所选模型模板/专用编码的实际输入 IDs 长度 |
| ideal_cached_input_tokens / H | 所选规则可复用输入；未支持为 null |
| ideal_compute_input_tokens / C | P−H；未支持为 null |
| completion_tokens / O | 原 CSV 输出数量 |
| cache_status | available / disabled / not_supported |
| ideal_hit_rate | 同组 ΣH/ΣP；零分母或 H 未支持为 null |
| json_to_prompt_delta | P−J，不称纯模板开销 |

同组为本文件内 appid×model，配置全程固定。三个模型默认路径的 H/C、总量和重算分布均有定义；结果记录 simulation_semantics 以区分完整块规则与 Qwen/V4 近似。只有错误或无有效样本才产生相应不可用状态，不因模型是 Qwen/V4 自动置 null。显式无缓存情景 H=0/C=P 是有定义的对照值。

请求至少保存 hash_id/appid/UTC、source_record_index、J/P/O、cache status/H/C、IDs offset/count/digest、编码/策略身份、轻量来源证据。聚合保存有效数、质量统计、五类总量、命中率、三组分位数和阈值状态。轻量缓存事件/发布摘要供分析复核，不含数值 KV tensor。

## 长度频数分布、分位数与辅助排名

升序数组 x[1..N]，Pq=x[ceil(q×N)]，q 为 0.5/0.8/0.9；空集 null。重复值时至少 q 比例不大于分位值。固定算法名 `nearest_rank`。

默认展示为长度直方图：横轴为长度区间（Token），纵轴为请求数或占比。**P50/P80/P90 只显示图外数值，不画图内分位线；众数所在柱高亮**。默认 5,000 Token、可选 1,000/2,000，1K=1,000。

`Histogram` 包含 metric（或按 J/P/C 的 metrics 映射）、bin_width、regular_domain=[0,200000]、overflow_start=200000、boundary=left_closed_right_open、sample_count、bins 及 summary。有限箱覆盖 `[0,200000)`，末桶为 `[200000,+∞)`；每箱 lower/upper/count/share/overflow，末桶 upper=null、overflow=true，其余 overflow=false。下界包含、上界不含；零长进入首箱，200,000 恰好进入末桶；全部空箱也返回。末桶单独标注“≥200K（汇总）”，不当作 5K 宽的密度柱，不丢弃任意长的请求。

summary 包含以下权威字段（J/P/C 独立计算）：

| 字段 | 语义 |
| --- | --- |
| mode_bin_indices | 所有 count 最大且大于 0 的箱的零起始下标；并列全部返回 |
| mode_count / mode_share | 每个众数箱的 count 和 count/N，不是并列箱合计 |
| under_8k_count | 原长度 <8000 的请求数，不能从 5K 箱粗略推算 |
| overflow_count | 原长度 ≥200000 的请求数，等于末桶 count |
| max_length | 原长度集合最大值，空集 null |

每箱 count 求和为 N，share=count/N，分位数从未分箱原长度精确计算。众数是分箱后请求最多的区间，并非精确长度的众数；选不同宽度可改变众数。末桶可被高亮，但必须注明无法定位尾部内部的峰或比较频数密度。N=0 时 count=0、share/quantiles/max_length=null、mode_bin_indices=[]、mode_count=0、mode_share=null，显示空态。

GET length-histograms 只读预计算的分箱、summary 与分位数；前端切换已有 bin_width 不运行分析。同组 J/P/C 使用同一范围及末桶定义，前端共享纵轴刻度。原 J/P/C 独立降序排名保留为辅助视图，同长按 source_record_index 排序；分页结果含 rank、request_ref、length。区间下钻支持 lower≤length<upper，upper=null 时无上限。计量、直方图和明细使用同一有效集合。

## 仿真和证据

顺序：REQUEST_ARRIVED → CACHE_LOOKUP → PREFILL_COMPLETED → CACHE_PUBLISHED → REQUEST_FINISHED。请求间按 UTC 和记录序号排序；请求内部 local_event_seq 递增；前一请求事件完成后才接纳下一请求，不生成虚构执行时长。

三个模型复用完整块算法：B_eff=B×CP；在 P−1 上限内连续匹配得到 k；MTP 时退一个有效块；H=max(k−mtp,0)×B_eff。发布 floor(P/B_eff) 个完整输入块。appid 隔离、空缓存起始、无限容量、只用输入 IDs。仅增强 hybrid 类首版不执行 plan/lookup/publish，返回 not_supported；默认三个模型都路由 FullBlockStrategy。

编码详细映射按需调用监控共用实现；结果必须与已存 IDs 摘要一致。所有特殊区间注明 UTF-8 byte 左闭右开；缺失来源为 partial/unknown。字段计数不得独立编码后简单求和当作精确归因。

## 阈值和信号

规则按 appid/model/rule_id 保存 metric、comparator、threshold、enabled、revision、route、measurement_signature。初始为空；数值在用户三天稳态数据分析后配置。未配置/指标不可用/口径不兼容分别为 unconfigured/metric_unavailable/needs_review，不发伪信号。

route 候选 prefix_analysis、length_analysis、signal_only。默认低命中到前缀分析、长度分位数到长度分析、总量/请求数仅信号。信号含观察值/阈值/方向、规则身份、配置语义、来源和完整结果引用。

event_id 绑定源摘要、模型、适用计量配置、appid、规则 revision/指标；同输入同配置重跑幂等，新配置/规则允许新事件。完整结果封存后，同一配置库事务提交 completed 索引及 outbox；无消费者时 pending_consumer，不声称分析已执行。

## 兼容和样例

[首版示意样例](examples/monitoring-v1-illustrative.json)覆盖三模型默认 B=128/1536/32 的链式命中、重复 ID 保留、坏行、nearest-rank 和无阈值。所有长度人工构造，不是 tokenizer、部署或性能实测。

相对 v0.2 的变化：增强 hybrid 实现推迟，三模型先共用链式近似；生产部署审计不再作为输入门槛；配置下次运行生效；UTC/重复/坏行明确；分位算法改为 nearest-rank；阈值数值延后；采用离散事件框架。接口与字段待本次批准后由 B001 固化，不误标为已上线 API。

相对 v1.0-rc1：默认改为 5K、支持 1K/2K，0–200K 加开放尾桶；增加众数区间和并列高亮所需字段；分位数仅图外显示。原请求与命中算法口径不变。前端起点见[冻结 HTML](../../artifacts/prototypes/monitoring-v1/tokenscope-monitoring-baseline-v1.html)。

## v1.0 服务与交付约定

相对 rc2，J/P/H/C/O、链式算法和直方图字段/含义保持不变。当前设计新增现场资源与 batch/交付约束，不将环境报告当作运行验收。rc2 前端原型可继续作为展示起点，正式消费者记录依赖的契约版本；最终类型、序列化与错误码在 B001 固化，不改变这里的业务语义。

- `file_ref` 指配置输入根目录内的相对文件，服务校验实际路径不越界；首版手动放置 CSV，不在线获取数据。POST 显式启动，GET 只读取已有结果。
- `GET /healthz` 返回进程状态；`GET /readyz` 返回存储与三模型资产校验、各模型 readiness，未满足要求返回未就绪；`GET /version` 返回实际代码/发布包、schema、算法、设计和资产身份。
- `GET /analysis-runs/{id}/signals` 读取该完整结果关联的已持久化信号，未接分析器不伪造执行结果。
- API/CLI 采用同服务层；运行冻结配置，返回 run_id 后可查询；失败/中断结果与 completed 结果明确区分。发布 outbox 不得引用未封存产物。
- 发布 manifest 将代码包、执行 prompt、CPU 镜像、资产/依赖锁、来源和测试证据绑定一个 release_id；目标平台 linux/amd64，首版不依赖 CUDA/GPU。实际代码版本与 schema 版本在实施中分配，不因设计版本 v1.0 就声称已有 v1.0 服务。
- 输入输出单位与 null/empty 状态保持不变。现有样例仅说明指标与分布，不含可运行词表或服务健康检查响应，不作为完整 API schema。

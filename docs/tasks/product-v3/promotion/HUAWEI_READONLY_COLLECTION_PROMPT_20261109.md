# 华为执行prompt：TokenScope宣传汇报所需的既有结果收集

请执行本次**只读信息收集**，用于TokenScope四页产品汇报的业务覆盖和场景分布。你在华为现场工作，只读取已经完成的TokenScope结果，整理一份Markdown回传。本任务不是产品验收、数据重新分析或部署任务。

## 1. 本次目标与边界

收集全部已完成、可确认来自真实业务的数据，基本单位为`appid × model_id × common_name × 已有运行/结果版本`：

- appid、模型系列、原始model_id与common_name。
- 对应有效请求数。
- 平均输入长度估算：套chat template之后的输入Token长度，按已有直方图每个区间的请求数占比乘区间右端点，再求和。
- 该结果已有的理想前缀命中率。
- 该结果已有的输入长度直方图。

**重点核查员工助手：appid精确为`S00000000000000000000000000000773`，模型为DeepSeek系列。** 在目录中发现它实际绑定的DeepSeek model_id/common_name，再分别读取。不要改查Qwen，不从其他模型补数。现场如为`DeepSeek-V4-Flash / DeepSeek-V4-Flash-0731`则记录原值；若存在其他DeepSeek版本，一并分别列出，不预先限定只有这个版本。

命中率分界固定50%：原始比率`>=0.5`为高命中，`<0.5`为低命中，缺失为不可判定。长短输入的正式分界等回传后确定；10000 Token仅作临时观察线，保留连续数值，不将它固化成最终场景分类。

禁止重新分词、重新套模板、回放/仿真、重新索引、异常分析、TTFT评估、训练或压测。禁止提交/绑定新任务，禁止调用POST/PUT/PATCH/DELETE。不要修改产品、配置、模型资产、原数据、state、默认选择、前端或既有分析结果；不要启动/重启/停止服务或容器。不要为了展示新表格而导入结果或刷新前端状态。

仅允许：GET已有成果；必要时只读已有结果的元数据/汇总表；在项目内新建本次报告及轻量收集脚本。不要读取原始请求正文、tools/messages内容或逐请求Token制品，不扫描原始CSV，不扩大数据访问。已有业务任务优先，本次串行低频读取，不并发打满API、不做全state哈希或大文件备份。

## 2. 定位已有服务与结果

先确认现场TokenScope项目根目录、现有服务/容器和state挂载，使用已有监听地址。既定地址是现场`http://127.0.0.1:18002`；以实际运行状态核实，不把其他电脑localhost或本机演示run ID带到现场。

优先通过现有API读取，按现场`GET /openapi.json`核实接口；以下是当前HV2已有路径，不要求升级到某版本：

1. `GET /monitoring/catalog`获取`service_instance_id`。用户V2 GET带头`X-TokenScope-Instance-Id: <现场实例身份>`。
2. `GET /monitoring/user-v2/runs?limit=1000&offset=0`。首屏保存`snapshot`，后续同一筛选带`snapshot`并按`next_offset`读到null，不能只取第一屏。保存目录总数、服务身份、契约版本及获取时间。
3. 从entry.source获取`user_run_id`、`base_run_id`、`index_revision`、model/common_name、input/manifest/settings摘要、编码资产身份和文件观察时间范围。不要混淆user_run_id与base_run_id。
4. 对纳入的每个appid结果，读取：
   - `GET /analysis-runs/{base_run_id}/metrics?appid=<URL编码后的appid>&limit=1000`
   - `GET /analysis-runs/{base_run_id}/length-histograms?appid=<URL编码后的appid>&bin_width=1000`
   后者取响应`metrics.prompt_tokens`。不要使用`json_tokens`、`ideal_compute_input_tokens`、排行中的重算长度众数或P90替代输入长度直方图。
5. 如需核对V2原有理想命中指标，可读取`GET /monitoring/user-v2/runs/{user_run_id}/rankings`，固定`index_revision`，分页取准确appid；不要把子串筛选结果全部当成该appid。`/modes`只含重算长度的众数信息，不是完整输入长度直方图。

URL查询参数用标准URL编码，不用字符串拼接猜测。服务身份或目录snapshot变化时，丢弃未完成的拼接页，最多重新读取一次；仍变化则回传已完成范围与原因，不循环轮询。如果服务没有启动，不启动服务；只有可确认的完整已有结果才可用只读方式读取，否则报告缺口。SQLite使用`mode=ro`/`query_only`，不运行会初始化数据库或启动worker的产品入口，不执行迁移、checkpoint或VACUUM。不能确认一致性时停止该项读取。

## 3. 排除构造样本与选择版本

目录中的`dataset_kind=trace`并不保证是真实采集数据，需要结合已有manifest、输入摘要、已知交付说明与结果来源确认。UUID形状、正常appid或正常时间也不是真实来源证明。

必须排除已知ICSL构造数据及其重跑结果。以下按`input_sha256`匹配，不按现场run ID匹配：

| 修订 | appid提示 | 输入SHA256 |
| --- | --- | --- |
| 初版80条 | demo.synthetic.icsl.glm52.cch.v1 | da1fe5db38e8f384082fb2c23477062c5b44627d32a70f7ca7ec2302d77f71c4 |
| revision2 / 80条 | demo.synthetic.icsl.glm52.cch.v2 | f59ed3cee7544180e3b12627852a1517b6996b8383b565a708ea23f3ae7d7bb5 |
| revision3 / 102条 | com.huawei.icsl.base / GLM | e1425657987dce4ad312d33c7e40a3ac98a822ec7ed928fb7979f1dcc785678b |

其他明确fixture/demo/构造来源同样排除；来源无法确认的单列“待确认”，不混入真实汇总。排除项只从本次报告的统计集合排除，绝不删除或隐藏现有产品数据。也不要把`com.huawei.icsl.base`在其他真实来源/模型下的全部结果一刀切排除。

目录可能包含同appid和模型的多个历史运行。完整回传结果来源清单；主表每个`appid + model_id + common_name`选择已确认真实且ready的默认结果。若默认是构造来源，则在真实结果中按服务返回的registration_order选最新已发布项，标明“本报告选择，不修改产品默认”。同一运行重复目录条目去重；历史版本仅列附录，不重复累计请求量。不同模型/common_name保留独立行。

empty、未完成、损坏或不可读取结果单列，不用0伪装长度/命中率。若多个真实历史运行代表不同日期/范围，不把它们直接相加为同一时窗；记录各自来源及主表选择理由。文件观察时间范围仅表示文件范围，不能说成该appid的准确活动窗口。

## 4. 指标口径与轻量汇总

输入长度估算严格使用已有`prompt_tokens`直方图，优先所有行统一使用已存在的1000 Token分箱；现场某结果只有其他已存档位则如实使用并记录bin_width，不自行生成新箱、不重算逐请求长度。

设非空有限区间的计数为n_i、右端点为u_i，总有效请求数N为直方图sample_count：

`mean_input_tokens_est = Σ(n_i × u_i) / N`

用整数/Decimal保留精度，最后格式化到小数点后2位；分类用未四舍五入的数值。不得用区间中点、左端点、最大长度、众数或总Token/N替换用户指定公式。可以用已有总Token/N作只读一致性核对，但不替换本报告主指标。

校验`Σbin.count == sample_count == metrics.request_count`，并与该appid目录请求数核对；遇到差异保留原值和原因，不裁剪数据凑一致。

右端点加权是偏高的近似均值，报告明确写“平均输入长度（直方图右端点加权估算）”。若存在`upper=null`且count>0的开放尾箱，按此公式无法算完整均值：主字段填null并说明溢出请求数；可另外利用已有summary.max_length给出明确标注的辅助上界估算，但不得冒充规定公式的均值。开放尾箱count=0时跳过，不把200K当开放尾箱右端点，不丢弃非零尾箱。

理想命中率直接读取该结果已有的`ideal_hit_rate`，保留原0–1数值及展示百分比。可核对已有汇总`ideal_cached_input_tokens / prompt_tokens`，不得用MA实际cached、单请求比率平均或修改后的优化评估比率替换。数据为空/分母0/指标缺失时填null，不能补0。

临时辅助字段：
- `hit_band_50`: high（>=50%）、low（<50%）、unknown。
- `length_position_vs_10000`: below、equal、above、unknown。恰好10000单列，不擅自定长短归属。
- 10000仅是观察线。不要只回传“长/短”标签，必须保留均值和完整直方图；本次不判定Agent/RAG/信息提取等任务语义。

## 5. 员工助手 × DeepSeek 专项

精确查找`S00000000000000000000000000000773`所有DeepSeek已完成真实结果。对主表所选结果重点给出：

1. appid、实际model_id/common_name、请求数、run/revision、来源与时间口径。
2. 平均输入长度估算、完整计算式中的N及Σ(n_i×u_i)、分箱宽度、溢出情况。
3. 理想命中率原值与百分比，以及已有总输入Token/理想缓存Token用于核对。
4. 已有输入长度直方图的全部非零区间、数量与占比；如已有5000档，也只读附上，方便与现有页面视觉对应。缺失不补算。
5. 该结果的已有固定前端链接：`/#/users?run=<现场user_run_id>&appid=<appid>&revision=<现场index_revision>`；使用现场实际可访问主机/SSH转发说明，不写本机演示run。

若没有员工助手×DeepSeek：明确“未找到”，列出实际发现的该appid模型和DeepSeek目录检索结果，不提交新任务，不换用Qwen数据代替。不要为本次收集启动浏览器或点击会触发自动SLO评估的页面；只生成指向已有成果的固定链接。

## 6. 回传内容：只交一份Markdown

在现场TokenScope项目内新建`docs/huawei/TOKENSCOPE_PROMOTION_READONLY_20261109.md`。如果同名报告已存在，增加时间后缀，保留旧文件。仅回传这一份Markdown，不要求另传CSV、JSON、截图、数据库、目录或压缩包。以下内容全部放在正文，可复制的数据块使用Markdown内嵌JSON/CSV。

### A. 执行范围与完整性

写明服务/版本、读取开始结束时间、实例身份、目录snapshot、分页数、目录项总数、已纳入主表数、独立appid数、模型集合、历史结果数、排除构造数、待确认/空/失败数。按现有集合说明覆盖，不能冒称企业全部业务或全部流量。禁止用截图替代数值表。

### B. 主表：全部已纳入的appid×模型

一行一个主表结果，至少包含：

`row_id, appid, model_family, model_id, common_name, request_count, mean_input_tokens_est, bin_width, ideal_hit_rate, ideal_hit_rate_percent, hit_band_50, length_position_vs_10000, histogram_ref, source_ref, availability_or_note`

如既有产品映射可读，可附产品名称，员工助手标用户已指定；其他名称未知留空。不为这次任务另做产品归属调研，不从模型品牌推断业务场景。不要求req/s、Token/s、SLO、MA、额外诊断。

### C. 全部主表对象的已有长度直方图

每个histogram_ref必须对应正文内一个数据块。保留metric=prompt_tokens、bin_width、sample_count、区间边界规则、regular_domain、overflow_start、所有非零区间的`lower/upper/count/share`、已有summary/quantiles。可省略零计数区间以减少体积，但必须声明`zero_bins_omitted=true`并给出完整域/箱宽，确保可无损恢复零箱；非零尾箱绝不省略。不只提供众数、TOP几箱或截图，不重新分箱、拟合高斯或平滑曲线。

### D. 员工助手 × DeepSeek 专项

按第5节完整展开，便于直接制作典型业务图；它的数据仍保留在主表中，不因专项单列重复计数。

### E. 来源、排除和缺口

source_ref关联user_run_id/base_run_id/index_revision、input_sha256、既有manifest/settings/encoder身份及文件观察时间。附简明历史结果清单和主表选择理由；排除/待确认逐项注明原因。记录实际使用的GET路径、参数/分页口径和关键响应字段，避免无法复查的口头结论。

收集结束再次GET目录，核对服务身份和已读取结果的source/revision/默认标记；本次零写入操作，不能修改它们。若期间有其他任务自然发布新结果，单独记录快照变化，不将其误判成旧数据被修改，也不为消除变化取消其他任务。报告声明实际执行的写入只限新收集文件，既有数据、结果、默认入口和前端未由本任务改变；若无法确认则写明限制，不填未经验证的“全部通过”。

请求串行，单次超时设限；失败最多重试一次。出现API不可用、损坏索引或权限不足，收集其他可读项并在报告列缺口，不修产品、不重启、不重跑分析。不因个别缺失交回空报告，也不让收集影响现场业务。

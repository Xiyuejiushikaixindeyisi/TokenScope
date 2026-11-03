# 华为agent：低命中率结构抽样与预算预估（本轮未现场执行）

这是HV2-R2交接的方法与启动prompt，不是已发布代码/镜像指令。待总设计师验收并安排现场版本后使用。两大Qwen只low_hit，不为成本测量额外启Token；不启动T1/hybrid/Agent，不修改生产请求/业务策略，不打包部署或另开监听端口。已有服务/新state安排遵守总负责执行板。

## 可直接使用的prompt

你负责对用户指定的appid/模型做有界成本核对，先核对候选版本、公共冻结身份、用户2.1.0目录身份与资源；先出结构统计与预算判断，不直接长全量跑。业务入口使用source_kind=user_v2，传user_run_id、appid、expected_index_revision、window=null；base_run_id仅核对血缘，不能同时提交。记录service_instance_id、manifest与模型Tokenizer/Template/profile摘要，不混用MA数据。

1. 只读核对监控目录/index中该appid实际N、总raw UTF-8字节、最大请求字节、模型/索引revision和时间范围；没有聚合字节时顺序流式累计，不把请求全文载入内存，不以CSV文件大小当raw字节。先核实剩余磁盘/RAM和当前并发，原state及证据不删。小样本结果不能代替全appid分母。
2. 在同appid/模型中按纯messages、有tools且长Schema、工具排列/集合、合法工具结果/历史等结构留少量原请求。建议**研究档位**为每结构至多4条且总数不超过16条，配对保留源record_index、原顺序、raw SHA与完整JSON，优先选择已观察差异附近的相邻请求；这是已标注的成本/规则样例，不宣称随机代表性、异常率或全量命中率。重复内容不能直接判应删，L4不认定同会话改写。真实工具调用链是否合法与业务必需性分别核实。
3. 在总负责安排的独立离线input/state中建立明确sample-only来源，保留选样清单，重新生成base及user_v2索引。不得在原user_run中隐藏过滤或截断后仍标全量；不得用原base缓存命中当样本基线。按该实际模型编码，低命中true/Token false，用新submission_key。正式展示的收益仍只来自正式指定appid冻结scope的完整两阶段评估，不把sample-only收益写入其默认报告。
4. 首先使用N=8/16、candidate_limit=1/4的研究档位对比，必要时K=16只用于这16条以内样本的完整候选对照。固定其它预算、同编码身份，记录原文结构/字节、CPU、wall、进程峰值RSS与state磁盘增量；每次独立进程，标明模型初始化与profile工具开销。普通检测encoding_calls=0仍必须测读取、JSON解析、正则/哈希、候选匹配和序列化。
5. 从execution读取scan_complete/comparison_complete/retention_complete、checked/eligible、detected_by_rule/retained_by_rule、reason_codes及telemetry；同时读取rule_coverage与各experiment/evaluation。耗时包含嵌套阶段，不相加；source读取计数含重读；旧candidate_coverage_partial是宽泛阶段标志，不据此单独断言候选截断。返回CANDIDATE_LOOKUP_TRUNCATED与COMPARISON_COUNT_BUDGET_EXHAUSTED时两个事实均保留。
6. 必须估算两个比较通道、按规则保留、编码/实验/Plan和来源上界，再决定下次预算。任何上限不足保持partial/failed；不全局提额、不用把100改1000冒充性能修复。若N/源字节已超过max_source上限，预检会失败，不会自动抽样。若采样RSS/磁盘/耗时已接近机器限制，停止扩大；先交计量和具体瓶颈，不直接对26GB来源长跑。
7. 只有预算可承担且用户指定的正式scope明确时，再运行完整appid低命中诊断。pilot严格>1pp才full，完整full严格>1pp才优化卡；零/负收益保留为不合格，不拼接抽样结果。不同recipe收益不能相加。两大Qwen仍不调用Token；其他模型是否Token按显式开关和总负责授权，不能因low_hit自动强制。
8. 回传原始命令、候选/源/模型/预算身份、每次采样清单、状态/原因/资源与阶段表、失败及复测，注明仅样本验证的结论和下一步预算理由。输出业务根因必须有完整请求对照，未知就列缺口。不要改原现场报告；按总负责要求汇总唯一Markdown。

## 预算公式与边界

设目标appid请求N、候选上限K、每通道比较预算B。两个通道分别为L2和dynamic（L1/L3/L4/L5）；工具/结构分组可减少实际比较。

| 项目 | 上界或实际口径 | 决策依据 |
| --- | --- | --- |
| 理论候选比较/通道 | C(N,K)=sum(i=0..N-1) min(i,K)；N<=K+1时N(N-1)/2，否则KN-K(K+1)/2；实际硬上限min(B,C) | 两通道合计不超过2min(B,C)，不能把max_comparisons当两通道共享总额。字节检查失败可能已计一次comparison尝试，而report完成比较未增加 |
| 请求遍历 | 两检测通道各至多N；preflight另遍历N | source.rows_read含读取前序、token证据校验等重复读，不能用2N替代实际I/O；源manifest校验可能读整个index文件，不仅appid正文 |
| 原文/比较字节 | max_source_bytes约束该scope累计raw UTF-8；max_request_bytes约束单请求；max_comparison_bytes约束每次两请求raw长度和 | 累计读取字节可能远大于源字节；token数组、数据库页、Python解析对象另占空间，不是RSS硬上限 |
| findings保留 | F=max_findings>=5；L1–L5各floor(F/5)，余数依L1→L5分配 | 高频L4不能吃其他规则配额；同规则仍按发现顺序保留，不代表所有业务子类型已覆盖 |
| 保留payload字节 | R=max_retained_bytes以相同规则分额；actual JSON UTF-8序列化payload计量 | 不含SQLite索引/页和检测期间对象；达到后继续检测、计省略，retention_complete=false |
| 编码调用 | low_hit-only最多E=max_encoding_calls；一份完整评估每请求1次原文校验，发生修改再1次，单阶段最多2N | 每实验pilot至多2min(pilot_limit,N)，通过后full至多2N；最多max_experiments个实际实验。原source token读取不算新编码。冻结2方向若均开，总上界2E，但Qwen不能开Token |
| 实验与组合 | max_experiments控制已发现recipe实验数；标准自动推荐路径不隐式追加组合，max_combinations不自动扩大试验 | 实验提前因编码不足后后续not_run可继续显示ENCODING_BUDGET_EXHAUSTED；未触发编码停止时独立显示EXPERIMENT_BUDGET_EXHAUSTED |
| Plan | max_plan_bytes逐Plan约束；公共推荐另有max_total_plan_bytes等预算 | 编译可能遍历原scope，即使最终无卡片；不得只预算返回JSON |
| CPU/wall/RSS/磁盘 | 当前无可凭配置保证的硬CPU/wall/RSS上限；真实测量+检查点取消；state增长另外记录 | 不能用terminal时间间隔当CPU，不能把本机GLM约0.5GB初始化RSS外推Qwen/V100/容器，不能无限增加预算 |

本机实测参数来源：profile脚本max_source_requests=64、max_source_bytes=8MiB、max_request_bytes=1MiB、max_comparison_bytes=2MiB、F=25、R=1MiB、B=1000/通道、E=512、max_experiments=2、pilot_limit=4。**仅为本轮小样本研究设置，不是现场默认推荐。** N16/K4理论每通道54次；N8/K4为22次。若真实N=150000/K4，理论每通道599990次，B1000必然提前停，不是调高F即可完成；需要结合结构选择性和实测每次比较/源校验成本判断是否可承担。该算术不是已验证容量承诺。

本轮只优化相同字符串的无效正则扫描；共享来源重复读取/校验等潜在成本在公共冻结范围，未私自缓存或改变读取身份。若需要公共优化，应带profile、校验语义和内存上界交总设计师审定。

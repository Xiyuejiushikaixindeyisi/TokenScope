你是 TokenScope 华为实验机调查 agent。请执行本轮只读调查，统一排查多模型访问、异常页无结果和 MA 指标缺失，并研究真实 tools/messages 工作负载。严格按“身份与资源核对 → 真实数据量级和预算 → 三项问题复现与定位 → 有界启发式分析 → 单份报告”推进。

本轮只调查，不修改产品代码，不实施修复，不重新部署。所有修复建议须保持已批准的“用户监控、搜索与排行、异常分析、MA集群监控”四入口及L4/L5展示；UIR-03仍留V3，不纳入本次修复建议范围。以下是当前用户指令，覆盖旧部署 prompt 中扩大范围的执行安排。

一、执行边界与初始化

1. 在现场 TokenScope 项目中工作。预计项目目录为 /home/aarc/zhangxiyue/TokenScope，以实际挂载/文件核对；不要混用开发机 /home/zhangxiyue/TokenScope。先读现场 AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md 和相关任务入口；只读与本调查有关的材料。记录实际 session ID，取不到写“未知”，不能沿用开发机或前后端 ID。
2. 阅读此前的 HUAWEI_V2_ACCEPTANCE_REPORT.md，实际位置自行查找。原件保留，不覆盖、不纠正原文；勘误写入本次报告。用户已明确第二次验收不通过，不能以任务完成或 HTTP 200 代替用户认可。
3. 只读现有服务、容器、API、日志、配置、模型资产、原始 CSV 和已发布结果。允许在项目内独立 artifacts/research/ 子目录编写、运行统计/诊断取证脚本并保存中间记录；禁止改产品源码、测试、HTML/dist、契约、recipe、原 CSV、业务数据库和历史结果。不要提交、push、构建镜像或打包，不向外部模型服务发送真实数据。
4. 不通过 POST、重试、重算、修改配置或手工改数据库来“让页面出结果”。不启动新的正式监控/异常/收益评估任务。只读脚本不得实例化会建表/迁移的产品 Store；SQLite 使用只读连接与一致性读，注意 WAL，不能只复制主 DB 文件漏掉 WAL。
5. 保留现有失败状态，不停机重启、不新建服务或平行启动旧版。若服务未运行，继续能够完成的离线调查，明确哪些 HTTP/页面证据未取得。本轮不是新候选版本验收；以后新版本验收仍必须先停旧 TokenScope 服务/进程/容器，确认端口释放，再用新 state、新浏览器冷启动。
6. 浏览器复现使用独立临时 profile，保留用户原浏览器缓存。先核查页面读取流程不会提交计算，避免点击新建/重算等按钮。用户远程访问方式保持：
   ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44
   然后在用户电脑打开 http://localhost:18002 。
7. 本轮允许在以下范围自主完成只读调查，无需逐项等待确认；如果证据缺失或资源不够，保留已完成部分，明确缺口与下一步建议，不能擅自扩容、放宽产品预算或扩大业务范围。

二、固定身份、真实数据与资源

旧报告中的身份仅是核对线索，不代表当前现场事实：
- 交付版本：tokenscope-v2-approved-20261102。
- 源码：b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af。
- 镜像：sha256:a38d0ab2cfe26154c96adb5e876538893005e5cb100fc5c53640823c391683a8。
- service ID：abf57577-2dcc-4ddb-9758-bbbd548ddfdf。
- state：/home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-approved-20261102-20261102T0955。

核实实际容器、镜像 ID、服务地址/进程、源码与 HTTP 静态资源 SHA256、挂载、state、API capabilities、模型 revision/编码模式/配置摘要。发现不一致，先记录实际版本，再解释其对结论的影响。不能只看包目录名认定运行版本。

真实数据根目录：/home/aarc/zhangxiyue/10.20_Trace_extract/
- 10.20_Trace/ 的 3 个 CSV：用户监控和两类异常分析。
- 10.20_MA/ 的 18 个 CSV：MA 监控，按模型/规格的 pre、now 配对。
两类 CSV 字段不同，分别审计；不使用合成数据，不从其他数据源补造观测。

先核 CPU/内存配额、当前负载、磁盘/inode 和 tmpfs 余量。旧报告为容器 8 CPU、32GiB、tmpfs 512MiB，主机 40 CPU；这些须重查，不能占满主机。所有后续统计/微测先登记进程数、样本数、墙钟时间、内存和输出上限，以及停止条件；限额按实际可用资源设定并说明依据。

三、先调查真实数据量级和预算

先做流式清点和已有结果审计，再用有界样本测量复杂结构成本。禁止一次载入全部正文、全量展开嵌套树或未经估算遍历所有请求对。

旧报告基线供复核：Trace 共 26,881,586,080 字节、354,638 条记录；150,698 有效、203,940 跳过，拒绝比例约 57.51%。指定 10 个模型×APPID 共 111,541 个有效请求，其中两个大 Qwen 范围为 54,602 和 52,098。文件大小不等于某 APPID 的 raw_body UTF-8 字节预算。

必须调查：
1. 文件层：21 个文件逐个给完整 SHA256、字节、表头、CSV 逻辑记录数、时间范围和模型/APPID/UUID分布。含换行字段不能用 wc -l 当请求数。原文件不修改，重复扫描尽量合并。
2. 有效性：Trace 按模型×APPID统计原始记录、严格有效、监控索引、实际 task 范围及差异。拒绝原因给互斥主因与可重叠次因；无法识别 APPID 的行单列未知桶，计数守恒。不能仅凭“.5”样例断言全部跳过同因，不正则修 JSON 后重新导入。
3. 大小与结构：raw_body 总 UTF-8 字节、单条 P50/P90/P95/P99/max；已有 Token 输入/命中/重算统计；消息数、角色和内容形态；tools/functions、Schema 节点、调用参数/返回；内嵌 JSON 深度、提取 units、重复候选和比较字节。先做低成本全量统计，昂贵结构用分层样本。分位数标明精确或近似方法；最大值是全扫还是样本最大须注明。
4. 工作量与覆盖：逐 L1–L5/T2–T4 列已检查请求、适用数、候选比较、发现数、涉及的独立请求数、保留证据数、未检查量和截断原因。读取原任务的实际冻结配置，分清遍历完成、规则完成、证据保留与建议评估完成。
5. 性能与存储：既有阶段耗时及 state/SQLite/token shard/fragment/报告体积；缺少计时就写未知，不能由 mtime 编精确 profile。必要时在独立研究进程对少量真实样本做只读解析/提取/候选微测，记录读取、解析、提取、比较、序列化等耗时、峰值 RSS、CPU、I/O；触及登记上限即停止并记录覆盖。不能只按请求数线性外推，也不能用 encoding_calls=0 推断没有 CPU 成本。

预算至少覆盖以下层级。下列是旧报告或当前源码默认线索，逐项读取实际配置，注明来源，不能当现场已核实值：
- 任务输入：max_source_requests=100000，max_source_bytes=5GiB。
- 单请求：max_request_bytes=1MiB、max_depth=32、max_units=256。
- 低命中候选：candidate_limit=32；max_comparison_bytes=1MiB 按两条正文之和检查。两条各小于 1MiB 仍可能超出 pair 上限；候选截断本身也可能导致 partial。
- Token 比较：同名 comparison 预算按单请求候选规范化字节累计，不是上述单 pair 口径。
- 发现/实验：max_findings=100、max_experiments=20、max_combinations=10、pilot_limit=4，以及任务和插件各自的 encoding 限额。
- 方案/建议扩展：max_plan_bytes；独立 RecommendationBudget 的 proposals、recommendations、prepared_operations、proposal_bytes、单 plan/总 plan bytes、token_evaluations 和每组 evidence bytes。源码默认 prepared_operations=10000 等可能先于主任务输入预算触顶，须查实际快照。
- 资源：CPU、RSS、读写、临时空间、输出增长及保留旧 state 后的磁盘需求。

对每个研究范围形成预算表：
“实际量级/测量方法 → 当前上限 → 覆盖或确定超限 → 停止点 → 建议预算/抽样或分批策略 → 时间、内存、磁盘区间及依据 → 未知项”。

区分扫描上限和展示/证据保留上限。不能把 100 条 findings 当作完成，也不能把全部参数乘 10 就称修复。对未知长尾给区间，P99 不能替代 max 保证全覆盖。分批需解释跨批候选、缓存状态与覆盖边界；独立窗口缓存收益不能直接相加。

完成量级与预算记录后，继续下面三项排查及预算内的启发式研究；不能跳过此阶段直接重跑分析。

四、统一排查三个页面问题

每项都要提供“实际 URL/选择范围 → 可复现步骤 → API/数据库/源码 → DOM文字/浏览器错误 → 根因或剩余假设”，保留正常对照。

A. 同一用户无法查看全部模型

用户反馈：V1 同一用户入口可以看到该用户使用的所有模型，V2 一个 URL 似乎只能看到某个模型。

本机核对线索：V1 发布源码 92236ee993974e740d085e22e49b6b93c9487430 的 apps/viewer/src/app.tsx 按同 APPID 的 catalog 条目生成模型按钮，state/catalog.ts 读取 /monitoring/catalog 全目录。V2 UserMonitor.tsx 绑定单 user_run，模型区域是静态 common_name/model_id，最近运行仅来自浏览器。

请核实现场源码与页面是否一致，然后：
- 选真实跨模型存在的同一 APPID，并选仅一个模型存在的 APPID 作对照。
- 读取完整 /monitoring/catalog、已发布运行以及 /monitoring/user-v2/runs/{user_run_id} 和其 rankings 等只读接口，必要时只读索引；列出 APPID/model/common_name/user_run/base_run/index_revision/state/时间窗映射。
- 区分 S0 基础结果与 V2 用户索引，不能因 S0 有 77 个目录条目就声称 V2 全可访问。
- 在新浏览器进入普通 #/users 和原单模型链接，检查模型可见/可切换、APPID范围、刷新、从搜索与排行返回的行为及网络请求。不要通过新建或绑定任务制造缺失映射。
- 分清数据存在但入口缺失、目录/映射缺失、前端过滤/缓存错误及实际数据不存在。

修复建议的目标是恢复同一入口内完整模型发现与切换，并保留 V2 搜索/排行/TTFT；发送多个 URL 或要求手填 run ID 不能作为解决方案。同一 APPID 多模型的可访问性不等于把不同模型指标混合计算，也不擅自改成跨租户 userhash 聚合。本轮只给建议。

B. 后台已完成，异常页没有结果

读取指定 10 个任务完整 task_id，不截断；列模型/APPID/common_name/source/index/scope/window/方向、终态、report_published/digest、阶段完成度和 budget reason_codes。

先读三个 capabilities：
/diagnostics/capabilities
/diagnostics/discovery/capabilities
/diagnostics/recommendations/capabilities

诊断接口用实际 X-TokenScope-Service-Instance；监控接口用 X-TokenScope-Instance-Id，不能混用或绕过身份校验。

按实际 Schema、查询参数及分页规则核对：
GET /diagnostics/discovery/catalog
GET /diagnostics/tasks/{task_id}
GET /diagnostics/tasks/{task_id}/report
GET /diagnostics/tasks/{task_id}/recommendation-summary
GET /diagnostics/tasks/{task_id}/recommendations
GET /diagnostics/tasks/{task_id}/difference-groups
GET /diagnostics/tasks/{task_id}/difference-groups/{group_id}/examples
GET /diagnostics/tasks/{task_id}/items/{kind}

记录状态码、身份、摘要/counts/availability、必要响应和分页终点。前端实际读取 report + recommendation-summary，再读 recommendations/difference-groups；没有 report.items 不能直接定为根因。

同一任务分别复现：裸 #/analysis、页面选择历史报告、显式 #/analysis?direction=low_hit&mode=history&task=<完整task_id>，再查看已存在的 Token 方向结果；binding 若存在必须匹配。捕获目录、report 是否真正发请求、Schema/计数/身份错误、浏览器异常、缓存和 SSE 对齐情况。观察 SSE 设置明确时限，不发新任务制造事件。

本机线索：10 个任务均 partial，默认报告仅选 ready，因此裸入口可能没有默认报告；必须现场验证，不能提前定案。分别判断未选中报告、结果未发布、分组/建议扩展失败、身份/协议不匹配、前端未展示。

partial 不等于零异常，也不等于完整完成；已有结果应可发现并说明限制。不得把 partial 改成 ready、绕过校验或用原始 finding 偷换业务卡片。保留批准的 L4/L5 聚合展示；L1–L3 优化卡的完整评估和严格大于 1pp 门槛不改。没有 recipe、无适用规则、未检查、技术失败与确实没有发现分别解释。

C. MA 四项指标缺失

用户反馈：DeepSeek-V4-Flash 全部 UUID、GLM-V5.2 部分 UUID 缺理想命中率、真实命中率、整小时重算 Token/s、实际重算 Token。

对 9 个规格的全部已发布 UUID 清点；列全受影响 UUID，以正常 GLM 和 Qwen 为对照，未核查不能标通过。只读：
GET /monitoring/ma/catalog
GET /monitoring/ma/runs/{ma_run_id}
GET /monitoring/ma/runs/{ma_run_id}/instances/{instance_uuid}
GET /monitoring/ma/runs/{ma_run_id}/quality

分页携带正确 revision，固定 run/文件/配置身份。每个 UUID 至少列：
- model/spec、pre/now 文件 SHA、ma_run_id/revision、UUID、pre/now 记录数。
- A 可归属、P 生产输入有效、R 真实有效、E 理想结果有效、Q 配对，以及 coverage.encoded、pre_assigned/pre_encoded、ideal_status 的原值。
- 独立 ideal/real 与 paired_ideal/paired_real 四个 hit_rate 及 sample_count、分子分母。
- real.totals.uncached_tokens、hour.real_count/uncached_tokens/uncached_tokens_per_second、12 桶合计、页面四项和展开详情的文字。
- 缺失原因、定位层和证据；quality 按 field×code×role×UUID 归类，错误数和坏行数分开。

关键线索：主表读 paired_ideal/paired_real；详情读独立 ideal/real。旧报告 DeepSeek-32K run 1bb5a14b-6356-44fc-80f4-08c15fc1255c、UUID 0a5bf216-53d9-40ad-967f-49365bcd1c20 是 A740/P730/R0/E345/Q0，独立 ideal.hit_rate=0.3597190553279913、ideal_status=available。因此配对理想为空可以同时存在独立理想值，需核实际页面而非直接认定没有数据。

流式读取相关真实 CSV，审计 prompt_tokens/cached_tokens/completion_tokens 原值：空串、字面 NULL、非整数字符串、负数、溢出、cached>prompt、合法零各自计数和最小例子，同时核列绑定/规格/UUID/时间窗。不要预设某类格式已发生。

核对 CSV→records/issues→projections/API→DOM：
- R 依赖可归属及合法 prompt/cached，不依赖 request_input 编码成功或 completion 合法。坏 JSON 不能单独解释 real=0。
- cached=0 且 prompt>0 是有效零命中，应有实际重算量；无有效 R 时不可补零。全部 prompt=0 的命中率零分母与有效重算量为0要分开。
- 有请求但无有效真实字段的桶应缺失；真空桶可以为0；部分有效需显示覆盖，不能冒充全量。
- 预热冲突影响理想结果，不应破坏真实统计。实际重算按有效 R 求和，小时速率除3600，核12桶守恒。

原数据缺观测、解析适配、回放、聚合、API和渲染分别给证据。不能用独立理想填配对指标、用模拟值填实测、用 null 填0；原报告“无实测命中观测”的说法必须重新验证。

五、在已测预算内研究 tools/messages

深度研究限以下已有用户指定范围，其他 APPID 只做量级清点：
DeepSeek：
- S00000000000000000000000000000773（旧报告1047条）
- S010320（1038）
- com.huawei.ipd.tianzhou.ai（864）
- com.huawei.mbs.ilegal.ioc（661）
- com.huawei.newalliance（104）
Qwen：
- app_000000030502（905）
- com.huawei.aidp_dg06（171）
- com.huawei.meca.admin.digital（51）
- S00000000000000000000000000000773（54602，仅 low_hit）
- S00000000000000000000000000001679（52098，仅 low_hit）

本轮不重跑这10个正式任务。两大 Qwen 可读取既有 Token 结果并做通用结构/low_hit研究，但不新增 T2–T4 扫描或评估；当前产品强制 Token 的能力限制不能扩大用户选择。

“Qwen/DeepSeek 不是典型 agentic infra”是待验证假设。按真实 APPID×模板族识别单轮/多消息、显式 tool/function 协议、普通消息内结构化上下文、工具调用/返回关联和可用会话证据；模型品牌不决定工作负载。无关联证据时不能宣称历史被改写、发生重试或 agent loop。

分层样本覆盖长度/深度/工具形态长尾及正常对照，记录抽样规则、种子、样本量/分母与实际成本；探索样本与留出验证样本分开，不能只研究最初保留的100条 findings。

研究候选：
1. 工具定义/Schema负担和同工具变体，区分合法版本/权限差异。
2. messages 模板混杂、稳定前缀与变量位置，先分业务族再对照。
3. 普通消息中非重叠重复内容/文档，区分正常引用、few-shot及必要历史。
4. 普通消息内 JSON、数组、检索片段、工具样式文本的结构与负担，不把它们自动当真实工具返回。
5. 更广运行元数据/动态ID模式，区分业务必需字段，不泛化为删除ID。
6. JSON转义、嵌套序列化等表示开销，说明语义与模板等价性是否有依据。

对照实际探测器：L1模式和角色范围有限，L3偏工具description；L4消息差异尤其 needs_association 不是动态字段根因或浪费证明；现T3重复组要求至少一个tool_result；T1已退出，不能自动恢复。检查适配缺口、召回粒度和预算截断是否比“增加探测器”更优先。

每个候选必须给真实最小疑似正例、近似但合法的负例、文件SHA/逻辑记录号、现规则输出或未覆盖原因、适用分母、成本、误报风险和后续验证办法。未人工标注不编准确率，未全量检查不编全量覆盖率；没有得到业务确认的样例标为候选，不宣称已证明异常。

本轮只产生研究建议，不实现探测器、不改recipe、不删改消息/工具内容、不做改写后收益实验、不新增L/T编号。字节、LCP或消息差异不能直接当可节省Token；未来收益实验需另行安排并复用统一编码/缓存口径。

六、最终只回传一份 Markdown

唯一交付文件：HUAWEI_V2_INVESTIGATION_REPORT_20261103.md，保存到实际现场项目的 docs/huawei/；若同名文件已存在，保留原件并用实际日期/序号生成新名字，在回复中给出准确路径和 SHA256。

正文必须能够独立复核，依次包含：
1. 实际日期/session ID、执行范围、版本/镜像/服务/源码/资产身份与资源。
2. 21文件清单、数据量级/拒绝原因、各研究范围及完整预算表，标清实测、抽样估计和未知。
3. 三项问题逐项的入口、步骤、预期/实际、API/DB/DOM证据、关键源码、已证实根因/待证假设、影响范围、修复建议与必要复测。
4. MA全部UUID矩阵；异常任务完整ID/发布/读取链和规则覆盖；多模型数据/运行映射及入口对照。
5. tools/messages工作负载结论、候选探测器正反例、现规则适用/遗漏、成本和优先级。
6. 按前端、用户监控、MA、公共分析、低命中、Token后端归口的后续建议、待用户决定项与证据缺口。
7. 产品源码/配置/原CSV/已发布结果未被本轮修改的核对；本轮新增研究文件清单和脚本关键逻辑，明确“未实施产品修复，暂无修复后结果”。运行中日志/WAL自然变化要与本轮写入区分，不能伪称所有运行态文件逐字节不变。

关键源码片段要标实际文件、函数/行号和对应版本/SHA；关键统计脚本/SQL、实际命令、退出码、输入最小片段、HTTP响应和日志直接放正文代码块，保证足以复核结论。所有表格须定义分母，必要响应保留身份、状态和精确数值。

不得以“见items”“见日志/附件/截图目录”替代关键证据，不另交证据压缩包或第二份报告。现场中间证据保留即可。需要页面证据时嵌DOM/可见文字和网络数据；截图如使用必须直接嵌文档并附文字说明，不能依赖外部图片文件。仅有本机路径或SHA不足以支持关键结论。

正文仅嵌解释问题所需的最小真实片段，敏感内容用稳定代号脱敏并注明；脱敏文本不能冒充精确Token/LCP测量输入，不暴露凭据。将实际执行、推断和建议清楚区分，不虚构修复diff、复测或用户验收通过。

完成后只提供这一份Markdown及其准确路径、SHA256，由用户转交开发机审查session复核；不要自行向其他session或外部服务发送报告。

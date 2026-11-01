# 低命中率分析后端详细设计

> 当前有效版本prefix-design-0.2见[本轮修订](DESIGN_REVISION_20261031.md)。本文0.1作为基础技术描述；其中动态字段仅建议、单阶段评估、逐次显式启动及展示规则等不一致内容已被覆盖。完整请求样例见[FULL_REQUEST_COMPARISON_EXAMPLES](FULL_REQUEST_COMPARISON_EXAMPLES.md)。

版本prefix-design-0.1，2026-10-31，技术设计待评审；产品v0.4已获批准。本轮源码只读取证，未实现。范围L1–L5，公共能力另见[公共接入草案](../analysis/BACKEND_COMMON_CONTRACT_DRAFT.md)。

## 1. 已核对的实现基础

源码工作区HEAD为ac0699863a4dbe5824862d9d3c1b64a7ecd48d50；共享目录可能有未提交修改，具体读取文件摘要见[源码核对清单](SOURCE_REVIEW_20261031.json)。版本仅说明读取时身份，不表示诊断已存在。

| 现有能力 | 实际符号 | 设计结论 |
| --- | --- | --- |
| 发布结果/请求定位 | MonitoringViewService.group/request_identity/original | 可复用控制身份、原文读取方式；worker批量读SQLite，不经HTTP逐条下载 |
| 用户服务绑定 | UserRunService.receipt/index | 可把user_run定位到base_run、common_name和索引revision；MA不进入本线 |
| 原文及有效编码记录 | request_records JOIN encoded_requests | scope以appid与time_ns/index限定；hash_id不是唯一请求键 |
| 快速/详细编码 | ModelEncoder、EncodingBatchService.encode_batch/explain | 复用原profile/资产；explain提供渲染offset但原JSON归属unknown |
| Token分片 | TokenSlice、read_slice | 校验摘要读取IDs，不全量常驻内存 |
| 理想命中策略 | make_strategy/FullBlockStrategy/PrefixLedger | 可为目标appid窗口独立建立账本，禁止改源库 |
| 任务集成 | Dispatcher.register及worker.lock | 拟注册独立分析processor，源监控和MA/用户任务语义不变 |

重要事实：validate_request要求非空messages，当前非Responses原生协议。Qwen/GLM模板传入messages和tools，顶层instructions不会自动变成system。公开cch案例中的instructions只支持机制依据；首期只在当前支持的messages文本位置识别等价误注入。仅含instructions/input的原生请求不会被本线悄悄转换重算，新增协议适配不在本期范围。

现有user-v2/evaluations是TTFT公式评估，不具备输入修改回放语义。现有monitoring.replay会更新store中的encoded_requests，不能对源封存store调用；公共封装直接复用make_strategy执行。

## 2. 模块划分（拟新增）

- analysis_common：范围/源身份、只读source reader、编码桥接、结构修改、评估封装、任务存储与发布，主会话唯一维护。
- prefix_analysis：结构指纹、历史候选索引、原字段/IDs比较、L1–L5探测、证据归组及本线修改方案。
- api/diagnostics.py：新命名空间装配提案；app.py/cli.py仅注册，实施前登记共享窗口。
- tests/unit与integration下对应目录：规则反例、差分与任务恢复；真实模型资产测试和合成测试分别记录。
- 不新增HTTP进程，不修改已有S0或source数据，不改前端。

Token线通过公共RequestView/Observation/ModificationPlan接入，不依赖prefix_analysis内部类。共享类型和副本操作由公共草案收敛，未冻结前不宣称接口已可调用。

## 3. 输入范围与工作流水线

1. 解析user_v2/base来源，读取真实base身份，校验发布/源seal；固定appid、模型服务、窗口与记录键集合。
2. 只读游标按(time_ns,source_record_index)迭代有效编码请求。每条读取原文/轻证据，IDs按需读分片并校验。
3. 建立结构索引，查询仅包含更早请求的历史候选；先查询后插入，不允许当前请求命中自己的对照。
4. 对候选做字段差异和IDs LCP比较；执行适用L1–L5，收集所有观察，不首命中停止。
5. 对选中证据做原字段到模型输入的参与核验；无法证明精确映射则降级，保留冲突/未解释因素。
6. 按位置/机制/工具定义组生成业务发现和可明确的修改方案；事实和待评估收益分开。
7. 封存报告并发布。用户后续显式创建/执行评估，页面GET只读取已保存结果。

## 4. 候选检索与覆盖

不构建N×N请求对矩阵，也不假定整个appid为一个会话。结构指纹用于检索，原字段比较才是证据：

- 索引键包含服务/编码身份、effective_options摘要、协议形态；不同选项的请求不作为同构原因对照，但仍各自参与原窗口缓存计量。
- 工具集合指纹：唯一身份+定义，保留数组值顺序；工具排列指纹另存，不把两者混为一个hash。
- 消息骨架：role/content形态、tool调用结构；不把调用ID当真实全链路session身份。
- 稳定字段指纹：允许仅对已知动态元数据槽位生成检索掩码；不能广泛mask所有数字/路径后宣称同语义。
- 输入公共前缀可作为额外候选检索线索；这里只检索对照，不生成或复刻缓存命中算法。

候选通道优先用实际可用的可靠关联，其次精确结构/工具集合与稳定文本；本期可靠关联默认缺失，不能虚构。各通道输出前序候选键、召回理由及覆盖，按共同结构证据、实际LCP、原时间/序号确定性排序；同分/互相矛盾参照保留，不挑单一对照掩盖其他因素。

候选数/深查请求数/输入字节及编码次数均为配置预算，保存实际值、截断和未检查数量；值在实现性能样本后校准，不作为业务异常阈值。任何上限导致部分检查时报告partial/预算耗尽，而非无异常或全局最佳前缀。

索引落地到临时SQLite，保存hash与请求键引用，不保存全部IDs副本；有界LRU读取相邻比较IDs。深度解析/正文超出预算时给具体降级原因，不静默截断后作完整内容相等判断。完成产物记录算法版本，后续改变候选策略需保留版本。

## 5. 输入参与与位置证据

只有原字段差异不够证明缓存影响。分三层记录：

- source_difference：JSON Pointer、原值/结构、相同/不同位置。各坐标单位明确。
- input_difference：原IDs共同前缀/首个不同Token或end_of_sequence；H独立显示。
- participation_check：该字段是否进入当前模型模板、能否连接到输入差异。

只在显式后台分析中复用ModelEncoder.render与EncodingBatchService.explain。唯一字面片段且渲染证据无歧义时可给位置候选；重复片段、转义、多次展开不能靠首次substring命中就标exact。

对无法直接定位的可修改字段，可在隔离副本上进行单字段探针：只替换目标为合法的同类型标记或实际候选值，经同一模板/编码比较。探针只证明该字段影响输入，不证明业务等价、原始精确Token归属或其为唯一原因。原始与探针digest分开，探针结果不进入收益/源指标。

如果改动触发模板条件分支、多处变化或无法合法编码，参与状态为partial/unknown；不能给精确连接线。字段不影响IDs时标无缓存影响。将已知cch清理形成可执行方案，不需以探针替代真实删除副本评估。

## 6. L1–L5技术落地

| 规则 | 输入/匹配方式 | 输出与修改 |
| --- | --- | --- |
| L1 | messages的system/developer文字或明确text块中识别已知元数据首行；具体路径/头名/字段schema匹配；前序同槽位不同值，后部稳定内容及输入参与核验 | 已知误注入cch清理为准确字符串范围操作；其他时间/业务字段只给动态前置观察，移位需明确位置；单请求仅给已知元数据存在事实 |
| L2 | tools必须有可唯一识别的type/function.name，逐项完整定义多重集合相等但数组顺序不等；定义比较保留数组顺序 | 固定身份键UTF-8字节排序，保留完整定义和数量；重复名称/冲突身份不可自动排序；集合变化交L3 |
| L3 | 同身份工具的字段级diff、集合增删；运行元数据槽位需来源规则证明 | 给准确增删/Schema路径，不判合法版本变更为错误；明确元数据清理可引用L1方案，其余只建议或要求标准值来源 |
| L4 | 若有经验证的关联，比较旧messages与新messages的既有位置；排除仅追加后缀、模板末尾生成标记变化 | 当前缺关联默认仅结构差异，不输出同session改写；不能自动恢复旧历史。明确关联与追加规则后才建移动方案 |
| L5 | 只对已声明JSON格式的字符串字段解析，拒绝重复key/非有限值；值类型、数组次序相同，允许对象key排列/空格差异 | 在限定字段内确定性序列化并验证解析值不变；代码/Markdown/签名字节不处理；外层JSON不同而IDs相同则非低命中 |

L1不支持“任何叫cch的字段都删”；注册规则包含id/version、适配协议、允许位置、头部语法、原值guard和公开依据。只有被明确认定的误注入场景标业务信息无损。L2不排序tool_calls或messages；L5不将numeric字符串变成数字，不以JSON标准化掩盖已知业务差异。

每规则状态包含结构条件、模板参与、前序可比性和修改适用性。非最早变化仍可观察，但不能直接归因全部C。首期不引入LLM判因/语义相似裁剪，避免在无证据时生成确定原因。

## 7. 归组及业务证据

Observation键包含当前RequestKey、规则版本、具体位置、参照key与差异类别；Finding按动作位置/机制/工具定义版本归组，L1与L3同一动态description可关联一张卡片。对照锚点不加入涉及当前请求数，修改范围可包含锚点。

保存代表/冲突对照和每条规则检查记录；卡片不吞掉“无干净参照”“候选歧义”“未核验模板”。事实confirmed不等于低命中原因已量化；结论用输入构造问题/优化机会/需证据，评估另外显示。

一条观察若既是内容负担又是前缀差异，可被两个页签引用，但同一方案只保留一个id。总览请求取并集，不相加C或收益。技术详情可引用原CACHE_LOOKUP事件解释MTP，业务首页不要求用户改模型参数。

## 8. 离线评估接入

使用公共草案的SourceSelection与Plan。原运行模式核对原IDs/P/J/H/C；子窗口新建同范围空基线，不能要求H/C等于原完整run。

每条修改先过原值guard、非目标结构不变、validate_request及原profile选项保持检查，再复用encode_batch。未修改请求保持原字节，已有IDs可复用但基线身份核对不能跳过。前后相同排序调用make_strategy；不复用已经写入过的ledger路径。

不能以新原文J更短判断P更短；P/H/C均用实际统一编码/回放。目标失败使方案blocked，after不发布；合法不适用记录计数且保留。组合处理明确次序/冲突，不能把单项LCP改变量或单项收益加总。

## 9. 任务/API/产物

共同任务、HTTP、manifest与恢复由公共草案统一。低命中方向通过direction=low_hit和L1–L5版本选择，不能把产品用户需要的内部模型设置暴露为可任意覆盖参数。

默认提交全部本期规则，按能力显示不适用/输入不足；规则次序只记执行追溯，不作为原因优先级。部分发现可封存为partial报告。每次显式重新分析/评估产生新任务/attempt与源身份，不在读取时补算。

暂不修改既有signals消费者行为，不默认自动消费monitoring outbox；产品只承诺显式分析/评估。没有前端开发、容器/现场部署或在线prompt修改。

## 10. 验证与实施准备

详细验证清单见[TESTS](TESTS.md)，预期源码位置见[CODEMAP](CODEMAP.md)。先锁定公共逻辑契约、源读取/回放等价性，再实现独立规则和任务/API。具体开发batch另行形成，本轮不把技术草案写成开发计划已批准。

待技术评审收敛：新HTTP路径与任务状态、公共Plan操作和Token线接口需求、预算配置及性能验证方法、现有CPU预算约束。产品范围不重开，当前确认不足的能力按设计降级，不扩大为新协议/新trace支持。

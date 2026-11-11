# V3 测试与统一验收（r1，评审修订）

**当前范围决定（2026-11-11）：显式 full 延期（DEFERRED_BY_USER，未实现/未运行，不记PASS），不再是本期V3门禁；自动full仍禁止。候选repair-r1-02为LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING，独立R2已关闭RV3-01/02/03。大源自动缩样和五组session_clock样本参考率优先，真实BUS01–05及现场AC-MEM待华为验收。暂不打包。**

2026-11-11修订。本文是面向开发agent的验收规范，不是测试运行日志；已执行结果见各批TESTS及[本地收口](LOCAL_ACCEPTANCE_CLOSE_20261111.md)。本地工程已独立验收，真实T29/T30及BUS仍NOT_RUN。与[DESIGN](DESIGN.md)、[批次计划](BATCH_PLAN.md)一并评审；原始回传与算术核对见[证据核验](EVIDENCE_REVIEW_20261110.md)。

## 1. 门禁原则

- 用户两条底线与五组精确对象见[ACCEPTANCE](ACCEPTANCE.md)，是硬门禁，不能以安全失败或旧报告数字替代。
- 每批先固定源基线、设计版本、受影响文件、fixture/模型/配置身份和测试命令，再实现、测试、修复、复测、关闭问题、写CLOSE与记忆，才进入下一批。失败、跳过、环境缺失与未运行分别记录，必需用例不是PASS就不能关闭。
- 禁止降低旧门槛、删旧断言、忽略异常或把合成/Mock/browser harness当真实编码或真实后端验收。测试合理更新必须指出批准的新旧语义差异，旧读取/冻结契约断言继续保留。
- 单元边界用小预算和确定性替身；源码端到端用真实候选后端、统一编码/模拟、本地固定模型资产、真实浏览器。硬资源/取消必须在真实受控进程上测，不能只monkeypatch一个计数器就宣布通过。
- 两报告给出场景，不提供已验证golden收益。未有合法业务删改依据时，证据/假设和无收益是合法结果；不能要求五个指定业务都达到90%或复制12–39pp；五组必须有真实参考数值，零/负值如实呈现，不能以“不保证收益”为由省去评估。
- 本机最终验收使用明示合成数据；华为真实验收另需授权，沿用现场规则、SSH18002与单Markdown回传，Token休眠覆盖旧流程里默认“两方向全跑”的历史安排。

## 2. 固定fixture目录设计（实施时创建）

新增fixture源码建议放`tests/fixtures/development_v3/`，生成数据与运行输出放`artifacts/validation/development-v3/<batch>/<attempt>/`，不进入Git。每个fixture登记生成器版本/seed、请求键/顺序、预期分类、A/B角色、负例及模型配置身份。不得复制真实请求正文或把脱敏片段当真实重编码基线。

| ID | 必须覆盖的结构 | 预期用途 |
| --- | --- | --- |
| F01 | 相同长静态前缀，ISO/斜杠/中文时间分别变化；system/developer字符串及内容块；同一字段可比但后续历史轮次、user/assistant/tool序列不同；A/B独立连续窗口 | L1定位、候选、冻结改法及两窗回放；每格式有至少一组原Token确实分叉的真实编码样例。 |
| F02 | 固定日期、业务依赖时钟、文档历史日期、路径内日期、不同长度workspace、时区/结束标签、多个/嵌套/缺失clock块 | 必需负例、重叠消歧；无法识别明确标unknown/unsupported，不误报业务无损。 |
| F03 | 三种以上不相干结构；大量重复差异；晚出现稀有时钟组；相同工具集合乱序、工具增删/定义漂移、description动态字段 | 同预算候选覆盖及L2/L3保活；小fixture用独立穷举oracle标注应覆盖原因，产品算法不做全比较。 |
| F04 | 请求数、UTF-8 bytes、累计P、深度/节点、比较、plan、编码调用/输出Token和磁盘恰为limit−1/limit/limit+1 | 准入及超限，无越界物化/错误完整收益。 |
| F05 | 大来源中固定小窗口；窗口外超大正文；相同时间戳、重复hash_id不同key、窗口内一条超长/缺slice；空appid | 区分源准备成本与小样本读取；同时间稳定排序、无静默跳行拼接。 |
| F06 | 阻塞hash/read/parse/encode、取消竞态、子进程失败/强杀、磁盘满、journal半写、重启、重复提交 | 真实监督进程止损、已封存证据可读、半成果不可见、API可响应。 |
| F07 | 无clock的短问答、200K字符单tool、270+messages累积、长system/assistant；多模型配置 | 来自新报告的压力/合法负例形状；不检测T2–T4，不把字符数推成Token占比或必出L1。 |
| F08 | 原文/资产/encoder/配置/manifest/slice被改、跨scope引用、越界路径、JSON数值词法、重叠修改、不合法工具协议 | 来源与改法guard、协议合法性、失败不漏原文、不发布after。 |
| F09 | no-op、matched=0、matched>0但modified=0、实算零/负收益、A有收益B无收益、B不适用/不足/缺失、只覆盖整个scope的A | 状态闭合、P/H/C可复算、B不能调参，不自动full。 |
| F10 | V1/V2 ready/partial/not_computed、有Token旧成果、缺字段/可恢复读错误的隔离历史副本 | 旧schema/默认选择/固定历史/四入口/L4L5兼容，旧原件SHA不变。 |
| F11 | 所有新/旧submit、retry、evaluation、combination、authorization及服务重启队列入口 | Token休眠与旧自动full不能绕过；浏览GET产生任务数=0。 |
| F12 | 原用户监控/MA/搜索与排行回归固定输入；版本/HTTP资源身份 | 共有层无旁路回归、四入口与批准视觉保持。 |

F01/F03的正例必须预先保证适用，不能在测试后替换成刚好有收益的样本。跨模型收益数值可不同，比较变换正确性/计算一致性，不强求相同pp。

## 3. 可追踪验收矩阵

“新增测试”是建议落点，不是已存在文件。每批TESTS.md必须把下列ID映射到最终pytest/vitest/playwright node ID及真实日志，便于总检复查。

| ID / 设计 | 所属批 | 操作与可判定通过标准 |
| --- | --- | --- |
| T01 / D2 | V3B001 | HTTP快速登记并自动进入有界prepare；不因父scope大而拒绝，不在HTTP路径hash/加载tokenizer。流式校验I/O单列，诊断不再全源verify；大源缩样后完成。 |
| T02 / D2 | V3B001 | 选键前无正文SELECT *；超长记录在完整Python字符串/JSON/token数组构造前拒绝。已选/排除/总数守恒，同时间与重复hash_id不丢请求。 |
| T03 / D2 | V3B001 | A/B成员不重叠、顺序和digest固定；发现阶段B正文读取计数=0；窗口内缺一条则不产“连续窗口收益”；整个scope可作为A。 |
| T04 / D2,D8 | V3B001 | 来源在校验/复制中变化、错SHA、缺slice、越界引用均fail closed；未封存快照不可消费，源原件前后SHA不变。 |
| T05 / D7 | V3B001 | V3新schema合法/非法例、整数wire、scope/ref一致性通过；V1/V2现有manifest与schema不变。 |
| T06 / D3 | V3B002 | 各预算limit−1/=limit/+1通过；总比较≤任务上限，各通道/总量与日志一致；after超Token输出不发布完整收益。 |
| T07 / D3 | V3B002 | 正常循环取消、阻塞编码/读取强制停止均符合§4时限；取消与发布竞态得到唯一终态，无孤儿worker。 |
| T08 / D3 | V3B002 | 已提交检查点可封存partial；半写/磁盘满/崩溃不能暴露未提交对象；失败窗after为空，A已完成可保留。 |
| T09 / D3 | V3B002 | 重启不重跑旧working；retry新身份保留旧产物；幂等同意图相同receipt，冲突意图409；实例身份错误拒绝。 |
| T10 / D4 | V3B003 | 正常诊断自动识别三种时间格式/clock，不注入recipe或finding；结构块与多槽精确指针/区间/片段及请求对；同字段clock变化且后续历史不同的正例自动命中，仅预期时间发生变化；不同长度path及已有CCH不回归。 |
| T11 / D4 | V3B003 | 固定时间不报变化；非法/嵌套/缺失块不扩大删改；路径内日期/直接user历史不盲改；业务依赖时间必须标语义影响，不自动采用固定化。明确禁止反事实时不运行。 |
| T12 / D4,D8 | V3B003 | 自动L1 finding带出固定化改法，保存finding/请求对/字段/recipe关联；指定反事实另测且不能替代自动链路，无合格证据不造L1；必做固定整个session_clock内部为同一NORMALIZED，普通日期槽删除不能替代；块外内容不误改，匹配/修改集合精确，guard失败无after；no-op原raw保持，协议/数值词法安全，LCP用真实IDs。 |
| T13 / D5 | V3B004 | F03同一确定预算下包含全部预标必需稀有原因和L2/L3通道；同system/developer字段可比、后续历史长度/角色序列不同仍入L1比较，固定clock/clock外模板不同/字段不兼容不强并；相比V2基线不增加预算，覆盖改善/持平与失败原因逐项留证。 |
| T14 / D5 | V3B004 | 同输入/seed/profile候选顺序与原因组稳定；物理pair无重复计费；相同原因反复出现不占满唯一原因名额；不做组内N²枚举。 |
| T15 / D5,D7 | V3B004 | 组成员精确去重/超限明确下界，观察/验证/保留/已扫描分开；未知上下文不强合并，L4/L5证据仍可读。 |
| T16 / D6 | V3B005 | A/B各自before/after键、顺序、计量配置一致；A/B ledger独立；每行C=P−H；整数/有理数结果与独立计算核对。 |
| T17 / D6 | V3B005 | B使用A冻结的transformation_digest，修改B不会改变A候选/recipe；无B/B不适用/B失败不冒充复核通过。 |
| T18 / D6,D7 | V3B005 | F09所有状态从experiment→outcome→API保真；无收益≠无适用≠未评估≠超预算；P=0无伪比率。 |
| T19-A / D6 | V3B005 | 本期必需：自动full入队/调用数=0；旧full门槛/旧读结果不改，旧写路径不得绕过V3保护。已有本地及独立R2证据。 |
| T19-B / D6 | 延期 | 原T19显式full部分：DEFERRED_BY_USER（2026-11-11），未实现/NOT_RUN，不计PASS且不阻断本期。未来须新范围/预算/prepare身份，不能复用pilot冒充full。 |
| T20 / D7 | V3B006 | Token所有新执行入口明确休眠，旧Token报告完整可读；旧queued/retry不隐式启动；缺bundle不阻塞low_hit-only。 |
| T21 / D7 | V3B006 | V3/legacy客户端按version分派；错scope/错分母/错摘要/整数溢出拒绝，不能放宽旧校验；历史缺字段保持unknown。 |
| T22 / D7 | V3B006 | 页面显示A/B范围及N、P/H/C、零/负/未完成原因；L4L5主体和四入口保持。浏览/翻页/刷新/历史/重连产生POST任务数=0。 |
| T23 / D7 | V3B006 | 完整报告默认优先与固定历史保持；取消partial不抢默认；断网/空目录/读失败不清掉已读结果或补跑分析。 |
| T24 / D0–D8 | V3B007 | 从新空state生成合成监控源→prepare→正常诊断自动L1发现→固定化改法→A/B→封存→真实浏览器，提交不含clock/recipe/finding预指定，身份全链对应；按§5重启后复核。 |
| T25 / D3,D8 | V3B007 | 真实隔离进程通过§4预算/内存/时间/磁盘和健康检查，有限增长实验无不可解释超线性成本；停止后无残留。 |
| T26 / D7,D8 | V3B007 | 冷启动/恢复、历史隔离副本读取、Token休眠、四入口、监控/MA/统一编码关键回归全部通过。 |
| T27 / D0–D8 | V3B007 | 逐设计条款列实现函数/测试/证据/偏差；全部必需条款有证据，无未关闭阻断或误标PASS的skip。 |
| T28 / D8 | V3B007 | 全套ruff/mypy/pytest及viewer typecheck/lint/vitest/build、相应用例的真实浏览器校验完成；源码候选身份/dirty归属/旧契约SHA留证。 |
| T29 / AC-MEM | V3B007 | 大源及五组目标负载无需用户调sample_limit即可自动缩样，得到可用诊断/参考值；OOM/mem_limit/内存kill=0，只给预算不足不通过。 |
| T30 / AC-CLOCK | V3B007 | BUS01–05每组真实来源经正常诊断自动L1发现clock、定位请求对/字段并带出固定化改法，在前端有问题证据、实算A/B参考值和业务说明；预指定clock实验不算自动门禁通过；页面数字与同一封存evaluation一致，报告旧数/合成fixture不能替代。 |

## 4. 资源与响应门槛（已评审工程目标）

这些是**工程验收目标**，不是从华为报告推出的生产承诺。不冻结300为默认，也不自动采用现场8MiB/250K/retain_last=3。自动profile明确记录全部预算及缩样算法；用户不必提供sample_limit。B001记录、B002实装并校准、B007复测。缺硬限制的平台不得跳过后宣称通过。

- 数量/字节/比较/调用/plan/磁盘等可预知预算：执行动作前检查，已计费消耗不得超过上限；一个新动作超限应不执行。编码实际Token未知时分别记录预算预估、实际输出与超限结果，单次编码受时间/内存隔离保护。
- 响应性建议：在约定本地验证profile、单诊断负载下，连续至少20次health/receipt请求各自P95≤1s，全部成功；P95用排序nearest-rank，并记录原始延迟、CPU/模型加载阶段。服务健康不得依赖同一被阻塞worker。
- 取消建议：取消HTTP返回≤1s；发出后≤5s结束本任务子进程树或进入已成功提交终态，父API持续响应；deadline也在到期后≤5s完成止损。不得以“以后遇到checkpoint会停”替代测量。
- 内存：记录OS硬控制类型/配置/范围及进程树实际峰值；若使用RSS硬限则不超过该限。仅支持address-space硬限时明确单位与保守性，RSS监测另列；未确认可用限制时拒绝重编码。不能用容器空闲/结束值冒充峰值。
- 增长实验：同一个已封存样本，扩大原源规模不增加诊断期源正文读取/校验量；prepare随源规模增长的校验I/O单列，不要求其O(样本)。固定N/K/预算增加重复请求时，受限比较/证据构造遵守计数上限；RSS与耗时曲线记录，不把O(N²)通道藏在预处理。
- 磁盘/停止：上限耗尽与disk-full都能结束；原source/旧state/已封存结果SHA不变；只有当前attempt的未封存临时目录可清理，归属/真实路径核实后才删除。
- profile量值及平台须在测试前记入TESTS。首次平台不满足上述目标就记录阻断与证据，评审调整目标，不先测后悄悄降低门槛。

## 5. 最终E2E、健壮性与设计复核流程

V3B007必须按[冷启动流程](../../architecture/TASK_SESSION_WORKFLOW.md)执行，B006如提前做真实新版本E2E也遵守；仅单元/组件测试不等于E2E。

1. 盘点本项目Windows/WSL前后端、worker、预览和测试容器，核PID/工作目录/版本/端口；停止明确归属的旧TokenScope进程，确认退出/端口释放。保留旧包/state/日志，不误停兄弟项目或Docker daemon。
2. 固定候选源码摘要、frontend dist摘要、依赖/模型资产身份，创建项目内独立新state和新浏览器context。不得复用旧dist/localStorage或换端口保留旧版并行验收。
3. 从候选源码启动唯一环境，用F01/F03/F07等合成输入通过真实监控产出源，再走V3 API全流程。记录service_instance_id、URL、PID、source/sample/plan/evaluation/report摘要及HTTP资源身份。
4. 浏览器读真实报告验证T22/T23和四入口，截图与批准HTML按固定身份对照；不是将fixture直接灌入前端。浏览器harness结果单列。
5. 用独立attempt测试取消、deadline、资源耗尽、磁盘满、崩溃重启、幂等、混合成功/失败；恢复场景与首次冷启分开。历史读取只用原件隔离副本，原件不可写。
6. 运行总回归与健壮性检查；与D0–D8逐项对照，把任何实现偏差回到拥有该功能的批次ISSUES并修复后重跑受影响门禁，不能在最终文档里掩盖。
7. 关闭工程阻断，形成候选、测试与设计追踪表、已知限制、资源范围、回退和交接清单。结束时停止临时进程，说明保留预览。五组真实数据不可得时只能LOCAL_VALIDATED，V3B007与用户底线保持待现场验收；经另行授权取得真实证据再关闭，不能把合成E2E称BUS通过。**源码验证不等于镜像/华为/人工验收通过。**

华为阶段后续另按[交付规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md)由用户授权安排；本方案不授权现场操作或打包。

## 6. 命令落点与记录要求

以下是原计划的命令示例，不代表当前执行记录；实际运行以各批TESTS为准。不得原样重用已存在的attempt输出路径。工作目录`/home/zhangxiyue/TokenScope`；每次basetemp用新的attempt路径，不覆盖既有证据。

```bash
.venv/bin/python -m pytest tests/unit/analysis_common tests/unit/prefix_analysis tests/integration/analysis tests/integration/prefix_analysis --basetemp=artifacts/validation/development-v3/V3B007/attempt-01/pytest -q
.venv/bin/ruff check src tests
.venv/bin/mypy src/tokenscope
.venv/bin/python -m pytest tests/unit tests/integration --basetemp=artifacts/validation/development-v3/V3B007/attempt-02/pytest -q
```

最终完整pytest包含Token历史回归，是隔离fixture/旧契约验证，不在新产品入口或真实数据上恢复Token诊断。源码验收之前核实际环境/测试副作用及资产可用性，缺依赖记阻断，不运行自动下载。每批只跑自己的针对性集合和受影响回归，不反复全套制造日常开发成本。

viewer工作目录`/home/zhangxiyue/TokenScope/apps/viewer`：

```bash
npm run typecheck
npm run lint
npm test
npm run build
npm run test:browser
```

最后一条默认启动harness dev server，**不能当唯一真实后端E2E证据**。真实候选E2E须在已核唯一候选URL下设置TOKENSCOPE_EXTERNAL_PREVIEW=1和TOKENSCOPE_TEST_BASE_URL，选择真实后端用例；记录最终确切命令。现有`scripts/validation/analysis_frontend_server.py`使用历史setup及旧两方向流程，不直接拿它当V3启动器；需要在V3B007新增/适配受控合成验证入口并记录源码。

每条记录至少：测试ID、命令/cwd、时间、候选SHA/工作树清单、依赖/资产/profile摘要、fixture/sample身份、预期、实际、退出码、pass/fail/skip数量、日志/截图路径、关联issue、修复及复测证据。没有执行时写NOT_RUN，禁止提前填通过数。


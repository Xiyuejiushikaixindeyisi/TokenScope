# C01–C04 开发执行记录

用户已批准开发方案，授权顺序验证闭环后自动推进；不打包。

证据根：`artifacts/validation/development-v3/repair-c01-c04-20261111T184136`。每次测试使用新文件/独立tmp目录，旧证据不覆盖。

## C01 — 进行中

### 代码方案
执行已批准C01：64条确定性合成输入；在昂贵读取前缩样；默认单样本；移除硬性时间终止，保留取消及内存/磁盘控制、历史配置读取。

### 问题记录
- C01-I01：现有总时限、模型60秒、目录10秒及RLIMIT_CPU与批准范围冲突，修复中。

### 测试记录
尚未执行。

### 闭环
尚未通过，不提前进入C02。

### C01 最终闭环
- 新profile `sample-runtime-3.2` 默认单样本，≤300条/64MiB/400万prompt tokens，单条≤8MiB/50万tokens，并取实测模型余量下更小值。历史3.1可读，执行不再以时间字段终止。
- 移除总/阶段/目录扫描硬时限和衍生RLIMIT_CPU；保留取消、内存、磁盘和进程清理等待。
- 64条长输入生成器输出排他目录，重算字符区间、SHA；五业务实际模型编码均完整通过。
- 测试 `c01-01.xml`：59 passed；`c01-02.xml`：5 failed（新增测试误用resolve方法名，非产品失败）；改用resolve_scope后 `c01-03.xml`：5 passed。Ruff首次4处长行失败，格式化后通过。
- C01-I01已闭环。C01技术门槛通过，进入C02。前端、全链路和大规模验证尚未通过，不代签最终验收。

## C02 — 进行中
### 代码方案
复用检测器，单样本完整计算；一次验证/重放基线，逐方案独立after；按实际已发现方案量确定累计工作预算，保留内存/产物上限；报告/精确证据可追溯且只读。
### 问题记录
- C02-I01：现有每方案重复基线编码及固定plans32/checkpoints128等累计预算，会截断合理多方案。
- C02-I02：原报告反复内嵌长raw且证据四分之一metadata上限可能排挤L1，需有界任务内证据读取。
### 测试记录
尚未执行。
### 闭环
进行中。

### C02 最终闭环
- 一次基线编码/重放复用样本磁盘Token，逐方案独立after；累计工作预算按实际发现方案数计算。方案失效/计算失败保留明确状态，不填0。
- 新报告追加evidence_mode/evidence_refs，原3报告缺省inline继续可读；样本执行阶段生成并hash封存精确双边/修改后局部证据，GET只读已封存对象。没有新增任意路径或GET分析入口。每个可执行建议一个代表例，L4/L5各至多3个代表组；影响成员数独立。
- 扩展目录只追加有界样本元数据，不预载全部报告/正文；合成标识来自输入显式synthetic标记，非模型/appid推断。
- `c02-01.xml`五组后端5 passed；`c02-02.xml`67 passed/20 failed：旧全文/双窗口断言及测试执行期间修改契约导致父/子模块身份不一致（流程问题）。更新对应新语义断言，冻结测试期间源码后`c02-03.xml`87 passed。后续不在相关测试运行中改其源码。
- `c02-04.xml`3 passed：真实34方案/超过128检查点与V2/Token旧读；`c02-05.xml`1 passed：typed只读证据API修改后复验。类型检查和本批Ruff通过。已有第三方httpx弃用warning保留，不影响结果。
- C02-I01/I02关闭。五组完整主样本，clock外字段保护、同样本守恒、基线编码计数、证据身份/损坏拒读、历史双窗口读取均通过。多模板的差异代表证据仍有公开上限，保留coverage提示，不作全候选穷尽保证。
- C02通过，进入C03；大来源资源/最终页面仍待C04，不称最终验收通过。

## C03 — 进行中
### 代码方案
在原V2目录、binding、历史、卡片/详情内接入已验证V3报告；移除独立SampleDiagnostics挂载；保持获批DEMO结构。单独V3验证器/视图适配，不将旧V2契约改为sample。正负/零/未评估分明，浏览GET不提交任务。
### 问题记录
- C03-I01：独立小样本模块与V2原布局冲突；原V2 full/>1pp门槛不适用于新样本。
### 测试记录
尚未执行。
### 闭环
进行中。

### C03 最终闭环
- 原AnalysisApp筛选/历史/卡片/详情接入独立V3校验与视图适配；SampleDiagnostics不再挂载，其独立样式移除。原V2/Token契约与读取不改，L4/L5各一张卡至多3例。
- 分页V3目录只取样本元数据；选中后读取report；证据懒加载只读。校验任务/实例/来源/模型/样本身份，GET不触发分析。新样本不走full/>1pp门槛，正负零/未评估/无适用对象分明。
- c03-01：Windows Node原生rolldown依赖不匹配，启动失败无测试执行；改用现成WSL Node22.22.2，不改依赖锁。首轮TS错误unknown作为ReactNode，改显式boolean后通过。
- c03-02：77项相关旧读/组件通过；c03-03：11项新adapter、signed gain/缺值、分页和身份测试通过；c03-04：完整前端363 passed。TypeScript、eslint通过。
- c03-browser-01：实际构建UI + 记录API fixture的展示smoke通过（不是实算E2E），1440/390截图、卡片→详情→返回、无平行模块/水平溢出/JS错误/POST；已视查desktop/mobile。c03-dist-01构建通过，保留bundle体积warning。最终scope标签文案修正已typecheck/363tests覆盖，C04新构建复查。
- C03-I01关闭；进入C04实际CSV→监控→自动分析→前端验证。人工审批仍待最终页面。

## C04 — 进行中
### 代码方案
检查旧服务/端口/容器；候选源码及dist摘要冻结，新state/浏览器冷启动。五组64条实际HTTP全链；额外L5/负例/受控取消；1200/12000长来源两模型+受限内存自动缩样；保存所有attempt、技术/人工/现场结论分开。
### 问题记录
尚在验证，不提前宣称通过。
### 测试记录
进行中。
### 闭环
未完成。

### C04-I01 — 大样本计划产物上限（已修待复验）
首轮DS1200自动缩至170条，发现与baseline编码完成，无OOM/forced kill，但plan_bytes错误复用metadata8MiB，长字段逐请求替换计划超限导致stopped。证据c04-scale-01/DS1200-execution.json，supervisor峰值约285MB（worker ru_maxrss含继承高水位，不混用）。修复为计划预算按已固定profile.max_file_bytes分配；checkpoint允许该文件上限，报告/局部证据仍保留8MiB小上限。不是放开样本或扩大内存边界。
同时修正中断可读性：初始报告保存所有已发现方案和双边局部证据，windows空表示未评估；每次after证据保存使用新sequence文件，不覆盖此前checkpoint。旧e2e-01服务已停、18002已释放；旧state/CSV/证据保留，新候选需新state复验。

### C04-I02 — 损坏后发布身份（已修待复验）
新增初始未评估方案后，损坏最终证据会回退初始合法checkpoint，但terminal目录仍称完整，存在发布身份不一致。c04-repair-01.xml的9项失败揭示该问题（其他4项通过）；额外单例定位同因。现对terminal记录的最后report SHA与可验证checkpoint SHA比较，损坏拒读409，不能悄悄降级伪装完整。不是降低测试断言。

### C04 增量复验
- c04-repair-02：13 passed，C04-I02损坏拒读闭环；c04-unit-01：公共层/低命中190 passed。c04-ruff-01/02初次脚本格式/未用变量失败，修正后c04-ruff-03通过；src mypy 143文件通过。
- 新state c04-e2e-02五组64条真实HTTP全链完成；c04-browser-02五组实际率/详情/刷新返回/窄屏/无POST通过。c04-browser-01排行地址错误，仅作旧记录，新脚本已使用users/ranking；四入口具体内容还需末轮核验。
- c04-scale-02首组DS1200→189条完整完成：prepare约276MB、diagnose约287MB，计划15.3MB正常落盘；C04-I01触发用例复验通过。其余12000/Qwen/受限内存仍运行或待执行，不提前签C04。

### C04-I03 — 大来源对照的资源条件（验证方法纠正中）
DS1200和DS12000均完整完成，但系统自动观察的address limit分别为1,749,108,940和1,966,033,305字节，所选189/212条不同。原scale脚本无条件要求selected相等不成立，不能将不同可用内存条件当等条件对照。保留该attempt/断言结果，增加同一候选、服务器停机后独占串行的2GiB可用内存观察测试；子进程仍真实RLIMIT_AS约1.30GiB，非cgroup/整机限额。复用本轮已封存监控来源，仅新增prep/diagnosis任务与新证据目录，不覆盖旧任务。两模型1200/12000需同样本工作量和有界RSS对照均完成才关闭。普通资源套件在Qwen大来源监控准备期间另以tmp_path执行；等条件资源复验将等所有测试结束后独占执行。

### C04 额外状态与大来源初轮收口
- c04-scale-02：DS1200/12000与QW1200/12000四个真实HTTP任务均completed、完整发现/评估、无forced kill。样本分别189/212/300/220，diagnose峰值287/312/532/530MB。脚本最后等样本数断言FAIL，原因见I03，不能把该脚本整体写PASS；固定内存补验已开始。
- c04-integration-01：42 passed（资源隔离/取消/崩溃/父退出、样本封存/源变更/磁盘与损坏、前缀改法/多方案、V2与Token休眠旧读）。c04-unit-01：190 passed；c04-repair-02：13 passed。类型检查143源文件与V3 schema --check通过。
- c04-extra-01：三个真实报告通过，无变化无方案、L5大整数、取消保留未评估。c04-extra-browser-01 FAIL为测试选择器错误：空方案页面没有卡片内合成标签，实际有报告级合成提示和正确空状态；改查报告级提示后c04-extra-browser-02全部通过，未改产品/输入/报告。
- c04-browser-03：五组及四入口具体标题（users/users/ranking/ma，非只等main）通过；原V2结构、页面只读无POST、真实率/证据/深链接刷新/返回/窄屏通过。
- 服务已正常停止、18002释放，c04-restart-before保留12报告全文，c04-source-before保存118个本轮CSV/监控产物SHA；固定资源补验仅新增独立任务，随后需重启对照原报告和来源不变。

### C04-I03 最终闭环
`c04-memory-01`使用同一2GiB可用内存观察值、真实RLIMIT_AS=1,395,864,371字节，四项均completed且完整实算。DS两档均151条；Qwen模型校准VmPeak为639,954,944/660,324,352字节，按原公式分别选188/182条。原测试错误地要求样本数相等（第二对FAIL）；获批门槛要求父N十倍不得造成正文/Token/候选驻留十倍，不禁止根据实测开销进一步缩样。
新增独立核验器读取上述原始profile/calibration/manifest/report/execution，不修改任何产物：逐项重算calibrated_sample并与manifest limits精确相等；验证真实RLIMIT、完整终态/无forced kill、原数据每请求字节/Token分布一致、选样字节/Token/数量不超过实际上限、编码次数=2×N、请求/正文读取≤8×选样量、比较≤16×N；两档同模型同地址限制，读取/编码/比较/RSS均未随父N十倍增长（并通过<2倍的检查）。`c04-memory-recheck-01/PASS.json`通过。此为对已完成真实执行的独立结果核验，不是重跑或伪造新测量。原scale-02及memory-01的脚本失败仍为FAIL，未补写PASS。
未来脚本把自动可用内存四例与等资源复验分开，等资源断言转为上述正式核验函数，不要求违背动态校准的恒定N。I03关闭；没有放宽产品内存/采样上限，没有修改产品或原数据换通过。

### C04 最终闭环
- 固定限制四例prepare/diagnose峰值（十进制MB）：DS1200 277/286、DS12000 277/286；QW1200 507/530、QW12000 526/529。自然资源四例加固定资源四例全部完整计算，无mem_limit/OOM/硬时间终止。模型固定开销不足环境不在该保证内；不是整机cgroup限制测试。
- `c04-restart-PASS.json`：同候选正常停机/确认端口释放后重启，12份既有报告内容不变、118个本轮CSV/监控产物SHA不变，4个固定资源测试是新增任务，共16任务，无自动重跑。候选源码摘要不变。`c04-browser-restart-01/PASS.json`新浏览器五组/四入口通过，0 POST/0页面异常。
- `c04-ruff-final-01`新增独立验证脚本闭包变量lint失败，绑定循环变量后`c04-ruff-final-02`全部通过。前端363 tests/typecheck/eslint、后端本轮190 unit +42 integration +13修复复验、mypy143文件/schema检查均通过；各批前述测试不重复计为额外唯一覆盖。
- C01/C02/C03/C04技术门槛收口为 **LOCAL_TECHNICAL_PASS / USER_ACCEPTANCE_PENDING / ON_SITE_PENDING**。C04-I01/I02/I03关闭；完整证据`artifacts/validation/development-v3/repair-c01-c04-20261111T184136/CLOSE.json`。人工说明：[LOCAL_ACCEPTANCE_20261111.md](LOCAL_ACCEPTANCE_20261111.md)。不能代用户签人工通过。
- 同候选服务PID411591，端口18002，命令/日志为`c04-e2e-02/server-restart-01.json`与`.log`；为用户保留。没有打包、Git提交/push、真实华为执行、派发其他会话或触碰原认可约15万条state。
- 限制：真实华为收益仍ON_SITE_PENDING；真实旧state不可得，旧V2/V3/Token只读采用隔离fixture/现有回归，不能称现场历史全部验过；0.5/零/负展示由组件测试验证，五主样本不伪造这些收益。显式full/新Token规则/业务时间无损保证均不在本轮。

### 最终设计对照
| 批次/门槛 | 结果 | 主要证据 |
|---|---|---|
| C01 入样前限制/单窗/无硬时限/取消 | PASS | c01-01/03、c04-unit-01、c04-integration-01；固定内存复验 |
| C02 五组自动发现/精确修改/同样本守恒/旧读 | PASS | c02-01/03/04/05、c04-repair-02、c04-e2e-02 |
| C02 多方案/部分结果/证据损坏拒读 | PASS | 34真实方案、c04-integration-01、c04-repair-02、c04-extra-01 |
| C03 原V2布局/移除独立模块/样本不套full与1pp | PASS | c03-04、c04-browser-03与restart-01；获批HTML SHA不变 |
| C04 两模型1200/12000/实际受限内存 | PASS | 原任务均完整，c04-memory-recheck-01；原错误测试断言FAIL保留 |
| C04 L5大整数/取消未评估/无变化 | PASS | c04-extra-01、extra-browser-02 |
| C04 重启/来源不变/浏览只读 | PASS | c04-restart-PASS、browser-restart-01 |
| 本机用户人工/华为五组真实收益 | PENDING | 用户实际验收/现场执行后再记录 |
| full/Token私有开发/打包 | NOT_RUN（范围外/未授权） | 不把延期记实现 |

### 2026-11-12 用户闭环与交付交接
用户明确“用户验收通过”，本机状态升级LOCAL_USER_ACCEPTED。用户授权镜像线独立端到端验收、Git/版本/记忆整理、打包，交接prompt为PACKAGING_HANDOFF_PROMPT_20261112.md，代码/测试/脚本改动SHA为HANDOFF_CANDIDATE_20261112.json。原CLOSE.json及所有测试FAIL/PASS不改写；现场收益继续ON_SITE_PENDING。开发本轮只准备交接和更新本人记录，不代镜像线执行，不宣称消息已发送。

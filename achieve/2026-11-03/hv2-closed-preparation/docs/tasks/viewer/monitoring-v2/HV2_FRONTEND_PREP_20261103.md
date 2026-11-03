# HV2-R1-MONITOR-FE-PREP：监控前端接入准备

2026-11-03。状态：**准备材料完成，等待用户/MA后端独立验收、冻结契约及正式接入通知；未开始编码或验收。**

本线实际 CODEX_SESSION_ID / CODEX_THREAD_ID 均为 `01a18c49-d9b4-7a33-8c04-e5a72adfcc24`，本轮环境再次核实。接受V2总设计师直接派发，负责用户监控、搜索排行、TTFT及MA；不接管异常页面。优先处理多模型发现和MA独立可用值，其次接入已批准的简化TTFT。依赖及窗口以[执行板](../../delivery/HV2_REPAIR_EXECUTION_20261103.md)和[总计划](../../delivery/V2_REPAIR_COORDINATION_PLAN_20261103.md)为准；后端编码已启动不等于前端依赖已验收。

## 1. 身份锁定与只读检查

当前HEAD与派发基线一致：`7cbe28621f4e46083bf47f9aa14b011b3cb250c4`；原交付源码身份 `b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af`仅作历史追溯，不用旧包替代新候选。共享工作区已有其他会话文档差异，未reset/clean/暂存/提交或覆盖。前端源码、测试、脚本、锁文件逐文件SHA见[本轮身份快照](../../../../artifacts/validation/viewer/HV2-FE-PREP-20261103/identity.json)，初始工作区见同目录status-before.txt；该快照不是构建或验收产物。

| 批准原件 | 路径（项目相对） | 本轮实读SHA256 |
| --- | --- | --- |
| 监控UI-02 | docs/tasks/viewer/monitoring-v2/prototypes/tokenscope-v2-demo-ui02.html | `799786cb3ee52e0931d2482211f82e594ab0f33ad57969232a7ea2ec06d2eaea` |
| 异常UI-04，跨线保持 | docs/tasks/viewer/analysis/prototypes/analysis-ui04/tokenscope-analysis-ui04.html | `779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f` |
| 原验收报告 | docs/huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md | `93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e` |
| 调查原件 | docs/huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md | `51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83` |

两HTML摘要与各自manifest一致，两报告摘要与派发一致。读取调查§4/§6及验收§4/问题P1，原件不改。四入口保持 `#/users`、`#/users/ranking`、`#/analysis`、`#/ma`；保持已有六卡、三图、TTFT三栏、MA全UUID表和画像双页签、布局及配色。最后批准L4/L5聚合展示优先于早期HTML，归异常前端维护；不恢复T1，UIR-03留V3。批准恢复依据见[历史UI恢复交接](../../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/viewer/monitoring-v2/APPROVED_UI_RESTORATION_HANDOFF_20261102.md)，不执行其中旧端口或旧阶段指令。

当前关键源码SHA256：

| 文件（apps/viewer/src/下） | SHA256 |
| --- | --- |
| features/v2/UserMonitor.tsx | `810f29d3a6918d667bb064cb5ea5704b83b1991d5d9fda8693340d9880d56c25` |
| features/v2/TTFT.tsx | `217d459be682a63e872c9ff0732ebce974798cde11d9f385bea021a5dc21c7fc` |
| features/v2/MAMonitor.tsx | `c6ae5ac1df69ee0c9387961c779067b6fe407976ed2a271637128ee364e97f05` |
| features/v2/MACharts.tsx | `920fb06eae3075dd0f17fd6491d41270d4940a7a1ec2d40433f4594295108c86` |
| api/v2/client.ts | `a4658fc1a6fef77235f834abb0f4471a1ea86f5d8aa34fd510f53a8cba678b1f` |

## 2. 证据边界与当前差异

| 主题 | 当前源码/报告可证事实 | 接入目标与不得外推的结论 |
| --- | --- | --- |
| 同APPID多模型 | UserMonitor范围栏只展示单receipt的common_name/model_id，APPID来自单run排行；V2Records.remember保留50个run；当前api/user.py没有GET全量用户run目录 | 使用待验收的服务端目录发现同APPID全部已发布模型。不是“扩展单槽localStorage”；不能从S0目录猜user_run绑定，也不能以多URL/手填ID替代发现 |
| TTFT | 当前要求先选/登记scenario，再显式POST评估；读取历史保留快照 | 日常只填W、SLO T；模型默认τ/K由后端提供，来源/revision可读，K覆盖选填。不在前端默认创建scenario或GET触发计算 |
| MA | 表中是paired_ideal/paired_real；详情已有独立real/ideal；小时压力来自hour，实际重算总量当前取real.totals并以样本数判缺失 | 在批准位置解释配对与独立差异及缺失，独立可用值不得被Q=0遮蔽；不将独立值填入paired列 |
| 现场证明 | 调查给DS cached空字段及GLM冲突的API/源码解释，但没有最终实际DOM证明 | 后续必须比对真实浏览器HTTP→DOM，不能直接宣布前端已正确展示；本轮只读，不声称现场复现 |

证据校正：DS的R/Q=0表示真实/配对无有效样本，不是“真实命中率等于0”；GLM冲突可能E/Q=0而R及小时值可用。调查GLM总数27与分项6+9+11=26不符；Qwen48个UUID完整矩阵、完整MA文件SHA、冲突最小真实行、研究正反例及脚本正文仍有缺口。151320与150698差622没有逐行映射，不认定全部窗口/去重。L4差异不等于动态字段浪费/会话改写；零recipe与TOKEN_FRAGMENT_INCOMPLETE不是同根因，后者由fragment.coverage.complete=false触发。这些异常分析事实不转为本线新增业务或UI结论。

## 3. 待冻结的消费者要求

以下是验收交接需要提供的语义清单，**不是已存在的新端点/DTO，也不先猜字段编码**。

### 用户目录及范围

- 后端给实际GET路径、Schema/OpenAPI版本、样例、身份头/错误码、分页及revision规则。明确按APPID精确发现还是枚举组合；不可用单run排行limit=1000当完整模型/租户目录。
- 每个可选项须可无歧义定位服务实例、Trace来源/摘要、APPID、模型规格common_name及编码model_id、user_run_id/base_run_id、结果revision和窗口。模型显示别名不能代替身份，不能裁掉MA制品后缀来合并。
- 明确同模型多个历史run的分组和稳定排序、“最新已发布”的选择规则、ready/empty/处理中/失败及不可读项的可见性。显式历史深链保持固定，不被新目录发布或刷新抢占。
- 明确目录并发发布、revision冲突、分页取消、服务重启、旧run不可读的响应；目录GET只读，不因发现创建binding、索引或分析任务。
- 用户与异常共Trace链：由后端冻结到异常SourceLink的身份映射；本线只保证跳转身份不串，异常报告/partial/SSE由异常前端维护。

### TTFT默认参数与历史兼容

最新用户给定：Qwen-V3.6-27B τ=1s、GLM-V5.2 τ=2.7s、DeepSeek-V4-Flash τ=2.6s；默认K=8192。均应登记为用户提供默认值，不能标实测校准。值由后端保存并返回，前端不复制为运行常量。

- 冻结模型别名→默认配置的映射、只读发现方式、source/revision/适用K及适用范围、缺配置状态、更新与重启持久性；其他模型缺τ须明确不可算，不借邻近模型值。
- 冻结新显式评估POST的请求/响应、幂等及错误，是否引用默认配置ID/revision、与旧scenario/evaluation接口如何并存。应能从结果追溯实际采用的模型、K、τ、来源、revision、run、APPID及P90，配置变化不改封存结果。
- K覆盖、恢复默认、覆盖后τ适用性由后端明确；不能暗推τ按K线性缩放。缺失与空字符串、0、小数的验证不得因表单简化改变。
- 日常只要求W和T；页面“等待时间”仍说明W覆盖首Token前全部非计算耗时，不重复扣O。默认≤；旧＜及旧W+O历史只读保持。评估为参考命中率，不宣称生产P90 SLO保证。
- 确认参数未配、无有效P90、0%/100%、无预算、超范围、不可用及服务故障的状态/原因字段；前端不本地重算公式，不把null显示0。

### MA值、分母与缺失

- 冻结现有或新增说明字段对应的独立real、独立ideal、paired_real/ideal、A/P/R/E/Q、样本分母、覆盖率、ideal_status、质量reason/limitations及其适用范围。整文件质量不得直接说成每个UUID均存在同一坏字段。
- 说明hour.request_count/real_count/uncached_tokens/rates与real.totals的范围及一致条件，12个300秒桶归属request_time和handle_time窗外计数语义；禁止前端按可见行/桶重算总量冒充权威值。
- 区分真空桶0、有请求无有效cached观测null、部分有效样本、有效零未命中、仅pre、empty_now、无有效预热、warmup_order_conflict。每项指标独立判断，不用单一整体失败标志遮蔽不受影响值。
- GLM冲突是否维持整体UUID理想不可用或另有获批策略须先审定。本线不截尾、不将partial改ready；DS缺真实观测仍需上游数据，不因显示优化声称补齐。

## 4. 接入位置与共享窗口申请（本轮不占用）

| 位置 | 后续拟接入内容 | 依赖/唯一窗口 |
| --- | --- | --- |
| UserMonitor.tsx | 在批准模型选择/范围栏恢复同APPID模型发现及切换；目录驱动、固定历史；最近记录仅偏好恢复 | 用户目录独立验收与冻结 |
| Ranking.tsx、TTFT.tsx | 排行保持20条/300ms/显式条件；切模型重读且隔离旧响应；TTFT在原三栏/条件入口简化为W/T和可选K | 用户目录/TTFT冻结；不得改变UI布局 |
| MAMonitor.tsx、MACharts.tsx | 已有单元格/条件说明/独立指标详情解释缺失，保留全UUID/最多4并发/逐行重试 | MA独立验收与样例冻结 |
| api/v2/client.ts、generated/user、generated/ma及生成脚本 | **已定位依赖**：verifyUserContract当前硬校验2.0.0且9个操作。新增目录会使当前握手拒绝；须按冻结版本/操作清单更新校验和新增DTO注册，不能去掉版本门禁或绕过Schema | 由总设计师安排单一客户端/Schema窗口；收到冻结内容后交精确补丁 |
| app.tsx、V2App.tsx、全局样式/路由、共享S0组件、锁/构建 | 当前不申请修改；四入口及异常L4/L5保持。若目录默认导航需要共享壳调整，先提交文件/分支条件/测试依赖的精确补丁 | 总设计师单一窗口，不与异常前端并发写 |

产品选择切换需取消/隔离旧轮询、请求池、TTFT和导出；失败/中断保留历史只能保留在其原身份标题下，不能把旧模型值挂在新模型标题下。既有服务身份、精确整数/小数、缓存/SSE、固定版本、幂等恢复、NDJSON SHA/行数和CSV结构/行数完整性要求均继续。

## 5. 冷state浏览器复验清单（待协调后执行）

本轮不监听端口、不停服务、不构建。申请由总设计师在后端冻结和编码自测完成后协调**唯一**真实服务/E2E窗口：先识别并停旧TokenScope服务/相关进程/测试容器，确认退出及端口释放，保留旧包/state/证据；再以固定候选、新独立state、全新浏览器context冷启动。不能沿用2026-10-31“另开端口保留旧版”做法。记录源码/契约/配置/输入SHA、浏览器与HTTP身份、执行命令/退出码。

1. **多模型准备**：最小合成Trace中，同一APPID分别属于三模型，另有两模型及单模型APPID；同模型保留两个固定历史run，另有empty/失败/处理中对照。显式提交并确认发布状态，禁止依赖测试顺序或旧localStorage。合成输入清楚标记，不能冒称现场CSV。
2. **发现与切换**：空浏览器直接进入用户页，应从服务端发现可用范围，无需手填runID；同APPID逐模型切换，核对目录→receipt→snapshot→排行→P90→导出各自完整身份。用跨目录页fixture确认没有只取首屏；未知APPID、单模型、目录空/失败/revision冲突分别检查。延迟旧请求、切范围/身份/重连，旧数据与成功提示均不得回写。
3. **固定历史和排行**：显式历史URL、返回排行、浏览器刷新、后端新发布后手动刷新目录及重启，历史不被静默替换。保持20+5、字面%/_、300ms/Enter竞态、显式应用范围、revision冲突、大整数/null、并列众数跨页/200K以外等宽箱断言；不加等待掩盖竞态。
4. **TTFT**：三模型自动读对应τ和K8192，仅填写W/T可显式评估；验证W空与显式0、T≤W、精确小数/等号、0%/100%、缺τ/无P90/超范围、K覆盖与恢复及来源文案。切模型/配置revision时延迟旧默认值和旧POST回包，不串值；新revision不改旧evaluation、旧＜和W+O快照。GET无分析写入，未配置不发无效评估，不自动重发POST。
5. **MA结构对照**：合成样例覆盖DS式cached全缺但ideal可用；GLM式warmup冲突但real/hour可用；两独立集合有值而paired为空；全部有效、零未命中、空桶、缺观测桶、仅pre/空now/无预热。全UUID占位/并发/重试及模型制品、run、UUID、窗口切换全部验证。HTTP逐字段对照表格与展开DOM：独立ideal/real仍可见且标签正确，paired仍缺失；不得用数值相似替代身份校验。
6. **后续现场单列**：针对报告GLM冲突UUID核验真实小时值/12桶与DOM，针对DS全部UUID核验独立ideal可见及真实观测缺失说明；补齐Qwen逐UUID对照和完整输入SHA。仅在取得实际证据和授权后执行，不由合成样例通过代签现场通过。GLM26/27计数差与审计622差保留未决。
7. **保护回归**：批准四入口、桌面/窄屏布局、最后L4/L5不变；身份变更、60秒状态/终态停止、失败历史、导出切范围取消及完整性、缓存/SSE/重启恢复；原UIR-01鼠标/键盘与UIR-02范围恢复不退化，不把UIR-03纳入本轮。独立审查由总设计师执行，前端不代签最终验收。

实现后的拟用检查：typecheck/lint/npm test/npm run build；扩展现有v2-user、v2-ranking、v2-ttft、v2-ma、v2-ma-boundaries、v2-review-fixes、approved-ui-restoration与四入口用例。新增测试代码仍待正式派发，本轮没有写或执行这些测试。最终交接区分真实HTTP、故障注入、DTO投影、文件API替身及现场证据，不累加重叠通过数。

## 6. 本轮实际完成与退出条件

实际命令仅为Get-Content/rg定向读取、环境ID、WSL git rev-parse HEAD/status --short、Get-FileHash SHA256及文档/身份清单写入；未运行产品、功能测试、监听服务或构建。报告和HTML摘要核对一致；现有源码用于差异分析，**没有修复前后运行结果**。

本轮变更仅：本文件、本线ENTRY、本线memory/tasks/viewer-monitoring-v2.md，以及artifacts/validation/viewer/HV2-FE-PREP-20261103只读核对记录。不修改CURRENT/SESSIONS/总执行板、源码、测试、HTML、契约、锁、CSV或发布结果；不创建子agent/session、不发送跨会话消息、不commit/push/Docker/打包/部署。

正式接入前需总设计师提供：用户目录及TTFT后端通过记录和冻结包；MA通过记录及空值/范围样例；明确客户端/Schema单一窗口；唯一E2E环境安排。字段/兼容语义未冻结前保持等待，不把本清单当作新契约或编码授权。

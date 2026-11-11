> V2历史材料，仅供追溯，不是当前启动/修复/打包指令。[原始字节](../../../../../originals/docs/tasks/viewer/analysis/FRONTEND_DEVELOPMENT_PLAN.md) · [当前会话登记](../../../../../../../../memory/SESSIONS.md)。下文仅迁移导航链接，历史决定和结果未更新。

# 异常分析正式前端开发方案 AF-1.0

> 2026-10-31 当前范围覆盖：UI-04信息结构/配色布局已批准；Token仅T2/T3/T4（三个探测器，编号不变），工具定义只归低命中既有顺序/内容一致性分析，不增长度精简。旧T1保留历史兼容但不生成新Token卡片；当前样例入口为后端ART3。正式前端待后端冻结接口及实际验证回传后返工，前端不承担后端开发。执行与身份见 [AR-03](REWORK_COORDINATION_AR03.md)，下文冲突内容为历史。

2026-10-31，待用户确认；负责人为异常分析前端session 01a19111-344a-75c1-84e0-14db8be08f4f。当前P0为方案评审，依赖两线已回传的只读协议；本轮只写文档，不创建源码、服务、测试任务或新DEMO。

## 1. 依据与范围

- 视觉规格：[UI-03](../../../../../../../../docs/tasks/viewer/analysis/prototypes/analysis-ui03/tokenscope-analysis-ui03.html)，SHA256 `e6fa9f96c946e066f2ed52a439b07350cb07d78a290427c6a1670f4662b56869`；保留配色、侧栏/顶栏、范围栏、双列/窄屏单列卡片、三段详情及信息层级。构造数值不进入正式产品。
- 有效交互：[I-0.5及范围修正](../../../../../../../../docs/tasks/viewer/analysis/INTERACTION_DRAFT.md)；接入事实：[最终核对](DEVELOPMENT_READINESS.md)、[低命中回执](../../../../../../../../docs/tasks/prefix-analysis/FRONTEND_READONLY_RECEIPT.md)、[Token回执](../../../../../../../../docs/tasks/length-analysis/FRONTEND_READONLY_RECEIPT.md)。本方案明确覆盖历史交互稿中的提交、取消、重试分析和单项评估流程，不恢复这些操作。
- 协议：analysis-common-1.0、diagnostics-http-1、diagnostics-discovery-1；以各自冻结Schema/manifest和两份当前工作树清单为依赖。开始实现及真实联调前重核，不拿历史HEAD替代工作树摘要。
- 最新项目决定：[Token自动建议/收益留至V3](../../../../../../../../docs/tasks/length-analysis/AUTOMATIC_RECOMMENDATION_EVALUATION.md)，本期不补后台自动建议/评估链，不以此阻塞只读前端。

本期交付应用/模型服务/类别选择、报告目录与历史、低命中/Token卡片及证据详情、已有且可关联收益、完成通知、错误恢复、轻量缓存和返回监控。报告页只出现有已发布历史的appid；某方向没有报告就显示该方向暂无报告，不借用另一方向数据。

不提供分析发起、取消、重试任务、参数/授权表单、单项/组合评估提交、导出、Agent修改或全历史评估搜集。只发GET；读取重试与重新分析明确区分。浏览器访问不能产生分析副作用。

## 2. 工程接入和模块边界

复用现有apps/viewer的React/TypeScript、AJV、Vitest、Playwright与Vite，不新增框架或依赖。以下为拟建模块，尚未创建；路径可在不改变职责与验收的情况下细分。

| 模块/拟定位置（相对apps/viewer） | 职责 | 边界与复用 |
| --- | --- | --- |
| src/features/analysis/AnalysisApp.tsx、analysis.css | UI-03外壳、范围与类别、目录入口、可访问性 | 样式限定.analysis；复用base.css变量；不改监控页面布局，不复制DEMO整页脚本 |
| src/features/analysis/Reports.tsx、LowHitReport.tsx、TokenReport.tsx | 两类卡片、折叠探测器说明、必要未检查提示 | 低命中两分区；Token单列表；无置信度/覆盖率、无合成影响数 |
| src/features/analysis/ReportDetail.tsx、Evidence.tsx | 问题/建议/预期提升、全文、位置、技术信息折叠 | 原文按需取、以纯文本呈现；不执行recipe/replacement，不渲染正文HTML |
| src/api/analysis/client.ts、generated/、contract-lock.json | GET封装、两类capabilities、Schema校验、实例头、SSE解码 | 独立诊断契约；不改监控的API头/协议；复用整数/时间等纯工具须先检查语义 |
| src/features/analysis/model.ts、adapters.ts | wire到业务视图映射、关联ID、缺值及状态语义 | Task/Rule/Evaluation三层状态分开；不实现Tokenizer、收益推断或规则算法 |
| src/state/analysis-discovery.ts、analysis-report.ts | 完整目录快照、单连接通知、目标/已显示报告、迟到响应防护 | 同标签页同实例共享1条流；组件不独自订阅；不复用监控任务轮询状态机 |
| src/storage/analysis-cache.ts | 白名单持久缓存、内存页复用、版本隔离、淘汰 | 独立命名空间；不迁移/清空监控缓存，不把fragment/Plan当轻量数据 |
| src/features/analysis/navigation.ts | URL身份、历史选择、卡片返回、监控跳转 | URL只含身份与选择，不含原文/参数；不把base_run_id当user_run_id |
| tests/analysis/及现有浏览器测试目录 | 契约fixture、组件/状态测试、真实浏览器及联合验收 | 复用两线样例，构造服务与真实后端证据分开 |

共享改动预计仅app.tsx增加分析路由分派、V2App.tsx增加桌面/移动导航入口；按最新SESSIONS登记单一编辑窗口，重读后最小修改。不重构监控状态/API/数据库，不预先升级锁文件。若实际需要新增依赖或大幅改共享结构，再说明影响并讨论。

拟定正式路由为 `#/analysis`；查询参数包含binding、direction、mode（latest/history）、task、itemKind、item。显式历史和详情固定task，详情返回保留来源mode和同task；绑定及对象均经目录/报告验证。UI-03的demo-rag演示路径不直接作为真实任务身份。实例由当前连接绑定，恢复的旧身份必须与之核对，不能跨实例解释同名task。

## 3. 接口与页面映射

所有诊断请求除capabilities外带 `x-tokenscope-service-instance`。以实际Schema校验，不因表格简写漏掉必需字段。B表示 `/diagnostics/tasks/{task_id}`；单项items响应直接是data，列表为items[{id,data}]+offset，无total/has_more。

| 页面用途 | GET接口 | 映射与检查 |
| --- | --- | --- |
| 连接初始化 | /diagnostics/capabilities；/diagnostics/discovery/capabilities | 主契约与扩展版本、同一service_instance_id；不支持时显示兼容提示，不回退轮询 |
| 应用/模型服务、报告选择、完成时间 | /diagnostics/discovery/catalog | binding_id及binding.appid/model_id/common_name/source_kind；directions；task_id/scope_id/scope/report_digest；analysis_completed_at；defaults按binding+direction给当前task |
| 完成通知 | /diagnostics/discovery/events?cursor=… | fetch流式SSE，terminal/reset/注释心跳；通知触发目录对齐，不拿事件字段替换指标 |
| 已知终态恢复 | /diagnostics/discovery/tasks/{id}/terminal | 仅有明确已知ID且需恢复时一次GET；不是定时任务查询，也不引入任务管理页 |
| 报告头、范围、规则状态、限制 | B/report | scope/scope_id、runtime_options、stages、reason_codes；完成时间来自目录，不取浏览器时间；空stages合法 |
| 低命中卡片及收益 | B/items/finding、experiment、evaluation、optimization | finding_id→experiment.finding_ids→evaluation_id；优先独立evaluation/optimization中的派生值，不能假设嵌套pilot/full具备派生字段 |
| 低命中证据/方案 | B/comparisons/{finding_id}；B/items/plan/{plan_id} | 两条完整请求与各自指针；evaluation.plan_id→plan.finding_refs回核；不按rule_id通配收益 |
| Token卡片 | B/items/fragment | items[].id定位fragment；data中findings/locations/units/observations按真实结构映射；T3没有Finding仍有观察，不走低命中finding通道 |
| Token位置及全文 | B/items/fragment_index/{fragment}；B/requests/{fragment} | 服务返回location/unit/observation IDs并与数组同序关联；scope用父report/requests，fragment本身无scope_id；raw_body/raw_sha256及完整/截断标志 |
| 已知Token/低命中评估 | 子任务terminal、report、items/evaluation、items/plan/{id}，必要时items/authorization | 仅消费可信已知ID且关联校验成功的已存结果。校验parent/plan_refs/scope及原文身份；T3 finding_refs可空，走授权输入与位置关联；不能可靠关联则不贴收益 |
| 原报告监控来源 | /analysis-runs/{base_run}/view-snapshot?appid=…；/monitoring/user-v2/runs/{user_run} | source.base_run_id/user_run_id各司其职；user receipt核对appid/model/common_name/base。用户监控用自己的X-TokenScope-Instance-Id，不能复用诊断头 |

目录第一页after=0、limit=100；续页固定snapshot和next_after直到null，defaults即使指向后续页也不能提前判缺失。数据列表limit=100，满页继续、不足结束；界面只称“已加载N项”。未读完不可宣称全scope计数/排序。

低命中收益关联需要的列表按需分页建立映射：关联尚在加载显示加载态，只有所需列表穷尽才显示“暂无量化结果”。首屏不取全量原文/Plan；技术详情按需取。各列表独立加载和重读，不让一条损坏证据清空报告。

### 展示语义

低命中只有后端认定合格的完整full/direct_full且严格>1pp进入“已验证的优化建议”，精确1pp不进入；其余进入差异/事实，不把pilot当全范围收益。标题可使用固定规则业务说明，建议优先F.advice；不假造服务没有的description、examples、affected_request_count。零值、缺值、未执行分别表达。

Token区分内容清单、策略不符合、重复观察与保留规则；无policy不判超限，unknown不计作已参与，T4缺失与0不同。度量标明字节/字符/Token，重复字节不换算节省Token。初始报告无收益时保留现有建议/观察；已有可关联结果显示P/C及零负值，blocked不补after=0，多个建议不相加。

原文保留服务完整文本，禁止JSON解析后重新序列化当原文，避免9007199254740993等整数失真及空串/null变化。元数据十进制字符串保持字符串或用现有安全整数工具，不经Number比较sequence。只展示服务提供的收益，不在前端做业务重算。

## 4. 状态、通知与失败恢复

状态分为连接状态（连接中/在线/重连/不可用）、目录状态、已显示报告、待读取目标、浏览模式（最新列表/历史/详情）。这几个状态独立，失败不能把报告变成空结果。

1. 打开先校验实例与契约，再获取完整目录快照；缓存可先显示但标正在核对。按快照event_cursor订阅，覆盖读取和订阅之间的完成事件。
2. 默认从defaults选择，按发布sequence而非数据窗口排序。读取报告头与当前首屏必要页、核对身份后一次提交内容和完成时间；分页后续为同报告增量，不把旧页混进新报告。
3. 在线terminal事件合并为一次目录对齐：同一时刻仅一个对齐请求在途，在途期间有新事件则完成后再对齐一次，不能吞掉末次通知。游标只在事件已处理/恢复意图已记录后推进。重复事件幂等，乱序不按到达顺序换报告。
4. partial/empty不替换默认；两方向整体ready才更新包含方向，Token-only不改低命中。无默认但有历史时提示选择历史；无历史appid不列出。legacy完成时间显示未提供。
5. 历史选择固定task；新报告仅提示。详情期间也只提示，返回原task列表及卡片位置，点击“查看最新”才采用新结果。最新列表可以在读取校验成功后自动更新。
6. 断线只重连通知，建议退避1/2/4/8/16/30秒封顶并加抖动；这是断线恢复，不是正常运行每隔几秒查询任务。恢复连接前重新对齐目录；离开分析模块/标签页隐藏关闭流并停止重试，重新可见时对齐并重连。无需后台实时提醒，跨标签不引入leader选举；每个可见分析标签最多1连接。
7. reset重新绑定capabilities和目录；实例变化取消在途读取、隔离旧缓存。目录读失败保留最后已显示报告并标目录未确认；通知成功但目标读取失败保留待读取目标，提供“重新读取”，下次打开/重连对齐可再次恢复。
8. 404显示任务/证据不可用，409按错误码区分实例/reset/来源或封存问题，422提示请求或兼容问题，503/网络错误可重读；未知错误保留code。详情局部失败只影响该区域，不展示无限加载或伪装无问题。

目录不提供全量活动任务，不保证显示正在运行的后台分析。仅在有可信已知任务信息时显示非实时状态；无法获知时照常展示旧报告及完成时间，不编造进度或“当前无任务”。

## 5. 缓存、历史与定位的工程默认值（待确认）

持久缓存仅保存白名单投影：服务/契约/缓存格式身份，binding显示字段与ID，task/direction/status/完成时间，数据窗口/计数/scope_id/report_digest，已确认的导航选择。不能整对象写入scope、runtime_options或原catalog，因为可能含配置/参数。禁止持久保存advice自由文本、fragment、finding正文、Plan、authorization、requests/comparisons或原文。

建议持久缓存上限2MiB、最近100条报告元数据、7天未使用淘汰，取先达到的限制；这是浏览器缓存，不限制服务器历史。完整服务器目录可分页访问，缓存裁剪不能裁剪服务器选择范围，也不能据裁剪结果认定报告被删。存储写满/禁用自动退回内存，页面不报致命错误。

内存报告页缓存建议最近3份报告且序列化载荷估算总量≤16MiB，LRU回收；不承诺等于浏览器实际堆大小。全文只在当前详情持有，返回时释放，不纳入跨报告缓存；超预算的单页/单份全文允许当前视图读取但不复用缓存，按需展示，不能静默截断为“完整原文”。若现场超大正文不可读，显式失败并记录验证限制，不虚构支持上限。

键包含service_instance_id、契约/缓存格式版本、task_id、scope_id、report_digest、direction；页再含kind/offset/limit；目录和默认引用额外绑定snapshot。过期只丢本地副本，已封存报告不因TTL变旧；“是否最新”始终由目录判断。

列表到详情保存同task、对象ID、已加载页、卡片锚点及滚动位置；浏览器history.state存轻量返回信息，内存存已读页。返回优先锚点、其次滚动位置。内存页被回收时最多重读原目标页及必要父上下文，不为返回无限遍历；无法恢复卡片则回同报告顶部并说明。刷新/分享可恢复报告与对象，不承诺跨设备滚动位置。

跳“原报告来源”精确使用旧run，标签明示历史来源；跳“当前监控”只使用已验证同服务当前关联，否则回用户监控选择入口。缺common_name或用户最新run目录不能用猜测补齐，不自动bind/recompute。

## 6. 分批实施顺序

用户批准本方案并授权实施后按AF000→AF006顺序推进。每批记录实际改动、依赖摘要、测试结果、缺陷/偏差及回退；正常缺陷批内修复，不按测试数量宣称完成。后批开始以依赖批通过为条件，遇契约/范围变化先澄清，不绕过门槛。

| 批次 | 实施内容及依赖 | 批次完成标准 |
| --- | --- | --- |
| AF000 接入锁定 | 复核两线清单/契约、UI-03、当前前端依赖；登记共享窗口；加入分析契约生成/校验和带来源标注的fixtures | 版本/摘要可复核；正确样例可解析，错版本/错实例/大整数不被静默接受；没有业务POST |
| AF001 只读目录骨架 | AnalysisApp及路由导航、capabilities、完整目录分页、范围/时间、历史选择、报告头 | 仅历史appid；方向/服务隔离；默认/partial/empty/legacy正确；切换失败不串内容时间；监控既有入口回归 |
| AF002 低命中报告 | finding/experiment/evaluation映射、两分区卡片、比较全文与Plan详情 | >1pp/精确1pp、pilot/full/direct_full、L4/L5、缺收益/未检查、同规则不同finding关联通过 |
| AF003 Token报告 | fragment/index/requests、同请求多位置、T1–T4、可信已有评估只读关联 | 无policy/unknown/T3观察/T4缺失与0、零负/blocked、完整原文与数值保真；无自动评估或参数表单 |
| AF004 通知和恢复 | 单流fetch SSE、目录快照衔接、事件合并、reset/重连、迟到响应保护、待拉取恢复 | 丢连接/重复/乱序/实例切换/读取失败均可恢复；正常心跳不触发GET，任务状态零轮询；旧报告和时间不丢 |
| AF005 缓存及导航 | 白名单/容量/回收、历史固定选择、详情返回、原来源/当前监控跳转 | 存储禁用/写满仍可用；无正文持久化；历史/详情不被通知打断；回收/刷新/失效深链接回退明确 |
| AF006 联合与视觉收口 | 真实两后端HTTP+浏览器；UI-03逐屏比对；监控回归；整理独立复审prompt | 下述验收矩阵通过或明确记录不能关闭的阻断；用户功能/视觉验收与独立复审交接就绪，不能代签通过 |

单批回退仅撤销本批自有文件/最小共享改动，保留用户报告及他人工作；可移除分析导航/路由恢复监控入口，不回退后端数据库。不得全局reset或清理共享工作区。

## 7. 验收标准与证据

| 编号 | 验收场景 | 明确通过条件 | 验证层 |
| --- | --- | --- | --- |
| A01 身份与精度 | 三契约、实例变化、9007199254740993、时间null | 拒绝错配、迟到响应不能落入新范围；字符串整数/原文不失真；时间不补造 | 契约/单元+真实HTTP |
| A02 目录完整性 | 多页defaults引用后页、首次partial/empty、legacy、Token-only | 完整快照后决定默认；无默认显式选历史；两方向独立，无空appid伪报告 | 状态+浏览器 |
| A03 只读性 | 打开/切换/刷新/重连/历史/详情 | 网络记录无业务POST和定时task查询；没有评估/授权/修改控件 | 组件+浏览器网络记录 |
| A04 低命中语义 | 严格>1pp、精确1pp、pilot、L4/L5、同规则不同finding | 分区与证据一致；不把子范围当全范围、不虚构影响数/收益、不复制不相干评估 | fixtures+真实后端 |
| A05 Token语义 | 无policy、unknown、T3无Finding、T4=0、零负/blocked、无评估 | 事实/问题标签正确，单位明确；缺值不补0、不强求输入；已有收益关联正确 | fixtures+真实后端 |
| A06 全文与位置 | >64KiB、多位置、双请求、空路径、null/空串 | 展示完整服务原文与真实位置，preview不冒充全文；纯文本无脚本执行 | 组件+浏览器 |
| A07 通知恢复 | 目录订阅竞态、重复/乱序、断线/reset、503/实例切换 | 恢复后与权威目录一致；1可见标签≤1连接；心跳无报告查询；读取失败可显式恢复 | 状态+真实SSE/浏览器 |
| A08 显示原子性 | 新报告读取失败、partial、切换报告/方向在途返回 | 原结果与原时间一起保留；不混task/scope；证据失败不清空卡片 | 状态+浏览器 |
| A09 缓存 | 白名单审计、淘汰、配额/禁用、离线 | 无原文/自由文本/配置持久保存；缓存有界且不影响服务器历史；离线/待核对明确 | 存储测试+浏览器 |
| A10 历史和返回 | 新报告到达时浏览历史/详情、后退、刷新、深链接失效 | 固定原task；返回原卡片或明确同报告回退；无无限分页；当前监控不冒用旧run | 浏览器 |
| A11 视觉及可访问性 | UI-03对应两列表/两详情；1440、1024、390宽度 | 配色/结构/信息层级保留；窄屏单列、无整页横向溢出（正文区域可滚动）；键盘可操作、折叠有名称、焦点可见 | 真浏览器截图+用户验收 |
| A12 兼容与发布边界 | 用户/MA/V1导航、设置、已有监控读取 | 原页面与状态/API契约无回归；typecheck/lint/相关测试及本地Vite构建通过 | 现有回归+本地构建 |

测试分层：先Vitest契约/状态/组件，后Playwright假服务边界，再真实后端HTTP+SSE+浏览器。构造样例验证语义，不能替代真实服务。AF006记录源码/配置/资产/契约/实例身份、实际数据来源、测试命令、截图路径及失败修复复测；历史后端测试不算本轮重跑。Vite构建是本地前端验证，不是镜像/交付包授权。

真实联调优先使用后端已有可读成果和脱敏/合成数据。若必须新建后端分析任务、占用额外模型资源或修改服务配置，先明确范围与现有授权；不由报告页面触发。代理SSE/华为现场未测可明确留作现场验证，不影响已通过本地证据的真实性，也不能称端到端现场通过。

浏览器工具若仍受阻，继续可独立完成的实现/契约测试，截图和真实浏览器验收记录待补；不得因此代填AF006视觉通过或绕过访问限制。最终功能与视觉需用户验收，随后提供独立复审材料；打包部署仍单独授权。

## 8. 本轮需要用户确认

1. **工程接入**：采用现有工程内独立分析模块、专用诊断客户端/状态/缓存，仅最小修改共享路由与导航；正式入口为#/analysis，保留UI-03外观。
2. **轻量工程默认值**：持久缓存仅元数据白名单，2MiB/100条/7天；内存3份/16MiB估算预算，全文只在当前详情；隐藏或离开分析页断开通知，可见时对齐恢复；不做跨标签连接协调。
3. **实施与验收安排**：按AF000–AF006逐批闭环，以上A01–A12为门槛；确认方案后是否授权本会话开始逐批实现。用户已明确本轮不改代码，因此未执行任何批次。

不再请求重复确认UI-03、只读定位、缺收益处理、partial保留旧报告或已接受的后端限制。当前无需用户补policy/业务授权/模型参数；本地联调的具体服务与成果身份在AF000/AF006核实，确实无法从项目取得时再询问。Token V3自动建议和全历史评估发现不在本次审批范围。

2026-10-31审批：用户认可全部三项，授权AF000–AF006按序实施验证闭环，普通问题自行修复，范围/接口变更再确认；暂不打包部署。

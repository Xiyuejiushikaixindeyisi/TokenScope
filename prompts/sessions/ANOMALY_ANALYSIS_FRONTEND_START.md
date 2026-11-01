# 新session启动prompt：异常分析模块前端设计与开发

> 2026-11-01：此启动阶段已完成，本文件仅保留历史交接。当前角色为异常分析功能总负责，当前只读UI-04/RV2、L4/L5各一张卡及T2–T4自动收益以[统筹入口](../../docs/tasks/analysis/COORDINATION_RV2.md)为准。不要根据下文旧完整请求、单项评估说明恢复已撤回范围；新的统一审查交付使用[RV2 prompt](ANALYSIS_UNIFIED_REVIEW_DELIVERY_RV2.md)。

2026-10-31接入更新：两类后端已完成本地实现与交接，低命中/公共层完整自审已获用户认可。当前主入口是 `docs/tasks/prefix-analysis/FRONTEND_HANDOFF.md`，对齐 `docs/tasks/length-analysis/BACKEND_HANDOFF.md` 与 `IMPLEMENTED_API.md`。公共 analysis-common-1.0、HTTP diagnostics-http-1 已冻结；低命中源码身份 low-hit-backend-local-2，Token 插件 token-content-1。不要恢复早期“尚无后端契约”的状态。本prompt由后端提供，不代表前端会话已创建、接收或取得正式编码授权。

本文件为唯一完整启动prompt，可整份直接复制，无需拼接增量prompt。Token权威交接：[Token前端交接TA-FE1](../../docs/tasks/length-analysis/FRONTEND_HANDOFF.md)。在公共/低命中交接后阅读，使用同一前端会话；重点核对fragment内的Token结果、三层状态、完整单请求多位置证据、显式业务授权以及Token/combined不适用低命中卡片门槛。本段只补入口，不改变下方视觉和审批约定。

你负责**异常分析前端**，统一承接“理想命中率低原因分析”和“Token异常分析”两个分析器的用户界面。你不是这两个分析器的后端/算法会话，不负责诊断、探测器实现、重算命中率或Token来源归因；不接管监控V2用户/MA监控页面。此前前端会话提供UI-01及报告原型，后续本任务由你按用户审批推进。

项目根目录为 /home/zhangxiyue/TokenScope；Windows 可用 \\wsl.localhost\Ubuntu-22.04\home\zhangxiyue\TokenScope 访问同一目录。所有新增材料留在本项目。不要全量阅读文档、历史批次或参考源码。

用户2026-10-30认可初版DEMO设计，明确要求正式前端严格遵循最终获批DEMO的配色和布局。当前UI-01是认可的展示起点，不是未来接口、交互方案或开发计划已获审批。不要把本prompt当作立即编码授权。

后端分线已完成：低命中会话维护L1–L5与公共API/任务/证据/回放，Token会话维护T1–T4及七类handler。本前端统一对接两类结果。先按memory/SESSIONS.md明确自己的真实ID、角色和阶段；禁止沿用这两个后端会话的ID。

## 阅读入口和优先级

以下均为项目内相对路径。P0先读；P1按当前阶段读；P2按问题读；P3仅追溯。

- P0：AGENTS.md → memory/CURRENT.md → memory/SESSIONS.md → docs/README.md → docs/tasks/viewer/ENTRY.md；按需读docs/architecture/TASK_SESSION_WORKFLOW.md。
- P1后端：docs/tasks/prefix-analysis/FRONTEND_HANDOFF.md（公共与低命中统一接入、字段、状态、门槛及完整JSON样例）→ docs/tasks/length-analysis/FRONTEND_HANDOFF.md（TA-FE1，Token字段/证据/样例）及BACKEND_HANDOFF.md、IMPLEMENTED_API.md（Token规则/参数）→ docs/contracts/analysis-common-1.0与diagnostics-http-1的README/wire.json。自审依据为docs/tasks/prefix-analysis/SELF_REVIEW_20261031.md。不将DEMO合成字段当作已交付能力，不全量阅读后端内部源码。
- P1展示：docs/tasks/viewer/PROTOTYPE_V2_UI_01.md、NEXT_PHASE_CONTEXT.md、DESIGN.md的“分析报告展示v0.2”及后续有效决定；docs/tasks/viewer/prototypes/tokenscope-v2-demo-ui01.html、docs/tasks/viewer/prototypes/ui01-manifest.json。主要路由#reports/demo-rag/glm/prefix及#reports/demo-rag/glm/token；HTML已沉淀在docs中，本地打开即可；原HTTP预览已撤下，docs内HTML是视觉阅读入口。
- P2原型源码（确需实现细节时才读）：artifacts/prototypes/monitoring-v1/tokenscope-monitoring-with-reports-v2.html、report-ui.js、report-evidence.js、report-ui.css、report-fixtures.json，按需读。这里的v2是旧报告第二稿，不是已实现的监控V2或正式分析Schema。
- P1交接底座：docs/tasks/viewer/CODEMAP.md、MONITORING_INTERACTION_V1.md的已有路由/缓存/版本原则；按依赖读取监控固定S0（docs/tasks/monitoring/batches/B005.1/S0_CONTRACT.md）和实际API。只使用已声明依赖，不把监控S0冒充分析契约。
- P2：docs/huawei/MONITORING_V1_ACCEPTANCE_20261030.md的有效子集/质量边界；必要时读docs/architecture/MAAS_REFERENCE.md理解模型服务。PrefixLens展示源仅在需要时读evidence/source_drops/prefixlens-ui-demo；算法研究和华为证据取得归分析会话，不由前端重做。
- P3：achieve与旧报告稿仅按问题追溯，不全量阅读两类分析内部算法或其他上游项目。

## 当前产品边界

- 面向业务用户，以appid×模型服务定位，低命中率/Token异常分两类。每张卡片对应一个探测器发现的具体问题，呈现业务描述、影响范围、可用置信度/评估覆盖、位置与证据、修改建议、例子和可证明的收益。
- 实际能展示什么由两类分析器冻结契约决定。缺少字段、来源映射或量化收益时不能虚构，不用前端临时算法补出诊断；断点位置与实际可复用边界分开，不能把LCP直接等同于引擎缓存边界。
- 基础排序沿用获批交互起点：影响请求数优先，置信度/覆盖辅助；收益只能在可比单位和范围内排序。最终采用后端已固定语义；“评估覆盖率”不是运行进度，不能把旧示例口径直接强加给分析器。单项收益不可相加成整体收益，除非后端提供组合评估。
- 读取用户已知task_id的已发布成果，明确数据范围；接口没有分析时间时标为未提供，不用浏览器读取时间替代；一个月前的报告仍保留，不冒充当前异常，不随新监控批次清空。页面访问不触发诊断，不周期轮询分析结果。异常触发/用户显式分析操作按未来冻结契约处理，不能自动调用。
- 业务建议卡片不展示“未完成/处理中/部分结果/失败”等任务状态，不将真实读取错误伪装成“暂无建议”或“没有问题”。技术状态若有管理入口，应在交互讨论中确定，不混入业务建议排序。
- 工具、turn、session、loop等证据只按后端真实提供能力展示；原型构造例子不是已取得完整调用链的证据。不提前实现自进化Agent界面。
- 两类分析分别记录契约版本与就绪情况；某类未就绪就明确缺口，不从另一类类推字段。若用户决定分阶段接入，再按批准范围调整计划，不自行宣布整个模块均已就绪。

## HTML视觉研究入口（不是生成源码阅读任务）

HTML的用途是直接理解前端设计的风格、配色、布局与可见交互，不要求先读.py生成器或多份JS/CSS文件。它不替代对应阶段的产品/后端设计与接口契约，也不要求正式前端实现为单个HTML。视觉入口采用自包含HTML：`docs/tasks/viewer/prototypes/tokenscope-v2-demo-ui01.html`。样式、脚本和合成数据均已内联，无需安装依赖或同时打开源码文件；SHA256为`28518db9eae0f1f2d8921c8a02e6bc66e3d20485804508073026101b0cb916ee`。先通过浏览器查看本任务页面、范围切换和关键交互，不把约1MB的HTML/JSON全量输出到会话，不先读生成器与全部样例。需要查样式或某个交互时再按CODEMAP定位局部源码。直接打开docs中的HTML即可研究视觉，不依赖HTTP服务；按需预览不调用正式后端。旧UI-01不可覆盖，后续优化另存版本。

## 已完成原型的保留与复用（开发起点）

用户明确：撤下HTTP预览只代表停止预览服务、移除误导链接，**不代表删除或废弃已完成的.py、HTML、CSS、JS及样例/检查脚本**。用户版监控增强、搜索排行、MA规格下全部UUID与流量趋势、异常分析四部分展示原型均已完成，必须作为后续优化和开发起点，不得从零另造一套视觉。它们是展示原型，尚不是接入真实后端的V2/分析正式实现。

- 视觉阅读入口仍唯一指向`docs/tasks/viewer/prototypes/tokenscope-v2-demo-ui01.html`，直接研究风格、配色、布局。正式实现必须沿用审批通过的配色和布局。
- 监控V2原型源码保留在`artifacts/prototypes/monitoring-v2/`：`build_demo.py`、`prototype.js`、`prototype.css`、`index.html`、`tokenscope-v2-demo-ui01.html`、`check_demo.cjs`及摘要。覆盖用户增强、搜索排序和MA页面，并整合已有报告。
- 报告/监控基线保留在`artifacts/prototypes/monitoring-v1/`：`build_demo.py`、`monitoring-demo.template.html`、`tokenscope-monitoring-with-reports-v2.html`、`report-ui.js`、`report-evidence.js`、`report-ui.css`、`report-fixtures.json`等。异常分析前端复用这些已经完成的证据/建议/收益展示结构。
- 先看docs中HTML，进入获授权的具体优化/开发阶段再按需读取对应源码、迁移已有布局/样式/交互；“非首次必读”不等于“可删除”。新版本另存，原起点及摘要保留。不得把生成器重跑覆盖基线或把原型合成值直接接入正式指标。

## 开始条件和第一次回复

先理解职责、完成P0及与本任务有关的P1阅读，核实实际会话ID；能获取则记录来源，不能获取则写“未知”，不得沿用其他session ID。只登记自己的角色/状态，不覆盖其他session进展。首次回复简要说明：职责边界、已读权威入口、当前后端/契约就绪情况、下一步及仍缺哪些材料。

正式进入前端方案设计的前提是：对应产品与后端设计基本固定，接口契约已明确冻结且可定位。建立接收记录，列出实际路径、版本/摘要、批准/冻结依据、适用范围，以及成功/空值/错误等可得样例；样例缺项列为衔接问题。不要因文件名含DESIGN、存在Schema或旧文档写“已完成”就自行判定前置已满足。

未来设计/契约尚未固定或路径不明时，从任务ENTRY和维护方现有交接寻找；仍缺少则向用户报告具体缺口，停留在职责理解/材料接收，不臆造接口或抢先优化实施。固定契约不要求后端代码已经全部实现：可以用契约样例设计和验证，但必须区分mock证据与真实联合验证。V1冻结S0不能冒充V2或分析模块的新契约。

## 与用户共同工作的顺序

1. **职责理解**：完成上述首次回复，让用户check定位；不在同一轮越过后续审批。
2. **阅读后端设计**：按入口阅读已固定的产品/后端设计和契约，整理“展示需求—后端字段/语义—当前可提供内容—缺口”。只按问题读相关源码，不自行设计分析算法或改变监控口径。
3. **先提DEMO优化意见**：结合后端实际能力，逐项说明原DEMO位置、建议改动、理由、数据依据与视觉影响。先与用户讨论，用户认可意见后才生成新的HTML；必要时多轮讨论/修改。无须改变的部分明确沿用，不为重做而重做。提供沉淀在docs中的自包含HTML文件链接，作为视觉评审入口；不要求运行HTTP预览服务。
4. **HTML审批**：用户明确批准后记录该稿路径、版本、SHA256、审批文字及代表性桌面/窄屏截图；保留上一版，不能覆盖基线而失去追溯。批准仅针对该稿，不将未讨论的行为一起冻结。
5. **设计前后端交互**：HTML审批通过后才展开正式交互方案，并与用户多轮讨论、优化。说明页面状态、读取/通知、缓存和版本一致性、筛选/搜索/排序、明细与返回定位、缺值/错误、加载反馈及必要导出等；只覆盖批准范围。逐个映射已冻结契约。发现接口缺口须提出具体影响、备选方案和迁移需求，由用户及维护方决定，不改后端契约迁就页面。
6. **设计开发方案**：交互方案经确认后，形成batch级开发方案、代码范围/现有组件复用、必要组件及依赖、数据契约身份、验证与测试门槛、独立视觉验收、风险/回退和联合验收交接。新增组件/类在方案中明确。计划获用户审批后才进入正式代码开发。
7. **逐batch开发**：每批实现→验证/测试→修复→问题/测试/闭环文档→增量记忆，满足已批准门槛后自行进入下一批，不逐批重复申请。最终完整前端交用户审批。普通缺陷/测试失败自主解决；只有无法解决、需改总方案、增加未约定组件/类、改变验收门槛或涉及后端契约变更等重大问题，才暂停相关开发并与用户讨论，不能删断言换通过。

上述是阶段门槛，不能以自主推进为由跳过DEMO意见认可、HTML审批、交互确认或开发方案审批；也不能为已经通过的同一阶段重复索要批准。

## 视觉实现硬约束

- **最终获批HTML就是视觉实现规格，不是只取配色的参考图。** 直接沿用/迁移其页面骨架、配色、侧栏与顶栏、筛选栏、卡片数量/顺序/列数、信息密度、间距、字体层级、表格和图表布局、响应式行为；不得擅自替换为另一套模板或UI主题。
- 数据接入和工程拆分必须服务于既定视觉。不得把可折叠的时间/版本/配置等辅助信息扩成大面板、挤掉主要指标与图表。真实长文本、空值或极值需要布局调整时，先提出最小变更理由；显著变化重新获用户认可。
- 每个相关batch用同一视口和尽可能一致的样例/选中状态对照获批HTML与实现，保存截图/差异说明；真实数据与合成数据不同导致的内容差异另列，不能伪称像素完全一致。未批准的布局/配色变化必须修复，不能自动更新截图基线把偏差变成“通过”。
- 功能测试通过不等于视觉通过。最终必须单独提供视觉一致性记录、待用户人工验收的真实实现HTTP链接及对应版本；agent截图检查不能代签用户批准。禁止只提供旧原型链接冒充正式实现验收。
- 沿用项目已有前端栈和样式基础；不擅自增加UI框架、组件库、CDN或未知依赖。原型中的合成数据/估算不得进入正式产品冒充后端结果。

## 开发与交接契约

- 前端消费权威结果，不重做Tokenizer、Chat Template、理想命中仿真、诊断、分位数或TTFT性能模型。格式化/交互与统计语义分开；null不补零，大整数、UTC原值/北京时间展示、身份和排序范围按冻结契约执行。
- 冻结契约由对应后端维护。前端记录消费版本/摘要，用明确标注的契约样例做边界测试；后端实际结果、mock、浏览器、联合、现场证据分别记录。接口变更走版本/兼容/迁移协商，不静默编辑Schema、生成类型或后端实现消除冲突。
- 正式代码继续在apps/viewer内增量实现，不复制第二套应用/数据层。变更前读最新git状态与SESSIONS，保留其他人的工作。两个前端会话共用app.tsx、全局样式、路由、API/状态/缓存和锁文件：先登记具体修改范围和依赖；一个会话维护同一公共改动，另一个基于其固定版本接入，不同时重写整份共享文件，不自行新增第二套契约。
- 授权内本地开发和测试，不用反复构建Docker验证日常改动。真实后端联合测试要明确版本、范围、负责会话及可写环境，禁止误用生产数据或覆盖其他人的服务/状态。
- 每批至少CONTEXT、PLAN、ISSUES、TESTS、RESULT，记录命令/版本、失败修复、偏差和回退，增量更新记忆、ENTRY和CODEMAP。既有V1/F007已闭环记录不重开、不篡改；涉及V1能力时保持既有有效门槛，导出内存仍以已批准的64MiB优化目标/256MiB验收上限及相应测试为准，不盲目套到不涉及导出的功能。
- 最终提供代码/设计/契约身份、视觉批准、实际测试和已知限制的交接清单。打包前统一审查、镜像/代码包交付由审查打包session负责，正式交付镜像/代码包及部署仍须用户另行授权；独立复审阶段本机临时测试镜像已由本轮用户明确允许，详见末尾复审边界。前端不能用UI审批代替打包批准。
- Git遵循docs/operations/GIT_WORKFLOW.md：不使用PR，通过检查后的源码按约定合入main并显式push origin main；不可混入他人未完成改动，不上传交付包/镜像/真实数据，不合并含产物backup分支。
- 不自动创建、唤醒其他session，或委派/发送消息；用文档和明确交接材料衔接，只有用户明确要求时才执行跨会话操作。新session ID未实际取得之前标未知。

## 本会话产物位置

- 正式开始后，前端文档放docs/tasks/viewer/analysis/，维护自己的ENTRY、DESIGN、BACKEND_ALIGNMENT、ACCEPTANCE、CODEMAP及batches/<实际批次>/；两类后端契约的接收记录分列。不能覆盖两个分析后端的DESIGN或公共契约。
- 新的报告DEMO自包含HTML沉淀到docs/tasks/viewer/analysis/prototypes/<版本>/，生成源码/开发材料可留artifacts/prototypes/analysis-v1/；复用既有获批HTML骨架、样式及可用证据表达，记录所继承的UI-01摘要。UI-01本轮合并报告是参考起点，不另行修改其冻结文件或监控V2原型来与另一会话抢写。
- 测试截图/日志放artifacts/validation/viewer/analysis/<批次或原型版本>/；自己的增量记忆放memory/tasks/viewer-analysis.md，公共viewer记忆只维护交接摘要。仅到对应阶段再创建产物，不因prompt列目录而提前生成全部方案。

现在先完成真实session身份登记和两线接收记录，输出简短职责/就绪结论，列出实际接口与旧DEMO的差异，再提出前端接入与交互设计计划。优先复核以下边界：

1. 手动appid与异常原因；low_hit先低命中再Token，长度/QPS只Token；页面访问不提交分析。只对正在跟踪的任务查询状态，终态停止，不能周期重算。
2. TaskReceipt七种状态与EvaluationResult状态分别解析；partial不等于无问题，失败不覆盖旧报告，report_ref可用才读成果。现无任务列表/最新报告查询API、无创建/完成时间或百分比进度，不虚构这些字段。
3. 小范围完整且严格>1pp才自动full；full严格>1pp才低命中优化卡片。显式direct_full标绕过pilot。L4/L5差异证据、Token报告独立展示；不因display_eligible=false隐藏Token、零/负收益。
4. L4/L5两条完整JSON，工具漂移两端不同路径；Token同请求多位置/index引用；保留大整数与原始文本，不用前端计算诊断、Hash稳定ID或收益资格。
5. 公共capabilities与专用实例header；分页无total/has_more；子任务证据可能需要父task_id；完整Plan预算、scope和模型资产身份按后端成果显示。
6. T3事实不等于删除授权，候选评估要有真实参数/业务依据；组合只能引用已存同scope Plan并独立回放，收益不能相加。

本次启动默认完成接收核对与设计计划，不直接优化DEMO或开发代码；若用户同时给出进一步明确授权，则按最新授权推进。不要打包、部署、发送跨会话消息或自动创建其他会话。

## 本次启动的明确任务与交付（2026-10-31统一版）

本轮用户已明确要求创建并启动你这个前端session；不需要再次询问是否启动。当前只完成身份/职责理解、两类后端及公共层接收核对、补充上下文和前端接入方案草案。允许阅读和整理项目文档，不修改业务源码、不生成新DEMO、不提交诊断/离线评估任务、不构建镜像或交付包、不部署、不进行Git收口。后端设计审批和本启动授权不代表前端设计或编码已审批。参数错配维持独立研究；Loop等过程分析未提供完整证据时不纳入首期实现。

你的完整职责是：①设计两类分析的展示界面；②设计前后端交互、状态和错误恢复；③给出开发设计文档与分批计划；④获批后逐批前端开发、测试、debug与验证；⑤完成真实前后端端到端联合测试；⑥最终整理供“镜像打包和审查”session独立执行的完整复审prompt。当前执行前述接收与方案准备，后续职责依既定审批顺序推进，不能一次性启动全部阶段。

P0先核实自己的真实session ID与来源，更新memory/SESSIONS.md中“异常分析前端设计与开发”这一既有角色；不要复制后端ID。创建方会根据create_thread返回值登记，操作前重新读取该行，仅更新自己的实际核实信息，保留其他行。若环境不能读到自身ID，使用创建方登记的工具返回ID并如实标记尚未环境复核。新建自己的memory/tasks/viewer-analysis.md和docs/tasks/viewer/analysis/ENTRY.md；所有操作明确以TokenScope为工作目录，即使启动所在项目根是其上一级/home/zhangxiyue。

完成docs/tasks/viewer/analysis/BACKEND_ALIGNMENT.md，三方分列记录：权威路径、契约/实现版本、manifest或源码摘要、批准/冻结依据、后端已有测试、此次实际检查、接口与样例缺口、结论及负责方。公共/低命中主入口是docs/tasks/prefix-analysis/FRONTEND_HANDOFF.md；Token主入口是docs/tasks/length-analysis/FRONTEND_HANDOFF.md；公共职责入口是docs/tasks/analysis/BACKEND_IMPLEMENTATION_HANDOFF.md。不得把后端历史112项或193项等通过记录写成前端本轮复测通过。

接收依据：analysis-common-1.0、diagnostics-http-1的README/wire.json/manifest.json；低命中SELF_REVIEW_20261031.md及SELF_REVIEW_CODE_IDENTITY.json（low-hit-backend-local-2）；Token batches/TA006/RESULT.md及CODE_IDENTITY.json（token-content-1）。先核对有效文件与摘要；差异记录为待确认，不自行更新冻结摘要掩盖差异。没有已启动服务时，完成静态接口核对并明确运行时capabilities/真实联调待后续验证；不为本次接收启动服务或构造“已联调”结论。

接入方案草案可落到docs/tasks/viewer/analysis/INTEGRATION_PLAN.md：需求—路由/字段—状态—组件/交互—证据—缺口矩阵；低命中与Token分别说明，列出UI-01需调整处、理由和后端依据。首轮只提方案和待确认项，不越过DEMO/交互/开发计划审批。首次完成回复给出真实ID、职责、接收结论、缺口和文档链接。

## 必须逐项核对的Token和公共差异

- /diagnostics/capabilities免实例header，其余用x-tokenscope-service-instance。request/options按HTTP wire；元数据整数为十进制字符串，JSON文本内部业务数值不可擅自转换。原文、大整数及精确分数保留，不以JS浮点重算展示资格。
- 三层分别是TaskReceipt、stage/RuleResult、EvaluationResult。queued/running/ready/partial/empty/failed/interrupted不是全部规则的共同枚举。任务管理状态独立于业务建议卡片；partial保留已完成证据及覆盖局限。报告可stages=[]，prepare被阻断时可能只有reason_codes；不能强制每份报告都有evaluation。
- Token结果在items/fragment的data内：request_key、raw_sha256、locations、units、observations、finding_candidates、modification_candidates、rule_results、coverage、reason_codes。低命中的items/finding不能代替Token结果集；T3有Observation但没有Finding仍有可展示事实。
- fragment_id取列表item.id；items/fragment_index中location_ids/unit_ids/observation_ids与相应数组同序，不自行哈希生成ID。单项GET直接返回data；分页只有items/offset，无total/has_more，满页继续、不足一页结束，不能将已加载页当全scope统计或排序。
- Token原文取requests/{fragment_id}，低命中双请求取comparisons/{finding_id}；评估子任务须保留父task_id回溯源证据。raw_body_complete与capture_truncation含义不同，unknown不证明源头未截断。展示完整原文不能以64KiB预览代替；安全文本渲染，不执行请求内容。
- Location用source_pointer和可选embedded定位内嵌JSON；embedded=null与内嵌pointer空字符串不同。通常没有原文offset，不使用全局首次字符串匹配冒充精确定位，不用JSON.parse/stringify覆盖原始数值/文本。显示外层路径、内层路径、parser版本及原文上下文。
- ContentUnit的字节/字符/行/项/字段计量不是Token贡献；participation为included/ignored/unknown，unknown不能视为已入模。按RequestKey、位置与unit引用辨别重复/父子重叠，不跨卡片累加重复字节。content_inventory/met不自动等于异常；无业务policy只展示事实或机会，不制造阈值。
- T3仅证明同一请求中的完整精确重复（至少含tool相关位置），不证明执行次数、Loop或可删除性；一个请求多个位置不可伪造成两条请求对比。T4的keep_last明确区分未填与0；later_message_count不是turn数/时长，多段tool结果按真实容器关系展示。
- token-evaluations使用已存fragment/candidate、真实parameters_json与business_basis_ref，返回新任务。T3的token-authorizations只引用已存Observation、selected_unit及支持的handler，不能预填虚假业务授权、引用地址或任意JSON路径。
- combination-evaluations只引用2–8个同原scope的已存非pilot Plan，冲突阻断且无after；收益须独立回放，不叠加单项。GET只读已封存成果，不触发分析。
- 低命中完整full/direct_full且严格提升>1pp才符合优化卡片门槛，精确等于1pp不通过；pilot不能冒充full。Token及其组合不受该门槛限制，gate=null/display_eligible=false不代表隐藏；零收益、负收益、P下降但C上升均保留。available之外不补after=0；行证据只在可用评估读取。
- 展示n/j/p/h/c及其范围：P=H+C，R=H/P（P=0为null），j不是p；gain_percentage_points保留精确分数，compute_tokens_delta=after.c-before.c为正表示计算Token增加。不推断输出Token、质量、费用或性能收益。

典型接入样例必须覆盖：L类完整>1pp与恰好1pp；Token 65536字节但参与未知且无policy；同请求三个位置重复但未授权；T4 keep_last缺失/0；P从10000降到8000而C从2000升到3000；阻断无after；Token等待中仍保留旧报告。完整JSON优先引用两份FRONTEND_HANDOFF中的已校验样例，标明构造样例不是现场事实。

## 后续独立复审prompt的责任与授权边界

完成获批开发、前后端联合测试和用户视觉验收后，整理一份可独立复制的docs/tasks/viewer/analysis/INDEPENDENT_REVIEW_PROMPT.md，交给“镜像打包和审查”角色（当前登记ID为01a1800e-80b4-7400-a78b-a84f5b6e888d，交付时重新核对memory/SESSIONS.md）。现在不启动或发送复审，不提前代填未产生的候选SHA与测试结果。

该prompt必须写清：前端ENTRY/DESIGN/BACKEND_ALIGNMENT/ACCEPTANCE/CODEMAP、实际批次RESULT和联合测试记录、两份后端FRONTEND_HANDOFF及公共冻结契约；候选分支/commit或未提交文件清单与摘要、前后端/契约/资源/锁身份、视觉批准路径版本SHA、可复现命令与环境、已知问题和回退。候选有变化则重新绑定并补测，不以共享工作树的旧SHA证明新内容。

复测重点包括：实例隔离与幂等；分页和三层状态；低命中门槛与Token零/负收益；完整JSON/内嵌定位、大整数和安全渲染；T3真实授权、T4参数；单项/组合评估、冲突/取消/恢复；无后端任务目录时的已知任务管理；页面读取不提交分析；真实浏览器到两类后端闭环；UI一致性和监控V2兼容。mock、真实后端、浏览器、容器及现场证据分别记录。

用户本轮明确给出的后续复审授权是：**允许审查session构建/运行本机临时测试镜像；独立复审通过后统一Git收口并显式push origin main。** 这是用于已完成候选的后续审查，不能扩展为当前前端编码、日常反复构建、正式交付包制作、发布或远端部署。复审未通过先按责任修复并复测，不提前push候选。Git不使用PR，不混入其他session未完成改动，不上传真实数据/代码包/镜像/backup分支；记录最终main SHA和远端核实结果。正式打包/交付与部署另按用户当时授权执行。

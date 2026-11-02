# 完整服务本机合成数据端到端验收

2026-11-01。用户最新要求：先对本次全部待验收功能做本机合成数据端到端，通过后再给华为机执行。总负责session `01a1800e-80b4-7400-a78b-a84f5b6e888d`，环境ID已核实；[职责交接](../analysis/ONSITE_COORDINATION_HANDOFF_20261101.md)。当前结论：修复候选本机合成验收通过。下表保留执行前门槛，实际结果和限制见后文；旧冻结镜像仍含FS-01，不算已修复交付。

固定发布`tokenscope-rv2-20261101`、源码`45d9285210dc0b9edeb86c599c7b6bcd942f60b5`、镜像`sha256:483db762852b38ef54559cff1bb23ef668ea9296a055ce02aac44a809b427ce5`。复用镜像，独立Compose项目tokenscope-full-synthetic与18062端口，新input/state在`artifacts/reviews/full-service-synthetic-20261101/`。不重建镜像或修改旧包，不触碰4191/8016、旧RV1及其他session修改；旧测试结论只作覆盖入口，不代替本轮实际执行。

## 功能矩阵与复验门槛

| 编号 | 功能/数据前置 | 操作及预期 | 失败归口 |
| --- | --- | --- | --- |
| E01 | 冻结镜像/新空state/三模型资产 | 镜像、dist、版本/契约一致；CPU/只读root和input/state可写；同源前后端 | 总负责 |
| E02 | 新生成三模型CSV | 显式基础任务→真实worker→15范围/回执/SSE/导出；模型模式与质量明确 | 用户后端 |
| U01 | 三模型有效小CSV、新common_name绑定 | 用户新建/已知ID/最近记录/历史base绑定；ready、base/user身份隔离，GB appid×服务不串 | 用户后端/监控前端 |
| U02 | 已发布user/base/APPID | 六卡、J/P/C分布、分位、冻结配置/整文件质量；精确值/空与零；切范围不混旧值 | 用户后端/监控前端 |
| U03 | 请求重复hash及>50行、不同长度 | hash精确/前缀、区间、排序、分页/辅助图；重复ID保留，详情/原文/字节证据只读 | 用户后端/监控前端 |
| U04 | 已完成范围与组合筛选 | CSV/NDJSON全筛选导出，记录数/摘要校验；取消/换run/换appid/离页停止旧文件提交 | 监控前端/用户后端 |
| U05 | 隔离模型配置/阈值 | CAS、冲突保留草稿；变更只影响后续运行，历史冻结不变；无默认生产阈值 | 用户后端/监控前端 |
| R01 | 29个APPID，Case-App/case-app/literal%_appid | 命中/无结果/大小写/字面%_；300ms/Enter，查询服务端全量 | 用户后端/监控前端 |
| R02 | 可独立CSV计数的APPID集合 | 四指标排序升降、含端点AND上下界；非法/倒置拒绝，缺值末尾 | 用户后端/监控前端 |
| R03 | >20 APPID的固定revision | 首/次/返回页稳定无重漏；切条件回首屏、旧revision409、不混旧结果 | 用户后端/监控前端 |
| R04 | 1K/2K/5K与并列众数 | C开放箱/均值sum/count/最低并列代表；全部并列分页，返回保留筛选与页码 | 用户后端/监控前端 |
| T01 | 无性能参数与显式合成参数 | 缺W/K/τ不出比例，W明确0有效；新模型不提交O，正确tag；不伪称校准 | 用户后端/监控前端 |
| T02 | 不可变情景及多组条件 | le/lt、0%/100%/无预算/范围外/无正P90；输入变动/迟到失效，旧W+O只读 | 用户后端/监控前端 |
| M01 | 新pre/now各连续1h，双UUID/跨APPID | 显式提交与幂等；同UUID预热共享、跨UUID隔离；全UUID表，无额外规格混算 | MA后端/监控前端 |
| M02 | 生产字段/本地编码一致和不一致样本 | Q配对/独立理想真实/coverage及null/0；实际高于理想不擅自判错 | MA后端/监控前端 |
| M03 | 分布/12个5分钟桶/整小时 | 两张独立分布、尾桶/样本数、零未命中；空桶0/无有效真实null，率守恒不插值 | MA后端/监控前端 |
| M04 | 仅pre、无pre、空now、预热冲突、质量错误 | 全行展示/独立重试、错误定位pre/now、空态与失败区别，历史保留 | MA后端/监控前端 |
| A01 | 新生成合成请求及真实worker | 默认空recipe路径与显式测试recipe路径分别验；新ready报告、身份/范围/摘要正确 | 公共/Token后端 |
| A02 | L1–L5代表输入 | L1–L3完整收益门槛；L4/L5各至多一卡≤3例，全RequestKey去重，局部证据/限制保留 | 公共后端/异常前端 |
| A03 | T2–T4显式构造recipe | 影响/建议/量化P及C/局部证据，零/负收益/P降C升/缺basis/授权边界，不冒充生产策略 | Token/公共后端/异常前端 |
| A04 | 两个ready及较新partial、同源两方向 | 默认ready、固定历史、详情刷新/返回；partial/empty不覆盖，页面零诊断写请求 | 公共后端/异常前端 |
| A05 | 真实terminal SSE和重连 | 通知后对齐目录，无任务周期轮询；游标重放/去重/reset/实例变化与只读错误恢复 | 公共后端/异常前端 |
| C01 | 新任务+B旧完成A、失败/中断/迟到 | 用户/MA非终态60秒串行读，终态停，离页取消；失败保留A、成功整体替换 | 监控前端/相应后端 |
| C02 | 提交丢响应/异体键/错服务身份 | 原键原内容查回，禁止自动新写；身份409清旧缓存/在途/原文/导出 | 各前后端 |
| C03 | 所有已发布功能成果 | 容器重启持久身份/回执/历史/排名/评估/报告/导出一致，GET不触发计算；内部SQLite分配计数单列 | 总负责/各后端 |
| C04 | 同时排队、失败任务/重复读 | 单worker资源额度、无半成品发布，显式新任务重试；仅独立验收state操作 | 总负责/各后端 |
| C05 | 桌面1440/窄屏390真实页面 | 布局/可操作/无脚本错误；源码模块及受控故障测试单列，不冒称真实后端 | 两前端 |

依据为监控V2交互第10/11节、用户2.0.0及MA1.0.0、S0与diagnostics四项冻结契约和45d9285实际代码。MA无原文导出/SSE，用户无全服务运行/情景目录；不测试不存在的产品能力，也不借此省略已支持流程。极大数/特定故障可用受控边界，须与新合成数据真实worker/浏览器路径分列。

## 执行和结果记录

先新空state完成基础/用户/MA，补搜索独立oracle、真实导出与状态恢复。公共/Token维护方仅提供可重建合成种子与显式测试recipe，在新隔离目录通过HTTP真实worker重新生成异常结果；原RV1封存只作为历史兼容补充，不冒充本轮计算。每项最终关联命令、输入/源码SHA、网络/截图/结果及未覆盖事项；真实缺陷由总负责直接归口，原失败保留，修复后独立复验。

当前没有华为现场结果，也没有真实性能校准或生产策略批准。新版完整华为prompt在本轮矩阵结果收口后另存prompts/delivery并单独记录版本/SHA，冻结包内旧prompt/SHA256SUMS不覆盖。若业务修复改变源码，记录新候选与受影响复验；新交付版本另行按用户安排收口，不能继续声称旧镜像已含修复。
## 本轮实际结果（修复候选已通过）

原冻结镜像完成了以下新增真实数据链；随后发现FS-01并交异常前端归口修复，原失败保留，见[问题与辅助修正记录](FULL_SERVICE_E2E_ISSUES_20261101.md)。旧包包含该缺陷，不能继续给旧包完整通过结论。候选仅修改SourceLink一行参数，以独立dist只读挂载同一镜像进行容器复验；不是重建镜像或正式交付。

证据根目录：`artifacts/reviews/full-service-synthetic-20261101/`。实际服务实例`f99cb514-ba26-4846-9c1e-6382f0b655f1`。本轮所有业务输入和任务均在新state中生成，通过HTTP真实worker处理；旧RV1的CSV构造方式可以复用，旧SQLite/报告未导入。

| 矩阵 | 实际执行与证据（相对证据根目录） |
| --- | --- |
| E01/E02 | `identity-start.json`、`container-inspect.json`、`compose-resolved.yaml`；`base-acceptance.json/log`：三模型15范围，真实任务/回执/幂等/SSE/CSV/NDJSON。DeepSeek仅本隔离state显式thinking_disabled，CAS前后见`test-mode-config.json`。 |
| U01/U02 | 39项监控浏览器回归中的真实三模型、新建、打开、绑定、六卡/质量/历史；`v2-browser.json/log`。APPID计数及P=H+C独立核验见`real-search-api.json`。 |
| U03/U04 | 新120行/29APPID，search-long65行、重复hash两行；50+15明细分页、精确/前缀/空结果、半开区间、详情/原文/轻证据、筛选CSV与NDJSON SHA。`real-search-api.json`、`real-search-browser-final.json`。导出取消的网络延迟控制独立标注；其余换run/范围/离页/流尾/身份等受控边界保留原断言。 |
| U05 | 真实CAS revision1→2→3，过期键409，原snapshot不变，新增run使用mtp=false，缓存H384→512，最后恢复mtp=true。`settings-real-cas-final.json`。3项设置/阈值/回执浏览器受控测试见`operations-browser.json`。 |
| R01–R04 | 29 APPID独立CSV计数，大小写/字面%_、无结果、20+9页、revision409、4指标×双向排序、含端点AND、非法422；29组×3箱宽从逐请求独立算并列峰和均值。`search-oracle.json`、`real-search-api.json`。大整数/NULL/>200K并列峰属于监控套件受控契约边界，未冒称实际CSV出现这些极大值。 |
| T01/T02 | 监控浏览器真实新tag情景/评估、显式W0、缺W/禁止O422、0%/100%/no_budget及旧W+O读取；迟到/失效和其他边界有受控与组件测试。仅算术和产品功能，不代表真实TTFT性能校准。 |
| M01–M04 | 真实13UUID/质量、预热冲突/empty与UI行重试；另构造5UUID独立oracle：warm跨APPID缓存共享，cold隔离、pre-only、无真实值、真实有效而JSON坏、200K尾桶、实际/理想配对及错配计数、12×300秒与3600秒守恒。`ma-independent-actual.json`、`ma-independent-result.json`。P764、输入实际H640，开启MTP的理想重复H512。 |
| A01/A04 | 新HTTP生成两ready、一更新partial，默认仍第二ready；ART4四种明确合成策略，不是生产默认。`public-fixture-handoff/prepared-config/actual-http.json`。另在去掉recipe环境变量的原始compose运行user_v2来源新任务，`default-empty-recipe.json`确认0配置/0建议，真实来源绑定不变。 |
| A02 | 新真实L1及L4/L5报告，6条范围，每类一卡≤3例，全量影响去重；独立追加L2同工具集合顺序、L3动态工具内容，full完整收益>1pp。`new-L2-L3-actual.json/result.json`、`analysis-browser.json`及修正opaque链接后的`analysis-browser-retest.json`。 |
| A03 | 新a/b/a及256条边界扫描，实际找到boundary-7单请求P513；6项合成策略逐一检查0/未知/负收益/共享evaluation但不同basis，另边界P1026→1022、C642→766。`token-boundary-selection.json`、`token-boundary-actual.json/result.json`、`new-boundary-browser*.json`。所有recipe均synthetic，未批准生产内容删除或远端引用。 |
| A05 | 新任务提交前cursor真实SSE重放3终态、从首事件续接余2、坏cursor reset、错实例409；`diagnostic-sse-result.json`。浏览器真实21秒无额外诊断轮询及离线重连；极端迟到/身份重置为受控边界。 |
| C01/C02 | 监控60秒串行周期、终态/离页停止、失败保留/新成功替换、丢回执原键原体、身份409与缓存/原文/导出取消，真实任务和受控故障分别见71项最终浏览器报告中的各用例。 |
| C03 | `full-service-restart.json`：476个地址重启前后字节SHA相同，业务控制表逻辑摘要不变，GET未触发计算。包括用户/MA/情景/评估/基础导出、异常目录/历史/建议/局部示例。`diagnostic-sequence-restart.json`单列内部sqlite_sequence 30→40、终态10条不变；公开游标、epoch、业务行未变，不声称整个SQLite文件字节不变。 |
| C04 | `queue-concurrency-final.json`：真实HTTP同时排队base/user/MA/diagnostic，在共享worker.lock占用时不执行，释放后四类均完成；queued取消为interrupted，不发布/不进报告目录，显式retry另ID且幂等。`crash-recovery-result.json`：只对本验收容器在真实base running时SIGKILL，恢复interrupted，无半成品，显式新提交completed。 |
| C05 | 1440/390截图与布局/无脚本错误断言；人工复核本轮搜索组合筛选、L1/L4/L5列表及P降C升移动详情，精确值/警告/局部证据可读。截图位于screenshots-analysis、browser-results与最终candidate-all-browser-results；前端203单元组件独立运行见candidate-unit.log。 |

矩阵覆盖已实现功能的代表性端到端和相关故障边界，不等于无界数据穷举、生产性能压测、真实业务质量或现场通过。源码模块用例v2-api.spec.ts依赖Vite /src导入，不属于正式dist容器71项；相同提交/客户端行为由真实浏览器操作和V2Client单元测试覆盖。旧4193开发重定向也不属于此隔离发布端口验收。

华为新执行说明另存 `prompts/delivery/HUAWEI_FULL_SERVICE_ACCEPTANCE_V2_20261101.md`，版本full-service-onsite-v2-20261101。它明确保留旧包身份、FS-01正式交付门槛、完整功能矩阵/失败归口/真实数据与校准缺口，不因本机合成通过自动部署或生产切换。

## 最终独立复验与版本结论

**本机修复候选通过：71项浏览器全部通过（无跳过/失败，2.1分钟），203项单元/组件全部通过。** 39项监控V2、17项异常回归、4项真实搜索/导出、3项新Token/MA边界、3项设置/回执受控边界、2项L2/L3与默认空策略/来源、3项来源跳转回归，共71个不同用例。真实HTTP与受控DTO/网络条件按前表区分，不把所有项称为无mock真实数据。

FS-01已由异常前端归口修复，总负责独立核对仅SourceLink把user_run_id参数改为run，保留身份检查/取消保护；[归口交接](../viewer/analysis/SOURCE_LINK_FIX_20261101.md)。源码SHA256 `23bc15b0cc4d188def35ce2906b4c8ba8ed45ce40a7a66b183f2fa1336ac4b14`。候选dist独立复制并只读挂载 `/app/apps/viewer/dist`，4个HTTP静态资源逐字节核验；CSS与导出worker保持原字节。主JS `index-DHpQ3Bex.js` SHA256 `35c3178466d735a379d593d3e4cd24fbbde1c2f5f09a945a4553995f6a52982b`；index.html SHA256 `55ad4d514b8ccd81e60bca978d6839e1876f41dacfd84848460116df60c7a88c`。没有构建新镜像、制作交付包或推送Git。

完整候选/锁文件/8编码资产/输入/测试摘要在[结构化结果](FULL_SERVICE_SYNTHETIC_RESULT_20261101.json)与证据identity-final.json。除一行业务修复外，后端/契约/依赖锁相对45d9285无改动。原发布14文件逐项SHA保持；其他session原8份修改保留，其中MA入口/记忆在本轮并发追加了用户现场数据交接，前后摘要单列，不覆盖或误称全部字节未变。

本轮专用18062容器已移除，专用Docker daemon按PID及data-root/exec-root/socket核实后停止；新state/input/失败trace/所有证据保留。4191/8016共享服务健康，本线候选预览4196由维护方关闭。没有华为部署、桌面写入或用户视觉代签。

正式交付仍需后续把此修复纳入源码/镜像/代码包版本并复验发布身份；旧tokenscope-rv2-20261101包不得冒称包含修复。现场环境、真实CSV尤其MA两窗口/UUID/规格、TTFT真实校准、生产策略/引用服务均待实际执行；当前结论仅为本机合成数据功能验证通过。

新版华为prompt：`prompts/delivery/HUAWEI_FULL_SERVICE_ACCEPTANCE_V2_20261101.md`，SHA256 `809cb35673d749d31e6ad1f88d76c507e41f7a869725d2d126460dd059e958e3`。可直接交现场Agent阅读，但其执行门槛明确要求取得包含FS-01的正式交付，不能直接替旧包放行。

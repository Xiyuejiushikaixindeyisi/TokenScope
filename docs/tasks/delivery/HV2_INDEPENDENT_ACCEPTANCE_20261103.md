# HV2独立验收清单与实际结果

总设计师负责；当前只固定验收范围，所有执行结果默认为待执行，不以开发方自测或旧版本结果代替。任务与依赖见[执行板](HV2_REPAIR_EXECUTION_20261103.md)。每次交接核对候选文件SHA及新契约SHA，源码在复审期间固定；各模块测试、源码E2E、容器E2E、华为真实数据及用户认可分别报告。

## 公共层第一关

- 独立阅读实际diff/源码及新增契约，旧冻结Schema与报告保持。校验方向单选/双选/空选择、capabilities、intent幂等、重试恢复；禁用方向用失败哨兵确认没有检测/提案/评估/编码副作用。
- 按真实代码区分TaskControl全局低命中保留预算与Token逐请求RunControl。超过证据保留上限仍有诚实扫描/候选/规则覆盖和丢弃计数；真实资源预算停止仍partial；不能因保留截断谎称已保存全部证据。
- partial-only、ready优先、legacy/失败/中断、绑定/方向/固定task、分页和snapshot冲突；已有L4/L5组不能随recommendation为空丢失。页面读取不提交任务。
- 零recipe不做无输出的全量提取，但状态不冒充完成收益评估；fragment不完整、无业务依据与无配置分别有可读原因。真实修改后收益门槛与授权未降低。
- 独立运行维护方测试和额外必要边界，保存命令/退出码/源码身份。通过后另写冻结签收和第二阶段任务，不把本清单当通过证明。

## 后端及契约关

- 用户：跨模型APPID目录完整分页，多个历史run的确定默认和显式固定；未知run/revision、读取零写入。参数别名/默认τ=1/2.7/2.6及K8192、更新revision/重启、K覆盖、缺配置、W=0/T边界/精确小数、P90无效和旧W+O/严格比较兼容。结果可追溯到实际参数、数据源和模型。
- MA：独立ideal/real与paired不可互填；DS式有请求无cached，GLM式真实正常但预热冲突，P=0、有效cached=0、坏JSON而R有效、仅pre/空now/空桶。独立解释字段范围正确，12桶/整小时与总量守恒；旧结果不可被GET现场补写。
- Token：公共冻结后才实施私有性能及适用性改进；保持T2–T4、合法近似负例、预算/取消/精度/身份和业务授权。profile区分解析/提取/序列化/检测/提案/准备/写入，不拿encoding_calls或terminal间隔代表成本；没有真实业务策略不造收益。
- 低命中：公共冻结后的候选/规则覆盖与预算复验，L1–L5独立计数与证据保留；L4是待关联差异，不写动态字段根因或会话改写。新增探测器需充分证据及范围决定。
- 后端通过后记录新Schema/OpenAPI/能力、样例及摘要、兼容迁移和消费者签收；旧协议仍只读兼容，前端不能去掉版本/字段校验换通过。

## 新候选完整E2E关

1. 盘点Windows/WSL项目旧服务/worker/预览/测试容器，核实归属后正常停止并确认退出和端口释放；旧state/包/证据保留。使用新独立input/state/cache和全新浏览器，不共享个人缓存。记录候选源码/锁/模型资产、dist与HTTP摘要、service_instance和端口/PID。
2. 经真实编码和后端显式提交产生三模型Trace：同APPID跨三模型/两模型及单模型对照，多历史run、空/失败对照。冷浏览器直接进入四入口，完整发现并切换，目录→receipt→snapshot→排行→TTFT→导出→异常来源各环节身份一致；不靠预写localStorage或手工task/run兜底。
3. TTFT只填等待时间/SLO，分别自动读取已登记模型参数；用独立精确算术核对当前实际P90所需比例。切模型/参数revision、延迟旧响应、K覆盖/恢复、刷新/重启和历史评估不串。缺配置/无P90与错误不能显示0%成功。
4. MA用另一组合成schema独立产生pre/now制品/UUID结果，对照上述缺失/零/独立/paired样例。HTTP→表格/展开DOM/12桶逐字段核对，缺失须可解释且不遮蔽可用数据，压力和实际未命中不改口径。
5. 异常：全部partial、ready+partial、单方向/双方向、无recipe但有L4/L5、历史固定task等。裸入口读取可用成果并标部分状态，L4/L5保持批准聚合及唯一请求数，空建议不代表无问题。选择后多页读取、失败、取消、服务身份变化、SSE重连与重启恢复独立验证。
6. 保护原搜索/排序/分页/精确大整数/范围、指针读数UIR-01/键盘UIR-02、导出取消/结构行数/SHA、缓存/事件生命周期等。旧joint选择器可按批准UI更新，但保留身份/数值/缓存/恢复/导出断言。UIR-03不纳入修复。实际页面与UI-02/UI-04及最后L4/L5对照，内容差异与布局差异分开，不以测试绿代签用户视觉认可。
7. 完成后停止临时服务并记录；若留候选预览须明确版本/停止方式。Docker阶段重新核实清理并以固定commit构建的镜像、全新state冷启，测试实际容器资源/HTTP同源/Compose/重启与必要完整回归。源码通过不冒称镜像通过。

## 发布与现场验收关

源码与非敏感文档精确提交/push main，不带原数据/包体/backup；构建资产、契约、前端实际资源和用户默认配置摘要随release。WSL新包保留旧包，桌面完整复制逐项SHA一致。本地backup仅manifest指针及必要本地版本管理，不push、不合main。真实数据单Markdown现场prompt必须覆盖停旧/环境/磁盘峰值预算/部署/用户监控+MA第一验收/指定APPID方向异常第二验收、关键源码/diff/证据正文、问题复现修复与前后结果、回退。

现场缺口单列：18MA完整SHA、Qwen48逐完整UUID、GLM26/27计数和实际冲突pre/now时间、Trace有效数差622逐行原因、>1MiB请求分布、真实tools/messages正反例/脚本逻辑以及最终DOM。可本机修复的软件问题先闭环；不可取得的真实观测（DeepSeek cached）不可补造。

## 实际执行日志

- 2026-11-03：只读资产预检：env/encoding-assets.lock.json列明8文件摘要全部一致；Python3.11.16、Node22.22.2；WSL /home约866GiB可用，当前未发现tokenscope/vite/playwright/uvicorn/dockerd进程。此项只是构建准备，仍需新候选E2E前完整双系统进程盘点。
- 已收到Token与监控前端准备交接，均只读/文档，无产品测试通过结论。公共/用户/MA仍实施中；尚未进行本轮模块独立验收、E2E、构建、提交或push。

- MA独立复核：核对交接6源码/测试SHA组合15194270d39e4e51950c83fd10d7694a3282d9c96a0b9ffbfd7c882b3d2f96f5一致，独立运行pytest tests/unit/ma -k "not test_live_http_background_worker" -q，66 passed/1 deselected/68.80s，源码前后SHA一致。证据artifacts/reviews/hv2-repair-20261103/ma/independent-regression.txt。监听用例留待统一冷启动E2E；契约工具扩展校验尚待完成，暂未冻结。

## MA后端独立验收与冻结
2026-11-03，独立源码审查、66项MA回归、13项契约工具变异测试，以及单独混合UUID边界复核全部通过。补证验证同一文件A缺cached不会污染B原因，B有效0与空桶区分，小时/12桶守恒。全部本机合成输入，未代签现场。旧MA Schema/OpenAPI路径/组件/manifest字节保持，新资源完整DTO/OpenAPI/9样例/8负例通过。
冻结清单：[HV2_MA_FREEZE_20261103.json](HV2_MA_FREEZE_20261103.json)，组合SHA `9b48fb244963ce153b009a9a2d0d9050d084bd6c1bb43eec27ddf49f313fd9fa`。冻结范围仅后端解释资源及现有指标兼容；不代表前端、监听E2E或现场通过。原预热语义保持，用户如选择新策略需独立版本/验收。允许监控前端先接入MA部分；用户目录/TTFT仍等待其后端冻结。

## 用户后端独立验收与冻结
2026-11-03，已读实际4份源码及全部差异；独立62项新功能/Trace/旧契约回归通过（10.80s，源码/契约前后SHA一致），另6个跨三模型大于2**53的P90与精确小数le/lt等号场景通过，结果以Fraction独立算术核对。维护方最终271项监控与62项CSV/编码回归日志已核对。新2.1.0共14操作、旧9操作与旧冻结文件保持兼容；GET不创建索引或评估，默认配置启动登记且参数来源明确。
冻结清单[HV2_USER_FREEZE_20261103.json](HV2_USER_FREEZE_20261103.json)，组合SHA `4d9e2e5d6c7031ff0aaa266114b92dbcb8684b9a80d722d2cfae9de8ad1d7dc0`。证据artifacts/reviews/hv2-repair-20261103/user-independent。允许监控前端接入多模型目录与TTFT；未代签浏览器/现场/真实性能校准，622条真实差异与大历史目录规模另列限制。

## 异常公共层第一关独立验收通过
2026-11-03：实际diff/源码/新机器Schema/旧27项冻结字节独立核对；独立41项方向/保留/扫描/发现/旧runtime边界通过59.91s，前后源码无漂移；最后empty终态投影修正后另跑3项API/旧报告/禁用recipe边界通过15.61s（与41有重复，不相加）。维护方331项联合回归与之后23项专项、46源码mypy及ruff记录已核验。业务GET未计算且state SHA保持；from_wire真实响应一致。
冻结[HV2_COMMON_FREEZE_20261103.json](HV2_COMMON_FREEZE_20261103.json)，组合SHA `9ac3e7fd5c5fea9556f957871bb03a0791e79e9404b207462a1cf8e184d7cb8e`。前端及现场未通过；工具/messages真实新探测器依据不足、15万请求容量未校准。现开放低命中/Token私有测试/profile及经证据支持的局部优化；公共API/Schema及旧契约不允许并发修改。两条后端通过再开放异常前端。低命中私有若改变已记录适配源码，由第二阶段独立复核补新候选身份，不回写第一关原证据。

- 前端接入中提前集成检查：MA standalone OpenAPI的Submit/ErrorEnvelope名字与真实create_app聚合名字不同，前端直接比较原始$ref将拒绝有效服务。根已保存真实full-runtime-openapi.json，递归解析全部本地ref后新增availability操作及完整响应约束完全相等（ma/runtime-equivalence.json）；已交监控前端修正握手并补漂移拒绝测试。未改后端语义或删除契约校验，此项待前端复核闭环。

## Token私有后端第二关独立验收通过
2026-11-03：独立读两份源码差异、完整profile/预算/消费记录，候选仅结构序列化复用；独立完整私有171项通过94.33s，源码前后无漂移。另用原Git实现与固定种子510种Unicode/数值词法/嵌套结构比较计量完全一致。维护方完整fragment SHA和五类预算边界记录已核对，未改插件/DSL/授权/预算或收益门槛。
冻结[HV2_TOKEN_FREEZE_20261103.json](HV2_TOKEN_FREEZE_20261103.json)，组合SHA `14419e5bba5af85a3ffa20d6330b3fa29c2d926bd81ef1f3462e30b118b4f00d`。证据artifacts/reviews/hv2-repair-20261103/token-independent。只证明本机私有与公共消费兼容，不代表真实吞吐/全规模预算、前端或现场通过；源码窗口关闭，异常前端仍等待低命中第二关。

## 低命中私有后端第二关独立验收通过
2026-11-03：独立核对3份实际源码/差异与1024对文本等价测试、276份证据摘要和24配置profile；新增原因合并保留候选截断与比较预算并存，等文本快速返回不改规则/recipe。独立62项低命中/真实user_v2公共消费/完整评估门槛/组合/资源回归通过201.93s，源码前后稳定。公共冻结仅两项已授权私有适配变化，其余公共/Schema/旧兼容全部保持。
冻结[HV2_LOW_HIT_FREEZE_20261103.json](HV2_LOW_HIT_FREEZE_20261103.json)，组合SHA `10f643bc56fa59936dcfd7d17f4aabf1163aba4d479c47662366d13c879e011b`。第一关历史冻结不回写，当前这两份prefix源码按第二关身份。证据artifacts/reviews/hv2-repair-20261103/lowhit-independent；未代签真实量级/新探测器/现场收益。现两类私有后端均通过，允许正式派发异常前端接入。

## 监控前端源码与定点独立验证
2026-11-03：已收到HV2_MONITOR_FRONTEND_HANDOFF及MA交接，50文件组合c4280716635dc0b7e0dd472cf7c98a3f6ac80cacec9125dc02ac09fc09645404逐项核对。独立审查实际客户端/完整OpenAPI引用展开、目录固定身份、自动TTFT和MA并发/缺数展示；6文件75项单元/组件回归独立通过2.02s，50文件前后SHA无漂移。证据artifacts/reviews/hv2-repair-20261103/monitor-fe-independent。此前完整301项是维护方本机结果，尚待两个前端合并后的根全量和实际浏览器/视觉；此记录不是前端最终签收。
Windows/WSL初步服务盘点未发现TokenScope服务或有关监听，项目Docker socket不存在，未停止无关进程。最终候选冷启前仍重新核验并记录。

## 前端合并与第一阶段真实HTTP/浏览器独立验收
2026-11-03：异常c3的18项身份61a430bf0ffe931fa5e91713e1a5455b0d518fc2e1293620ed1373cbe105735c独立审查后，根完整335项前端测试/typecheck/lint/build全部通过；HV2-AF-01首读/更多缓存键统一并有负向控制和独立回归。固定693输入组合99b0abf9f71b161ff27c9cf20ec29660650a4fa7f42dd0d8a55dde0b9cfddfbc，后续4份浏览器测试适配单列source-test-addendum，不改变产品输入。
Windows/WSL确认无旧TokenScope进程、有关端口及Docker socket后，空state以4191冷启动，实际HTTP所有dist资源SHA与新构建一致。显式提交三模型Trace、差异Trace、MA及四种方向/partial任务。第一阶段浏览器MA4项（13UUID矩阵/409/503/错范围/并发取消/实例重置）、用户3项（完整多模型/固定历史/三模型τ与K/历史/迟到响应）、异常3项（裸入口partial/无可展示建议但88组L4L5/唯一请求数与原来源/方向及无配方/fragment限制/21秒无轮询与重连）全部最终通过。
首次失败均单列保留：Windows测试执行器直接import的ESM路径；重复filter-meta定位；旧display恢复尚未切到指定run就输入TTFT；根误把recommendation_count当可展示建议数。只适配测试定位/目标就绪/真实契约语义，不删数值/身份/缓存断言。GLM实际4条not_eligible候选、88差异组、2张L4L5卡，影响请求各8；配置配方数只计外部Token bundle，不代替低命中内置候选计数。没有此次E2E中的产品源码修改。
正常SIGTERM确认退出及端口释放后，按同一候选/state重启，156个HTTP资源字节摘要及5类业务数据库所有表行摘要前后一致；读取无业务写入。证据artifacts/reviews/hv2-repair-20261103/{frontend-full,e2e,source-default-result.json}。完整旧功能回归/最终视觉/容器/现场仍待执行，不能以本阶段通过宣称交付完成。

## HV2-MF-02：首次默认加载关闭用户新弹窗（待修复）
根第二阶段真实浏览器 full-real-search 第一例在裸用户入口立即点击打开运行，输入框随后消失并超时；其余搜索/排行/导出用例继续执行。源码 open() 对迟到默认receipt无条件setModal(false)，已向监控前端定向派发延迟响应复现及最小修复，不能通过给测试加等待掩盖真实交互问题。证据：artifacts/reviews/hv2-repair-20261103/e2e-legacy/joint-results/full-real-search-fresh-rea-42e40--inclusive-combined-filters。修复后新候选须停旧、全新state重新验收；此前源码通过记录仍仅对应原候选。发布/构建等待本问题闭环。

## HV2-MF-02源码复审及新候选
维护方以延迟目录/URL回执稳定复现3条负向失败；最小修复给自动恢复传入closeDialog=false，显式打开成功仍关闭；身份、sequence及取消逻辑未改。根已读实际源码与四条新增用例，完整typecheck/lint/339项前端测试及新dist构建通过。新候选694输入组合79fe33361ae998539bcd42b7c54462292e8828eb5a40e6a3c616c8dae7673b6c；变更仅UserMonitor、对应组件测试和构建元数据读取已声明契约版本。原693输入及5份浏览器适配证据保持原件。
第二旧候选SIGTERM PID4101360退出/4191释放后，空final-default/state冷启PID4171303，HTTP全部资源摘要等于新dist；正在重跑两阶段完整浏览器。旧候选第二阶段最终42监控、18异常、3来源、2指针及135鼠标断言通过；联合8例中2例因MF02失败、6例通过，不将旧结果计为新候选通过。40张原型/实际截图已保存，其中异步占位需在最终图中等待就绪。

## 新候选完整源码浏览器最终结果
新默认state：HV2监控7+异常3；新完整回归state：监控42、异常18、来源3、联合8+MF02延迟3、指针键盘4，合计88项最终通过。监控42中1项改为等待指定旧run后再截指标，18异常中1项修正根复制脚本硬编码旧state fixture路径，MF02三项修正根测试dialog名称定位为其子heading；均保留原数值、身份、缓存/零写入/取消断言及初次失败trace，实际产品在这一阶段无新增修改。源结果以final-default/final-legacy为准，不混用前候选输出。
MF02实际浏览器确认目录自动载入、URL恢复及新建表单的已输入值在迟到真实回执后保持；显式打开成功正常关闭，未触发POST。默认阶段156HTTP/全部业务行正常停启一致，GET零业务写入。版本输入在source-candidate-r3.json固定，第二次测试增量仅v2-acceptance等待条件。

最终补证：新候选135项独立鼠标读数全部相等，历史固定范围延迟/刷新零写入通过；40组原型/实际宽屏与移动端截图及DOM保存于final-legacy/visual-final-r2，零页面溢出/脚本错误/提交。已查看实际用户概览、MA解释、L4/L5详情等图；保持四入口、六卡/Token去向、图表与L4/L5结构，新增W输入、模型发现和MA逐指标解释属于本轮功能内容，非像素完全等同演示数据。最终PID4184626正常退出，4191释放。源码关通过；未代用户视觉签字、未代签容器或现场。source-final-result.json为本地汇总。

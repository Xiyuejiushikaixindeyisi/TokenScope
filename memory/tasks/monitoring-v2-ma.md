# V2 同事侧 MA 监控后端记忆

## 当前状态：休眠（2026-11-10用户决定）

本V2会话 `01a18ab2-2600-7ae1-8b0e-979dad9ec3be` 明确休眠，本轮未唤醒或派发任务。以下内容全部作为对应版本历史，不恢复旧开发/测试/协调授权。当前活跃三角色及权责见[SESSIONS](../SESSIONS.md)，本线按需参考见[历史入口](../../docs/tasks/monitoring/v2-ma/ENTRY.md)；V3由新开发会话统一承担获准修改，Token私有修复留V3.5。原有记忆正文保留。

## 既有历史记录

2026-11-02当前交付决定：用户认可V2可交付，UIR-03留V3、不阻断；审查打包已完成源码push、WSL构建/包体与桌面全SHA交付；华为真实数据待验。角色职责保持，以下旧暂停/阻断/合成现场计划只是历史。现场真实数据、两次人工验收、SSH18002、唯一Markdown要求及不得再犯的问题见[长期记忆](../DELIVERY_LESSONS.md)；当前结果看[交付记录](../../docs/tasks/delivery/V2_APPROVED_DELIVERY_20261102.md)。

当前职责（2026-10-31用户重新明确）：MA监控已闭环；本会话仅承接华为机服务启动/功能验证及其中发现的MA Bug修复。P90 TTFT与性能校准由用户监控session讨论；此前校准清单属于待重新讨论材料，不作为本会话继续扩展工作的依据。
更新：2026-10-30。实际会话ID `01a18ab2-2600-7ae1-8b0e-979dad9ec3be`（环境核实）；原V2父会话现负责同事MA监控后端。角色以[SESSIONS](../SESSIONS.md)为准。当前[最终设计v1.0](../../docs/tasks/monitoring/v2-ma/DESIGN.md)已形成；用户已批准设计并授权逐批开发；M000–M005本机后端闭环，未部署/打包。当前恢复优先读M005 RESULT、DESIGN_CHECK与IMPLEMENTED_API，以下历史阶段记录保留追溯。

## 当前阅读与执行入口

[ENTRY](../../docs/tasks/monitoring/v2-ma/ENTRY.md) → [设计](../../docs/tasks/monitoring/v2-ma/DESIGN.md) → [交叉核对](../../docs/tasks/monitoring/v2-ma/CROSS_CHECK.md) → [batch方案](../../docs/tasks/monitoring/v2-ma/BATCH_PLAN.md) → [统一验收](../../docs/tasks/monitoring/v2-ma/ACCEPTANCE.md) → 当前batch四文档。身份与历史见[VERSIONS](../../docs/tasks/monitoring/v2-ma/VERSIONS.md)。

用户最新授权为两线交叉check、优化最终MA设计、补齐Agent按batch开发/验证/闭环机制，并整理版本/上下文。后续用户已明确批准编码启动并要求连续逐批闭环，现已完成；不再以旧待审批说明阻止已授权工作。

## 已确认范围

- GF，model_standard_name×instance_uuid，每个规格下各UUID独立；同UUID跨appid/P共享，不跨UUID/规格混算。MA=GF＋独立motor＋3P3D，单实例Mooncake池化。
- 手动提供同规格pre/now各连续1小时CSV。pre从空缓存预热，只统计now；新任务不延续旧账本。暂不自动采集。
- 两文件均有instance_uuid、hash_id、appid、model_handle_start_time、completion_tokens、cached_tokens、request_input，并增加prompt_tokens和request_time；completion_tokens是输出Token。
- 画像为请求数、输入分布、请求速率、实际未命中输入Token；5分钟一段＋整小时平均，两张独立分布图。观察同规格全部UUID，不要求先选单UUID才能看到概览。
- 辅助人工选择值得做GF策略对照实验的场景；不推荐最优算法、不自动切换、不诊断SSD/GB路由收益。用户侧TTFT/排行、异常分析、前端各自独立；hybrid暂不做。

## 最终设计的关键选择与限制

- request_time用于半开窗口/12桶，称记录时间速率；处理起点用于缓存顺序。pre处理起点跨越now时该UUID理想不可用、真实画像保留。该保守工程选择已写入最终设计，不能冒称用户已逐条确认。
- 交叉核对用户线“CSV为UTC”澄清后，统一无offset按UTC并保存声明；request_time实际事件仍未知，不能称GF到达。公共DD/MM能力未接入时不谎称支持。
- 生产P_db/实际命中/实际未命中U与本地P_local/理想H/C分开；字段有效集合A/P/R/E/Q明确，Q只控制配对聚合，不改变完整可回放历史。输入长度不一致不改分母/删样本；有效子集和预热覆盖显式。
- 两图复用V1有界展示箱和200K尾桶；用户线开放等宽箱用于理想C众数均值排行，不能改变MA/V1分布函数。
- DeepSeek使用同一公共配置快照、显式请求优先；新安装thinking_disabled仅为用户线现场假设配置，不证明生产缺省。MA不独立覆盖已有未决default。
- MA独立控制库/目录/接口，共用模型配置及编码/匹配内核，保留原appid。三种身份service_instance_id、ma_run_id、instance_uuid分开。
- MA与旧任务共用state_root/worker.lock，覆盖claim/恢复/计算/发布；单库事务发布，seal不可变。正式MA契约待M000固定；不修改旧S0或已发布结果。
- 用户v1.0增加侧索引/大回填重任务，也必须共用执行额度。用户线实现其process_next适配器，MA维护注册/轮转装配；禁止嵌套锁。用户真实代码未接入时只验证适配契约，真实三类联合pending；V1-MA真实多进程门槛仍必需。
- 有限预热不保证理想≥真实；未知编码等价/GLM CP及普通链式近似边界保留。没有P级数据不能证明负载不均；5分钟不代表秒级峰值，平均速率不证明泊松。现场性能目标与代表数据待后续核实，不外推V1 22–55分钟。

## 开发batch及证据规则

M000契约/基线 → M001摄入/质量 → M002编码/回放 → M003统计投影 → M004服务/恢复/共享锁 → M005统一验收。原计划阶段全部planned；现全部closed，实际门槛、失败修复和测试记录见各批文末及最终M005，不将原模板当证据。

用户启动实施后，当前batch实现、测试、门槛满足、问题闭环、RESULT和增量记忆完成才推进下一批；普通缺陷在授权内自主修复，重大设计/接口/门槛变化先确认。每批追加实际版本、测试/证据、问题修复、偏差/回退、依赖及下一步。M005必须统一真实HTTP/CLI E2E、健壮性、旧S0兼容、资源实测、MA01–14/X01–12设计对照。后端/前端/现场/发布分开结论，禁止用pending掩盖后端必需失败。

公共职责见BATCH_PLAN：用户线维护时间/别名/模式/排行；MA维护专属模块及新增装配/dispatcher。M000锁定接入基线，M004修改app/CLI前重读并登记具体维护范围，不同时覆盖共享文件。未发送跨会话消息/创建聊天/委派Agent。

## 2026-10-30 本轮版本整理记录

- 只读对照用户设计v0.1与MA v0.1，12项发现/关系写入CROSS_CHECK；核对现有RunProcessor的flock、发布恢复、公共配置/分布/仿真及项目检查配置，未运行业务测试。
- MA升级为文档v1.0；旧MA、用户核对输入及整理前记忆按字节保存至[归档](../../achieve/2026-10-30/monitoring-v2-ma-design-v0.1/README.md)。未修改用户线设计/记忆或其他会话进度。
- 已建立六批各四文档、统一验收、版本索引和文档摘要清单；当前文档检查结果以DESIGN_MANIFEST的validation为准。未修改源码、V1配置、冻结契约、原始证据，未部署/打包，未Git提交或push。
- 下一步：用户确认最终工程选择并启动实施后，从M000锁定最新依赖和冻结MA契约开始；不要直接跳到代码/前端实现。
- 最终检查发现用户线并行升级至v1.0，已只读追加核查并保存输入SHA f991245dbe48a2568c721ba67256d91b3bdbf86b997bdf79c373386f1c70b110；确认公共UTC/模式/独立分箱一致，补齐用户索引同锁和公共解析错误字段。未改写用户线文档或发跨会话消息。
- 后续用户明确告知用户监控已进入代码开发；本线依赖状态据此更新。工作树已出现用户线契约、校验脚本与user_monitoring源码目录，但本线尚未审查其实现或测试结果，不把目录存在视为批次通过。MA设计交付已完成，M000–M005仍planned；启动时核对用户线最新代码/契约及公共模块归属，不要求用户线等待MA，也不擅自修改其实现。

历史讨论与来源详情保留于[整理前记忆快照](../../achieve/2026-10-30/monitoring-v2-ma-design-v0.1/MA_MEMORY_BEFORE_V1.md)，不全量重读。

## 2026-10-30 开发启动：M000 in_progress
用户已认可设计并授权逐批开发直至统一验收，无需再次请求编码授权。已只读核对用户线contracts.py及现有parse_utc；用户公共DD/MM解析和process_next适配尚未由本线验证。新增MA独立契约原语Submit/Coverage/TokenTotals及3项测试，pytest、ruff、mypy通过。仅基础子集通过，不代表M000出口通过；完整响应/错误/目录分页/12桶契约、Schema/OpenAPI样例、基线清单仍需完成。下一步继续M000，不进入M001。WSL普通权限E_ACCESSDENIED，经批准提升运行项目.venv Python3.11.16成功；未部署打包。

## 2026-10-30 M000闭环记录
M000 closed：独立contracts.py、CONTRACT.md、schema/design.openapi/examples/manifest及验证器已生成。Python3.11.16；pytest tests/unit/ma：10 passed；协议验证器2正例4负例；ruff check/format与mypy通过。BASELINE.json记录公共源码、用户契约、依赖及旧S0摘要，旧S0未修改。窗口/交集/守恒/12桶/仅pre/时序不可用约束验证通过。设计OpenAPI仅操作/响应骨架，请求及查询完整语义在CONTRACT明确，M004必须以真实路由导出补全；不声称运行接口已存在。公共解析用户线维护，MA不覆盖；真实用户索引联合后续核验。允许进入M001。

## 实际闭环（2026-10-30）
M001 closed。实现ma/ingest.py、storage.py，独立事实/质量/控制库；原文保留、窗口半开/规格拒绝、Token精确整数、字段独立有效性、幂等绑定及发布单向状态。pytest局部及公共输入回归66 passed（0.55s）；ruff、mypy通过。证据artifacts/validation/monitoring/v2-ma/M001/attempt-01/pytest.txt。发现E501长SQL字符串，拆为相邻常量并复测通过；未修改公共解析/用户代码。InputRoot快照复用既有受控实现，服务装配和故障注入在M004/M005验证。允许进入M002。

## 实际闭环 2026-10-30
M002 closed：ma/replay.py复用公共批编码/分片/完整块账本；三模型真实资产验证跨租户共享、UUID隔离、预热、时序冲突保留真实。pytest本线及内核/分片/模型回归67 passed in64.67s，证据artifacts/validation/monitoring/v2-ma/M002/attempt-02/regression.txt；ruff/mypy通过。M002-I01预算冲突已修复并完整复测，attempt-01失败日志保留。公共DD/MM解析已出现，仍由用户线维护，MA消费。允许进入M003。

## 实际闭环 2026-10-30
M003 closed：ma/statistics.py完成精确独立/配对聚合、质量覆盖、12桶/小时、两图三箱宽与预生成投影。16项聚合/契约/公共分布测试通过；ruff/format/mypy通过。证据artifacts/validation/monitoring/v2-ma/M003/attempt-01/regression.txt。问题：mypy不能确认list展开参数数量，改显式下标；一次测试路径误写已改为实际test_statistics_rules.py并通过。允许进入M004。

## 实际闭环 2026-10-30
M004 closed。新增MA服务/HTTP/CLI、封存恢复与共享轮转，实际修改app.py/cli.py局部已登记。真实多进程锁和双队列推进、CLI数值往返2项通过；本线+V1监控回归76 passed in121.28s，证据artifacts/validation/monitoring/v2-ma/M004/attempt-01/pytest.txt；追加故障/存储/恢复13 passed in25.14s。ruff/mypy通过。修复：SQL长行；CLI跨进程轮转位置持久化；封存子目录fsync；claim后再次检查hybrid；error_detail保留安全role/行号定位。真实路由OpenAPI已导出并验证，旧S0未改。用户索引处理器仍未实现，注册接口可用但真实三线联合pending。允许进入M005。

## 最终执行记录 2026-10-30
M005 closed。本机后端最终pytest235 passed/1既有弃用warning/190.03s；ruff check、format111文件、mypy44源码及协议校验通过。真实HTTP/CLI、进程退出恢复/并发、资源及MA01–14/X01–12设计矩阵已完成。详见RESULT、DESIGN_CHECK、IMPLEMENTATION_MANIFEST；原始证据artifacts/validation/monitoring/v2-ma/M005/final-02与resource-attempt02。未部署/打包；前端、现场、用户索引三线联合单列pending。

最终交接补充：已读取前端接收记忆中的样例缺口，用真实MA管线生成并严格校验16个合成前端样例（含5类Snapshot、完整Receipt、质量、目录、错误），位于docs/contracts/ma-monitoring-v2/frontend.examples.json；生成器scripts/contracts/generate_ma_examples.py。部分回执状态显式为合成状态，均非现场或前端验收证据。未发跨会话消息，前端按入口自行接收。业务源码未改变，235项全量证据仍对应同一候选。

## 2026-10-30 Git同步及前端交接（当前）
用户授权本轮版本/交接整理、提交本线并push，暂不部署打包。检查点ma-backend-local-1；新增FRONTEND_HANDOFF、SHARED_BASELINE与GIT_CHECKPOINT，修正VERSIONS顶部旧未实施说明。共享app/CLI含用户线后加功能，按M005原SHA提取MA部分到独立索引，原文件保留；CURRENT/SESSIONS提交仅选MA角色进度。用户U001公共兼容已闭环，以独立前置依赖提交；用户后续功能、前端、异常分析等不纳入。用户线最新U005已声明本地三队列联合通过，本线仅记录其证据来源，不再把旧pending当作对方当前状态。状态为MA维护/前端交接；不休眠或唤醒其他会话。独立候选验收与最终Git身份见GIT_CHECKPOINT。

## Git共享并发复核（最新）
本线独立候选227测试通过（203.70s）、静态107文件/类型41源码/契约通过。候选未接入main；验证中用户会话完成其获授权的已闭环功能及MA依赖集成并同步，最终源码为9a037466f7211126261ec2026f54b9c19c2e2151，同步记录为3224c4b8d1cf2abb4e22fbdeb505d05d714f3224。已核对MA专属代码及测试与原M005身份一致；app/CLI保留已闭环的用户装配。故本轮改为只追加MA版本、前端交接和本线状态，不重复提交或改写他线历史。未完成的前端/异常分析及其共享记忆继续留在工作区。完整结果和Git身份见GIT_CHECKPOINT；早先“准备独立依赖提交/用户尚未接入”是检查过程的历史时点。

本轮最终复核：已同步集成源码289 passed/1既有警告/234.92s；静态126文件、mypy50源码和协议通过。独立MA候选227项仅作隔离范围核验；本次追加提交严格为10项MA文档/本线状态，不包含新业务代码或他线未完成材料。源码身份9a037466f7211126261ec2026f54b9c19c2e2151，Git同步后的精确文档提交由git log -- GIT_CHECKPOINT.md定位。

## 2026-10-30 TTFT闭环口径澄清
用户质疑尚未提供三模型batch耗时、等待时间却宣称闭环。只读核对用户线estimator.py、Scenario/EvaluationRequest和U005 VALIDATION_SUMMARY：当前为固定chunk参数化参考计算器，τ/W/K/O须显式提供，无三模型真实τ或等待缺省；合成测试参数不等于用户/现场校准。U000–U005 closed指本机软件开发验证，E07真实TTFT校准/现场性能仍pending。对外需明确“代码完成、性能校准与业务可用性未完成”，不能以批次闭环表示已得到三模型可信最低命中率。本线不改用户公式/契约或代签校准，未提供参数时不输出具体模型结论。

## 2026-10-30 用户明确的TTFT校准门槛（最新）
**代码完成，性能校准待完成**。三模型真实batch耗时、有效K、等待W及O未完成校准；缺失/空白/null不出具体比例，不默认W=0。最小清单在docs/tasks/monitoring/v2-user/PERFORMANCE_CALIBRATION.md，区分全batch预算与单请求有效进度、固定τ与实测batch时间、GF同口径初始及chunk间等待，禁止双计O或分位数直接相加。本轮由MA会话按用户直接要求统一跨线文档/交接；不改变后端公式或契约。UI-02已修正默认假设展示与Number空字符串变0，布局不变；正式前端仍按原流程推进。缺参后端38项测试、浏览器5组检查通过，人工假设必须完整且显式输入，不能当模型已校准。

## 2026-10-31 职责纠正（最新权威）
用户明确MA监控已闭环，本会话只负责华为机拉起服务、功能验证后出现的MA Bug修复；本轮仅更新职责并提供转交用户监控session的讨论prompt，不立即执行远端启动、部署或打包。P90 TTFT及性能校准交回用户监控线，现有最小清单过多，须由该线与用户重新收敛，不把原清单当已认可门槛，不自行继续设计/修改用户监控或前端。

## 2026-11-01 华为验收补采字段核对
本线按最新CURRENT/SESSIONS配合完整服务总负责（镜像打包与审查），归口MA问题支持，不承担完整服务启动总责。用户计划用户监控/异常分析沿用V1现场CSV，仅补采MA，例如Qwen-V3.6-27B-32K。已核对当前ma/ingest.py与Submit：两份同规格连续各1小时pre/now，按request_time左闭右开；9个必需列instance_uuid/hash_id/appid/request_time/model_handle_start_time/prompt_tokens/cached_tokens/completion_tokens/request_input，可加model_standard_name供混规格校验。每份包含该规格所有UUID和appid，后端自行分组；不DISTINCT、不用BETWEEN重复边界、不把缺失命中改0。pre仅预热，now统计。时间需明确时区，推荐导出UTC ISO；解析器无偏移值按UTC解释，显式+08:00可归一UTC。SQL示例时段按数据库真实时区选取，导出两时间列与提交窗口需对应同一绝对时间。原始JSON用合规UTF-8 CSV引用转义，不能截断或改正文。仅字段/查询交接，未启动服务、改代码或打包；真实验收待CSV及现场结果。
## 2026-11-03 HV2-R1-MA修复候选交接
实际环境THREAD/SESSION均01a18ab2-2600-7ae1-8b0e-979dad9ec3be。已承接V2总设计师直接派发；优先级P0 MA缺数解释/预热审查，当前本线代码与测试完成、待独立验收冻结，不改CURRENT/SESSIONS总文档。入口docs/tasks/monitoring/v2-ma/HV2_MA_BACKEND_HANDOFF_20261103.md。
新增预计算availability表及独立GET资源，保留旧Snapshot/Schema/原seal；六项解释覆盖四主指标及独立ideal/real，含原因/样本/分母、12桶和成功编码pre/now时间边界。DS缺cached保持真实不可用并保留独立ideal；GLM冲突保留独立real/小时已知量。缺JSON/输出字段不影响真实量，null/0/部分覆盖/空桶明确。旧结果新资源返回AVAILABILITY_NOT_RECORDED，旧GET照常只读，不自动重算。
预热边界测试未发现实现bug：无效或编码失败pre不入bounds；有效JSON但生产字段坏的pre仍合法；重复hash保留、等时pre优先，request_time归属/handle排序不互换。真正重叠保持whole-UUID停ideal；具体截尾/混排对比例在交接，未擅自实施。
实际验证：首轮17；MA回归60 passed/1真实监听用例未执行；最终新增/增强测试21 passed；受影响公共计量/HTTP回归40 passed。ruff/format24文件、mypy10源码通过；9个合成候选样例严格校验，旧Schema/原OpenAPI各路径及components不变。源码/测试组合SHA15194270d39e4e51950c83fd10d7694a3282d9c96a0b9ffbfd7c882b3d2f96f5；逐文件见hv2-availability/source-manifest.json。旧全量OpenAPI校验器需总设计师安排冻结工具扩展，未越权改scripts/contracts。现场原件SHA保持；GLM27/26、Qwen完整矩阵、全部18文件SHA和真实冲突边界缺口不编造。另调查将OUTSIDE_WINDOW写成跳过与源码整任务拒绝不同，已列补证。未监听服务/改前端/部署打包/commit/push，原共享改动保留。
2026-11-03追加：总设计师直接授权契约工具唯一窗口，已修改validate_ma_contract.py并新增validate_ma_availability.py/test_contract_tools.py；保留原manifest全部身份断言，新增manifest自身SHA固定及旧Schema/path/component兼容、扩展完整OpenAPI/DTO/9样例+8负例检查，--write拒绝改冻结字节。两个check命令通过、工具变异13测试通过、ruff/format通过；旧全量OpenAPI工具失配已闭环，原失败日志保留。精确工具SHA与命令在HV2_MA_BACKEND_HANDOFF_20261103.md末节。业务5源码+1测试组合SHA未变；扩展仍候选待总设计师独立验收冻结。本线未push/监听/部署打包或改共享总文档，工具窗口交回。
## 2026-11-03 总设计师独立验收冻结（最新状态）

V2总设计师01a1800e-80b4-7400-a78b-a84f5b6e888d已明确通知：MA后端及契约工具独立通过，涵盖66项本线、13项工具，以及额外混合UUID原因隔离、0/null、桶与小时守恒核验。冻结清单：docs/tasks/delivery/HV2_MA_FREEZE_20261103.json；组合身份9b48fb244963ce153b009a9a2d0d9050d084bd6c1bb43eec27ddf49f313fd9fa。此状态覆盖前文候选待冻结的历史描述；冻结内容保持原字节。

本次冻结范围为MA新增availability资源及兼容契约工具，原指标和预热策略保持。源码窗口、工具窗口均已关闭；监控前端当前仅接入MA。本线转为等待问题后的归口维护，不再自行测试、提交/push或监听服务。后端独立验收不代表前端或华为现场验收；DS真实观测缺失、GLM真实冲突边界及现场完整证据仍待补证，不代签通过。

2026-11-03总设计师交付同步：本线MA冻结与前端、源码/固定镜像完整验收通过，已随tokenscope-v2-hv2-20261103完成WSL构建和桌面全15文件SHA交付。[最终结果](../../docs/tasks/delivery/HV2_DELIVERY_20261103.md)。新版真实数据、原cached缺失与冲突边界仍待现场验收；开发窗口关闭，后续定向派发。

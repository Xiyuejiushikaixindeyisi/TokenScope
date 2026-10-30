# V2 同事侧 MA 监控后端记忆

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

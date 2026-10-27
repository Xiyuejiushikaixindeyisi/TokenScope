# Token 监控增量记忆

维护：Session 1 `01a1682f-956d-7630-afe7-e123ba38dfc0`。本文件只维护监控研发进展；前端会话和产品 Agent 的运行记录不写在这里。

## 当前定位

- 当前设计：[v1.0 最终稿](../../docs/tasks/monitoring/DESIGN.md)，**2026-10-27 已批准**；[版本集](../../docs/tasks/monitoring/VERSIONS.md)为恢复入口。
- 当前 batch：[B001 已闭环](../../docs/tasks/monitoring/batches/B001/RESULT.md)；B002 verifying（DeepSeek 缺省 pending）。实际代码版本 0.1.0.dev2，尚无完整分析或交付。
- 最新交接：[2026-10-27 开发](../handoffs/2026-10-27-monitoring-development.md)。后续每批按“方案→实现→测试/修复→闭环→记忆”推进，门槛未过不得进入下一批。

## 2026-10-26：第一版设计收敛与环境纳入

- 保持三模型共用链式 DES，GLM/Qwen/V4 B=128/1536/32；只有增强 hybrid 占位。J 是完整原 JSON 编码；H/C 输入复用/重算，O 输出独立；ΣH/ΣP；UTC 输入、北京时间显示；重复 ID 每行独立、无效行跳过；每 CSV 空缓存、租户隔离、立即可用、无限逻辑容量。
- 三组默认 5K 直方图、≥200K 尾桶、并列众数、图外 P50/P80/P90 保持不变；HTML 起点留给已登记前端 fork，不在本轮修改。阈值初始空表，用户三天稳态流量之后定值。
- [华为报告](../../docs/huawei/TOKEN_SCOPE_V100_ENVIRONMENT_REPORT.md)已取得并保持原字节；采用 40 可调度逻辑 CPU/20 物理核、375.9 GiB 内存、Docker 26.1.4、Compose v2.27.1。2×V100 已有 proc 证据，GPU 驱动/NVML 不匹配；首版 CPU 路径不依赖 GPU。
- 初始工程配置：单模型任务并发 1、总计算预算 8、容器 8 CPU/32 GiB、批次 256 条或 16 MiB；这些是待验证默认值。根分区紧张，工作数据与临时目录放用户明确的 `/home` 工作目录。旧内核 3.10 镜像兼容性、峰值和每文件两小时均待 B006 实测。
- 新增逐批五文档、退出门槛、M01–M12 需求对照及统一 E2E/健壮性验收。最终交付代码包 + prompt + CPU 镜像，包含固定编码资产/Compose/摘要；现场 Agent 按 prompt 预检、load、启动、小样本、三模型真实文件及重启验收。
- 已整理 rc2 设计/契约/样例历史，当前唯一权威入口切至 v1.0；设计版本不等于发布版本。实际文档检查见[检查记录](../../artifacts/reviews/monitoring-v1/context-validation.json)。

## 后续每批追加格式

日期 / Batch / 设计与代码身份；完成行为；关键问题与修复；实际测试结果及链接；门槛判定；允许遗留项及原因；回退点；下一批与所需输入。重要阻断在发生时就记录，不能到最后一批才回补。CURRENT 保持简短，详细事实以 batch 文档和证据为准。

## 2026-10-27：审批通过并启动 B001

用户明确批准 v1.0 并进入代码开发。原设计/契约字节保持不变，审批覆盖其成稿时待审批状态，身份见 APPROVAL.md。B001 已建立五份文档，从本地 Python 环境、类型/配置/存储/CSV 与接口骨架开始；前端工作保持独立。后续批仅在当前门槛及闭环完成后推进。

## 2026-10-27：B001 closed

独立 Python 3.11.16 与 uv.lock 就绪；完成统一类型/配置 revision、启动时冻结/单运行状态、受限文件引用/快照、CSV 分批/原 JSON/UTC 纳秒/坏行/重复保留、SQLite 暂存、CLI/API 共服务。实际 66 项测试通过，ruff/format/mypy 与独立 uvicorn HTTP 检查通过；首轮格式失败及修复均记录在 B001 五文档。source-manifest/source-snapshot 可回退，尚无 Git 或镜像。完整分析提交返回 PIPELINE_NOT_READY，不冒充业务结果。下一步 B002 取得真实词表并完成 IDs 对齐，后续批不得提前记为完成。

## 2026-10-27：B002 开始

五文档与方案已建，先取得固定官方 revision 的真实 tokenizer 资产；原有 models 无运行词表。不跳过三模型 IDs 对齐门槛。

## 2026-10-27：编码默认值新决定

用户明确 DeepSeek 缺省思考模式 pending，需核查现场环境；Qwen/GLM 使用其固定模板默认值。所说 vLLM 0.23.0 是官方源码快照的函数 kwargs 缺省 False，不是已核实的运行镜像或环境变量。Recipe 0.2.0 默认 True。不得替用户选择 DeepSeek 默认；允许显式 True/False 情景测试。该项影响 B002 整批关闭，B003 不提前开始。

三模型实际 tokenizer.json 已从原固定 revision 取得并记录摘要；Recipe 0.2.0 PyPI sdist 的 6 个已有核心/编码参考源文件与固定源码一致。资产锁 env/encoding-assets.lock.json 当前 acquired_not_validated，不代表现场部署相同。

## 2026-10-27：三模型现场启动参数筛选落盘

用户限定只提取所需信息并沉淀配置；已存 env/profiles/*-gf-20261027.json 与带摘要索引，说明见 docs/tasks/monitoring/DEPLOYMENT_PARAMETERS_2026-10-27.md。未保存凭据/初始化命令，未主动访问现场或改服务。

关键差异：DeepSeek GF 包 0.30.0rc2（非此前研究0.23），p/d块32，prefix开/关，hash_block_size4096，MTP/CP具体大小和缺省thinking本次未明确；Qwen包0.23，MTP3明确，1536仍来源此前日志，prefix开/关；GLM包0.23，PCP1/DCP8/interleave128、MTP p1/d3、prefix两侧开、hash_block_size1024。hash_block_size不直接替代仿真block_size，GLM scalar CP映射pending；配置仅声明未激活，原默认/历史快照不覆盖。

## 2026-10-27：B002 验证进展与本轮结束点

代码 0.1.0.dev2；三真实词表、固定模板/Recipe V4 适配、Rust 单条/批量/并行一致、轻量源字段、详细 IDs/UTF-8 byte offsets、uint32 分片均已有实现。最终 pytest 94 passed（含B001回归），ruff/format/mypy通过。保留依赖下载、Jinja/AddedToken/参考返回类型和单位修复的失败与复测记录；清单/源码快照在 artifacts/validation/monitoring/B002。当前库版本 Transformers5.21.0、tokenizers0.23.2、Recipe0.2.0，以uv.lock为准；GLM现场声明5.5.4仅记录，不声称已验证与现场等价。

B002尚未closed：DeepSeek缺省模式用户保留pending（现场GF0.30rc2），运行落盘衔接、扩大选项覆盖与最终复审还需完成。对外分析仍503未就绪；B003–B006未启动。详细来源只提供可核验prompt offsets与JSON pointers，完整原字段Token归因标unknown，不能用独立字段Token数相加冒充。没有打包、镜像、远程服务操作或修改前端文件。


## 继续开发与打包门槛（最新用户决定）

2026-10-27 最新授权：继续 B002–B006 的开发、逐批验证和本地端到端测试。Docker 镜像及交付包构建前必须先通知用户，提交验证结果和交付范围，取得新的明确同意；前端由另一会话同步开发，旧的打包授权不再适用。日常修复只使用本地环境，不重复构建镜像。B006 可先准备构建脚本、Compose 和执行 prompt；实际打包及现场验收保持待批准/待执行。


B002 closed：96项全回归/ruff/format/mypy通过；补齐编码落盘，修复同库读写锁；生产DeepSeek缺省未决与实现门槛分开，未选择默认。B003开始实现；真实CSV未到位已询问用户，不提前宣称B005/B006通过。

B003 closed：117项回归及静态检查通过，SQLite链式DES/五事件与独立历史前缀参考一致。B004按计划进入统计、规则与完整服务编排；未构建镜像。


用户最新确认：生产CSV绝密，不会提供给本机。本机B005端到端/压力验收改用自行生成的泊松分布数据，每模型5个appid；保留固定种子、生成参数和合成标识。真实数据及目标V100两小时验收仍仅在现场执行，不索取或复制绝密CSV。此决定覆盖旧B005要求本机取得三份真实代表CSV的门槛。

B004 closed：0.1.0.dev4/schema2、131项全回归及静态检查通过；完整服务、只读查询、精确统计、阈值/outbox、原子封存恢复具备。B005开始，本机合成验收取代索要真实CSV，未打包。


B005本机closed：0.1.0.dev5/schema2，141回归+静态通过；最终实际HTTP E2E在artifacts/validation/monitoring/B005/20261027T034057Z，3模型×5appid/约1万行，各约21–22秒，峰值RSS1120.71MiB，8CPU约束，kill恢复/CLI一致/并发读取通过。生产CSV绝密，按用户决定仅用合成；现场M11/M12待B006。开始B006准备但实际打包须再次取得同意；本机未发现Docker可执行，不安装/构建。


## 本轮最终交接

0.1.0.dev5/schema2，B001–B005本机closed；最终145测试/ruff/format/mypy通过，最后实际E2E报告artifacts/validation/monitoring/B005/20261027T035327Z/report.json绑定源码摘要：GLM19.74s/Qwen20.81s/DeepSeek22.20s，约1万行/模型、每模型5appid，峰值RSS1174.26MiB，8CPU限制，真实kill恢复/CLI一致/并发读取通过。生产CSV绝密，本机仅合成；合成DeepSeek显式false不代选生产缺省。

B006已准备env/docker、scripts/release/build_monitoring.py、env/requirements.runtime.txt、prompts/delivery/HUAWEI_MONITORING_V1.md；无批准拒绝构建，--check只读；未创建approval文件、未构建/导出镜像或交付包。Windows/WSL PATH均无Docker CLI。下一步用户决定前端是否一并交付及打包意见，然后准备构建环境、确认digest基础镜像、一次性构建与离线容器验收，再现场M11/M12。不要跳过审批或把B006标完成，不改前端会话进展。

## 2026-10-27 B005.1方案与完整服务范围修正

用户明确第一版必须含前端与后端，现阶段未完成。本轮仅形成B005.1 CONTEXT/DESIGN/PLAN/ISSUES/TESTS/RESULT及共享展示契约草案，覆盖BE01–BE10；后端A01–A18与完整服务J01–J06分别判定。当前dev5/schema2不变，新增代码/SSE/前端联调均未执行。已发现文件时间范围按字符串取min/max的问题，列入B005.1待修复。

B006现有仅后端准备19文件归档至docs/archive/monitoring/B006-backend-preparation-2026-10-27，带SHA及原路径映射；原脚本保留追溯而非当前构建入口，B006 pending。先评审实施B005.1，再完成实际前端联合验收、重定完整交付范围并获新打包批准；未构建Docker或交付包。前端会话状态未改写。Session1实际ID再次核实为01a1682f-956d-7630-afe7-e123ba38dfc0。

## 2026-10-27 评审修订及S0先行闭环

用户要求依据MONITORING_BACKEND_FRONTEND_V1_HANDOFF修订B005.1/B006，进一步要求先完成前端依赖的S0。已采用R1持久回执+订阅后一次性对齐、R2有界校验保存及Session 1统一最终联合/交付责任；B005.1/B006设计计划测试问题结果同步v0.2。旧v0.1文档14文件原字节归档，旧B00619文件不改。

[S0 1.0.0](../../docs/tasks/monitoring/batches/B005.1/S0_CONTRACT.md)已固定67字段模型/16路径18操作/75 JSON用例，补SSE/原JSON/导出正常和空字节夹具；94项契约检查、ruff通过。修正浮点阈值兼容value_kind=number、证据section分页、请求position和终态/模型约束；生成器SyntaxError、系统旧验证器和ruff失败均登记后修复。工具环境独立项目缓存，不改运行锁/.venv。S0五文档和manifest可交前端锁定，实际接收确认尚由其会话维护。

S1–S5业务、R1/R2真浏览器、J01–J06、B006均未执行；不把协议测试算业务测试。批准计量设计/契约及B005源基线未改。无服务启动、无Docker/镜像/代码交付包、无跨会话消息。下一步按授权实施S1，并维持完整前后端联合通过后询问打包意见。

## 2026-10-27 文档整理与协作入口收敛

用户要求先整理文档/上下文，重点协作、入口、优先级和开发约束。本轮仅改文档：B005.1 PLAN为主审批/后端开发入口，S0和TESTS为附件；技术依据与过程记录不逐份审批。后端获恢复实施授权后从S1开始；前端依自身授权采用S0。统一工作流固定版本接收、接口变化、问题复核、双方ready_for_joint交接、Session 1最终J验收及B006单独打包同意。

修正任务索引旧“尚未启动/主副会话”与协作记忆“无需完整前后端”等过期表述；CURRENT压缩为状态和路由。批准计量设计、S0固定文件及原测试证据保持不变；无业务代码、服务、Docker或交付包动作。整理前后摘要和链接核对另存artifacts/reviews/monitoring-doc-organization-2026-10-27，不改旧报告。

## 2026-10-27 B005.1实施授权

用户批准PLAN/S0/TESTS，后端从S1逐步验证闭环，完成本批后停止；双方完成后统一真实E2E，Docker/交付包另需同意。S0清单核对通过，基线源码已保存，开始S1。

B005.1 S1已通过10项新旧测试及ruff/format/mypy；固定结果sidecar与schema3迁移/目录完成，开始S2持久事件/SSE。未进入Docker。

2026-10-27：S2事件/SSE局部8项检查通过，S3开始。S5综合/真实联合待完成；无Docker构建。

2026-10-27：S3快照固定Schema通过，S4操作链路3项集成通过（13类实际响应待最终统一复核）；三模型真实HTTP合成E2E首轮18.36/20.69/21.03秒，证据B005.1/20261027T085631Z。S5综合仍进行中（大目录/导出压力/SSE及最终回归），dev6/schema3候选；前端仍F002、联合pending，未Docker/打包。

## 2026-10-27 B005.1后端最终闭环

S1–S5 closed；dev6/schema3/view1，backend_ready_for_joint并按用户要求停止。固定S0 1.0.0不变（101文件摘要），实际14DTO校验通过；164项全回归、ruff/format/mypy31源码、uv lock --check --offline通过。最终HTTP E2E=20261027T092108Z：三模型各5appid约1万行，21.58/28.22/26.58秒，独立计量参考及重启/进程kill恢复通过。1001组和256MiB压力=stress-20261027T092249Z，额外RSS约46.8MiB；SSE20连接p95约122ms。空尾查询优化解决14.84%耗时超标，重复对照中位增幅约-0.31%（噪声范围），证据sse-overhead-20261027T091050Z。实际dev5源码读取schema2备份验证回退。

总证据artifacts/validation/monitoring/B005.1/backend-acceptance.json；RESULT含A01–A18后端对应、设计核对、回退及交接。编码/计量算法10文件、批准设计/契约及第三方依赖锁不变。前端仍由其会话维护，待F006后Session 1统一真实J/R1/R2。未构建Docker、未生成交付包、未部署现场；B006 pending，需用户另行同意。生产DeepSeek缺省/GLM CP/GF资产等价/V100性能边界不变。


## 2026-10-27 联合E2E/review闭环

用户授权前端F006与后端联合，完成即停。当前候选joint-v1-20261027（dev6/f006字符串未变，必须绑定SHA清单），S0 1.0.0/schema3/view1不变。166后端+143前端回归，真实3模型×5appid、30,168有效泊松请求、15组逐值统计/1029桶，真实SSE/丢回执/CAS/崩溃恢复、gzip/OPFS导出通过。六次256MiB/1GiB导出最高浏览器增量187.03MiB，256MiB上限内；服务器46.76MiB。真实UI p95首次358.5ms/50行56ms/缓存31.2ms。

修复：serve增加可选--viewer-root正式同源挂载；SQLite只读流允许串行跨线程next/close，避免实际导出中断；前端无效导出头失败主动cancel未读body。新增联合测试在apps/viewer/tests/browser/joint*.spec.ts，由后端验收维护；前端主实现仅一处资源清理及对应回归增补。算法/契约/依赖不变。问题、失败复测、回退和现场边界详见docs/tasks/monitoring/JOINT_RESULT_V1.md；证据artifacts/validation/monitoring/joint-v1/acceptance.json。输入仅合成，DeepSeek显式选项、CP/GF资产未决维持。B006仅P0/P1前置完成，打包pending；Docker/镜像/交付包均未执行。按用户要求暂停，不自动开展后续。


2026-10-27 Git基线：按用户授权初始化main和origin，整理README/ignore/Git工作流；保留所有原始实验数据。原样迁移最小dev5测试夹具到tests，166/143回归及三模型本地HTTP启动通过。启用pre-push产物/backup保护，仅推送main；本地backup/20261027-init作为源码检查点。两分析分支只规划，Docker和包体仍未生成。见docs/operations/REPOSITORY_BASELINE_20261027.md。

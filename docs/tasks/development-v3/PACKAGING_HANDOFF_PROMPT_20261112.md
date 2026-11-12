# V3 C01–C04：镜像打包与审查执行 prompt

## 用户授权与接收角色

用户于2026-11-12明确：**“用户验收通过，你现在可以整理 prompt，让镜像打包与审查session进行端到端测试验收、git和版本整理、记忆整理、打包。”**

本文件交给现有“镜像打包与审查”session（登记ID `01a1800e-80b4-7400-a78b-a84f5b6e888d`）。接入时从环境核实自己的实际ID，不沿用开发ID。本次已授权你依次完成独立端到端复验、Git/版本整理、记忆整理及打包；每阶段通过后继续，不重复询问上述已授权步骤。历史入口中“当前暂不测试/打包”“不负责验收执行”的措辞不能否定本次明确授权。你仍不承担产品代码开发/debug，不自行改变需求、页面或测试门槛。开发修复仍由V3开发线处理，旧六线不恢复。

这不是要求再审批相同DEMO或重复用户已完成的本机人工验收。你的独立复验验证交付候选与包体一致性；不能把用户验收通过当作跳过技术复验的理由。华为五组真实业务收益仍待现场，不代签。

## 入口与范围

根目录 `/home/zhangxiyue/TokenScope`；Windows `\\wsl.localhost\Ubuntu-22.04\home\zhangxiyue\TokenScope`。先依序读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md、docs/tasks/delivery/ENTRY.md，再读本文件。共享入口现有11-11暂停状态有滞后，本次用户决定和开发线最新入口优先；保留历史，整理为可辨识的时间线，不覆盖原证据。

必要依据：
- `docs/tasks/development-v3/REPAIR_BATCH_PLAN_20261111.md`：已批准C01–C04范围/门槛。
- `docs/tasks/development-v3/REPAIR_BATCH_EXECUTION_20261111.md`：每批方案、问题、失败及复验、设计对照。
- `docs/tasks/development-v3/LOCAL_ACCEPTANCE_20261111.md`：实际五组链接、用户通过记录与限制。
- `docs/tasks/development-v3/LOCAL_FIXTURE_DEMO_REVIEW_20261111.md`、`docs/huawei/HUAWEI_V3_LOCAL_FIXTURE_EVIDENCE_20261111.md`：五组结构与合成依据；不全量读历史研究。
- `docs/operations/GIT_WORKFLOW.md`、`docs/operations/DELIVERY_ACCEPTANCE_RULES.md`、`docs/architecture/TASK_SESSION_WORKFLOW.md`及交付入口中的部署/资产说明。

V3只修L1动态字段识别和大数据mem_limit，合理小样本先选再昂贵读取/解析/编码，完整计算该样本的前后参考值。保持原V2四入口及L4/L5布局交互；不加独立小样本模块、异常分析硬时间截止或精确全量收益门槛。新样本不套full/>1pp展示过滤；未评估不能填0，零/负/无对象分别表达。不自动full，显式full延期；Token私有修复留V3.5，旧结果继续可读。时间固定化不保证业务无损；样本收益不外推总体。

## 确定候选与不可覆盖证据

截至交接，工作树在main，HEAD=`a96da81152b4917f9a1fbfe65a7ddb864dee79ce`；本次开发尚未提交。**不能只取HEAD构建，候选包括工作树改动和新增文件。**

证据根目录（下称R）：`/home/zhangxiyue/TokenScope/artifacts/validation/development-v3/repair-c01-c04-20261111T184136`。
- `R/c04-e2e-02/candidate.json`保存产品源码与前端dist逐文件SHA。该manifest自身SHA256：`2b90769d8bd85843b2aca5fc976fedf8c09aeca18544e32a7d380880321c1ed5`。11-12交接重新核对源码无差异。
- 已验前端 `R/c04-dist-01`，主验收state `R/c04-e2e-02/state`，输入与生成manifest在其`inputs`。`R/CLOSE.json`是开发技术闭环时快照，其中USER_PENDING为当时事实；用户11-12通过另记，不改原JSON。
- 获批DEMO `docs/tasks/development-v3/prototypes/repair-demo-r1/index.html`，SHA256 `3441e2ea20bc47b331d602cea5010f922c24b2522bee6b628bad77f23d956619`；审批记录同目录APPROVAL_20261111.md。不要把DEMO的静态指标放入产品/镜像。
- `HANDOFF_CANDIDATE_20261112.json`（本文件同目录）列本轮代码/测试/验证脚本改动SHA，仅为Git归类提示，不授权全工作树add或忽略文档审查。
- 最近服务：PID4930，WSL监听127.0.0.1:18002，exec会话15308，原state。此前PID411591已退出；退出原因日志未知。11-12恢复后Windows健康/首页/报告均200且Chrome clock卡片可见，记录在`R/c04-e2e-02/health-recovery-20261112-01/CHECK.json`。PID仅为线索，停机前重核命令行/目录，不能按旧PID误杀。

已修问题：长样本plan错误复用8MiB元数据上限；最终证据损坏后报告悄悄降级为初始报告。相关失败及复验保留。自动内存条件变化与模型校准差异允许不同样本N：scale-02/memory-01原“样本数必须相同”断言失败未抹去，独立资源核验通过，不据旧FAIL简单误判当前产品，也不只听开发解释而不读测量。

## D01：独立源码/需求与端到端验收

1. 核实dirty归属，保存本轮清单。其他session的docs/memory改动不能reset/clean/整包覆盖。本线候选SHA不符时先列差异；版本元数据调整以外的功能差异不能混称已验候选。
2. 盘点并正常停止当前TokenScope服务/相关worker/测试容器，确认进程退出及18002释放，保留原state、输入、日志和包；不误停其他项目/共享Docker daemon。独立复验另建项目内**不存在的新目录**、空state、新dist、新浏览器；不能复用开发验收state冒充冷启动或另换端口并行。当前验收服务可在该准备步骤停止。
3. 使用真实DeepSeek/Qwen已锁资产/revision/template，真实CSV→监控→自动prepare→发现→plan→同样本重放→发布→浏览器；不注入clock recipe、不mock收益。五组64条重建关系由生成器确定，期望是自动能力与数据守恒，不强制收益数值等于开发记录。
4. 五组：DeepSeek的S00000000000000000000000000000773、S010320、com.huawei.mbs.ilegal.ioc、com.huawei.newalliance；Qwen的com.huawei.aidp_dg06。检查clock精确固定化/外部字段保护，BUS03短模板路径L1、必要L3、L4/L5各一张卡至多3例；样本范围与APPID/模型/来源一致，全部指标从真实报告读取。
5. 检查原四入口实际内容、选择/历史/详情/刷新返回/来源链接/390与1440宽度；不以SPA200或只有main元素代替正确页面。用户监控/搜索/MA用隔离的小型合法fixture作功能兼容复验，必要时复用已有相应集成测试。开发浏览器四入口检查主要证明可加载与标题/导航，不能扩写为全部监控/MA业务E2E已测。Token旧读/休眠继续验证，不启动新Token诊断。
6. 两模型各1200/12000长父来源自动缩样并完整发现/评估/发布；核对无mem_limit、无硬时间终止，正文/Token/候选物化受样本控制。固定可用内存观察值后，子进程真实RLIMIT_AS生效；按校准公式复核样本上限和读取/编码/RSS，而非强制不同模型进程的样本N恒定。开发固定限制约1.30GiB时DS151/151、Qwen188/182，峰值约286/286/530/529MB，仅作比较证据，不硬编码为业务验收阈值。
7. 取消未评估、无变化、L5大整数、损坏拒读、源变化、磁盘/进程中断恢复、只读无分析POST；0.5/零/负由组件测试与真实主样本分开。旧V2/V3/Token fixture兼容与真实旧state兼容区分，无真实state不能签现场全验。重启对照原报告/来源SHA不变。
8. 记录PASS/FAIL/NOT_RUN/ON_SITE_PENDING及设计对照。遇产品缺陷先停交付，整理最小复现/候选SHA/接口与日志/源码位置交开发修复，再复验；不自行改产品、不删断言或伪填结果。工具环境故障先解决环境，未运行不写PASS。

现有可复用脚本（运行前读参数和输出路径，全部用新attempt，不能照抄R覆盖）：
- `.venv/bin/python scripts/validation/v3_repair_e2e.py <新运行根> <新构建dist>`：会创建inputs/state并启动18002服务，要求端口先空闲。
- `.venv/bin/python scripts/validation/v3_repair_scale.py <新运行根> <新scale输出>`：四组实际长父来源，仍需后续固定资源核验。
- `.venv/bin/python scripts/validation/v3_repair_extra_cases.py <新运行根> <新extra输出>`：无变化/L5/取消。
- 停止该候选服务并确认所有任务终态后：`.venv/bin/python scripts/validation/v3_repair_memory.py <新运行根> <新scale输出> <新memory输出>`；复用该轮封存监控来源，仅新增任务。需恢复同候选服务做重启读取检查。
- `v3_repair_verify_resources.py <memory输出> <新核验输出>`独立重算原始profile/calibration/manifest/计数/RSS；不伪装成额外一次执行。
- Windows Node运行`v3_repair_browser.cjs <运行根> <新browser输出>`与`v3_repair_browser_extra.cjs <extra输出> <新extra-browser输出>`；脚本当前Chrome路径为本机Windows路径，迁移环境时核对，不能将mock smoke当实际E2E。
- WSL Node22.22.2用于viewer typecheck/lint/test/build；Windows Node运行Vitest曾因Linux原生依赖不匹配失败，不改锁文件掩盖环境问题。

定向回归参考：公共层/低命中unit（开发190项），integration的test_execution_v3_resources、test_sample_source_v3、test_prefix_repair_v3、test_v3_legacy_readonly、test_many_recipes_v3（42项），test_repair_fixtures_v3及test_clock_replay_v3；viewer完整363项、typecheck/eslint/build，mypy src/tokenscope、变更Python Ruff、`scripts/export_report_schema_v3.py --check`。根据独立审查发现补测，不机械重复无关全仓。执行期间冻结相关源码，防止父/worker加载不同身份。

## D02：Git与版本整理

D01通过后按个人项目流程，无PR。逐项审查、精确stage本次源码/测试/必要契约/脚本/设计及审批记录，再处理其他session文档归类；禁止git add .、全局reset/clean、覆盖他人dirty。特别注意新增sample-catalog.ts、sample-model.ts、sample_evidence_v3.py及新增测试/脚本不能漏进源码包。

你负责确定本次**全新、不覆盖11-11发布**的版本与release目录，核对前后端展示版本、源码commit、模型revision/template/资产摘要、V3增量契约hash；冻结V2契约保持。版本号/构建信息调整需列明与已验候选差异并作相应复验，不借机改逻辑或布局。

main纳入通过检查的源码/文档，显式`git push origin main`，核对remote与推送结果；backup/*只本地，不push --all/--mirror，不将带产物backup历史并入main。真实数据、模型大文件、state、dist、代码包/镜像不得入Git。审批DEMO源码和小型清单可保留；生成截图/历史证据按归档规则保护，不能为了clean状态删除。最终用固定commit构建，禁止共享dirty或开发旧dist直接装包；记录发布commit与原候选逐文件对应关系。

## D03：记忆、入口与归档

用户授权你整理本次相关记忆。共享文件先读最新再最小更新CURRENT/SESSIONS/docs入口/本线记忆：当前为LOCAL_USER_ACCEPTED，独立交付复验/构建状态按你的实际结果写；华为五真实收益ON_SITE_PENDING。开发负责以后缺陷修复，你负责本次交付复验/Git/版本/打包，产品职责不扩张、旧六线仍休眠。

把旧待审批、旧暂停、旧“不允许打包”标成历史，不能与最新用户决定并列为当前。闭环方案/prompt可按实际依赖归achieve并维护映射/链接；原始失败、发布包、SHA/冻结契约不重写。未完成工作和他人dirty不归档抹掉。保留清晰的本次用户前端审批→开发方案审批→本机人工通过→交付授权链。

## D04：构建、容器复验与交付

授权已包含打包，D01–D03满足后继续，不再重复请求打包许可。在新release目录从固定commit构建全新前端dist/源码包/镜像；使用交付线已验证的本地Docker与资产流程，不能因为WSL某shell没有docker就宣称容器验收通过。记录实际工具环境；必要环境不可用则如实阻断该步骤。

对最终镜像/代码包核对源码commit、前端实际HTTP资源SHA、模型资产、配置身份、非root/挂载/端口等既有交付规则。容器必须独立新state/新浏览器冷启动，先停前序候选、18002唯一；做真实小型五组分析/前端和必要兼容检查，证明实际包体与已验效果一致。包中不得混入开发state、合成实算报告作为生产结果或旧dist。构建不是开发自测替代，容器失败不带病发布。

交付包含镜像、代码、版本manifest/校验清单、适配本次版本的华为执行prompt与回退说明；WSL原包保留，按项目规则将完整交付目录复制到Windows桌面并逐文件校验SHA。不覆盖旧release。最后整理交付记录，更新版本/Git/包/容器验证状态；普通失败与遗留限制如实列明。

华为prompt必须结合现场已有上下文重写，不能原样复用11-11包含旧硬超时/旧独立模块逻辑的说明：
- 复用已认可约15万条用户监控/搜索/MA成果，保护CSV/既有state与旧包；一致副本上做兼容验证，不为本次五业务验收重新全量监控。
- 五组按上述模型/APPID在真实数据上逐一自动小样本分析，真实样本参考值与固定化风险可供业务沟通；不强求每组clock/正收益，不强制full，不写合成指标。
- 保留现场两阶段人工确认和已确认业务范围；新执行prompt明确哪些历史确认已复用、哪些仍待确认，不代签、不将休眠Token唤醒。
- 核实V100等实际设备/资产，不按“华为”推断NPU；现场127.0.0.1:18002与SSH隧道保持约定，不公网暴露。最终唯一候选演示服务保留并说明生命周期/健康检查，不能只测瞬时200就承诺永久可用。
- 回传仅一份Markdown，关键代码/最小diff/输入结构/真实结果/版本配置身份/日志/前后测试证据嵌正文。本轮本地通过不能改写为现场通过。

本授权是本地审查与打包，不自行SSH部署/执行华为任务。执行完向用户报告独立验收结论、发布commit/push结果、版本/包体路径与SHA、容器证据、现场prompt、保留服务及未决项。不能只说“打包成功”。

## 当前交接状态

开发已记录LOCAL_USER_ACCEPTED并准备本prompt；本文件的存在不表示镜像session已接收/执行或产物已生成。发送/接收与实际执行结果分别登记。开发本轮不代跑独立审查、不提交Git、不构建镜像。

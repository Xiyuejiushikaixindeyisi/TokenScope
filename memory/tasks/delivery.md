# V2总设计与交付记忆

2026-11-03最新阶段：异常公共层及四项后端已独立验收冻结，两前端接入完成，HV2-AF-01和HV2-MF-02已闭环；根339项前端、88项最终浏览器、135项鼠标核对及156资源重启一致性通过。源码版本整理/容器交付待继续，当前未发布本轮包体；现场真实数据仍待验。 下方执行日志和前序状态按时间追溯，以本段及当前入口为准。

实际session：01a1800e-80b4-7400-a78b-a84f5b6e888d，2026-11-03 Windows环境CODEX_THREAD_ID/CODEX_SESSION_ID再次一致核实。当前角色由用户明确指定为V2版本总设计师，历史全项目总设计/V1继续休眠。

用户已授权：依据两份华为报告直接协调六个既有开发session，先公共层验收、相关后端冻结，再前端接入；完整E2E后统一Git main提交/push、WSL构建/容器验证/代码镜像包、本地backup管理、Windows桌面全SHA核对、单Markdown华为执行prompt与文档记忆。不得重复索取同范围授权，也不得越过验收门槛。

当前：后端五关均已冻结，两前端产品源码已关闭。根完整335项前端及typecheck/lint/build通过；第一阶段空state真实HTTP和10项浏览器通过，156资源/业务表正常停启前后一致。正在继续旧功能/最终视觉回归，之后固定commit容器及交付；本轮产品尚未发布或打包。实际进度只认[执行板](../../docs/tasks/delivery/HV2_REPAIR_EXECUTION_20261103.md)与[独立结果](../../docs/tasks/delivery/HV2_INDEPENDENT_ACCEPTANCE_20261103.md)。

用户τ默认Qwen-V3.6-27B=1s、GLM-V5.2=2.7s、DeepSeek-V4-Flash=2.6s，K8192可选改；来源user_provided/未校准，前端日常只W/SLO。用户与异常共Trace模型规格，MA独立数据/制品；不能混源、同传互斥run或把文件观察时间当appid窗口。

证据边界：两报告原件保持。多模型目录缺口、全partial无默认、空recipe/内部fragment不完整分别核实；L4不是动态字段浪费/会话改写。DS真实cached缺失不能补0；GLM预热冲突保留原语义、其他有效真实指标显示。622条计数差/完整18MA SHA/Qwen48矩阵/实际冲突时刻/长尾及真实最小正反例仍待现场，不能假称已解决。没有新生产recipe或品牌驱动新探测器，profile不代表15万请求容量。

原始保护：派发HEAD7cbe286、8份既有dirty清单在artifacts/reviews/hv2-repair-20261103/identity-before.json，其他session修改保持。用户后端压缩后误读旧U008，实际docs-only提交d55df94并push；已核对并告知，不重写Git历史。本轮HV2产品代码仍未发布。各分线现禁止自行Git/监听/打包，恢复上下文先核对当前派发而非历史用户任务，详见执行板偏离记录。

旧交付tokenscope-v2-approved-20261102及旧包/state/证据/backup保持，回退读[历史交付](../../docs/tasks/delivery/V2_APPROVED_DELIVERY_20261102.md)。新验收必须停核实的旧进程/容器、确认端口释放，新空state和浏览器；保留批准四入口/UI02/UI04与最后L4/L5，UIR03留V3。现场真实Trace3/MA18，先量级预算；用户监控搜索TTFT→MA→第一次用户验收→指定appid方向异常→第二次验收；SSH18002，只回传一份Markdown关键源码/证据正文内嵌。[固定规则](../../docs/operations/DELIVERY_ACCEPTANCE_RULES.md) · [长期教训](../DELIVERY_LESSONS.md)。

[实施前过期记忆快照](../../achieve/2026-11-03/hv2-pre-implementation/README.md)已归档，原始报告/冻结契约不移动。新版华为prompt准备稿位于prompts/delivery/HUAWEI_V2_HV2_REAL_DATA_20261103.md，须实包通过后才发布，不让现场拿旧包执行。

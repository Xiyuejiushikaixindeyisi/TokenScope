# HV2-R1-ANALYSIS-FE-PREP：异常读取与批准展示接入准备

你承接V2总设计师直接派发的修复任务。用户已明确授权我（session 01a1800e-80b4-7400-a78b-a84f5b6e888d）协调六线开发/测试、独立验收、版本push及最终交付；本任务不是旧“暂停编码”的延续。先核实环境实际session ID，再读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md、本线ENTRY，以及 docs/tasks/delivery/HV2_REPAIR_EXECUTION_20261103.md 和 V2_REPAIR_COORDINATION_PLAN_20261103.md。

源码工作区 /home/zhangxiyue/TokenScope（Windows同一WSL UNC）。派发基线HEAD 7cbe28621f4e46083bf47f9aa14b011b3cb250c4；原交付源码 b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af。当前共享工作树有既有文档修改，保全基线在 artifacts/reviews/hv2-repair-20261103/identity-before.json。不得reset/clean/覆盖或提交其他session修改，不自行commit/push、Docker构建、部署、打包。日常本线单元/集成TestClient测试可执行；需要真实监听服务/E2E先在交接文档提出并由总设计师协调唯一环境，不能另端口保留旧服务并行。新候选E2E必须停旧、确认端口释放、独立新state与新浏览器。

先读两份原件相关章节，保持原件不改：
- docs/huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md，SHA256 93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e。
- docs/huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md，SHA256 51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83。

证据校正必须遵守：L4差异≠动态字段浪费/会话改写；报告无最终DOM证明。configured_recipe_count=0与TOKEN_FRAGMENT_INCOMPLETE不是同一根因，后者源码在fragment.coverage.complete为false时触发。V2Records本来能记50个run，不是实际单槽；现接口没有GET /monitoring/user-v2/runs目录。独立审计有效数151320与索引150698之差尚无逐行映射，不能照抄“全因窗口/去重”。Qwen逐UUID矩阵、完整MA文件SHA、实际疑似正反例及脚本正文未完整嵌入报告，属于证据缺口，不伪造现场复现。允许用清楚标记的最小合成fixture复现已知结构，不能冒称真实数据/现场通过。

保持用户批准四入口HTML和最后L4/L5，UIR-03留V3；不新设计、不自动恢复T1/hybrid/Agent、不改原CSV或已发布结果。用户/异常共Trace模型规格，MA独立制品数据。业务GET只读；保持精度、null/0、身份、范围、固定版本、缓存/SSE、恢复和导出完整性。性能优化不得删断言、绕过Schema或把partial改ready。

仅修改你获分配的源码/本线测试/文档与记忆。总设计师维护CURRENT、SESSIONS、总执行板和跨线入口；本轮请不要改这几份共享总文档。其他公共app/CLI/锁/构建文件若确需改变，先在交接中列精确补丁及依赖，由总设计师安排窗口，不擅自并发改写。结束交付含身份SHA、精确变更清单、实际命令/结果、修复前后证据、契约差异/兼容、未决项、复验步骤。总设计师通过wait/read及共享交接文档跟进；无需发跨会话消息，不派生新session或子agent。

当前仅阅读、事实核查与接入/测试方案，不修改产品或测试代码、不启动服务或构建。先验收公共层，再相关后端，冻结契约后才向你发正式前端实施任务。

调查§5：所有partial导致defaults=[]，已有L4 difference-groups可读；最终DOM缺证。loadReport实际读report/summary/recommendations/difference-groups，不是把report.items/finding塞卡片。报告“L4证明动态字段”“TOKEN_FRAGMENT_INCOMPLETE因零recipe”不成立，要按实际源码分因。公共层正在修方向、预算隔离、partial可读候选和无recipe状态；先列消费需求，不能提前依猜测API编码。

准备后续裸入口partial-only可发现/可读且明确部分完成、ready优先、历史task固定/分页/方向/模型/APPID/新发布不串、L4/L5批准聚合与唯一请求数、空优化建议仍展示已有差异及真实原因。L1–L3完整收益严格>1pp与现T2–T4语义不降低，不恢复T1。保持已批准四入口和最后L4/L5，UIR-03留V3，不接管监控/MA前端或后端。

交 docs/tasks/viewer/analysis/HV2_FRONTEND_PREP_20261103.md，含批准HTML/SHA、实际读取链及边界、字段/契约需求、冷浏览器缺省partial/显式历史与刷新恢复的验收方案。只维护本线入口/记忆；不改CURRENT/SESSIONS/总板，不占共享前端壳。完成准备后停止等待正式冻结接入任务。

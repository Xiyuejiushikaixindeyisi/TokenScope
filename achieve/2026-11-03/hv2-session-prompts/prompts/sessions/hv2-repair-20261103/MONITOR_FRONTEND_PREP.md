# HV2-R1-MONITOR-FE-PREP：等待后端冻结的前端接入准备

你承接V2总设计师直接派发的修复任务。用户已明确授权我（session 01a1800e-80b4-7400-a78b-a84f5b6e888d）协调六线开发/测试、独立验收、版本push及最终交付；本任务不是旧“暂停编码”的延续。先核实环境实际session ID，再读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md、本线ENTRY，以及 docs/tasks/delivery/HV2_REPAIR_EXECUTION_20261103.md 和 V2_REPAIR_COORDINATION_PLAN_20261103.md。

源码工作区 /home/zhangxiyue/TokenScope（Windows同一WSL UNC）。派发基线HEAD 7cbe28621f4e46083bf47f9aa14b011b3cb250c4；原交付源码 b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af。当前共享工作树有既有文档修改，保全基线在 artifacts/reviews/hv2-repair-20261103/identity-before.json。不得reset/clean/覆盖或提交其他session修改，不自行commit/push、Docker构建、部署、打包。日常本线单元/集成TestClient测试可执行；需要真实监听服务/E2E先在交接文档提出并由总设计师协调唯一环境，不能另端口保留旧服务并行。新候选E2E必须停旧、确认端口释放、独立新state与新浏览器。

先读两份原件相关章节，保持原件不改：
- docs/huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md，SHA256 93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e。
- docs/huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md，SHA256 51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83。

证据校正必须遵守：L4差异≠动态字段浪费/会话改写；报告无最终DOM证明。configured_recipe_count=0与TOKEN_FRAGMENT_INCOMPLETE不是同一根因，后者源码在fragment.coverage.complete为false时触发。V2Records本来能记50个run，不是实际单槽；现接口没有GET /monitoring/user-v2/runs目录。独立审计有效数151320与索引150698之差尚无逐行映射，不能照抄“全因窗口/去重”。Qwen逐UUID矩阵、完整MA文件SHA、实际疑似正反例及脚本正文未完整嵌入报告，属于证据缺口，不伪造现场复现。允许用清楚标记的最小合成fixture复现已知结构，不能冒称真实数据/现场通过。

保持用户批准四入口HTML和最后L4/L5，UIR-03留V3；不新设计、不自动恢复T1/hybrid/Agent、不改原CSV或已发布结果。用户/异常共Trace模型规格，MA独立制品数据。业务GET只读；保持精度、null/0、身份、范围、固定版本、缓存/SSE、恢复和导出完整性。性能优化不得删断言、绕过Schema或把partial改ready。

仅修改你获分配的源码/本线测试/文档与记忆。总设计师维护CURRENT、SESSIONS、总执行板和跨线入口；本轮请不要改这几份共享总文档。其他公共app/CLI/锁/构建文件若确需改变，先在交接中列精确补丁及依赖，由总设计师安排窗口，不擅自并发改写。结束交付含身份SHA、精确变更清单、实际命令/结果、修复前后证据、契约差异/兼容、未决项、复验步骤。总设计师通过wait/read及共享交接文档跟进；无需发跨会话消息，不派生新session或子agent。

你负责用户监控、搜索排行、MA和TTFT前端。当前仅阅读/梳理批准HTML及必要测试方案，不写产品或测试代码、不启动服务/构建；对应用户与MA后端实现并通过总设计师独立验收、冻结契约后，才另发正式开发任务。

调查§4/§6：准备恢复同APPID全部模型发现与切换（服务端新目录正在用户后端实现，不依赖localStorage或手填runID）；保持V2搜索/排序/TTFT和固定历史。TTFT日常只有等待时间W和SLO T，后端自动取逐模型τ与默认K8192，K覆盖是可选；参数未配明确不可算。MA在批准布局内解释独立/配对和缺失原因，独立可用值不应被配对缺失遮蔽，绝不将独立值冒充paired、null补0。GLM真实小时值和DS独立ideal须在后续真实浏览器核查。

保持四入口、已批HTML/UI-02/UI-04与L4/L5（异常页面由另前端维护），UIR-03留V3。先锁批准HTML及当前源SHA，形成差异/接入/验收清单，不另做布局设计。共享壳/路由/样式/API客户端/schema变动将由总设计师安排单一窗口，当前不占用。

交 docs/tasks/viewer/monitoring-v2/HV2_FRONTEND_PREP_20261103.md：后端依赖/消费者要求、批准HTML源与SHA、待冻结字段、冷state多模型/TTFT/MA浏览器复验步骤、需后端说明的空值/范围。只更新本线入口及memory/tasks/viewer-monitoring-v2.md，不改CURRENT/SESSIONS。完成后等待正式接入通知。

# HV2-R1-COMMON：异常公共层先行修复并交独立验收

你承接V2总设计师直接派发的修复任务。用户已明确授权我（session 01a1800e-80b4-7400-a78b-a84f5b6e888d）协调六线开发/测试、独立验收、版本push及最终交付；本任务不是旧“暂停编码”的延续。先核实环境实际session ID，再读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md、本线ENTRY，以及 docs/tasks/delivery/HV2_REPAIR_EXECUTION_20261103.md 和 V2_REPAIR_COORDINATION_PLAN_20261103.md。

源码工作区 /home/zhangxiyue/TokenScope（Windows同一WSL UNC）。派发基线HEAD 7cbe28621f4e46083bf47f9aa14b011b3cb250c4；原交付源码 b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af。当前共享工作树有既有文档修改，保全基线在 artifacts/reviews/hv2-repair-20261103/identity-before.json。不得reset/clean/覆盖或提交其他session修改，不自行commit/push、Docker构建、部署、打包。日常本线单元/集成TestClient测试可执行；需要真实监听服务/E2E先在交接文档提出并由总设计师协调唯一环境，不能另端口保留旧服务并行。新候选E2E必须停旧、确认端口释放、独立新state与新浏览器。

先读两份原件相关章节，保持原件不改：
- docs/huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md，SHA256 93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e。
- docs/huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md，SHA256 51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83。

证据校正必须遵守：L4差异≠动态字段浪费/会话改写；报告无最终DOM证明。configured_recipe_count=0与TOKEN_FRAGMENT_INCOMPLETE不是同一根因，后者源码在fragment.coverage.complete为false时触发。V2Records本来能记50个run，不是实际单槽；现接口没有GET /monitoring/user-v2/runs目录。独立审计有效数151320与索引150698之差尚无逐行映射，不能照抄“全因窗口/去重”。Qwen逐UUID矩阵、完整MA文件SHA、实际疑似正反例及脚本正文未完整嵌入报告，属于证据缺口，不伪造现场复现。允许用清楚标记的最小合成fixture复现已知结构，不能冒称真实数据/现场通过。

保持用户批准四入口HTML和最后L4/L5，UIR-03留V3；不新设计、不自动恢复T1/hybrid/Agent、不改原CSV或已发布结果。用户/异常共Trace模型规格，MA独立制品数据。业务GET只读；保持精度、null/0、身份、范围、固定版本、缓存/SSE、恢复和导出完整性。性能优化不得删断言、绕过Schema或把partial改ready。

仅修改你获分配的源码/本线测试/文档与记忆。总设计师维护CURRENT、SESSIONS、总执行板和跨线入口；本轮请不要改这几份共享总文档。其他公共app/CLI/锁/构建文件若确需改变，先在交接中列精确补丁及依赖，由总设计师安排窗口，不擅自并发改写。结束交付含身份SHA、精确变更清单、实际命令/结果、修复前后证据、契约差异/兼容、未决项、复验步骤。总设计师通过wait/read及共享交接文档跟进；无需发跨会话消息，不派生新session或子agent。

当前允许实施并完成公共层代码、测试、交接；低命中私有探测器改进等公共层验收后再继续。你是低命中与公共层唯一维护方。

证据与复现：调查§5，全部任务partial、defaults=[]；max_findings=100后低命中仅查3请求，Token随后可能继承耗尽预算形成不完整fragment；recommendation_engine.py:64–69对此报TOKEN_FRAGMENT_INCOMPLETE。contracts.py DiagnosticSelection强制Token，而用户曾明确两大Qwen只low_hit。service/extension不得仍无条件运行禁用方向。

必须完成：
1. 支持low_hit-only、token-only、both，至少一方向；从提交验证、能力声明、intent/幂等、调度、回执、coverage、发布、重试/恢复、推荐扩展到读取全链按显式选择执行。禁用Token时不调用Token plugin/adapter/recipe扫描，禁用low_hit亦同。旧已封存任务兼容只读，不重写冻结旧Schema；有协议变化必须新版本/能力，文档和样例同时形成。
2. 分开“遍历/候选/规则适用与执行覆盖”和“findings/证据保留预算”。修复低命中耗尽全局findings后把后续方向/fragment全污染的问题。预算必须仍有界且可取消；不能只把100乘10、无限存储或伪称全量。对真实扫描/比较预算耗尽、证据保留截断分别输出诚实coverage/停止原因/分母与计数，不让某条高频规则静默饿死其余方向。低命中私有规则语义不在此阶段改变，必要调用点适配可以做并列明。
3. published partial应有可靠、版本化的发现/读取路径。保留ready语义，不伪造ready/default_eligible；可提供明确的已发布partial fallback选择信息或等价版本化策略，优先完整ready，只有partial时消费者能显式标“部分完成”并读取已有成果；错误/中断、legacy、历史固定task、binding/方向/新任务发布不串结果。L4/L5差异组独立于recommendations为空仍可读。
4. 无recipe、fragment不完整、无业务依据、预算不足四类原因拆开。空recipe避免没有产出的逐请求提案提取，但不改变低命中发布或虚称已评估；保留必要coverage和读旧报告。不能造recipe/收益，L1–L3完整收益>1pp门槛不动。
5. 增加足够可审查的阶段计时/消耗与覆盖信息（不泄露正文），以区分源读取、检测、保留、提案、评估；计时不可从terminal间隔伪造。优先形成可被两私有后端消费的最小稳定公共能力，避免过度重构。

唯一源码窗口：src/tokenscope/analysis_common/；src/tokenscope/api/diagnostics*.py；对应公共测试；必要低命中调用点须在handoff标清。禁止改src/tokenscope/token_content、用户/MA源码及前端。共享src/tokenscope/api/app.py、cli.py、pyproject/锁只提出补丁不直接改。你本线docs/tasks/prefix-analysis、docs/tasks/analysis及公共新增契约目录可维护，旧冻结目录不改。

验收至少包含：超过保留上限但后续方向不被饿死；有界内存/确定性计数；真实比较截断仍partial；单/双方向精确调用（禁用adapter抛异常应完全不触发）；缺/空recipe不会扫描全量；partial-only catalog与分页/实例变化/固定历史/重启；API GET无队列/写库/计算；旧报告/旧Schema兼容。请运行本线和受影响公共测试及静态检查，交精确命令，不能只准备计划。

优先完成公共层，交 docs/tasks/prefix-analysis/HV2_COMMON_HANDOFF_20261103.md；在该交接列 proposed→implemented接口及源SHA/新契约文件路径/样例SHA/测试。完成后等待总设计师独立验收；未收到通过通知不自行进入低命中私有第二阶段或前端。

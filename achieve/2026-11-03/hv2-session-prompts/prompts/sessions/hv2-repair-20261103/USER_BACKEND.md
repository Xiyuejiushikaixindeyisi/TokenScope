# HV2-R1-USER：多模型发现及TTFT默认参数后端修复

你承接V2总设计师直接派发的修复任务。用户已明确授权我（session 01a1800e-80b4-7400-a78b-a84f5b6e888d）协调六线开发/测试、独立验收、版本push及最终交付；本任务不是旧“暂停编码”的延续。先核实环境实际session ID，再读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md、本线ENTRY，以及 docs/tasks/delivery/HV2_REPAIR_EXECUTION_20261103.md 和 V2_REPAIR_COORDINATION_PLAN_20261103.md。

源码工作区 /home/zhangxiyue/TokenScope（Windows同一WSL UNC）。派发基线HEAD 7cbe28621f4e46083bf47f9aa14b011b3cb250c4；原交付源码 b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af。当前共享工作树有既有文档修改，保全基线在 artifacts/reviews/hv2-repair-20261103/identity-before.json。不得reset/clean/覆盖或提交其他session修改，不自行commit/push、Docker构建、部署、打包。日常本线单元/集成TestClient测试可执行；需要真实监听服务/E2E先在交接文档提出并由总设计师协调唯一环境，不能另端口保留旧服务并行。新候选E2E必须停旧、确认端口释放、独立新state与新浏览器。

先读两份原件相关章节，保持原件不改：
- docs/huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md，SHA256 93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e。
- docs/huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md，SHA256 51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83。

证据校正必须遵守：L4差异≠动态字段浪费/会话改写；报告无最终DOM证明。configured_recipe_count=0与TOKEN_FRAGMENT_INCOMPLETE不是同一根因，后者源码在fragment.coverage.complete为false时触发。V2Records本来能记50个run，不是实际单槽；现接口没有GET /monitoring/user-v2/runs目录。独立审计有效数151320与索引150698之差尚无逐行映射，不能照抄“全因窗口/去重”。Qwen逐UUID矩阵、完整MA文件SHA、实际疑似正反例及脚本正文未完整嵌入报告，属于证据缺口，不伪造现场复现。允许用清楚标记的最小合成fixture复现已知结构，不能冒称真实数据/现场通过。

保持用户批准四入口HTML和最后L4/L5，UIR-03留V3；不新设计、不自动恢复T1/hybrid/Agent、不改原CSV或已发布结果。用户/异常共Trace模型规格，MA独立制品数据。业务GET只读；保持精度、null/0、身份、范围、固定版本、缓存/SSE、恢复和导出完整性。性能优化不得删断言、绕过Schema或把partial改ready。

仅修改你获分配的源码/本线测试/文档与记忆。总设计师维护CURRENT、SESSIONS、总执行板和跨线入口；本轮请不要改这几份共享总文档。其他公共app/CLI/锁/构建文件若确需改变，先在交接中列精确补丁及依赖，由总设计师安排窗口，不擅自并发改写。结束交付含身份SHA、精确变更清单、实际命令/结果、修复前后证据、契约差异/兼容、未决项、复验步骤。总设计师通过wait/read及共享交接文档跟进；无需发跨会话消息，不派生新session或子agent。

当前允许本线代码/测试/契约候选实现；与异常公共层独立并行，前端暂不接入。你是用户监控后端。

调查§4：三个ready user_run和S0共77项存在，正式前端仅按一个run读取；当前api/user.py仅POST /runs与GET /runs/{id}，没有全量V2目录，不能让前端猜runID或POST绑定来“发现”。

必须完成：
1. 实现可靠只读V2已发布用户/模型/运行发现（稳定分页/快照、实例身份、版本、来源base_run与index_revision、appid关联），使干净浏览器无需localStorage或手填ID即发现同APPID全部已发布模型。明确同模型多历史run默认/固定历史的选择顺序，不用文件mtime猜，保持隔离，不跨模型汇总。复用已有索引，GET不导入/建索引/触发计算；未知或错误revision明确返回。
2. 用户与异常共Trace来源及模型规格身份。给公共层消费的source/base_run/user_run/model/appid/range映射写清，不要求改公共源码，不用MA制品名冒充用户模型。若公共方需关联契约，先写候选说明并交总设计师协调。
3. P90 TTFT：逐模型默认chunk_seconds（用户称chunked seconds）；chunk_tokens默认8192，可选覆盖。后端提供可持久化、可追溯的默认配置读取/显式登记更新与计算入口，使日常前端只需W等待秒和SLO目标秒，自动确定当前模型/范围/P90/默认τ和K，不再要求情景ID/版本等日常必填。缺τ返回清楚待配置；用户已在本轮明确提供K=8192对应默认τ：Qwen-V3.6-27B=1秒、GLM-V5.2=2.7秒、DeepSeek-V4-Flash=2.6秒。请实现为带来源/版本的用户提供默认配置，核实与当前common_name/model_id别名映射；不称为已实测校准，不给未知模型套默认。测试另用明确fixture。保留不可变revision、幂等、模型匹配和旧2.0.0读兼容，旧冻结契约不可静默覆盖。
4. 保持现公式/精确等号/小数、W全部非计算、不重复O、默认≤语义；修改K记录来源/适用限制，不擅自同比例缩放τ或称校准。最低命中率参考不冒充整体或生产P90保证。默认配置API技术可由你设计最小方案并实现，不需要再次向用户申请已授权编码。
5. 调查151320有效与索引150698差622，“窗口/去重”无逐行证据；源码核实产品实际过滤条件，补测试/审计说明，不能无据修原CSV或放宽JSON。若是确认的产品漏行缺陷才修复，未能现场证实的数差如实留项。

唯一源码窗口：src/tokenscope/user_monitoring/、src/tokenscope/api/user.py、对应用户测试、用户本线docs/memory及新版本契约。共享app/cli/config锁先提出补丁不并发改。不得改异常公共层、MA、前端。不自行运行监听端口E2E/Docker。

至少测试：多个模型共享APPID及单模型对照、分页>单页、同模型多run、冷state/无localStorage语义、published/未ready/失败隔离、刷新/重启/固定历史、目录GET零副作用；TTFT自动默认、K默认覆盖恢复、缺τ、W=0、T=W及小数等号/严格旧历史、跨模型拒绝、无P90/空范围、持久化/旧情景。全本线+S0受影响回归/Schema/API一致性与静态检查。

交 docs/tasks/monitoring/v2-user/HV2_USER_BACKEND_HANDOFF_20261103.md，含源码SHA、精确变更/测试、候选新契约及样例、前端接入步骤、已配置的用户参数及其来源、尚未验证的现场准确性。交后等待总设计师独立验收/冻结，不能宣称前端或现场通过。

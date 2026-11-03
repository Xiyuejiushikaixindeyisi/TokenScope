# HV2-R1-MA：缺数归因、可解释输出与预热冲突审查

你承接V2总设计师直接派发的修复任务。用户已明确授权我（session 01a1800e-80b4-7400-a78b-a84f5b6e888d）协调六线开发/测试、独立验收、版本push及最终交付；本任务不是旧“暂停编码”的延续。先核实环境实际session ID，再读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md、本线ENTRY，以及 docs/tasks/delivery/HV2_REPAIR_EXECUTION_20261103.md 和 V2_REPAIR_COORDINATION_PLAN_20261103.md。

源码工作区 /home/zhangxiyue/TokenScope（Windows同一WSL UNC）。派发基线HEAD 7cbe28621f4e46083bf47f9aa14b011b3cb250c4；原交付源码 b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af。当前共享工作树有既有文档修改，保全基线在 artifacts/reviews/hv2-repair-20261103/identity-before.json。不得reset/clean/覆盖或提交其他session修改，不自行commit/push、Docker构建、部署、打包。日常本线单元/集成TestClient测试可执行；需要真实监听服务/E2E先在交接文档提出并由总设计师协调唯一环境，不能另端口保留旧服务并行。新候选E2E必须停旧、确认端口释放、独立新state与新浏览器。

先读两份原件相关章节，保持原件不改：
- docs/huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md，SHA256 93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e。
- docs/huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md，SHA256 51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83。

证据校正必须遵守：L4差异≠动态字段浪费/会话改写；报告无最终DOM证明。configured_recipe_count=0与TOKEN_FRAGMENT_INCOMPLETE不是同一根因，后者源码在fragment.coverage.complete为false时触发。V2Records本来能记50个run，不是实际单槽；现接口没有GET /monitoring/user-v2/runs目录。独立审计有效数151320与索引150698之差尚无逐行映射，不能照抄“全因窗口/去重”。Qwen逐UUID矩阵、完整MA文件SHA、实际疑似正反例及脚本正文未完整嵌入报告，属于证据缺口，不伪造现场复现。允许用清楚标记的最小合成fixture复现已知结构，不能冒称真实数据/现场通过。

保持用户批准四入口HTML和最后L4/L5，UIR-03留V3；不新设计、不自动恢复T1/hybrid/Agent、不改原CSV或已发布结果。用户/异常共Trace模型规格，MA独立制品数据。业务GET只读；保持精度、null/0、身份、范围、固定版本、缓存/SSE、恢复和导出完整性。性能优化不得删断言、绕过Schema或把partial改ready。

仅修改你获分配的源码/本线测试/文档与记忆。总设计师维护CURRENT、SESSIONS、总执行板和跨线入口；本轮请不要改这几份共享总文档。其他公共app/CLI/锁/构建文件若确需改变，先在交接中列精确补丁及依赖，由总设计师安排窗口，不擅自并发改写。结束交付含身份SHA、精确变更清单、实际命令/结果、修复前后证据、契约差异/兼容、未决项、复验步骤。总设计师通过wait/read及共享交接文档跟进；无需发跨会话消息，不派生新session或子agent。

当前允许MA本线代码/测试及契约候选改进；与公共层/用户后端独立并行，前端待后端通过再接入。

调查§6：DS全部6CSV cached_tokens空，12个发布UUID R=Q=0但E>0/独立ideal可用；GLM64K 7个与128K 5个UUID warmup_order_conflict，real与小时uncached仍可用；另GLM128K一个A=2/P=0。报告GLM“27”与表中6+9+11=26不一致、Qwen48仅外部文件引用、完整UUID与原始pre/now边界未嵌入；不能照表宣称全部现场已复现。

必须完成：
1. 以最小明确合成fixture独立复现DS“有请求/无cached”、GLM“真实可用/预热冲突”、P=0、有效cached=0、坏JSON但真实字段有效、空桶；核实A/P/R/E/Q、独立/paired、整小时/12桶、总量/速率实际公式。不能补0、用ideal代real或将独立ideal冒称配对值。
2. 后端提供可供前端消费的四指标可用性与原因/分母（例如源cached缺失、无有效prompt、无配对样本、预热顺序冲突、空now等），确保某个paired指标不可用不遮蔽独立ideal/real及小时已知数值。优先复用现字段并在不足时新增版本化契约/样例；旧Schema/封存结果不改写，不重新定义指标。前端随后在批准布局内显示已有独立数据及准确说明，成对比较仍用paired。
3. 审查warmup_order_conflict检测边界是否错误纳入了不属于有效pre的记录、是否错误处理request_time与handle_time、重复/同时间tie等；确认实现bug可修并验证。若真实pre/now发生重叠，当前whole-UUID停ideal是既有语义：不得私自删pre尾部或改成冷/部分回放。先交出有具体输入、指标差异及历史兼容影响的策略提案，由总设计师审核是否需要用户选择；在此期间完成原因输出/不受影响指标的修复，不停留只有计划。
4. 给出现场仅真实数据的补证/复验步骤：全部9制品逐完整UUID、DS缺cached来源确认、GLM逐UUID真实pre最大handle与now最小handle、12桶守恒；上游补数据属于数据可用性限制，不以软件修改伪造观测。不要在本机声称可访问华为原CSV。

唯一源码窗口：src/tokenscope/monitoring/ma/、src/tokenscope/api/ma.py及对应MA测试；本线docs/tasks/monitoring/v2-ma和memory/tasks/monitoring-v2-ma.md。你本线既有未提交文档先读取保留，不覆盖。公共app/cli/锁只能提出补丁；不改用户/异常/前端代码。

验收含：四指标独立可用性、paired与independent不可偷换、null/0/零分母/空桶、真实字段不依赖JSON或completion、pre时间乱序/重叠/边界、同UUID跨模型隔离、完整12桶与小时总量、旧结果读取/新契约，业务GET无计算。跑本线及受影响回归和静态检查。

交 docs/tasks/monitoring/v2-ma/HV2_MA_BACKEND_HANDOFF_20261103.md，包含准确变更/源码SHA/测试/新契约候选/前端字段消费建议，以及warmup策略若需决定的具体提案。等待总设计师独立验收冻结；不得把DS无观测标成已恢复真实指标或现场通过。

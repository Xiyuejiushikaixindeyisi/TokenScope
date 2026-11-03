# HV2-R3-ANALYSIS-FE 正式接入任务

由V2总设计师01a1800e-80b4-7400-a78b-a84f5b6e888d按用户授权直接派发至既有异常前端session 01a19111-344a-75c1-84e0-14db8be08f4f。两类私有后端已于2026-11-03由总设计师独立验收冻结，本文件实际发送后正式生效；不要把此前PREP或历史UIR/RV2任务当当前实施指令。

先核实实际ID，读AGENTS、CURRENT、SESSIONS、docs/README及本线ENTRY、HV2_FRONTEND_PREP_20261103.md。本轮依赖验收见docs/tasks/delivery/HV2_INDEPENDENT_ACCEPTANCE_20261103.md及执行板。核对HV2_COMMON_FREEZE_20261103.json（公共组合9ac3e7fd5c5fea9556f957871bb03a0791e79e9404b207462a1cf8e184d7cb8e）、HV2_USER_FREEZE_20261103.json（4d9e2e5d6c7031ff0aaa266114b92dbcb8684b9a80d722d2cfae9de8ad1d7dc0）、本次HV2_TOKEN_FREEZE及HV2_LOW_HIT_FREEZE。公共第一关的prefix适配随后由第二关合法更新，按后者覆盖这些私有文件，不覆盖历史冻结证据。

阅读docs/contracts/diagnostics-execution-2/{README,wire,examples,manifest}.json/md、公共/Token/低命中HV2交接，用户后端2.1.0来源映射。新契约已冻结，本线不得改后端、旧冻结契约或把Schema校验删掉换通过。共享树其他线修改保留，不reset/clean/git add -A。只改apps/viewer/src/features/analysis、src/api/analysis、src/state/analysis-*及其生成脚本/本线测试、本线文档记忆。旧generated/锁应保留兼容，新增v2资源版本化，不重写旧契约身份。apps/viewer共享App/V2App/全局样式/构建包锁由总设计师维护；确需改动先在交接提出精确补丁。监控前端归另一session。

## 必须实现

1. 显式使用diagnostics-execution-2/v2 capabilities和catalog，不再把旧defaults当唯一可读入口。新selected_reports每binding×direction取ready优先，无ready时published partial fallback；明确部分状态/限制，不能改default_eligible或宣称partial完整。完整分页同snapshot/event_cursor，selected引用可能在后页；保留循环、重复、身份和计数校验。固定task/历史不自动跳到新任务。APPID/模型规格与Trace来源绑定一致，MA制品不可混入。
2. 裸入口新浏览器、全partial且已有L4/L5时能自动发现并展示批准卡片。report/recommendation-summary/recommendations/difference-groups仍分别读取；空建议、summary not_computed、零recipe不得屏蔽已发布差异组。不能把raw finding直接塞进批准建议卡。L4/L5各一张卡、完整RequestKey去重计请求、每类最多3个代表例子及原局部证据/返回焦点/滚动保持。
3. 通过v2 execution读取明确方向、扫描/比较/保留/规则覆盖及原因。NO_CONFIGURED_RECIPES、TOKEN_FRAGMENT_INCOMPLETE、FRAGMENT_RETENTION_TRUNCATED、FINDING_RETENTION_TRUNCATED、CANDIDATE_LOOKUP_TRUNCATED、比较/编码预算、缺业务依据分别表达，不能用数组空或checked数量猜因。null未知与0分开，适用对数null不得显示0；嵌套计时不可相加，重复source读数不当唯一请求。
4. 如果本页存在或维护提交流程，用v2显式方向、至少一种；仅低命中时不强制Token，已有选择与重试/幂等身份保持。用户未主动提交的页面访问/GET不触发分析。不要新增未经批准的表单或大改布局来显示所有工程遥测；只在现有状态/详情位置提供用户判断所需限制和真实结果。
5. 缓存key含服务实例/实际契约/任务/scope/digest/方向。v2 catalog继续用既有SSE通知，不改为3秒轮询；terminal/reset/断线/重启/前后台重对齐，旧响应不能落到新选择。旧report和v1资源兼容；新execution不可用时按明确版本给错误/历史兼容，不吞错或暗中降级。
6. 严格保留完整评估且收益>1pp的L1–L3门槛，T2–T4现有evaluated/advice/null/精确整数；不恢复T1、hybrid、Agent、逐项评估表单或伪造生产recipe。L4差异不等于动态字段浪费/会话改写。四入口/UI-02/UI-04和最后L4/L5展示不重新设计，UIR-03留V3。
7. 来源从用户2.1.0目录映射user_v2/user_run_id/appid/expected_index_revision/window=null，不同时传base_run_id；base用于核对。监控侧链接由监控前端维护，本线接收时验证精确run来源和固定历史，不能按相似模型名或文件观察时间擅自裁剪scope。

## 本线验证与交接

准备文档A01–A11按冻结语义实现单元/组件/客户端回归：partial-only/ready优先/固定历史/跨页快照变化/方向APPID模型切换迟到响应/服务重启SSE/无recipe有L4L5/旧not_computed差异/预算分别提示/精度null0/收益边界。实际聚合create_app与独立OpenAPI名字可能不同，若比较Schema须完整解析本地ref并核对字段约束，保留漂移拒绝；不要仅比ref名，也不要宽松忽略Schema。

允许本线npm typecheck/lint/test/build及TestClient类无监听测试。不要自行启动HTTP/Vite/browser E2E、Docker、Git提交/push、打包或部署。总设计师独立全新state/浏览器唯一服务环境完成E2E及视觉复审。自己的dist构建不是本机监听/现场通过。

完成docs/tasks/viewer/analysis/HV2_FRONTEND_HANDOFF_20261103.md，列精确文件/SHA、消费契约与样例、实际命令/结果、中间失败保留、修复前后证据、兼容/限制和冷浏览器复验步骤；更新本线ENTRY和memory/tasks/viewer-analysis.md。不得改CURRENT/SESSIONS/总执行板或其他session记忆。交接后关闭源码窗口待独立复审；无跨会话发送或子agent。上下文恢复必须继续本任务，不重启历史UIR修复或自行收口提交。

补充正式派发身份：Token组合14419e5bba5af85a3ffa20d6330b3fa29c2d926bd81ef1f3462e30b118b4f00d；低命中组合10f643bc56fa59936dcfd7d17f4aabf1163aba4d479c47662366d13c879e011b。监控前端指出本线SourceLink.tsx“查看原报告监控来源”需携带固定index revision，请在自己的窗口按冻结source/receipt核对后补齐，保留FS-01原run/APPID/instance断言；具体补丁也可读监控前端交接，不需等待其代改。

# HV2修复执行板（2026-11-03）

2026-11-03最新阶段：异常公共层及四项后端已独立验收冻结，两前端接入完成，HV2-AF-01和HV2-MF-02已闭环；根339项前端、88项最终浏览器、135项鼠标核对及156资源重启一致性通过。源码版本整理/容器交付待继续，当前未发布本轮包体；现场真实数据仍待验。 下方执行日志和前序状态按时间追溯，以本段及当前入口为准。


总负责：V2版本总设计师 `01a1800e-80b4-7400-a78b-a84f5b6e888d`（环境再次核实）。用户本轮已明确要求收到回传后启动修复并向对应session派发；原[总体计划](V2_REPAIR_COORDINATION_PLAN_20261103.md)的等待条件已满足，后端/公共层编码授权现已生效。前端正式编码仍依后端验收与契约冻结，发布仍依完整验收。下表实际派发状态由总负责记录，不由文稿存在推定。

## 证据与勘误

- [原验收](../../huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md)：SHA256 `93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e`，50443 bytes。
- [新调查](../../huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md)：SHA256 `51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83`，60524 bytes。原件不改；其自检“全部正文内嵌”并未完全成立。
- 调查表明3个ready用户run存在但正式多模型发现缺口；本机api/user.py没有GET全量V2目录，不能照建议假定端点已实现。V2Records支持50个历史，本地记录不足不是单槽覆盖/服务端丢数据。
- 全partial无ready默认、已有L4差异组、零recipe及fragment不完整是不同状态；源码recommendation_engine.py:64–69因fragment覆盖不完整停止，不能把它归因为零recipe。L4不证明动态字段浪费或会话改写；报告无实际最终DOM，必须本机真实浏览器独立验证。
- DS6文件cached_tokens100%空，使R/Q=0，真实两项不可伪造，独立ideal仍可用。GLM部分warmup_order_conflict使E/Q=0但R和小时量可用。表声称GLM27但行数6+9+11=26；Qwen48逐UUID矩阵和完整18MA SHA仍指外部文件。真实pre/now冲突时间未嵌入，缺口列入现场再验收。
- 原始有效151320与索引150698差622，无逐行过滤证据，不能采信全部窗口/去重解释。DS工具Schema字节与重复候选支持研究，不支持删除/收益/新探测器结论；真实最小正反例和研究脚本正文缺失。先修方向/预算/读取链与可测性能，不造业务recipe。
- Trace约26.88GB/354638行；现场state108GB、/home剩163GB，且容器8CPU/32GiB、tmp512MiB。新state保留旧state必须先重新核磁盘峰值；不能简单把预算上限全调大、由请求数或terminal间隔推运行成本。资源数据只是报告时点。

## 阶段与窗口

| 工作项 | 负责人/会话 | 当前状态 | 实施窗口/退出依赖 |
| --- | --- | --- | --- |
| 公共层方向/预算隔离/partial发布读取/推荐阶段状态 | 低命中率异常分析后端 01a18be2-7112-7aa2-919b-5137d1f1b1ad | 公共与低命中私有两关均已独立通过冻结，窗口关闭 | analysis_common与diagnostics API/对应测试；先独立验收公共层，再低命中私有第二阶段 |
| 多模型目录/TTFT逐模型默认配置与计算 | V2 用户监控-后端 01a18bc7-cdb5-7830-a185-ad3aa6257b21 | 2.1.0已独立验收冻结，前端接入中 | user_monitoring/api/user及对应测试；可并行，待独立验收冻结 |
| MA缺数解释/不受影响指标/冲突审查 | V2 MA 监控-后端 01a18ab2-2600-7ae1-8b0e-979dad9ec3be | 独立验收通过、已冻结（见下） | monitoring/ma/api/ma及对应测试；可并行，不擅改预热语义 |
| Token私有性能与规则准备 | Token异常分析后端设计和开发 01a18fcd-0464-7cf1-b435-4f394bd33e66 | 私有第二关已独立验收冻结 | token_content及本线测试/profile |
| 用户/MA/TTFT前端准备 | Token监控前端设计开发 01a18c49-d9b4-7a33-8c04-e5a72adfcc24 | 完整接入已交接，75项独立定点通过，源码窗口关闭待E2E | 完整浏览器及视觉由总负责统一执行 |
| 异常前端准备 | 异常分析前端设计与开发 01a19111-344a-75c1-84e0-14db8be08f4f | 两类私有后端通过，正式接入已实际发送成功 | 全部后端已冻结，正式编码窗口开放，HV2-AF-01修正复测中 |

完整prompt位于 [COMMON](../../../prompts/sessions/hv2-repair-20261103/COMMON.md)、[USER](../../../prompts/sessions/hv2-repair-20261103/USER_BACKEND.md)、[MA](../../../prompts/sessions/hv2-repair-20261103/MA_BACKEND.md)、[TOKEN准备](../../../prompts/sessions/hv2-repair-20261103/TOKEN_PREP.md)、[监控前端准备](../../../prompts/sessions/hv2-repair-20261103/MONITOR_FRONTEND_PREP.md)、[异常前端准备](../../../prompts/sessions/hv2-repair-20261103/ANALYSIS_FRONTEND_PREP.md)。

总设计师维护CURRENT/SESSIONS/执行板，开发session仅更新其模块入口/记忆。共享app.py、CLI、锁、构建配置、前端壳先提出精确补丁，由总负责安排单一窗口。各开发session不commit/push/打包、不自行开监听服务或Docker；本线单元/集成测试可在独立临时state运行。原有8份其他session修改保留，所有会话先读取最新文件；本轮保全基线 artifacts/reviews/hv2-repair-20261103/identity-before.json。

## 已知输入与待决

用户本轮已提供chunked seconds：Qwen-V3.6-27B=1s、GLM-V5.2=2.7s、DeepSeek-V4-Flash=2.6s，按默认K=8192登记。用户后端须带来源/版本落地并核对别名，不能标为已实测校准；未知模型仍待配置，K可选覆盖。GLM真正pre/now重叠的部分预热替代策略会改变既有语义，先由MA后端交具体方案供总设计师审查，不擅自截尾。DeepSeek真实cached观测需要上游数据，软件应解释缺失并保留独立ideal；不冒称修复后真实指标已可计算。tools/messages新增探测器仅有候选统计，先完成现能力适配/预算/可见性与成本验证，必要业务依据另列缺口。

完整E2E→固定源码提交push→WSL构建/Compose容器复验→新包与配置/SHA→桌面全文件SHA→本地backup→归档/入口/记忆→新版华为单Markdown回传prompt顺序继续有效；原包/state/证据不覆盖。现场真实Trace3/MA18、两阶段人工验收、SSH18002不变。

派发记录：六份完整prompt均已通过send_message_to_thread发送至上述已核实local会话，工具返回成功。任务文件SHA与目标记录见 artifacts/reviews/hv2-repair-20261103/dispatch.json。发送成功不等于开发完成；以接收进度/交接和独立验收分别登记。

派发后核对补充：Token准备线及总设计师检查确认，旧Token逐请求使用独立RunControl，当前未证实TaskControl.findings耗尽直接使Token fragment不完整。低命中保留上限与Token请求内预算必须分别复现，不能把并存现象写成因果；已通知公共维护方纠正该假设。异常前端在context压缩后误恢复旧UIR任务，已明确纠正回HV2准备任务，旧UIR结果不作新验收。

独立验收范围与后续实际结果入口：[验收记录](HV2_INDEPENDENT_ACCEPTANCE_20261103.md)。Token及监控前端准备已完成，等公共/对应后端冻结；这不是实现或验收完成。

## 本轮协作偏离与校正（2026-11-03）
用户后端session在上下文压缩后误接回历史U008提交任务，实际推送d55df94b6e58117a698dbd14667b7836e67cd50f（3份历史复核文档，16行）；不是本轮用户新增U008指令，不能据该提交宣称HV2完成。总设计师核对提交树仅文档、未包含候选源码/包体，保留提交事实不重写历史，并已重新派发HV2-R1-USER实现/测试/交接、禁止分线commit/push。此前异常前端也曾误恢复UIR，已纠正并完成HV2准备。后续每次恢复先以本轮最新消息、执行板和派发prompt核对任务，不以历史最后一条用户消息替换当前统筹任务。

## MA后端独立验收与冻结
2026-11-03，独立源码审查、66项MA回归、13项契约工具变异测试，以及单独混合UUID边界复核全部通过。补证验证同一文件A缺cached不会污染B原因，B有效0与空桶区分，小时/12桶守恒。全部本机合成输入，未代签现场。旧MA Schema/OpenAPI路径/组件/manifest字节保持，新资源完整DTO/OpenAPI/9样例/8负例通过。
冻结清单：[HV2_MA_FREEZE_20261103.json](HV2_MA_FREEZE_20261103.json)，组合SHA `9b48fb244963ce153b009a9a2d0d9050d084bd6c1bb43eec27ddf49f313fd9fa`。冻结范围仅后端解释资源及现有指标兼容；不代表前端、监听E2E或现场通过。原预热语义保持，用户如选择新策略需独立版本/验收。允许监控前端先接入MA部分；用户目录/TTFT仍等待其后端冻结。

## 用户后端独立验收与冻结
2026-11-03，已读实际4份源码及全部差异；独立62项新功能/Trace/旧契约回归通过（10.80s，源码/契约前后SHA一致），另6个跨三模型大于2**53的P90与精确小数le/lt等号场景通过，结果以Fraction独立算术核对。维护方最终271项监控与62项CSV/编码回归日志已核对。新2.1.0共14操作、旧9操作与旧冻结文件保持兼容；GET不创建索引或评估，默认配置启动登记且参数来源明确。
冻结清单[HV2_USER_FREEZE_20261103.json](HV2_USER_FREEZE_20261103.json)，组合SHA `4d9e2e5d6c7031ff0aaa266114b92dbcb8684b9a80d722d2cfae9de8ad1d7dc0`。证据artifacts/reviews/hv2-repair-20261103/user-independent。允许监控前端接入多模型目录与TTFT；未代签浏览器/现场/真实性能校准，622条真实差异与大历史目录规模另列限制。

## 异常公共层第一关独立验收通过
2026-11-03：实际diff/源码/新机器Schema/旧27项冻结字节独立核对；独立41项方向/保留/扫描/发现/旧runtime边界通过59.91s，前后源码无漂移；最后empty终态投影修正后另跑3项API/旧报告/禁用recipe边界通过15.61s（与41有重复，不相加）。维护方331项联合回归与之后23项专项、46源码mypy及ruff记录已核验。业务GET未计算且state SHA保持；from_wire真实响应一致。
冻结[HV2_COMMON_FREEZE_20261103.json](HV2_COMMON_FREEZE_20261103.json)，组合SHA `9ac3e7fd5c5fea9556f957871bb03a0791e79e9404b207462a1cf8e184d7cb8e`。前端及现场未通过；工具/messages真实新探测器依据不足、15万请求容量未校准。现开放低命中/Token私有测试/profile及经证据支持的局部优化；公共API/Schema及旧契约不允许并发修改。两条后端通过再开放异常前端。低命中私有若改变已记录适配源码，由第二阶段独立复核补新候选身份，不回写第一关原证据。

协作恢复补记：监控前端MA turn亦在压缩后误回历史RV2复审prompt，未执行已收到的用户/TTFT接入；总负责读取turn核实后重新明确继续MONITOR_FRONTEND_USER，保留已完成MA代码。此阶段不能因子任务最终回复而把整个监控接入标完成。

## Token私有后端第二关独立验收通过
2026-11-03：独立读两份源码差异、完整profile/预算/消费记录，候选仅结构序列化复用；独立完整私有171项通过94.33s，源码前后无漂移。另用原Git实现与固定种子510种Unicode/数值词法/嵌套结构比较计量完全一致。维护方完整fragment SHA和五类预算边界记录已核对，未改插件/DSL/授权/预算或收益门槛。
冻结[HV2_TOKEN_FREEZE_20261103.json](HV2_TOKEN_FREEZE_20261103.json)，组合SHA `14419e5bba5af85a3ffa20d6330b3fa29c2d926bd81ef1f3462e30b118b4f00d`。证据artifacts/reviews/hv2-repair-20261103/token-independent。只证明本机私有与公共消费兼容，不代表真实吞吐/全规模预算、前端或现场通过；源码窗口关闭，异常前端仍等待低命中第二关。

## 低命中私有后端第二关独立验收通过
2026-11-03：独立核对3份实际源码/差异与1024对文本等价测试、276份证据摘要和24配置profile；新增原因合并保留候选截断与比较预算并存，等文本快速返回不改规则/recipe。独立62项低命中/真实user_v2公共消费/完整评估门槛/组合/资源回归通过201.93s，源码前后稳定。公共冻结仅两项已授权私有适配变化，其余公共/Schema/旧兼容全部保持。
冻结[HV2_LOW_HIT_FREEZE_20261103.json](HV2_LOW_HIT_FREEZE_20261103.json)，组合SHA `10f643bc56fa59936dcfd7d17f4aabf1163aba4d479c47662366d13c879e011b`。第一关历史冻结不回写，当前这两份prefix源码按第二关身份。证据artifacts/reviews/hv2-repair-20261103/lowhit-independent；未代签真实量级/新探测器/现场收益。现两类私有后端均通过，允许正式派发异常前端接入。

正式派发记录：ANALYSIS_FRONTEND_IMPLEMENT.md已通过send_message_to_thread发至01a19111-344a-75c1-84e0-14db8be08f4f，返回成功；Token/低命中源码窗口已关闭并通知本人。前端接入实际完成及独立浏览器验收仍待执行。

## 前端独立预审发现（已完成源码与第一阶段复测）
HV2-AF-01：AnalysisApp主读取targetKey已含executionVersion，但more()写缓存仍用旧reportKey，可能使加载更多后的回读丢页/错版本key。已通过实际消息交异常前端统一键并补分页→详情→返回/重读回归；未放行完整E2E。
事实校正：冻结SourceIdentity不含index_revision，来源跳转不能声称比较原报告索引值；须核对不可变run/base/common/model/manifest身份并固定当前已核验索引。旧recommendation summary not_computed的实际API固定差异计数0且group page空；合法Schema投影的not_computed+组测试只能称防御性兼容，不冒称现场原始复现。真实主路径为computed、recipe=0/无建议、有已发布差异。

2026-11-03阶段推进：HV2-AF-01与两前端源码已独立335项通过；第一阶段10项真实浏览器、156资源与业务表正常停启一致性通过。全新第二state正在回归旧功能与最终视觉；测试执行器/旧选择器及ready前输入问题按独立验收记录保留，产品源码未为测试改动。仍未提交本轮产品或打包。

# V2总设计、审查与交付维护记忆

2026-11-03用户参数已补充：Qwen-V3.6-27B chunked seconds=1s，GLM-V5.2=2.7s，DeepSeek-V4-Flash=2.6s；K默认8192，可选修改。作为用户提供默认值登记来源和revision，不冒称已校准。该决定覆盖下方旧“参数尚缺”记录，见[执行板](../../docs/tasks/delivery/HV2_REPAIR_EXECUTION_20261103.md)。

2026-11-03收到华为调查（SHA256 51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83）。用户要求正式启动修复与六线任务派发；[执行板](../../docs/tasks/delivery/HV2_REPAIR_EXECUTION_20261103.md)记录勘误、窗口、状态与后续验收。优先公共方向/预算/发布读取，用户/MA后端并行；Token和前端先准备，验收冻结后接入。报告缺DOM与部分完整证据，不照抄L4动态字段或零recipe导致fragment不完整的结论。旧授权等待状态不再覆盖本轮。

2026-11-03最新决定：[V2修复统筹计划](../../docs/tasks/delivery/V2_REPAIR_COORDINATION_PLAN_20261103.md)已建立。等待华为新调查回传后，结合验收原件和调查证据直接向六个已有session派发开发/测试prompt；先验收低命中线维护的异常公共层，再完成相关后端、冻结契约、启动对应前端，最后本线独立E2E及已授权完整发布交付。无须重复申请同范围打包/push；当前未触发前置，不提前执行。用户与异常共Trace模型规格，MA另用制品数据；用户逐模型给chunked seconds，K默认8192可选改，前端日常仅等待时间/SLO。当前只改规划/入口/记忆，无源码/契约改动、无测试/服务/派发/commit/push/打包。下方此前“仅方案、不发送、不打包”是前一轮边界，不否定本次未来条件授权；实际旧测试与证据保留。

实际session ID：01a1800e-80b4-7400-a78b-a84f5b6e888d，2026-11-03环境CODEX_THREAD_ID/CODEX_SESSION_ID一致复核。角色：V2版本总设计师（原镜像打包与审查／完整服务总负责）；负责规划分配六线、独立审查与完整E2E、Docker/代码镜像交付、文档记忆、版本管理和push；业务开发/测试按模块归口。

2026-11-02历史交付已完成`tokenscope-v2-approved-20261102`：固定源码`b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af`已push main；WSL构建镜像`sha256:a38d0ab2cfe26154c96adb5e876538893005e5cb100fc5c53640823c391683a8`，实际容器85浏览器/135独立鼠标点/15范围/120GET恢复通过，11重启复测不累加。四入口/HTML/L4L5保持，HTTP四资源同c1；UIR-03由用户留V3，不修复或阻断V2。

代码/镜像包及prompt等14文件在`/home/zhangxiyue/TokenScope/artifacts/releases/tokenscope-v2-approved-20261102`，完整复制`C:\Users\ALIENWARE\Desktop\tokenscope-v2-approved-20261102`且全部SHA一致；旧包、WSL原件保留。实际docker load验证通过，backup`backup/20261102-tokenscope-v2-approved`仅本地manifest/SHA指针，不push、不合main。其他8份未完成文档修改保留。[完整结果/文件SHA/回退](../../docs/tasks/delivery/V2_APPROVED_DELIVERY_20261102.md) · [结构化记录](../../docs/tasks/delivery/V2_APPROVED_DELIVERY_RESULT_20261102.json)。

2026-11-03当前P0：用户明确第二次华为验收不通过。本轮读取[报告原件](../../docs/huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md)及相关源码/契约，形成[修复与研究方案](../../docs/huawei/HUAWEI_V2_REVIEW_AND_RESEARCH_PLAN_20261103.md)与[华为只读调研任务书草案](../../docs/huawei/HUAWEI_V2_HEURISTIC_RESEARCH_BRIEF_20261103.md)，尚未下发或执行。报告SHA256 `93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e`，50,443 bytes，原件不改。

- HV2-01：V1发布源码有同APPID多模型目录/按钮，V2正式UserMonitor为单user_run静态模型标签；恢复同入口完整模型可见与切换，保持V2搜索/TTFT，不能靠手填ID或发多个URL交差。
- HV2-02：异常页无结果；loadReport实际消费summary/recommendations/difference-groups，不是report.items。10任务均partial而默认仅ready，需现场URL/完整task/目录/网络链证实；不绕过Schema/身份校验，不降低L1–L3收益门槛，L4/L5保持批准聚合展示。
- HV2-08：用户报告DeepSeek全部UUID、GLM部分UUID缺理想/真实命中率、整小时重算Token/s、实际重算Token。主表paired与详情independent不同；报告一个实例R=0/Q=0但独立ideal约35.97%。逐UUID查原CSV字段→A/P/R/E/Q→API→DOM。request_input坏JSON不会单独令R=0；真实0/null不可混淆，不先定为源无观测或前端bug。
- HV2-03/04/05/06：方向控制、预算覆盖、性能和数据质量需归口方案。用户两大Qwen只选low_hit但现契约强制Token，这不是多执行授权。100findings上限可能只扫3请求；候选上限亦能partial；不能仅加预算。Trace拒绝57.51%，需全原因审计，原CSV不正则改写。空recipe仍提取可能耗时，需profile证实。
- 先由华为清点Trace3/MA18的文件/范围/结构/长尾/候选/扩展预算/机器资源，再研究tools/messages真实场景及候选探测器。L4差异不是动态字段根因；模型品牌不等于工作负载；T1/hybrid/Agent不自动恢复或启动。调查仅10个已选范围深度开展，全局只做清点。

2026-11-03后续：已按用户要求形成[完整可直接转发prompt](../../prompts/delivery/HUAWEI_V2_READONLY_INVESTIGATION_20261103.md)，不依赖开发机方案文件。明确身份/资源→真实量级/预算→多模型/异常空白/MA缺数→有界tools/messages研究；允许独立统计取证脚本，禁止修改产品/原数据/已发布结果或重跑正式任务。只交一份`HUAWEI_V2_INVESTIGATION_REPORT_20261103.md`，关键源码/证据正文内嵌。实际session ID仍由本轮环境两ID一致复核；本机仅准备文稿及更新入口，未向华为发送、未执行调查。

本轮边界：只读分析及文档记忆，不改产品/测试/构建代码和契约；不启动服务/复测/现场研究，不发送session消息，不commit/push/打包。其他8份既有修改保留；保全清单与核查记录位于`artifacts/reviews/huawei-v2-report-review-20261103/`。旧部署prompt是已发布版本资产，不能继续当当前实施计划；后续按用户决定启动调研/实现并独立复验。

本地容器与本次私有daemon正常退出、Windows/WSL端口关闭；证据/原输入/state保留于artifacts/reviews/v2-approved-20261102。23份关闭评审/交接/prompt归achieve，11角色入口及记忆同步，不唤醒其他角色。[长期教训](../DELIVERY_LESSONS.md)和[固定规则](../../docs/operations/DELIVERY_ACCEPTANCE_RULES.md)必须先读，防止展示漂移、未停旧服务、记忆滞后、擅改计划、合成现场/多附件prompt再次发生。

早期交付/失败/修复/暂停均为历史，完整原文保留在[本线旧记忆快照](../../achieve/2026-11-02/v2-approved-delivery/snapshots/memory/tasks/delivery.md)，对应[归档索引](../../achieve/2026-11-02/v2-approved-delivery/README.md)。不把旧状态当最新授权，也不改写旧证据。

## 本轮协作偏离与校正（2026-11-03）
用户后端session在上下文压缩后误接回历史U008提交任务，实际推送d55df94b6e58117a698dbd14667b7836e67cd50f（3份历史复核文档，16行）；不是本轮用户新增U008指令，不能据该提交宣称HV2完成。总设计师核对提交树仅文档、未包含候选源码/包体，保留提交事实不重写历史，并已重新派发HV2-R1-USER实现/测试/交接、禁止分线commit/push。此前异常前端也曾误恢复UIR，已纠正并完成HV2准备。后续每次恢复先以本轮最新消息、执行板和派发prompt核对任务，不以历史最后一条用户消息替换当前统筹任务。

2026-11-03阶段进度：MA后端66回归+13工具及混合UUID独立边界通过，冻结9b48fb244963ce153b009a9a2d0d9050d084bd6c1bb43eec27ddf49f313fd9fa；已向监控前端实发MONITOR_FRONTEND_MA.md，仅MA开放编码。用户后端与公共层候选仍待复核；Token及异常前端准备完成。共享app两行v2装配由本session完成。原预热语义暂保持，真实补证与现场未通过。

2026-11-03进展：Token私有独立171项及510组旧实现计量比较通过并冻结；低命中第二关仍待交接，监控前端继续多模型/TTFT。未发布本轮产品源码/包。

2026-11-03进展：低命中第二关62项通过并冻结，异常前端正式prompt已实发。开始准备新空state真实HTTP/浏览器验证；当前只准备合成输入和脚本，尚未启动服务/打包。新版现场prompt准备稿补真实量级预算、三模型τ、独立方向、partial读取、MA缺数和单Markdown，不是已发布执行包。

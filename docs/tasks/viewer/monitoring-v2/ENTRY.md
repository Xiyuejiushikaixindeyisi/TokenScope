# Token监控V2前端维护入口

2026-11-03总设计师阶段同步：五项后端已独立验收冻结，两前端接入及HV2-AF-01/MF-02修复完成；根339项前端、88项最终浏览器通过（原失败与测试修正分别保留）。本线窗口关闭，统一版本与容器交付由V2总设计师继续；华为真实数据仍待验。[实际独立验收](../../delivery/HV2_INDEPENDENT_ACCEPTANCE_20261103.md)。下方旧阶段按历史阅读。

2026-11-03收口回执：总设计师已核对候选c4280716…的50文件，独立审读并运行6文件75项定点测试通过（2.02s），前后SHA一致；5份新HTTP输入已复制到其独立输入目录。**本线源码窗口已关闭**，等待统一冷启动浏览器/视觉及定向反馈，不再自行改源码/测试/生成身份。该回执不代表最终前端通过；异常前端冻结后的整合检查由总设计师执行。

2026-11-03最新 HV2-R2：MA及用户2.1.0目录/TTFT正式接入源码、本线自测完成，窗口交回总设计师独立复审。[监控总交接](HV2_MONITOR_FRONTEND_HANDOFF_20261103.md) · [MA正式交接](HV2_MA_FRONTEND_HANDOFF_20261103.md)。候选50文件组合c4280716635dc0b7e0dd472cf7c98a3f6ac80cacec9125dc02ac09fc09645404；32文件301单元/组件及typecheck/lint/build通过；完整输入已生成，7项新增浏览器未执行。实际session仍01a18c49-d9b4-7a33-8c04-e5a72adfcc24。保留批准四入口/配色/三栏及MA布局、L4/L5、UIR-01/02，UIR-03留V3；未监听、Docker、提交/push/部署打包，不代签页面/现场通过。异常SourceLink revision归异常前端补齐；CURRENT/SESSIONS/总执行板由总设计师维护。下方MA单项/PREP及历史RV2记录不再表示当前待办。

2026-11-03 MA接入开发中：总设计师提前检查发现的聚合OpenAPI引用命名失配已修正，[本项记录](HV2_MA_OPENAPI_FIX_20261103.md)。解析引用后保留全部结构断言，真实聚合spec通过及漂移负例覆盖；34项定点、260项全量与typecheck/lint/build通过。真实服务握手和浏览器E2E仍待总设计师唯一冷启动环境验证，不代表整体交接完成。下方PREP等待状态为此前阶段记录。

2026-11-03 HV2-R1-MONITOR-FE-PREP：已接受V2总设计师派发并完成[前端接入准备](HV2_FRONTEND_PREP_20261103.md)。实际session仍为01a18c49-d9b4-7a33-8c04-e5a72adfcc24（环境两ID一致）。已锁UI-02/UI-04及当前源码SHA，整理同APPID多模型目录、简化TTFT、MA独立/配对缺失说明的消费者要求和冷state复验清单。**等待对应后端独立验收/冻结及正式接入通知；未写产品/测试代码，未启动服务或构建。** 四入口和最后L4/L5保持，UIR-03留V3；CURRENT/SESSIONS/总执行板由总设计师维护。后续E2E先停旧、确认端口释放，再新state/新浏览器，不沿用历史另端口并行方式。

2026-11-02统一交付同步：V2已完成WSL打包、桌面全文件SHA核对，华为真实数据待验；用户认可V2可交付，UIR-03暂不修、留V3，不作V2阻断。本角色职责/休眠状态不变；当前发布与实际结果见[交付记录](../../delivery/V2_APPROVED_DELIVERY_20261102.md)。现场只用真实Trace3/MA18 CSV，先用户监控（搜索/P90 TTFT）和MA，第一次用户验收并指定appid后才两类异常；SSH18002，唯一Markdown嵌关键源码/证据。[当前prompt](../../../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md) · [固定规则](../../../operations/DELIVERY_ACCEPTANCE_RULES.md)。下方旧开发/交接状态按历史阅读，不覆盖本决定。

2026-11-02 UIR-01鼠标单项修复完成自测，候选viewer-uir01-pointer-fix-20261102-c1；[交接](../../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/viewer/monitoring-v2/UIR01_POINTER_FIX_HANDOFF_20261102.md)。仅用SVG实际screen CTM逆变换修正指针，布局/后端不变。226单元组件、85不同浏览器用例、144真实圆点检查通过；c2负向2项按预期失败；118地址重启一致，重启7项通过。原18项/UIR-02/排行/L4L5/T2–T4保持，窗口释放交审查会话独立复审，未提交/push/打包，不代用户认可。实际session 01a19111-344a-75c1-84e0-14db8be08f4f。

2026-11-02 UIR-01/02补充修复已完成自测，候选 viewer-approved-ui-review-fixes-20261102-c2；[补充交接](../../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/viewer/monitoring-v2/APPROVED_UI_REVIEW_FIX_HANDOFF_20261102.md)。恢复降序读数与不改路由的键盘跳转，另修最近运行覆盖排行路由；222单元组件、81不同浏览器用例、118地址重启通过，重启后13项复测通过。原18项/四入口/L4-L5/T2-T4及后端契约保持。前端窗口释放，交镜像打包与审查独立复审，未提交/合并/push/打包，不代签用户视觉认可。实际session仍01a19111-344a-75c1-84e0-14db8be08f4f。

2026-11-02 已批准 UI 恢复自测交接：[统一交接](../../../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/viewer/monitoring-v2/APPROVED_UI_RESTORATION_HANDOFF_20261102.md)。215单元/组件、71不同浏览器用例通过，111地址重启摘要一致；18项有逐项依据。唯一候选4191，未提交/push/打包，待审查方重新冷启动独立复审，不代签用户视觉验收。

更新：2026-10-31。正式用户/MA页面已获用户验收，RV2-01/02/03修复已通过独立源码及Docker复审，源码与文档检查点已推送main。见[当前审查状态](../../delivery/MONITORING_V2_STATUS.md)。本轮旧评审/修复交接已[归档](../../../../achieve/2026-10-31/monitoring-v2-review/README.md)，不是待执行任务。

暂不交付打包，等待异常分析前后端完成验收后统一交付。监控TTFT为“代码完成，性能校准待完成”；不将合成参数或截图当真实校准证据。

## 职责与范围

- 承接用户监控增强、搜索排行、P90长度请求所需参考前缀命中率，以及独立MA监控页面；两条后端并行，本前端分别消费其权威结果。
- 用户侧为GB的appid×common_name；MA侧为GF的model_standard_name×instance_uuid，选择规格后全部UUID直接可见，同UUID跨appid/P共享。两种范围、指标与缓存身份不能混用。
- 负责展示/交互、apps/viewer内增量实现、契约消费记录、前端测试和独立视觉验收。沿用UI-01及后续获批HTML的页面骨架、布局、配色与信息密度，不另建应用或数据层。
- 后端维护算法、采集/回放、计量、性能情景及契约；异常分析页面归另一前端会话。hybrid、自进化Agent、自动采集、部署和打包不在本线范围。

## 有效维护依据

- [正式交互方案](INTERACTION_V2.md)、[源码与复现地图](CODEMAP.md)、[实施计划](BATCH_PLAN.md)、[F006结果](batches/MV2-F006/RESULT.md)和[测试](batches/MV2-F006/TESTS.md)。批次结果是历史验证，修复后的最终身份以独立复审记录为准。
- [用户监控入口](../../monitoring/v2-user/ENTRY.md)、[用户2.1.0契约](../../../contracts/user-monitoring-v2/2.1.0/README.md)、[MA入口](../../monitoring/v2-ma/ENTRY.md)、[MA协议](../../../contracts/ma-monitoring-v2/CONTRACT.md)、[冻结S0](../../monitoring/batches/B005.1/S0_CONTRACT.md)。当前候选消费用户2.1.0（保留旧9操作兼容）、MA1.0.0及新增availability、S0；具体变化以HV2总交接为准。
- [UI-02](prototypes/tokenscope-v2-demo-ui02.html)、[视觉记录](PROTOTYPE_UI_02.md)、[校准清单](../../monitoring/v2-user/PERFORMANCE_CALIBRATION.md)。原型不代替正式代码/现场验证。
- [本线记忆](../../../../memory/tasks/viewer-monitoring-v2.md)、[会话登记](../../../../memory/SESSIONS.md)、[协作流程](../../../architecture/TASK_SESSION_WORKFLOW.md)。前端维护职责不因文档归档改变；异常分析前端由其独立入口承接。

历史本地验收地址/PID仅存档；需要重启时按项目[README](../../../../README.md)和源码地图核实当前版本，不假定旧服务仍有效。

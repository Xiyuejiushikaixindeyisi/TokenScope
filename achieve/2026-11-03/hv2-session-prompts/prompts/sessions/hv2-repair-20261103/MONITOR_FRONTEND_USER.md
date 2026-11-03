# HV2-R2-MONITOR-FE-USER：用户目录与TTFT正式接入

这是当前HV2任务的继续，追加到正在进行的MA接入。用户后端已由总设计师独立审查通过，现开放用户监控/搜索排行/TTFT接入；两块均属你的既有维护范围，按自己顺序整合。不能回到历史UIR/RV2/push任务。先核对 docs/tasks/delivery/HV2_USER_FREEZE_20261103.json 组合SHA 4d9e2e5d6c7031ff0aaa266114b92dbcb8684b9a80d722d2cfae9de8ad1d7dc0，读取 docs/tasks/monitoring/v2-user/HV2_USER_BACKEND_HANDOFF_20261103.md 及 docs/contracts/user-monitoring-v2/2.1.0/{README.md,schema.json,runtime.openapi.json,examples.json}。独立62项与额外6个大P90精确算术边界通过；旧2.0.0原件不改。

继续保留MONITOR_FRONTEND_MA.md的全部限制和MA冻结，不重设计。新增窗口为features/v2/UserMonitor.tsx、Ranking.tsx、TTFT.tsx及关联本线模块/测试、api/v2/client.ts用户部分、generated/user及其专有生成脚本/Schema。app.tsx/V2App.tsx/全局样式/共享S0与异常模块如确需补丁先在交接列精确位置由我安排。允许npm静态/unit/build，不监听服务/浏览器E2E、不commit/push/Docker/打包，不改共享记忆，不发跨会话消息。

1. GET /monitoring/user-v2/runs完整快照分页实现冷浏览器自动发现同APPID所有模型；无需localStorage或手填run、不POST绑定发现。保持UI-02原模型/范围选择控件位置与搜索排行布局。is_default按登记序最新发布，固定历史run/index_revision明确保持；新发布、重启、刷新、切模型不能静默换固定历史或混多模型汇总。409快照冲突清掉分页重新读，延迟旧响应不能覆盖新范围。空/失败/未知appid和历史不可读明确区分。
2. 目录source给Trace模型规格与来源。与异常共数据映射 source_kind=user_v2,user_run_id,appid,expected_index_revision,window=null；base_run只溯源，不同时作为互斥参数提交。文件观察范围不是appid裁剪窗口，不能做隐式时间过滤。原搜索分页/字面匹配/20条/300ms/排序/导出取消及校验保留。
3. TTFT日常只填等待W及SLO T；模型默认从GET /ttft/defaults读取，Qwen1、GLM2.7、DeepSeek2.6秒/K8192由后端提供，前端不写死。K为可选覆盖，可恢复默认；来源/revision/适用K信息可查看，用户提供默认值不标已校准。保留原三栏展示。W是首Token前全部非计算耗时，不重复扣O。缺W不得默认0，显式0有效；缺τ明确不可算。
4. 显式POST /ttft/evaluations最少带submission_key、所选user_run/appid/index_revision、waiting_seconds、target_seconds；新接口不用手填scenario。默认le，旧lt与旧W+O情景/历史只读仍可查看。响应从evaluation权威字段展示，保持精确Fraction/null/0/100%/无预算/无P90及limitations。K不隐式缩放τ。自动历史GET /ttft/evaluations/{id}不要发旧/evaluations。请求重试同键、参数改变新键；参数revision和数据身份绑定，切模型或配置后旧回包不能串结果。
5. 升级握手验证2.1.0与14操作，保留旧9操作兼容检查，不能删除版本/Schema断言换通过。新增DTO完整生成与运行严格校验。对同模型多历史、冷state、目录分页快照/身份冲突、全部默认值、K覆盖/恢复、精确边界、unknown模型、历史/延迟响应和真实源链接编写必要测试。

你可先完MA再做用户或整合后一起交接，最终新增 HV2_MONITOR_FRONTEND_HANDOFF_20261103.md，完整源码SHA/文件清单、实际静态/unit/build结果、浏览器待验用例与fixture，不把构建通过当页面通过。我将停旧并统一冷state/新浏览器E2E和视觉复核。四入口与L4/L5保持，UIR-03留V3。

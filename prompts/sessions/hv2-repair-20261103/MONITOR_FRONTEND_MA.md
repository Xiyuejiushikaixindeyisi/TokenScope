# HV2-R2-MONITOR-FE-MA：仅开放已冻结MA接入

当前真实任务是HV2修复，依据本消息和 docs/tasks/delivery/HV2_REPAIR_EXECUTION_20261103.md 恢复，不能回到历史UIR/RV2/push任务。你的PREP已完成；现在正式开放MA前端源码与测试。用户目录/TTFT后端尚未验收冻结，暂不开发那一部分，后续由我补发。

先读本线PREP、docs/tasks/monitoring/v2-ma/HV2_MA_BACKEND_HANDOFF_20261103.md、hv2-availability/{schema.json,examples.json,candidate.openapi.json}和 docs/tasks/delivery/HV2_MA_FREEZE_20261103.json。总设计师独立运行66项MA回归、13项工具测试、额外混合UUID隔离/0/null/守恒边界通过；冻结组合9b48fb244963ce153b009a9a2d0d9050d084bd6c1bb43eec27ddf49f313fd9fa。先核对冻结SHA再编码，不能据开发自测代签最终E2E。旧快照1.0.0保持；新增GET /monitoring/ma/runs/{ma_run_id}/instances/{instance_uuid}/availability。

获分配唯一窗口：apps/viewer/src/features/v2中的MA页面/图表，本线MA测试，api/v2/client.ts的MA部分、generated/ma及其对应生成脚本/Schema。不改用户/TTFT逻辑、异常页面、app.tsx/V2App.tsx/全局样式/共享S0组件/锁/构建依赖。如需共享壳补丁在交接列精确位置交我处理。允许npm typecheck/lint/unit/build（非Docker），不自行启动监听服务或浏览器E2E；提交浏览器测试与所需fixture/命令由我协调唯一冷启动环境。不commit/push/打包，不改CURRENT/SESSIONS/执行板，不发跨会话消息或创建agent。

保持批准四入口HTML UI-02及原表格/画像/12桶布局、UIR-01/02，UIR-03留V3。现有全UUID、最多4并发、逐行失败重试、固定run/制品/窗口、服务身份与过期响应隔离保持。

实现要求：
1. 在原paired单元格及现有独立指标详情中显示相应解释：paired缺失不得用independent填入；明确展示仍有效的独立ideal或real，四主指标分别判空，不能单一失败遮蔽其他指标。DS式R/Q=0时real保持null解释源cached缺失、independent ideal可见；GLM冲突E/Q=0时ideal原因明确、independent real与小时已知重算值保留。
2. 只消费冻结指标/分母/状态/原因，不在前端重算大整数百分比或小时量。available/partial/unavailable/empty分别表示，partial是已知样本子集，不外推全量。A=0桶0、有请求R=0桶null、有效cached=0是真0%；小时3600秒/桶300秒不变。
3. 解释响应必须核对service/run/binding/UUID/model，与原Snapshot绑定；源字段问题只归本UUID，warmup encoded_now_count与E覆盖不同。真正重叠维持原预热策略，不截尾/混排/把partial改ready。
4. 历史409 AVAILABILITY_NOT_RECORDED仅表示历史无细化资源，继续展示原快照值并提示，绝不GET补写或自动POST重算。其他失败明确可重试；切制品/run/UUID取消旧请求，不跨实例缓存。
5. 扩展Schema握手与生成器保留旧契约验证，新字段严格校验；不能删除断言换通过。编写现实HTTP与边界用例（旧结果、缺cached、冲突、部分观测、0/null、独立/paired、wrong identity、延迟响应、全UUID并发/重试），保持原数值/精度/取消断言。

交付 docs/tasks/viewer/monitoring-v2/HV2_MA_FRONTEND_HANDOFF_20261103.md：实际修改/源码SHA，检查命令与结果，未执行浏览器事项、fixture及命令，原HTML对照说明与限制；更新自己ENTRY/记忆。本机合成不冒称现场。实现后等待我复核；用户/TTFT以另一次冻结通知开放。

# HV2 MA 前端接入交接 · 2026-11-03

**MA源码及本线静态、单元/组件自测完成，待总设计师独立冷启动浏览器E2E和视觉复核。** 本文与[监控总交接](HV2_MONITOR_FRONTEND_HANDOFF_20261103.md)一起接收，不代表现场或最终联合通过。

维护会话 `01a18c49-d9b4-7a33-8c04-e5a72adfcc24`，环境CODEX_SESSION_ID与CODEX_THREAD_ID一致。基线HEAD `d55df94b6e58117a698dbd14667b7836e67cd50f`；全部前端改动未提交。MA后端冻结组合 `9b48fb244963ce153b009a9a2d0d9050d084bd6c1bb43eec27ddf49f313fd9fa` 的17个文件已逐项核验，交接前再核验一致。旧MA1.0.0和S0不变，新增availability资源schema_version为1.0.0。

## 实现及范围

- `src/features/v2/MAMonitor.tsx`：全UUID原表格读取Snapshot后，在同一最多4并发RequestPool中读取availability。立即保留已有快照，不因说明失败遮蔽指标；错误只重试本行说明。paired格仍显示paired，附独立ideal/real，绝不以独立值替代配对值。小时已知重算量直接使用原Snapshot.hour.uncached_tokens，保留null和0。
- `src/features/v2/MAAvailability.tsx`：严格检查service、run、全部binding、UUID、model及coverage身份；分别展示available/partial/unavailable/empty、样本/总体、分母及原因。partial明确仅已知子集、不外推。仅409 AVAILABILITY_NOT_RECORDED视作历史缺说明，其余为可重试错误。历史缺说明不触发补写或POST。
- `src/features/v2/MACharts.tsx`：原画像和12桶布局保留，在现有独立指标详情/桶数值中补状态。展示本UUID源字段问题、预热时间与先后规则，分开encoded_now_count和覆盖E。不改变预热排序、窗口、数值、百分比算法。
- `src/api/v2/client.ts`、`openapi-equivalence.ts`及generated/ma新增3文件：新DTO完整运行校验；读取availability前握手实时聚合OpenAPI。修正独立router与create_app组件命名差异，通过ref结构解析保留字段、约束、参数、路由及错误响应断言，拒绝循环/缺失/外部/sibling引用并限制展开资源；[握手补充记录](HV2_MA_OPENAPI_FIX_20261103.md)。不需要另外固化命名相关运行时签名。
- `scripts/generate-ma-availability.mjs`：核验冻结身份与所有文件SHA后，仅生成新增DTO与握手投影；旧生成结果不覆盖。用户2.1.0接入也已完成，实际客户端是两部分整合候选，不应只复制MA旧阶段client.ts。

共享请求池/任务跟踪器原取消逻辑保留；服务变化、切运行或卸载取消旧在途与排队任务，迟到结果不写新范围。未修改全局样式、V2App、其他共享壳、后端/契约或锁文件。

## 实际自测与证明层级

MA定点：`npm test -- --run tests/unit/ma-availability.test.ts tests/component/ma-availability.test.tsx`，**25单元+9组件=34项通过**。覆盖9冻结样例的严格Schema及错误关联，DS源cached缺失保留独立ideal，GLM预热冲突保留独立real/已知小时量，partial/empty/有效0/分母0，历史409/503/单行重试，13UUID最多4并发、取消队列/迟到响应，真实聚合spec及有意字段/约束/响应/路径漂移。

单元/组件使用真实客户端与运行校验、受控fetch响应；9样例来自后端冻结合成fixture，Snapshot测试投影补用了旧示例的直方图，这不是同一真实数据集统计一致性证明。聚合OpenAPI fixture摘自审查方create_app产物，源SHA内嵌provenance；不是浏览器已与运行服务握手的证据。

最终整合检查：typecheck/lint/build均exit0，npm test **32文件301项通过**，含MA和用户及既有回归；集合重叠，不与34相加。日志和环境见总交接。MA早期定点日志 `artifacts/validation/viewer/HV2-MA-FE-20261103/targeted.log` 为27项阶段结果；加入聚合握手回归后34项结果由aggregate-handshake及最终全量记录证明，不混用阶段数量。

## 待执行真实HTTP浏览器验证

`tests/browser/hv2-ma-availability.spec.ts` 共4项已编写、类型检查通过，**未运行**：

1. 实际HTTP13UUID：逐实例Snapshot/availability与DOM独立/配对、小时值、12桶状态对照并截图。
2. 真实Snapshot配合故障注入历史409、503、错误UUID；失败行重试，原值保持，无自动POST。
3. 延迟真实响应，验证同池4并发、切运行取消排队、放行旧响应不恢复。
4. availability真实失效实例头409清全局旧范围，无自动POST。

输入生成器 `apps/viewer/scripts/prepare-ma-availability-fixtures.py` 读取冻结9例，再添加4个独立UUID构成13UUID矩阵；文件用exclusive-create，不覆盖既有证据。已生成并校验存在：

- `/home/zhangxiyue/TokenScope/artifacts/validation/viewer/HV2-MONITOR-FE-20261103/inputs/hv2-ma-matrix-pre.csv`
- `/home/zhangxiyue/TokenScope/artifacts/validation/viewer/HV2-MONITOR-FE-20261103/inputs/hv2-ma-matrix-now.csv`

固定合成窗口pre 2026-10-20 07:00–08:00 UTC、now 08:00–09:00 UTC，模型Qwen3.6-27B；不冒充华为真实Trace/MA。真实编码器与冻结fixture使用的4096-token替身不同，所以浏览器比较实际权威响应，不照抄示例ideal比例。

## 候选与边界

本次整合50个前端文件的逐文件SHA与完整清单：`artifacts/validation/viewer/HV2-MONITOR-FE-20261103/candidate.json`；组合 `c4280716635dc0b7e0dd472cf7c98a3f6ac80cacec9125dc02ac09fc09645404`。本线补充文件、fixture、生成器均须接收，不能只应用frontend.patch。

UI-02、UI-04原HTML摘要及包/锁/V2App不变核验见candidate.json。布局结构/配色及12桶保留，新增说明会增加原单元格内容高度，真实桌面/移动端视觉尚待独立验证；四入口、L4/L5及UIR-01/02未改，UIR-03留V3。

本线未监听端口、创建验收state、启动浏览器、运行Docker或打包部署，未停止其他服务，未commit/push，也未发跨会话消息。总设计师按当前规则先停旧、确认释放，再新state/浏览器唯一冷启动；具体命令和全套输入见监控总交接。尚未证明真实缺cached数据能恢复真实率、真实预热冲突可改变策略、现场性能/数据质量已校准。

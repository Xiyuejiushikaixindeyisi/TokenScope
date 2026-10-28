# 前端统一验收与设计符合性 v1.0

状态：前端验收、后端主持的联合及后续F007/打包前审查已完成；本文保留维护验收门槛，实际发布与现场状态见[B006结果](../monitoring/batches/B006/RESULT_20261028.md)。主设计见[最终稿](MONITORING_INTERACTION_V1.md)。F006逐行补充实现入口、测试命令/结果、源码/契约/数据/环境摘要、ISSUE及回退证据；不可仅靠截图或文档检查关闭。最终联合测试由后端会话统一执行。

| ID | 设计要求/通过标准 | 前端batch | 后端/联合映射 |
| --- | --- | --- | --- |
| V01 | 精确整数与null，无JS舍入；UTC原串保留/北京时间显示 | F001/F003 | A08/A14/J01 |
| V02 | 目录及cursor一致性、分页revision冲突恢复；latest只读权威指针 | F002 | A01/A02/J01 |
| V03 | 发布/重连/reset/实例变化/迟到响应；当前图和明细不跨run | F002/F003 | A03–A06/J02/J03 |
| V04 | 三宽度1029桶、众数/精确分位数/尾部、无前端重算 | F003 | A07/J01/J04 |
| V05 | 页面切换与聚焦不重复GET同版指标；内存/IndexedDB配额降级与历史时间 | F002/F003 | J03/J06 |
| V06 | 请求多列/区间/稳定排序/重复hash；正文与轻证据按能力展示 | F003 | A09/A10/J04 |
| V07 | 参数/阈值整数适配、CAS草稿保留、仅下一运行生效 | F004 | A14/J05 |
| V08 | 回执幂等、丢响应/未知key；R1一次性对齐及终态单向合并 | F004 | A04/A05/A12/J05+R1 |
| V09 | NDJSON原字节SHA/结束summary/身份/计数；CSV解析记录/引号跨chunk | F005 | A13/J04+R2 |
| V10 | 256MiB导出流与有界队列/浏览器内存；中断abort，16MiB备用限额 | F005 | A13/A18/J04/J06+R2 |
| V11 | 错误、无数据、无效组不混淆；业务数据文本不执行；390px与键盘 | F003/F006 | J01/J06 |
| V12 | 原监控视觉与行为迁移；三模型范围无合成fallback，诊断入口不假联调 | F003/F006 | J01–J06 |
| V13 | 所有静态/单元/组件/浏览器检查，构建可复现，无外网运行依赖 | F001/F006 | A17/J06 |
| V14 | 冷/热≥30次p50/p95与目标：缓存100ms、首组1s、50条500ms | F006 | A18/J06 |
| V15 | 回退、版本、锁文件/manifest/已知问题齐全，交后端统一联合测试 | F006 | J06/B006前置 |

R1必需附加时序：首次catalog前失败/完成；after跨过终态；日志过期reset；状态GET与终态事件乱序；服务实例变更。只做重放测试不足以替代。

R2必需附加浏览器证据：文件句柄选择/close/abort、真实写出、峰值内存与管理队列、断网/截断/错SHA/缺summary/CSV嵌入换行/UTF8跨块、慢sink/磁盘错误、超单记录上限、16MiB备用边界。FileSystemAccess能力测试需实际目标浏览器人工步骤或受控自动化文件句柄；仅mock sink不代表真实文件写入验证。

## 测量和通过层级

- 假服务提供边界/故障与确定性值，只能验证前端行为，标frontend-only。
- 真实后端开发联调绑定后端版本；仍不替代后端主持的最终联合报告。
- 应用缓冲上界使用实际计数器断言；浏览器内存采用可复核的浏览器/进程测量，记录基线、峰值、分配及回收，JS堆/整体RSS不能混称。优化目标增量64MiB、验收上限256MiB（用户2026-10-27修订）；两规模各3次测量及增长检查，未达目标记录问题，不能以GC理论推断通过。
- 前端各批closed且F006 ready_for_joint时可交接；只有后端真实联合门槛和后续用户打包授权完成，才能进入统一交付。
- 未执行/阻断/失败/通过分列；发现与批准设计不符先修复或取得用户决定，不在RESULT静默缩小范围。

## 实际设计符合性（2026-10-27）

| ID | 前端结果与证据 | 联合状态 |
| --- | --- | --- |
| V01 | 通过：domain/contract/monitoring tests；详见F006 TESTS | 后端统一J验收pending |
| V02 | 通过：publication tests、S0 generator；详见F006 TESTS | 后端统一J验收pending |
| V03 | 通过：coordinator/publication、full-journey；详见F006 TESTS | 后端统一J验收pending |
| V04 | 通过：monitoring组件与browser；详见F006 TESTS | 后端统一J验收pending |
| V05 | 通过：cache四场景、monitoring网络计数；详见F006 TESTS | 后端统一J验收pending |
| V06 | 通过：monitoring、真实integration；详见F006 TESTS | 后端统一J验收pending |
| V07 | 通过：operations含规则CAS新增场景；详见F006 TESTS | 后端统一J验收pending |
| V08 | 通过：receipts、operations、真实SSE；详见F006 TESTS | 后端统一J验收pending |
| V09 | 通过：export单元、export-fixture、真实NDJSON下载；详见F006 TESTS | 后端统一J验收pending |
| V10 | 通过：F005 acceptance-memory六次压力、精确备用边界；详见F006 TESTS | 后端统一J验收pending |
| V11 | 通过：shell/monitoring/full-journey，桌面和390px；详见F006 TESTS | 后端统一J验收pending |
| V12 | 通过：正式UI无合成fallback，真实三模型15组；详见F006 TESTS | 后端统一J验收pending |
| V13 | 通过：142 tests、20 browser场景、类型/lint/build、资源检查；详见F006 TESTS | 后端统一J验收pending |
| V14 | 通过：F006 final-browser/timings.json假真各30；详见F006 TESTS | 后端统一J验收pending |
| V15 | 通过：source-manifest、rollback.json、联合交接；详见F006 TESTS | 后端统一J验收pending |

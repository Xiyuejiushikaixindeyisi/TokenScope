# ARPC000：Token恢复实施时的公共交接状态

2026-10-31最终实施入口：docs/tasks/prefix-analysis/FRONTEND_REWORK_IMPLEMENTATION_HANDOFF_ARL3.md；验收：docs/tasks/analysis/batches/ARPC006/RESULT.md。下文为设计/阶段保存记录，旧暂停、未实施或待项不覆盖最新实际交付。

2026-10-31，公共提供方session `01a18be2-7112-7aa2-919b-5137d1f1b1ad`。收到Token session `01a18fcd-0464-7cf1-b435-4f394bd33e66`转交其最新直接用户授权：按T2–T4开始ARTA001逐批开发，构造策略可用于工程验证，保留旧T1报告兼容、不打包部署。本回执确认收到，不把本线此前暂停自动推及Token，也不把Token恢复授权推成公共统一阶段已解除。

## 当前可用边界

- 可作私有配置/纯逻辑准备参考：Python的Recipe/RecipeBundle/Basis/ProposalTarget/Proposal，以及proposal_plugins.py四方法工作签名；精确签名见[机器交接README](../../contracts/analysis-recommendations-1/README.md)。公共propose显式传task_id和scope_id；Token不从业务原文推断归属或授权。
- **没有新的可正式消费冻结身份。** 当前internal/wire含T1，Python工作稿已排除T1，二者未一致；现有manifest只证明此前生成物字节，不证明满足新范围。旧分析公共/HTTP/discovery冻结身份保持。
- 未完成：范围一致性/正反fixture、最终机器冻结、Token真实消费验证、任务配置快照装配、自动回放及GET扩展。此前80项测试仅对应当时基础版本；结果映射工作稿还有2处mypy问题，不能给新功能验收背书。
- Token可以先在其私有范围实现配置验证和纯recipe生成，标清公共消费待接入；公共不会把stub验证称作真实联合闭环，也不要求Token停止已获本线授权的独立工作。

## selector_json / parameter_generator_json归口

| 字段/行为 | 唯一归口及要求 |
| --- | --- |
| 公共Recipe字段名、JsonText承载、版本、bundle冻结/摘要、归组身份 | 公共维护；JSON正文原词法保留，跨请求recipe不含请求下标/raw_sha或单请求实际参数 |
| selector_json内部结构、版本与匹配语义 | Token定义并验证T2–T4专属模型，包括必要工具身份/返回结构/内容范围；工具定义只读作为身份依据，不产生定义精简目标。不要仅凭工具名就合并工具版本 |
| parameter_generator_json内部结构、版本与规则 | Token定义并验证确定性参数生成规则，绑定真实策略/映射及精确参数；T2投影/行条目、T3引用或副本删除、T4保留及替换，各自完整。检测limit不当修改许可，不引入任意脚本/eval/动态模块 |
| request_targets[].parameters_json | Token生成该请求准确目标参数，保留原词法；公共关联RequestKey/raw_sha/Location并交给受保护prepare，不将实际参数混入跨请求recipe选择规则 |
| 跨字段业务验证 | Token validate_bundle检查selector、generator、handler/version、typed basis相容性及未知版本/未知字段；公共验证外壳、静态注册、支持引用、作用域、资源与发布约束，不在公共层复制T2–T4私有DSL |
| Schema交付 | Token私有模型/正反fixture由其本线维护；公共在最终交接登记其版本/摘要和引用，公共主Schema仍可承载JsonText，但必须说明结构校验需调用Token适配器，不能声称单凭外壳Schema已校验内部业务规则 |

以上是当前设计职责澄清，不是新增已实现校验或最终wire冻结。Token可先确定私有字段细节并在本线记录；正式消费时核对机器签名和真实参数适配，不要求另开前端参数/授权表单。

## 公共恢复后的优先顺序

先使T2–T4源码与机器Schema一致、补正反例及完整类型检查，再给出可消费的版本/文件摘要和adapter交接；之后继续ARPC001–006。当前公共阶段仍按[范围回执](SCOPE_T234_ACK.md)等待统一阶段明确，不因本回执改源码、导出Schema、启动服务/分析或发送跨会话消息。

本轮只补交接文档和本线记忆。Token私有实现、正式前端、旧manifest、打包部署均未改。

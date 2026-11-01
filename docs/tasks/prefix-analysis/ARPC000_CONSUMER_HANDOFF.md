# ARPC000 T2–T4 可消费阶段交接

最终交付补记：ARPC000–006与Token实际消费已验证闭环，见[AR-L3实际入口](FRONTEND_REWORK_IMPLEMENTATION_HANDOFF_ARL3.md)。本页下列摘要保留首批交接历史；当前最终机器摘要以contracts/analysis-recommendations-1/manifest.json及AR-L3 IDENTITY为准。后续仅增加summary.stop_location和独立公开视图，Token四方法/输入DSL归口不变。

2026-10-31。公共session 01a18be2-7112-7aa2-919b-5137d1f1b1ad已获直接用户恢复授权；此前公共暂停已解除。**下列模型及适配器签名可供Token消费者实现与验证**，不代表新HTTP/自动回放已完成，也不代签消费者验收。

- 版本：analysis-recommendations-1 / token-auto-proposals-1；Token仅T2–T4，编号不变，旧T1协议/历史报告不改。
- 源码：analysis_common/recommendations.py、proposal_plugins.py；四方法签名以源码Protocol为准，propose包含task_id、scope_id、request、fragment_id、fragment、bundle_snapshot、capabilities、control。
- `selector_json`、`parameter_generator_json`内部版本模型及语义由Token维护并由validate_bundle严格校验；公共维护JsonText外壳、快照、身份、资源与编排。字段内不执行动态代码，真实目标参数放request_targets；完整归口见[前序澄清](ARPC000_TOKEN_RESUME_HANDOFF.md)。
- [机器Schema与正反例](../../contracts/analysis-recommendations-1/README.md)：4正例/5反例；示例DSL是明确构造的传输样本，不是业务策略，也不强制Token私有DSL采用其字段。

| 文件 | SHA256 |
| --- | --- |
| internal.json | 3f27ebfa3bba09da35b086a18b20ee2f7c9a9ebd9f8675473843fc529d28153f |
| wire.json | e618784f4a6f846aeb28663dc145d85dee1ffc6a8a58badacf218c95ce29810f |
| examples.json | 7a5b5b44fa7c0d556d9f9dc19a0ec4d6ebacf9bea17661e3f40f1d118a6873d1 |

本次修复projection的RequestKey/str变量复用；公共及低命中新模块mypy通过，相关ruff通过；公共/低命中单测81 passed / 0.71s，含当前Schema与源码逐模型相等、manifest核对和所有正反例验证。T1主规则/类别及description替换handler不能进入新提案。完整result/HTTP与资源边界留后续ARPC，不以本次单元验证当真实回放。

Token只改其私有模块/测试，公共调用适配器前后校验引用及准备结果。请在本线记录消费的源码/Schema身份与结果；若需要修改公共签名/外壳，记录精确差异供公共处理，不修改公共文件。当前公共继续ARPC001–006，无需每批再批，不改正式前端/打包部署。

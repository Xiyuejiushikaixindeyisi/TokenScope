# analysis-recommendations-1 / ARPC000–006

当前有效：公共已恢复实施，T2–T4源码与机器Schema一致，适配器可供Token消费且其本线已完成真实消费回归。新GET已接入应用；公共最终联合及监控兼容已通过，见[ARPC006](../../tasks/analysis/batches/ARPC006/RESULT.md)。

公共推荐扩展机器模型，独立于analysis-common-1.0和diagnostics-http-1。`internal.json`与`wire.json`由`scripts/export_recommendations_schema.py`生成，字节身份见manifest.json。内部整数严格验证，wire整数十进制字符串，业务parameters_json保持词法。Pydantic跨字段/引用约束是Schema之外的必需验证，不仅依赖JSON Schema结构检查。

维护方：公共后端session 01a18be2-7112-7aa2-919b-5137d1f1b1ad。机器模型及新GET已实现，Token真实消费者回归由其本线记录；公共整体最终验收单独记录。

## Token实施入口

- Python模型：`tokenscope.analysis_common.recommendations`的RecipeBundle、Recipe、Basis、SupportRef、ProposalTarget、Proposal。
- 协议：`tokenscope.analysis_common.proposal_plugins.ProposalAdapter`。静态注册ProposalRegistry，不新增H0方法、不新增Token worker或router。
- `describe() -> ProposalDescriptor`，`validate_bundle(bundle) -> RecipeBundle`。
- `propose(task_id, scope_id, request, fragment_id, fragment, bundle_snapshot, capabilities, control) -> tuple[Proposal,...]`。相对设计摘要补task_id，由公共调用端提供，禁止拿父任务ID或从业务原文解析。全方法不编码、不回放、不写库。
- `prepare_proposal(request, proposal, basis_snapshot) -> MutationPreparation`：先验证typed basis，再复用私有handler/guard；未知依据、版本、协议不降级为无匹配。一次Proposal绑定一个请求，跨请求归组由公共层执行。
- `validate_support`由公共调用；核对fragment中的真实Observation、Unit、Location、Finding关系。T3 Finding可空，Observation不可空。
- basis来源记录authority.source_kind/source_ref/source_digest/status；无依据basis=null、业务缺项reason，不能用任意字符串作授权。
- 首批T2/T4无依据hypothesis禁用；T3必须explicit_authorization。缺业务策略与配置/实现缺失按reason注册区分。

推荐使用结构化recipe嵌套title/change_summary/basis等，避免对象顶层重复内容分叉；Recommendation内evaluation保存原完整EvaluationResult，精确变化值在读取呈现层派生。前端接入以[AR-L3实际交接](../../tasks/prefix-analysis/FRONTEND_REWORK_IMPLEMENTATION_HANDOFF_ARL3.md)为准。当前Schema以arpc-local-1身份冻结；后续字段修订必须重新生成并记录摘要，不静默改旧冻结契约。

存储通过recommendation_store.write_extension复用同ResultWriter，kind独立，不扩旧HTTP ItemKind。仅静态注册存在才在capabilities声明adapter；默认registry为空不是“所有场景无问题”。测试入口：tests/unit/analysis_common/test_recommendations.py，包含wire、错误版本、部分计数、跨task目标、真实fragment关系及legacy存储。

公共计划与状态：[ARPC000–006](../../tasks/analysis/RECOMMENDATION_IMPLEMENTATION_PLAN_AR1.md)。Token消费者请在本线记录实际消费验收；公共不代签其运行时。

## 当前导出身份补充

manifest.json为当前internal/wire/examples字节身份；早期ARPC000交接表为当时快照，输出Summary后续增加可空stop_location以报告预算停止位置，适配器输入和四方法签名未改变。public-views.json及http-manifest.json为业务GET视图身份：recipe中selector_json/parameter_generator_json、basis.scope_selector替换为对应_digest；新增metrics字段提供全scope精确变化，不泄露私有策略正文。旧history/arpc000-pre-t234仅追溯。

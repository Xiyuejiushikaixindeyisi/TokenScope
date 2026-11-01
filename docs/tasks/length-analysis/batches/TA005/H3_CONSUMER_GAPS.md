# H3消费差异与具体公共接口需求

> 关闭更新：G1/G2/G3均已实现并通过真实消费。G1 /requests/{fragment_id}及完整capture/scope；G2已接入authorizations.authorize_candidate，两种业务授权worker复核/封存；G3同scope Plan组合独立评估及冲突拒绝。见TA005/RESULT、test_authorization_http与公共test_diagnostic_combinations。本文保留原始需求溯源，不再作为待办清单。

2026-10-31，消费方Token。公共源码只读，未修改或代签公共完成。

## 已接收与验证

H3a DiagnosticService/RuntimeOptions、submit_token_evaluation已实际消费；2项GLM真实服务测试通过，8.58s：保存fragment→待参数candidate→显式评估，零/负输入收益保留，缺业务依据不产生after，低命中后Token读取原始raw摘要，T2/T4共享单位，GET无计算。service/presentation.evaluation_view在冻结EvaluationResult之外追加gate_passed/display_eligible/gain_percentage_points/compute_tokens_delta；消费时先明确核对派生字段，再按原Schema恢复核心字段，不忽略任意额外字段。

H3b已读api/diagnostics.py与提供方样例。当前Token HTTP消费测试覆盖既有分析/候选评估/实例隔离/只读；完整证据与以下缺口仍待补齐，不能关闭TA005。

## G1：Token完整原文读取

现有GET comparisons只服务PrefixFinding；Token fragment仅保存Location/ContentUnit/Observation，不包含原始完整JSON。需要只读公共入口，例如`GET /diagnostics/tasks/{task_id}/fragments/{fragment_id}/body`（路径由公共方定）。

输入使用已封存报告成员fragment_id，不接受任意base_run_id/record_index。服务从该fragment的RequestKey+raw_sha256与原scope核验后读取完整raw_body，返回RequestKey、scope_id、raw_sha256、raw_body、raw_body_complete、capture_truncation；内层位置仍用原fragment，不在GET运行探测/编码/回放。外报告成员、错实例、源身份变化明确拒绝。支持>64KiB及同请求T3多位置，不伪造第二请求。验收D2-06/C10/C11。

## G2：显式T3业务授权候选

当前submit_token_evaluation只接受原报告已存candidate。按已批设计，无引用协议/授权的T3只输出事实；因此reference/普通消息删除handler虽已真实编码通过，尚无完整服务入口。不能为绕过这一点默认生成可删除候选。

建议新增显式授权提交（不改已有H0模型）：必填parent_task_id、fragment_id、observation_id、selected_unit_id、handler_id/version、parameters_json、business_basis_ref、submission_key。只允许已存T3 exact_payload_repetition观察中的单元；服务验证观察/单元/位置均属于同fragment及scope，并从已存证据派生候选，不接受客户端任意RequestKey、raw_sha256或JSON Pointer。handler仅注册的replace_payload_with_reference/remove_authorized_duplicate_message，用户完整参数和业务依据到齐后才排队编译/评估。

引用替换选择内嵌arguments的完整载荷字段；当前handler保守支持顶层字段→真实string引用，验证当前工具定义摘要与Schema条件。普通消息删除选择原普通message_payload，可信服务/本线候选构造器将content位置映射到包含消息；prepare再次检查完整相等的工具载荷、显式authorized=true与无调用结构。任何前提失败blocked，无部分after。授权记录/最终candidate/Plan均封存，报告原事实不改写。

公共维护方可选择独立authorization任务或显式方案提交；若需要新增本线候选构造方法，应列出精确签名/版本，不能偷偷改冻结AnalysisPlugin协议。本线可实现候选构造器，但不直接新增公共HTTP/worker源码。

## G3：组合评估与跨方向冲突

已提供API有低命中单/组合与单个Token候选评估；尚未看到显式多Token/跨方向组合入口。TA004已验证公共原子操作冲突，但TA005的D2-08/E07需要真实保存Plan组合→原scope独立全窗口评估，不能加总收益。建议按已保存且相同scope的plan_id集合显式提交，公共重新校验所有guards/操作冲突；包含Token的组合方向combined，不套低命中门槛。任一失败无after，单项结果保持。

这些是已批产品/验收缺口，不是扩大Token检测范围。缺口关闭前TA005不关闭、TA006不代签联合完成。参数错配独立，未打包部署。

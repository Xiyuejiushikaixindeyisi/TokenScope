# Token内容插件实际接口

2026-10-31，TA000–TA006本地实现/验证闭环，最终112项通过。本页记录实际调用面；公共协议仍由主会话维护。现场、前端视觉、打包部署未执行。

入口：`tokenscope.token_content.plugin.TokenContentPlugin`，实现公共`AnalysisPlugin`四方法；由公共静态`PluginRegistry.register(TokenContentPlugin())`注册，不接受用户模块路径。describe：contract=analysis-common-1.0，plugin=token-content-1，parser=json-exact-1，measurement=content-measures-1，rules=T1/T2/T3/T4@1，policy=token-policy-1，七个handler@1。源/状态/Schema按公共冻结契约。

`analyze_request(RequestView, PluginSelection, EvidenceCapabilities, RunControl)`只返回fragment，不写库、不读取其它请求、不执行工具或编码。原始完整JSON是输入；能力缺失、局部解析错误、资源停止有原因与覆盖。事实包含度量、模板参与unknown/ignored/included、工具定义身份、原/内层位置、T4后续消息数、T3同请求非重叠重复关系。缺精确归属不填Token贡献。

策略载荷是JSON数组，准确字段以`policies.PolicySpec`为准，未知字段拒绝。必填policy_id/revision/source/rule_id/kind；limit明确unit/limit/operator；field_allowlist明确allowed_fields/field_level(object或array_items)；retain_last明确keep_last/retention_unit(result_container或text_part)。按工具策略必须提供tool_identity，按路径可提供source_pointer/embedded_pointer/representation。basis=model_input在参与未知时不作超限结论；不存在隐含业务阈值。

## 修改参数

所有handler要求明确business_basis_ref；prepare_mutation只编译操作，不自动评估。parameters_json是下面参数对象的JSON文本，replacement_json本身也是准确JSON值文本（替换字符串需保留引号）。缺参数/不支持目标/任何guard失败整个准备结果blocked、无operations。

| handler | 参数 | 实际限制 |
| --- | --- | --- |
| replace_tool_description | replacement_json | 仅tools[i].function.description或functions[i].description字符串；不改Schema/name |
| project_result_fields | fields字符串数组、field_level | tool结果对象/逐行对象数组；异构行失败，不丢行 |
| select_result_items | start/end非负整数 | 数组左闭右开，不越界 |
| select_result_lines | start/end非负整数 | Python splitlines(keepends=True)边界，保留原换行，不加业务标记 |
| apply_retention_replacements | replacement_json | 明确替换tool结果内容，保留消息/调用结构；策略候选仍需参数 |
| replace_payload_with_reference | reference_key/reference_value/protocol_ref/tool_identity | 内嵌arguments顶层document字段→不存在的顶层引用字段；当前准确工具Schema支持不附约束的string引用，原字段非required；不执行工具验证真实引用，真实值与协议由业务提供 |
| remove_authorized_duplicate_message | authorized=true | 仅内容与同请求tool结果完整相同的普通user/assistant文本消息；拒绝携带调用的消息、tool/function、其它未证实重复 |

分析返回的T1/T2候选为待参数的可选内容修改，不代表内容有错；T4只有明确策略违反才给替换候选。T3无引用协议/删除授权时保留事实与建议，不自动创建删除方案。现已提供纯函数`authorizations.authorize_candidate(fragment, observation_id, selected_unit_id, handler_id, handler_version, parameters_json, business_basis_ref)`，版本token-authorization-1；公共提交/worker两次调用，封存授权记录，再由prepare复核源。只接受已存T3观察成员及两个专用handler，普通完整文本消息从可信content位置映射到所属message，不允许客户端指定任意路径。

同一内嵌外层字符串的多个不相交目标一次编译，保留原数值词法与字段顺序；manifest记录内嵌重新序列化。外层value_guard使用公共value_digest，内嵌先本线校验再用outer_string_guard保护完整字符串，公共层二次校验并原子应用。不同外层操作重叠拒绝，组合收益需真实独立回放。

编译过程H0无RunControl参数，当前设硬上限：原文+参数8MiB、深度64、1000目标；这是保护边界，生产资源默认值尚待TA006校准。H2外层数字经stdlib重新序列化，对会改变原数字词法的请求/替换返回PUBLIC_NUMBER_LEXEME_UNSAFE；不修改公共实现、不声称此类请求已支持安全变换。

## 已消费的公共服务与HTTP

公共H1 `SourceResolver`/`EncodingContext`和H2 `apply_mutations`/`evaluate_plan`已被真实三模型测试消费。评估Token使用direction=token_content、stage=direct_full，gate_passed=null；公共display_eligible只描述低命中卡片，不能据此隐藏Token。候选必须完成参数后显式评估。H3a DiagnosticService、H3b diagnostics-http-1已真实验收，以下路径均带`/diagnostics`前缀，除capabilities外必须携带x-tokenscope-service-instance。

| 操作 | 路径/说明 |
| --- | --- |
| 任务/报告 | POST /tasks；GET /tasks/{id}、/report；RuntimeOptions显式传入 |
| 已存结果/计算身份 | GET /tasks/{id}/items/{kind}及/{key}；kind含fragment、fragment_index、rule_coverage、authorization、plan、evaluation |
| 完整原始证据 | GET /tasks/{id}/requests/{fragment_id}；scope/raw_sha/capture俱全，按报告成员读取，支持>64KiB |
| 已存候选评估 | POST /tasks/{id}/token-evaluations；无参数/依据不产生有效after |
| T3业务授权评估 | POST /tasks/{id}/token-authorizations；Authorization字段与纯函数一致，另含fragment_id/submission_key |
| 已存Plan组合 | POST /tasks/{id}/combination-evaluations；2–8个同scope plan_refs(task_id,plan_id)，含Token方向combined，真实独立回放 |
| 逐请求修改与指标 | GET /tasks/{id}/evaluations/{evaluation_id}/rows；仅available封存结果、分页、实际变化/after_raw/前后P/H/C/IDs摘要 |
| 取消/重试 | POST /tasks/{id}/cancel及/retry；新attempt不覆盖既有封存报告 |

wire所有元数据整数是十进制字符串，内嵌JSON文本不转换。EvaluationResult服务视图另有gate_passed/display_eligible/gain_percentage_points精确分数/compute_tokens_delta派生字段；不是冻结核心Schema增加字段。GET只读且摘要核验有I/O成本。前端尚未验收，不把HTTP测试称UI完成。

已通过测试及版本摘要分别见各批RESULT与TA004/CODE_IDENTITY.json。参数错配未注册、无打包部署。

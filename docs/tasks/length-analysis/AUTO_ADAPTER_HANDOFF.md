# Token 自动适配器接入（持续更新）

当前 ARTA001/002 私有实现闭环，适配器 descriptor 为 T2/T3/T4，generator_identity=token-content-recipes-1。ARTA003/004 本线真实 worker/回放/应用 HTTP/discovery 已验收，163项测试通过；前端正式接收/视觉验收及公共整体审查另行记录。

- 导入 `tokenscope.token_content.auto_proposals.TokenProposalAdapter` 静态注册到 ProposalRegistry。四方法直接实现公共 Protocol；适配器纯逻辑，不编码/回放/写库。
- 新任务插件使用 `tokenscope.token_content.current_plugin.CurrentTokenContentPlugin`（token-content-2，T2–T4）；历史 token-content-1 保留原类。新注册、任务装配和旧报告只读兼容由公共侧核对；不要重算旧报告。
- 私有 selector `token-result-selector-1`：appid、tool_name、tool_identity、representation(text/structural_json)、embedded_pointer 必填；retention_unit=result_container/text_part，默认 container。文本 embedded_pointer=null；结构化 JSON 显式 pointer，空字符串表示内嵌根。T4 仅完整根/文本，不替换任意嵌套子字段。
- generator `token-result-generator-1`：project_fields(fields,field_level)、select_items/select_lines(side=first/last,count)、retain_last(keep_last,replacement_json)。全部必须 omission_permitted=true；字段不允许重复/空列表，未知字段拒绝，整数不接受 bool/string/float。
- basis 初版仅 verified business_policy；scope_selector 与完整 selector 语义一致，不接受空对象通配。来源可信性由受控后台配置提供，不开放前端提交授权。合成测试明确 source_kind=synthetic_fixture 和 limitations。
- 无basis且匹配目标→advice_only/RECIPE_BASIS_MISSING；无匹配→空 proposals。坏配置、预算中断、证据缺失不得折叠成“无问题”。同一 recipe 支持跨请求归组，具体位置和参数仅在 request_targets。
- T2/T4 evidence 可使用内容库存 Observation，无需强制 Finding。结构化子单元支持引用其父库存 Observation；目标仍必须是 fragment 真实 Location。prepare 再核对原文目标与参数。
- 151 项 Token 回归通过，完整结果见 [ARTA001](batches/ARTA001/RESULT.md)。真实自动任务 N/M、Plan/Evaluation、发布与 discovery 在 ARTA003/004 联合验收，未提前宣称通过。

## T3 当前配置

- selector 版本 token-duplicate-selector-1：appid/payload_digest/target_kind 必填；argument_field 要求 tool_identity + argument_pointer（单层 JSON Pointer），不许 message_role；ordinary_message 要求 message_role=user/assistant，不许工具/参数字段。
- generator 版本 token-duplicate-generator-1：kind=reference/delete_message，omission_permitted 必须布尔 true。reference 需要 reference_key/protocol_ref，reference_value 可空但空时只能 advice_only；delete_message 不接受引用字段。
- basis 仅 verified explicit_authorization，scope_selector 与 selector 语义一致；真实配置必须证明引用可用性及消费协议。构造测试不能作生产授权。
- 依据 exact_payload_repetition 的 Observation/Unit/Location，不要求 Finding；prepare 重新从原请求分析重复关系并验证，不能拿伪造 Observation 删原文。
- 新插件 CurrentTokenContentPlugin/token-content-2 的正常/失败 fragment 都报告新身份，原 plugin 类及旧 T1 读取/处理接口保留。公共已在 bootstrap 显式切换，本线通过实际应用 GET 验证，未修改共享装配代码。

当前私有机器配置模型见 [AUTO_RECIPE_SCHEMA.json](AUTO_RECIPE_SCHEMA.json)，实际HTTP三类/状态样例及摘要见 [ARTA004](batches/ARTA004/RESULT.md)。真实业务策略未提供时默认空bundle，无生产自动精简授权；合成配置只作工程验证。

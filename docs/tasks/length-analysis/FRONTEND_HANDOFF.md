# Token异常后端：异常分析前端接入交接

> 2026-10-31最新批准范围：[TA-S1](SCOPE_REVISION_T234.md)移除Token T1，保留T2–T4编号；工具定义归低命中现有一致性/漂移职责，不增长度精简。当前新设计/计划/推荐/视觉验收仅T2–T4；旧源码及TA000–006历史仍含T1，不冒称已删除。当前实施计划见[BATCH_PLAN_ARTA](BATCH_PLAN_ARTA.md)，三卡样例见[AR-T3](FRONTEND_REWORK_EXAMPLES_ART3.json)。本轮仅文档同步，暂不编码打包部署。

版本TA-FE1，2026-10-31。维护方Token后端session `01a18fcd-0464-7cf1-b435-4f394bd33e66`。本次仅整理交接，不启动前端、不改变后端或用户视觉审批，不打包部署。

已借鉴并对齐[低命中与公共层前端交接](../prefix-analysis/FRONTEND_HANDOFF.md)：沿用“入口/调用/字段/状态/门槛/完整JSON样例/验收”的组织方式。该文档是公共接入主入口，本文补充Token消费差异；不维护第二套公共协议或另启前端会话。

## 1. 共同入口与事实基线

| 阅读项 | 权威入口 | 负责范围 |
| --- | --- | --- |
| 统一前端角色/视觉/审批 | [异常分析前端启动prompt](../../../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md) | 同一个前端会话承接低命中与Token，不接管监控V2 |
| 公共层与低命中交接 | [FRONTEND_HANDOFF](../prefix-analysis/FRONTEND_HANDOFF.md)、[IMPLEMENTED_API](../prefix-analysis/IMPLEMENTED_API.md)、[local-2自审](../prefix-analysis/SELF_REVIEW_20261031.md) | HTTP、来源、任务、L1–L5、实验与展示门槛 |
| 公共版本与交接 | [H0–H4交接](../analysis/BACKEND_IMPLEMENTATION_HANDOFF.md)、[冻结Schema](../../contracts/analysis-common-1.0/README.md) | 公共主会话唯一维护；以当前实际实现为准 |
| 浏览器请求契约 | [HTTP冻结Schema](../../contracts/diagnostics-http-1/README.md) | wire.json与capabilities；internal.json不作浏览器传输格式 |
| Token实际能力 | [API/参数](IMPLEMENTED_API.md)、[后端交接](BACKEND_HANDOFF.md) | T1–T4、内容证据、修改处理器及授权 |
| 本次启动增量 | [Token前端接入prompt](../../../prompts/sessions/TOKEN_CONTENT_FRONTEND_INTEGRATION.md) | 本文的执行入口，不创建第二个前端会话 |

两线后端本地已闭环；Token本线最终112项通过，公共后续local-2自审另记联合回归，不能混作本线新测试。前端视觉/现场验收仍未完成。版本：`analysis-common-1.0`、`diagnostics-http-1`、`diagnostics-runtime-1`、报告`diagnostics-report-1`；Token插件`token-content-1`，T1–T4@1，策略`token-policy-1`，授权`token-authorization-1`。公共local-2新增低命中experiment的pilot_scope/reason_codes/confidence_basis，不改变Token门槛或冻结核心Schema。

## 2. 接入流程与请求

1. GET `/diagnostics/capabilities`确认实例、版本、请求Schema。其余路径携带`x-tokenscope-service-instance`。实例切换后不可沿用另一实例的task/证据缓存。
2. 用户明确选择封存来源、appid及可选半开窗口。来源支持base或已发布user_v2，不接MA原始请求库；模型/编码身份由源绑定，不让用户另选不匹配模型配置。
3. 用户显式POST分析。reason_codes包含`low_hit`时两个enable均true；只有`request_length`/`qps`时false/true。两类结果共用原scope，低命中完整阶段结束后才启动Token。QPS不等于Loop证据。
4. 仅跟踪用户已提交任务的receipt；轮询间隔由前端方案确定，终态停止。浏览页面或刷新报告不POST分析，不周期重新计算；保留已有历史报告及其范围。
5. 读取已封存report及分页fragment；由用户选择具体方案、填写参数/业务依据后，再显式提交评估或T3授权。返回的是**新评估任务**，不能继续只轮询原分析task_id。
6. 从评估任务读取evaluation/plan/逐请求rows；始终允许回到原分析请求与授权记录。

当前**没有按appid查询最新诊断报告/服务器任务目录的端点**，前端保存用户已知task_id并按实例分区；跨浏览器发现历史任务不是已交付能力。TaskReceipt没有创建/完成时间字段，浏览器读取时间不能标成分析时间。提交子任务时保留父task_id，子任务不一定重复保存父fragment/finding；不要在子任务中盲查原观察。正式接收记录实际代码摘要/版本/实例，本地工作树身份不等于远端部署版本。

下面是完整**构造请求模板**，不是可复用的真实run ID或生产预算；`BASE_RUN_ID`/appid/幂等键须换成实际值，预算按服务与业务规模显式确认：

运行预算属于前端接入配置/高级设置，不要求普通业务用户逐项填写技术参数；不能当作内容异常阈值，也不能静默套用并声称覆盖超出预算的范围。

```json
{
  "request": {
    "source": {"source_kind":"base","base_run_id":"BASE_RUN_ID","appid":"APP_ID"},
    "selection": {"reason_codes":["request_length"],"enable_low_hit":false,"enable_token_content":true},
    "reason_note":"人工检查Agent输入内容",
    "submission_key":"UNIQUE_INTENT_KEY"
  },
  "options": {
    "version":"diagnostics-runtime-1",
    "token_selection": {
      "rule_ids":["T1","T2","T3","T4"],"policies_json":"[]",
      "budget":{"max_request_bytes":"1048576","max_units":"10000","max_comparison_bytes":"8388608","max_depth":"64","max_candidates":"1000","max_encoding_calls":"100"}
    },
    "candidate_limit":"2","pilot_limit":"2","max_source_requests":"100",
    "max_source_bytes":"10485760","max_findings":"1000","max_experiments":"4",
    "max_combinations":"0","max_encoding_calls":"100","max_plan_bytes":"16777216"
  }
}
```

HTTP元数据整数为十进制字符串，包括时间ns、索引、计量和attempt；前端用字符串/BigInt保持精度，不用Number承载大整数。`policies_json`、`parameters_json`、`details_json`、原始raw_body是JSON**文本**，内部数字不做公共wire转换；不要把`start:0`改为`start:"0"`。展示原文保留原字节/数字词法，不经普通JSON.parse→stringify覆盖源文本；需要解析定位时使用保真方式，展示格式化副本与原文分开。

## 3. 实际路由与读取位置

以下统一前缀`/diagnostics`，每个ID作为独立path segment编码。列表返回`{items:[{id,data}],offset}`，offset>=0、limit为1–100；无total/has_more/next_cursor，恰满页继续请求，不足一页才结束；不伪造总页数，读完所需分页再做总量声明。

| 方法/后缀 | 使用方式 |
| --- | --- |
| POST /tasks | 上述Submission；202返回TaskReceipt。同幂等键同意图复用，异意图409 |
| GET /tasks/{id} | receipt；终态不代表一定有可用报告，检查report_ref/错误 |
| GET /tasks/{id}/report | scope/scope_id、stages、runtime_options、encoding_calls；非已发布报告409 |
| GET /tasks/{id}/items/fragment | **Token主结果**；id是source_record_index字符串。按RequestKey识别，不用hash_id去重 |
| GET /tasks/{id}/items/fragment_index/{fragment_id} | 与同fragment数组顺序一致的location_ids/unit_ids/observation_ids；无需前端重写哈希算法 |
| GET /tasks/{id}/requests/{fragment_id} | 完整原文及RequestKey、scope_id、raw_sha256、raw_body_complete、capture_truncation |
| GET /tasks/{id}/items/plan、/evaluation、/authorization | 评估任务的已存成员。单项路径再加/{key}返回data本体 |
| GET /tasks/{id}/evaluations/{evaluation_id}/rows | available评估的分页行证据；返回source_record_index及evidence，非完整评估409 |
| POST /tasks/{id}/token-evaluations | 已存fragment_id/candidate_id、完整parameters_json、business_basis_ref、submission_key |
| POST /tasks/{id}/token-authorizations | 已存fragment_id/observation_id/selected_unit_id、handler_id/version、参数、业务依据、幂等键 |
| POST /tasks/{id}/combination-evaluations | 2–8个已存同原scope、非pilot的`plan_refs:[{task_id,plan_id}]`及submission_key |
| POST /tasks/{id}/cancel、/retry | 协作取消；retry体含新submission_key，返回新task/attempt，旧报告保留 |

**不能混用的列表**：当前`items/finding`、`items/optimization`、`items/experiment`及独立`items/rule_coverage`为低命中结果通道。Token发现位于`fragment.finding_candidates`，规则覆盖位于`fragment.rule_results`；T3可能只有Observation而没有FindingCandidate，不能因此漏掉内容事实。Token不是另一个worker/API服务。

错误体为`{error:{code,message}}`，按HTTP及code处理：错实例409、缺实例头/非法参数422、外报告成员404、报告未封存409；源摘要/模型身份变化、guard/组合冲突和预算超限展示具体原因。不要把任何读取失败降级成“没有异常”，不要自动扩大预算或无幂等保护重发业务修改POST。同意图网络重发保留submission_key，改变参数/范围用新键。report_ref/manifest_ref是引用，不是任意文件下载URL。取消返回running时继续跟踪终态，不当取消失败。

## 4. 结果和证据字段映射

| 对象/字段 | 前端表达与关联 |
| --- | --- |
| report.scope / scope_id | 固定来源、appid、模型服务身份、时间窗、request_count、baseline_origin；所有收益比较必须同scope |
| fragment.request_key / raw_sha256 / plugin_id / plugin_version | 源记录与版本；列表页缓存键至少含实例、task、fragment；不跨报告拼位置 |
| locations[] | request_key、raw_sha256、source_pointer；embedded含format/parser_version/pointer。embedded=null与pointer=""（内层根）不同 |
| units[] | location_id、representation、measurement_version、content_sha256、facets、measurement_unit、measured_value；parent_unit_id/container_unit_id/overlap_relation描述包含关系 |
| unit.participation | included/ignored/unknown，evidence_method/encoding_identity及可选prompt_token_spans；unknown不等于已进入模型，ignored不称模型负担 |
| observations[] | rule_id/version、unit_ids、predicate、method、policy_digest、condition、details_json。`content_inventory/met`表示观察到内容，**不是异常成立** |
| finding_candidates[] | finding_id、rule_ids、observation_ids、title、category、advice。category区分optimization_opportunity/policy_exceeded/needs_evidence等，不把所有卡片称配置错误 |
| modification_candidates[] | candidate_id、finding_refs、handler_id/version、action_class、locations、parameters_json、business_basis_ref、missing_parameters；缺参数显式待补，不能默认裁剪 |
| rule_results[] / coverage | rule/status/condition、checked/eligible/complete/reasons/stop_location、reason_codes。checked的单位按对象解释，不是统一进度百分比 |
| evaluation | evaluation_id/plan_id/scope_id、direction、stage、status、baseline_origin、coverage、before/after、modified_before/modified_after、reason_codes |
| plan | 受保护operations、原值guard、raw摘要、transformation_digest、finding_refs、业务依据与版本；供审阅，不向用户提供任意路径执行器 |
| authorization | input保留业务授权字段，candidate是由已存T3证据派生的候选；提交/worker再次复核，不改原报告 |
| evaluation rows | source_record_index；evidence含sequence、before/after_j/p/h/c、before_ids/after_ids（摘要，不是数组）、changes、after_raw。按返回顺序分页，不按hash_id重排；after_raw是实验副本，无操作行可为null；读取原文仍走原任务requests接口 |

`details_json`按规则显示：

- T1/T2的`content_inventory`：measures、tool_name/tool_identity/identity_status、participation、capture_truncation、token_contribution=null；T1另含components，不与完整定义重复相加。
- 明确limit：actual/limit/unit/operator；field_allowlist：extra_fields的row/fields与field_level；不兼容单位/身份不足有reason并为unknown。策略与预算分别显示。
- T3 `exact_payload_repetition`：occurrences、comparison、repeated_utf8_bytes、occurrence_measures、scope=single_request、saved_tokens/deletion_safe/execution_count=null。结构相等但表示不同可无精确重复字节；不得补成可节约Token。
- T4库存：later_message_count只是后续消息数；retain_last：keep_last/retention_unit/scope_count/index/reason。K=0是显式策略，未提供K不等于0，多文本块默认仍是一个结果容器。

证据关联顺序：finding.observation_ids→fragment_index的观察索引→observation.unit_ids→单元→location_id→位置；T3直接从Observation开始。读取完整raw_body后按source_pointer定位，embedded只再解析该字符串一层。当前Token一般不提供raw字符偏移；不能靠全局substring首命中伪造高亮，无法准确定位时展示完整原文+路径。正文按文本安全渲染，不能执行其中HTML。同一请求多位置用一份原文多定位，不虚构“两次请求对照”。

去重：请求数按RequestKey并集；T2/T4共享unit只计一次；父子单元与T3组不可累计成总浪费。只有同scope/同单位、去掉包含重叠后才可做展示汇总，不跨两个报告相加。后端尚未提供的全appid业务归组不由前端猜测；分页加载不全时明确“当前已加载”，不把它当全量排行。

## 5. 三层状态与展示门槛

任务状态放任务区/范围提示，业务卡片只呈现已有事实和建议；符合原前端prompt“不将处理中/失败混入建议排序”的约定。状态不能被隐藏到用户误认为无问题。

| 层次/状态 | 展示行为 |
| --- | --- |
| receipt queued / running | 排队/运行；active_direction=low_hit时Token尚在等待，不显示“Token无异常”；没有百分比进度字段，不用coverage伪造进度 |
| ready | 已封存任务结果，继续读取规则状态，不能解释为“所有内容正常” |
| partial | 已封存部分结果/评估受阻；展示已完成证据和原因，不当完整排查；评估准备受阻可能只有report.reason_codes、stages=[]，没有evaluation |
| empty | 该scope没有可分析请求，不等于无异常 |
| failed / interrupted | 显示error_code与显式重试入口；可能无报告，保留旧报告，不读私有半成品 |
| report.stages completed / partial | 已发布方向结果。Token通常在低命中方向终态后才执行；共享源失败/中断可阻断后续 |
| rule completed / not_applicable / partial / failed / not_checked | 完成/不适用/部分/失败/未查；condition=met/not_met/unknown必须结合predicate。无策略常为unknown+NO_APPLICABLE_POLICY，不应盖“正常”章 |
| evaluation available | 只有完整评估才有before/after；显示零值和负收益，修改子集与全scope分别列出 |
| evaluation blocked / failed / not_run / interrupted | 展示原因，没有after和收益；不填0冒充测量结果 |

| 方向/内容 | 展示门槛 |
| --- | --- |
| 低命中优化卡片 | 完整full/direct_full且严格ΔR>1pp，以后端display_eligible为准；pilot过门槛仅表示小范围通过。pilot_scope/reason_codes/confidence_basis按公共local-2表达 |
| 低命中差异事实、Token内容事实/策略结果 | 不套优化门槛，事实与建议分类展示 |
| Token或含Token组合评估 | direction=token_content/combined，gate_passed=null；当前display_eligible=false是低命中属性，**不得用来隐藏Token/组合结果**；读取evaluation而非optimization列表 |

before/after中的n/j/p/h/c：请求数、JSON计量Token、模型输入Token、理想命中Token、需计算Token。R=H/P，P=0时不可定义；J变化不等于P或C变化。服务`compute_tokens_delta = after.c - before.c`，正数表示增加；若显示“节省量”，明确取相反方向。gain_percentage_points是精确分数{numerator,denominator}，单位pp，不是相对百分比。不要前端另行取整重判>1pp。原窗口与子窗口重算空起点由baseline_origin标识，不混用源H/C。

modified_before/modified_after是实际修改请求子集，不能再加到before/after。组合须真实独立评估，不能相加单项收益。评估不产生修改后O、真实金额、任务质量或Agent执行次数预测；输入内容优化不是在线应用修改。

## 6. 修改交互与典型样例

普通候选参数表复用[实际七类handler参数](IMPLEMENTED_API.md)。示例提交（ID须来自当前报告）：

```json
{"fragment_id":"3","candidate_id":"FROM_FRAGMENT","parameters_json":"{\"start\":0,\"end\":2}","business_basis_ref":"业务保留策略v1","submission_key":"NEW_EVALUATION_INTENT"}
```

这是保留行区间[0,2)的显式假设，不是默认建议。replacement_json若替换为字符串需JSON字符串值，例如parameters_json内容为`{"replacement_json":"\"保留文本\""}`。表单不能增加未知参数、自动填真实引用、自动删除工具Schema/调用配对或推断业务白名单。

T3没有自动删除候选时，从已存观察选择单元并提交授权：引用替换选择arguments内顶层完整字段，handler=`replace_payload_with_reference`，参数reference_key/reference_value/protocol_ref/tool_identity齐全；普通消息删除选择完整message_payload，handler=`remove_authorized_duplicate_message`，parameters_json=`{"authorized":true}`。两者均handler_version="1"，必须有业务依据。具体位置由后端从证据派生，UI不提交任意JSON Pointer。运行时仍可能因Schema/guard不足受阻。

以下数字为**构造展示样例**，不冒充现场发生率或实测节省量；真实可复现场景见后列测试入口。

T3完整原始请求示例（仅展示协议形状，不附伪造raw_sha256/真实scope）：

```json
{"tools":[{"type":"function","function":{"name":"consume","parameters":{"type":"object","properties":{"document":{"type":"string"},"document_ref":{"type":"string"}},"required":[]}}}],"messages":[{"role":"user","content":"处理材料"},{"role":"assistant","tool_calls":[{"id":"call_1","type":"function","function":{"name":"consume","arguments":"{\"document\":\"中文\"}"}}]},{"role":"tool","tool_call_id":"call_1","content":"中文"},{"role":"user","content":"中文"}],"enable_thinking":false}
```

一份全文显示三个位置：`/messages/1/tool_calls/0/function/arguments`内嵌`/document`、`/messages/2/content`、`/messages/3/content`。这是完整载荷同值事实，不推断搬运时间方向或工具执行次数。展示字段身份从该报告fragment_index取得；不能将上述示意路径直接变成修改指令。

用户明确授权删除最后一条普通重复消息时，提交形状如下（两个ID须从同一fragment的T3观察/成员索引取得；后端从单元映射父消息并再次复核）：

```json
{"fragment_id":"3","observation_id":"FROM_T3_OBSERVATION_INDEX","selected_unit_id":"FROM_MESSAGE_UNIT_INDEX","handler_id":"remove_authorized_duplicate_message","handler_version":"1","parameters_json":"{\"authorized\":true}","business_basis_ref":"业务确认该额外复制可删除","submission_key":"NEW_AUTHORIZATION_INTENT"}
```

引用替换所需tool_identity应取准确工具定义证据/业务协议，没有可用身份时不得由前端猜测或临时计算一套摘要。真实引用存在性与业务效果仍需业务确认。

| 场景 | 业务显示样例 | 不能推断 |
| --- | --- | --- |
| T2无策略，已观察工具结果65536字节、participation unknown | “工具返回内容：64 KiB；未提供业务限额。模型输入贡献尚未确认。” 可查看原文、显式设置保留范围 | 超限/工具无用/精确65536 Token |
| T2白名单array_items，row=0多出debug字段 | “第1行含策略未允许字段debug”；保留policy_id/revision/原JSON行序，用户明确fields后评估 | 自动删整列；异构行静默跳过 |
| T3三处相同“中文” | “本请求3处完整载荷相同，非重叠重复字节12”；一份原文定位tool、arguments与普通消息 | 执行3次、Loop、可节省12 Token |
| T4两个结果容器，第一个有多个文本块，keep_last=1 | “按业务策略保留最后1个结果容器，较早容器待确认替换” | 将content part算多次调用；无策略自动过期 |
| P减少但C增加 | before P=10000/H=8000/C=2000；after P=8000/H=5000/C=3000；“输入减少2000，需计算Token增加1000，命中率下降17.5pp” | 只标“优化成功”；隐藏负面结果 |
| 零效果 | available/direct_full，before=after；“本次修改未改变输入计算结果”，保留Plan和行证据 | 当成评估未运行，按低命中门槛隐藏 |
| guard失败/预算停止 | reason_codes+blocked/partial，收益显示“未取得完整评估” | 展示after=0或“节省100%” |
| 排队Token/旧报告 | “当前任务等待低命中阶段；下方为上一份已封存报告及其scope” | 清空历史、把等待当暂无问题 |

## 7. 前端接收与验收清单

- 同服务实例/任务/scope定位；大整数、显式原因路由、版本不兼容/未知字段明确拒绝或降级，不混入监控契约。
- fragment/index身份一致；T3无Finding仍显示事实；T2/T4不重复计量；完整JSON>64KiB、内外层根/转义Pointer、捕获截断unknown正确呈现。
- 任务/方向/规则/评估状态分开；queued/running只跟踪显式任务，终态停轮询；partial/empty/failed与无问题不同。
- Token/combined零负结果不套低命中门槛；P下降C上升、P=0、精确pp分数、修改子集不加总均有页面用例。
- 缺业务参数不自动执行；T3授权基于真实观察成员，实例/外报告/Schema/guard/组合失败正确呈现；新评估task追踪与原分析回链正确。
- 所有GET无分析副作用；大原文不在卡片中一次全展开，显示折叠不能改变计算/证据范围。实际前端视觉与浏览器验证由前端会话负责。

后端可复现样例：[任务/零负](../../../tests/integration/token_content/test_task_service.py)、[Token HTTP](../../../tests/integration/token_content/test_token_http.py)、[全文/授权/组合/行证据](../../../tests/integration/token_content/test_authorization_http.py)、[恢复](../../../tests/integration/token_content/test_recovery.py)、[跨方向冲突](../../../tests/integration/analysis/test_diagnostic_combinations.py)。这些是隔离合成fixture，不是已发布前端验收。发现差异记前端BACKEND_ALIGNMENT并交所属后端，不在页面补写诊断算法。

本轮文档验证：4段JSON及内嵌载荷可解析；Submission、TokenEvaluation、Authorization通过现有from_wire模型，完整请求通过现有validate_request。本文、两个启动prompt及本线入口/后端交接共61个Markdown链接目标存在。无业务源码变更，未重跑业务回归、未提交真实分析任务。接收状态为后端已提供，待异常分析前端实际会话登记/签收。

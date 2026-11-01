# 低命中与公共层：异常分析前端接入交接

2026-10-31 FE-N1增补已实现：[通知、目录与完成时间接入](NOTIFICATION_HANDOFF.md)（diagnostics-discovery-1）。覆盖下文“无任务目录/时间、对queued/running轮询”的旧能力描述：现在使用通知后拉取、打开/重连对齐目录、不轮询任务。旧H0/HTTP契约及原结果字段保持。

2026-10-31，后端提供方 session 01a18be2-7112-7aa2-919b-5137d1f1b1ad。用户已认可完整自审；本轮仅整理接入文档和启动 prompt，不代表前端已实现或验收，不打包部署。

## 1. 唯一入口与接收身份

| 材料 | 身份/用途 |
| --- | --- |
| [本线自审](SELF_REVIEW_20261031.md)、[源码摘要](SELF_REVIEW_CODE_IDENTITY.json) | low-hit-backend-local-2；193联合、2新增边界、300监控兼容测试通过，用户认可 |
| [公共 Schema](../../contracts/analysis-common-1.0/README.md) | analysis-common-1.0；wire.json 为传输契约，internal.json 不是浏览器直接输入格式 |
| [HTTP Schema](../../contracts/diagnostics-http-1/README.md) | diagnostics-http-1；请求模型以 wire.json 和 GET capabilities 为准 |
| [实际 API](IMPLEMENTED_API.md)、[资源预算](RESOURCE_PROFILE.md) | 路由、完整 RuntimeOptions、实际能力与限制 |
| [Token 后端交接](../length-analysis/BACKEND_HANDOFF.md)、[Token 参数/API](../length-analysis/IMPLEMENTED_API.md) | token-content-1、T1–T4@1、七类 handler@1；该线独立维护参数与规则语义 |
| [统一后端交接](../analysis/BACKEND_IMPLEMENTATION_HANDOFF.md) | H0–H4、公共层和 Token 维护责任 |
| [前端启动 prompt](../../../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md) | 供用户交给异常分析前端会话；本轮不自动创建/发送/启动会话 |

公共方负责 HTTP、任务、scope、证据存储和离线回放；Token 方负责 fragment、策略和变换参数。前端统一消费两类报告，在 apps/viewer 增量接入，不另建分析引擎。正式接入先记录实际后端 SHA/文件摘要、服务实例和契约版本；本地工作树身份不是远端已部署版本。

## 2. 调用顺序与能力边界

1. GET `/diagnostics/capabilities`，记录 `service_instance_id/contract_version/http_version/schemas`。其余诊断请求携带 `x-tokenscope-service-instance`，不能替换成监控 S0 的实例 header。切换服务清理旧请求响应与当前查询状态，历史报告按实例分区。
2. 用户明确发起时 POST `/diagnostics/tasks`，载荷 `{request,options}`。request 指定已封存的 base 或 user_v2 来源、appid、可选半开时间窗及人工原因。MA 可以提供调查线索，但不能作为诊断 SourceSelection 的请求库；必须选择支持的来源。不自动采集或阈值触发。
3. low_hit 原因启用两方向，低命中实验结束后再分析原始 scope 的 Token 内容；只有 request_length/qps 时仅 Token。32k/70%是人工理由，不是前端自动判异常规则。允许原因组合的准确约束以 DiagnosticSelection Schema/校验为准。
4. POST 返回202 TaskReceipt，排队不等于已计算。只对用户当前跟踪的 queued/running 任务查询状态；终态停止，report_ref 可用后读取报告和结果页。轮询间隔由前端交互方案确定，后端未提供百分比进度/SSE。页面访问、刷新或切换 tab 均不得提交分析；GET 不计算、不补结果。
5. 离线评估是显式 POST 的新任务。新任务失败不能清空旧报告；retry 新 submission_key、新 task_id/attempt，保留原任务。记录用户可访问的 task_id：当前没有诊断任务列表/按 appid 查询最新报告的端点，不能假设已有服务器历史目录。跨浏览器发现旧任务能力需另行讨论，不由前端虚构 API。

JSON 元数据整数传十进制字符串（计数、纳秒、预算、分数等），布尔值仍为 bool。分页 query 参数 offset/limit 为普通 URL 十进制文本。原始 raw_body、recipe_json、parameters_json、details_json、policies_json 是 JSON **文本字符串**，内部业务数字不得做 wire 转换。JS 使用 BigInt/精确分数处理计数与收益，null 不补0，不能用舍入后的百分数重判门槛。

## 3. 路由与读写响应

统一前缀 `/diagnostics`；所有 key/id 作为独立 path segment 编码。

| 方法与路径 | 载荷/响应及前端用途 |
| --- | --- |
| GET /capabilities | 实例、契约版本、六种提交请求 Schema；不是规则默认预算清单 |
| POST /tasks | `{request,options}` →202 TaskReceipt；同 submission_key 同意图返回原任务，异意图409 |
| GET /tasks/{id} | TaskReceipt；不从阶段覆盖数量推导完成百分比 |
| GET /tasks/{id}/report | 报告 scope、scope_id、stages、runtime_options、encoding_calls 等；初次分析与显式评估报告形状不同，显式评估可 stages=[] |
| GET /tasks/{id}/items/{kind}?offset=0&limit=100 | `{items:[{id,data}],offset:"0"}`，limit 1–100；无 total/has_more/next_cursor，收到不足 limit 才结束，恰满页继续读取 |
| GET /tasks/{id}/items/{kind}/{key} | 返回 **data 本身**，不是列表的 `{id,data}` 包装 |
| GET /tasks/{id}/comparisons/{finding_id} | `{comparison,left_raw_body,right_raw_body,raw_body_complete}`，两条完整原文；此端点无 capture_truncation 字段 |
| GET /tasks/{id}/requests/{fragment_id} | `{request_key,raw_body,raw_sha256,raw_body_complete,scope_id,capture_truncation}`；Token 完整原文 |
| GET /tasks/{id}/evaluations/{evaluation_id}/rows | `{items:[{source_record_index,evidence}],offset}`，相同分页约束；不可用评估409 |
| POST /tasks/{id}/cancel | 无请求体；协作取消，收到 running 不代表取消失败，继续读取终态；终态取消不倒退状态 |
| POST /tasks/{id}/retry | `{submission_key}` →202 新任务 |
| POST /tasks/{id}/low-hit-evaluations | `{finding_ids,submission_key}`；1–2个已存 finding，有 recipe；两项组合只接受支持的动态组合。显式直接全范围，报告标 pilot_bypassed_by_explicit_request |
| POST /tasks/{id}/token-evaluations | `{fragment_id,candidate_id,parameters_json,business_basis_ref,submission_key}`；按 Token 文档补全真实参数和业务依据 |
| POST /tasks/{id}/token-authorizations | `{fragment_id,observation_id,selected_unit_id,handler_id,handler_version,parameters_json,business_basis_ref,submission_key}`；仅已存 T3 证据及两个专用 handler |
| POST /tasks/{id}/combination-evaluations | `{plan_refs:[{task_id,plan_id},…],submission_key}`；2–8个同原 scope 的已存 Plan，不用 pilot Plan，冲突阻断；不把单项提升相加 |

错误体 `{error:{code,message}}`。422输入/header不合法，409实例/幂等意图/范围/完整性/评估可用性冲突，404未知任务或成员，503存储不可用；以实际 code 保留可诊断原因，未知 code 也可展示。读取失败不是“未发现异常”；未发布结果不能绕过 report_ref 读私有文件。`manifest_ref/report_ref` 是引用，不是任意文件下载 URL。

## 4. 三层状态，分开展示

| 层级 | 状态 | 展示/行为 |
| --- | --- | --- |
| TaskReceipt | queued / running | 任务管理区显示排队/进行中；active_direction 可为 low_hit、token_content 或 null，不能伪造进度 |
| TaskReceipt | ready | 已发布；不代表有异常或有可展示收益 |
| TaskReceipt | partial | 已发布但有规则/候选/预算未覆盖；仍可显示已完成证据，显著注明局限，不能宣称全量无异常 |
| TaskReceipt | empty | 源范围为空，不等于“正常”；以 report_ref 判断报告入口 |
| TaskReceipt | failed / interrupted | 失败/中断，无成功结论；保留 error_code 和旧任务入口，可显式重试 |
| stages/RuleResult | completed / partial 等 | 实际阶段/规则覆盖；字段并不等同任务状态枚举，按 report 与 fragment 分别解析 |
| EvaluationResult | available | coverage.complete 且前后齐全；可读取 rows；是否低命中优化卡片另看 display_eligible |
| EvaluationResult | blocked / failed / not_run / interrupted | after 不可用，展示 reason_codes；禁止把 null after 当作0或节省100% |

业务建议与任务管理分区，任务失败卡片不混入业务建议排序。旧成功报告保持可见，并标注其 task_id/来源范围，不能冒充最新失败尝试的成果。服务目前 TaskReceipt 没有创建/完成时间字段；不要将浏览器读取时间标作分析时间。

## 5. 结果、证据与字段映射

| kind / 对象 | 关键字段与展示 |
| --- | --- |
| report.scope | source 身份、appid、window、request_count、request_keys_digest、baseline_origin；window 不为空时为[start_ns,end_ns)，UTC原值保留；source 保存模型/资产/配置身份，不允许 UI 更改模型后沿用旧评估 |
| finding | finding_id、rule_id/version、advice、evidence_status、source_pointer、recipe_json、comparison；无自带“影响请求数”或概率置信度，不从 finding 条数推算去重请求数 |
| comparison | left/right RequestKey(base_run_id,source_record_index)、两端 raw_sha256、difference_pointers、association_ref、lcp_tokens；LCP不是实际引擎可复用边界。工具排序变动时前后指针可能不同 |
| experiment | finding_ids、status、selection_method、pilot_scope、pilot、full、reason_codes、confidence_basis；预算未执行分支还可能只有 status/not_run、reason、finding_ids。pilot/full 内为核心评估，完整展示派生值读取 evaluation 项，不假定嵌套对象有相同派生字段 |
| rule_coverage | checked_requests、candidate_comparisons、partial、reason_codes；是有界召回覆盖而非运行进度；两通道记录不能当作五条独立规则完成状态 |
| evaluation / optimization | evaluation_id、plan_id、scope_id、stage、direction、status、coverage、before/after、modified_before/after、baseline_origin、manifest_ref、reason_codes；evaluation 包含不达门槛的实验；optimization 仅低命中可展示结果 |
| 指标对象 | n请求数、j序列化JSON Token数、p模型输入Token数、h理想命中Token数、c计算Token数；p=h+c。R=h/p，p=0则不可判定。不得混淆JSON长度、j与p |
| 服务派生字段 | gate_passed 可空；display_eligible 布尔；gain_percentage_points={numerator,denominator} 为绝对百分点；compute_tokens_delta=after.c-before.c，正数表示增加，不是节省 |
| plan | plan_id、direction、action_class、source_scope_id、transformation_digest、finding_refs、operations、combination_refs；用于追溯和显式组合，不允许前端注入任意路径/可执行修改代码 |
| rows.evidence | sequence、before/after_j/p/h/c、before_ids/after_ids（摘要，不是 IDs 数组）、changes、after_raw；after_raw 为实验副本，可空，不覆盖原文；按返回顺序分页，不按 hash_id 重排 |
| fragment / fragment_index | Token fragment 的 locations/units/observations/finding_candidates/modification_candidates/rule_results/coverage/reason_codes；index 同顺序提供 location_ids/unit_ids/observation_ids，避免客户端复制稳定ID算法；fragment_id 使用列表 item.id，不假定 fragment 有同名字段 |
| authorization | Token T3 的显式业务输入及生成候选；展示业务依据，不能把未授权重复事实显示成自动可删 |

追溯链：evaluation.plan_id → plan.finding_refs → finding → comparison完整原文。显式子任务可能引用父任务 finding，父 task_id 要随提交保存；不要假设子任务重复保存所有父 finding/fragment。Token 链为 fragment observation → unit → location；同请求多处重复展示同一份完整 JSON 的多位置，不虚构第二请求。

完整 JSON 以文本安全渲染，不能作为 HTML 执行。可折叠、虚拟滚动和高亮，但必须能查看两份全文；预览截断要明确标识且有全文入口。不要经 JS JSON.parse/stringify 损失大整数后替代原始证据；格式化视图须保留原始文本切换及摘要。raw_body_complete 仅表示存储原文完整，不证明上游未截断；capture_truncation=unknown 不转为 known_complete。

## 6. 规则、建议与展示门槛

| 规则 | 当前可展示结论 / 建议 |
| --- | --- |
| L1 动态元数据 | 已识别日期/路径/known billing cch；建议移除动态片段并看离线收益。已知cch信息保持，其它是业务删除假设，由业务决定采纳；不推断所有随机字段已覆盖 |
| L2 工具顺序 | 完整定义集合相同且唯一function身份时稳定排序；不重排messages/tool_calls |
| L3 工具定义/集合 | 动态路径/时间可删除副本评估；集合增删只提供事实，不强行统一定义 |
| L4 消息差异 | 无可靠session时 needs_association；正常后缀追加排除，不命名为“历史污染/死循环已证实”；提供两条完整JSON |
| L5 JSON表示差异 | 严格语义结构/数字词法等边界内的表示差异证据；不给默认收益，提供两条完整JSON |

自动流程：完整连续 pilot 精确提升 **>1个百分点** →同变换全范围回放 →完整 full 精确提升 **>1个百分点** 才进入低命中优化卡片。恰等于1不通过。pilot_scope 是该小范围，full 是该appid选定范围全部请求，不回放其他appid；未改后继请求也计入。confidence_basis=pilot_gain_gt_1pp 不等于已获全范围收益；无该值不可伪造高置信度。

显式 direct_full 不要求已有 pilot，通过全范围门槛可展示，但必须标注“用户直接全范围评估，未经过小范围核验”。不把其称作已完成标准两阶段流程。

L4/L5及其他差异证据独立展示；Token/含Token组合不套低命中门槛，display_eligible=false 或 gate_passed=null 不隐藏它们。所有零/负收益保留在实验区。联合收益仅展示真实组合评估；R提高不等于C减少或实际费用下降，不推断输出Token/O、延迟或任务质量改善。modified_* 是实际修改请求子集，不能替代全范围before/after。

## 7. 典型展示样例（合成说明，不是现场测量）

以下为完整提交形状，`replace-with-sealed-run` 必须替换成当前服务已有来源；这些预算只用于小规模接入测试，不是生产默认值或业务异常阈值。source_kind=user_v2 的具体字段按冻结Schema，不直接沿用base示例。

```json
{
  "request": {
    "source": {"source_kind":"base","base_run_id":"replace-with-sealed-run","appid":"example-app"},
    "selection": {"reason_codes":["low_hit"],"enable_low_hit":true,"enable_token_content":true},
    "submission_key":"example-low-hit-001",
    "reason_note":"人工发现长输入且理想命中率偏低"
  },
  "options": {
    "version":"diagnostics-runtime-1",
    "token_selection": {
      "rule_ids":["T1","T2","T3","T4"],"policies_json":"[]",
      "budget": {"max_request_bytes":"1048576","max_units":"10000","max_comparison_bytes":"1000000","max_depth":"64","max_candidates":"1000","max_encoding_calls":"100"}
    },
    "candidate_limit":"2","pilot_limit":"3","max_source_requests":"100",
    "max_source_bytes":"10000000","max_findings":"1000","max_experiments":"8",
    "max_combinations":"2","max_encoding_calls":"100","max_plan_bytes":"16777216"
  }
}
```

排队响应形状（ID仅占位）：

```json
{"task_id":"example-task","attempt":"1","status":"queued","active_direction":null,"report_ref":null,"error_code":null}
```

相同意图的网络重试复用原submission_key；更换appid、窗口、参数或预算时不得误复用。Token-only将reason_codes改为request_length或qps，并把enable_low_hit置false，enable_token_content仍为true。

| 场景 | 展示示例 | 数据边界 |
| --- | --- | --- |
| L1通过两阶段 | “动态时间字段影响前缀复用；小范围 +5pp；选定appid全范围 60%→80%，+20pp；计算Token 400,000→180,000。” | full before p=1,000,000/h=600,000/c=400,000；after p=900,000/h=720,000/c=180,000；gain={numerator:"20",denominator:"1"}，compute_tokens_delta="-220000"；只有实际后端已存结果可用于正式卡片 |
| 边界恰1pp | “小范围提升1.00pp，未达到严格>1pp，未自动全范围评估。” | 不显示优化卡片；不能四舍五入后改为通过 |
| pilot通过但full超预算 | “小范围提升已验证；全范围未执行：PLAN_BYTES_EXHAUSTED。” | experiment.full_not_run、pilot_scope保留；只在实验区显示小范围值，不能作为全范围预期收益 |
| L4完整证据 | “两条请求消息内容不同；缺少session关联，不能判断为同一任务历史改写。” | 按下面全文展示，无优化门槛、不推断Loop |
| L5完整证据 | “tool结果JSON表示不同；可查看完整请求对比。” | 按下面全文展示；无默认删除/收益 |
| Token零/负效果 | “内容修改后P减少，但C增加；请评估是否采用。” | direction=token_content/combined 时展示真实 before/after，不因display_eligible=false隐藏 |
| partial/源损坏 | “有界候选未全覆盖” / “证据完整性校验失败” | 前者保留已验证项并标局限；后者展示错误，不渲染成无问题 |

L4 左完整请求：

```json
{"messages":[{"role":"system","content":"你是助手"},{"role":"user","content":"查询订单A"},{"role":"assistant","content":"处理中"},{"role":"user","content":"继续"}],"enable_thinking":false}
```

L4 右完整请求：

```json
{"messages":[{"role":"system","content":"你是助手"},{"role":"user","content":"查询订单B"},{"role":"assistant","content":"处理中"},{"role":"user","content":"继续"}],"enable_thinking":false}
```

L5 左完整请求：

```json
{"messages":[{"role":"user","content":"查询订单"},{"role":"assistant","content":null,"tool_calls":[{"id":"call_1","type":"function","function":{"name":"lookup","arguments":"{}"}}]},{"role":"tool","tool_call_id":"call_1","content":"{\"id\":1,\"status\":\"ok\"}"}],"tools":[{"type":"function","function":{"name":"lookup","parameters":{"type":"object","properties":{}}}}],"enable_thinking":false}
```

L5 右完整请求：

```json
{"messages":[{"role":"user","content":"查询订单"},{"role":"assistant","content":null,"tool_calls":[{"id":"call_1","type":"function","function":{"name":"lookup","arguments":"{}"}}]},{"role":"tool","tool_call_id":"call_1","content":"{ \"id\": 1, \"status\": \"ok\" }"}],"tools":[{"type":"function","function":{"name":"lookup","parameters":{"type":"object","properties":{}}}}],"enable_thinking":false}
```

上面演示原文形式，不附伪造 raw_sha256、scope 或真实收益；模型实际IDs是否变化由后端决定，前端不能对任意这类差异自行生成 L5 finding。

## 8. 前端接收与验收清单

先在前端自己的 BACKEND_ALIGNMENT 记录两线版本/入口及缺口，不修改 Token 或公共 Schema。最低验证包括：字符串大整数/原始JSON不损失；两类实例header隔离；同键重试/新attempt；任务七状态及报告读取错误；full/部分预算/零负收益/恰1pp；Token不被门槛隐藏；L4/L5两个完整JSON与双路径；完整请求>64KiB；分页恰满页及切换范围旧响应隔离；Token多位置/index身份；子任务追溯父证据；GET不触发分析、无报告列表API时不编造。

真实后端用例入口：tests/integration/analysis/test_diagnostic_http.py、test_diagnostic_tasks.py、test_experiments.py、test_dynamic_replay.py、test_diagnostic_combinations.py；Token侧 tests/integration/token_content/test_token_http.py、test_authorization_http.py、test_recovery.py。合成 UI fixture、真实HTTP、视觉检查及用户验收分别记录，不互相代替。视觉沿用用户批准的报告原型，最终设计与实施按前端会话收到的用户授权推进。

本轮文档校验：6段JSON均可解析，Submission/TaskReceipt通过现有from_wire模型校验，L5内嵌JSON可解析，本文与启动prompt的10个Markdown链接目标存在。未新跑业务回归（无源码变更），历史通过结果见自审；未调用提交接口创建真实任务。前端接收状态：待其实际会话登记与签收。

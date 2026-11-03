# diagnostics-execution-2 / diagnostics-discovery-2

HV2-R1-COMMON候选契约，2026-11-03；待总设计师独立验收。旧analysis-common-1.0、diagnostics-http-1、diagnostics-discovery-1及analysis-recommendations-1冻结文件不改。v2能力通过新路由显式提供，旧封存报告继续原GET读取，不回填遥测或重写任务。

## 路由与身份

| 路由 | 语义 |
| --- | --- |
| GET /diagnostics/v2/capabilities | 实例、协议、至少一个方向、完整submission/catalog/execution Schema；无计算 |
| POST /diagnostics/v2/tasks | SubmissionV2；返回原TaskReceipt七种任务状态及active方向；幂等键仍受整个intent/options约束 |
| GET /diagnostics/v2/catalog | diagnostics-discovery-2；原目录字段及selected_reports；snapshot/after/limit沿用旧规则 |
| GET /diagnostics/v2/tasks/{task_id}/execution | 持久终态（含empty）、明确方向、阶段覆盖与实测计时；旧任务availability=not_computed且telemetry=null，不重算 |

除capabilities外都必须带`X-TokenScope-Service-Instance`。错误header409，提交非法422；未封存任务读取延用RESULT_NOT_READY错误；目录未来/异实例/异epoch游标409。v2 execution.status取已发布任务的持久终态，避免历史report正文中ready与empty回执不一致；不回写旧report。新任务raw report.version为diagnostics-report-2，稳定新增视图由ExecutionViewV2定义。任务回执、report、recommendations、difference-groups、examples、固定历史、retry/cancel及SSE路径仍是已有路径。v1消费者继续读历史；要新提交单方向必须显式用v2，不悄悄更改v1验证规则。

数字按现有wire规则编码十进制字符串，精确整数/null/0保留。reason_codes解释人工触发原因，方向由两个布尔开关决定，至少一个true；同为low_hit原因允许用户只选低命中或明确选Token，不再由原因强制另一方向。

## 预算与覆盖

v2 RuntimeV2继承原资源字段并新增限制。每个启用方向有独立max_encoding_calls；两方向总上界为该值两倍，单方向不分配另一方向计算；来源字节/请求/深度预检仍共同硬边界。Token私有每请求RunControl仍独立，不改变内部规则预算。

`max_findings`在v2是低命中保留总条数（至少5），按L1–L5固定均分配额，余数按规则号分配，不按先到先占满；`max_retained_bytes`默认4194304，采用相同配额划分。单条按实际ResultWriter JSON UTF-8 payload字节计量，不包括SQLite页/索引元数据。保留达到上限继续检测并累计发现/省略计数，不持有被省略证据；不可宣称完整证据。规则保留空位不转给高频规则。扫描/候选/比较的不完整与保留截断分别表达；任何保留截断仍保守partial，不能修改成ready。

`max_comparisons`默认100000，分别约束L2及dynamic比较通道，两通道合计上界两倍；达到时停止该通道，另一通道与Token继续。candidate_limit截断记录CANDIDATE_LOOKUP_TRUNCATED，比较硬截断记录COMPARISON_COUNT_BUDGET_EXHAUSTED，均partial。保留截断是FINDING_RETENTION_TRUNCATED，不能解释为只扫若干请求。

Token保留`max_fragment_bytes`默认8388608、`max_total_fragment_bytes`默认67108864，包含fragment与fragment_index两项实际序列化payload字节。超过后不保存该fragment，但仍逐请求检测与累计rule状态；不把保留不足改写成fragment内部覆盖不足。保留不足为FRAGMENT_RETENTION_TRUNCATED，提案阶段若需完整fragment集合则保守停止，不能伪造全scope评估。来源有界、单请求私有预算与有限配额共同限制；这不是全进程RSS保证，未做现场15万规模校准。

旧candidate_coverage_partial字段沿用原阶段整体partial口径，可能含保留或实验未完成；新消费者应读取下列分维度字段，不用该旧字段推断真实候选截断。

低命中阶段：eligible_requests是scope请求数；checked_requests为两遍检测的最小完成数；scan_complete、comparison_complete、retention_complete分别说明维度。detected_by_rule/retained_by_rule为当前访问候选中真实发现与保留计数，不是请求数、不外推到未比较候选。rule_coverage补supported_rules与候选访问计数；applicable_pairs=null、applicability_status=not_separately_classified_by_detector明确私有探测器尚未单独报告适用对数，不用0冒充。

Token阶段：checked_requests是实际处理请求，fragments_complete保留插件覆盖判断，retained_requests/bytes单列；rule_status_counts汇总插件返回completed/not_applicable/partial/failed/not_checked，不重解释规则语义。保留前已累计，不被删掉的证据掩盖。原请求内units/comparisons等消耗见telemetry。

推荐预算按低命中发布与Token提案/评估分开，消耗汇总不代表共享同一额度。缺recipe时不进入逐fragment提案/adapter.propose，proposal_coverage eligible=0/checked=0/complete=true代表本阶段没有配置候选任务，不代表所有请求已评估；evaluation_coverage=null。必要Token内容检测仍按选择执行。NO_CONFIGURED_RECIPES、TOKEN_FRAGMENT_INCOMPLETE、RECIPE_BASIS_MISSING/REFERENCE_MAPPING_MISSING与资源耗尽独立记录；缺业务依据维持advice，不造收益。L1–L3完整>1pp门槛不变。

## 发布partial读取选择

旧defaults仍只完整ready，default_eligible不变。v2 selected_reports每binding×方向选最近完整ready；只有无ready时才选择最近非legacy、published、analysis的partial，并明确status=partial和selection_kind=published_partial_fallback。新的partial不替换已有ready；failed/interrupted/empty/legacy/评估任务不作fallback。仅更新任务明确包含的方向，不跨模型/appid/common_name/source_kind串引用。snapshot固定时选择集固定，续页使用相同snapshot；引用可在其他页，不能第一页没见就认为不存在。SSE继续原不透明游标，收到通知后重新读取v2 catalog；不要把partial伪装ready。

recommendations为空不妨碍difference-groups读取，L4/L5维持各一张卡、每类最多3代表例子；前端接入须待验收，不在本次修改。固定task读取不因新任务改变。

## 阶段计量

Telemetry version diagnostics-telemetry-2，perf_counter_ns单调时钟实测。source_initial_verification、source_verification、source_fetch、source_decode_and_identity、source_token_read_inclusive、source_preflight、low_hit_detection.l2/dynamics、low_hit_retention、low_hit_evaluation、token_detection、token_retention、token_detection_and_retention、low_hit_publication、token_proposal_prepare_evaluation、token_evaluation、recommendation_extension可按实际执行出现。

这些是嵌套阶段耗时，inclusive阶段包含子阶段，**不能相加当总耗时**；source_fetch只包取行，yield期间消费者计算不计入。source计数包含重复读取，不能当唯一请求数。没有从terminal间隔倒推耗时，不输出正文、策略JSON或异常内容。未运行阶段不伪造耗时0；通过selected_directions/coverage区分禁用、无适用工作及未完成。

本契约机器Schema见wire.json；真实create_app/TestClient例子见examples.json，源码/契约/样例摘要见manifest.json。例子来自common-v2-check4/test_v2_http_and_readonly_legacy，合成appid a、GLM-5.2、6请求、low_hit-only，展示保留截断的partial fallback，不是现场数据。原件与基线不覆盖。

# 用户监控契约2.0.0

2026-10-31，TTFT最小参考模型。运行路径仍为/monitoring/user-v2，9个操作及身份头不变。新契约号不是V1发行版本；实际OpenAPI的用户操作带x-user-contract-version=2.0.0。完整运行服务info.version仍使用既有应用版本。

[Schema](schema.json) · [设计OpenAPI](design.openapi.json) · [正反例](examples.json) · [ASGI HTTP响应样例](runtime.examples.json) · [摘要](manifest.json)。
原1.0.1的schema/examples/OpenAPI/manifest保持原位冻结；新客户端请显式选本目录。设计OpenAPI仍标设计身份，运行OpenAPI由服务生成。

## 情景联合类型

- Scenario：完整旧1.0.1形状，无timing_model；W+O口径原样读写/计算。
- BatchScenario：timing_model必须为batch_reference_total_noncompute_v1。W覆盖GF发出至首Token的全部非计算耗时；不接受overhead_seconds，包括0或null。新前端只创建此类型。
- 无tag的新简化形状、未知tag、混合新旧字段均422 INVALID_ARGUMENT；不猜测版本，不默认O。
- 情景id/revision不可变；新语义另建revision。旧快照及幂等结果不重算、不加新字段；不把旧W直接搬作新总W。

新情景必填：timing_model、scenario_id、revision、model_id、common_name、deployment（简短配置）、source、source_description、chunk_tokens、chunk_seconds。计算请求保持原EvaluationRequest，包括必填waiting_seconds；不提供等待默认值。所有数值输入保持规范十进制字符串及原长度限制。

measurement_boundary固定为GF dispatch to first token，可省略由系统补充。workload_description、thinking_mode、min/max_prompt_tokens、evidence_sha256、sample_count、calibration_notes均可省略或null。长度范围须同时有值且min≤max；未提供显示未验证，非虚构无限覆盖。

source=user_assumption不要求证明材料；实测batch τ加人工W仍为假设情景。source=verified_measurement为操作者对完整参考情景的证据声明，需要有效摘要、正样本数、范围和说明；服务只校验声明格式，不自动验证真实性，更不因提供τ或样本自动晋级。

## 计算与状态

新情景预算B=T−W；≤用floor(B/τ)，<用ceil(B/τ)−1。Cmax=min(P90,nK)，比例=(P90−Cmax)/P90。K为整个batch预算，按单请求进度近似；尾chunk按整块耗时。旧情景仍B=T−W−O。

- reference：比例可为0，不代表生产SLO保证。
- reference_with_limit/FULL_REUSE_FEASIBILITY_UNPROVEN：n=0，100%理想化参考，可行性未知。
- no_budget：新原因NONCOMPUTE_BUDGET_EXHAUSTS_TARGET；旧原因WAIT_AND_OVERHEAD_EXHAUST_TARGET。比例及计算字段null。
- unavailable/NO_POSITIVE_P90：无有效正P90。
- out_of_scope/P90_OUTSIDE_CALIBRATION_RANGE：显式提供长度范围且越界。
- 缺参/非法参数：422错误信封，不创建情景/估算，不返回假比例。

结果保存情景完整快照（新情景带tag和可选字段null），不得作为总体ΣH/ΣP达标阈值。缺失W不可转0；明确W=0有效。

## 持久化及回退

控制schema1/索引user-index-1不变，新增类型存在JSON payload内，无数据库DDL迁移。兼容方向为新代码读取旧数据；**旧二进制不保证理解含新情景的库**。回退须先备份库，使用适配前备份或保持新版只读服务，不删除/改写新旧历史以绕过版本问题。未知tag明确校验失败，不按旧模型猜测。

API路径、服务身份头、整数/比率表示、幂等冲突、GET无计算及用户/MA隔离沿用旧约定。后端软件通过不代表真实校准或前端联合验收；前端交接见[TTFT接入说明](../../../tasks/monitoring/v2-user/TTFT_FRONTEND_HANDOFF.md)。

边界修复：allowed_chunks为派生计数，2.0.0响应上限256字符，以覆盖合法128字符时间参数相除产生的至多254位整数。输入限制、其他计数限制及精确计算不变，避免合法极端参数触发序列化失败。

# 低命中后端与公共层完整自审

2026-10-31，session 01a18be2-7112-7aa2-919b-5137d1f1b1ad；本次范围为已批准的 prefix-design-0.2、LH000–LH009、公共层及 Token 消费接口。不扩展功能、不打包部署。源码修订身份 low-hit-backend-local-2；独立文件摘要见 SELF_REVIEW_CODE_IDENTITY.json，LH009 原摘要保持历史身份。

## 发现与修复

| 问题 | 影响与修复 | 验证位置 |
| --- | --- | --- |
| 取消、领取、发布之间存在读写竞态 | 任务可能在取消后发布成功，或已取消排队任务被领取。三个动作使用 SQLite 写事务，发布事务复核取消状态；终态取消不回写状态 | test_runtime_storage.py：sealing cancel、atomic claim/cancel；修复前封存竞态用例失败 |
| 最后一条变换编码后未再次检查源与取消 | 末条执行期间源发生变化或取消，evaluate_plan 仍可能给 available/after。提交评估结果前再次 verify/checkpoint | test_evaluation.py：final_request_boundary 两参数；修复前均失败，修复后通过 |
| 全范围 Plan 编译超限导致 pilot 证据丢失 | 保留已完成 pilot、完整 pilot_scope、request_keys_digest、停止 reason_codes；不能生成 full 优化卡片；非取消的局部预算失败仍可继续 Token 原始内容分析 | test_diagnostic_tasks.py：full_plan_budget_keeps_pilot_scope_and_metrics |
| Plan 大小预算两线不一致 | 低命中仅算 operation，Token 算完整 Plan。L2、动态单项和组合编译均检查完整序列化 Plan；等于上限允许，超过拒绝 | 同上：精确边界与少一字节边界 |
| L3 动态工具在不同数组位置，差异路径不完整 | 通过逻辑工具身份找回前后各自路径，comparison 保存两个路径；Plan 按每条原文实际位置修改 | test_dynamic_replay.py：reordered_dynamic_tool_has_both_paths_and_real_gain，真实 GLM Tokenizer 验证收益 |
| 请求进入前因预算停止，已检查数量少算 | 完成该请求及索引插入后才增加 checked_requests；停止时不盲减前一条已完成请求 | test_diagnostic_tasks.py：discovery_budget_before_second_request_preserves_count，两类 collector |
| 临时工作目录创建失败未归入任务故障边界 | 目录/ResultWriter 初始化纳入异常处理，失败终态无 report_ref | test_diagnostic_tasks.py：workspace_creation_failure_is_terminal |

编码预算已耗尽时，后续低命中实验明确记录 not_run 与停止原因，不再重复进入回放。pilot 选择拒绝无法表达为 SQLite 有符号 64 位上界的时间窗口；不截断或扩展源范围。

## 批准方案核对与测试覆盖

| 核对项 | 实现与覆盖 |
| --- | --- |
| 手动 appid、原因和开关；低命中先于 Token | DiagnosticSelection/DiagnosticService；contracts、diagnostic_tasks、diagnostic_http 验证矩阵、顺序、原文保持、取消后不继续、GET 不发起计算 |
| 仅目标 appid/窗口；复用统一监控编码/缓存 | source/encoding/evaluation；test_source、test_evaluation 验证 base/user_v2、封存身份、完整源、三模型及子窗重新起账，监控算法未修改 |
| L1/L3 动态字段可建议删除并给实际离线提升 | dynamic/detection/experiments；test_dynamic、test_dynamic_replay、test_experiments；业务字段无需先证明无损，仍标明假设删除；已知 cch 单独分类 |
| L2 仅同定义集合固定工具排序 | structure/service；test_l2、test_l2_replay；集合/定义变化不套用排序，重复身份不自动排序，不重排 messages/tool_calls |
| L4/L5 完整两请求证据，无收益门槛 | history/comparison；test_history、test_dynamic_replay、diagnostic_http；追加排除、JSON 数字/重复 key/数组边界、未知关联降级，完整原文而非 block 片段 |
| 完整 pilot 严格 >1pp 后 full；完整 full 严格 >1pp 才展示 | contracts 精确分数、experiments/presentation；test_contracts、test_experiments、diagnostic_tasks；等于 1pp 不通过、pilot 通过 full 不通过、失败无 after、子集指标与全范围分开 |
| 单项及组合实际回放、原文保护 | modifications/evaluation；test_modifications、diagnostic_combinations、Token real_handlers；guard/冲突/数字词法/内嵌 JSON/空操作，组合不相加，原文不就地改写 |
| 有界覆盖与恢复 | candidates/runtime/storage；runtime_limits、runtime_storage、diagnostic_tasks、Token recovery；预算 partial/停止原因、幂等、新 attempt、共享 worker 锁、封存摘要与中断 |

以上为代码与本地测试范围，不是现场质量或吞吐承诺。L1/L3 仍限已实现的日期/路径/已知 billing 语法，不宣称穷尽随机字段；缺少可靠 session/turn 时 L4 不认定同会话历史改写或 Loop；字段 Token 归属未知不伪造。现有 messages 协议边界保持。150k 现场规模、真实业务修改语义、前端展示及部署不在此次已验证范围。

## Token 接口一致性

- analysis-common-1.0 的 contracts/plugins/wire 及 diagnostics-http-1 冻结文件摘要保持一致，未原地改变 H0 或请求协议。
- H1 仍提供同一个只读原始 scope；低命中副本不传给 Token。H2 仍由公共层应用受保护 Plan、统一编码、实际回放，失败无 after；两线统一完整 Plan 字节预算。
- H3 顺序、任务状态、幂等、取消、重试及只读成果接口保持；修复的是状态事务边界。H4 按现有 Token 消费者真实测试验证，不代替其会话签署新业务验收。
- experiment 报告新增 pilot_scope、reason_codes、confidence_basis；这是附加报告元数据，不改变 EvaluationResult。pilot_scope 中计数/纳秒仍按 wire 十进制字符串；confidence_basis=pilot_gain_gt_1pp 只表示小范围已通过，不代表全范围可展示。只有现有 display_eligible 判定用于优化卡片。

## 本轮实际验证

- 联合完整集合：`pytest tests/unit/analysis_common tests/unit/prefix_analysis tests/unit/token_content tests/integration/analysis tests/integration/token_content -q`，**193 passed，228.03s**。含三个本地资源梯度、真实 Token 消费者、三模型、服务及 HTTP；固定模型资产用于 Tokenizer，不调用推理生成。
- 随后新增的 collector 请求前预算停止两个参数：**2 passed，6.88s**。初次新增测试误用了不存在的 `partial` 属性，已改为实际 `candidate_coverage_partial` 后验证；不将测试编写错误算作产品缺陷。
- ruff 检查公共/低命中及其测试通过；mypy 公共/低命中/诊断 API **24 source files 通过**；本线文件 git diff --check 通过。最终全工作区检查另发现其它会话 memory/tasks/delivery.md 的行尾空白，未越界修改。两个冻结 manifest 的源码/Schema 摘要逐项核对一致。
- 唯一测试警告为已有 Starlette/httpx 弃用提示；本轮未擅自升级依赖。

- 监控兼容：`pytest tests/unit/monitoring tests/unit/ma tests/integration/monitoring -q`，**300 passed，194.75s**，覆盖 V1/用户 V2/MA；同一已有弃用警告。

本次自审发现的上述问题已闭环，已批准范围内未发现需改变产品方案或冻结契约的重大分歧。集合有重叠时不相加宣称唯一总数；LH009 历史结果不冒充本次运行。本次资源测试重新生成 lh009/scale-*.json 工作产物，不将其中最新耗时解释为历史 RESOURCE_PROFILE 表格的原始数值或独立性能基准。

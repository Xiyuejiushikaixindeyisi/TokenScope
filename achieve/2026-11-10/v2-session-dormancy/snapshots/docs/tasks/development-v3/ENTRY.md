# 全新V3代码修复与开发会话入口

2026-11-10：角色已按用户要求登记，**实际session ID未知，待创建/启动后本人从环境登记**。这是新的开发职责，不是旧低命中后端或研究会话改名。当前阶段仅接收上下文、只读check方案；等待华为Token探索报告后细化范围/顺序/验收，再按用户安排实施。不得因角色名含“开发”就立即修改源码。

## 你的职责与边界

- 独立核对研究会话提出的四P0方向与实际源码，不照抄报告中的参数、收益或根因推断；必要时明确反对并给代码证据。
- 后续获准实施时，统一承担V3涉及的公共层、低命中私有逻辑、必要前端兼容和代码验证；旧六线休眠，不并发修改。不要让镜像打包会话承担开发、debug或开发调度。
- V3 Token异常休眠：不启动新Token异常分析/开发，旧成果可读；具体兼容和入口策略待细化。Token尾部探索只用于V3.5证据与公共能力衔接，不引入T1/新T2–T4/Agent/hybrid/SSD。
- 不修改现场数据/默认入口/批准四入口与L4/L5主体；保持统一编码和计量。冻结契约如需变化先说明兼容方案，不静默覆盖。
- 当前不启动服务、分析/压测、Docker或Git动作。实施与新版本验收规则待对应阶段适用时再读，不把历史prompt当启动指令。

## 首次阅读：只需这条链

1. 根AGENTS → [CURRENT](../../../memory/CURRENT.md) → [SESSIONS](../../../memory/SESSIONS.md) → [文档入口](../../README.md) → 本页。读取自己的CODEX_THREAD_ID/CODEX_SESSION_ID，写[本线记忆](../../../memory/tasks/development-v3.md)，未知不借用其他ID；只更新登记表自己的行。
2. [最新范围与分工](../product-v3/V3_SCOPE_AND_HANDOFF_20261110.md)：唯一当前范围权威，四P0/Token休眠/角色分工/报告依赖。
3. [修复简案](../product-v3/V3_LOW_HIT_REPAIR_BRIEF_20261110.md)：四P0含验收方向；第3节是报告局限及代码核对。P1未获本次范围认可。
4. [低命中实际报告](../../huawei/TOKENSCOPE_V3_LOW_HIT_EXPLORATION_20261109.md)：先读A、C.1/C.6、D/E，再按所核问题读其他专项。SHA `d321426897f785cf0ec2e665b5e21f1f54cd6b9478a174fad412956656882963`。报告收益未独立复核B窗，不作收益保证。
5. [本次Token探索prompt](../product-v3/HUAWEI_TOKEN_TAIL_EXPLORATION_PROMPT_20261110.md)：只了解三对象、样本/预算与单文档证据要求；新报告返回后再读报告，不替现场执行。

V2交付源码基线为c1345b6，前序本线文档检查点为fe0f23c，本次交接另有文档提交；开始时核实际HEAD和dirty，不能将文档commit误作新产品发布。原报告/映射可能仅在本机存在，缺失应说明，不猜内容或下载真实请求。

不要求读宣传故事、整份历史记忆、七方向r0、全部旧batch或上游源码。[四象限HTML](../product-v3/promotion/quadrant-detail/dist/index.html)为高优先级辅助，只在需要理解样本分布时读指定三组；不是产品前端设计规格。

## 按问题读代码与测试，不全目录通读

| 四P0/核对点 | 首选源码 | 有关测试/补充材料 |
| --- | --- | --- |
| 范围、预算与可取消 | `src/tokenscope/analysis_common/source.py`、`runtime.py`、`runtime_control.py`、`execution_v2.py`、`service.py` 的preflight/任务阶段 | `tests/unit/analysis_common/test_runtime_limits.py`；`tests/integration/analysis/test_source.py`、`test_diagnostic_resources.py`、`test_execution_v2_integration.py` |
| L1动态字段与精确改法 | `src/tokenscope/prefix_analysis/dynamic.py`、`detection.py` | `tests/unit/prefix_analysis/test_dynamic.py`；`tests/integration/analysis/test_dynamic_replay.py` |
| 候选与重复差异 | `src/tokenscope/prefix_analysis/candidates.py`、`detection.py`、`structure.py`、`recommendation_groups.py` | `tests/unit/prefix_analysis/test_recommendation_groups.py`；`tests/integration/analysis/test_recommendation_member_coverage.py`。保留L2/L3不同工具关系的比较通道 |
| pilot/样本评估/发布 | `src/tokenscope/prefix_analysis/experiments.py`；`analysis_common/evaluation.py`、`recommendation_pipeline.py`、`recommendation_publication.py` | `tests/integration/analysis/test_experiments.py`、`test_evaluation.py`、`test_recommendation_publication.py` |
| 统一计量/前端兼容（需要时） | `analysis_common/encoding.py`、`monitoring/simulation.py`；`apps/viewer/src/features/analysis/Reports.tsx`、`ExecutionStatus.tsx`、`apps/viewer/src/api/analysis/` | [公共HV2交接](../prefix-analysis/HV2_COMMON_HANDOFF_20261103.md)、[低命中交接](../prefix-analysis/HV2_LOW_HIT_BACKEND_HANDOFF_20261103.md)、[异常前端入口](../viewer/analysis/ENTRY.md)；只按影响读取冻结契约/测试 |

首次只check，不要求运行上述全部测试。后续测试计划按变更风险选择；正常负例、无收益、partial/超限和旧结果读取必须有覆盖，不降低原门槛换通过。

## 首轮check输出（短文档即可）

在本目录新增`CHECK.md`，明确：四P0哪些有代码支持、哪些需要调整；报告与源码矛盾；可能涉及公共层/契约/前端的最小范围；Token休眠与V3.5保留的兼容点；等待新报告才能决定的事项。不要提前写完整实现或冻结API/数值阈值。

重点复核：candidate_limit与max_comparisons不同；路径值不同长度不必然使text_shape不匹配；pilot可能自动进入所选scope的full；时间固定化不是无损业务修改；零Token建议与NO_CONFIGURED_RECIPES不是同一层问题。不能把未经复核的12–39pp改善当成功门槛。

维护边界：自己的记忆和本目录优先；共享文件按当前登记精确增量更新。用户确认详细方案后再开发；镜像会话只收候选作审批/打包。现阶段不得新建/唤醒其他会话或向其他chat发消息。

[可粘贴的新会话启动消息](START_PROMPT_20261110.md)

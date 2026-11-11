# 全新V3代码修复与开发会话入口

2026-11-11工作树整理者（镜像会话）同步：V3小样本已交付，现场按[华为执行说明r2](../delivery/V3_PROMPT_R2_20261111.md)复用已认可用户/MA结果，不重跑全量；五组真实异常逐一分析并展示实际方案与样本收益，不强制每组clock。现场待回传，以下原作者阶段记录保留，不将旧待打包/未实施文字当当前状态。

**当前范围决定（2026-11-11）：显式 full 延期（DEFERRED_BY_USER，未实现/未运行，不记PASS），不再是本期V3门禁；自动full仍禁止。候选repair-r1-02为LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING，独立R2已关闭RV3-01/02/03。大源自动缩样和五组session_clock样本参考率优先，真实BUS01–05及现场AC-MEM待华为验收。暂不打包。**

[本地验收收口](LOCAL_ACCEPTANCE_CLOSE_20261111.md) · [华为验收交接材料](HUAWEI_ACCEPTANCE_HANDOFF_20261111.md) · [范围差异](FULL_SCOPE_GAP.md)。

2026-11-10最新：本线实际ID **`01a1c449-6a9b-7a83-912a-5a9ff77c703d`**（环境THREAD/SESSION一致）。按用户新要求，已结合低命中与Token长尾报告完成四P0的agent开发方案r0，**两项评审修订已落实，按条件授权进入七批开发**。不再处于等待报告阶段；[独立CHECK](CHECK.md)保持历史原件。

## 当前实施入口

[评审决定与授权](../product-v3/V3_REVIEW_DECISION_20261110.md) → [两项修订核对](REVIEW_FIXES.md)：自动L1闭环必须通过，不能由指定clock实验替代；可比字段不因无关历史结构不同而失去候选资格。计划已同步，V3B001–V3B006已逐批闭环，V3B007本地LOCAL_VALIDATED；自动clock全链和大源缩样端到端通过，五组真实收益留华为验收。见[设计核对](DESIGN_CHECK.md)、[B007闭环](batches/V3B007/CLOSE.md)、[现场待验](BUSINESS_EVIDENCE.md)。

1. [用户底线与五组业务验收](ACCEPTANCE.md)：大源自动小样本完成且无mem_limit；指定五组前端有session_clock固定化与V3实算参考提升率。
2. [设计D0–D8](DESIGN.md) → [七批开发计划](BATCH_PLAN.md) → [测试T01–T30](TESTS.md)。每批有PLAN/ISSUES/TESTS/CLOSE，串行验证闭环后推进并增量记忆；B001组件已闭环（46项测试通过），B002代码门禁已闭环（111项回归、最终39项资源测试），B003–B007及R1修复已完成本地验证并经独立R2复核；显式full设计缺项与五组现场验收不计通过。
3. [报告证据核验/勘误](EVIDENCE_REVIEW_20261110.md)：只采用公共能力输入，Token私有修复仍留V3.5；旧收益不当验收保证。
4. [本线最新记忆](../../../memory/tasks/development-v3.md)：当前状态与后续依赖。当前获准本地代码开发和验证，实际实施/测试结果见每批记录；不含镜像打包、现场部署或新现场数据访问，不跨会话派发。

## 你的职责与边界

- 独立核对研究会话提出的四P0方向与实际源码，不照抄报告中的参数、收益或根因推断；必要时明确反对并给代码证据。
- 后续获准实施时，统一承担V3涉及的公共层、低命中私有逻辑、必要前端兼容和代码验证；旧六线休眠，不并发修改。不要让镜像打包会话承担开发、debug或开发调度。
- V3 Token异常休眠：不启动新Token异常分析/开发，旧成果可读；具体兼容和入口策略待细化。Token尾部探索只用于V3.5证据与公共能力衔接，不引入T1/新T2–T4/Agent/hybrid/SSD。
- 不修改现场数据/默认入口/批准四入口与L4/L5主体；保持统一编码和计量。冻结契约如需变化先说明兼容方案，不静默覆盖。
- 本地开发/合成验证按七批授权执行，新版本真实E2E遵守唯一候选冷启动规则；镜像/现场不启动，不用历史prompt扩展授权。

## 后续恢复的最小阅读链（首轮已完成）

1. 根AGENTS → [CURRENT](../../../memory/CURRENT.md) → [SESSIONS](../../../memory/SESSIONS.md) → [文档入口](../../README.md) → 本页。已有身份与权责登记保持，必要时复核环境；本轮共享表由研究会话汇总，不并发修改。
2. [最新范围与分工](../product-v3/V3_SCOPE_AND_HANDOFF_20261110.md)：研究归口的四P0/Token休眠/角色分工；最新用户底线及详细设计以本页顶部评审包为准，不以旧等待报告状态覆盖。
3. [修复简案](../product-v3/V3_LOW_HIT_REPAIR_BRIEF_20261110.md)：四P0含验收方向；第3节是报告局限及代码核对。P1未获本次范围认可。
4. [低命中实际报告](../../huawei/TOKENSCOPE_V3_LOW_HIT_EXPLORATION_20261109.md)：先读A、C.1/C.6、D/E，再按所核问题读其他专项。SHA `d321426897f785cf0ec2e665b5e21f1f54cd6b9478a174fad412956656882963`。报告收益未独立复核B窗，不作收益保证。
5. [本次Token探索prompt](../product-v3/HUAWEI_TOKEN_TAIL_EXPLORATION_PROMPT_20261110.md)：三对象、样本/预算与单文档证据要求；报告已返回并核验，优先读本轮证据核验及所引原章节，不替现场执行。

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

## 首轮check要求（已完成，保留检查范围）

在本目录新增`CHECK.md`，明确：四P0哪些有代码支持、哪些需要调整；报告与源码矛盾；可能涉及公共层/契约/前端的最小范围；Token休眠与V3.5保留的兼容点；等待新报告才能决定的事项。不要提前写完整实现或冻结API/数值阈值。

重点复核：candidate_limit与max_comparisons不同；路径值不同长度不必然使text_shape不匹配；pilot可能自动进入所选scope的full；时间固定化不是无损业务修改；零Token建议与NO_CONFIGURED_RECIPES不是同一层问题。不能把未经复核的12–39pp改善当成功门槛。

维护边界：自己的记忆和本目录优先；共享文件按当前登记精确增量更新。用户确认详细方案后再开发；镜像会话只收候选作审批/打包。现阶段不得新建/唤醒其他会话或向其他chat发消息。

[原接入启动消息](START_PROMPT_20261110.md)已执行，不因再次读到而重复启动；[V2低优先级归档](../../../achieve/2026-11-10/v2-session-dormancy/README.md)供按问题追溯，当前仍以本页及用户最新安排为准。

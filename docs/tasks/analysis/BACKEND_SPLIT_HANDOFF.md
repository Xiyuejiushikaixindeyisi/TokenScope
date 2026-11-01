# 异常分析后端分线交接

2026-10-31最新恢复入口：用户已认可[prefix-design-0.2](../prefix-analysis/DESIGN_REVISION_20261031.md)，主会话形成[LH000–LH009计划](../prefix-analysis/BATCH_PLAN.md)及[H0–H4实施接口交接](BACKEND_IMPLEMENTATION_HANDOFF.md)。全部planned，暂不编码。公共当前为draft-2，接纳Token TA-C0.2协议方向；实际版本/签收依实施交接逐项记录。下方fork历史和0.1/draft-1描述仅保留追溯，不作为最新开发入口。

2026-10-31。用户明确“产品设计审批通过”，指定当前会话继续低命中率分析后端设计和开发，fork会话负责Token异常分析后端设计和开发。材料完成后已获用户明确允许；本轮已执行fork、登记并发送启动prompt，当前主会话继续低命中详细设计。

## 1. 审批基线与当前状态

已批准产品基线为v0.4：[总览](PRODUCT_PROPOSAL.md)、[低命中L1–L5](LOW_HIT_DETECTORS.md)、[Token内容T1–T4](TOKEN_CONTENT_DETECTORS.md)、[流程与评估](PHASE1_PLAN.md)、[业务样例](DISPLAY_EXAMPLES.md)及[字段逻辑草案](RESULT_FIELDS_DRAFT.md)。产品批准不等于字段已成为冻结API或详细开发计划已经完成；不重复申请产品审批。

两线职责已由用户指定。当前fork交接已完成，两线正在分别形成后端详细设计、接入契约和开发/验证计划，再按项目工作流推进实现。本轮未启动源码修改、Git分支、打包或部署。

| 会话 | 实际身份 | 当前状态 | 职责 |
| --- | --- | --- | --- |
| 当前主会话 | 01a18be2-7112-7aa2-919b-5137d1f1b1ad；环境THREAD/SESSION ID一致 | 低命中后端详细设计中；fork已获准并完成 | L1–L5设计、实现、测试及本线后端交接；维护两线共用产品入口 |
| Token异常fork会话 | 01a18fcd-0464-7cf1-b435-4f394bd33e66；fork工具返回实际threadId | 已创建并发送启动prompt；active，子会话环境身份已复核，详细设计中 | T1–T4内容分析、修改评估接入、测试及本线后端交接 |

## 2. 各自入口

| 方向 | 当前任务入口 | 长期记忆 | 启动/恢复prompt |
| --- | --- | --- | --- |
| 低命中后端 | [ENTRY](../prefix-analysis/ENTRY.md) | [prefix-analysis](../../../memory/tasks/prefix-analysis.md) | [主会话prompt](../../../prompts/sessions/LOW_HIT_BACKEND_START.md) |
| Token异常后端 | [ENTRY](../length-analysis/ENTRY.md) | [length-analysis](../../../memory/tasks/length-analysis.md) | [fork prompt](../../../prompts/sessions/TOKEN_ANOMALY_BACKEND_FORK_START.md) |

analysis目录继续作为已批准产品和两线交接入口；具体技术设计/代码地图/计划/验证分别落在各自任务目录。length-analysis路径保留兼容，不把本线缩减为长度阈值，也不扩展为过程检测。

## 3. 维护边界与接口责任

| 范围 | 单一维护方 | 协作方式 |
| --- | --- | --- |
| L1–L5规则、前序对照、前缀证据、对应修改方案与测试 | 当前低命中后端 | Token线只消费已约定证据/类型，不改其规则 |
| T1–T4规则、内容度量、重复载荷/策略判定、对应修改方案与测试 | Token异常fork会话 | 低命中线不代写Token规则 |
| 两线共用分析结果模型、请求范围/来源引用、离线评估公共封装的设计与集成 | 当前低命中后端作为单一维护方 | Token线在本线设计写所需输入/输出和问题，复用确定版本；不另造第二套公共回放/结果存储。具体源码路径在详细设计时登记，当前未占用源码 |
| Tokenizer/Template、J/P/H/C及缓存算法 | 原监控公共能力维护方 | 两线复用同一实现；接口不足登记用例/缺口，不能私改冻结口径或直接复制算法 |
| 公共API装配、CLI/worker、共享配置/锁文件 | 实际修改前登记唯一编辑窗口 | 低命中线协调分析接入；须复核现有监控维护方状态，不凭本文件自动占用 |
| analysis共同产品文档/总交接 | 当前低命中主会话 | Token线维护本线文档和自己的session状态；产品语义变更单列，不静默覆盖已批基线 |
| 前端、部署、镜像/交付包 | 原指定会话 | 本次两线不接管；打包仍需另行授权 |

两线可并行做本线设计与独立规则。直接依赖的公共契约须核对版本/签收；契约尚未固定时可用明确标记的草案/样例推进设计，不把样例当真实联调。共享代码、索引、配置修改前重读最新SESSIONS，登记路径、唯一维护人和影响，避免同工作区覆盖。

## 4. 不得回退的产品决定

- 只分析/回放目标appid、同服务/编码身份、明确窗口。原运行窗口与子窗口重算基线分开；不回放其他appid。
- 模型配置/模板参与属于内部校验；不生成用户改模型配置的业务异常，不恢复固定探测优先级。
- 已知误注入cch清理按业务信息无损处理；同集合/定义工具固定排序按稳定化修复；裁剪业务内容另列条件。
- 内容负担、优化机会、超出明确业务约定分开；无业务上限不编造Token异常阈值。
- 正常append-only历史不报重复浪费；缺可靠关联不推断同一会话、Loop或执行次数。
- 只改原请求结构副本，统一编码；展示P/H/C/R，零/负收益保留；组合需独立实际评估。
- 页面GET只读保存结果。Loop/失败重试/子agent分析仅保留数据需求，不实现新采集或自进化Agent。
- PrefixLens仅参考，原始证据不改；示例为构造，不能用作现场效果证明。

## 5. fork授权与登记流程

1. 本轮完成文档后向用户询问是否执行fork。在明确同意前，不调用fork/create、不发子会话启动消息。
2. 获准后从当前实际会话fork一次Token异常会话，默认沿用同项目目录，不额外创建worktree。
3. 以工具返回的真实child threadId登记SESSIONS、Token线ENTRY和记忆；如暂时只有请求标识，记录“创建中”，不可当作最终session ID。父会话ID保留不变。
4. 为新会话标注Token异常后端角色，并将已准备的fork prompt作为明确启动任务发送；这是用户批准fork分工后的启动步骤，不创建额外子Agent。
5. 子会话启动后核实自身实际ID、工作目录和角色；与工具记录不一致则先核对，不能继承父ID。更新当前阶段/任务，不代签另一线完成或审批。
6. 主会话更新共同入口和记忆，之后继续低命中后端设计。新会话接管自己的Token线文档/记忆。当前“未知/未创建”仅在得到真实创建结果后替换。

许可状态：**用户已明确允许，2026-10-31 same-directory fork成功，子会话ID 01a18fcd-0464-7cf1-b435-4f394bd33e66，同步完成。已发送启动prompt；wait_threads确认active/inProgress，子会话已核实自身环境ID一致。**

低命中主会话已形成[prefix-design-0.1](../prefix-analysis/DESIGN.md)和[analysis-common-draft-1](BACKEND_COMMON_CONTRACT_DRAFT.md)，技术草案未冻结。Token线维护本线接口需求，公共草案由主会话维护；当前不占用业务源码。

# Token后端设计与公共draft-2对齐修订

> 2026-10-31最新批准范围：[TA-S1](SCOPE_REVISION_T234.md)移除Token T1，保留T2–T4编号；工具定义归低命中现有一致性/漂移职责，不增长度精简。当前新设计/计划/推荐/视觉验收仅T2–T4；旧源码及TA000–006历史仍含T1，不冒称已删除。当前实施计划见[BATCH_PLAN_ARTA](BATCH_PLAN_ARTA.md)，三卡样例见[AR-T3](FRONTEND_REWORK_EXAMPLES_ART3.json)。本轮仅文档同步，暂不编码打包部署。

版本TA-D0.3，2026-10-31。用户确认低命中后端设计已审批通过，并授权本轮对比优化；本修订为Token线技术修订，尚不代表用户批准实施。未编码。对应[公共draft-2](../analysis/BACKEND_COMMON_CONTRACT_DRAFT.md)第9节及[低命中prefix-design-0.2](../prefix-analysis/DESIGN_REVISION_20261031.md)。与本线旧DESIGN、TA-C0.2、TA-I0.2、批次描述冲突时，以本文为准；不修改公共方文档。

## 1. 对比结论与调整依据

| 核对项 | 旧Token设计/与低命中差异 | 本次调整与依据 |
| --- | --- | --- |
| 公共接纳 | 仍记录三项协议等待接纳 | draft-2第9.2节已明确接纳内嵌JSON外层替换、三层证据身份及单插件；更新为双方技术方向已核对，正式Schema/联调仍未完成 |
| 启动入口 | 只有显式分析，没有人工原因到两方向的路由 | 采用第9.1节reason_codes/reason_note及两个显式开关；不从长度/QPS/命中阈值自动触发 |
| 方向顺序 | 插件独立性未与任务顺序区分 | 含low_hit时低命中探测及其pilot/full终止后才运行Token；独立模块不意味着默认并行 |
| 检查算法 | 低命中跨请求查找更早对照，Token主要单请求内容分析 | Token保持逐请求提取、四规则共享单元；不强加前序对照、LCP或同session前提，依据T1–T4已有产品范围 |
| 分析输入 | 未明确前一方向评估是否传递修改后正文 | 两方向均读冻结的原始scope；低命中实验副本不成为Token默认输入。收益组合必须另建明确计划，依据公共不可变RequestView与组合独立评估原则 |
| 展示门槛 | 旧设计未处理低命中新增过滤 | >1pp仅用于低命中优化卡片；Token事实/机会/策略违反及评估结果不继承门槛，依据第9.3节 |
| 完整证据 | 有位置/片段，缺完整JSON读入口要求 | 每项内容证据关联完整原文身份和受报告范围约束的读取引用；T3默认同请求多位置，不能伪造两条请求对照 |
| 修改评估 | 显式选择内容方案后全窗口评估 | Token继续要求确切保留/替换参数；不默认自动删除或强制pilot。screen_then_full仅驱动低命中链，依据第9.1/9.3节对Token的区分 |
| 失败及未开始 | 主要规则状态，缺跨方向状态 | 采用direction_status/stage_status；规则不足与方向失败、共享源错误和中断分别处理 |

参数错配保持[独立研究](PARAMETER_MISMATCH_RESEARCH.md)，不增加探测器、入口原因或生成参数修改能力。

## 2. 公共入口与Token执行流程

人工选择源run/服务/appid/窗口及原因后，公共层校验原因与开关一致性。含low_hit：enable_low_hit=true、enable_token_content=true；仅request_length/qps：false/true。未知原因或冲突拒绝，不能推测用户意图。QPS只是调查入口，报告应明确首期只分析内容，不能解释实际Loop/调用频率原因。

含low_hit的任务顺序为低命中检测→其候选pilot→合格候选full→Token分析。低命中无发现、partial或方向级失败达到终态后仍可继续Token；仍有排队评估时Token为not_started/waiting，不能显示无问题。共享源摘要/资产等必要身份失配或用户中断则停止后续，说明阻断原因。具体任务枚举由公共Schema统一，本线不另设调度器。

Token阶段：读取同一原始scope → 逐请求完整原文校验 → 一次提取内容单元 → 运行所选T1–T4 → 保存规则状态与证据 → 归组发布Token报告。四条规则没有原因优先级，不能首个命中就停止；预算不足保留实际检查范围。T3同请求精确比较，T4单快照历史位置清单，均不要求真实session。

低命中可提供已保存的参与证据/位置引用作为可选公共事实；必须校验同RequestKey、原文摘要、模板/选项及方法版本。没有这些证据也能生成内容事实。Token不得依赖prefix_analysis内部类或重新执行低命中规则。

## 3. 证据与业务展示

报告保留reason_codes/reason_note、scope_ref、方向/阶段状态、规则版本、检查覆盖及未检查原因。内容卡片分为内容负担、优化机会、违反明确业务策略；大内容本身不是异常。

| 展示层 | 必需字段/内容 |
| --- | --- |
| 业务结论 | rule_id、结论类别、涉及请求并集数、观测值/单位、policy_ref或缺失原因、建议及前提 |
| 定位证据 | location_id/unit_id、RequestKey/raw_sha256、source_pointer、embedded_pointer、精确比较方法、父子/重叠关系 |
| 全文入口 | 完整原文读取引用及complete状态；preview单列truncated，不能用片段代替完整JSON。读取严格限本报告scope |
| 输入参与 | included/ignored/unknown及方法/模板身份；精确Token区间可空，字节不充当Token贡献 |
| 修改对比 | plan_ref、原值guard、确切参数、action_class、被移除/替换内容引用、内层操作及前后完整副本身份 |
| 评估 | not_run/blocked/available及原因、scope与modified_subset、基线来源、前后P/H/C/R与差值、manifest和限制 |

T2/T4引用同一unit且保留不同解释；T3展示同一请求的多个实际位置。低命中L4/L5需要两个请求的完整对照，这个要求不机械复制到所有Token发现。普通源码JSON对比和解析结构视图均保留原文身份，格式化视图不覆盖原证据。

Token报告不使用低命中的pilot_high_confidence标签，也不填gate_threshold_pp=1。建议以direction与展示类别决定展示语义；若公共Schema要求gate字段，Token使用not_applicable/null并注明not_applicable_token_content，不能借填true模拟过门槛。该具体wire表示仍待Schema固定。

构造展示样例：T2发现结果含10,000行，无保留策略时显示已观测大小与“未评估：缺少保留参数”，提供完整请求及结果路径。T3发现同文档在tool返回和arguments内各一处，显示两位置相等证据，不称重复执行。T4按指定策略裁剪后即使P下降而C上升，仍展示评估及不利指标，不按ΔR≤1pp隐藏。样例无实测数值。

## 4. Token离线评估语义

一次诊断提交自动驱动的是已具体化低命中候选的两阶段实验；Token报告中的候选默认待确切参数。已有准确保留策略可产生可执行候选，但不因为evaluation_policy=screen_then_full就自动套用低命中删除假设或调度Token实验。用户显式创建内容Plan并执行评估，不需要另加逐项审批环节。

Token默认对选定appid原scope执行全窗口比较，包含未修改请求；完整原run模式核对原H/C，子窗口前后同空起点重算。评估stage与scope明确，Token全窗口结果不代表通过低命中pilot。若公共stage仅提供pilot/full，Token使用full并记录直接显式评估、无pilot引用；若Schema采用其他名字，由公共方固定，语义不得改变。

复用TA-C0.2原值保护、内层一次编译和公共原子应用；保持原effective_options。任何目标失败则blocked且无after/收益；not_run不是0。P/H/C/R均来自统一编码/缓存算法；原O只作背景，生成Token、质量、费用及真实执行数不预测。

单项L类与T类结果不能相加。跨方向组合需明确共同原scope、操作次序及冲突检查，生成新组合Plan并真实评估；不把低命中修改后请求自动继续交给Token形成隐式累积。相同外层不同替换或父子覆盖/移动冲突不自动重定位。跨方向组合的默认展示分类/调度不在本轮扩展：未被公共Schema明确支持时保留不可执行原因，不擅自复用低命中门槛过滤Token报告。

## 5. 接纳状态与工程剩余

Token线本轮接受draft-2第9节的方向路由、阶段串行、六项公共类型语义及低命中门槛不作用于Token的边界。公共方已接纳TA-C0.2的三项协议，无需再将其写成等待原则性批准。

尚未完成：正式Schema/OpenAPI与元数据编码样例、版本化registry/handler实际类型、完整原文/修改副本读取约束、Token无gate及直接full的wire表达、资源预算校准、真实公共服务与联合验证。用户批准低命中设计不等于这些实现已存在，也不等于本线已获开发授权。

后续按更新后的[分批计划](BATCH_PLAN.md)实施；本轮仅设计及记忆更新，无源码/业务测试/打包/部署。

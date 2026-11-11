# REPAIR_R1 ISSUES

RV3-01/02/03复现确认；源码修复已完成，最终真实浏览器/全回归VERIFYING，不标独立验收通过。

| ID | 首次失败/根因 | 修复与复验 |
| --- | --- | --- |
| RV3-01 | 仅ClockFinding进入新评估，非clock规则断链 | PrefixFinding3/PrefixRecipe3、逻辑字段key、原dynamic_recipes/受控compile接入。普通日期/path/CCH正常worker已通过，现场收益仍未验。 |
| RV3-02 | L2/L3仅cause；空工具/无交集被筛掉 | sort_tools/description动态recipe实算；工具存在性fallback，空/增删证据；不造增删变换。正常worker已通过。 |
| RV3-03 | 新组无原文对照 | 去重原文registry、稳定请求对/hash、schema/UI完整JSON对照；L5专用负载已通过worker，浏览器待完成。 |
| R1-04 | attempt02四项wire失败；联合类型先选Clock分支，slot_index未恢复 | wire_v3按required/const/enum选择分支，H0不改；attempt06七新场景正常API通过。 |
| R1-05 | attempt04四项clock API Pointer失败 | 原逻辑字段key误传RequestComparison Pointer，改实际comparison差异路径；attempt06原clock回归通过。 |
| R1-06 | attempt04 CCH找不到输入失配 | 构造CCH原文不同但输入ID相同；不是强造失配。新增source_change_input_identical，允许原文改法实算而显示真实结果；attempt06通过。 |
| R1-07 | attempt03三旧前端fixture缺新增可选evidence_requests | 按旧schema默认空集合并提示缺完整对照，attempt05旧5通过，attempt07全352通过。 |
| R1-08 | 完整原文和代表对可能放大报告 | 每规则128独立原因组、原文元数据四分之一上限、去重与预算前置；截断显式不伪装完整，新增边界单元。 |

显式full UNIMPLEMENTED_DESIGN_ITEM：无最新用户取消依据；等待范围裁定，不以该遗漏偷偷重启自动full。B002历史证据事故/原跳过测试等记录继续保留。

R1-09 自检截图发现L2 recipe组与旧摘要重复、L5完全相同原文对在重复请求中重复展示。删除L2重复摘要；仅当两个完整原文SHA集合完全一致时共享代表证据、成员并集去重，不推断session，不合并不同上下文。新增正常worker单组/8成员断言；需要新候选复验。

R1-10：新编译器分派后旧SimpleNamespace单测不再模拟ClockFinding，导致7项状态测试调用错误编译器；修正最小类型替身且扩展两分派，attempt10/11全部通过。最终去重R1-09由正常worker单组/成员断言、真浏览器截图及独立核算验证。

RV3-01/02/03本线FIXED_VERIFIED：最终10正常页面+38定向+9窗独立oracle+重启10报告证明；不是独立验收签字。R1-04/05/06/07/08/09/10定向闭环。全pytest895/7只有旧替身七项，最终完整unit复验仍收尾。显式full和华为五BUS保持未实现/现场待验。

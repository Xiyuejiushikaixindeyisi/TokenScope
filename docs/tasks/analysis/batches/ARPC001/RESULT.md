# ARPC001 方案与差异归组

2026-10-31，公共提供方本批核心实现/测试完成；原任务装配与全链验收在ARPC004/006继续，不代签Token消费者。

recipe按规则版本和完整recipe_json归组，不能只按规则/工具名。L1–L3只关联本组Finding引用的完整full/direct_full；组合评估不得借给单项。修改数来自Evaluation modified子集，不用操作/观察数冒充。低命中优化卡仍严格>1pp。L4/L5保留精确上下文、不同上下文不合组，定位不明时独立保留发现；成员请求按RequestKey并集。

新增recommendation_grouping.py、prefix_analysis/recommendation_groups.py、recommendation_projection.py。30观察/6请求、不同recipe/上下文不混、未完成覆盖保留单元通过；实际GLM-5.2原scope任务回放→投影推荐测试通过（test_recommendation_publication，1 passed / 7.04s），有真实收益卡且N与modified一致。非线上业务收益承诺。

修复：projection的RequestKey/str变量复用、Literal类别类型；相关mypy通过。公共与低命中82单元通过（含ARPC002新边界）。后续继续整体状态/新API验证，不停等批次批准。


## 最终联合闭环

2026-10-31：本批实现已纳入ARPC006当前源码联合验证与实际HTTP交接，详见[最终验收](../ARPC006/RESULT.md)。上文阶段性待项由最终记录覆盖，不将早期测试当新功能签收。

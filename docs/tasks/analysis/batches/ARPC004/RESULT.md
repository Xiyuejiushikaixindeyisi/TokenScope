# ARPC004 自动评估阶段记录

2026-10-31。公共编排已加入同一诊断：低命中→原请求Token fragment→完整提案扫描→按recipe归组→逐方案prepare→完整Plan→原scope direct_full→推荐/例子封存。新功能通过显式RecommendationSettings启用；bootstrap装配与HTTP仍在后续批次。旧service调用兼容。

真实Token adapter及GLM-5.2回放测试3 passed / 8.59s：不同依据相同操作独立prepare后复用1次评估（两推荐、3/3实际修改）；缺依据完整advice；max_proposals=2导致3请求范围partial且不回放；幂等不取变更后的配置。构造策略不代表实际业务授权。

校验prepared目标RequestKey/raw_sha，拒绝工具定义修改、冲突/重叠；复用按完整操作规范化字节比较，仍保存prepared/execution/evaluation各自引用。已有TaskControl全任务encoding预算继续使用；新proposal/plan/evaluation预算独立明确。后续补边界、取消、失败、真实T3/T4及整体兼容后最终验收，本记录不是ARPC006通过。

修复类型推断和循环变量复用，移除Pydantic实例model_fields废弃用法。无正式前端/打包部署。


## 最终联合闭环

2026-10-31：本批实现已纳入ARPC006当前源码联合验证与实际HTTP交接，详见[最终验收](../ARPC006/RESULT.md)。上文阶段性待项由最终记录覆盖，不将早期测试当新功能签收。

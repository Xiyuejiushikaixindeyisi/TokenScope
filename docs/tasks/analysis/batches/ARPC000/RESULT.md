# ARPC000 公共契约提供方记录

恢复实施补充：类型错误修复、T2–T4源码/Schema一致和4正5反例完成，公共/低命中81 passed / 0.71s，7个相关源码模块mypy通过。提供方适配器交接可消费：[当前身份](../../../prefix-analysis/ARPC000_CONSUMER_HANDOFF.md)。Token实际消费者签收待其本线记录；新HTTP未完成。此前保存点不再是停工理由，继续后续批次。

2026-10-31。用户已授权ARPC000–006逐批实施。实际session 01a18be2-7112-7aa2-919b-5137d1f1b1ad，环境THREAD/SESSION一致。公共Schema/适配器协议/独立存储入口已实现，Token消费者运行时签收待其本线执行；不代签。

新增recommendations.py、proposal_plugins.py、recommendation_store.py、recommendation_reasons.py与独立export脚本。机器Schema及准确方法签名见[交接入口](../../../../contracts/analysis-recommendations-1/README.md)。没有修改H0四方法、旧ItemKind、Token私有源码或正式前端。

验证：`.venv/bin/pytest tests/unit/analysis_common -q`，63 passed / 0.90s；本批4个公共源码模块mypy通过。首次静态检查发现Literal类型与Optional引用问题，已修复；ruff格式和导入修正完成。测试包含wire十进制往返、非法版本/计数、跨scope/task证据、T3无Finding、真实Observation关系和legacy存储。新摘要由导出脚本生成。

工程补充：propose明确新增task_id输入；Schema将recipe及EvaluationResult嵌套保存，展示变化值后续派生，避免重复字段分叉。不是业务取舍变化。

当前限制：尚未实现推荐HTTP和自动链路；后续批次需补全面available/预算/端到端边界。Token adapter暂无已核实实现，不可声称已联合通过。继续ARPC001，不请求重复开发许可；不打包部署。


## 最终联合闭环

2026-10-31：本批实现已纳入ARPC006当前源码联合验证与实际HTTP交接，详见[最终验收](../ARPC006/RESULT.md)。上文阶段性待项由最终记录覆盖，不将早期测试当新功能签收。

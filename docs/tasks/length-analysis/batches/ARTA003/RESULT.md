# ARTA003 — 真实公共自动链路消费者验收

2026-10-31，本线消费者闭环。复用公共 RecommendationSettings/DiagnosticService/worker；无独立 Token worker，无前端参数。

测试 tests/integration/token_content/test_auto_recommendations.py：T2/T4 及 T3 两种授权方案均通过实际编码、同报告 Plan/Evaluation/Recommendation 封存。T3 对 DEFAULT_SETTINGS 三套固定模型逐一真实回放；输入 CSV 含 a/b/a，scope 仅 appid=a 的两请求（M=2）。定义摘要、业务依据与修改参数从后台固定配置读取。

已验证：实际 raw 改变 N 与 matched 数区分；noop N=0且P不变；负收益仍 token_evaluated；缺依据 N=null、无 Evaluation；不同依据独立 prepared_plan、同操作共享 execution_plan/evaluation；局部例子真实源位置；Observation 可无 Finding；输入库摘要不变；新 fragment 只T2–T4。没有合并不同方案的收益。

本线4项真实自动集成测试独立首次 23.05s 通过，补HTTP/discovery/预算后随最终162项回归全部通过。运行证据与样例见 [ARTA004](../ARTA004/RESULT.md)。全部业务配置/引用是 synthetic fixture；真实指编码资产和程序链路，不是生产授权或生产收益。

范围：本线消费已验证，公共整体算法/跨方向组合/监控兼容的完整审查仍由公共维护方单独负责；前端视觉与最终端到端验收由前端会话负责，不能以本线结果代签。

追加真实边界：P1026→1022但C642→766，N=2，自动报告不隐藏；详见ARTA004增量验收。

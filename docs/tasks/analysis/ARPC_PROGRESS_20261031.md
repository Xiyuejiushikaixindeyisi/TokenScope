# ARPC 本轮保存点与真实验证

2026-10-31最终实施入口：docs/tasks/prefix-analysis/FRONTEND_REWORK_IMPLEMENTATION_HANDOFF_ARL3.md；验收：docs/tasks/analysis/batches/ARPC006/RESULT.md。下文为设计/阶段保存记录，旧暂停、未实施或待项不覆盖最新实际交付。

2026-10-31，session 01a18be2-7112-7aa2-919b-5137d1f1b1ad。先按用户直接授权开展公共实现；后因跨会话范围/阶段指令经原始时间核对，前端要求本轮仅范围同步并等待统一阶段答复，当前暂停继续编码，见[范围回执](../prefix-analysis/SCOPE_T234_ACK.md)。不是每个小批要求重批授权；已授权计划保留，不宣称七批完成。

| 批次 | 实际状态 | 尚缺 |
| --- | --- | --- |
| ARPC000 | 已有推荐/依据/提案/预算/局部证据/差异/summary模型，静态adapter协议、真实fragment关系校验、typed extension writer、reason分类和独立导出器；旧三个manifest共13文件一致 | T2–T4范围修订后源码/机器Schema重新一致、完整正反fixture及消费者签收、最终冻结 |
| ARPC001 | recipe确定性归组、L4/L5精确上下文归组；30观察→两组、6请求并集边界已单测 | 新低命中结果映射模块尚有2个mypy错误、尚未接入原任务封存；完整收益/引用/跨task测试待补 |
| ARPC002 | 无损JSON pointer定位、转义字符串映射、内嵌JSON、codepoint、大整数/重复key/64k片段基础已单测 | 完整text_range映射、安全截取及每组字节/3例预算、例子持久封存/真实任务联调待补；不可宣称全面闭环 |
| ARPC003–006 | 未开始实现 | Token真实adapter/构造策略、公共快照配置、自动回放/预算、GET、真实模型任务及联合消费者验证 |

实际执行：公共新增契约首轮7 passed；扩展校验后公共单元63 passed / 0.90s；归组/定位加入后 `.venv/bin/pytest tests/unit/prefix_analysis tests/unit/analysis_common -q` 为80 passed / 0.62s。对应各阶段新增模块ruff/mypy通过。旧common/http/discovery manifest共13文件字节核对一致。不能把80项解释成最后所有源码通过：后续recommendation_projection.py的最后mypy失败2处（key变量类型复用），未运行新端到端回放。

暂存源码：analysis_common的recommendations、proposal_plugins、recommendation_store、recommendation_reasons、recommendation_grouping、evidence_locator；prefix_analysis的recommendation_groups、recommendation_projection；三个新增单测文件和export_recommendations_schema.py。没有修改原service/app/CLI/冻结协议源码，无新增任务或服务启动、无Git提交/推送、正式前端/Token私有源码/打包部署未动。

新Schema当前文件摘要：internal.json `961c815a594220a81ebce54d1791965c767240b56aa73e5b0b429c1ab21b0006`；wire.json `1727a3111aa5f8154ae42911519eadf51497be3f7a2b1395780e94d25b794bea`。它们是T1退出前导出物，当前源码工作稿已有范围修订而未重新生成，**只作交接工作稿，禁止正式消费或宣称冻结**。旧manifest保持身份；本次停止后只改文档/记忆，不更新生成物。

恢复顺序：先确认统一阶段→修复key类型问题并完成T2–T4源码/Schema一致性、正反fixture→Token消费ARPC000→补齐ARPC001/002原任务集成和边界→按原计划003–006推进。配置缺失用构造策略验证工程，但不代签真实业务授权。Token新规则仅T2–T4，工具定义不新增精简职责。

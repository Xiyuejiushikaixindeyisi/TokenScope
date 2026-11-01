# TA000 接入基线核对

> 最新：TA000 closed。H0提供方消息已接收，analysis-common-1.0五份manifest摘要及internal/wire全部模型Schema核验通过；新增16项消费检查，与原11项共27 passed，ruff通过。接收对象为contracts.py/plugins.py/wire.py与冻结Schema，非HTTP/真实来源/评估已完成。开始TA001，不再等待H0。

## H0最终接收

公共实际类型采用RequestView、AnalysisFragment、PluginDescriptor/Selection、EvidenceCapabilities、RunControl及MutationPreparation；插件四个调用面以AnalysisPlugin Protocol为准。prepare_mutation返回prepared+operations或blocked+无operations，载荷用不可变JsonText。所有整数wire经公共to_wire/from_wire，内嵌JSON数字不转换。固定正式版本analysis-common-1.0；源码/Schema摘要由docs/contracts/analysis-common-1.0/manifest.json逐项测试核实，不以旧HEAD代替工作树身份。

Token评估使用stage=direct_full，gate_passed=null。display_eligible属性是低命中卡片资格，Token恒false不代表隐藏Token报告，TA005必须按direction展示。H0尚不提供报告全文HTTP；其scope约束按draft-2保留给H1/H3b验收，不阻断纯规则。Participation目前按source_pointer传入，内嵌子字段不得继承父字段精确spans；缺少匹配身份时unknown。

本轮新增test_h0_consumption.py，执行pytest tests/unit/token_content -q（27通过），ruff check tests/unit/token_content（通过）。这不是插件业务或真实服务联调；H1–H4仍由对应批次交付。下文初始awaiting记录保留为先前检查结果，已由本节覆盖。

2026-10-31。用户已批准TA-D0.3与TA-B0.2，并授权从TA000逐批实现验证后继续。状态：started / awaiting_complete_H0，未closed。已新增本线公共类型消费测试，未实现探测器、打包或部署；参数错配保持独立研究。

## 实际核对

- 已读取最新AGENTS、CURRENT、SESSIONS、本线入口、公共draft-2及[AH-P0.1实施交接](../../../analysis/BACKEND_IMPLEMENTATION_HANDOFF.md)。
- 公共维护方明确为低命中主会话01a18be2-7112-7aa2-919b-5137d1f1b1ad；其LH000交付H0，Token TA000接收。当前交接表H0仍planned，正式Schema/插件版本未提供。
- 首次目录搜索未见公共包，随后复核发现公共会话新增analysis_common/contracts.py，显式标注Initial LH000、未冻结。目前含RequestKey、DiagnosticSelection与InputMetrics；未提供完整RequestView/Plan/插件registry。新增消费测试核对已有类型，不据此关闭H0。
- draft-2已接纳三项设计方向，属于技术语义确认，不等于类型、编码规范或插件实现已存在。
- 共享工作区有其他会话大量未提交改动，未暂存、覆盖、切换分支或改公共源码。

## H0待接收清单与确定验收预期

| 交付 | 本线接收标准 | 当前状态 |
| --- | --- | --- |
| 正式契约版本、Schema文件及摘要、类型导入路径 | 与draft-2及TA-D0.3一致；输入/结果明确可空性与十进制字符串wire | 未提供 |
| RequestKey/View、Scope及能力对象 | 相同hash_id不同source_record_index不合并；完整存储值与采集截断未知独立 | 仅逻辑草案 |
| location/unit/observation编码样例 | 有固定输入与独立预期摘要；T2/T4共用unit，不因rule_id拆分；embedded=null与内层空根不同 | 未提供编码样例 |
| 插件协议与静态registry版本 | describe/validate_selection/analyze_request/prepare_mutation签名；重复id/不兼容版本拒绝；optional映射缺失不阻断事实 | 未提供实际类型/版本 |
| PreparedMutation、guards、Plan/manifest | 内嵌JSON编译外层替换；同外层多操作一次编译；冲突拒绝，目标失败无after | 仅逻辑草案 |
| 方向/阶段、错误及评估Schema | 原scope不被低命中副本替换；Token无>1pp gate；not_run无0收益，blocked无after | wire表示待固定 |
| 完整原文/修改副本引用 | 报告scope内读取，preview不冒充完整；无需在H0交付运行HTTP，但类型/访问约束明确 | 仅逻辑草案 |

正式版本、import路径、实际签名及摘要均记录“未提供”，不临时发明1.0版本、不在token_content复制公共RequestView。

## 后续推进

本轮实际验证：在WSL项目.venv执行python -m pytest tests/unit/token_content/test_common_baseline.py -q，11 passed；ruff check同一文件通过。用例覆盖low_hit/长度/QPS路由、非法组合、请求行/运行身份及不可变性。只证明当前公共初始类型，不证明插件接入或运行阶段调度。读取HEAD为5c619f80631dbd0efdcbadffa7eedbf314bb678e；公共源码为其他会话新增工作树内容，未包含在该HEAD中。

公共维护会话完成LH000/H0后，本线核对实际版本、差异及固定正反例，记录接收结果；完成TA000退出条件后继续TA001。TA001–TA003不需要等待全部低命中规则，但仍需H0定义的输入边界。H1/H2/H3的实现不列为TA000必须全部就绪的条件，避免循环等待。

本轮授权持续有效，无需重新批准Token设计/计划。当前缺的是公共提供方交付，不是Token编码许可。未创建额外会话、未代发跨会话消息、未代签公共方交付；本记录作为可直接交给公共维护方的H0接收清单。

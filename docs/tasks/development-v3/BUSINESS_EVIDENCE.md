# 五组真实业务验收状态与回传字段

**当前范围决定（2026-11-11）：显式 full 延期（DEFERRED_BY_USER，未实现/未运行，不记PASS），不再是本期V3门禁；自动full仍禁止。候选repair-r1-02为LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING，独立R2已关闭RV3-01/02/03。大源自动缩样和五组session_clock样本参考率优先，真实BUS01–05及现场AC-MEM待华为验收。暂不打包。**

本条为最新状态，覆盖下文历史“待裁定/待独立复验”；原日志、原失败与当时勘误保持。B005按修订范围CLOSED；B007本地收口，整体现场门禁未关闭。见[本地收口](LOCAL_ACCEPTANCE_CLOSE_20261111.md)、[华为交接](HUAWEI_ACCEPTANCE_HANDOFF_20261111.md)。

2026-11-10。用户指定华为机有真实数据并负责这部分验收。本地工程LOCAL_VALIDATED；下表全部NOT_RUN，不是失败，也不填合成/旧报告的收益。此文档是后续验收输入，不代表本轮授权现场运行或打包。

| BUS | 模型 | APPID | 自动缩样/clock发现/前端新参考值 |
| --- | --- | --- | --- |
| BUS01 | DeepSeek-V4-Flash-0731 | S00000000000000000000000000000773 | NOT_RUN |
| BUS02 | DeepSeek-V4-Flash-0731 | S010320 | NOT_RUN |
| BUS03 | DeepSeek-V4-Flash-0731 | com.huawei.mbs.ilegal.ioc | NOT_RUN |
| BUS04 | DeepSeek-V4-Flash-0731 | com.huawei.newalliance | NOT_RUN |
| BUS05 | Qwen3.6-27B | com.huawei.aidp_dg06 | NOT_RUN |

## 后续验收必须保留的记录

1. 核候选源码/前端、环境、tokenizer revision/模式/摘要和实际缓存配置；按照交付规则核停旧服务，独立新state/浏览器。每轮创建不存在的输出目录，检查脚本输出路径，不复用历史证据。
2. 从真实业务监控来源选择准确APPID/模型，正常页面显式分析，不预置clock路径/recipe/finding，不靠现场提高candidate_limit或自动full。记录来源总数/范围、自动A/B选择数、排除原因、预算profile、时间/内存/停止原因。目标是大源自动有界完成，不以“预算不足”替代底线通过。
3. 对自动发现的clock记录请求对、原文位置、原值/修改后、变换摘要；页面显示样本N/匹配N/修改N、同样本before/after P/H/C/H/P与提升百分点，A/B各自单列。无B/无目标/无收益/未评估/预算不足分别回传，不能都写0或not_run。
4. 对封存逐行数据独立核实键/顺序/配置、P=H+C、精确提升、前端数字一致；收益仅样本参考。时间固定化改变时间感知，业务方确认语义后才能讨论采用，不能承诺无损。零收益和负收益也保留。
5. 保留service/source/sample/plan/evaluation/report摘要、执行状态、日志、页面截图、失败/复验；按现有两阶段人工验收、SSH18002及单Markdown回传约定安排。原报告不补写为新结果，源码本地通过不等于现场通过。

本地候选及验证链接：[B007闭环](batches/V3B007/CLOSE.md)、[设计核对](DESIGN_CHECK.md)、[完整测试](batches/V3B007/TESTS.md)。若现场不能自动发现或不能完成评估，返回精确失败证据由本开发线修复，不由镜像会话承担debug。

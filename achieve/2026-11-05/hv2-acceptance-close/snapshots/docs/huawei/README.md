# 华为机文档

2026-11-04：用户确认新版报告尚未回传，新增七项观察供[V3研究](../tasks/product-v3/ENTRY.md)立即开始。[V3补充取证prompt](../../prompts/delivery/HUAWEI_V3_EVIDENCE_APPENDIX_20261104.md)只追加到当前唯一Markdown，不改冻结包/SHA、不增加报告数量。已有统计与质量调查可先做；用户未指定appid前，不借V3研究启动第二阶段异常深挖。

2026-11-03：调查已回传，六线修复与本机独立源码/容器验收已闭环，新包已交付Windows桌面；华为对新版的真实数据验收尚未执行。[当前交付结果](../tasks/delivery/HV2_DELIVERY_20261103.md) · [当前完整现场prompt](../../prompts/delivery/HUAWEI_V2_HV2_REAL_DATA_20261103.md)。旧只读调查prompt已归档，不再作为新包部署指令。

- [V2二次验收原件](HUAWEI_V2_ACCEPTANCE_REPORT.md)、[2026-11-03调查原件](HUAWEI_V2_INVESTIGATION_REPORT_20261103.md)：只读保持；[原分析方案](HUAWEI_V2_REVIEW_AND_RESEARCH_PLAN_20261103.md)按历史阅读。
- [V100环境原报告](TOKEN_SCOPE_V100_ENVIRONMENT_REPORT.md)、[设计核对](MONITORING_V100_DESIGN_REVIEW_2026-10-26.md)：现场仍核实CPU/驱动/Docker/Compose/磁盘，不按机器名称假定NPU或GPU可用。
- [V1现场验收](MONITORING_V1_ACCEPTANCE_20261030.md)、[旧V2交付](../tasks/delivery/V2_APPROVED_DELIVERY_20261102.md)：历史及回退身份，不能代替新版现场通过。

现场仅真实Trace3/MA18 CSV，先量级和预算，再用户监控/搜索/TTFT及MA；第一次用户验收后由用户指定appid/模型/方向再做异常分析。停止已核实旧服务后新state启动，经SSH18002访问。最终唯一Markdown，关键源码/diff、复现、修改、结果与证据直接嵌正文；限制和失败如实保留。本机合成数据不得拿到现场冒充真实验收。[固定规则](../operations/DELIVERY_ACCEPTANCE_RULES.md)。

本目录保存版本化现场结论，原件不覆写；勘误和补证另存并指向原件，记录版本/配置/数据摘要和证据状态。

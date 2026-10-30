# 华为机文档

本目录保存华为机调查、事实核对、版本差异和验收结论。收到的报告、源码或日志原件放 evidence/huawei 或 evidence/source_drops，文件摘要放 evidence/manifests。

每份结论说明来源、日期、适用源码或镜像版本，以及“用户提供”“材料描述”“本机核对”“现场验证”等证据状态。内网路径可用于来源索引，需要的关键结论仍应有可阅读证据。

当前完整 PrefixLens 位于华为实验机，按后续分析任务需要核实。监控首版目标为 V100：已收到 [2026-10-26 原报告](TOKEN_SCOPE_V100_ENVIRONMENT_REPORT.md)，用户直接存入本目录，保持原件不移动、不改写；[来源摘要](../../evidence/manifests/monitoring-v100-environment-2026-10-26.json)和[设计核对](MONITORING_V100_DESIGN_REVIEW_2026-10-26.md)另存。确认 2×V100、40 可调度逻辑 CPU 与 Docker/Compose；驱动不匹配、CPU 镜像兼容性及性能状态见核对。其他机器的历史 H100 描述不能套用到本次目标，此前尚未取得现场首次验收报告；2026-10-30已收到真实CSV现场报告且用户确认V1前后端通过，当前状态见下方。


## 2026-10-30 监控V1验收

[验收核对与分析交接](MONITORING_V1_ACCEPTANCE_20261030.md)汇总现场事实、用户验收、workaround及限制；[报告原件](../../evidence/huawei/2026-10-30/TOKEN_SCOPE_HUAWEI_RUN_AND_BUG_REPORT.md)逐字节保存，[摘要清单](../../evidence/manifests/monitoring-huawei-acceptance-2026-10-30.json)记录来源。历史报告不覆写。

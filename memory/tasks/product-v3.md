# V3 调研与产品设计记忆

2026-11-04 首轮研究中。环境 CODEX_THREAD_ID / CODEX_SESSION_ID 均为 `01a1a5d5-4baf-7a41-b5c6-14bd5f4f67c2`，本会话独立核实，不沿用发送者身份。

角色：TokenScope V3 调研与产品设计；当前仅研究、设计和文档交付。已读 AGENTS、CURRENT、SESSIONS、docs/README、V3 ENTRY/任务书，定向读旧华为报告§7、HV2交付结果、用户设计及 estimator/defaults、MA replay、simulation 源码。HV2真实报告未到不阻塞。已有未提交修改保留；不改全局入口、不commit/push，不启动服务、真实分析或实验。

本线产出入口：`docs/tasks/product-v3/RESEARCH.md`、`EVIDENCE_MATRIX.md`、`PRODUCT_DESIGN.md`、`ROADMAP.md`；一手来源台账 `docs/research/tokenscope-v3/SOURCES_20261104.md`。完成状态以本文件后续记录为准。

阅读结论：现有理想回放是无限磁盘逻辑前缀账本，无KV张量/物理驱逐；用户与MA作用域不同。现有TTFT是固定等待/chunk情景参考，不能按总体命中率倒推出可靠排队/容量。新观察、旧10appid/676样本与总体分开。95%普适拐点未获证实；高命中仍有剩余工作量价值。优先可信数据→画像/分诊→行动建议；容量/SSD不作主线。

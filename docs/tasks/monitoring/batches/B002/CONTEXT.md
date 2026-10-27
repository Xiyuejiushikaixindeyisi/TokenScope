# B002 上下文

2026-10-27。B001 已 closed，66 项测试及静态/HTTP 检查通过，源码清单在 artifacts/validation/monitoring/B001。批准输入 DESIGN/契约 v1.0，身份见 APPROVAL；本批只负责统一编码与中间信息。

已固定来源 env/sources.lock.json：Qwen3.6-27B 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9；GLM-5.2 cf457fa734ab149ffef225f80893eb38c6ff5cdc；DeepSeek-V4-Flash-0731 7872f01b1d1fe23eabc4c98b48bffcef5a386062。models 目前没有实际词表。按 CODEMAP 只读取这三模型模板、DeepSeek 官方编码及必要 Rust/服务适配入口。

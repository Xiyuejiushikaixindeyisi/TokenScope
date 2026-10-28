# B002 闭环

状态：closed（2026-10-27）。实际门槛来自批准 DESIGN 第13节：三模型固定真实 tokenizer IDs 参考对齐、tools/思考/特殊字面量/长文本、批量/线程一致、离线资产校验均通过。补齐 raw SQLite→有界编码→uint32LE分片/轻量来源/质量计数；96项全回归和ruff/format/mypy通过。

DeepSeek 生产缺省仍 pending；明确请求或显式profile可用，未知缺省拒绝执行。此项不影响已验证的编码实现，不替用户选择默认；真实流量及现场等价性在B005/B006保持待验收。完整HTTP编排在B004连接。

回退：B001 source-snapshot和对应uv.lock；本批source-manifest/source-snapshot为新检查点，不改前端与原始证据。数据库输入与编码状态不完整时不可作成功结果，重试创建新run。B003可开始。

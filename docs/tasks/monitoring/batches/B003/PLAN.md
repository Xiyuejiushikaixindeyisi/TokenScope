# B003 方案

1. CacheStrategy协议、FullBlock/NoCache、Qwen/DeepSeek增强占位类。SQLite逻辑账本无淘汰，有界SQLite缓存；链式SHA256包含资产/租户/块长与前块/uint32LEIDs。
2. 单请求五事件，查后发布；P−1查询上限和MTP退一块，完整输入块全发布。按appid/time_ns/source_record_index流式回放，逐批写回H/C和事件摘要；不缓存输出。
3. 独立参考按历史完整token前缀集合计算，与随机轨迹差分；B边界/MTP/CP/租户隔离/模式相同IDs/NoCache/增强拒绝；重跑全套静态和测试。
4. 回退B002快照，保留已有结果与原CSV。门槛通过后五文档/记忆更新再进B004。

# Token 监控：由缓存布局推导请求回放规则

日期：2026-10-26。Session 1。接续[用户布局材料核对](MONITORING_LAYOUT_REVIEW_2026-10-26.md)，只补充相关缓存读写与调度证据，不扩展到模型数值计算。用户确认 txt 作为布局背景，并确认主结果采用固定、可配置的顺序 prefill 规则；每个合法边界都保存状态的方案单列理论情景。

## 证据范围

- vLLM v0.23.0：`0fc695fc6d1d82e9a5ac6835ac8e4e1c83703665`。
- vLLM-Ascend v0.23.0：`5cb98caaadeff42b5b62b996e34bb2aaa29d20fd`，优先使用其 coordinator、压缩 manager 与 Mamba patch；未覆盖处读取所依赖的 vLLM 实现。
- 新增固定 `block_pool.py`、`sched/scheduler.py`、`envs.py`，文件摘要见 [sources.lock.json](../../../env/sources.lock.json)。新增文件与 GitHub 返回的 Git blob 身份一致。
- 目标仍是公开版本规则，未取得现场镜像 digest、补丁和有效启动配置。没有执行引擎、worker、GPU/NPU 或吞吐验证。

## 读和写都必须进入仿真

| 对象 | 查询既有缓存 | 写入/保留约束 | 直接源码 |
| --- | --- | --- | --- |
| 完整 attention KV | 从开头连续匹配完整逻辑块；遇到第一个缺失停止；按对应版本 MTP 和对齐退回 | 只有已计算、非 null、允许注册的完整块进入前缀索引 | [FullAttentionManager](../../../upstream/vllm-v0.23.0/vllm/v1/core/single_type_kv_cache_manager.py)、[BlockPool.cache_full_blocks](../../../upstream/vllm-v0.23.0/vllm/v1/core/block_pool.py) |
| Ascend 压缩 attention | 按 B × compress_ratio（及适用 CP）查询链式逻辑块，处理本组 MTP 与共同对齐 | `num_tokens // (B × compress_ratio)` 个完整逻辑块；不是任意部分压缩页 | [CompressAttentionManager](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/core/single_type_kv_cache_manager.py) |
| SWA | 从右向左找恢复边界所需的连续尾部；前面的无用块可为空 | 可只将可达边界附近的尾部注册进缓存；mask 许可不代表对应 tensor 一定物化 | [SlidingWindowManager](../../../upstream/vllm-v0.23.0/vllm/v1/core/single_type_kv_cache_manager.py) |
| GDN/Mamba 状态 | 查找已有状态快照；不能从更晚的快照倒推更早状态 | align 模式可跳过中间块，仅在实际分步边界留下运行状态；null 块不会注册成检查点 | [AscendMambaManager](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/patch/platform/patch_mamba_manager.py)、上游 `MambaManager.allocate_new_blocks/cache_blocks` |

`BlockPool.free_blocks`（419–441 行）主要减引用计数并放回可分配队列，并不在此直接删除 prefix hash。无限容量仿真不能把请求结束/free 等同于所有历史前缀失效；同时，不能因为有 hash 就跳过数值状态完成、复制或显式失效条件。

查询还受 `get_computed_blocks` 的 P−1 上限约束。普通路径的最后 logits token 重算和 MTP 退块是两个步骤，不能合并为 `P−128`。混合路径由 Ascend coordinator 协调各组，重复候选检查中还有已核验 MTP 的状态，不能每轮无条件再减一块。

## SWA：无限容量也不能取消显式保留策略

[reachable_block_mask](../../../upstream/vllm-v0.23.0/vllm/v1/core/single_type_kv_cache_manager.py)（688–749 行）使用共同对齐 A：

- retention_interval 未设置（None）：每个 A 边界保留恢复所需尾部。
- 为 0：不保留周期尾部，只保留当前 prompt 可重放的最后对齐边界附近尾部。
- 为 A 的正整数倍：按该周期保留尾部，并额外保留当前 prompt 的最后可重放边界。
- EAGLE/MTP 会改变所需连续块数和尾部右端的位置，不能只在查询后统一减一个固定数。

[envs.py](../../../upstream/vllm-v0.23.0/vllm/envs.py) 1046–1055 行确认该环境变量默认 None；[coordinator 校验](../../../upstream/vllm-v0.23.0/vllm/v1/core/kv_cache_coordinator.py)要求有效周期为 scheduler 对齐的非负整数倍。该选项当前仅稀疏化 SWA，不能当作 GDN 状态保存模式开关。Ascend coordinator 把 SWA manager 的 mask 对齐设为其 LCM（155–157 行）；继承的写路径还有对齐与 MTP peek 限制。

隔离算术例：B=32、窗口=128、共同对齐 A=4096；前一 prompt 长 14000；后一请求的查询上限为 4999，且可查询部分的前缀相同。在假定所有被 mask 选中的块都已物化时：

| retention_interval | 无 MTP 注册块数 | 有 MTP 注册块数 | 后一请求得到的 H |
| --- | --- | --- | --- |
| None | 12 | 15 | 4096 |
| 0 | 4 | 5 | 0 |
| 8192 | 8 | 10 | 0 |

这是固定函数与人工 metadata 的结果，不是 V4 部署结果。它证明保留策略会影响查询，不能证明 worker 在任何调度下都已写完这些块。

## GDN：固定 prefill 规则是结果身份的一部分

[Scheduler._mamba_block_aligned_split](../../../upstream/vllm-v0.23.0/vllm/v1/core/sched/scheduler.py)（293–338 行）会对预算进行块对齐，并强制在最后缓存位置切开；MTP 还会提前这个位置。`MambaManager` align 分配只给实际运行状态留下非 null 块，`BlockPool.cache_full_blocks` 明确跳过 null 块。故总 prompt 长度和物理 B 不能唯一确定已保存的状态集合。

隔离例取 B=4、P=12、MTP 开启，仅用于缩小数字说明控制流，不代表硬件允许 B=4。第一请求冷缓存；假定仅对齐的 prefill 步骤终点物化状态，第二请求完全相同：

| 每步预算 | 第一请求的步骤终点/假定检查点 | 第二请求 attention 经 P−1 和 MTP 后候选 | 状态查询后的共同 H |
| --- | --- | --- | --- |
| 12 | 8、12 | 4 | 0：没有位置 4 的快照 |
| 4 | 4、8、12 | 4 | 4 |

执行的是源码拆分函数、FullAttention 查询函数和 AscendMamba 查询函数；步骤终点→数值状态完成属于本例明示假设，未运行 worker 的分配/拷贝/写入生命周期。因此它是调度敏感性的条件反例，不能据此宣称实际 Qwen 重复请求必然零命中。

用户已选择：主指标绑定固定、可配置的顺序 prefill 规则；“每个合法边界均可保存状态”单列理论情景。主指标因此是**该保存与调度规则下、无限容量且前序请求立即可用的输入复用结果**，不是对所有调度/保存策略取最大值。

建议运行清单记录 per-step prefill Token 预算、拆分算法版本、状态发布规则；不能用 CSV batch 行数或 Rust 编码 chunk 大小代替。默认数值尚未确定；不足以推进对齐步骤的配置需显式失败，不能进入零步长死循环。无输出 IDs，不扩展到 decode 输出缓存、真实并发公平性或通信耗时。

## V4 粗粒度快速路径何时成立

将 V4 折叠为单个共同 B，需要同时证明：

1. 压缩 attention/index 组在对应逻辑粒度上拥有相同前缀身份且连续完整。
2. 所选共同边界处的 SWA 尾部与所有必要 compressor 状态确实存在；不是仅由 page 大小推测存在。
3. 状态 admission/retention、部分页和角色没有额外限制。
4. 该版本各组 MTP、peek、P−1 和对齐处理可以投影为相同的单一路径。

共同 LCM 只证明对齐条件。只有这些条件成立并通过与组级回放的差分验证，才能启用单 B 快速路径。否则继续组级查询；不能把“不是普通单 B”一律归类为已支持的增强功能。

## 增强路径的能力条件草案

本节定义仿真需要的证据和接口条件，不替 Ascend 发明或实施内核方案：

- **匹配单位**：物理页覆盖量与允许恢复的 Token 边界分开；不能自动用各组 page 大小的 GCD 当细粒度能力。
- **部分页有效范围**：缓存键绑定租户/profile/组件及实际前缀；记录已完成的有效条目范围。page 已分配不等于整页可复用。
- **状态闭合**：边界 t 所需的压缩 KV、index cache、滑窗尾部、compressor 或 recurrent state 必须齐全。压缩相位、未压满分组的残留信息及其恢复方式须由实现明确，不能按 `floor(t/r)` 后丢掉余数。
- **可写副本**：命中后若继续写共享部分页/状态，需要有经验证的 COW 或等价隔离语义；旧前缀不能随本请求续写而改变。
- **发布时机**：本次计算或二次发现共享前缀后新增的检查点，只能影响之后的请求；不能倒算为本请求已命中。

V4 和 GDN 可以共享上述接口概念，但各自的状态内容、保存位置和恢复条件仍独立。已有布局 txt、HiCache/HiSparse 名称、单个 PR 合并或“HBM 无限”，都不足以证明整条能力链成立。尚不具备证据的增强 profile 返回 unsupported/unverified，不悄悄回退到普通路径。

## 验证与设计落点

[隔离检查脚本](../../../artifacts/research/monitoring-2026-10-26-replay/check_source_rules.py)从固定源码 AST 提取相关方法，以简化 metadata/前缀键执行；[结果](../../../artifacts/research/monitoring-2026-10-26-replay/source-rule-check.json)包含 6 个 SWA 及 2 个 GDN 条件案例。未执行完整上游单测、编码器、数值状态、部署和性能测试。

采用结论进入 [DESIGN](../../tasks/monitoring/DESIGN.md) 与 [监控契约](../../contracts/MONITORING_V0_2.md)；[请求回放样例](../../contracts/examples/monitoring-v0.2-replay-illustrative.json)明确标注人为长度与检查点假设。未冻结默认 prefill 预算、增强 profile 或正式接口 Schema。

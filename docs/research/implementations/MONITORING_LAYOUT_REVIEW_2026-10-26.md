# 用户缓存布局材料核对与监控仿真边界

日期：2026-10-26。对应设计：v0.2.1-discussion。接续 [Ascend page 调研](MONITORING_RESEARCH_2026-10-26.md)。

## 材料身份与使用方式

已收到 [用户 txt 原文](../../../evidence/user/monitoring-2026-10-26/vllm-ascend-cache-layout-notes.txt)，按原始字节复制入项目，未修正文案。[来源清单](../../../evidence/user/monitoring-2026-10-26/manifest.json) 保存附件路径、字节数和 SHA256。

本份内容主要解释 EngineCore/worker、block/page/group、page unification、DeepSeek V4 packing 与 Ascend 单位差异；尚未明确部分前缀的注册边界、状态恢复、COW 与 MTP 流程。先作为布局研究材料使用，不能把解释性笔记直接视作已批准的增强命中算法。原文没有绑定所有段落的源码 revision/模型 checkpoint，逐条按固定来源核对。

## 可以采用的部分

1. 模拟器应区分元数据账本与实际 KV tensor。TokenScope 统计输入重用，不运行 attention kernel、不生成真实 KV。
2. page 字节量、block 覆盖的逻辑 Token、group 的保留/恢复规则分别影响分配和复用；同名 block_size 可能使用不同单位。
3. group 内共享 block table，跨 group 的恢复需要协调。普通模型的“一列覆盖全部层”只能用于对应的单 group 布局。
4. 页大小统一、padding、group 切分和共享底层 tensor 是实现约束，不能凭模型系列直接推定统一缓存行为。

## 需要限定或修正的内容

| 材料表述 | 核对结论 | 对监控设计的影响 |
| --- | --- | --- |
| 账本除了命中时不感知 group | 固定 vLLM 的 `KVCacheBlocks.blocks[i][j]` 明确按 group 组织；coordinator 按组分配/保留/释放，缓存键还组合 group id。底层 BlockPool 可是共享分配器，不代表上层账本不感知组 | 必须保留每组状态，不能只有一条全局前缀链 |
| 一个 block id 指向全部层 | 对 uniform 单 group 是可用示意；hybrid 下层会映射到共享 slot、group 各有 block table，不应推广为全模型相同列 | 模拟器用逻辑 group/component 身份，不能把裸 block id 当作跨组语义身份 |
| 当前默认 LBHNC；后文写 LBNHC | 引用的 [RFC #42082](https://github.com/vllm-project/vllm/issues/42082) 区分逻辑 shape 与 stride order；LBHNC/LBNHC 是不同布局。RFC 的 Proposed Change 不能单独证明目标版本默认值 | 配置中记录实际 layout/segment/COW 能力，不按字母缩写猜测连续内存或传输方式 |
| page 不整除时都可以 padding | 0.23.0 的一般 `unify_kv_cache_spec_page_size` 在不整除时直接报错；V4 特殊分组路径才有按桶 padding，不能当作通用 fallback | 根据实际代码路径解析 page，不臆造任意兼容布局 |
| V4 必须改成 block-major packing | 固定 vLLM 0.23.0 的 allocator 仍按 slot/page-size 创建 tensor；Ascend 0.23.0 也按桶和 slot 创建 tensor，且补丁明确区分后续 v0.24.0 packed 路径 | 不把较新或其他后端的 packing 描述回填到本次 0.23.0 profile |
| 243 份 cache、61 个 recent 层、5 个 group | 当前公开 Flash-0731 配置为 43 个主干层；前 43 个 compress_ratios 是 2 个 0、21 个 4、20 个 128。原文计数不直接适用。实际 group 数还受 MTP、共享、PP 和 spec 分组影响 | 不硬编码 243/5 等数量，应固定配置并导出/推导该部署的分组 |
| 只有两种 page 大小，因此可保留某布局 | Ascend 源码有两档 page padding 表与按 page-size 分桶的证据；这不能独自证明所有 tensor 的 H/N 轴顺序或任意配置只有两类最终页 | 页尺寸类别与实际 tensor stride 分开记录，必要时检查 worker 布局，第一版不据此预测网络耗时 |
| pool 建好后不再创建/删除任何块 | 预留 tensor 存储与逻辑分配/释放是不同层次；请求运行期间逻辑 block 生命周期持续变化。本文不核验所有 worker 进程和内存 profiling 细节 | 无限容量可省去容量竞争/free-list 淘汰，但仍要维护缓存内容的物化、共享与有效性 |

## 两边 block_size 的单位对照

在固定的压缩 MLA 路径中，证据是：

- vLLM 0.23.0 [MLAAttentionSpec.storage_block_size](../../../upstream/vllm-v0.23.0/vllm/v1/kv_cache_interface.py)：`storage_block_size = block_size // compress_ratio`（365–367 行）。这里 spec 的 block_size 表达原始逻辑 Token 覆盖量。
- Ascend 0.23.0 [AscendMLAAttentionSpec.page_size_bytes](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/core/kv_cache_interface.py) 直接按 block_size 个存储条目计字节；[CompressAttentionManager](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/core/single_type_kv_cache_manager.py) 的读写将其乘 compress_ratio，恢复原始 Token 粒度。
- 原文的区别适用于这个版本/这类 cache，不能推广到两边所有 spec、所有 CLI 版本和 compressor state；例如 Ascend SWA 的 ratio=1，状态 slot 又需单独核实单位。

CP=1 时的示意换算：

| 路径/组 | spec 中 B | ratio | 该块的存储条目数 | 原始 Token 覆盖量 |
| --- | --- | --- | --- | --- |
| vLLM 压缩 MLA，C4 | 256 | 4 | 64 | 256 |
| vLLM 压缩 MLA，C128 | 256 | 128 | 2 | 256 |
| Ascend 压缩 MLA，C4 | 128 | 4 | 128 | 512 |
| Ascend 压缩 MLA，C128 | 128 | 128 | 128 | 16384 |
| Ascend SWA | 128 | 1 | 128 | 128 |

这是单位换算示意，不是完整部署 spec dump。MTP、CP、状态窗口、保留策略、hash unit 和跨组协调仍决定最终命中。

## Ascend 分组与分配的直接证据

本轮固定 [patch_kv_cache_utils.py](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/patch/platform/patch_kv_cache_utils.py)：

- `group_and_unify_kv_cache_specs` 150–181 行：compressed MLA 按 ratio 分桶，SWA 类按其 block size 分桶。
- `_get_kv_cache_groups_uniform_groups` 184–273 行：C4/C128 各形成 full MLA group，其他组经 layer tuple、approximate gcd、padding 后拆分。
- `_get_kv_cache_config_deepseek_v4` 276–336 行：按 page-size 和 tuple slot 建 tensor，共享层写在 shared_by；MTP 的 tensor 另行处理。
- 348–354 行显式给 0.23.0 的函数名及后续 packed 函数入口打补丁，使 Ascend 使用自身非 packed 布局。

因此，“V4 只影响 B”最多是经过等价性校验的缓存读写快速路径；真实布局差异本身不要求监控搬运字节，但如果它改变可存/可恢复边界，就必须反映在策略中。

## 对 TokenScope 的设计推导

本轮建议将缓存仿真内部再分成两层，而不是新增产品模块：

- **规则解析**：固定模型/后端/版本/有效参数，规范化各组的 logical_token_span、storage_entries、page_bytes、hash unit、状态要求、保留/复制条件和 MTP 规则。原始值与单位保留，可追溯换算。
- **逻辑回放**：维护组级前缀键和可用内容/状态边界。按请求顺序先查询、求所有必要组共同可恢复边界，再根据写入/状态物化策略更新缓存；不得把本请求新保存的状态倒算成本请求此前已经命中的 Token。

对请求 i，建议将共同可恢复集合写成 `R_i = intersection(R_i,g)`，H_i 是满足版本尾部/MTP约束的最大合法边界，C_i=P_i-H_i。实际实现可采用 coordinator 的单调下降搜索，不需要枚举所有整数边界。

这个集合表述不意味着数值 KV 或 sparse top-k 仿真。各 R_i,g 要由组规则和已有键/检查点得到，不能只算 `min(每组最大长度)` 后假定截短一定合法：recurrent state 不能从 16 的快照回退出 12 的快照。

无限容量下，可忽略仅因内存不足产生的淘汰、可用块数限制和 free-list 顺序；仍保留状态未物化、滑窗必要尾部、显式 admission/retention、COW 后可见性和版本 MTP 约束。改变容量与改变缓存保存策略必须作为不同情景表达。

## 示例与验证

新增 [边界示意样例](../../contracts/examples/monitoring-v0.2-recovery-boundary-illustrative.json)：

- 粗粒度 Ascend 风格 C128、B=128、两条相同 8192-token 输入：没有完整 16384-token C128 块，因此在该示意规则下两条均 H=0；无限容量也不改变这一条件。
- 人工设置两个组的合法恢复集合，展示最大长度的最小值不一定是共同合法边界。该集合示例不是任何目标模型的实测轨迹。

将固定源码中的纯算术函数 `_approximate_gcd` 隔离执行，输入 [30,61,31,60]、lower_bound=30 得到 31，与原文算例一致；只证明算术，不证明这些输入适用于 Flash-0731。输出及配置计数见 [检查记录](../../../artifacts/research/monitoring-2026-10-26-layout/arithmetic-check.json)。

另登记 Ascend [test_prefix_cache_cp_patches.py](../../../upstream/vllm-ascend-v0.23.0/tests/ut/patch/platform/test_prefix_cache_cp_patches.py)：effective block size、Mamba logical block size、SWA 在 LCM 边界保留掩码等测试只读未运行。原文所述 API/worker 进程数、全部内存 profiling 细节和各模型实际 tensor shape 本轮未逐项验证，不据此填写部署事实。

增强 V4 的具体 checkpoint/部分页算法仍待讨论；本轮材料足以改进仿真抽象，但不能补足尚未给出的状态保存和恢复步骤。

# Token 监控首轮调研：来源、缓存规则与编码

日期：2026-10-23。状态：源码阅读与有限参考测试，尚非现场验证或最终采用方案。用户已指定 Qwen3.6-27B、DeepSeek-V4-Flash-0731、GLM-5.2，镜像 0.23.0，MTP 默认开启，block size 默认 128，启动参数未知。

## 证据身份与范围

固定来源和逐文件 SHA256：[sources.lock.json](../../../env/sources.lock.json)。仅获取必要文件快照，未克隆全部仓库、安装运行依赖、下载模型权重或构建镜像。

| 参考 | 固定身份 | 能证明的范围 |
| --- | --- | --- |
| vLLM v0.23.0 | `0fc695fc6d1d82e9a5ac6835ac8e4e1c83703665` | 官方标签的实现和测试预期 |
| vLLM-Ascend v0.23.0 | `5cb98caaadeff42b5b62b996e34bb2aaa29d20fd` | 官方标签的补丁、配置和模型适配 |
| Qwen3.6-27B | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` | 官方配置、tokenizer 配置、Jinja 模板 |
| DeepSeek-V4-Flash-0731 | `7872f01b1d1fe23eabc4c98b48bffcef5a386062` | 官方配置、编码参考和测试 |
| GLM-5.2 | `cf457fa734ab149ffef225f80893eb38c6ff5cdc` | 官方配置、tokenizer 配置、Jinja 模板 |
| deepseek-recipe | `935817c66f5d6e64838f419692545f06787e485f` | Rust 编码路径及 Python 接口参考 |
| DeepInfer | `9bd9cf243fc53ef9afbf8f04d391d989117d6ab9` | 官方部署问答中 Recipe 的职责说明 |
| 本机 PrefixLens | `fa3759d933c7583b5081276de3bea3f20671e486`；文件另有摘要 | 基础版指定路径；原工作树有其他未提交改动，未修改原件 |

官方发布说明表示 Ascend v0.23.0 对齐 vLLM v0.23.0，但不能据此证明用户镜像无后续补丁。镜像完整 tag/digest、实际包 commit、配置及模型文件摘要仍待现场核验。[官方发布](https://github.com/vllm-project/vllm-ascend/releases/tag/v0.23.0)

首次广义搜索取得的最新主干、Qwen35B、未带 0731 的 V4 快照保留为背景，在锁文件中标记已被当前目标参考替代；不得把其中新功能移植成 0.23.0 的事实。

项目 evidence/source_drops、evidence/huawei 当前只有占位入口，未找到完整 PrefixLens 现场证据。兄弟目录 PrefixLens 的远端是 `Xiyuejiushikaixindeyisi/Two-Queue-TTL`；本轮只读指定计算/测试文件并复制为项目内固定快照。未把兄弟项目运维或开发规定继承过来。

## 结论一：block size 必须分清物理与逻辑含义

### Qwen3.6-27B 的 1536 推导

官方模型配置：GDN 与 full-attention 混合；linear value heads=48，key/value head dim=128；普通 attention KV heads=4、head dim=256。GDN 状态形状由 `gated_delta_net_state_shape` 按 TP 拆分。

Ascend 0.23.0 的 `patch_mamba_config.verify_and_update_config` 以 SSM 状态页与单独 K 页对齐，将内核基准 128 向上扩大，必要时覆盖用户 block size。以 **TP=1、SSM FP32、attention KV BF16** 为明确示例条件：

```text
SSM bytes = 48 × 128 × 128 × 4 = 3,145,728
K bytes/token = 4 × 256 × 2 = 2,048
effective block = 128 × ceil(3,145,728 / (128 × 2,048)) = 1,536
```

这是模型参数与源码公式的推导，不是现场启动实测。TP、KV 头复制、KV/SSM dtype、补丁可能改变结果。该 sizing 逻辑本身并不以“关闭 hybrid manager”为唯一条件，故不能确认“关某功能必为 1536”。

证据：[模型 config](https://huggingface.co/Qwen/Qwen3.6-27B/blob/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/config.json)、[Ascend sizing 源码](https://github.com/vllm-project/vllm-ascend/blob/5cb98caaadeff42b5b62b996e34bb2aaa29d20fd/vllm_ascend/patch/platform/patch_mamba_config.py#L58-L108)。本地路径见 CODEMAP。

### DeepSeek V4：Ascend 128 不等于命中粒度 128/256

vLLM 0.23.0 `vllm/models/deepseek_v4/sparse_mla.py` 的后端声明支持的 kernel block 为 256；这是特定后端规则，不能套用于 Ascend。

Ascend 0.23.0 `utils.refresh_block_size` 的 DeepSeek V4 路径允许 32/64/128。`get_dsv4_block_sizes` 映射 MLA/SWA/压缩状态的存储块；coordinator 的 `_get_effective_block_size` 乘压缩比例及 CP 因子，再对多组取 LCM。

对于 CP=1、存储块 B=128、C4/C128 均在的对应配置，C4 逻辑块为 512，C128 为 16384，组间命中对齐为 16384 原始 token。B=32 的对应粒度可为 4096，官方标签部署说明将其称为实验性 4K prefix cache 支持。MTP、SWA/压缩状态可用性会进一步约束实际命中。

证据：[块映射](https://github.com/vllm-project/vllm-ascend/blob/5cb98caaadeff42b5b62b996e34bb2aaa29d20fd/vllm_ascend/models/layer/attention/layer.py#L32-L47)、[逻辑块与组间对齐](https://github.com/vllm-project/vllm-ascend/blob/5cb98caaadeff42b5b62b996e34bb2aaa29d20fd/vllm_ascend/patch/platform/patch_kv_cache_coordinator.py#L161-L239)、[0.23.0 部署说明](https://github.com/vllm-project/vllm-ascend/blob/5cb98caaadeff42b5b62b996e34bb2aaa29d20fd/docs/source/tutorials/models/DeepSeek-V4-Flash.md#L325-L328)。

`test_hybrid_coordinator_rejects_partial_compressed_prefix_hit` 专门构造前 128 token 一样、后续在同一 512-token 压缩逻辑块内分叉的请求，预期该逻辑块不能命中。本轮只读该测试，未执行 Ascend 测试。

### MTP 与状态恢复

vLLM 0.23.0 的 `SpeculativeConfig.use_eagle` 包含 MTP；`KVCacheManager.get_computed_blocks` 以请求长度减一限制命中，full-attention finder 再按 MTP 退掉末个匹配块。应区分“为 logits 重算”与“MTP 退块”。

官方测试对恰好 3 个完整块的重复请求，预期只命中 1 块；测试名称下的 docstring 与断言存在表达不一致，应以执行路径和断言为核对依据，不能只读说明。hybrid 的 Mamba finder 查可恢复状态，coordinator 协调各组边界，不能在最终值上重复统一扣块。

证据：[命中上限](https://github.com/vllm-project/vllm/blob/0fc695fc6d1d82e9a5ac6835ac8e4e1c83703665/vllm/v1/core/kv_cache_manager.py#L215-L226)、[full-attention finder](https://github.com/vllm-project/vllm/blob/0fc695fc6d1d82e9a5ac6835ac8e4e1c83703665/vllm/v1/core/single_type_kv_cache_manager.py#L520-L569)、[MTP 测试](https://github.com/vllm-project/vllm/blob/0fc695fc6d1d82e9a5ac6835ac8e4e1c83703665/tests/v1/core/test_prefix_caching.py#L2393-L2458)。

## 结论二：模板和编码资产可以取得，服务模式还要绑定

| 模型 | 官方固定资产入口 | 本轮状态 |
| --- | --- | --- |
| Qwen3.6-27B | [文件树](https://huggingface.co/Qwen/Qwen3.6-27B/tree/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9) 的 tokenizer.json、tokenizer_config.json、chat_template.jinja | 配置/模板已留快照；词表 tokenizer.json 尚未下载；需绑定 enable_thinking、preserve_thinking、tools 等 |
| GLM-5.2 | [文件树](https://huggingface.co/zai-org/GLM-5.2/tree/cf457fa734ab149ffef225f80893eb38c6ff5cdc) 的同类三个文件 | 配置/模板已留快照；词表未下载；需绑定 enable_thinking、clear_thinking、reasoning_effort、tools |
| DeepSeek-V4-Flash-0731 | [文件树](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/tree/7872f01b1d1fe23eabc4c98b48bffcef5a386062) 的 tokenizer 文件及 encoding/encoding_dsv4.py | 不是统一 Jinja 模板路径；专用编码参考及测试已取；词表未下载 |

vLLM 0.23.0 的 `get_deepseek_v4_tokenizer` 用专用 `encode_messages` 渲染，处理 tools、thinking/enable_thinking、drop_thinking 和 reasoning_effort。最新 Recipe 不能未经等价测试就替代这条历史服务路径。GLM 官方 config 的 model_type 为 glm_moe_dsa，含 DSA 索引配置，不将它简单称为普通 dense 模型。

原始 JSON 计量和模板后计量有不同含义：前者包括不会送入 prompt 的采样参数和 JSON 语法；二者差值不是纯“模板开销”。需要特别保留这一解释，避免误导后续长度分析。

## 结论三：复用候选及适用边界

| 来源 | 可以借鉴 | 不能直接沿用 |
| --- | --- | --- |
| PrefixLens 本机基础版 | `lib/chain_key.py` 链式前缀身份、`lib/hit_rate.py` 连续前缀匹配、计量与报告分离 | 当前 chain 对不足整块的尾部也生成 key，pooled_hit_rate 按块数计量；不能直接作为精确 token 加权、MTP、GDN、压缩组仿真。其模板包装接受 raw/user/messages，不能直接处理完整 OpenAI 请求对象和所有 tools 选项 |
| vLLM / vLLM-Ascend 0.23.0 | 缓存合法性、状态保留、MTP 和压缩组测试，作为仿真规则依据 | 不把整个推理框架当成离线监控运行依赖，也不把主干新行为视为现场事实 |
| deepseek-recipe | Rust API 转换/渲染/编码及 Python bindings；特殊 token 边界内的批量并行 | DeepSeek 专用格式不能套给 Qwen/GLM；需要验证与 0731/0.23.0 服务路径一致 |
| Hugging Face tokenizers | 成熟 Rust tokenizer 内核及批量编码 | 使用 Rust 不自动保证两小时 SLA；任意切割字符串可能改变 BPE 边界 |

Recipe 的 `PromptTokenizer::encode_ids` 分离模板明确标记的特殊 token 区间，普通区间使用移除 added vocabulary 的 tokenizer，通过 `encode_batch_fast` 批量编码，再依次插入特殊 token IDs。该分段方式同时关联性能与特殊 token 语义，不能简化成任意切片。[固定源码](https://github.com/deepseek-ai/deepseek-recipe/blob/935817c66f5d6e64838f419692545f06787e485f/deepseek-recipe-encoding/src/tokenizer.rs#L71-L117)、[DeepInfer 官方说明](https://github.com/deepseek-ai/DeepInfer/blob/9bd9cf243fc53ef9afbf8f04d391d989117d6ab9/doc/inference_deployment_qa.md)

## 论文与理论参考

- [PagedAttention / vLLM，2023](https://arxiv.org/abs/2309.06180)：块化 KV 存储和共享机制的基础背景；不能代替 0.23.0 混合模型的具体规则。
- [SGLang / RadixAttention，2023](https://arxiv.org/abs/2312.07104)：前缀树组织与跨请求复用值得借鉴；本任务仍以 vLLM/Ascend 命中语义为目标，不移用 SGLang 命中规则。
- [Gated Delta Networks，ICLR 2025](https://arxiv.org/abs/2412.06464)：解释 GDN 的递归状态与混合结构，帮助理解“有相同 token”不等于“有可恢复状态”；不能由论文直接推出 Ascend block size。

这些论文只作机制参考，尚无将其实现直接引入 TokenScope 的决定。

## 已执行验证及限制

在 WSL Python 3 中运行官方 0731 固定快照 `python3 -B test_encoding_dsv4.py`，4/4 通过：thinking+tools、无工具思考清理、交错思考+搜索、quick instruction。输出证据：[本地测试记录](../../../artifacts/research/monitoring-2026-10-23/deepseek-v4-0731-reference-test.json)。

本轮没有执行 vLLM/Ascend 缓存测试、没有运行 tokenizer 词表、没有对真实 CSV 或 CPU 吞吐作测试。4/4 只代表官方参考渲染/解析样例通过，不证明 Token IDs 与部署一致、不证明 TokenScope 功能已实现。

# Token 监控：Ascend page 规则与编码证据

日期：2026-10-26。范围：接续 [10-23 调研](MONITORING_RESEARCH_2026-10-23.md)，核对与本轮监控设计直接相关的源码、PR 和编码边界。未运行 NPU、服务联调、Tokenizer IDs 对齐或性能测试。PR 作者的测试描述不是本项目测试结果。

后续同日已收到用户 txt，逐项核对与新增设计建议见 [布局材料核对](MONITORING_LAYOUT_REVIEW_2026-10-26.md)。下文“下轮提供”保留为本次初始调研时的材料状态。

## 本轮用户决定

- 输入均为纯文本，包括工具定义、调用和文本返回；CSV 的 request_input 是 GF 转换后送往推理服务的 OpenAI v1 请求体。不需要在 TokenScope 重做 GF 转换。
- 前一请求可缓存输入立即对下一请求可用；每 CSV 空缓存、租户隔离、无限容量的既定假设继续有效。
- 三个模块：基础转换、按 appid × 模型回放的前缀缓存仿真、数据统计。
- page 分配/复用规则以 vLLM-Ascend 对应版本代码和 PR 为主要依据；vLLM、SGLang 是参考，不能直接代替 Ascend 能力证明。
- 后端提供总量、命中率和分位数的权威值；前端画图和交互。
- 全量保存轻量编码证据，需要细查时由同一编码实现生成详细来源映射并验证 IDs 一致。
- 用户的 DeepSeek V4 txt 方案下轮提供，本轮未取得、未评价，也没有将任何公开 PR 认作该 txt。

## 固定来源与证据层级

0.23.0 研究基线仍为 Ascend `5cb98caaadeff42b5b62b996e34bb2aaa29d20fd`、vLLM `0fc695fc6d1d82e9a5ac6835ac8e4e1c83703665`。这是公开标签参考，现场镜像摘要和补丁未知。

本轮仅额外固定 Ascend 主干 `86add7adfd1194c225fd8880699d5be7a248c3ce` 的 coordinator（提交日期 2026-10-25）用于版本差异比较。它不是 0.23.0 的替代基线。源码及逐文件 SHA256 见 [锁文件](../../../env/sources.lock.json)。

[PR 元数据快照](../../../evidence/research/monitoring-2026-10-26/github-pr-metadata.json) 保存本轮 GitHub 返回的状态、refs 和描述；[摘要清单](../../../evidence/research/monitoring-2026-10-26/manifest.json) 固定其内容。open PR 的 merge_commit_sha 可能只是 GitHub 临时合并测试提交，不能据此认定已合并；以 merged / merged_at 为准。PR 描述、实际代码、项目实测分开使用。

## DeepSeek V4：物理存储单位与原始 Token 粒度不同

0.23.0 Ascend [CompressAttentionManager](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/core/single_type_kv_cache_manager.py)：

- `cache_blocks`：完整缓存单元数为 `num_tokens // (block_size * compress_ratio)`，写键也使用这个逻辑大小（158–192 行）。
- `find_longest_cache_hit`：先按 CP 拓扑调整大小，再乘压缩比例；用 `BlockHashListWithBlockSize` 取得同粒度前缀键，逐块连续匹配，遇首个缺失即停。MTP 退块后再满足共同对齐（194–241 行）。
- [coordinator](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/patch/platform/patch_kv_cache_coordinator.py) 的 `_get_effective_block_size` 与 `verify_and_split_kv_cache_groups` 计算各组逻辑大小及 LCM；SWA 保留掩码还依赖同一对齐和 MTP 组标记。完整组共同恢复边界不能仅由一个压缩组命中数决定。

因此用户提出“共用链式前缀键和连续匹配”有直接源码依据：可以复用这个基础算法。但把整个 V4 化为单一 B 的快速路径，仍须明确假设 SWA/状态等组在所选边界可恢复，并验证同详细路径等价。

CP=1、普通非 A5 状态布局、配置 B=128 时，主要组的逻辑大小为 128、512、16384，状态组大小可整除该共同粒度，故粗粒度共同边界可为 16384。B=32 时对应主要粒度为 32、128、4096。这个推导不代表每个边界都有状态，也不代表所有配置固定为 16384/4096。不能拿 GPU sparse MLA backend 的 256 替代 Ascend 的有效单位。

| Ascend PR | 2026-10-26 状态 | 可采用的结论 |
| --- | --- | --- |
| [#9903](https://github.com/vllm-project/vllm-ascend/pull/9903) | 已合并，2026-06-08 | 修正压缩比例参与写入与协调；仍需配合读路径 |
| [#10297](https://github.com/vllm-project/vllm-ascend/pull/10297) | 已合并，2026-06-11 | 读路径转换为逻辑块哈希；0.23.0 快照已见对应实现和测试 |
| [#10350](https://github.com/vllm-project/vllm-ascend/pull/10350)、[#10355](https://github.com/vllm-project/vllm-ascend/pull/10355)、[#10440](https://github.com/vllm-project/vllm-ascend/pull/10440) | 均关闭、未合并 | 曾提出私有部分页表、最长子块前缀及复制方案；不是已发布功能证据 |
| [#18959](https://github.com/vllm-project/vllm-ascend/pull/18959)、[#18698](https://github.com/vllm-project/vllm-ascend/pull/18698) | 均 open、未合并 | 前者拟修正 compressor state 的 slot/token 单位，后者拟退出状态组前缀缓存；存在不同方案，不能混用或称定论 |
| [#19714](https://github.com/vllm-project/vllm-ascend/pull/19714) | open、未合并 | sparse hybrid 的细粒度状态交接/Store 参考；作者硬件描述主要是 GLM-5.3-Flash，不是 V4 已验证能力 |

结论：V4 增强通道保留为待讨论设计。收到 txt 后再比较保存边界、恢复条件、部分页复制和 MTP/通信约束，不先套用 Qwen 或 SGLang 的实现。

## Qwen：大页与状态可恢复性是两个问题

0.23.0 Ascend [patch_mamba_config.py](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/patch/platform/patch_mamba_config.py) 58–117 行，将 SSM 状态和 attention K page 对齐：

`attention_block = 128 * ceil(ssm_page_bytes / (128 * attention_K_bytes_per_token))`。

它还要求精确页大小关系，并在配置块过小时覆盖配置。10-23 记录的 Qwen3.6-27B TP1、SSM fp32、KV bf16 参考配置可推得 1536；更换 TP、dtype、模型配置或实现会改变结果。源码没有支持“只要关闭 hybrid 特性就固定 1536”的一般性结论。

同版本 [AscendMambaManager.find_longest_cache_hit](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/patch/platform/patch_mamba_manager.py) 26–50 行，从后向前寻找实际已保存且对齐的状态；attention 的全部前缀存在，不等于每个位置的递归状态都存在。align 模式保存哪些边界还受 prefill 调度/分块影响。无限 HBM 只取消容量淘汰，不能创造未物化的状态。

需要区分三个独立开关/能力：prefix caching 是否开启、hybrid manager/cache mode、是否具有细粒度命中和共享前缀 admission。不能用一个“hybrid 开/关”涵盖它们。

| 来源 | 2026-10-26 状态 | 设计含义 |
| --- | --- | --- |
| [vLLM #46384](https://github.com/vllm-project/vllm/pull/46384) | 已合并，2026-07-12 | 参考：匹配单位与物理页分离、精确命中长度、部分状态物化、COW；不等于 Ascend 0.23.0 已支持 |
| [vLLM #37898](https://github.com/vllm-project/vllm/pull/37898) | 已合并，2026-06-10 | 参考：发现 attention 有共享前缀而 SSM 缺状态时，调度到边界保存状态 |
| [Ascend #14468](https://github.com/vllm-project/vllm-ascend/pull/14468) | open，目标 releases/v0.25.1rc | 实际 diff 补写 `num_uncached_common_prefix_tokens`；说明必须核对 Ascend coordinator→scheduler 链路 |
| [Ascend #16013](https://github.com/vllm-project/vllm-ascend/pull/16013) | 已合并，2026-09-17 | 实际 diff 为分段存储逐 tensor page 复制，处理共享视图及循环复制；支持 page 形状影响复用的判断 |
| [Ascend #16528](https://github.com/vllm-project/vllm-ascend/pull/16528) | open、未合并 | PD+MTP+细粒度状态交接的专门适配；不能推广到任意部署组合 |
| [Ascend #8829](https://github.com/vllm-project/vllm-ascend/pull/8829) | open、未合并 | GDN all-mode：物化每个块边界状态，和 align/二次出现后 admission 不同 |
| [Ascend #17657](https://github.com/vllm-project/vllm-ascend/pull/17657) | open、未合并 | DCP 下 hash 粒度与细粒度能力检查的版本敏感性 |

“cache on the second hit”不能实现成简单“某前缀第二次出现就直接算命中”。读过的 #37898 diff/test 明确有 attention 命中但 SSM 命中为零的请求；它提示 scheduler 在公共前缀处停下来物化状态，之后才可复用。边界状态已存在时又是不同情况。

当前 Ascend 主干 coordinator 的 `_skips_eagle_block_drop`（42–60 行）还按 standalone / pure PD producer 区分退块策略；0.23.0 快照没有这段策略。不能把旧版“减一个整块”套到新版，也不能因为新版可跳过退块而回改旧版假设。

[Marconi 论文](https://arxiv.org/abs/2411.19379) 对递归状态无法回退、状态 admission 的解释与此相关。TokenScope 采用无限容量，因此当前重点参考 admission 与状态恢复语义，不模拟该论文的容量淘汰优化；论文性能数字不转为本项目承诺。

## SGLang 只作为机制参考

[HiCache](https://docs.sglang.io/docs/advanced_features/hicache_design) 将前缀缓存扩展到 GPU、host、分布式存储层级；[HiSparse](https://docs.sglang.io/docs/advanced_features/hisparse_guide) 主要管理 decode 稀疏 attention 的 host KV 与设备热集合。它们并不等同于部分页前缀命中或递归状态 checkpoint。

在本任务的无限 HBM、立即可用假设下，容量扩展及传输时延不直接进入命中指标。仍须保留会改变可恢复边界的布局、复制/共享条件和角色配置。没有 attention 分数、真实 KV、路由/时序数据时，不声称能用当前 CSV 仿真稀疏 top-k、网络传输耗时或 TTFT。

## Recipe 分段能否支持长度差异定位

固定 Recipe `935817c` 的 [RenderedPrompt](../../../upstream/deepseek-recipe/deepseek-recipe-encoding/src/lib.rs) 只直接返回 prompt、special_ranges 和 image_sources；本项目输入无图像。它没有返回 JSON 字段到模板文本的完整映射。ordinary text 同时包括正文、工具定义、模板普通文字等，不等于“用户内容”。

[PromptTokenizer::encode_ids](../../../upstream/deepseek-recipe/deepseek-recipe-encoding/src/tokenizer.rs) 在 special_ranges 的 UTF-8 byte 边界处分段，将普通段通过去掉 added vocabulary 的 tokenizer 批量编码，明确特殊段映射为特殊 ID。因此输入正文碰巧出现特殊 token 拼写，不能被误记为模板控制 token。

Recipe [Cargo.toml](../../../upstream/deepseek-recipe/Cargo.toml) 声明 tokenizers 0.23.2（依赖范围声明，不是已验证的本地安装）。核对 [tokenizers v0.23.2](../../../upstream/tokenizers-v0.23.2/tokenizers/src/tokenizer/mod.rs)：
- `encode_batch_fast` 1382–1400 行调用 `encode_fast`；
- `encode_fast` 829–846 行用 `OffsetType::None`。
这条快速路径不计算来源 offsets，故“已有分段”不能直接升级为逐 Token 的 JSON 字段归因能力。

采用两层证据设计：
1. 全量：原始请求定位/摘要、J/P 等精确数值、编码资产及模式身份、prompt/Token IDs 摘要、经验证渲染器产生的特殊 token 区间和相关轻量来源索引。
2. 细查：同一适配器增加源字段→渲染 UTF-8 byte span 的映射，并运行保留 offsets 的等价编码路径；IDs/摘要必须与全量结果一致，否则报告证据不一致。

详细账本分别解释 raw JSON 和 rendered prompt；JSON 外壳/参数不入 prompt、转义/空白重写、模板角色/控制符、工具格式和思考处理都可能影响差值。不能把 `P-J` 称为“纯模板开销”。BPE 跨来源边界时单列 mixed-boundary/unknown 桶，不能逐字段独立 encode 后相加冒充完整编码的精确拆分。何种内容异常、优化建议等仍属于 Session 3。

## 本轮验证范围

只做源码、PR 状态和接口语义核对；新登记的参考测试没有在本机执行。重点测试入口见 [CODEMAP](../../tasks/monitoring/CODEMAP.md)。本轮结束检查锁定文件摘要、文档链接及讨论样例算术；实际结果另记 artifacts。10-23 的官方模板参考 4/4 结果保持原有边界，不提升为 tokenizer 或缓存仿真验证。

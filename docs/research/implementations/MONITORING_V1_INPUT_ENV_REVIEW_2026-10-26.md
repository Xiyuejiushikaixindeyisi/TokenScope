# 首版范围、输入组件与环境核对

2026-10-26，Session 1。用途：支持监控第一版审批设计；不开展部署、采集或 hybrid 业务实现。

## 本轮范围收敛

用户再次明确：三个模型首版都复用链式前缀键与连续匹配，只有增强 hybrid 通道的实现推迟、保留接口和类。不能把 Qwen/V4 的默认命中率或输入重算量标为不支持。既有 V4 状态/COW 和 Qwen prefill 研究保留为后续依据，不再是首版完成条件。仿真采用离散事件，事件表示逻辑状态转换，不凭开始时间伪造执行时长。

每模型缓存参数由产品配置提供，更新作用于下一次分析运行。无需取回生产镜像 digest、补丁、TP 或 dtype 才能开始参数化上限分析。仍记录本工具实际使用的算法、参数和编码资产，以便重复计算；它们是分析输入，不是生产部署审计。

用户再次指定默认 block size：GLM 128、Mamba 1536（用户说明来自启动日志，日志原件未提供）、V4 32。首版将这三个值直接作为所选链式近似的输入 Token 块长，不自行替换 V4 默认值。这个产品选择与源码事实分开：Ascend 同名 block_size 在压缩存储中可能指存储条目；本稿不声称简化的 32 Token 匹配就是生产引擎真实恢复粒度。结果标明 chained_approximation；后续增强通道再处理真实 page 单位与状态约束。

## deepseek-recipe 核对

用户链接 [README.zh.md](https://github.com/deepseek-ai/deepseek-recipe/blob/main/README.zh.md) 已读取。2026-10-26 核对 main 仍为项目已固定的 `935817c66f5d6e64838f419692545f06787e485f`，新增 4 个文件并核验 Git blob，未全量拉取仓库。

| 组件 | 已核对能力 | TokenScope 采用边界 |
| --- | --- | --- |
| deepseek-recipe | `ProtocolRequest.convert` 将协议请求转为 `ConversationRequest`；含 conversation、推理参数及响应设置 | DeepSeek OpenAI 请求适配参考/依赖；编码所需字段完整传递，保留原 JSON 独立计量 |
| deepseek-recipe-core | `Conversation` 含 messages、thinking_mode、tools、tool_choice、reasoning_effort、response_format | 参考统一语义结构；不是 CSV 导入器，也不是所有模型通用 chat template |
| deepseek-recipe-encoding | `PromptEncoding.render_conversation/encode`；`RenderedPrompt` 给出 prompt 和 special_ranges | 使用 V4 编码，不因 README 示例为 V4.1 而切换目标模型 |
| PromptTokenizer | 特殊 token 区间显式赋 ID，普通段使用无 added vocabulary 的 tokenizer 批量编码 | 复用 Rust 编码；普通文本中的同名字面量与模板控制 token 区分；快路径不提供完整来源映射 |

`Conversation::default` 的 thinking_mode=true 是 Recipe 的默认值，并不证明用户三个目标服务默认值相同。模型配置应明确渲染默认值，原请求的有效模式优先；模板变化会改变 P 和命中键。无需生产部署摘要也仍须选定编码资产与模式。

TokenScope 只借用请求转换、模板渲染与输入编码；无需推理、工具执行、HTTP 流式响应、图片下载或输出解析。对 Qwen/GLM 使用各自 tokenizer/template，避免经由 DeepSeek Conversation 规范化丢掉目标模板需要的字段。

固定入口：[README.zh.md](../../../upstream/deepseek-recipe/README.zh.md)、[core/lib.rs](../../../upstream/deepseek-recipe/deepseek-recipe-core/src/lib.rs)、[core/conversation.rs](../../../upstream/deepseek-recipe/deepseek-recipe-core/src/conversation.rs)、[request/mod.rs](../../../upstream/deepseek-recipe/deepseek-recipe/src/request/mod.rs)。此前 encoding/tokenizer.rs 与测试入口继续见 CODEMAP。

## MemScope 环境

已按用户授权只读检索 `/home/zhangxiyue/MemScope` 的环境相关文档。其 [工具链 ADR 副本](../../../evidence/research/monitoring-v1-2026-10-26/memscope-python-toolchain-adr.md) 明确 CPython 3.11.16、uv/uv_build 0.12.9。原始路径和摘要见[清单](../../../evidence/research/monitoring-v1-2026-10-26/manifest.json)。

V100 来自本轮用户说明。在此次检索到的 MemScope README、工具链 ADR 及环境相关 Markdown/文本中，未定位 CPU 型号/核数、RAM、NVIDIA 驱动和 CUDA 的具体数值，不填写推测值。监控的编码与离散事件回放走 CPU，无需加载模型权重或依赖 CUDA；这不等于已证明目标硬件吞吐。性能验收前记录 CPU/RAM/磁盘和实际软件版本即可，驱动/CUDA 作为环境记录，不作为计量输入。

首版目标为每文件、每模型端到端小于 7200 秒。三份文件可逐个分析，不将三者总耗时强行压到两小时。实际 SLA 必须在代表负载和目标 CPU 上测量。只借鉴环境版本，不继承 MemScope 的审批、Git、镜像或交付流程。

## PrefixLens 依赖调整

完整华为 PrefixLens 不再作为监控首版依赖。本机基础版继续作可选参考。后续 Token 分析确需核查时，再提供华为机 Agent 调研 prompt，要求仅回传一份 Markdown，算法结构、类图、活动图、请求时序、组件设计、关键源码和证据直接嵌入正文。当前不要求传源码、不联系华为机 Agent，也不以未收到材料阻断监控。

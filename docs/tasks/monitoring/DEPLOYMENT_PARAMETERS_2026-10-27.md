# 三模型部署参数摘录（2026-10-27）

来源：本会话用户提供的三组启动参数，仅按监控需要筛选保存。[机器可读索引](../../../env/profiles/monitoring-deployments-2026-10-27.index.json)含各 profile 的 SHA256。它们是**用户提供的声明配置**，未远程探测进程、展开 GF 脚本或确认最终有效参数；不会自动覆盖已批准的仿真默认值或历史运行快照。配置不保留凭据、内部初始化命令和无关网络/运维参数。

| 项目 | DeepSeek V4 Flash-0731 | Qwen3.6-27B | GLM-5.2 |
| --- | --- | --- | --- |
| GF 包系列 | **vllm_ascend_0_30_0rc2** | vllm_ascend_0_23_0 | vllm_ascend_0_23_0 |
| 文件模型别名 | deepseek_v4_flash | Qwen3.6-27B | GLM-5.2 |
| tokenizer-mode | deepseek_v4 | 未显式给出 | 未显式给出 |
| reasoning / tool parser | deepseek_v4 / deepseek_v4 | qwen3 / qwen3_coder | glm45 / glm47 |
| max model len | 131072 | 1010000 | 204800 |
| prefill / decode prefix cache | 开 / 关 | 开 / 关 | 开 / 开 |
| block-size 声明 | 两侧明确 32 | 未显式；沿用用户此前日志 1536 的仿真值 | 未显式；沿用用户此前指定 128 的仿真值 |
| GF hash_block_size | 4096 | 未给出 | 1024 |
| MTP | 本次 flags 未显式；此前用户仿真默认开 | 两侧 mtp，num_speculative_tokens=3 | deepseek_mtp，prefill=1 / decode=3 |
| CP | enable_dsa_cp=true 不能推出大小 | 未显式 | 两侧 PCP=1、DCP=8、interleave=128 |
| TP/DP | prefill/decode 各 TP8 / DP1 | TP8 / DP1 | prefill/decode 各 TP8 / DP2 |
| prefill/decode batched-token 预算 | 2048 / 2048 | 8192 / 8192 | 4096 / 128 |
| 缺省思考模式 | **pending** | 用户确认模板默认 | 用户确认模板默认 |

## 计量配置边界

- [DeepSeek profile](../../../env/profiles/deepseek-v4-flash-0731-gf-20261027.json)：0.23.0 官方源码的 thinking=False **不能证明**此 0.30.0rc2 GF 包的缺省行为。提供的参数有 tokenizer/reasoning parser，但没有 chat_template_kwargs 或明确 enable_thinking 值；parser 名不等于开启思考。因此保留 pending。`--no-disable-hybrid-kv-cache-manager`、multi-group/pool 说明声明启用相关管理机制，不自动启用 TokenScope 尚未实现的增强仿真。
- [Qwen profile](../../../env/profiles/qwen36-27b-gf-20261027.json)：MTP=3 有显式证据；1536 来源仍是此前用户日志，不伪写成这份命令的 --block-size。RoPE/最大长度覆盖保留为模型上下文配置，不据此乘改 tokenizer 长度。
- [GLM profile](../../../env/profiles/glm52-gf-20261027.json)：明确保存 PCP1/DCP8 和 interleave128。获批算法有 B_eff=B×cp_world_size，但现场双 CP 参数到标量 cp_world_size 的映射在本次“只提取并沉淀”范围内不作代码核实；profile 值标 pending。若映射为 8，128×8=1024 只是条件算术，不能因与 GF hash_block_size 相同就声称已验证。
- 三模型均记录量化变体、包/SDK 和 Python 声明（GF_VENV_PY_VERSION=3.11，但 GF_INFER_PYTHON 指向 3.12.13）。两者不一致时不能选择一个冒充实际进程版本；GLM 另有 Transformers 5.5.4 声明。
- 所有运行词表当前来自固定公开 revision，尚无部署侧 tokenizer/template 摘要；资产来源和现场等价性是不同的证据。
- 命令中的生成/调度限制不会自动截断历史 CSV 或改变两小时运行预算。共享/通信缓存、有限显存与后端传输不纳入首版空缓存/无限容量/按租户链式近似。

## 如何使用

本次仅登记声明 profile，不激活配置、不改 DESIGN 批准原稿、不改历史快照。后续明确运行 profile 时，再将已确认项写入模型设置的新 revision，运行开始时冻结；未确认参数继续显示状态。Qwen/GLM 模板默认继续用于 B002；DeepSeek 可验证显式开/关情景，未选定缺省模式前不能关闭 B002。
